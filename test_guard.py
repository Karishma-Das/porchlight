"""Run hand-written sample suggestions through Porchlight's REAL guard.

This does NOT call the AI model. It feeds fixed, scripted suggestions into the
same validate() function that porchlight.py uses, so you can see the guard
accept or reject them. (The demo website's 'Try the guard' section is a
JavaScript copy of these same rules.)

Run:  python test_guard.py
"""
import porchlight as pl

PEOPLE = {
    "Can't leave home": (
        {"max_distance_m": 0, "stairs_ok": False, "heat_sensitive": True, "low_vision": False, "spots": ["window", "balcony"]},
        {"minutes": 5, "energy": "low", "hot": True, "places": ["window", "balcony"]},
    ),
    "Short walker (150 m)": (
        {"max_distance_m": 150, "stairs_ok": False, "heat_sensitive": False, "low_vision": False, "spots": ["window", "doorstep"]},
        {"minutes": 15, "energy": "ok", "hot": False, "places": ["window", "doorstep", "short_walk"]},
    ),
    "Heat-sensitive, hot day": (
        {"max_distance_m": 100, "stairs_ok": True, "heat_sensitive": True, "low_vision": False, "spots": ["doorstep", "yard"]},
        {"minutes": 10, "energy": "ok", "hot": True, "places": ["doorstep", "yard", "short_walk"]},
    ),
}


def mission(title, place, minutes, dist, stairs, exposure, steps):
    return {"title": title, "place": place, "minutes": minutes, "distance_m": dist,
            "needs_stairs": stairs, "exposure": exposure, "sense_focus": "sight", "steps": steps}


SAMPLES = {
    "Window sound-spotting (5 min)": mission("Window sound-spotting", "window", 5, 0, False, "indoors",
        ["Stand beside the window.", "Close your eyes and count three sounds.", "Open your eyes and find something moving."]),
    "Doorstep deep breath (5 min)": mission("Doorstep deep breath", "doorstep", 5, 0, False, "shade",
        ["Sit on the threshold.", "Breathe slowly.", "Describe the air in three words."]),
    "Loop to the park (20 min, 400 m, stairs)": mission("Loop to the park", "short_walk", 20, 400, True, "sun",
        ["Take the stairs down.", "Jog to the park.", "Walk back."]),
    "Sunny yard sit (10 min)": mission("Sunny yard sit", "yard", 10, 0, False, "sun",
        ["Step into the yard.", "Sit in the sunniest spot.", "Notice the warmth."]),
    "Barefoot doorstep grounding (10 min)": mission("Doorstep grounding", "doorstep", 10, 0, False, "shade",
        ["Stand barefoot on your doorstep.", "Notice the temperature of the surface.", "Take a few slow breaths."]),
    "Slow loop to the gate (8 min, 50 m)": mission("Slow loop to the gate", "short_walk", 8, 50, False, "shade",
        ["Walk slowly to the gate.", "Look for something green.", "Walk back and rest at the door."]),
}

accepted = rejected = 0
for person, (profile, ctx) in PEOPLE.items():
    print(f"\n=== {person} ===")
    for name, m in SAMPLES.items():
        errs = pl.validate(m, profile, ctx)
        if errs:
            rejected += 1
            print(f"  REJECTED  {name}")
            for e in errs:
                print(f"            - {e}")
        else:
            accepted += 1
            print(f"  accepted  {name}")

print(f"\nTotal: {accepted} accepted, {rejected} rejected (scripted samples, no AI model used).")
