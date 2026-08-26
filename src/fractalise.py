"""Make it a fractal, since it is not one.

src/fractal.py answers "is this a fractal" with no, and the reason is narrow:
the series stops. 62 815 cosines is a lot of cosines but it is a finite number,
so there is a smallest feature and below it the pattern is smooth. Fix exactly
that and nothing else -- add the motif back at every zoom, each copy weaker by
a fixed ratio -- and the same measurement that said no says yes.

    f_H(x) = sum_j  b^(-jH) f(b^j x)          Weierstrass, in two dimensions

b is an integer and the grid is odd, so index multiplication mod N is a
bijection: f(b^j x) is EXACT, no interpolation, and both the period and the
four-fold centre survive every level. The result is still a sum of cosines and
still p4 -- it has simply acquired a dilation symmetry it did not have.

H is the knob. Smaller H means the small copies stay loud, which means rougher:
for a self-affine field the level set has dimension D = 2 - H, and that is what
comes out of the box counting below.

Two ways to apply it, and they do different things:

  seed_stack()   stack the coarse motif on itself. This is the honest proof --
                 a clean plateau in the local slope, sitting on Koch's. It is
                 also mould. Copies land in the middle of solid areas, where
                 they punch holes, because a perturbation moves the boundary by
                 (perturbation / steepness) and the interior is flat.

  frill()        multiply the perturbation by |grad f| first. The boundary then
                 moves by a bounded amount everywhere and flat interiors do not
                 move at all, so the drawing survives and only its edge frays.

The cost is not negotiable and is worth stating plainly. Scale-free means the
wobble at scale L is (L/L0)^H times the wobble at the top. You cannot order
frilling at 2 px without accepting 2^(7H) times as much of it at 256 px. Fine
detail is not an accessory you bolt on the bottom; asking for it only at the
bottom is asking for a cutoff, which is what made the tile not a fractal.
"""
import numpy as np
from PIL import Image

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import fourier as F4
from trace import ink_mask
from fractal import boundary, local_slopes, koch

N2 = 2049                 # odd, so gcd(2, N2) = 1 and the dilation is exact
EPS = [1, 2, 4, 8, 16, 32, 64, 128, 256]
INK = 0.21                # ink fraction, held equal across every picture
PAPER_RGB, INK_RGB = (247, 245, 240), (33, 54, 96)


def coefficients():
    m = ink_mask(n=F4.N).astype(float)
    return F4.coefficients(F4.centred(F4.p4_symmetrise(m)))


def upsample(F, K, n2=N2):
    """Resample the band-limited tile onto a bigger grid, exactly.

    Zero-padding in Fourier is interpolation with the right kernel: for a
    band-limited signal it adds resolution without inventing detail, which
    matters here because invented detail is the thing being measured.
    """
    G = F4.band(F, K)
    B = np.zeros((n2, n2), complex)
    h = int(np.floor(K))
    for u in range(-h, h + 1):
        for v in range(-h, h + 1):
            if u * u + v * v <= K * K:
                B[u % n2, v % n2] = G[u % F4.N, v % F4.N]
    return np.real(np.fft.ifft2(B)) * n2 * n2


def norm(a):
    return (a - a.mean()) / a.std()


def stack(g, H=0.7, b=2, J=7, n2=N2):
    """The dilation ladder. g at scale 1, g(bx) at 2^-H, g(b^2 x) at 4^-H, ..."""
    i = np.arange(n2)
    out = np.zeros((n2, n2))
    for j in range(J + 1):
        idx = (pow(b, j, n2) * i) % n2
        out += b ** (-j * H) * g[np.ix_(idx, idx)]
    return out


def steepness(f):
    return np.hypot((np.roll(f, -1, 1) - np.roll(f, 1, 1)) / 2,
                    (np.roll(f, -1, 0) - np.roll(f, 1, 0)) / 2)


def frill(tile, seed, H=0.5, wobble=20.0):
    """Fray the edge and leave the interior alone. wobble is in pixels."""
    return tile + wobble * steepness(tile) * norm(stack(seed, H=H))


def ink_of(f, frac=INK):
    return f > np.percentile(f, 100 * (1 - frac))


