"""Website-style card for Porchlight.

One self-contained HTML file: no internet, no external fonts, no images, no
scripts except a Print button. Works offline, prints cleanly, and has a
high-contrast extra-large mode for low vision.
"""
import html
import os
from pathlib import Path

CARD_PATH = Path(__file__).resolve().parent / "porchlight_card.html"

LANTERN = (
    '<svg viewBox="0 0 64 64" width="__SZ__" height="__SZ__" aria-hidden="true">'
    '<rect class="lamp" x="22" y="6" width="20" height="7" rx="3.5"/>'
    '<path class="lamp" d="M20 15h24l4 29H16z"/>'
    '<rect class="lamp-glass" x="26" y="21" width="12" height="17" rx="6"/>'
    '<rect class="lamp" x="17" y="44" width="30" height="7" rx="3.5"/>'
    '</svg>'
)

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Porchlight: __TITLE__</title>
<style>
:root{--fs:19px}
*{box-sizing:border-box}
body{margin:0;font:var(--fs)/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#fff6e6;background:#241228}
body.calm{background:radial-gradient(1100px 560px at 78% -8%,#6b2f5c 0%,transparent 60%),linear-gradient(160deg,#2a1530,#3d2040 55%,#1d0f24)}
body.big{--fs:28px;background:#000;color:#ffe600}
h1,h2,h3{font-family:Georgia,"Times New Roman",serif;line-height:1.15;margin:0}
.wrap{max-width:980px;margin:0 auto;padding:0 24px}
.lamp{fill:#f6b84b}.lamp-glass{fill:#fff6e6}
body.big .lamp{fill:#ffe600}body.big .lamp-glass{fill:#000}
.nav{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:22px 0;flex-wrap:wrap}
.logo{display:flex;align-items:center;gap:10px;font:700 1.2em Georgia,serif;color:inherit;text-decoration:none}
.nav ul{display:flex;gap:22px;list-style:none;margin:0;padding:0;font-size:.8em}
.nav a{color:inherit;text-decoration:none;opacity:.92}
.nav a:hover,.nav a:focus-visible{text-decoration:underline;opacity:1}
.pill{display:inline-flex;align-items:center;gap:10px;background:#fff6e6;color:#2a1530;border:0;border-radius:999px;padding:.5em .55em .5em 1.1em;font:600 .8em system-ui,sans-serif;cursor:pointer;text-decoration:none}
.pill .dot{width:1.8em;height:1.8em;border-radius:50%;background:#5a2a52;color:#fff6e6;display:grid;place-items:center}
body.big .pill{background:#ffe600;color:#000}
body.big .pill .dot{background:#000;color:#ffe600}
.pill:focus-visible,.step input:focus-visible + .num{outline:4px solid #f6b84b;outline-offset:3px}
.hero{padding:48px 0 44px;display:grid;grid-template-columns:1.35fr .65fr;gap:32px;align-items:center}
.eyebrow{letter-spacing:.14em;text-transform:uppercase;font-size:.6em;color:#f6b84b;margin:0 0 14px}
body.big .eyebrow{color:#fff}
.hero h1{font-size:2.7em}
.lead{font-size:.9em;opacity:.92;max-width:34em;margin:18px 0 28px}
.glow{aspect-ratio:1;width:100%;max-width:270px;justify-self:center;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle,rgba(246,184,75,.6),rgba(246,184,75,.14) 55%,transparent 72%);animation:pulse 4s ease-in-out infinite}
body.big .glow{background:none;border:6px solid #ffe600;animation:none}
@keyframes pulse{50%{transform:scale(1.06);opacity:.86}}
@media (prefers-reduced-motion:reduce){.glow{animation:none}}
.card{background:#fff6e6;color:#2a1530;border-radius:28px;padding:34px;margin:8px 0 52px;box-shadow:0 20px 60px rgba(0,0,0,.35)}
body.big .card{background:#000;color:#ffe600;border:6px solid #ffe600;box-shadow:none}
.label{letter-spacing:.14em;text-transform:uppercase;font-size:.6em;color:#8a4a7a;margin:0 0 8px}
body.big .label{color:#fff}
.card h2{font-size:1.9em}
.chips{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0 22px}
.chip{background:#2a1530;color:#fff6e6;border-radius:999px;padding:.25em .9em;font-size:.7em}
body.big .chip{background:#ffe600;color:#000;font-weight:700}
.step{position:relative;display:flex;gap:16px;align-items:flex-start;padding:16px 0;border-top:1px solid rgba(42,21,48,.18);cursor:pointer}
body.big .step{border-top:3px solid #ffe600}
.step input{position:absolute;opacity:0;width:1px;height:1px}
.num{flex:0 0 auto;width:2em;height:2em;border-radius:50%;background:#f6b84b;color:#2a1530;display:grid;place-items:center;font-weight:700}
body.big .num{background:#ffe600;color:#000}
.step input:checked + .num{background:#2a1530;color:#fff6e6}
body.big .step input:checked + .num{background:#fff;color:#000}
.step input:checked + .num + .txt{opacity:.55;text-decoration:line-through}
.hint{font-size:.65em;opacity:.75;margin:14px 0 0}
.sec-title{font-size:1.5em;margin:0 0 18px}
.how{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:0 0 52px}
.how div{background:rgba(255,246,230,.08);border:1px solid rgba(255,246,230,.22);border-radius:20px;padding:22px}
body.big .how div{background:none;border:3px solid #ffe600}
.how h3{font-size:1.1em;margin-bottom:8px;color:#f6b84b}
body.big .how h3{color:#fff}
.how p{margin:0;font-size:.75em;opacity:.93}
.privacy{border-left:6px solid #f6b84b;padding:6px 0 6px 20px;margin:0 0 52px;font-size:.85em;max-width:40em}
body.big .privacy{border-left-color:#fff}
footer{padding:26px 0 48px;font-size:.6em;opacity:.85;border-top:1px solid rgba(255,246,230,.22)}
@media (max-width:760px){.hero{grid-template-columns:1fr}.how{grid-template-columns:1fr}.glow{max-width:170px}.hero h1{font-size:2.1em}.card{padding:22px}}
@media print{
 body,body.calm,body.big{background:#fff;color:#000}
 .noprint{display:none}
 .card,body.big .card{box-shadow:none;border:2px solid #000;background:#fff;color:#000}
 .chip,body.big .chip{background:#fff;color:#000;border:1px solid #000}
 .num,body.big .num{background:#fff;color:#000;border:2px solid #000}
 .label{color:#000}
 footer{border-top:1px solid #000;opacity:1;color:#000}
}
</style></head>
<body class="__BODYCLASS__">
<div class="wrap">
<header class="nav noprint">
 <a class="logo" href="#top">__LANTERN_SM__ Porchlight</a>
 <ul><li><a href="#mission">Today's mission</a></li><li><a href="#how">How it works</a></li><li><a href="#privacy">Privacy</a></li></ul>
 <button class="pill" onclick="window.print()">Print this card <span class="dot" aria-hidden="true">&#8599;</span></button>
</header>

<section class="hero noprint" id="top">
 <div>
  <p class="eyebrow">Touch grass at your own pace</p>
  <h1>Step outside, your way.</h1>
  <p class="lead">Gentle outdoor missions that fit your body and your day, written by an open AI model running on your own computer. No account. No cloud.</p>
  <a class="pill" href="#mission">See today's mission <span class="dot" aria-hidden="true">&#8595;</span></a>
 </div>
 <div class="glow">__LANTERN_LG__</div>
</section>

<section class="card" id="mission">
 <p class="label">Today's mission</p>
 <h2>__TITLE__</h2>
 <div class="chips">__CHIPS__</div>
 __STEPS__
 <p class="hint noprint">Tick each step as you go. Take your time.</p>
</section>

<section id="how" class="noprint">
 <h2 class="sec-title">How Porchlight keeps it safe</h2>
 <div class="how">
  <div><h3>1. You set the limits</h3><p>How far you can go, stairs, heat and time. Asked once and saved only on this computer.</p></div>
  <div><h3>2. The model suggests</h3><p>An open-weight model writes one tiny mission, just for today.</p></div>
  <div><h3>3. The code decides</h3><p>Every idea is checked against your limits. If it doesn't fit, it is rejected and the model tries again, or a safe backup is used.</p></div>
 </div>
</section>

<section id="privacy" class="privacy noprint">
 <h2 class="sec-title">Private by design</h2>
 Your answers and history never leave this computer. No cloud API, no sign-up.
</section>

<footer>
 __WHO__. Not medical advice: stop and rest if you feel unwell.
 <span class="noprint">Built for Hacktoberfest 2026, Touch Grass week.</span>
</footer>
</div>
</body></html>
"""


def write_card(mission, profile, source):
    esc = lambda v: html.escape(str(v))
    model = os.getenv("PL_MODEL", "gemma3:4b")
    chips = [esc(mission.get("place", "")), f"about {esc(mission.get('minutes', ''))} min"]
    if mission.get("sense_focus"):
        chips.append(f"focus: {esc(mission['sense_focus'])}")
    if mission.get("exposure"):
        chips.append(esc(mission["exposure"]))
    chip_html = "".join(f'<span class="chip">{c}</span>' for c in chips if c)
    steps = "".join(
        f'<label class="step"><input type="checkbox">'
        f'<span class="num">{i}</span><span class="txt">{esc(s)}</span></label>'
        for i, s in enumerate(mission["steps"], 1)
    )
    who = (f"Written by {esc(model)} running on this computer" if source == "model"
           else "A built-in safe mission (the model's ideas were out of bounds)")
    page = (TEMPLATE
            .replace("__BODYCLASS__", "big" if profile.get("low_vision") else "calm")
            .replace("__LANTERN_SM__", LANTERN.replace("__SZ__", "30"))
            .replace("__LANTERN_LG__", LANTERN.replace("__SZ__", "130"))
            .replace("__TITLE__", esc(mission["title"]))
            .replace("__CHIPS__", chip_html)
            .replace("__STEPS__", steps)
            .replace("__WHO__", who))
    CARD_PATH.write_text(page, encoding="utf-8")
