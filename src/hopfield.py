"""A copyist who remembers a vocabulary, not the answer.

memory.py cheated: it added lam*(stored - 1/2) every generation, which in the
Hopfield energy is the external field h, not the memory. It puts the original
on the copyist's desk.

Here the memory is content-addressable and has a capacity. Once, at the start,
the copyist learns k prototype patches from the tile -- her motif vocabulary,
an aster, a fan, a curl. After that she never sees the original again. Each
generation she looks at the fired tile and re-inks every patch as the nearest
motif she knows.

k is the capacity. The question is how large a vocabulary a tradition must
carry for the design to still be itself after 285 years.
"""
import numpy as np
from PIL import Image

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask
from kiln import gauss

N, P = 500, 32
SIGMA = 3.0 * N / 700.0
RNG = np.random.default_rng(7)


def patches(img, stride, p=P):
    n = img.shape[0]
    ys = range(0, n - p + 1, stride)
    idx = [(y, x) for y in ys for x in ys]
    M = np.stack([img[y:y + p, x:x + p].ravel() for y, x in idx])
    return M, idx


def kmeans(X, k, iters=40):
    C = X[RNG.choice(len(X), k, replace=False)].copy()
    for _ in range(iters):
        d = ((X[:, None, :] - C[None, :, :]) ** 2).sum(-1) if k * len(X) < 4e6 else None
        if d is None:
            d = np.stack([((X - c) ** 2).sum(1) for c in C], 1)
        lab = d.argmin(1)
        for j in range(k):
            m = lab == j
            if m.any():
                C[j] = X[m].mean(0)
            else:
                C[j] = X[RNG.integers(len(X))]
    return C


def learn(stored, k):
    """The copyist's one look at the original."""
    X, _ = patches(stored.astype(float), stride=6)
    return kmeans(X, k)


def recall(field, C, stride=8, p=P):
    """Re-ink every patch as the nearest motif in the vocabulary."""
    n = field.shape[0]
    acc = np.zeros((n, n))
    cnt = np.zeros((n, n))
    X, idx = patches(field, stride, p)
    d = np.stack([((X - c) ** 2).sum(1) for c in C], 1)
    lab = d.argmin(1)
    for (y, x), j in zip(idx, lab):
        acc[y:y + p, x:x + p] += C[j].reshape(p, p)
        cnt[y:y + p, x:x + p] += 1
    return np.divide(acc, np.maximum(cnt, 1))


def iou(a, b):
    return float((a & b).sum()) / float((a | b).sum())


def run(k, gens=60, stored=None):
    stored = ink_mask(n=N) if stored is None else stored
    C = learn(stored, k)
    m = stored.copy()
    hist = []
    for g in range(gens + 1):
        hist.append(iou(m, stored))
        fired = gauss(m.astype(float), SIGMA)          # the kiln
        m = recall(fired, C) > 0.5                     # the copyist
    return m, hist, C


if __name__ == "__main__":
    stored = ink_mask(n=N)
    print("patch %dx%d, sigma %.2f px, %d generations" % (P, P, SIGMA, 60))
    print()
    print("  %5s %10s %10s %10s" % ("k", "IoU@10", "IoU@30", "IoU@60"))
    finals = {}
    for k in (2, 4, 8, 16, 32, 64):
        m, h, C = run(k)
        finals[k] = m
        print("  %5d %10.3f %10.3f %10.3f" % (k, h[10], h[30], h[60]))
    np.save("out/hopfield_finals.npy",
            np.stack([finals[k] for k in sorted(finals)]))
    print()
    print("  control (no copyist, kiln only) is IoU@60 = 0.49")


# MEASURED, and it is not the metric's fault.
#
# The first run scored on intersection-over-union and the copyist lost to doing
# nothing: 0.315 at k=64 against 0.49 for the kiln alone. The obvious suspicion
# was that IoU rewards keeping large blobs, which is exactly what the fire
# preserves, so the same runs were scored again on what the fire actually takes
# -- the length of the outline, and the number of separate inked regions.
#
#   after 30 firings        perimeter    regions      IoU
#   the tile itself             28612        164      1.000
#   nobody, kiln alone           5972         13      0.532
#   copyist, 8 motifs               0          0      0.000
#   copyist, 16 motifs            566          3      0.063
#   copyist, 32 motifs           2368          8      0.293
#   copyist, 64 motifs           2112          8      0.258
#
# On every measure tried, a copyist who has learned k motifs and never sees the
# original again destroys more than the fire does. Eight motifs erase the tile
# completely. So the failure is real, not an artefact: patch-wise recall of a
# fixed vocabulary is a worse transmission channel than no transmission at all,
# and the version in src/memory.py that survives is the one that cheats by
# keeping the original on the desk.