def save(mask, path, size=760, n2=N2):
    im = np.roll(mask, (n2 // 2, n2 // 2), axis=(0, 1))
    rgb = np.where(im[..., None], np.array(INK_RGB, np.uint8), np.array(PAPER_RGB, np.uint8))
    Image.fromarray(rgb).resize((size, size), Image.LANCZOS).save(path)


def row(mask, label):
    print("   %-26s %s" % (label, "  ".join("%5.2f" % s
                                            for s in local_slopes(mask, EPS))))


def report(outdir="out"):
    F = coefficients()
    seed = norm(upsample(F, 8))         # the coarse motif only
    tile = upsample(F, 200)             # all 62 815 cosines

    head = "   %-26s %s" % ("", "  ".join("%3d-%-3d" % (EPS[i], EPS[i + 1])
                                          for i in range(len(EPS) - 1)))
    print("1. the proof: stack the coarse motif on itself")
    print("   a fractal holds ONE value across the row. sparse enough that the")
    print("   covering artefact stays away, so the plateau is readable.")
    print()
    print(head)
    row(boundary(ink_of(seed)), "the motif alone")
    for H in (0.9, 0.7, 0.5, 0.35):
        row(boundary(ink_of(stack(seed, H=H))), "stacked, H=%.2f  (D=2-H=%.2f)" % (H, 2 - H))
    row(koch(order=8, n=N2), "Koch curve  (D=1.262)")
    print()
    print("   flat, and on Koch's line. the construction works, and H sets where")
    print("   the plateau sits. the same test that refused the tile accepts this.")
    print()

    print("2. the same thing applied to the real tile, edge only")
    print(head)
    row(boundary(ink_of(tile)), "the tile as it is")
    for H, w in ((0.7, 20), (0.5, 20), (0.5, 60), (0.35, 60)):
        row(boundary(ink_of(frill(tile, seed, H=H, wobble=w))),
            "frilled H=%.2f wobble %dpx" % (H, w))
    print()
    print("   the dimension rises where the detail was added -- 1.07 to 1.44 at")
    print("   4-8 px -- but no plateau is claimed here and none is visible. the")
    print("   tile covers the wall, so above about 8 px the box count is measuring")
    print("   coverage, not roughness, and it drowns the signal. the plateau in")
    print("   part 1 is the evidence; this row is the picture.")
    print()

    os.makedirs(outdir, exist_ok=True)
    save(ink_of(tile), os.path.join(outdir, "frac_tile.png"))
    save(ink_of(stack(seed, H=0.7)), os.path.join(outdir, "frac_mould.png"))
    save(ink_of(frill(tile, seed, H=0.5, wobble=20)), os.path.join(outdir, "frac_frilled.png"))
    save(ink_of(frill(tile, seed, H=0.5, wobble=60)), os.path.join(outdir, "frac_frilled_hard.png"))
    print("wrote %s/frac_tile.png, frac_mould.png, frac_frilled.png, frac_frilled_hard.png" % outdir)


if __name__ == "__main__":
    report()


# --- page assets -----------------------------------------------------------

def build_page_assets(webdir="web"):
    """The fourth knob, as a gif, plus the two stills the page argues from."""
    from build_assets import framed, gif

    F = coefficients()
    seed = norm(upsample(F, 8))
    tile = upsample(F, 200)
    g = steepness(tile)
    S = norm(stack(seed, H=0.5))          # depends only on H, so build it once

    up = list(np.linspace(0, 26, 24))
    frames = [framed(np.roll(ink_of(tile + w * g * S), (N2 // 2, N2 // 2), axis=(0, 1)),
                     "wobble = %.0f px" % w, "H = 0.50")
              for w in up + up[::-1][1:-1]]
    mb = gif(os.path.join(webdir, "fractal.gif"), frames, 115)

    save(ink_of(frill(tile, seed, H=0.5, wobble=20)), os.path.join(webdir, "frac_frilled.png"))
    save(ink_of(stack(seed, H=0.7)), os.path.join(webdir, "frac_mould.png"))
    print("wrote %s/fractal.gif (%.1f MB), frac_frilled.png, frac_mould.png" % (webdir, mb))
