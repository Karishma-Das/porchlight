#!/usr/bin/env python3
"""Porchlight: touch grass at your own pace.

An accessibility-first outdoor coach that runs an open-weight model (Gemma via
Ollama) entirely on your own computer. No cloud API, no keys, no accounts, no
pip installs (standard library only).

The key idea: the model SUGGESTS, the code DECIDES. Every suggestion is checked
against hard limits from your profile (distance, stairs, heat, time). Anything
that breaks a limit is rejected and the model is asked to try again. If it
keeps failing, a built-in safe mission is used instead.

Usage:
    ollama pull gemma3:4b
    python porchlight.py            # make today's mission
    python porchlight.py --reset    # re-answer the profile questions
    python porchlight.py --stats    # how often did the guard step in?

Env vars: PL_MODEL (default gemma3:4b), PL_OLLAMA_URL.
Not medical advice. Stop and rest if you feel unwell.
"""
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path

MODEL = os.getenv("PL_MODEL", "gemma3:4b")
OLLAMA_URL = os.getenv("PL_OLLAMA_URL", "http://localhost:11434/api/chat")
HERE = Path(__file__).resolve().parent
PROFILE_PATH = HERE / "porchlight_profile.json"  # stays on your machine
LOG_PATH = HERE / "porchlight_log.json"          # stays on your machine
CARD_PATH = HERE / "porchlight_card.html"
MAX_TRIES = 3
HOME_SPOTS = {"window", "balcony", "doorstep", "yard"}
RISKY = re.compile(r"\b(hike|climb|jog|sprint|run|cycle|swim|jump|barefoot)\b", re.I)

SYSTEM_PROMPT = """You are Porchlight, a gentle coach who helps people spend a few
minutes outdoors in a way that fits their body and their day. You never push.
Reply with ONE JSON object only, no other text, in exactly this shape:
{"title": "short title",
 "place": "one of the allowed places",
 "minutes": 5,
 "distance_m": 0,
 "needs_stairs": false,
 "exposure": "sun" | "shade" | "indoors",
 "sense_focus": "smell" | "sound" | "touch" | "sight",
 "steps": ["step 1", "step 2", "step 3"]}
Rules: exactly 3 short, calm steps. Use one or two senses, not equipment. Respect
every limit you are given. If unsure, choose the smaller, easier option."""

FALLBACKS = {
    "window": ("Five-sense window pause", "indoors", "sound", 0, [
        "Open the window if you can, or stand right beside it.",
        "Close your eyes for ten breaths and name three sounds you hear.",
        "Open your eyes and find one thing outside that is moving."]),
    "balcony": ("Balcony sky check", "shade", "sight", 0, [
        "Step onto the balcony and stand or sit comfortably.",
        "Look at the sky for one full minute without your phone.",
        "Notice one colour you hadn't seen before and say it out loud."]),
    "doorstep": ("Doorstep deep breath", "shade", "smell", 0, [
        "Open the door and sit or stand on the threshold.",
        "Breathe slowly and notice any smell in the air.",
        "Stay until you can describe the air in three words."]),
    "yard": ("Yard touch-and-notice", "shade", "touch", 0, [
        "Step into the yard and find a spot that feels comfortable.",
        "Touch one plant, wall or stone and describe its texture.",
        "Listen for the quietest sound you can find."]),
    "short_walk": ("Slow loop to the gate", "shade", "sight", 50, [
        "Walk slowly to the nearest gate, tree or corner.",
        "Pause there and look for something green.",
        "Walk back at your own pace and rest at the door."]),
}


# ---------- small helpers ----------
def ask(prompt, default=""):
    shown = f" [{default}]" if default != "" else ""
    return input(f"{prompt}{shown}: ").strip() or str(default)


def ask_yes(prompt, default="n"):
    return ask(f"{prompt} (y/n)", default).lower().startswith("y")


def ask_int(prompt, default):
    try:
        return max(0, int(ask(prompt, default)))
    except ValueError:
        return int(default)


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------- profile and context ----------
def build_profile():
    print("\nA few questions, asked once. Answers stay on this computer.\n")
    spots = [s.strip().lower() for s in
             ask("What do you have at home? (window, balcony, doorstep, yard)",
                 "window, doorstep").split(",")]
    spots = [s for s in spots if s in HOME_SPOTS] or ["window"]
    profile = {
        "max_distance_m": ask_int(
            "Farthest you can comfortably go from home, in metres "
            "(0 = can't leave home, 100 = a short walk)", 100),
        "stairs_ok": ask_yes("Can you manage stairs?", "y"),
        "heat_sensitive": ask_yes("Do you struggle in the heat?", "n"),
        "low_vision": ask_yes("Want extra-large, high-contrast text?", "n"),
        "spots": spots,
    }
    write_json(PROFILE_PATH, profile)
    return profile


