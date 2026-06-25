# circling-plan

A mobile-friendly web app to run a circling session from your phone. It renders the session
plan (`session-program-v2.md`) and adds three live tools for use during the session:

- **Live clock** — current time, always visible in the header.
- **Focus timer** — countdown (with a 15-min "focus" preset for the Focus Circle) and a stopwatch,
  with start/pause/reset, quick presets, ±1 min, an end-of-time beep + vibration.
- **Music player** — embedded YouTube player for *Nicola Cruz – Cumbia del Olvido* with
  play/stop, a seek slider to scrub to any point, volume, and an option to load a different track.

## Live site

Deployed via GitHub Actions to GitHub Pages on every push to `main`.

## Local preview

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Editing the plan

Edit `session-program-v2.md` and push — the site re-renders it automatically.
