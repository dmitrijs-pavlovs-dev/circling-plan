"""Volume/waveform analysis of the breathwork track.

Computes per-second energy envelopes (total, bass, mid/voice band),
onset-strength rhythmicity, independently detects rhythmic sections
by activity threshold, compares them against the refined boundaries,
and renders a full-session overview plot.
"""
import json
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = "/tmp/sandy-1hr.mp3"
SR = 22050
HOP = 512

with open("/tmp/beat-analysis.json") as f:
    ANALYSIS = json.load(f)
PHASES = ANALYSIS["phases"]

print("loading...")
y, sr = librosa.load(SRC, sr=SR, mono=True)
dur = len(y) / sr
fps = sr / HOP

print("spectrogram...")
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP)) ** 2
freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
times = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=HOP)

def band_db(lo, hi):
    m = (freqs >= lo) & (freqs < hi)
    e = S[m].mean(axis=0)
    return 10 * np.log10(e + 1e-10)

total_db = 10 * np.log10(S.mean(axis=0) + 1e-10)
bass_db = band_db(20, 160)      # rhythm / drums
voice_db = band_db(200, 3500)   # voice + melodic mids
high_db = band_db(4000, 10000)  # air / cymbals

onset_env = librosa.onset.onset_strength(S=librosa.power_to_db(S), sr=sr)

def smooth(x, seconds=2.0):
    w = int(seconds * fps)
    k = np.hanning(2 * w + 1)
    k /= k.sum()
    return np.convolve(x, k, mode="same")

total_s = smooth(total_db)
bass_s = smooth(bass_db)
onset_s = smooth(onset_env, 3.0)

# --- independent rhythmic-section detection --------------------------------
# combine rhythmicity (onsets) and bass energy, normalize 0..1
def norm(x):
    lo, hi = np.percentile(x, 5), np.percentile(x, 97)
    return np.clip((x - lo) / (hi - lo + 1e-9), 0, 1)

activity = 0.6 * norm(onset_s) + 0.4 * norm(bass_s)
thr = 0.45
active = activity > thr

# clean: merge gaps < 20s, drop islands < 45s
def runs(mask):
    d = np.diff(mask.astype(int))
    starts = list(np.where(d == 1)[0] + 1)
    ends = list(np.where(d == -1)[0] + 1)
    if mask[0]: starts = [0] + starts
    if mask[-1]: ends = ends + [len(mask)]
    return list(zip(starts, ends))

segs = runs(active)
merged = []
for s0, e0 in segs:
    if merged and (s0 - merged[-1][1]) / fps < 20:
        merged[-1] = (merged[-1][0], e0)
    else:
        merged.append((s0, e0))
detected = [(times[s0], times[min(e0, len(times) - 1)])
            for s0, e0 in merged if (e0 - s0) / fps >= 45]

print(f"\nindependently detected {len(detected)} rhythmic sections:")
ref_rounds = [p for p in PHASES if p["type"] == "breathing"]
report = []
for i, (a, b) in enumerate(detected):
    match = ref_rounds[i] if i < len(ref_rounds) else None
    if match:
        da, db_ = a - match["s"], b - match["e"]
        line = (f'  detect {a:7.1f}-{b:7.1f}  vs  {match["label"]}: '
                f'{match["s"]:7.1f}-{match["e"]:7.1f}  '
                f'(start diff {da:+5.1f}s, end diff {db_:+5.1f}s)')
    else:
        line = f"  detect {a:7.1f}-{b:7.1f}  (no matching round!)"
    print(line)
    report.append(line)

# per-phase stats
print("\nper-phase loudness:")
stats = []
for p in PHASES:
    i0, i1 = np.searchsorted(times, p["s"]), np.searchsorted(times, p["e"])
    st = dict(label=p["label"], type=p["type"], s=p["s"], e=p["e"],
              rms_db=round(float(total_db[i0:i1].mean()), 1),
              bass_db=round(float(bass_db[i0:i1].mean()), 1),
              rhythmicity=round(float(norm(onset_s)[i0:i1].mean()), 2))
    stats.append(st)
    print(f'  {p["label"]:14s} {p["type"]:10s} rms {st["rms_db"]:6.1f} dB  '
          f'bass {st["bass_db"]:6.1f} dB  rhythm {st["rhythmicity"]:.2f}')

# --- plot -------------------------------------------------------------------
COLORS = {"intro": "#7a6a58", "breathing": "#c2571f", "hold": "#45372c",
          "recovery": "#a8773f", "meditation": "#7a6a58"}
fig, axes = plt.subplots(3, 1, figsize=(42, 13), sharex=True,
                         gridspec_kw=dict(height_ratios=[2, 1.2, 1]))
fig.patch.set_facecolor("#f3ece1")

step = max(1, len(y) // 400000)
wt = np.arange(0, len(y), step) / sr
ax = axes[0]
ax.fill_between(wt, y[::step], -np.abs(y[::step]), color="#45372c", alpha=0.5, linewidth=0)
ax.set_ylabel("waveform")
ax.set_ylim(-1, 1)

axes[1].plot(times, total_s, color="#45372c", lw=1.2, label="total (dB)")
axes[1].plot(times, bass_s, color="#c2571f", lw=1.2, label="bass 20-160 Hz (dB)")
axes[1].legend(loc="upper right", framealpha=0.6)
axes[1].set_ylabel("energy (dB)")

axes[2].plot(times, activity, color="#c2571f", lw=1.2)
axes[2].axhline(thr, color="#7a6a58", ls="--", lw=1)
axes[2].set_ylabel("rhythmic activity")
axes[2].set_xlabel("time (s)")

for ax in axes:
    ax.set_facecolor("#f8f3ea")
    for p in PHASES:
        ax.axvspan(p["s"], p["e"], color=COLORS[p["type"]],
                   alpha=0.10 if p["type"] in ("breathing",) else 0.05, lw=0)
        ax.axvline(p["s"], color=COLORS[p["type"]], alpha=0.7, lw=1)
    for a, b in detected:
        ax.axvline(a, color="#2f6f4f", ls=":", lw=1.4)
        ax.axvline(b, color="#2f6f4f", ls=":", lw=1.4)
    ax.set_xlim(0, dur)

for p in PHASES:
    if p["type"] in ("breathing", "hold", "meditation", "intro"):
        axes[0].text((p["s"] + p["e"]) / 2, 0.88, p["label"].replace(" of 8", ""),
                     ha="center", fontsize=11, color="#45372c")
axes[0].set_title("Breathwork session: waveform, energy and rhythmic activity "
                  "(solid lines = refined boundaries, green dotted = independent detection)",
                  fontsize=14, color="#45372c")
plt.tight_layout()
plt.savefig("/tmp/waveform-analysis.png", dpi=100)
print("\nplot saved: /tmp/waveform-analysis.png")

env = dict(hop_seconds=round(1 / fps, 5),
           note="per-frame dB envelopes downsampled to 1s",
           seconds=[round(float(x), 1) for x in
                    total_db[::int(fps)]],
           bass=[round(float(x), 1) for x in bass_db[::int(fps)]],
           stats=stats,
           detected_sections=[[round(a, 2), round(b, 2)] for a, b in detected])
with open("/tmp/volume-analysis.json", "w") as f:
    json.dump(env, f)
print("envelope saved: /tmp/volume-analysis.json")
