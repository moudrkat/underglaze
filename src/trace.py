"""Turn the photographed tile into strokes.

Threshold the ink, thin it to a one-pixel skeleton (Zhang-Suen), then walk the
skeleton into polylines, breaking at junctions. These polylines are what the
pen draws; fitting Beziers to them is a later refinement, not needed to see it
move.
"""
import json
import numpy as np
from PIL import Image

TILE = "data/tile_single.jpg"
CENTRE, HALF = (1054, 1038), 880          # from src/symmetry.py
N = 700


def ink_mask(path=TILE, n=N, pct=28.0):
    A = np.asarray(Image.open(path).convert("L"), dtype=np.float64)
    cx, cy = CENTRE
    sub = A[cy - HALF:cy + HALF, cx - HALF:cx + HALF]
    sub = np.asarray(Image.fromarray(sub).resize((n, n), Image.BILINEAR), float)
    # the photo has a lighting gradient; flatten it before thresholding
    yy, xx = np.mgrid[0:n, 0:n] / n
    Aq = np.stack([np.ones_like(xx).ravel(), xx.ravel(), yy.ravel(),
                   (xx * yy).ravel(), (xx ** 2).ravel(), (yy ** 2).ravel()], 1)
    coef, *_ = np.linalg.lstsq(Aq, sub.ravel(), rcond=None)
    flat = sub - (Aq @ coef).reshape(n, n)
    return flat < np.percentile(flat, pct)


def _nb(P):
    """The 8 neighbours P2..P9 of every pixel, clockwise from north."""
    z = np.zeros_like(P)
    def sh(dy, dx):
        out = z.copy()
        ys = slice(max(0, -dy), P.shape[0] - max(0, dy))
        xs = slice(max(0, -dx), P.shape[1] - max(0, dx))
        yd = slice(max(0, dy), P.shape[0] - max(0, -dy))
        xd = slice(max(0, dx), P.shape[1] - max(0, -dx))
        out[yd, xd] = P[ys, xs]
        return out
    return [sh(-1, 0), sh(-1, 1), sh(0, 1), sh(1, 1),
            sh(1, 0), sh(1, -1), sh(0, -1), sh(-1, -1)]


def thin(mask):
    """Zhang-Suen, vectorised. Returns a 1-px skeleton."""
    P = mask.astype(np.uint8).copy()
    while True:
        changed = False
        for step in (0, 1):
            n2, n3, n4, n5, n6, n7, n8, n9 = _nb(P)
            B = n2 + n3 + n4 + n5 + n6 + n7 + n8 + n9
            seq = [n2, n3, n4, n5, n6, n7, n8, n9, n2]
            Aa = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.uint8)
                     for i in range(8))
            if step == 0:
                c1, c2 = n2 * n4 * n6, n4 * n6 * n8
            else:
                c1, c2 = n2 * n4 * n8, n2 * n6 * n8
            kill = (P == 1) & (B >= 2) & (B <= 6) & (Aa == 1) & (c1 == 0) & (c2 == 0)
            if kill.any():
                P[kill] = 0
                changed = True
        if not changed:
            return P.astype(bool)


def polylines(S, min_len=6):
    """Walk the skeleton into paths, cutting at junctions."""
    deg = sum(_nb(S.astype(np.uint8)))
    node = S & (deg != 2)                     # endpoints and junctions
    todo = {tuple(p) for p in np.argwhere(S)}
    paths, H, W = [], *S.shape
    def nbrs(y, x):
        return [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                if (dy or dx) and 0 <= y + dy < H and 0 <= x + dx < W and S[y + dy, x + dx]]
    starts = [tuple(p) for p in np.argwhere(node)] + sorted(todo)
    for s in starts:
        for nb in nbrs(*s):
            if s not in todo and nb not in todo:
                continue
            path, cur, prev = [s], nb, s
            todo.discard(s)
            while True:
                path.append(cur)
                todo.discard(cur)
                nxt = [q for q in nbrs(*cur) if q != prev and q in todo]
                if node[cur] or not nxt:
                    break
                prev, cur = cur, nxt[0]
            if len(path) >= min_len:
                paths.append(path)
    return paths


if __name__ == "__main__":
    m = ink_mask()
    print("ink   %.1f%% of the tile" % (100 * m.mean()))
    S = thin(m)
    print("skel  %d px" % S.sum())
    P = polylines(S)
    print("paths %d, total %d px, median len %d"
          % (len(P), sum(len(p) for p in P), int(np.median([len(p) for p in P]))))
    json.dump([[[int(y), int(x)] for y, x in p] for p in P],
              open("out/strokes.json", "w"))
    Image.fromarray((~S * 255).astype(np.uint8)).save("out/skeleton.png")
    Image.fromarray((~m * 255).astype(np.uint8)).save("out/mask.png")
    print("wrote out/strokes.json, out/skeleton.png, out/mask.png")
