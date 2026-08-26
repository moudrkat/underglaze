"""Replace the tile plank by plank. When does it stop being the tile?

The spectrum turned out to be generic: src/fractal.py measured the tail at
k^-1.85 against k^-2.01 for a smooth boundary, which is Porod's law and holds
for anything with edges. If the magnitudes |a_mn| carry no identity, then all
of it is in the signs -- and the ship can be rebuilt from its own timber and
come back a different ship.

So: keep every magnitude exactly, flip a fraction p of the signs, and score
against the original. Three orders, because which planks you replace first is
the whole question:

    fine first    the small coefficients, the detail
    coarse first  the big ones, the layout
    random        no preference

The floor is not zero. Two unrelated patterns at the same ink fraction still
overlap by chance, and that number is measured here rather than assumed.
"""
import numpy as np

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask
from fourier import N, C, p4_symmetrise, centred, coefficients, synth, orbits, band

K = 120


def setup():
    m = p4_symmetrise(ink_mask(n=N).astype(float))
    F = coefficients(centred(m))
    ref = np.roll(synth(F, K), (C, C), axis=(0, 1)) > 0.5
    return F, ref, float(ref.mean())


def iou(a, b):
    u = np.count_nonzero(a | b)
    return np.count_nonzero(a & b) / u if u else 0.0


def flip(F, keys, ink, seed=0):
    """Flip the sign of the given orbits, then re-threshold to the same ink."""
    G = F.copy()
    rng = np.random.default_rng(seed)
    for (u, v) in keys:
        s = -1.0 if rng.random() < 0.5 else 1.0     # a random plank, not a flipped one
        for (p, q) in {(u, v), (-v, u), (-u, -v), (v, -u)}:
            G[p % N, q % N] = s * G[p % N, q % N]
    f = np.roll(synth(G, K), (C, C), axis=(0, 1))
    return f > np.percentile(f, 100 * (1 - ink))


def run(fracs=np.linspace(0, 1, 21)):
    F, ref, ink = setup()
    orb = [uv for uv, _, _ in orbits(K) if uv != (0, 0)]
    mag = {uv: abs(F[uv[0] % N, uv[1] % N].real) for uv in orb}
    fine = sorted(orb, key=lambda uv: (uv[0] ** 2 + uv[1] ** 2), reverse=True)
    coarse = list(reversed(fine))
    rng = np.random.default_rng(1)
    rand = [tuple(x) for x in np.array(orb)[rng.permutation(len(orb))]]

    rows = []
    for p in fracs:
        n = int(round(p * len(orb)))
        rows.append({"p": round(float(p), 3),
                     "fine": round(iou(flip(F, fine[:n], ink, seed=3), ref), 4),
                     "coarse": round(iou(flip(F, coarse[:n], ink, seed=3), ref), 4),
                     "random": round(iou(flip(F, rand[:n], ink, seed=3), ref), 4)})
    # chance floor: two independent full sign-scrambles
    a = flip(F, orb, ink, seed=11)
    b = flip(F, orb, ink, seed=22)
    return rows, round(iou(a, b), 4), ink, len(orb)


if __name__ == "__main__":
    rows, floor, ink, n = run()
    print("K=%d, %d orbits, ink held at %.3f" % (K, n, ink))
    print("chance floor (two unrelated sign-scrambles): IoU %.4f\n" % floor)
    print("  %8s %10s %10s %10s" % ("replaced", "fine first", "coarse 1st", "random"))
    for r in rows:
        print("  %7.0f%% %10.4f %10.4f %10.4f"
              % (100 * r["p"], r["fine"], r["coarse"], r["random"]))
