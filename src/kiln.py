"""Fire the tile, let a copyist re-ink it, fire it again.

One generation is two steps:

    diffuse   cobalt spreads in the molten glaze      -> Gaussian, sigma = l
    threshold the next copyist inks what she can see  -> back to black/white

Blurring and re-thresholding is not an analogy for anything. It is the
Merriman-Bence-Osher scheme (1992), and it converges to motion by mean
curvature (Evans 1993; Barles & Georgelin 1995). Every boundary moves inward
in proportion to its own curvature. Thin tendrils are all curvature and go
first; round blobs are the fixed points and stay.

So the roundness of blue-and-white porcelain is not a taste. It is what is
left when you run a curvature flow whose timestep is a diffusion length.
"""
import numpy as np
from PIL import Image

from trace import ink_mask

N = 700
TILE_MM = 150.0
PX_PER_MM = N / TILE_MM


def gauss(f, sigma):
    """Gaussian blur by FFT, periodic -- which is what a tiled wall is."""
    n = f.shape[0]
    k = np.fft.fftfreq(n) * n
    KX, KY = np.meshgrid(k, k, indexing="xy")
    H = np.exp(-2.0 * (np.pi ** 2) * (sigma ** 2) * (KX ** 2 + KY ** 2) / n ** 2)
    return np.real(np.fft.ifft2(np.fft.fft2(f) * H))


def perimeter(m):
    """Boundary length in px: count 4-neighbour black/white transitions."""
    return int((m[:, 1:] != m[:, :-1]).sum() + (m[1:, :] != m[:-1, :]).sum())


def components(m):
    """Number of connected ink blobs (8-connectivity), by flood fill."""
    lab = np.zeros(m.shape, np.int32)
    cur = 0
    idx = np.argwhere(m)
    seen = np.zeros(m.shape, bool)
    H, W = m.shape
    for y0, x0 in idx:
        if seen[y0, x0]:
            continue
        cur += 1
        stack = [(y0, x0)]
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            lab[y, x] = cur
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    a, b = y + dy, x + dx
                    if 0 <= a < H and 0 <= b < W and m[a, b] and not seen[a, b]:
                        seen[a, b] = True
                        stack.append((a, b))
    return cur


def run(sigma_px=3.0, gens=60, keep=(0, 1, 3, 8, 20, 40, 60), n=N):
    m = ink_mask(n=n)
    frames, rows = {}, []
    for g in range(gens + 1):
        want = g in keep
        if want:
            frames[g] = m.copy()
        rows.append((g, m.mean(), perimeter(m),
                     components(m) if want else None))
        m = gauss(m.astype(float), sigma_px) > 0.5
    return frames, rows


if __name__ == "__main__":
    import sys
    sigma = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
    frames, rows = run(sigma_px=sigma, gens=60)
    print("sigma = %.1f px = %.3f mm per firing   (tile %.0f mm at %d px)"
          % (sigma, sigma / PX_PER_MM, TILE_MM, N))
    print()
    print("  %4s %10s %12s %12s" % ("gen", "ink", "perimeter", "blobs"))
    for g, ink, per, comp in rows:
        if comp is not None:
            print("  %4d %9.1f%% %12d %12d" % (g, 100 * ink, per, comp))
    for g, f in frames.items():
        Image.fromarray((~f * 255).astype(np.uint8)).save("out/gen_%02d.png" % g)
    print()
    print("wrote out/gen_*.png")
