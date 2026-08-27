"""What is behind a tile, once the tile is off.

The page lets you take a tile off the wall, and something has to be under it.
A flat panel is a lie: what is under an 1885 kitchen tile is a lime mortar bed
-- sandy, pitted with air holes, combed by whoever spread it, stained where the
damp got in, and not remotely flat.

So it is built here rather than drawn in CSS, because CSS gradients cannot do
relief and relief is the entire point. The colour is not invented: it is the
lit face of the real grout in web/wall.jpg, divided by the white of the tile
next to it, so the ratio survives the fact that the photograph is two stops
under. Everything else -- the pits, the sand, the comb, the stains -- is noise
with a light on it.

Seamless in both directions: every noise field is periodic (FFT low-pass of
periodic white noise), every pit is drawn with wrap-around, and the comb runs
at a frequency that divides the tile. So it repeats without a visible grid.

    python src/plaster.py        ->  web/plaster.jpg
"""
import numpy as np
from PIL import Image

N    = 512          # texture is NxN and tiles seamlessly
SEED = 1885         # the year on the wall
rng  = np.random.default_rng(SEED)


def periodic_noise(n, cells):
    """White noise low-passed to `cells` features across the tile.

    Done in the Fourier domain, so the result is periodic by construction --
    which is the whole reason for not using a smooth-interpolation lattice.
    """
    w = rng.standard_normal((n, n))
    fy = np.fft.fftfreq(n)[:, None] * n
    fx = np.fft.fftfreq(n)[None, :] * n
    r  = np.hypot(fy, fx)
    lp = np.exp(-(r / cells) ** 2)                 # gaussian roll-off at `cells`
    out = np.real(np.fft.ifft2(np.fft.fft2(w) * lp))
    s = out.std()
    return out / s if s else out


def fbm(n, cells, octaves=5, gain=0.55):
    """Fractal sum: each octave twice the frequency and a bit less of it."""
    out, amp, tot = np.zeros((n, n)), 1.0, 0.0
    for k in range(octaves):
        out += amp * periodic_noise(n, cells * 2 ** k)
        tot += amp
        amp *= gain
    return out / tot


def pits(n, count, rmin, rmax, depth):
    """Air holes. Lime mortar is full of them and they are what makes it ugly.

    Each is a dish with a slightly raised lip, drawn on a wrapped grid so a pit
    near an edge comes back in on the other side.
    """
    h = np.zeros((n, n))
    yy, xx = np.mgrid[0:n, 0:n]
    for _ in range(count):
        cy, cx = rng.integers(0, n, 2)
        rad    = rng.uniform(rmin, rmax)
        # wrapped distance, so the pit is continuous across the seam
        dy = np.minimum(np.abs(yy - cy), n - np.abs(yy - cy))
        dx = np.minimum(np.abs(xx - cx), n - np.abs(xx - cx))
        d  = np.hypot(dy, dx) / rad
        m  = d < 1.6
        if not m.any():
            continue
        # dish inside r, lip just outside it
        bowl = np.where(d < 1.0, -np.cos(d * np.pi / 2) ** 2, 0.0)
        lip  = np.where((d >= 1.0) & (d < 1.6), 0.22 * np.sin((1.6 - d) * np.pi / 0.6), 0.0)
        h += depth * rng.uniform(.55, 1.0) * (bowl + lip)
    return h


