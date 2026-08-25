"""Two more gifs, both using the photograph itself rather than a panel beside it.

overlay  the sum is painted in over the real tile as the cutoff rises
wipe     photograph on one side, sum on the other, the seam travelling across
"""
import numpy as np
from PIL import Image, ImageDraw, ImageOps

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask, CENTRE, HALF
from fourier import p4_symmetrise, centred, coefficients, synth, orbits, N, C
from render import PAPER, INK, GREY, DARK, font

SIZE, PAD = 620, 40


def photo():
    A = Image.open("data/tile_single.jpg").convert("RGB")
    cx, cy = CENTRE
    p = A.crop((cx-HALF, cy-HALF, cx+HALF, cy+HALF)).resize((SIZE, SIZE), Image.LANCZOS)
    return ImageOps.autocontrast(p, cutoff=2)


def cosines(K):
    return sum(1 if (u, v) == (0, 0) else s // 2 for (u, v), s, _ in orbits(K))


def caption(im, n, note):
    d = ImageDraw.Draw(im)
    y = PAD + SIZE + 20
    d.text((PAD, y), "%s cosines" % f"{n:,}".replace(",", " "),
           font=font("DejaVuSans-Bold.ttf", 32), fill=INK)
    d.text((PAD + SIZE, y + 8), note, anchor="ra", font=font("DejaVuSans.ttf", 16), fill=GREY)
    return im


def canvas():
    return Image.new("RGB", (SIZE + PAD*2, SIZE + PAD + 96), PAPER)


def build(F, ph, mode):
    ref = np.asarray(ph, np.uint8)
    Ks = sorted(set(np.round(np.linspace(1.0, np.sqrt(200), 56) ** 2).astype(int)))
    out = []
    for i, K in enumerate(Ks):
        ink = np.roll(synth(F, K), (C, C), axis=(0, 1)) > 0.5
        ink = np.asarray(Image.fromarray((ink*255).astype(np.uint8)).resize((SIZE, SIZE),
                          Image.LANCZOS), np.uint8) > 127
        if mode == "overlay":
            img = ref.copy()
            img[ink] = INK
            note = "painted over the photograph"
        else:
            drawn = np.where(ink[..., None], np.array(INK, np.uint8),
                             np.array(PAPER, np.uint8))
            x = int(SIZE * (i + 1) / len(Ks))
            img = ref.copy()
            img[:, :x] = drawn[:, :x]
            note = "left of the seam: the equation"
        im = canvas()
        im.paste(Image.fromarray(img), (PAD, PAD))
        out.append(caption(im, cosines(K), note))
    return out


def gif(path, frames, hold=20):
    seq = [frames[0]]*5 + frames + [frames[-1]]*hold
    pal = seq[-1].quantize(colors=64, method=Image.MAXCOVERAGE)
    q = [f.quantize(palette=pal, dither=Image.NONE) for f in seq]
    q[0].save(path, save_all=True, append_images=q[1:], duration=115, loop=0, optimize=True)
    return os.path.getsize(path)/1e6


if __name__ == "__main__":
    m = ink_mask(n=N).astype(float)
    F = coefficients(centred((p4_symmetrise(m) > 0.5).astype(float)))
    ph = photo()
    for mode, name in (("overlay", "post_overlay"), ("wipe", "post_wipe")):
        fr = build(F, ph, mode)
        mb = gif("out/%s.gif" % name, fr)
        fr[-1].save("out/%s_last.png" % name)
        print("out/%s.gif  %.1f MB" % (name, mb))
