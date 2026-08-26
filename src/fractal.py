"""Is the tile a fractal?

Someone looked at the tendrils and asked. It is a testable claim, so it is
tested rather than argued, the same way src/symmetry.py tested the wallpaper
group: apply the transform, correlate, and put a meaningless control next to
the answer.

A fractal needs a dilation symmetry -- the pattern reappearing when you zoom.
Two independent tests, plus one that failed:

  1. box counting     a fractal boundary has a PLATEAU in the local slope of
                      log N(eps) vs log eps. A dense pattern of ordinary
                      smooth curves has no plateau: the slope climbs from 1
                      (curve) to 2 (the boxes just cover the tile). The
                      control is the tile's OWN band-limited reconstruction,
                      which is a finite sum of cosines and therefore analytic,
                      so its level sets are provably smooth curves, D = 1.

  2. dilation         correlate the tile against itself viewed through a
                      window s times smaller, about the same four-fold centre.
                      Self-similar => stays high. Compare against the mirror
                      and shift controls already in theory/symmetry.md.

  3. Porod slope      the high-k spectral exponent should steepen for a smooth
                      boundary. It does not separate the cases here -- kept and
                      reported as inconclusive, not quietly dropped.

There is also a structural answer, which the measurements only confirm: f is a
FINITE sum of cosines, hence real-analytic, so {f = theta} is an analytic curve
with box dimension exactly 1 for every cutoff K. No number of cosines makes it
fractal. And p4 is a crystallographic group -- discrete translations and a
finite point group. It contains no dilation. Scale symmetry was excluded the
moment the group was measured.
"""
import numpy as np
from PIL import Image

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask, TILE, CENTRE, HALF
from symmetry import load, crop, corr
import fourier as F4

EPS = [1, 2, 4, 8, 16, 32, 64, 128]
N = 1400


def boundary(m):
    """The pixels where the ink changes to glaze."""
    b = np.zeros_like(m)
    b[:-1, :] |= m[:-1, :] ^ m[1:, :]
    b[:, :-1] |= m[:, :-1] ^ m[:, 1:]
    return b


def counts(b, epss=EPS):
    out = []
    for eps in epss:
        n = b.shape[0]
        k = n // eps * eps
        z = b[:k, :k].reshape(k // eps, eps, k // eps, eps)
        out.append(int(z.any(axis=(1, 3)).sum()))
    return out


def local_slopes(b, epss=EPS):
    """D estimated separately in each octave. A fractal holds one value."""
    N_ = counts(b, epss)
    return [-(np.log(N_[i + 1]) - np.log(N_[i])) /
            (np.log(epss[i + 1]) - np.log(epss[i])) for i in range(len(epss) - 1)]


def koch(order=7, n=N):
    """A real fractal, rasterised at the same resolution. D = log4/log3 = 1.262."""
    pts = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3) / 2], [0, 0]], float)
    R = np.array([[0.5, -np.sqrt(3) / 2], [np.sqrt(3) / 2, 0.5]])
    for _ in range(order):
        out = []
        for a, b in zip(pts[:-1], pts[1:]):
            d = (b - a) / 3
            out += [a, a + d, a + d + R @ d, a + 2 * d]
        out.append(pts[-1])
        pts = np.array(out)
    p = (pts - pts.min(0)) / (pts.max(0) - pts.min(0)).max() * (n - 4) + 2
    img = np.zeros((n, n), bool)
    for a, b in zip(p[:-1], p[1:]):
        t = np.linspace(0, 1, int(max(abs(b - a).max(), 1) * 2) + 2)
        q = (a[None, :] * (1 - t[:, None]) + b[None, :] * t[:, None]).astype(int)
        img[q[:, 1], q[:, 0]] = True
    return img


def analytic_control(ink_fraction, K=48, n=N):
    """The tile's own band-limited reconstruction, thresholded to the same ink.

    A finite cosine sum is analytic, so this boundary is a smooth curve by
    construction -- and it has the tile's density, spacing and stroke width,
    which a circle does not. If the tile scores like this, the score is not
    telling us about fractality.
    """
    m = ink_mask(n=F4.N).astype(float)
    F = F4.coefficients(F4.centred(F4.p4_symmetrise(m)))
    f = F4.synth(F, K)
    th = np.percentile(f, 100 * (1 - ink_fraction))
    big = Image.fromarray(((f > th).astype(np.uint8) * 255)).resize((n, n), Image.NEAREST)
    return np.asarray(big) > 127


