"""Which wallpaper group is the tile in?

The answer decides the Fourier basis everything else is written in, so it is
measured, not assumed. Test: align a crop to itself under each symmetry of the
square and correlate. p4 keeps the four rotations and kills the four mirrors;
p4m would keep all eight.

The controls matter more than the scores. Line art on white decorrelates fast
under sub-pixel misalignment, so no score here will be near 1. What carries the
verdict is that the mirrors sit at the level of a meaningless shift.
"""
import numpy as np
from PIL import Image

TILE = "data/tile_single.jpg"


def load(path=TILE):
    return np.asarray(Image.open(path).convert("L"), dtype=np.float64)


def crop(A, cx, cy, w, n=256):
    H, W = A.shape
    x0, x1, y0, y1 = int(cx - w), int(cx + w), int(cy - w), int(cy + w)
    if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
        return None
    z = np.asarray(Image.fromarray(A[y0:y1, x0:x1]).resize((n, n), Image.BILINEAR),
                   dtype=np.float64)
    z -= z.mean()
    s = z.std()
    return z / s if s > 1e-9 else None


def corr(z, zz):
    return float((z * zz).mean())


def find_centre(A):
    """Locate the tile by maximising its own 90-degree rotational correlation.

    Deliberately optimises the thing we are about to test. That is safe only
    because the mirrors are then read off the SAME crop without re-fitting --
    the fit cannot manufacture a mirror it was not asked for.
    """
    H, W = A.shape
    best = None
    for w in range(780, 1001, 20):
        for cx in range(W // 2 - 120, W // 2 + 121, 20):
            for cy in range(H // 2 - 120, H // 2 + 121, 20):
                z = crop(A, cx, cy, w)
                if z is None:
                    continue
                c = corr(z, np.rot90(z))
                if best is None or c > best[0]:
                    best = (c, cx, cy, w)
    c, cx, cy, w = best
    for step in (10, 4, 2):
        for _ in range(3):
            cand = best
            for dw in (-step, 0, step):
                for dx in (-step, 0, step):
                    for dy in (-step, 0, step):
                        z = crop(A, cx + dx, cy + dy, w + dw)
                        if z is None:
                            continue
                        cc = corr(z, np.rot90(z))
                        if cc > cand[0]:
                            cand = (cc, cx + dx, cy + dy, w + dw)
            if cand == best:
                break
            best = cand
            c, cx, cy, w = best
    return best


def report(path=TILE):
    A = load(path)
    c, cx, cy, w = find_centre(A)
    z = crop(A, cx, cy, w, n=512)
    print("%s  centre=(%d,%d) half-width=%d px" % (path, cx, cy, w))
    print()
    rot = {"90": np.rot90(z, 1), "180": np.rot90(z, 2), "270": np.rot90(z, 3)}
    mir = {"vertical": np.fliplr(z), "horizontal": np.flipud(z),
           "diagonal": z.T, "antidiagonal": np.rot90(z.T, 2)}
    print("  rotations   (p4 and p4m both need these)")
    for k, v in rot.items():
        print("    %-14s %+.3f" % (k, corr(z, v)))
    print("  mirrors     (only p4m needs these)")
    for k, v in mir.items():
        print("    %-14s %+.3f" % (k, corr(z, v)))
    print("  controls")
    rnd = np.random.default_rng(0).permutation(z.reshape(-1)).reshape(z.shape)
    print("    %-14s %+.3f" % ("shuffled", corr(z, rnd)))
    print("    %-14s %+.3f" % ("shift 37 px", corr(z, np.roll(z, 37, axis=0))))
    r = np.mean([corr(z, v) for v in rot.values()])
    m = np.mean([corr(z, v) for v in mir.values()])
    print()
    print("  mean rotation %+.3f | mean mirror %+.3f | ratio %.1f" % (r, m, r / m))
    print("  verdict: %s" % ("p4 (chiral)" if r > 2 * m else "inconclusive"))


if __name__ == "__main__":
    report()
