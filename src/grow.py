"""The tile drawing itself out of cosines.

One frame per cutoff K. Everything on screen is the sum

    f(x,y) = sum_{m^2+n^2 <= K^2}  a_mn [ cos(2pi(mx+ny)/L) + cos(2pi(-nx+my)/L) ]

thresholded at f > 1/2. The a_mn are measured off the photograph.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask
from fourier import p4_symmetrise, centred, coefficients, synth, orbits, N, C
from render import PAPER, INK, GREY, DARK, font

SIZE = 560


def schedule(kmax=140, frames=64):
    """Dense where the picture is changing: linear in sqrt(K)."""
    ks = np.unique(np.round(np.linspace(1.0, np.sqrt(kmax), frames) ** 2)).astype(int)
    return list(ks)


def build():
    m = ink_mask(n=N).astype(float)
    target = (p4_symmetrise(m) > 0.5).astype(float)
    F = coefficients(centred(target))
    ref = target > 0.5
    out = []
    for K in schedule():
        f = np.roll(synth(F, K), (C, C), axis=(0, 1))
        ink = f > 0.5
        iou = (ink & ref).sum() / max((ink | ref).sum(), 1)
        out.append((K, ink, len(orbits(K)), iou))
    return out


def frame(K, ink, nterms, iou):
    W, H = SIZE + 80, SIZE + 168
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.text((40, 34), "f > ½,   f = Σ aₘₙ [ cos 2π(mx+ny) + cos 2π(−nx+my) ]",
           font=font("DejaVuSans.ttf", 19), fill=DARK)
    img = np.where(ink[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8))
    im.paste(Image.fromarray(img).resize((SIZE, SIZE), Image.LANCZOS), (40, 84))
    y = 84 + SIZE + 18
    d.text((40, y), "m² + n²  ≤  %d²" % K, font=font("DejaVuSans-Bold.ttf", 21), fill=INK)
    d.text((40, y + 32), "%s cosine terms" % f"{nterms:,}".replace(",", " "),
           font=font("DejaVuSans.ttf", 16), fill=GREY)
    d.text((W - 40, y + 32), "%.0f %% of the tile" % (100 * iou), anchor="ra",
           font=font("DejaVuSans.ttf", 16), fill=GREY)
    return im


if __name__ == "__main__":
    data = build()
    frames = [frame(*d) for d in data]
    seq = [frames[0]] * 6 + frames + [frames[-1]] * 18
    seq[0].save("out/drawn_by_cosines.gif", save_all=True, append_images=seq[1:],
                duration=120, loop=0, optimize=True)
    frames[-1].save("out/drawn_last.png")
    print("K from %d to %d, %d frames, %.1f MB"
          % (data[0][0], data[-1][0], len(seq),
             os.path.getsize("out/drawn_by_cosines.gif") / 1e6))
    print("final: %d terms, IoU %.3f" % (data[-1][2], data[-1][3]))
