"""The gif for the post: the real tile, and the sum catching up with it."""
import numpy as np
from PIL import Image, ImageDraw

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask, CENTRE, HALF
from fourier import p4_symmetrise, centred, coefficients, synth, orbits, N, C
from render import PAPER, INK, GREY, DARK, font

PANEL, GAP, PAD = 470, 34, 44


def cosines(K):
    return sum(1 if (u, v) == (0, 0) else s // 2 for (u, v), s, _ in orbits(K))


def photo_panel():
    A = Image.open("data/tile_single.jpg").convert("RGB")
    cx, cy = CENTRE
    return A.crop((cx-HALF, cy-HALF, cx+HALF, cy+HALF)).resize((PANEL, PANEL), Image.LANCZOS)


def frame(photo, ink, n):
    W = PAD*2 + PANEL*2 + GAP
    H = PAD + PANEL + 116
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    im.paste(photo, (PAD, PAD))
    img = np.where(ink[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8))
    im.paste(Image.fromarray(img).resize((PANEL, PANEL), Image.LANCZOS), (PAD+PANEL+GAP, PAD))
    y = PAD + PANEL + 22
    d.text((PAD, y), "the tile", font=font("DejaVuSans.ttf", 17), fill=GREY)
    d.text((W-PAD, y), "%s cosines" % f"{n:,}".replace(",", " "), anchor="ra",
           font=font("DejaVuSans-Bold.ttf", 34), fill=INK)
    return im


if __name__ == "__main__":
    m = ink_mask(n=N).astype(float)
    F = coefficients(centred((p4_symmetrise(m) > 0.5).astype(float)))
    photo = photo_panel()
    Ks = sorted(set(np.round(np.linspace(1.0, np.sqrt(200), 58) ** 2).astype(int)))
    frames = [frame(photo, np.roll(synth(F, K), (C, C), axis=(0, 1)) > 0.5, cosines(K))
              for K in Ks]
    seq = [frames[0]]*6 + frames + [frames[-1]]*22
    # One fixed palette for every frame. Otherwise each frame quantises the
    # static photograph slightly differently and gif delta-compression, which
    # only helps on pixels that are bit-identical, has nothing to work with.
    pal = seq[-1].quantize(colors=64, method=Image.MAXCOVERAGE)
    q = [f.quantize(palette=pal, dither=Image.NONE) for f in seq]
    q[0].save("out/post.gif", save_all=True, append_images=q[1:], duration=115,
              loop=0, optimize=True)
    frames[-1].save("out/post_last.png")
    print("out/post.gif  %d frames, %d..%s cosines, %.1f MB"
          % (len(seq), cosines(Ks[0]), f"{cosines(Ks[-1]):,}", os.path.getsize("out/post.gif")/1e6))
