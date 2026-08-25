"""One knob: how far the tile is from having mirrors.

p4 has no mirrors, so (m,n) and (n,m) are different orbits and a_mn need not
equal a_nm. Swapping m and n is exactly the transpose of the coefficient array,
so the whole knob is one line:

    a(t) = (1+t)/2 * a  +  (1-t)/2 * a^T

t = 1 leaves the tile alone. t = 0 forces a_mn = a_nm, which is p4m -- the
mirror-symmetric tile nobody ever painted. t > 1 pushes past the original.

What comes out is not a subtle difference. Chirality is what growing things
have and crystals do not, so a botanical pattern with its handedness removed
stops looking grown and starts looking frozen.
"""
import numpy as np

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fourier import orbits, N


def knob(F, t):
    return (1 + t) / 2.0 * F + (1 - t) / 2.0 * F.T


def chi(F, K=24):
    num = den = 0.0
    for (u, v), _, _ in orbits(K):
        a, b = F[u % N, v % N].real, F[v % N, u % N].real
        num += (a - b) ** 2
        den += a * a + b * b
    return num / den
