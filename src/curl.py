"""Is a higher chi actually more twisted?

chi measures how far the coefficients are from mirror symmetry. "Twisted" is a
claim about the tendrils, which is not the same thing. So measure the tendrils.

Mean signed curvature along the ink skeleton, length-weighted. A quarter turn
preserves the sign of curvature, so a p4 tile does not cancel itself out; a
mirror flips it, so a p4m tile must give exactly zero. That zero is the check
on the measurement, not a result.
"""
import numpy as np

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask, thin, polylines
from fourier import p4_symmetrise, centred, coefficients, synth, N, C
from chirality import knob, chi


def smooth(p, k=9):
    if len(p) < k + 2:
        return None
    a = np.asarray(p, float)
    ker = np.ones(k) / k
    return np.stack([np.convolve(a[:, i], ker, mode="valid") for i in (0, 1)], 1)


def mean_signed_curvature(mask, min_len=28):
    """Sum of signed turning divided by total arc length, in rad/px."""
    paths = polylines(thin(mask), min_len=min_len)
    turn = length = 0.0
    n = 0
    for p in paths:
        s = smooth(p)
        if s is None or len(s) < 3:
            continue
        d = np.diff(s, axis=0)
        seg = np.hypot(d[:, 0], d[:, 1])
        good = seg > 1e-9
        d, seg = d[good], seg[good]
        if len(d) < 2:
            continue
        cross = d[:-1, 0] * d[1:, 1] - d[:-1, 1] * d[1:, 0]
        dot = (d[:-1] * d[1:]).sum(1)
        turn += np.arctan2(cross, dot).sum()
        length += seg.sum()
        n += 1
    return (turn / length if length else 0.0), n, length


if __name__ == "__main__":
    m = ink_mask(n=N).astype(float)
    F = coefficients(centred((p4_symmetrise(m) > 0.5).astype(float)))
    print("  %6s %8s %14s %8s %10s" % ("t", "chi", "curl [rad/px]", "paths", "length"))
    for t in (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5):
        G = knob(F, t)
        ink = np.roll(synth(G, 200), (C, C), axis=(0, 1)) > 0.5
        c, n, L = mean_signed_curvature(ink)
        print("  %6.2f %8.3f %14.5f %8d %10.0f" % (t, chi(G), c, n, L))
