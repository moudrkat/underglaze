# underglaze

**[Talk to a brick wall →](https://unt1l1f1nd-talk-to-a-brick-wall.static.hf.space)**

![nine painted tiles, and the line one of them just said](docs/wall.png)

One kitchen wall in a valley under the Krkonoše, photographed once. Nine tiles, each put a
different question about itself, each answering with a number measured off that photograph.

**When you are lonely you talk to the kitchen tiles. This one talks back, and you learn
something.**

```
f(x,y) = Σ a_mn [ cos 2π(mx+ny)/L  +  cos 2π(−nx+my)/L ]     blue where f > ½
```

C4 plus reality force every coefficient real — there are no sine terms. Every `a_mn` is measured,
none chosen.

## How it answers you

Two models, both in the visitor's own browser, behind one button that says what it costs before
it spends it. No server, no key, nothing leaves the page.

```mermaid
flowchart TD
  Q(["a visitor types a question"]) --> C1

  C1["<b>call one</b> · all-MiniLM-L6-v2 · 23 MB<br/>embed the question against the nine subjects<br/><i>nearest one wins, or none of them does</i>"]
  C2["<b>call two</b> · Qwen2.5-0.5B · 483 MB<br/>that tile's ten written replies, numbered<br/><i>answer with one number, or NONE</i>"]
  C3["<b>call three</b> · Qwen2.5-0.5B<br/>write one, for this tile<br/><i>one sentence, first person</i>"]

  C1 -->|a tile| C2
  C1 -->|nothing above 0.10| C3
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

A 23 MB model that produces no words beats a 483 MB one at deciding what a question is about,
and loses to it at deciding which sentence answers it. `src/eval_flow.py` presses the real button
in a real browser, so it cannot drift from what ships: **95 of 123** land on the right tile over
141 questions, all of them in `evals/flow.md`.

Press **▶** instead and the wall runs on its own — every tile at once, no model, no download.

## What did not work

- The chirality knob could not be shown to look more twisted: no skeleton segment over 27 px.
- `Ea` for Co²⁺ in a glaze melt moves the predicted bleed width by 40×, so no length is quoted.
- The Porod slope could not tell a fractal from a smooth boundary.
- A copyist who only remembers, with no original on the desk, does worse than no copyist at all.
- Whether the nine tiles are one print or nine is undecided: +0.006 against +0.132 for a
  meaningless shift, which measures a failed registration and nothing else.

## Files

`src/` is one module per tile, each generating the table in `theory/` named at the top of it —
regenerate, do not hand-edit. `src/build_wall.py` writes the page; `src/eval_flow.py` scores the
three calls inside it; `src/film_wall.py` films it.
