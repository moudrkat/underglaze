"""Cosines or strokes -- which basis is the tile actually cheap in?

`the cost of detail` reports 62 815 cosines for 99 % of the tile, and that
number gets read as "this pattern is complicated". It may only mean "cosines
are a bad basis for line art". Fourier coefficients are global: every one of
them is nonzero because the tile has edges, and a sharp edge costs a power-law
tail no matter what is drawn. So the count could be a fact about the basis
rather than about the cibulak.

Test it by pricing the same picture in a second basis and putting both on one
axis. The strokes are already there -- src/trace.py thins the ink to a one
pixel skeleton and walks it into polylines. Simplify those polylines to a
tolerance, give each one a width measured off the ink, draw them back, and
score with the same intersection-over-union against the same reference.

Parameters are counted as free real numbers on both sides, which is the only
comparison that means anything:

  cosines   one real a_mn per p4 orbit. Note the page's x-axis says "cosines"
            and counts terms, of which each orbit contributes two -- so the
            page's 62 815 is 41 901 free numbers. Both are given below.
  strokes   two per retained point, plus one width per stroke.

The interesting number is not which wins but where the stroke curve stops.
"""
import json
import numpy as np
from PIL import Image, ImageDraw

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask, thin, polylines
from fourier import (N, C, p4_symmetrise, centred, coefficients, synth, orbits)


def reference():
    """Exactly what src/build_assets.py scores the cosine curve against."""
    m = ink_mask(n=N).astype(float)
    return (p4_symmetrise(m) > 0.5)


def iou(a, b):
    inter = np.count_nonzero(a & b)
    union = np.count_nonzero(a | b)
    return inter / union if union else 0.0


def _edt1d(f):
    """Felzenszwalb-Huttenlocher lower envelope of parabolas, one row."""
    n = len(f)
    v = np.zeros(n, int)
    z = np.empty(n + 1)
    z[0], z[1] = -np.inf, np.inf
    k = 0
    for q in range(1, n):
        while True:
            s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2.0 * q - 2.0 * v[k])
            if s <= z[k]:
                k -= 1
            else:
                break
        k += 1
        v[k], z[k], z[k + 1] = q, s, np.inf
    out = np.empty(n)
    k = 0
    for q in range(n):
        while z[k + 1] < q:
            k += 1
        out[q] = (q - v[k]) ** 2 + f[v[k]]
    return out


def halfwidths(mask):
    """Exact Euclidean distance to the nearest non-ink pixel.

    Chebyshev-by-erosion was tried first and overfilled: it draws a round disk
    with the radius of an inscribed square, so the reconstruction came out at
    0.235 ink against the reference's 0.209. Exact is not expensive here.
    """
    INF = 1e12
    f = np.where(mask, INF, 0.0)
    for i in range(f.shape[0]):
        f[i] = _edt1d(f[i])
    for j in range(f.shape[1]):
        f[:, j] = _edt1d(f[:, j])
    return np.sqrt(f)