def build_context(profile):
    places = list(profile["spots"])
    if profile["max_distance_m"] >= 50:
        places.append("short_walk")
    return {
        "minutes": max(1, ask_int("How many minutes do you have?", 10)),
        "energy": "low" if ask_yes("Is your energy low today?", "n") else "ok",
        "hot": ask_yes("Is it hot outside right now?", "n"),
        "places": places,
    }


# ---------- the guard: the model suggests, the code decides ----------
def validate(m, profile, ctx):
    errs = []
    if not isinstance(m, dict):
        return ["Reply was not a JSON object"]
    if m.get("place") not in ctx["places"]:
        errs.append(f"place must be one of {ctx['places']}")
    steps = m.get("steps")
    if (not isinstance(steps, list) or len(steps) != 3
            or not all(isinstance(s, str) and s.strip() for s in steps)):
        errs.append("steps must be exactly 3 non-empty strings")
    if not isinstance(m.get("title"), str) or not m["title"].strip():
        errs.append("title is missing")
    minutes, dist = to_int(m.get("minutes")), to_int(m.get("distance_m"))
    if minutes is None or not 1 <= minutes <= ctx["minutes"]:
        errs.append(f"minutes must be between 1 and {ctx['minutes']}")
    if dist is None or not 0 <= dist <= profile["max_distance_m"]:
        errs.append(f"distance_m must be at most {profile['max_distance_m']}")
    if m.get("place") in ("window", "balcony", "doorstep", "yard") and dist not in (0, None):
        if dist > 20:
            errs.append("home spots must stay within 20 metres")
    if m.get("needs_stairs") and not profile["stairs_ok"]:
        errs.append("stairs are not allowed for this person")
    if ctx["hot"] and profile["heat_sensitive"] and m.get("exposure") == "sun":
        errs.append("no direct sun when it is hot")
    text = " ".join([str(m.get("title", ""))] + [str(s) for s in (steps or [])])
    if (profile["max_distance_m"] <= 200 or ctx["energy"] == "low") and RISKY.search(text):
        errs.append("no strenuous activity words (hike, run, climb, etc.)")
    return errs


def fallback_mission(profile, ctx):
    for place in ("doorstep", "balcony", "yard", "window", "short_walk"):
        if place in ctx["places"]:
            title, exposure, sense, dist, steps = FALLBACKS[place]
            return {"title": title, "place": place, "minutes": min(5, ctx["minutes"]),
                    "distance_m": min(dist, profile["max_distance_m"]),
                    "needs_stairs": False, "exposure": exposure,
                    "sense_focus": sense, "steps": steps}
    title, exposure, sense, dist, steps = FALLBACKS["window"]
    return {"title": title, "place": "window", "minutes": min(5, ctx["minutes"]),
            "distance_m": 0, "needs_stairs": False, "exposure": exposure,
            "sense_focus": sense, "steps": steps}


# ---------- local model ----------
def ask_model(user_message):
    body = json.dumps({
        "model": MODEL, "stream": False, "format": "json",
        "options": {"temperature": 0.7},
        "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": user_message}],
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["message"]["content"].strip()


def build_prompt(profile, ctx, feedback, recent):
    msg = (f"Allowed places: {ctx['places']}. Minutes available: {ctx['minutes']}. "
           f"Farthest distance allowed: {profile['max_distance_m']} m. "
           f"Stairs allowed: {profile['stairs_ok']}. Energy today: {ctx['energy']}. "
           f"Hot outside now: {ctx['hot']}. Heat sensitive: {profile['heat_sensitive']}. "
           f"Recent missions (do not repeat): {recent or 'none'}.")
    if feedback:
        msg += f" Your previous answer was rejected because: {feedback}. Fix it."
    return msg


