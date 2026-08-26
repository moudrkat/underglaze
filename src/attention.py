"""Does attention find the wallpaper group without being told there is one?

Softmax attention has no notion of geometry. It sees a set of vectors and
scores them by similarity. Give it the tile cut into patches, with no positions
and no learned weights -- Q = K = the patch itself -- and ask a narrow question:

    where does a patch send its attention?

The tile is p4. Every patch has three partners, its images under the quarter
turns about the four-fold centre. If attention lands on those partners more
than chance allows, then a mechanism that knows nothing about rotation has
recovered the symmetry group from similarity alone.

The control decides it. The same computation is run on a tile whose patches
have been shuffled, which destroys p4 and keeps the marginal statistics. If
the shuffled tile scores the same, the effect is arithmetic, not geometry.

beta is the slider: the inverse temperature of the softmax. At beta = 0 the
attention is uniform and finds nothing by construction. Large beta collapses
it onto the single nearest patch. The question is what happens between.
"""
import numpy as np

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask
from fourier import N, C, p4_symmetrise

P, S, M = 48, 25, 8          # patch size, grid stride, half-grid extent


def grid():
    """Patch centres, symmetric about the four-fold centre so p4 maps grid to grid."""
    ks = [k for k in range(-M, M + 1)]
    return [(a, b) for a in ks for b in ks]


def patches(img):
    cells = grid()
    X = []
    for a, b in cells:
        y, x = C + a * S, C + b * S
        X.append(img[y - P // 2:y + P // 2, x - P // 2:x + P // 2].ravel())
    return np.stack(X).astype(float), cells


def orbit_index(cells):
    """For each patch, the indices of its three quarter-turn partners."""
    pos = {c: i for i, c in enumerate(cells)}
    out = []
    for (a, b) in cells:
        out.append([pos[(-b, a)], pos[(-a, -b)], pos[(b, -a)]])
    return np.array(out)


def attention(X, beta):
    Z = X - X.mean(1, keepdims=True)
    Z /= np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-9)
    Sc = Z @ Z.T                                   # cosine similarity, no learned weights
    np.fill_diagonal(Sc, -np.inf)                  # a patch may not attend to itself
    Sc = Sc - np.nanmax(Sc[np.isfinite(Sc)])
    A = np.exp(beta * Sc)
    A[~np.isfinite(A)] = 0.0
    return A / A.sum(1, keepdims=True)


def orbit_mass(A, orb):
    return float(np.mean([A[i, orb[i]].sum() for i in range(len(A))]))


def entropy(A):
    p = np.clip(A, 1e-300, 1)
    return float(np.mean(-(p * np.log(p)).sum(1)) / np.log(A.shape[1] - 1))


def run(betas=(0, 2, 5, 10, 20, 40, 80, 160, 320)):
    m = p4_symmetrise(ink_mask(n=N).astype(float))
    X, cells = patches(m)
    orb = orbit_index(cells)
    rng = np.random.default_rng(0)
    Xs = X[rng.permutation(len(X))]                # same patches, p4 destroyed
    chance = 3.0 / (len(X) - 1)
    out = []
    for b in betas:
        A, As = attention(X, b), attention(Xs, b)
        out.append({"beta": b, "entropy": round(entropy(A), 4),
                    "orbit": round(orbit_mass(A, orb), 4),
                    "control": round(orbit_mass(As, orb), 4),
                    "lift": round(orbit_mass(A, orb) / chance, 2),
                    "control_lift": round(orbit_mass(As, orb) / chance, 2)})
    return out, chance, len(X)


if __name__ == "__main__":
    rows, chance, n = run()
    print("%d patches of %dx%d, stride %d.  chance orbit mass = 3/%d = %.4f"
          % (n, P, P, S, n - 1, chance))
    print()
    print("  %6s %10s %10s %10s %8s %8s"
          % ("beta", "entropy", "orbit", "shuffled", "lift", "ctrl"))
    for r in rows:
        print("  %6d %10.4f %10.4f %10.4f %7.1fx %7.1fx"
              % (r["beta"], r["entropy"], r["orbit"], r["control"],
                 r["lift"], r["control_lift"]))
