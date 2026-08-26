"""The wall: nine tiles of the same pattern, and what differs between them.

data/wall.jpg sat unused. It answers a question the page asserts and never
measured -- whether this pattern was printed or painted. A print from an
engraved plate is identical on every tile; a brush is not. So find the lattice,
cut the tiles out, and correlate them against each other, with the same
controls src/symmetry.py used.

Order matters. The lattice is found first, from the autocorrelation of the
photograph, before any tile is cut -- so the cutting cannot invent agreement
that is not there.
"""
import numpy as np
from PIL import Image

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

WALL = "data/wall.jpg"


def load(path=WALL, long_side=1200):
    im = Image.open(path).convert("L")
    s = long_side / max(im.size)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return np.asarray(im, float), s


def flatten(A, sigma=40.0):
    """Kill the lighting gradient and the specular highlight, keep the ink."""
    F = np.fft.fft2(A)
    ky = np.fft.fftfreq(A.shape[0])[:, None] * A.shape[0]
    kx = np.fft.fftfreq(A.shape[1])[None, :] * A.shape[1]
    R = np.hypot(ky / A.shape[0], kx / A.shape[1]) * max(A.shape)
    hi = np.real(np.fft.ifft2(F * (1 - np.exp(-(R / (max(A.shape) / sigma)) ** 2))))
    return hi / (hi.std() + 1e-9)


def autocorr(Z):
    F = np.fft.fft2(Z)
    a = np.real(np.fft.ifft2(F * np.conj(F)))
    return np.fft.fftshift(a / a.max())


def lattice(Z, lo=90, hi=400):
    """The two shortest non-trivial autocorrelation peaks."""
    a = autocorr(Z)
    cy, cx = np.array(a.shape) // 2
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    r = np.hypot(yy - cy, xx - cx)
    m = (r > lo) & (r < hi)
    cand = []
    b = np.where(m, a, -np.inf)
    for _ in range(12):
        i = np.unravel_index(np.argmax(b), b.shape)
        cand.append((float(b[i]), int(i[0] - cy), int(i[1] - cx)))
        b[max(0, i[0] - 25):i[0] + 25, max(0, i[1] - 25):i[1] + 25] = -np.inf
    cand = [c for c in cand if c[1] >= 0]                  # one of each antipodal pair
    cand.sort(key=lambda c: -c[0])
    return cand, a


def report():
    A, s = load()
    Z = flatten(A)
    print("wall.jpg resampled to %dx%d  (scale %.3f)" % (A.shape[1], A.shape[0], s))
    cand, a = lattice(Z)
    print("\nautocorrelation peaks  (dy, dx in px, correlation)")
    for c, dy, dx in cand[:8]:
        print("   %+5d %+5d   %.3f   |v| = %.0f px" % (dy, dx, c, np.hypot(dy, dx)))
    return A, Z, cand


if __name__ == "__main__":
    report()
