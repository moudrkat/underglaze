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

## How it works

Nothing is downloaded when the page opens. The wall talks anyway: it has nine measured things
to say and it says them, all nine tiles moving at once for the ones the whole wall can say, one
at a time for the rest, until somebody touches something. The question box is shut until both
models are here, and says so.

Two buttons, two models, both running in the visitor's own browser. No server, no key, nothing
leaves the page. Each says its size before it spends it and removes itself once it has arrived.

```mermaid
flowchart TD
  Q(["a visitor types a question"]) --> C1

  C1["<b>call one</b> · all-MiniLM-L6-v2 · 23 MB<br/>embed the question against the nine subjects<br/><i>nearest one wins, or none of them does</i>"]
  C2["<b>call two</b> · Qwen2.5-0.5B · 483 MB<br/>that tile's ten written replies, numbered<br/><i>answer with one number, or NONE</i>"]
  C3["<b>call three</b> · Qwen2.5-0.5B<br/>write one, for this tile<br/><i>one sentence, first person</i>"]

  C1 -->|a tile| C2
  C1 -->|nothing above 0.20| C3
  C2 -->|a number| OUT
  C2 -->|NONE| C3
  C3 --> F{"a digit in it?<br/>an assistant in it?<br/>looped? wrong length?"}
  F -->|no| OWN
  F -->|yes| MISS

  OUT(["a line somebody measured and wrote"])
  OWN(["the model's own sentence"])
  MISS(["thrown away — a written refusal instead"])

  classDef page fill:#eef3fb,stroke:#213660,color:#213660
  classDef model fill:#fff,stroke:#b0554a,color:#b0554a
  class C1,C2,C3,F model
  class Q,OUT,OWN,MISS page
```

Call one takes about fifty milliseconds. Calls two and three take about thirty-five seconds on a
machine with no GPU, so the tile does not stand still through it: it is already chosen, so it
runs — out to the far end and back, over and over, the rest of the wall in shadow — with the
line above it reading *WHEN I JOIN UP is thinking…* until the sentence lands. The animation is
the answer arriving. The sentence is the caption.

**Nothing but the models decides.** There were phrase rules in front of them and they are gone,
from the code and from the comments. What is left to tune is the nine subjects the router
embeds against, and tuning those took call one from 3/27 to 23/27.

## What a small model can and cannot do here, measured

`src/eval_flow.py` presses the real button in a real browser and scores the real calls, so it
cannot drift from what ships. It puts **every question anybody has written for this wall**
through call one — 141 of them, over four sets.

| set | what it is | on the wall | refuses |
|---|---|---|---|
| CASES | written next to the patterns | 36 / 49 | 2 / 2 |
| HARD | written blind | 25 / 30 | — |
| FRESH | shown to neither router while being written | 24 / 30 | — |
| WEIRD | what people actually type | 10 / 14 | 12 / 16 |
| **all** | | **95 / 123** | **14 / 18** |

Two things moved that number a long way, and neither was the model.

**The router was comparing against twelve things, not nine.** Three of them were not tiles at
all — *show me everything*, *what is this*, *surprise me* — and they were winning: "who are you
really?", "what makes you you?" and "what was here before you?" all went to *surprise me*
rather than to a tile. They have buttons of their own. Out of the pool, and the nine went up.

**The confidence threshold was set for a different router.** Swept over all 141:

| threshold | on the wall | refuses | total |
|---|---|---|---|
| 0.10 | 98 / 123 | 9 / 18 | 107 |
| 0.12 | 95 / 123 | 11 / 18 | 106 |
| **0.14** | **95 / 123** | **14 / 18** | **109** |
| 0.20 | 82 / 123 | 17 / 18 | 99 |

Higher refuses nonsense better and answers real questions worse. 0.14 is where the two stop
paying for each other. The page ran at 0.20.

