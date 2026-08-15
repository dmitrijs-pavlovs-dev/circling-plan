"""Blend original audio with separated instrumental.

Uses the vocals stem as a voice-activity map: where voice is present
(with padding and smooth fades), take the separated instrumental;
everywhere else take the original untouched audio.
"""
import numpy as np
import soundfile as sf

ORIG = "/tmp/breath-source-44k.wav"
INST = "/tmp/roformer/breath-source_(Instrumental)_model_bs_roformer_ep_317_sdr_12.wav"
VOC = "/tmp/roformer/breath-source_(Vocals)_model_bs_roformer_ep_317_sdr_12.wav"
OUT = "/tmp/blended.wav"

orig, sr = sf.read(ORIG, dtype="float32")
inst, sr2 = sf.read(INST, dtype="float32")
voc, sr3 = sf.read(VOC, dtype="float32")
assert sr == sr2 == sr3, (sr, sr2, sr3)
n = min(len(orig), len(inst), len(voc))
orig, inst, voc = orig[:n], inst[:n], voc[:n]

# Vocal energy envelope, 50 ms windows
win = int(0.05 * sr)
frames = n // win
v = voc[: frames * win].mean(axis=1) if voc.ndim > 1 else voc[: frames * win]
rms = np.sqrt((v.reshape(frames, win) ** 2).mean(axis=1))
db = 20 * np.log10(rms + 1e-10)

# Voice active where above threshold; -55 dB catches whispers and breaths
active = db > -55.0

# Dilate: pad 0.4 s before and after any active frame
pad = int(0.4 / 0.05)
kernel = np.ones(2 * pad + 1, dtype=bool)
dilated = np.convolve(active, kernel, mode="same") > 0

# Per-frame weight (1 = instrumental), smoothed to ~0.5 s fades
w = dilated.astype(np.float32)
smooth = int(0.5 / 0.05)
k = np.hanning(2 * smooth + 1)
k /= k.sum()
w = np.convolve(w, k, mode="same")
w = np.clip(w, 0.0, 1.0)
# Never let a detected voice frame fall below full instrumental
w[dilated] = np.maximum(w[dilated], 1.0)

# Expand to samples
ws = np.repeat(w, win)
ws = np.pad(ws, (0, n - len(ws)), mode="edge")
if orig.ndim > 1:
    ws = ws[:, None]

out = ws * inst + (1.0 - ws) * orig
sf.write(OUT, out, sr)

voiced = dilated.mean()
print(f"frames voiced (with padding): {voiced * 100:.1f}%")
print(f"pure original share: {(w == 0).mean() * 100:.1f}%")
print(f"written: {OUT}, {n / sr:.1f}s")