def build():
    n = N

    # ---- height: what the light will actually be reading -------------------
    h  = 0.80 * fbm(n, 3.0, octaves=6)            # slow undulation, a bad float
    h += 0.36 * fbm(n, 14.0, octaves=4)           # trowel-scale lumps
    h += 0.24 * fbm(n, 70.0, octaves=2)           # sand
    h += 0.17 * periodic_noise(n, 190.0)          # grit, near pixel scale

    # the comb: whoever bedded this tile dragged a notched trowel through it.
    # 7 ridges across the tile at -22 degrees, both integers, so it wraps.
    yy, xx = np.mgrid[0:n, 0:n]
    th = np.deg2rad(-22.0)
    # rounded to integer wave numbers in x and y or the seam shows
    kx, ky = 7, 3
    comb = np.sin(2 * np.pi * (kx * xx + ky * yy) / n)
    h += 0.17 * np.sign(comb) * np.abs(comb) ** 1.7      # flat-topped ridges

    h += pits(n, 110, 2.0, 6.0, 0.42)             # air holes
    h += pits(n, 12, 8.0, 15.0, 0.32)             # the bigger blow-outs
    h -= 0.5 * np.clip(fbm(n, 5.0, octaves=3) - 0.82, 0, None) * 4   # crumbled chips
    h = (h - h.mean()) / h.std()

    # ---- albedo: the colour before any light ------------------------------
    # Lit face of the real grout / white of the tile beside it, in web/wall.jpg:
    #   (84,83,73) / (119.1,122.5,121.5) = (0.705, 0.678, 0.601)
    # times the page's paper (247,245,240) -> a dirty warm mortar.
    # ...then opened up, because that ratio is the *shadowed* joint between two
    # tiles and nineteenth-century lime plaster is pale.
    #
    # The first version that was rough enough was also far too loud: bright,
    # lumpy, high-contrast, reading as a different material from the tile it
    # came out from under, and the writing had no chance on it. So the relief
    # is shallow now and the light nearly flat -- the surface is still sand and
    # air holes and a dragged comb, but it whispers them.
    base = np.array([174.0, 166.0, 144.0]) * 1.34
    alb  = np.repeat(base[None, None, :], n, 0).repeat(n, 1)

    # Plaster is one colour with dirt on it. Every earlier attempt that gave the
    # damp and the rust real saturation came out as camouflage, so they are here
    # only as changes in value, near enough neutral, and the surface carries its
    # ugliness in the relief instead.
    tone  = fbm(n, 2.5, octaves=4)                       # patchiness, value only
    alb  *= (1.0 + 0.045 * tone)[..., None]

    damp  = np.clip(fbm(n, 1.8, octaves=3) - 0.30, 0, None)   # darker, barely cooler
    alb  -= (damp * 13)[..., None]
    alb[..., 2] += damp * 5

    lime  = np.clip(fbm(n, 6.0, octaves=3) - 0.70, 0, None) * 2.0   # dried lime, paler
    alb  += (lime * 13)[..., None]

    stain = np.clip(fbm(n, 3.2, octaves=4) - 0.92, 0, None) * 2.0   # rust, rare
    alb[..., 0] += stain * 8
    alb[..., 1] += stain * 6
    alb[..., 2] -= stain * 6

    sand  = (rng.random((n, n)) < 0.010) * rng.uniform(7, 20, (n, n))  # quartz specks
    alb  += sand[..., None]

    # ---- light: same 116 degrees the glaze highlight uses on the tile ------
    # so the wall and the tile that came off it are lit by the same window.
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
    relief = 1.05
    nz = 1.0 / np.sqrt(1.0 + relief ** 2 * (gx ** 2 + gy ** 2))
    nx, ny = -relief * gx * nz, -relief * gy * nz

    a = np.deg2rad(116.0)
    L = np.array([np.sin(a), -np.cos(a), 0.80]);  L /= np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    shade = 0.845 + 0.215 * diff                      # ambient + directional
    # cavity: pits keep their own shadow even where the light would reach
    shade *= 1.0 + 0.045 * np.clip(h, -3, 0.6)

    out = np.clip(alb * shade[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGB")


if __name__ == "__main__":
    img = build()
    img.save("web/plaster.jpg", quality=88, optimize=True, subsampling=0)
    a = np.asarray(img, float)
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]) / 255
    print("web/plaster.jpg  %dx%d  %.0f kB" % (
        img.width, img.height, len(open("web/plaster.jpg", "rb").read()) / 1000))
    print("luminance  mean %.3f  p5 %.3f  p95 %.3f" % (
        lum.mean(), np.percentile(lum, 5), np.percentile(lum, 95)))
    # contrast of the page's ink (#282c34) against the mean of this surface
    ink = 0.028
    L1, L2 = max(lum.mean(), ink), min(lum.mean(), ink)
    print("ink contrast   %.1f:1" % ((L1 + 0.05) / (L2 + 0.05)))
