# underglaze

A blue kitchen tile in a deep valley under the Krkonoše — the kind that is in
every other Czech house. The pattern is
*cibulák* — Meissen's Zwiebelmuster, 1739, itself a copy of Chinese blue-and-
white. The "onions" are not onions. They are peaches and pomegranates, drawn by
European painters who had never seen either.

It has been copied for nearly three centuries through steadily worse channels —
hand-painting, transfer print, screen print, finally a bathroom wall — and it
still comes out looking like itself.

**This project is about why.**

## The claim

The finest line a blue-and-white painter can draw is not set by the brush. It
is set by how far cobalt diffuses into the molten glaze while the kiln sits at
peak. Draw finer than that and the fire erases it.

So the copy chain has a **physical low-pass filter** in it, and its cutoff is a
diffusion length. Every generation of copyists who drew too fine had the detail
taken back out by the kiln. The motif is round and heavy because thin did not
survive. The pattern is an attractor, and the basin is shaped by `D`.

## The equation

```
f(x, y) = Σ  exp( −|k_mn|² ∫D dt ) · [ c_mn C_mn(x, y)  +  s_mn S_mn(x, y) ]
         m,n

C_mn = cos(2π(mx+ny)/L) + cos(2π(−nx+my)/L)
S_mn = sin(2π(mx+ny)/L) + sin(2π(−nx+my)/L)

blue where f > θ
```

Two halves, and they were found from two different directions:

- `C_mn`, `S_mn` are the harmonics invariant under **p4** — the symmetry the
  tile actually has (measured, see below). Not p4m: there are no mirrors.
- `exp(−|k|² ∫D dt)` is the **diffusion propagator**. It is not a stylistic
  blur. It is the kiln.

Which means the "watch it appear out of nothing" animation is not an effect
laid over the tile. Running `∫D dt` from large down to zero **replays the
firing backwards**.

## Two tracks

**A — the kiln.** `src/scales.py`. What survives a firing, and can we measure
it. Status: first table done, see `theory/scales.md`.

**B — the group.** `src/symmetry.py`. Which wallpaper group, what the chirality
is worth, and the render. Status: group identified, basis not built yet.

## What is settled

**The tile is p4, and it is chiral.** Measured on `data/tile_single.jpg` by
correlating the tile against each symmetry of the square:

```
rotations  90 +0.536   180 +0.480   270 +0.536      mean +0.517
mirrors     V +0.158     H +0.189   D +0.169  A +0.190   mean +0.176
controls    shuffled -0.002        shift 37 px +0.120
```

Mirrors sit at the level of a meaningless shift; rotations are three times
higher. So the curl in the tendrils is real structure, not drawing slop — and
it lives entirely in the `S_mn` terms, which a mirror would kill.

## What is not settled

**`Ea` for Co²⁺ in a glaze melt, and it matters more than anything else here.**
Across the plausible range 200–300 kJ/mol the predicted edge width moves by a
factor of **40** (0.74 mm → 0.019 mm). Any single number quoted for the bleed
length right now is decoration. What *is* robust is the contrast: at every `Ea`,
a 1400 °C high fire bleeds 2–5 orders of magnitude more than an 800 °C decal
fire.

That inverts the experiment, and for the better. We do not measure a line to
confirm the physics — **we measure a line to invert for the firing.** The edge
of a brush stroke is a record of the kiln that fired it.

## Next

1. A real value for `D0`, `Ea` from the silicate-melt literature.
2. A macro photo of an actual underglaze piece — a *cibulák* plate or cup, the
   frame filled with ~2 cm of it. `data/tile_single.jpg` is 85 µm/px, which can
   only say "sharp"; it cannot measure a bleed. ~20 µm/px can.
3. Build the p4 basis, fit `c_mn`, `s_mn` to the tile, render.
