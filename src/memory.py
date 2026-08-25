"""Does the copyist need to remember, and how much?

One generation, now with a copyist who is not a photocopier:

    m_next = [ blur(m, sigma)  +  lam * (stored - 1/2) ]  >  1/2

lam = 0 is the pure MBO curvature flow of kiln.py: the fire wins and the
design is eaten. lam > 0 is a Hopfield-style pull toward a stored pattern --
the copyist knows what a cibulak is supposed to look like and inks that.

The question is whether there is a critical lam. If there is, then a motif
surviving three centuries is not a matter of luck or beauty; it is a motif
whose carriers remembered it hard enough to beat a diffusion constant.
"""
import numpy as np
from PIL import Image

from trace import ink_mask
from kiln import gauss, perimeter

N = 500
TILE_MM = 150.0


def iou(a, b):
    return float((a & b).sum()) / float((a | b).sum())


def evolve(stored, sigma, lam, gens=60, keep=()):
    m = stored.copy()
    frames, hist = {}, []
    for g in range(gens + 1):
        if g in keep:
            frames[g] = m.copy()
        hist.append((g, iou(m, stored), m.mean(), perimeter(m)))
        m = (gauss(m.astype(float), sigma) + lam * (stored.astype(float) - 0.5)) > 0.5
    return m, frames, hist


if __name__ == "__main__":
    stored = ink_mask(n=N)
    sigma = 3.0 * N / 700.0          # same physical bleed as kiln.py
    print("sigma = %.2f px = %.3f mm per firing, %d px tile" % (sigma, sigma*TILE_MM/N, N))
    print()
    print("  %6s %10s %10s %12s" % ("lam", "IoU@60", "ink@60", "perim@60"))
    for lam in (0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.50):
        m, _, hist = evolve(stored, sigma, lam, gens=60)
        g, i, ink, per = hist[-1]
        print("  %6.2f %9.3f %9.1f%% %12d" % (lam, i, 100*ink, per))


def mean_width(m):
    """Mean stroke width in px. For elongated ink, 2*area/perimeter."""
    return 2.0 * m.sum() / max(perimeter(m), 1)


def law(gens=60):
    """Is the surviving stroke width  w* = C * sigma / sqrt(lam) ?"""
    stored = ink_mask(n=N)
    rows = []
    print("  %7s %7s %10s %10s" % ("sigma", "lam", "w* [px]", "w*[mm]"))
    for sigma in (1.5, 2.14, 3.0, 4.2):
        for lam in (0.05, 0.10, 0.20, 0.40):
            m, _, _ = evolve(stored, sigma, lam, gens=gens)
            w = mean_width(m)
            rows.append((sigma, lam, w))
            print("  %7.2f %7.2f %10.2f %10.3f" % (sigma, lam, w, w*TILE_MM/N))
    s = np.array([r[0] for r in rows])
    l = np.array([r[1] for r in rows])
    w = np.array([r[2] for r in rows])
    # fit  log w = log C + a log sigma + b log lam
    A = np.stack([np.ones_like(s), np.log(s), np.log(l)], 1)
    coef, *_ = np.linalg.lstsq(A, np.log(w), rcond=None)
    pred = np.exp(A @ coef)
    print()
    print("  fit  w* = %.2f * sigma^%.2f * lam^%.2f" % (np.exp(coef[0]), coef[1], coef[2]))
    print("  expected exponents:  sigma^1.00  lam^-0.50")
    print("  max relative error   %.1f%%" % (100*np.max(np.abs(pred-w)/w)))
