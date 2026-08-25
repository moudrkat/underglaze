"""Order-of-magnitude table for cobalt bleeding into a molten glaze.

The claim this project rests on: the finest line a blue-and-white painter can
draw is not set by the brush, it is set by how far Co2+ diffuses into the glaze
while the kiln is at peak. Draw finer than that and the fire erases it.

Everything in SI. Run it, paste the table into theory/. No number in this
project is allowed to exist only in prose.
"""
import numpy as np

R = 8.314462618          # J/(mol K)

# --- cobalt in a silicate melt --------------------------------------------
# D = D0 exp(-Ea/RT).  Divalent network-modifying cations (Ca, Mg, Fe, Co, Ni)
# in silicate melts sit broadly in D0 ~ 1e-6..1e-5 m^2/s, Ea ~ 200..300 kJ/mol
# (Zhang, Ni & Chen 2010, "Diffusion data in silicate melts", RiMG 72 — this is
# the number to pin down properly; see CAVEAT below).
D0 = 1.0e-5              # m^2/s   pre-exponential
EA_LO = 200e3            # J/mol   fast end  (depolymerised, fluid melt)
EA_HI = 300e3            # J/mol   slow end  (polymerised, stiff glaze)
EA_MID = 250e3


def D(T, Ea):
    """Arrhenius diffusivity at absolute temperature T [K]."""
    return D0 * np.exp(-Ea / (R * T))


# --- firing schedules ------------------------------------------------------
# A schedule is a list of (temperature_C, duration_s) leg endpoints, walked
# linearly. Diffusion is integrated along it: Arrhenius is steep enough that
# the integral is dominated by the top, but the ramps are not free and we do
# not get to assume that -- we integrate.
MEISSEN = [(1000, 0), (1400, 2*3600), (1400, 3*3600), (1000, 5*3600)]
# 820 C is not a guess: RAKO's current Cibulak 15x15 tile is sold as
# "dekor vypalovany pri 820 C". The 15x15 cm size is from the same spec, and
# it is what feasibility() below assumes.
DECAL   = [(400, 0), (820, 20*60), (820, 50*60), (400, 80*60)]


def integrate(schedule, Ea, n=200_000):
    """int D(T(t)) dt over the schedule [m^2]."""
    Ts = np.array([s[0] for s in schedule], dtype=float) + 273.15
    ts = np.array([s[1] for s in schedule], dtype=float)
    t = np.linspace(ts[0], ts[-1], n)
    T = np.interp(t, ts, Ts)
    return np.trapezoid(D(T, Ea), t)


def widths(schedule, Ea):
    """Gaussian sigma and visible 10-90% edge width [m].

    A sharp step smeared by diffusion becomes an erf of width sigma =
    sqrt(2 * int D dt). What the eye reads as the soft edge is the 10-90%
    rise, which for an erf is 2.563 sigma.
    """
    J = integrate(schedule, Ea)
    sigma = np.sqrt(2.0 * J)
    return sigma, 2.563 * sigma


def table():
    print("cobalt diffusivity, D = %.0e exp(-Ea/RT)  [m^2/s]" % D0)
    print()
    print("  %-14s %10s %12s %12s" % ("Ea [kJ/mol]", "T [C]", "D", ""))
    for Ea in (EA_LO, EA_MID, EA_HI):
        for Tc in (800, 1200, 1400):
            print("  %-14.0f %10d %12.2e" % (Ea/1e3, Tc, D(Tc+273.15, Ea)))
    print()
    print("edge width after firing")
    print("  %-22s %-12s %10s %10s" % ("schedule", "Ea [kJ/mol]", "sigma", "10-90%"))
    for name, sched in (("Meissen high fire", MEISSEN), ("modern decal/print", DECAL)):
        for Ea in (EA_LO, EA_MID, EA_HI):
            s, w = widths(sched, Ea)
            print("  %-22s %-12.0f %8.1f um %7.3f mm" % (name, Ea/1e3, s*1e6, w*1e3))


def feasibility(tile_mm=150.0, tile_px=1760.0):
    """Can the photo we already have even see this?

    tile_mm is documented, not assumed: RAKO Cibulak is a 15x15 cm tile.
    """
    px_per_mm = tile_px / tile_mm
    um_per_px = 1e3 / px_per_mm
    print()
    print("can we measure it, with data/tile_single.jpg?")
    print("  tile %.0f mm across, %.0f px  ->  %.1f px/mm, %.0f um/px"
          % (tile_mm, tile_px, px_per_mm, um_per_px))
    for name, sched in (("Meissen high fire", MEISSEN), ("modern decal/print", DECAL)):
        for Ea in (EA_LO, EA_HI):
            _, w = widths(sched, Ea)
            print("  %-22s Ea=%3.0f  edge %7.3f mm = %6.2f px"
                  % (name, Ea/1e3, w*1e3, w*1e3*px_per_mm))
    print("  -> at 85 um/px only the Ea=200 end is resolved. This photo can say")
    print("     'sharp' but cannot measure a bleed length.")
    print()
    print("what photo would be enough?")
    print("  %-12s %10s %12s %14s" % ("target edge", "want 5 px", "so um/px", "frame width*"))
    for w_mm in (0.02, 0.1, 0.3, 0.74):
        um_px = w_mm * 1e3 / 5.0
        frame_mm = um_px * 4000 / 1e3      # a 4000 px phone frame
        print("  %8.3f mm %10s %10.1f um %11.1f mm" % (w_mm, "5", um_px, frame_mm))
    print("  * how wide a region a 4000 px phone frame may cover.")
    print("  -> fill the frame with ~2 cm of a real underglaze piece and every")
    print("     case above is resolved.")


if __name__ == "__main__":
    table()
    feasibility()
