"""Beat and section-boundary analysis for the breathwork track.

Refines Gemini's approximate phase boundaries by finding the strongest
energy transition near each estimate, snapping starts of rhythmic
sections to the first strong onset, and extracting per-round beat grids.
"""
import json
import numpy as np
import librosa

SRC = "/tmp/sandy-1hr.mp3"
SR = 22050
HOP = 512

# Gemini estimates in seconds: (start, type, label)
PHASES = [
    (0,    "intro",      "Welcome"),
    (320,  "breathing",  "Round 1 of 8"),
    (540,  "hold",       "Breath hold"),
    (604,  "recovery",   "Recovery"),
    (644,  "breathing",  "Round 2 of 8"),
    (882,  "hold",       "Breath hold"),
    (972,  "recovery",   "Recovery"),
    (987,  "breathing",  "Round 3 of 8"),
    (1224, "hold",       "Breath hold"),
    (1325, "recovery",   "Recovery"),
    (1346, "breathing",  "Round 4 of 8"),
    (1613, "hold",       "Breath hold"),
    (1733, "recovery",   "Recovery"),
    (1754, "breathing",  "Round 5 of 8"),
    (2024, "hold",       "Breath hold"),
    (2156, "recovery",   "Recovery"),
    (2181, "breathing",  "Round 6 of 8"),
    (2457, "hold",       "Breath hold"),
    (2607, "recovery",   "Recovery"),
    (2636, "breathing",  "Round 7 of 8"),
    (2913, "hold",       "Breath hold"),
    (3093, "recovery",   "Recovery"),
    (3116, "breathing",  "Round 8 of 8"),
    (3483, "hold",       "Breath hold"),
    (3663, "recovery",   "Recovery"),
    (3690, "meditation", "Meditation"),
]

print("loading audio...")
y, sr = librosa.load(SRC, sr=SR, mono=True)
duration = len(y) / sr
print(f"loaded {duration:.1f}s")

rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=HOP)
fps = sr / HOP  # frames per second

# ~1.5s smoothing window for the energy envelope
w = int(1.5 * fps)
k = np.hanning(2 * w + 1)
k /= k.sum()
sdb = 20 * np.log10(np.convolve(rms, k, mode="same") + 1e-9)

onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
onset_times = librosa.onset.onset_detect(
    onset_envelope=onset_env, sr=sr, hop_length=HOP, units="time",
    backtrack=True, delta=0.35)

def refine(t0, mode, half):
    """Find the strongest energy transition within +/-half s of t0."""
    i0 = max(0, np.searchsorted(times, t0 - half))
    i1 = min(len(times) - 1, np.searchsorted(times, t0 + half))
    grad = np.gradient(sdb[i0:i1])
    if mode == "rise":
        j = int(np.argmax(grad))
    elif mode == "drop":
        j = int(np.argmin(grad))
    else:
        j = int(np.argmax(np.abs(grad)))
    return float(times[i0 + j])

def snap_to_onset(t0, back=1.5, fwd=4.0):
    """Snap to the first detected onset just at/after the transition."""
    cand = onset_times[(onset_times >= t0 - back) & (onset_times <= t0 + fwd)]
    return float(cand[0]) if len(cand) else t0

MODE = {"breathing": "rise", "hold": "drop", "recovery": "abs", "meditation": "abs"}
HALF = {"breathing": 15, "hold": 15, "recovery": 8, "meditation": 15}

refined = [dict(s=0.0, type=PHASES[0][1], label=PHASES[0][2])]
for start, ptype, label in PHASES[1:]:
    t = refine(start, MODE[ptype], HALF[ptype])
    if ptype == "breathing":
        t = snap_to_onset(t)
    refined.append(dict(s=round(t, 2), type=ptype, label=label))

# enforce monotonicity and set ends
for i in range(1, len(refined)):
    if refined[i]["s"] <= refined[i - 1]["s"]:
        refined[i]["s"] = refined[i - 1]["s"] + 1.0
for i, ph in enumerate(refined):
    ph["e"] = round(refined[i + 1]["s"], 2) if i + 1 < len(refined) else round(duration, 2)

# per-round beat grids
rounds = []
for ph in refined:
    if ph["type"] != "breathing":
        continue
    a, b = int(ph["s"] * sr), int(ph["e"] * sr)
    tempo, beats = librosa.beat.beat_track(
        y=y[a:b], sr=sr, hop_length=HOP, units="time")
    tempo = float(np.atleast_1d(tempo)[0])
    beats = (np.asarray(beats) + ph["s"]).round(3).tolist()
    rounds.append(dict(label=ph["label"], tempo=round(tempo, 1),
                       n_beats=len(beats), beats=beats))
    print(f'{ph["label"]}: {ph["s"]:.2f} -> {ph["e"]:.2f}  tempo {tempo:.1f} bpm, {len(beats)} beats')

out = dict(duration=round(duration, 2), phases=refined, rounds=rounds)
with open("/tmp/beat-analysis.json", "w") as f:
    json.dump(out, f, indent=1)

print("\nrefined boundaries (old -> new):")
for (old, _, lbl), ph in zip(PHASES, refined):
    print(f'  {lbl:14s} {old:7.1f} -> {ph["s"]:8.2f}  (shift {ph["s"]-old:+6.2f}s)')