def generate(profile, ctx, recent):
    attempts, feedback = [], ""
    for n in range(1, MAX_TRIES + 1):
        raw = ask_model(build_prompt(profile, ctx, feedback, recent))
        try:
            mission = json.loads(raw)
            errs = validate(mission, profile, ctx)
        except json.JSONDecodeError:
            mission, errs = None, ["reply was not valid JSON"]
        attempts.append({"attempt": n, "accepted": not errs, "errors": errs,
                         "raw": raw[:400]})
        if not errs:
            return mission, "model", attempts
        feedback = "; ".join(errs)
    return fallback_mission(profile, ctx), "fallback", attempts


# ---------- large-print card ----------
def write_card(mission, profile, source):
    big = profile["low_vision"]
    size = "46px" if big else "30px"
    bg, fg, accent = ("#000", "#ffe600", "#fff") if big else ("#fffaf0", "#1a1a1a", "#b45309")
    steps = "".join(f"<li>{html.escape(str(s))}</li>" for s in mission["steps"])
    who = (f"Written by {html.escape(MODEL)} running on this computer"
           if source == "model" else "A built-in safe mission (the model's ideas were out of bounds)")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Porchlight</title><style>
body{{margin:0;padding:32px;background:{bg};color:{fg};font:{size}/1.5 Georgia,serif}}
h1{{font-size:1.3em;color:{accent};margin:0 0 .2em}}
.meta{{font-size:.6em;opacity:.85;margin-bottom:1em}}
li{{margin:.6em 0}}
.foot{{font-size:.55em;margin-top:2em;opacity:.8}}
@media print{{body{{background:#fff;color:#000}}h1{{color:#000}}}}
</style></head><body>
<h1>{html.escape(str(mission['title']))}</h1>
<div class="meta">{html.escape(str(mission['place']))} &middot; about
{html.escape(str(mission['minutes']))} min &middot; focus: {html.escape(str(mission.get('sense_focus', '')))}</div>
<ol>{steps}</ol>
<div class="foot">{who}. Not medical advice: stop and rest if you feel unwell.
Go at your own pace. Porchlight is on.</div></body></html>"""
    CARD_PATH.write_text(page, encoding="utf-8")


# ---------- stats for the write-up ----------
def show_stats():
    log = read_json(LOG_PATH, [])
    attempts = [a for e in log for a in e.get("attempts", [])]
    rejected = [a for a in attempts if not a["accepted"]]
    fallbacks = sum(1 for e in log if e.get("source") == "fallback")
    print(f"Missions: {len(log)} | model attempts: {len(attempts)} | "
          f"rejected by guard: {len(rejected)} | fallbacks used: {fallbacks}")
    for a in rejected[-5:]:
        print(" -", "; ".join(a["errors"]))


from card import write_card  # polished website-style card (overrides the simple one above)


def main():
    if "--stats" in sys.argv:
        return show_stats()
    print(f"\n=== Porchlight (local model: {MODEL}) ===")
    profile = None if "--reset" in sys.argv else read_json(PROFILE_PATH, None)
    if not profile:
        profile = build_profile()
    ctx = build_context(profile)
    log = read_json(LOG_PATH, [])
    recent = "; ".join(e["mission"]["title"] for e in log[-3:] if e.get("mission"))

    print("\nThinking, locally...")
    try:
        mission, source, attempts = generate(profile, ctx, recent)
    except (urllib.error.URLError, ConnectionError):
        print("Could not reach Ollama. Is it running? Try: ollama serve")
        print(f"And check the model exists: ollama pull {MODEL}")
        return

    write_card(mission, profile, source)
    rejected = sum(1 for a in attempts if not a["accepted"])
    print(f"\n{mission['title']}  [{mission['place']}, ~{mission['minutes']} min]")
    for i, s in enumerate(mission["steps"], 1):
        print(f"  {i}. {s}")
    if rejected:
        print(f"\n(The safety guard rejected {rejected} model suggestion(s) before this.)")
    print(f"\nLarge-print card: {CARD_PATH}")
    webbrowser.open(CARD_PATH.as_uri())

    entry = {"time": datetime.now().isoformat(timespec="minutes"), "source": source,
             "context": ctx, "mission": mission, "attempts": attempts, "reflection": ""}
    log.append(entry)
    write_json(LOG_PATH, log)

    input("\nGo outside. Press Enter when you're back... ")
    entry["reflection"] = ask("One line: how did it go?")
    write_json(LOG_PATH, log)
    print("Saved your note.")


if __name__ == "__main__":
    main()
