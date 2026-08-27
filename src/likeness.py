"""Where each slider is standing when the tile most looks like the tile.

Every one of the nine sliders is a way of breaking the pattern -- firing it,
blurring it, replacing its coefficients, thresholding it somewhere else. Each
one therefore has a position at which the frame is closest to the tile that was
photographed, and it is downhill from there in both directions.

That position is the wall's resting state. It is not a taste decision: it is
the frame closest in RGB to the tile as this page draws it -- the ink measured
off the photograph, painted in the page's own paper and ink. Written to
web/likeness.json and read by src/build_wall.py, so the page opens on nine
measured numbers like everything else on it.

RGB and not IoU on the ink, because IoU cannot see colour: the attention frames
lay a warm wash over an untouched pattern, so on shape alone the wall opened on
a tile that was entirely orange and scored 0.95 for it.

The comparison allows the four quarter-plane rolls, because the frame sets do
not agree about where the origin is -- some are rolled onto the four-fold
centre before saving and some are not. A wrong roll costs so much likeness
that the right one is never in doubt.

    python src/likeness.py       ->  web/likeness.json
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask
from fourier import N, p4_symmetrise

SIZE  = 460                     # every frame set is saved at this size
PAPER = (247, 245, 240)         # the page's two colours, as wall_assets writes them
INK   = (33, 54, 96)

SETS = [("cut", "k"), ("kiln", "s"), ("perc", "p"), ("eye", "e"), ("chi", "t"),
        ("frac", "w"), ("copy", "c"), ("ship", "s"), ("attn", "a")]


def frame(path):
    return np.asarray(Image.open(path).convert("RGB"), float)


def reference():
    """The tile itself, drawn the way the page draws every frame."""
    m = p4_symmetrise(ink_mask(n=N).astype(float)) > 0.5
    im = Image.fromarray((m * 255).astype(np.uint8)).resize((SIZE, SIZE), Image.LANCZOS)
    m = np.asarray(im) > 127
    return np.where(m[..., None], np.array(INK, float), np.array(PAPER, float))


def likeness(a, b):
    """1 at identical, 0 at the worst two of these images could differ."""
    rmse = float(np.sqrt(((a - b) ** 2).mean()))
    return 1.0 - rmse / 255.0


def best(f, refs):
    return max(likeness(f, r) for r in refs)


def build(web="web"):
    ref = reference()
    h = SIZE // 2
    refs = [np.roll(ref, (dy, dx), axis=(0, 1))
            for dy in (0, h) for dx in (0, h)]

    out = {}
    print("  %-6s %6s %8s   %s" % ("tile", "start", "likeness", "runner-up"))
    for name, pre in SETS:
        d = os.path.join(web, name)
        files = sorted(f for f in os.listdir(d)
                       if f.startswith(pre) and f.endswith(".png"))
        if not files:
            continue
        scores = [best(frame(os.path.join(d, f)), refs) for f in files]
        k = int(np.argmax(scores))
        order = [j for j in np.argsort(scores)[::-1] if j != k]
        out[name] = {"start": k, "likeness": round(scores[k], 4), "n": len(files)}
        print("  %-6s %6d %8.4f   %d at %.4f" %
              (name, k, scores[k], order[0], scores[order[0]]))

    json.dump(out, open(os.path.join(web, "likeness.json"), "w"), indent=1)
    print("wrote %s/likeness.json" % web)
    return out


if __name__ == "__main__":
    build()
