"""The other two knobs, precomputed the same way as the chirality one.

kiln    m = [ G_l * m0 > 1/2 ]        one firing, l the diffusion length
cutoff  keep only m^2 + n^2 <= K^2    the tile assembling out of cosines

Both are rendered to two-colour PNGs so the page can drag at full rate with
no solver behind it. That is what makes the Space backendless.
"""
import json
import numpy as np
from PIL import Image

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask
from fourier import p4_symmetrise, centred, coefficients, synth, orbits, N, C
from kiln import gauss
from render import PAPER, INK

SZ, PX_PER_MM = 460, N / 150.0
PALETTE = list(PAPER) + list(INK) + [0] * (768 - 6)


def save2(ink, path):
    im = Image.fromarray(np.where(ink, 1, 0).astype(np.uint8), mode="P")
    im.putpalette(PALETTE)
    im = im.resize((SZ, SZ), Image.LANCZOS).convert("P", palette=Image.ADAPTIVE, colors=2)
    im.putpalette(PALETTE)
    im.save(path, optimize=True)
    return os.path.getsize(path)


def cosines(K):
    return sum(1 if (u, v) == (0, 0) else s // 2 for (u, v), s, _ in orbits(K))


if __name__ == "__main__":
    m = ink_mask(n=N).astype(float)
    target = (p4_symmetrise(m) > 0.5).astype(float)
    F = coefficients(centred(target))
    base = np.roll(synth(F, 200), (C, C), axis=(0, 1)) > 0.5

    # --- knob: the kiln ----------------------------------------------------
    ls = [round(x, 2) for x in np.linspace(0, 8, 25)]
    meta, tot = [], 0
    for i, l in enumerate(ls):
        ink = base if l == 0 else (gauss(base.astype(float), l) > 0.5)
        tot += save2(ink, "web/kiln/s%02d.png" % i)
        meta.append({"l": l, "mm": round(l / PX_PER_MM, 3), "ink": round(float(ink.mean()), 4)})
    json.dump(meta, open("web/kiln/meta.json", "w"))
    print("kiln   %d frames, l = 0..%.0f px (0..%.1f mm), %.0f KB"
          % (len(ls), ls[-1], meta[-1]["mm"], tot / 1024))

    # --- knob: the cutoff --------------------------------------------------
    Ks = sorted(set(np.round(np.linspace(1.0, np.sqrt(200), 25) ** 2).astype(int)))
    meta, tot = [], 0
    for i, K in enumerate(Ks):
        ink = np.roll(synth(F, K), (C, C), axis=(0, 1)) > 0.5
        tot += save2(ink, "web/cut/k%02d.png" % i)
        iou = (ink & base).sum() / max((ink | base).sum(), 1)
        meta.append({"K": int(K), "cos": cosines(K), "iou": round(float(iou), 4)})
    json.dump(meta, open("web/cut/meta.json", "w"))
    print("cutoff %d frames, K = %d..%d, %s cosines at the top, %.0f KB"
          % (len(Ks), Ks[0], Ks[-1], f"{meta[-1]['cos']:,}", tot / 1024))