def smooth_field(ink_fraction, n=N, sigma=18.0, seed=0):
    """Filtered noise: no structure at all, but the same slow crossover."""
    z = np.fft.fft2(np.random.default_rng(seed).standard_normal((n, n)))
    k = np.fft.fftfreq(n) * n
    U, V = np.meshgrid(k, k, indexing="ij")
    s = np.real(np.fft.ifft2(z * np.exp(-(np.hypot(U, V) / sigma) ** 2)))
    return s > np.percentile(s, 100 * (1 - ink_fraction))


def dilation_scores(scales=(1.19, 1.41, 1.68, 2.0, 2.38, 2.83, 4.0), n=512):
    """Correlate the tile with a zoomed view of itself about the C4 centre."""
    A = load(TILE)
    cx, cy = CENTRE
    z = crop(A, cx, cy, HALF, n=n)
    out = {}
    for s in scales:
        zz = crop(A, cx, cy, HALF / s, n=n)
        out[s] = None if zz is None else corr(z, zz)
    return z, out


def porod_slope(mask, lo=20, hi=250):
    """Shell-summed spectral energy. -2 is Porod's law for a smooth boundary."""
    n = mask.shape[0]
    z = mask.astype(float)
    z -= z.mean()
    P = np.abs(np.fft.fft2(z)) ** 2
    k = np.fft.fftfreq(n) * n
    U, V = np.meshgrid(k, k, indexing="ij")
    w = np.bincount(np.hypot(U, V).astype(int).ravel(), weights=P.ravel(), minlength=n)
    kk = np.arange(n)[lo:hi]
    return float(np.polyfit(np.log(kk), np.log(np.maximum(w[lo:hi], 1e-300)), 1)[0])


def report():
    m = ink_mask(n=N)
    frac = m.mean()

    print("1. box counting -- D measured separately in each octave")
    print("   a fractal holds one value; a dense set of smooth curves climbs 1 -> 2")
    print()
    print("   %-32s %s" % ("", "  ".join("%3d-%-3d" % (EPS[i], EPS[i + 1])
                                         for i in range(len(EPS) - 1))))
    rows = [("the tile", boundary(m)),
            ("band-limited K=48  (D=1 exactly)", boundary(analytic_control(frac))),
            ("filtered noise     (D=1)", boundary(smooth_field(frac))),
            ("Koch curve         (D=1.262)", koch()),
            ("circle             (D=1)", boundary(
                (lambda yy, xx: xx ** 2 + yy ** 2 < 0.16)(*(np.mgrid[0:N, 0:N] / N - 0.5)))),
            ]
    for label, b in rows:
        print("   %-32s %s" % (label, "  ".join("%6.2f " % s for s in local_slopes(b))))
    print()
    print("   the tile tracks the two D=1 controls octave for octave.")
    print("   only the Koch curve is flat, which is what scale invariance looks like.")
    print()

    print("2. dilation about the four-fold centre")
    z, sc = dilation_scores()
    for s, c in sc.items():
        print("   zoom x%-5.2f    %s" % (s, "out of frame" if c is None else "%+.3f" % c))
    print("   controls")
    rnd = np.random.default_rng(0).permutation(z.reshape(-1)).reshape(z.shape)
    print("   %-14s %+.3f" % ("shuffled", corr(z, rnd)))
    print("   %-14s %+.3f" % ("shift 37 px", corr(z, np.roll(z, 37, axis=0))))
    print("   %-14s %+.3f" % ("mirror", corr(z, np.fliplr(z))))
    print("   %-14s %+.3f" % ("rot90 (p4)", corr(z, np.rot90(z))))
    print()
    print("   every zoom sits at or below the meaningless-shift control, while the")
    print("   quarter turn the tile does have scores +0.54. there is no scale symmetry.")
    print()

    print("3. Porod slope -- INCONCLUSIVE, kept")
    print("   the tile          %+.2f" % porod_slope(m))
    print("   band-limited K=48 %+.2f   (smooth boundary, must be -2)" % porod_slope(analytic_control(frac)))
    k = koch()
    fill = np.zeros_like(k)
    for row in range(N):
        xs = np.flatnonzero(k[row])
        if len(xs) > 1:
            fill[row, xs[0]:xs[-1] + 1] = True
    print("   Koch interior     %+.2f   (D=1.262)" % porod_slope(fill))
    print("   -1.85 against -1.80 and -2.01 does not separate the hypotheses. the")
    print("   photograph's jpeg noise biases the tail shallow by an unknown amount,")
    print("   so this test decides nothing and is reported as deciding nothing.")
    print()

    print("verdict: not a fractal. it is broadband, which is not the same thing --")
    print("         structure runs over about two decades of scale and then stops.")


if __name__ == "__main__":
    report()
