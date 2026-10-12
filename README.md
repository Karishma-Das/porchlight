# Porchlight: touch grass at your own pace

Most "go outside" apps assume you can hike, jog or walk a mile. Porchlight is for everyone else: older adults, people with limited mobility or low vision, people recovering from illness, or anyone with five minutes and a doorstep.

It runs an **open-weight model (Gemma via Ollama) entirely on your own computer**. No cloud API, no API keys, no accounts, no `pip install`.

## How it works

1. Answer a few questions once (how far you can go, stairs, heat, vision, what you have at home). They are saved only in a local file.
2. Each day, say how much time and energy you have.
3. The local model suggests a tiny outdoor mission (a balcony, a doorstep, a window, or a short walk).
4. **The model suggests, the code decides.** Every suggestion is checked against your hard limits (distance, stairs, heat, time, no strenuous words). Anything that breaks a limit is rejected and the model must try again. After 3 failed tries a built-in safe mission is used.
5. You get a large-print, high-contrast card to read or print, then you put the screen away.

## Run it

```
ollama pull gemma3:4b
python porchlight.py
```

- `python porchlight.py --reset` re-asks the profile questions.
- `python porchlight.py --stats` shows how often the guard rejected the model.
- Use a different model with the `PL_MODEL` environment variable (run `ollama list` to see yours).

Requires Python 3.8+ and [Ollama](https://ollama.com). Nothing else.

## Why open-weight and local

- **Privacy:** mobility and health details never leave the machine. Your profile and log are plain local files (and are git-ignored).
- **Works offline:** no signal needed once the model is downloaded.
- **Swappable:** change the model with one environment variable.
- **Free to run:** no per-request cost.

## Limits (honest notes)

- Small local models sometimes break rules. That is why the guard exists, and why `--stats` is there.
- This is not medical advice and does not assess anyone's health. Stop and rest if you feel unwell.
- Files in `porchlight_profile.json` and `porchlight_log.json` are created at runtime.

## Built for

Hacktoberfest 2026 Open-Source AI Challenge, Week 1: Touch Grass. Started and built within the challenge window. Any commits made after the deadline are listed here:

- (none yet)

License: MIT