**And the nine subjects were overlapping.** *from across the room* said "the smallest detail you
can resolve", so it took *does it repeat if I look closer?*, *is there detail all the way down?*
and *what if I keep magnifying?* — all of which belong to the fractal — plus *how much
information is in you?*, which belongs to the cosines. Rewritten so the nine stop reaching into
each other, the blind set went 23 to 25 and the fresh set 20 to 24.

### Neither generator can pick a tile

| call one — which of the nine | on the wall | should refuse |
|---|---|---|
| SmolLM2-135M-Instruct, 117 MB | 0 / 18 | 9 / 9 |
| Qwen2.5-0.5B-Instruct, 483 MB | 3 / 18 | 0 / 9 |
| **all-MiniLM-L6-v2, 23 MB** | **95 / 123** | **14 / 18** |

SmolLM2 restates the question; Qwen latches onto one number and gives it to everything —
ATTENTION to all twenty-seven, then 8 to everything, then 3. Seven prompt shapes were tried
across the two: bare names, names with glosses, an options list, a labels list, numbered names,
numbered subjects, and the nine headline sentences numbered. The best reached 5 of 12. Asked
whether it is a fractal, SmolLM2 still answers *"I'm a fractal"*, which is the one thing this
page spends a page disproving.

### The one they can do is the next one down

Given the tile, Qwen picks which of its ten sentences answers the question, and picks well:

| call two — which of that tile's ten | distinct lines | took the first |
|---|---|---|
| SmolLM2-135M | always line 0 | 18 / 18 |
| **Qwen2.5-0.5B** | **9 of 9 tiles, 9 different lines** | **2 / 9** |

*who painted you?* → "Printed from steel, copied from a painting, copied from a Chinese bowl."
*when does your blue join up?* → "Push it a little further and I stop being flowers."

**A 23 MB model that produces no words beats a 483 MB one at deciding what a question is about,
and loses to it at deciding which sentence answers it.** Routing is a nearest-neighbour lookup
in an embedding space and nothing has to be said. Choosing a reply is reading. They are not the
same job and they do not want the same model.

**Call three, the one that writes.** It works, and its voice was the problem. *who cleans you?*
came back "The wall cleans itself" and *what is behind you?* came back "The walls hold stories
and memories" — but *hello* came back "Hello! How may I assist you?" and *how are you* came back
"I'm doing well, thank you." A wall that has been up since 1885 says neither, so the same trick
as the digits: the prompt names the voice, and the page throws away anything with an assistant
in it.

`evals/flow.md` has all 141 answers call one gave, with the nearest tile and the score for each.

## The wall opens as a wall

Nine sliders, and every one of them is a way of breaking the pattern. So each has a position
where the frame is closest to the tile that was photographed, and it is downhill from there in
both directions. That position is where the page opens, and it is measured rather than chosen:
`src/likeness.py` scores all 235 frames in RGB against the ink taken off the photograph and
takes the argmax per tile. Six of the nine land on an end of their slider; percolation lands on
step 8 of 26, two clicks before its own transition; attention on 25 of 26.

RGB and not overlap-of-ink, because overlap cannot see colour — on shape alone the wall opened
on an attention frame that was entirely orange and scored 0.95 for it.

Click a tile's **?** and the tile comes off the wall: it hinges on its bottom edge, tips out,
and what is behind it is the mortar bed it was set into, with the writing on a patch of
limewash. The mortar is generated (`src/plaster.py`) rather than drawn in CSS, because CSS
gradients cannot do relief, and its colour is the lit face of the real grout in `web/wall.jpg`
divided by the white of the tile beside it.

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
src/likeness.py     where each slider stands when the tile most looks like the tile
src/plaster.py      what is behind a tile, once the tile is off
src/film_wall.py    films the page answering three questions, 1 tile then 3 then 9
src/eval_flow.py    presses the button and scores the three calls, in the page
```

Every table in `theory/` is generated by the module named at the top of it. Regenerate, do not
hand-edit.