def simplify(path, tol):
    """Douglas-Peucker. tol = 0 keeps every point."""
    if tol <= 0 or len(path) < 3:
        return list(path)
    P = np.asarray(path, float)
    keep = np.zeros(len(P), bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(P) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, b = P[i], P[j]
        ab = b - a
        L = np.hypot(*ab)
        seg = P[i + 1:j]
        if L < 1e-9:
            d = np.hypot(*(seg - a).T)
        else:
            r = seg - a
            d = np.abs(ab[0] * r[:, 1] - ab[1] * r[:, 0]) / L
        k = int(np.argmax(d))
        if d[k] > tol:
            keep[i + 1 + k] = True
            stack += [(i, i + 1 + k), (i + 1 + k, j)]
    return [tuple(p) for p in P[keep].astype(int)]


def draw(strokes, widths, n=N):
    """A disk at every retained point, and a band between neighbours.

    One width per stroke was tried first and could not exceed IoU 0.57: the
    half-width runs from 1 to 8 px along a single stroke, so a constant is
    always wrong somewhere. Per point it is, at three reals each.
    """
    im = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(im)
    for pts, ws in zip(strokes, widths):
        for i, (y, x) in enumerate(pts):
            r = max(0.5, ws[i])
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
            if i:
                y0, x0 = pts[i - 1]
                d.line([(x0, y0), (x, y)], fill=255,
                       width=max(1, int(round(ws[i] + ws[i - 1]))))
    return np.asarray(im) > 127


def stroke_curve(ref, tols=(8.0, 5.0, 3.0, 2.0, 1.2, 0.8, 0.4, 0.0)):
    S = thin(ref)
    paths = polylines(S, min_len=1)
    D = halfwidths(ref)
    out = []
    for tol in tols:
        simp, ws = [], []
        for p in paths:
            q = simplify(p, tol)
            simp.append(q)
            ws.append([float(D[y, x]) for y, x in q])
        pts = sum(len(p) for p in simp)
        out.append({"tol": tol, "strokes": len(simp), "points": pts,
                    "params": 3 * pts,                 # y, x and a width at each point
                    "iou": round(iou(draw(simp, ws), ref), 4)})
    return out


def cosine_curve(ref, Ks=(10, 18, 29, 42, 57, 75, 95, 118, 143, 170, 200)):
    F = coefficients(centred(ref.astype(float)))
    out = []
    for K in Ks:
        orb = orbits(K)
        rec = np.roll(synth(F, K), (C, C), axis=(0, 1)) > 0.5
        out.append({"K": K, "params": len(orb),
                    "terms": sum(1 if uv == (0, 0) else s // 2 for uv, s, _ in orb),
                    "iou": round(iou(rec, ref), 4)})
    return out


def stroke_budget(ref, keeps=(40, 100, 250, 600, 1500, 3500, 7411), tol=1.2):
    """Below the floor there is only one move left: draw fewer strokes.

    Simplifying cannot go under 3 x 2 x (number of strokes), because every
    fragment needs two endpoints. The skeleton has 7 411 fragments, so the
    floor is 44 466 reals. To price the tile at 500 reals the strokes have to
    be thrown away, longest kept first.
    """
    S = thin(ref)
    paths = polylines(S, min_len=1)
    D = halfwidths(ref)
    scored = sorted(paths, key=lambda p: -sum(D[y, x] for y, x in p))
    out = []
    for k in keeps:
        sel = scored[:k]
        simp, ws = [], []
        for p in sel:
            q = simplify(p, tol)
            simp.append(q); ws.append([float(D[y, x]) for y, x in q])
        pts = sum(len(p) for p in simp)
        out.append({"keep": k, "points": pts, "params": 3 * pts,
                    "iou": round(iou(draw(simp, ws), ref), 4)})
    return out


def report():
    ref = reference()
    print("reference: %d ink pixels of %d  (%.1f %%)\n"
          % (ref.sum(), ref.size, 100 * ref.mean()))

    cos = cosine_curve(ref)
    print("cosines")
    print("  %6s %10s %10s %8s" % ("K", "free reals", "terms", "IoU"))
    for r in cos:
        print("  %6d %10d %10d %8.4f" % (r["K"], r["params"], r["terms"], r["iou"]))

    st = stroke_curve(ref)
    print("\nstrokes")
    print("  %6s %8s %8s %10s %8s" % ("tol", "strokes", "points", "free reals", "IoU"))
    for r in st:
        print("  %6.1f %8d %8d %10d %8.4f" % (r["tol"], r["strokes"], r["points"],
                                              r["params"], r["iou"]))

    best = max(st, key=lambda r: r["iou"])
    print("\n  the stroke curve stops at IoU %.4f -- that is its ceiling, not a"
          % best["iou"])
    print("  budget limit. thinning throws away every blob interior and every")
    print("  junction, and no number of control points puts them back.")

    bud = stroke_budget(ref)
    print("\n  fewer strokes, longest kept first")
    print("  %8s %8s %10s %8s" % ("strokes", "points", "free reals", "IoU"))
    for r in bud:
        print("  %8d %8d %10d %8.4f" % (r["keep"], r["points"], r["params"], r["iou"]))

    print("\n  at matched budget, cosines against strokes")
    print("  %10s %10s %10s" % ("free reals", "cosine IoU", "stroke IoU"))
    for r in bud:
        c = min(cos, key=lambda q: abs(q["params"] - r["params"]))
        print("  %10d %10.4f %10.4f   (K=%d, %d strokes)"
              % (r["params"], c["iou"], r["iou"], c["K"], r["keep"]))

    for target in (0.80, 0.90, best["iou"]):
        c = next((r for r in cos if r["iou"] >= target), None)
        s = next((r for r in st if r["iou"] >= target), None)
        if c and s:
            print("  IoU %.2f : %6d cosine reals vs %6d stroke reals   (%.1fx)"
                  % (target, c["params"], s["params"], c["params"] / s["params"]))
        elif c:
            print("  IoU %.2f : %6d cosine reals, strokes never reach it" % (target, c["params"]))

    json.dump({"cosines": cos, "strokes": st, "budget": bud}, open("out/strokes_vs_cosines.json", "w"))
    print("\nwrote out/strokes_vs_cosines.json")


if __name__ == "__main__":
    report()


def build_page_asset(webdir="web", K=42, keep=250, tol=1.2):
    """One picture at one matched budget, since the table is the argument."""
    from build_assets import paint
    from PIL import Image as I
    ref = reference()
    F = coefficients(centred(ref.astype(float)))
    a = np.roll(synth(F, K), (C, C), axis=(0, 1)) > 0.5

    S = thin(ref); D = halfwidths(ref)
    sel = sorted(polylines(S, min_len=1), key=lambda p: -sum(D[y, x] for y, x in p))[:keep]
    simp = [simplify(p, tol) for p in sel]
    ws = [[float(D[y, x]) for y, x in q] for q in simp]
    b = draw(simp, ws)

    n = 460
    im = I.new("RGB", (2 * n + 18, n), (247, 245, 240))
    im.paste(paint(a, n), (0, 0)); im.paste(paint(b, n), (n + 18, 0))
    im.save(os.path.join(webdir, "strokes_vs_cosines.png"), optimize=True)
    print("wrote %s/strokes_vs_cosines.png  (K=%d: IoU %.4f | %d strokes: IoU %.4f)"
          % (webdir, K, iou(a, ref), keep, iou(b, ref)))
