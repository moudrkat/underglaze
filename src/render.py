"""The animation: the same tile copied and fired, with and without a memory.

Left  lam = 0     the kiln alone. Curvature flow has no non-trivial fixed
                  point, so the design is eaten.
Right lam = 0.15  a copyist who knows what a cibulak is supposed to be.

Same physics on both sides. The only difference is that somebody remembers.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask, CENTRE, HALF
from kiln import gauss

N, PANEL, GENS = 500, 470, 60
LAM = 0.15
SIGMA = 3.0 * N / 700.0

PAPER = (247, 245, 240)
INK = (33, 54, 96)
GREY = (150, 148, 143)
DARK = (40, 44, 52)

F = "/usr/share/fonts/truetype/dejavu/"
def font(name, sz):
    return ImageFont.truetype(F + name, sz)


def true_ink():
    """White-balance the photo and report the tile's real ink colour."""
    A = np.asarray(Image.open("data/tile_single.jpg").convert("RGB"), float)
    cx, cy = CENTRE
    sub = np.asarray(Image.fromarray(
        A[cy-HALF:cy+HALF, cx-HALF:cx+HALF].astype("uint8")).resize((N, N)), float)
    m = ink_mask(n=N)
    wb = sub / np.percentile(sub[~m], 85, axis=0)          # paper is white
    ink = np.median(wb[m], axis=0)
    return tuple(int(round(255 * c)) for c in ink)


def panel(mask, size=PANEL):
    img = np.empty(mask.shape + (3,), np.uint8)
    img[...] = PAPER
    img[mask] = INK
    return Image.fromarray(img).resize((size, size), Image.LANCZOS)


def evolve_pair(gens=GENS):
    stored = ink_mask(n=N)
    a = b = stored.copy()
    out = [(a.copy(), b.copy())]
    for _ in range(gens):
        a = gauss(a.astype(float), SIGMA) > 0.5
        b = (gauss(b.astype(float), SIGMA) + LAM * (stored.astype(float) - 0.5)) > 0.5
        out.append((a.copy(), b.copy()))
    return out


def frame(a, b, g):
    W, H = 2 * PANEL + 150, PANEL + 210
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.text((50, 34), "the same tile, copied and fired %d times" % g,
           font=font("DejaVuSerif.ttf", 27), fill=DARK)
    d.text((50, 74), "blur = the kiln  ·  re-threshold = the next copyist  ·  "
                     "together they are motion by mean curvature",
           font=font("DejaVuSans.ttf", 15), fill=GREY)
    x0, x1, y = 50, PANEL + 100, 118
    im.paste(panel(a), (x0, y)); im.paste(panel(b), (x1, y))
    for x, t, s in ((x0, "no one remembers", "λ = 0"),
                    (x1, "someone remembers", "λ = %.2f" % LAM)):
        d.text((x, y + PANEL + 16), t, font=font("DejaVuSans-Bold.ttf", 19), fill=DARK)
        d.text((x, y + PANEL + 44), s, font=font("DejaVuSans.ttf", 16), fill=GREY)
    d.text((W - 50, y + PANEL + 16), "generation %d" % g, anchor="ra",
           font=font("DejaVuSans.ttf", 17), fill=GREY)
    return im


if __name__ == "__main__":
    print("measured ink colour (white-balanced):", true_ink())
    pairs = evolve_pair()
    frames = [frame(a, b, g) for g, (a, b) in enumerate(pairs)]
    seq = [frames[0]] * 8 + frames + [frames[-1]] * 12
    seq[0].save("out/copy_and_fire.gif", save_all=True, append_images=seq[1:],
                duration=110, loop=0, optimize=True)
    frames[0].save("out/frame_first.png")
    frames[-1].save("out/frame_last.png")
    frames[3].save("out/frame_gen03.png")
    print("wrote out/copy_and_fire.gif  (%d frames, %.1f MB)"
          % (len(seq), os.path.getsize("out/copy_and_fire.gif") / 1e6))
