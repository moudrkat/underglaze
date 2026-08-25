"""The equation that draws the tile. Cosines, and nothing else.

Put the origin on the tile's four-fold centre. A real image with C4 symmetry
about the origin has purely real Fourier coefficients -- because reality gives
F(-k) = conj F(k), C4 gives F(-k) = F(k), and the two together leave no
imaginary part. So there are no sine terms. The whole tile is

    C_mn(x,y) = cos(2pi(mx+ny)/L) + cos(2pi(-nx+my)/L)

    f(x,y) = sum over p4 orbits of  a_mn * C_mn(x,y)

    blue where f(x,y) > theta

Every a_mn is measured off the photograph, not chosen. Raising the cutoff K on
m^2+n^2 is the tile drawing itself.

Where the chirality is: p4 has no mirrors, so (m,n) and (n,m) are different
orbits and a_mn need not equal a_nm. In p4m they would be equal. The imbalance
between them is the curl of the tendrils, as one number.
"""
import numpy as np

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from trace import ink_mask

N = 501                      # odd, so the quarter turn has an exact fixed point
C = (N - 1) // 2


def p4_symmetrise(img):
    return sum(np.rot90(img, j) for j in range(4)) / 4.0


def centred(img):
    """Move the four-fold centre to index (0,0)."""
    return np.roll(img, (-C, -C), axis=(0, 1))


def coefficients(img):
    """F[u,v] with f(y,x) = sum F[u,v] exp(2pi i (u y + v x) / N)."""
    return np.fft.fft2(img) / img.size


def orbits(K):
    """One representative per p4 orbit inside |k| <= K."""
    out, seen = [], set()
    R = int(np.floor(K))
    for u in range(-R, R + 1):
        for v in range(-R, R + 1):
            if u * u + v * v > K * K:
                continue
            orb = {(u, v), (-v, u), (-u, -v), (v, -u)}
            key = min(orb)
            if key in seen:
                continue
            seen.add(key)
            out.append((key, len(orb), orb))
    return out


def band(F, K):
    n = F.shape[0]
    k = np.fft.fftfreq(n) * n
    U, V = np.meshgrid(k, k, indexing="ij")
    return np.where(U * U + V * V <= K * K, F, 0)


def synth(F, K=None):
    G = F if K is None else band(F, K)
    return np.real(np.fft.ifft2(G)) * G.size


def series(F, K, n=N):
    """Sum the a_mn C_mn series literally, exactly as the docstring writes it."""
    y, x = np.mgrid[0:n, 0:n] / n
    f = np.zeros((n, n))
    for (u, v), size, orb in orbits(K):
        a = F[u % N, v % N].real
        if u == 0 and v == 0:
            f += a
            continue
        terms = np.zeros((n, n))
        for (p, q) in orb:
            terms += np.cos(2 * np.pi * (p * y + q * x))
        f += a * terms
    return f


def chirality(F, K=24):
    """How far the tile is from having mirrors. 0 = p4m, 1 = maximally chiral."""
    num = den = 0.0
    for (u, v), _, _ in orbits(K):
        a, b = F[u % N, v % N].real, F[v % N, u % N].real
        num += (a - b) ** 2
        den += a * a + b * b
    return num / den


if __name__ == "__main__":
    m = ink_mask(n=N).astype(float)
    g = centred(p4_symmetrise(m))
    F = coefficients(g)
    print("p4 projection keeps %.1f%% of the ink energy" % (100*(p4_symmetrise(m)**2).sum()/(m**2).sum()))
    print("largest imaginary part of any coefficient: %.2e  (C4 says zero)"
          % np.abs(F.imag).max())
    for K in (4, 8, 16):
        a = synth(F, K)
        b = series(F, K)
        print("verify K=%2d  %3d orbits  max|series - fft| / max|fft| = %.2e"
              % (K, len(orbits(K)), np.max(np.abs(a - b)) / np.max(np.abs(a))))
    print("chirality  %.3f   (0 would mean the tile has mirrors)" % chirality(F))
