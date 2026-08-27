"""Frames for the wall's sliders. One directory per tile, same contract as the
existing three: <dir>/<prefix><NN>.png, palette-quantised, 460 px.
"""
import json
import numpy as np
from PIL import Image

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask
from fourier import N, C, p4_symmetrise, centred, coefficients, synth, orbits
from kiln import gauss
import percolation as PC
import theseus as TH
import acuity as AC
import attention as AT

PAPER, INK, WARM = (247, 245, 240), (33, 54, 96), (176, 85, 74)
NF = 26


def palette():
    """One fixed palette for every frame of every tile.

    MAXCOVERAGE picks its 32 colours per image, so each tile ended up with its
    own idea of what the paper was -- (247,245,240) here, (255,244,234) there,
    pure white on a frame where the heat map happened to be flat. Nine tiles,
    six different whites, and a wall that looked wrong before you touched it.

    So the palette is fixed instead: the page's three colours exactly, plus the
    ramps between them for what LANCZOS leaves along an edge. Paper is paper in
    every frame of all nine.
    """
    cols = [PAPER, INK, WARM]
    def ramp(a, b, n):
        return [tuple(int(round(a[c] + (b[c] - a[c]) * i / n)) for c in range(3))
                for i in range(1, n)]
    cols += ramp(PAPER, INK, 20) + ramp(PAPER, WARM, 28) + ramp(WARM, INK, 16)
    cols = list(dict.fromkeys(cols))[:256]
    pal = Image.new("P", (1, 1))
    flat = [v for c in cols for v in c]
    pal.putpalette(flat + [0] * (768 - len(flat)))
    return pal


PALETTE = None


def save(rgb, path):
    global PALETTE
    if PALETTE is None:
        PALETTE = palette()
    Image.fromarray(rgb).resize((460, 460), Image.LANCZOS) \
        .quantize(palette=PALETTE, dither=Image.Dither.NONE).save(path, optimize=True)


def two(mask, path):
    save(np.where(mask[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8)), path)


def three(mask, hot, path):
    rgb = np.where(mask[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8))
    rgb[hot] = np.array(WARM, np.uint8)
    save(rgb, path)


def outdir(web, name):
    d = os.path.join(web, name)
    os.makedirs(d, exist_ok=True)
    return d


def build(web="web"):
    m = p4_symmetrise(ink_mask(n=N).astype(float))
    F = coefficients(centred(m))
    meta = {}

    # --- percolation: threshold, largest component in warm ------------------
    d = outdir(web, "perc")
    f = PC.field()
    rows = []
    for i, th in enumerate(np.linspace(0.78, 0.24, NF)):
        r = PC.measure(f, th)
        mask = f > th
        lab = PC.components(mask)
        ids, cnt = np.unique(lab[mask], return_counts=True)
        big = lab == ids[np.argmax(cnt)]
        three(mask, big, os.path.join(d, "p%02d.png" % i))
        rows.append(r)
    meta["perc"] = rows

    # --- acuity: what the eye receives at distance d ------------------------
    d = outdir(web, "eye")
    rows = []
    for i, dist in enumerate(np.geomspace(0.3, 12.0, NF)):
        K = min(200.0, AC.K_of(dist))
        two(np.roll(synth(F, K), (C, C), axis=(0, 1)) > 0.5, os.path.join(d, "e%02d.png" % i))
        rows.append({"d": round(float(dist), 2), "K": round(float(K)),
                     "mm": round(AC.resolvable_mm(dist), 3),
                     "cos": AC.cosines(int(round(K)))})
    meta["eye"] = rows

    # --- theseus: random planks replaced ------------------------------------
    d = outdir(web, "ship")
    F2, ref, ink = TH.setup()
    orb = [uv for uv, _, _ in orbits(TH.K) if uv != (0, 0)]
    rng = np.random.default_rng(1)
    order = [tuple(x) for x in np.array(orb)[rng.permutation(len(orb))]]
    rows = []
    for i, p in enumerate(np.linspace(0, 1, NF)):
        n = int(round(p * len(orb)))
        mk = TH.flip(F2, order[:n], ink, seed=3)
        two(mk, os.path.join(d, "s%02d.png" % i))
        rows.append({"p": round(float(p), 3), "iou": round(TH.iou(mk, ref), 4)})
    meta["ship"] = rows

    # --- copying: the kiln, with and without someone who remembers ----------
    d = outdir(web, "copy")
    stored = ink_mask(n=N)
    sig = 3.0 * N / 700.0
    cur, lam = stored.copy(), 0.15
    rows = []
    for i in range(NF):
        two(cur, os.path.join(d, "c%02d.png" % i))
        rows.append({"gen": i, "ink": round(float(cur.mean()), 4),
                     "iou": round(float((cur & stored).sum() / (cur | stored).sum()), 4)})
        cur = (gauss(cur.astype(float), sig) + lam * (stored - 0.5)) > 0.5
    meta["copy"] = rows

    # --- attention: where one patch sends its attention ---------------------
    d = outdir(web, "attn")
    X, cells = AT.patches(m)
    orbidx = AT.orbit_index(cells)
    src = cells.index((3, 3))
    rows = []
    for i, beta in enumerate(np.geomspace(1.0, 400.0, NF)):
        A = AT.attention(X, beta)
        heat = np.zeros((N, N))
        for j, (a, b) in enumerate(cells):
            y, x = C + a * AT.S, C + b * AT.S
            heat[y - AT.S // 2:y + AT.S // 2, x - AT.S // 2:x + AT.S // 2] = A[src, j]
        h = heat / (heat.max() + 1e-12)
        rgb = np.where((m > 0.5)[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8))
        rgb = (rgb * (1 - h[..., None] * 0.85) + np.array(WARM) * (h[..., None] * 0.85)).astype(np.uint8)
        save(rgb, os.path.join(d, "a%02d.png" % i))
        rows.append({"beta": round(float(beta), 1),
                     "entropy": round(AT.entropy(A), 4),
                     "lift": round(AT.orbit_mass(A, orbidx) / (3.0 / (len(X) - 1)), 2)})
    meta["attn"] = rows

    json.dump(meta, open(os.path.join(web, "wall.json"), "w"))
    tot = sum(os.path.getsize(os.path.join(web, k, f))
              for k in ("perc", "eye", "ship", "copy", "attn")
              for f in os.listdir(os.path.join(web, k)))
    print("wrote 5 x %d frames, %.0f kB, and web/wall.json" % (NF, tot / 1000))


if __name__ == "__main__":
    build()
