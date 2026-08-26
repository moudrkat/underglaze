# underglaze

**[Talk to a brick wall →](https://unt1l1f1nd-talk-to-a-brick-wall.static.hf.space)**

One kitchen wall in a valley under the Krkonoše, photographed once. Nine tiles, each put a
different question about itself, each answering with a measured number. Ask it in plain words,
or let a browser agent drive it.

| the tile asks | it answers |
|---|---|
| how many cosines I take | 62 815 for 99 %; strokes are worse at every budget |
| what the fire does to me | perimeter 40 744 → 6 210; curvature flow has no fixed point |
| when my blue joins up | largest piece 10.7 % → 46.3 % between θ = 0.55 and 0.53 |
| what you actually see of me | 26 129 cosines reach an eye at 2 m, 6 427 at 4 m |
| which way I curl | p4, not p4m — mirrors score at the level of a meaningless shift |
| the fractal I am not | box dimension climbs 0.90 → 1.95; a fractal holds one value |
| three centuries of being copied | with a copyist 0.795 after 25 firings; without, the fine work goes |
| how much of me can be replaced | 5 % of the largest coefficients, and it is a different tile |
| what attention finds in me | repetition, never symmetry — lift 0.2–0.9 against chance |

## The equation

```
f(x,y) = Σ a_mn [ cos 2π(mx+ny)/L  +  cos 2π(−nx+my)/L ]     blue where f > ½
```

Put the origin on the tile's four-fold centre and C4 plus reality force every coefficient
**real** — there are no sine terms. Every `a_mn` is measured off the photograph, none chosen.

## Three results worth the trip

**It is not cibulák.** Zwiebelmuster has five motifs; audited against a marked Meissen plate this
tile has the aster and none of the fruit. *An onion pattern with no onion in it.*

**Identity is a few dozen numbers.** Keep every magnitude and give 5 % of the signs fresh random
values, largest first, and the tile scores 0.149 against itself — below the 0.186 that two
unrelated rebuilds reach by chance. Replace 95 % of the smallest and it still scores 0.618.

**Attention cannot see symmetry.** Patches as their own queries and keys land on their p4
partners *less* than chance. Cosine similarity is not rotation-invariant and p4 acts by rotation,
so a mechanism blind to geometry finds repetition and never symmetry.

## What is not settled

`curl.py` tried to show that a larger chirality looks *more twisted* and could not: the skeleton
has no segment longer than 27 px. `Ea` for Co²⁺ in a glaze melt is unpinned and moves the
predicted edge width by 40×, so no bleed length is quoted. The Porod slope could not separate a
fractal from a smooth boundary. The copyist who only remembers a vocabulary does **worse** than
no copyist at all, which may be a fact or may be an artefact of the measure. Whether the nine
tiles are one print or nine is undecided: tile-to-tile correlation came out at +0.006 against
+0.132 for a meaningless shift, which measures a failed registration and nothing else.

## Which model drives it?

Two, and the interesting part is which one wins.

`wall.ask()` began as a deterministic regular-expression router. **That was a mistake I made
about the platform, not a constraint:** an in-browser model needs no key, no backend and no
paid API, so "a static page cannot carry a key" was never a reason to skip one. It carries one
now.

**all-MiniLM-L6-v2**, 23 MB, loads by itself through transformers.js and embeds whatever you
type. **SmolLM2-135M-Instruct**, 117 MB, is behind a button, because half a gigabyte arriving
uninvited from a link is not a welcome. Qwen2.5-0.5B was the first choice at 483 MB and lost on
size alone.

Three question sets, in `src/eval_wall.py`. The first 51 were written next to the patterns; the
next 30 blind; the last 30 after both routers existed and shown to neither while being written.
Only the third comparison means anything:

| on 30 questions neither was tuned on | correct |
|---|---|
| regular expression alone | 14 / 30 |
| all-MiniLM-L6-v2 alone | **21 / 30** |
| words first, model for the rest | **22 / 30** |

The regex scores 81/81 on the sets it was tuned on and 47 % on fresh ones, which is what
overfitting looks like from the inside. A 23 MB model beats it outright on questions nobody
tuned for, and the two together beat either.

One thing the model cannot do: tell a real question from nonsense. *"What time is it?"* scores
0.103 against the nine tiles and the weakest genuine question scores 0.083, so the bands
overlap and no clean threshold exists. The page uses 0.10 and accepts that it will sometimes
answer the weather.

## Files

```
src/fourier.py      the series — the written cos form matches the FFT to 5e-15
src/symmetry.py     which wallpaper group, measured before anything was drawn
src/chirality.py    one knob: a_mn(t) = (1+t)/2 a_mn + (1−t)/2 a_nm
src/kiln.py         blur + re-threshold = Merriman–Bence–Osher = curvature flow
src/scales.py       how far cobalt diffuses in a firing, and whether it is measurable
src/strokes.py      cosines priced against a stroke basis at equal fidelity
src/fractal.py      three tests for a fractal, one of which decides nothing
src/fractalise.py   building one anyway, to check the ruler
src/percolation.py  where the threshold stops being a choice
src/acuity.py       what an eye receives from across the room
src/theseus.py      how much can be replaced before it is a different tile
src/attention.py    repetition yes, symmetry no
src/memory.py       the kiln with a copyist who has the original on her desk
src/hopfield.py     the honest version, where she only remembers — it fails
src/wall.py         the wall's lattice, and the comparison that is not settled
src/eval_wall.py    81 questions put to the router
src/curl.py         a failed measurement, kept
```

Every table in `theory/` is generated by the module named at the top of it. Regenerate, do not
hand-edit.
