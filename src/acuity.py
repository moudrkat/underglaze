"""How much of the tile does an eye actually receive, from where you stand?

The page counts 62 815 cosines. That is the photograph's count. A person in
the room has their own low-pass filter: at best the eye separates two lines
one arcminute apart, so at distance d it cannot resolve anything finer than

    w(d) = d * tan(1 arcmin)

One arcminute is 20/20 vision on a high-contrast grating, which is generous --
real contrast sensitivity falls off well before the acuity limit, so every
number below is an upper bound on what is seen, not an estimate.

A feature of width w on a tile of side L is a cosine of order k = L / 2w, so
the eye's cutoff turns straight into a cutoff K, and the page's own curve turns
it into a number of cosines.
"""
import numpy as np

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fourier import orbits

ARCMIN = np.pi / (180 * 60)
L_MM = 150.0                 # the tile is 150 mm across
PHOTO_UM_PER_PX = 85.0       # from theory/scales.md


def resolvable_mm(d_m):
    return d_m * np.tan(ARCMIN) * 1000.0


def K_of(d_m, L=L_MM):
    return L / (2.0 * resolvable_mm(d_m))


def cosines(K):
    return sum(1 if uv == (0, 0) else s // 2 for uv, s, _ in orbits(min(K, 200)))


def run(ds=(0.25, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0)):
    out = []
    for d in ds:
        w = resolvable_mm(d)
        K = K_of(d)
        out.append({"d": d, "mm": round(w, 3), "px": round(w * 1000 / PHOTO_UM_PER_PX, 1),
                    "K": round(K, 1), "cos": cosines(int(round(K))),
                    "capped": K > 200})
    return out


if __name__ == "__main__":
    print("eye: 1 arcmin, generous.  tile %.0f mm.  photo %.0f um/px."
          % (L_MM, PHOTO_UM_PER_PX))
    print()
    print("  %7s %10s %10s %8s %12s" % ("d [m]", "finest mm", "in photo px", "K", "cosines"))
    for r in run():
        print("  %7.2f %10.3f %10.1f %8s %12s"
              % (r["d"], r["mm"], r["px"],
                 ">200" if r["capped"] else "%.0f" % r["K"],
                 "all 62 815" if r["capped"] else "%d" % r["cos"]))
    e = next(r for r in run() if r["px"] >= 1.0)
    print("\n  the eye first falls behind the photograph at about %.2f m." % e["d"])
