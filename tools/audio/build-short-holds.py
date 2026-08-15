"""Final build: shortened holds + optimized no-fire segment boundaries."""
import numpy as np
import soundfile as sf

BLENDED = "/tmp/blended.wav"
FULL_START = 110.0
FADE = 3.0

CUTS = [  # from build_short2 search
    (471.70, 485.20),
    (523.95, 529.95),
    (732.05, 746.05),
    (770.75, 776.75),
    (805.25, 809.25),
]

audio, sr = sf.read(BLENDED, dtype="float32")
mono = audio.mean(axis=1)


def features(t, fade):
    i = int(t * sr)
    w = mono[i:i + int(fade * sr)]
    hop = int(0.05 * sr)
    fr = len(w) // hop
    rms = np.sqrt((w[:fr * hop].reshape(fr, hop) ** 2).mean(axis=1))
    spec = np.abs(np.fft.rfft(w * np.hanning(len(w))))
    spec = np.log10(spec + 1e-9)
    k = np.ones(64) / 64
    spec = np.convolve(spec, k, mode="same")[::32]
    return rms, spec


def cosine(a, b):
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / d) if d > 0 else 0.0


def corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0


def score(ta, tb, fade):
    ra, sa = features(ta, fade)
    rb, sb = features(tb, fade)
    la = 20 * np.log10(ra.mean() + 1e-9)
    lb = 20 * np.log10(rb.mean() + 1e-9)
    return (0.4 * corr(ra, rb) + 0.6 * cosine(sa, sb)
            - 0.08 * abs(la - lb))


def best_boundary(a_lo, a_hi, b_lo, b_hi, fade):
    best = (-9, None, None)
    for a in np.arange(a_lo, a_hi, 0.25):
        for b in np.arange(b_lo, b_hi, 0.25):
            s = score(a, b, fade)
            if s > best[0]:
                best = (s, a, b)
    return best


# search both no-fire boundaries, 4 s fades there
s1, a1, b1 = best_boundary(305.0, 317.0, 439.0, 451.0, 4.0)
s2, a2, b2 = best_boundary(566.0, 578.0, 693.0, 705.0, 4.0)
print(f"A->B boundary: {a1:.2f} -> {b1:.2f} (score {s1:.3f})")
print(f"B->C boundary: {a2:.2f} -> {b2:.2f} (score {s2:.3f})")


def render(pieces_spec, path):
    """pieces_spec: list of (start, end, fade_at_join_before_this_piece)."""
    pieces = []
    for (s, e, fd) in pieces_spec:
        pos = s
        for a, b in CUTS:
            if pos < a < e:
                pieces.append((pos, a, fd if not pieces or pieces[-1][1] != pos else FADE))
                fd = FADE
                pos = max(pos, min(b, e))
        pieces.append((pos, e, fd))
    # first piece's fade unused
    out = audio[int(pieces[0][0] * sr):int(pieces[0][1] * sr)].copy()
    joins = []
    for s, e, fd in pieces[1:]:
        head = audio[int(s * sr):int(e * sr)]
        n = min(int(fd * sr), len(out), len(head))
        joins.append((len(out) - n, fd))
        t = np.linspace(0, np.pi / 2, n, dtype=np.float32)[:, None]
        out[-n:] = out[-n:] * np.cos(t) + head[:n] * np.sin(t)
        out = np.concatenate([out, head[n:]])
    n = int(0.5 * sr)
    out[:n] *= np.linspace(0, 1, n, dtype=np.float32)[:, None]
    out[-n:] *= np.linspace(1, 0, n, dtype=np.float32)[:, None]
    sf.write(path, out, sr)
    print(f"{path}: {len(out) / sr:.1f}s")
    m = out.mean(axis=1)
    for j, fd in joins:
        t0 = j / sr
        levels = []
        for off in np.arange(-2.0, fd + 2.0, 0.25):
            i = int((t0 + off) * sr)
            w = m[max(0, i):i + sr]
            levels.append(20 * np.log10(np.sqrt((w ** 2).mean()) + 1e-9))
        jump = max(abs(np.diff(levels)))
        print(f"  join @{t0:7.2f}s: max RMS step {jump:.2f} dB "
              f"{'OK' if jump < 3 else 'CHECK'}")


end = len(audio) / sr
render([(FULL_START, end, FADE)], "/tmp/breathing-short.wav")

# fix the cut-piece fade bookkeeping simply: boundaries get 4 s, holds 3 s
render([(222.0, a1, FADE), (b1, a2, 4.0), (b2, end, 4.0)],
       "/tmp/breathing-no-fire-short.wav")
