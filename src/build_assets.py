"""Render everything the page shows."""
import json
import numpy as np
from PIL import Image, ImageDraw

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask
from fourier import p4_symmetrise, centred, coefficients, synth, orbits, N, C
from chirality import knob, chi
from render import PAPER, INK, GREY, DARK, font

SIZE, KMAX = 560, 200


def tile(F, K=KMAX):
    return np.roll(synth(F, K), (C, C), axis=(0, 1)) > 0.5


def paint(ink, size=SIZE):
    img = np.where(ink[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8))
    return Image.fromarray(img).resize((size, size), Image.LANCZOS)


def framed(ink, top, left, right):
    W, H = SIZE + 80, SIZE + 152
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.text((40, 32), top, font=font("DejaVuSans.ttf", 19), fill=DARK)
    im.paste(paint(ink), (40, 76))
    y = 76 + SIZE + 18
    d.text((40, y), left, font=font("DejaVuSans-Bold.ttf", 21), fill=INK)
    d.text((W - 40, y + 3), right, anchor="ra", font=font("DejaVuSans.ttf", 16), fill=GREY)
    return im


def gif(path, frames, duration):
    """Two inks plus antialiased text: 16 colours is plenty, and it is 10x smaller."""
    q = [f.quantize(colors=16, method=Image.MAXCOVERAGE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=duration,
              loop=0, optimize=True)
    return os.path.getsize(path) / 1e6


def cosines(K):
    return sum(1 if (u, v) == (0, 0) else s // 2 for (u, v), s, _ in orbits(K))


if __name__ == "__main__":
    m = ink_mask(n=N).astype(float)
    target = (p4_symmetrise(m) > 0.5).astype(float)
    F = coefficients(centred(target)); ref = target > 0.5

    # --- the chirality knob -------------------------------------------------
    ts = list(np.linspace(1.5, 0.0, 34)) + list(np.linspace(0.0, 1.5, 34))[1:]
    frames = []
    for t in ts:
        G = knob(F, t)
        frames.append(framed(tile(G),
                             "aₘₙ(t) = (1+t)/2 · aₘₙ  +  (1−t)/2 · aₙₘ",
                             "χ = %.3f" % chi(G),
                             "t = %.2f" % t))
    mb = gif("web/chirality.gif", frames, 90)
    print("chirality.gif  %d frames  %.1f MB" % (len(frames), mb))

    for t, name in ((1.0, "chi_real"), (0.0, "chi_zero")):
        paint(tile(knob(F, t))).save("web/%s.png" % name)

    # --- the cutoff ---------------------------------------------------------
    Ks = sorted(set(np.round(np.linspace(1.0, np.sqrt(KMAX), 62) ** 2).astype(int)))
    grow = []
    for K in Ks:
        ink = tile(F, K)
        iou = (ink & ref).sum() / max((ink | ref).sum(), 1)
        grow.append(framed(ink,
                           "f > ½,   f = Σ aₘₙ [ cos 2π(mx+ny) + cos 2π(−nx+my) ]",
                           "%s cosines" % f"{cosines(K):,}".replace(",", " "),
                           "%.0f %% of the tile" % (100 * iou)))
    seq = [grow[0]] * 5 + grow + [grow[-1]] * 16
    mb = gif("web/drawn_by_cosines.gif", seq, 115)
    grow[-1].save("web/drawn_last.png")
    print("drawn_by_cosines.gif  K->%d  %s cosines  %.1f MB"
          % (Ks[-1], f"{cosines(Ks[-1]):,}", mb))

    # --- the cost curve, as data for the page -------------------------------
    pts = []
    for K in list(range(4, 60, 4)) + list(range(60, 241, 8)):
        ink = tile(F, K)
        pts.append({"c": cosines(K),
                    "i": round(float((ink & ref).sum() / (ink | ref).sum()), 4)})
    json.dump(pts, open("web/curve.json", "w"))
    print("curve.json  %d points, %d -> %d cosines" % (len(pts), pts[0]["c"], pts[-1]["c"]))
