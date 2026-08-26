"""The half in "blue where f > 1/2" is a choice. What does it decide?

Lower the threshold and the ink grows. Somewhere it stops being separate
flowers and becomes one connected thing that reaches from edge to edge. That
crossing is a percolation transition, and it is sharp: the largest connected
component jumps rather than drifts.

The tile is not random, so the textbook threshold does not apply and is not
quoted. What is measured is where THIS pattern crosses, and how far the
painter's own half sits from it.
"""
import numpy as np

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask
from fourier import N, C, p4_symmetrise, centred, coefficients, synth


def field():
    m = p4_symmetrise(ink_mask(n=N).astype(float))
    F = coefficients(centred(m))
    f = np.roll(synth(F, 200), (C, C), axis=(0, 1))
    return (f - f.min()) / (f.max() - f.min())


def components(mask):
    """Label 4-connected components by iterated propagation of the max index."""
    lab = np.where(mask, np.arange(mask.size).reshape(mask.shape) + 1, 0)
    while True:
        nxt = lab.copy()
        for ax in (0, 1):
            for sh in (-1, 1):
                nxt = np.maximum(nxt, np.where(mask, np.roll(lab, sh, ax), 0))
        nxt = np.where(mask, nxt, 0)
        if np.array_equal(nxt, lab):
            return lab
        lab = nxt


def measure(f, theta):
    m = f > theta
    if not m.any():
        return {"theta": theta, "ink": 0.0, "n": 0, "big": 0.0, "spans": False}
    lab = components(m)
    ids, cnt = np.unique(lab[m], return_counts=True)
    big = ids[np.argmax(cnt)]
    B = lab == big
    spans = bool((B[0].any() and B[-1].any()) or (B[:, 0].any() and B[:, -1].any()))
    return {"theta": round(theta, 3), "ink": round(float(m.mean()), 4),
            "n": int(len(ids)), "big": round(float(cnt.max() / m.sum()), 4),
            "spans": spans}


def run(thetas=None):
    f = field()
    thetas = np.linspace(0.75, 0.25, 26) if thetas is None else thetas
    return [measure(f, t) for t in thetas]


if __name__ == "__main__":
    rows = run()
    print("  %7s %8s %8s %10s %8s" % ("theta", "ink", "pieces", "largest", "spans"))
    for r in rows:
        print("  %7.3f %8.4f %8d %10.4f %8s"
              % (r["theta"], r["ink"], r["n"], r["big"], "yes" if r["spans"] else "-"))
    first = next((r for r in rows if r["spans"]), None)
    if first:
        print("\n  first spans at theta = %.3f, ink %.3f" % (first["theta"], first["ink"]))
