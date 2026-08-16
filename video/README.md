# Breathwork countdown video

A silent-guidance video for the breathwork segment: section countdowns, a
breath pacer, and on-screen prompts that replace the spoken guidance. Designed
to be cast to a screen while the music-only track plays.

`countdown.html` is the frame source, rendered at 1 fps and encoded to 30 fps.
It is a standalone page: open it in a browser and call `seek(seconds)` from the
console to inspect any moment.

## Source audio

The session is Sandy's *1 Hour Breathwork Journey, 8 Rounds of Acceptance*
(Patreon, member-only). **The audio is not in git.** Both the full-length
tracks and the rendered video are git-ignored because of their size; only the
29-minute cuts under `audio/` are published with the site.

## Analysis data

Both files are tracked, so the numbers below can be reused without redoing the
signal processing.

| File | What's in it |
|---|---|
| `beat-analysis.json` | The 28 phase boundaries, and a beat grid for each of the 8 rounds (3,396 beat timestamps). |
| `volume-analysis.json` | Per-second loudness envelope, per-phase loudness and rhythmicity stats, and the independently detected rhythmic sections. |
| `waveform-analysis.png` | Full-session overview: waveform, energy, rhythmic activity, with both boundary sets drawn over it. |

Findings worth keeping in mind:

- **One tempo throughout: 83.4 bpm.** Every round sits on the same grid, so
  splices between rounds land naturally.
- **Breath cycle is 5.71 s (~10.5 breaths/min)**, identical in all 8 rounds and
  exactly 8 beats long. This is what the pacer dot is driven by.
- **Holds are 17 dB quieter than rounds** (−37.7 LU vs −20.2 LU). On a small
  speaker the holds can vanish; compress before playing in a room.
- **The closing "meditation" is three sections,** not one: deep stillness with a
  singing-bowl pulse, an ethereal choral swell, then a fade to silence.

## Rebuilding

Boundaries were derived from the signal, not typed by hand. To redo them:

```bash
python analyze-beats.py      # energy-gradient boundaries + beat grids
python analyze-waveform.py   # loudness envelopes + independent detection
```

Voice removal uses BS-Roformer via `audio-separator`. **Split the source into
10-minute chunks first**: a single pass over the 86-minute file deadlocks (all
Python threads block on a lock acquire, GPU idle, and it never recovers).

```bash
ffmpeg -i source.mp3 -ar 44100 -f segment -segment_time 600 -c:a pcm_s16le chunk_%02d.wav
for f in chunk_*.wav; do
  audio-separator "$f" -m model_bs_roformer_ep_317_sdr_12.9755.ckpt --output_format WAV
done
```

The published music-only track is not the raw instrumental stem. Wherever
nobody is speaking, the original untouched audio is used instead, and the
separated stem is faded in only around speech. Separation dulls the music, so
this keeps roughly a third of the track at original quality.

To render the video:

```bash
node render.js    # 5,146 frames at 1 fps via headless Chrome
ffmpeg -framerate 1 -i frames/%05d.jpg -c:v libx264 -preset medium \
  -tune stillimage -crf 22 -pix_fmt yuv420p -r 30 video-silent.mp4
ffmpeg -i video-silent.mp4 -i ../audio/breathing-full.mp3 \
  -c:v copy -c:a aac -b:a 160k -shortest countdown.mp4
```
