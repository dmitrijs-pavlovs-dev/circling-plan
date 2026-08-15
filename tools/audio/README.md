# Breathing track pipeline

How the tracks in `audio/` are made, so they can be rebuilt.

Source: audio ripped from the kundalini breathwork video, vocals removed with
BS-Roformer (`audio-separator`), then `blend.py` switches between the
untouched original (where nobody speaks) and the separated instrumental
(where someone does), gated by the vocals stem.

The big intermediates live **outside the repo** in
`~/apps/circling-plan-audio-src/`: `blended.wav` (the voice-free master
everything is cut from) and the vocals stem (the voice-activity map). They
are too large for GitHub. If they are lost, re-rip the video audio and re-run
`audio-separator` with `model_bs_roformer_ep_317_sdr_12` plus `blend.py`.

Timeline of `blended.wav` (1053 s):

| Blended time | What it is |
|---|---|
| 0–110 | intro talk (not used) |
| 110–222 | fire breathing, round 1 |
| 222–317 | holds and recovery, round 1 |
| 317–439 | fire breathing, round 2 |
| 439–578 | holds and recovery, round 2 |
| 578–693 | fire breathing, round 3 |
| 693–~880 | holds and recovery, round 3 |
| ~880–1053 | closing meditation tail |

Cuts:

- `breathing.mp3` (first version): blended from 110 s to the end.
- `breathing-no-fire.mp3` (first version): the three hold blocks joined.
- `breathing-short.mp3` / `breathing-no-fire-short.mp3`: same cuts with the
  five long retention holds shortened by 9–17 s each
  (`build-short-holds.py`, 15 August 2026). Join points are searched by
  loudness-envelope and timbre similarity so the equal-power crossfades stay
  inaudible; the script prints an RMS continuity check per join. It also
  fixed the rough 9.5 dB seam the first no-fire cut had at its round-3
  boundary.

Encode to match the existing files: `ffmpeg -i in.wav -codec:a libmp3lame
-q:a 2 out.mp3`.
