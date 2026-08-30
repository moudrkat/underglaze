"""What SmolLM2-135M can and cannot do in this page, measured in this page.

The wall's answer is three calls to a 135M model in the visitor's own browser:

    one    which of the nine tiles, or NONE
    two    which of that tile's ten written replies, or NONE
    three  only after two said NONE: one sentence of its own, for that tile

This runs the real page in a real browser, presses the real button, and scores
the real calls. Nothing is reimplemented here, so it cannot drift from what
ships -- the failure mode of src/eval_wall.py, which keeps a copy of the phrase
rules and has to check them against the page every run.

    python -m http.server 8777        # from the repo root
    python src/eval_flow.py           # -> evals/flow.md and a table on stdout

Call one is scored against a gold tile. Call two has no gold answer -- ten
sentences about one subject do not have a single right one -- so it is scored
on whether it *chooses*: how many distinct lines it reaches across the set, and
how often it takes the first, which is what a model that is not reading the
options does.
"""
import io
import json
import os
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = os.environ.get("WALL_URL", "http://localhost:8777/web/wall.html")
OUT = os.environ.get("WALL_EVAL_OUT", "evals/flow.md")

# Every question anybody has written for this wall, from src/eval_wall.py: the
# 51 written next to the patterns, 30 blind, 30 shown to neither router while
# they were written, and 30 of what people actually type -- one word, typos,
# Czech, emoji, boredom, prompt injection, nothing at all.
def question_sets(path="src/eval_wall.py"):
    src = io.open(path, encoding="utf-8").read()
    out = {}
    for name in ("CASES", "HARD", "FRESH", "WEIRD"):
        m = re.search(r"^%s = \[(.*?)\n\]" % name, src, re.S | re.M)
        rows = re.findall(r"\(\s*['\"]((?:[^'\"\\]|\\.)*)['\"]\s*,\s*(['\"]\w+['\"]|None)\s*\)",
                          m.group(1))
        out[name] = [(q, None if g == "None" else g.strip("'\""))
                     for q, g in rows]
    return out


MODEL = os.environ.get("WALL_MODEL", "")
THRESH = None      # read off the page below; a copy kept here is the drift
                   # this file exists to prevent, and the copy read 0.12 to
                   # the page's 0.10


def load_router(pg, timeout=900000):
    """The 23 MB one. Call one needs only this, and it never fails."""
    pg.goto(URL)
    pg.wait_for_timeout(1200)
    if MODEL:
        pg.evaluate("m => { window.WALLMODEL = m; }", MODEL)
    t0 = time.monotonic()
    pg.click("#speak")
    pg.wait_for_function("() => !!window.wall._model", timeout=timeout)
    return time.monotonic() - t0


def load_writer(pg, tries=3, timeout=1800000):
    """The 483 MB one. Fails about one attempt in two from a headless browser,
    so calls two and three are scored only if it turns up."""
    for _ in range(tries):
        # There is no second button any more: one press of #speak fetches both
        # models. This waits on the fetch the router already started rather
        # than pressing anything. It used to click #write, which has not
        # existed since the two buttons became one, and that is the reason
        # calls two and three have never once been scored.
        pg.wait_for_function(
            "() => !!window.wall._improvise || (document.getElementById('speak')"
            " && document.getElementById('speak').textContent === 'could not load')",
            timeout=timeout)
        if pg.evaluate("() => !!window.wall._improvise"):
            return True
        pg.click("#speak")          # it said it could not; ask it again
        pg.wait_for_timeout(2000)
    return False


def main():
    os.makedirs("evals", exist_ok=True)
    sets = question_sets()
    every = [(q, g, name) for name, rows in sets.items() for q, g in rows]
    print("%d questions over %d sets" % (len(every), len(sets)))
    rows, lines_seen, first_pick, line_rows = [], {}, 0, []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        secs = load_router(pg)
        global THRESH
        THRESH = pg.evaluate("() => WALLLM.THRESHOLD")
        print("router up in %.0f s, page threshold %.2f" % (secs, THRESH))

        # Call one is the router, and it is fast enough to put every question
        # through it. This is the real one in the real page, not a copy.
        print("\ncall one -- which tile, all %d questions" % len(every))
        t0 = time.monotonic()
        for q, gold, which in every:
            id_, sim = pg.evaluate("q => wall._model(q).then(m => [m[0], m[1]])", q)
            hit = id_ if (sim >= THRESH and not id_.startswith("_")) else None
            rows.append((q, gold, hit, which, id_, round(sim, 3)))
        one = time.monotonic() - t0
        for name in sets:
            got = [r for r in rows if r[3] == name]
            onw = [r for r in got if r[1]]
            off = [r for r in got if not r[1]]
            print("  %-6s  on the wall %2d/%-2d   refuses %2d/%-2d"
                  % (name, sum(1 for r in onw if r[2] == r[1]), len(onw),
                     sum(1 for r in off if r[2] is None), len(off)))
        for q, gold, hit, which, id_, sim in rows:
            if gold and hit != gold:
                print("     X  %-40s -> %-5s (%s %.2f) want %s"
                      % (q[:40] or "(empty)", str(hit), id_, sim, gold))

        # Calls two and three take about 25 s each on a CPU, so they get a
        # sample rather than all 141: one question per tile, and the awkward
        # ones for the writer.
        print("\nfetching the writer for calls two and three\u2026")
        if not load_writer(pg):
            print("  it did not turn up; call one above stands on its own")
            b.close()
            two = 0.0
            report(rows, lines_seen, first_pick, line_rows, sets, one, two)
            return rows
        print("\ncall two -- which of that tile's ten, with the tile given")
        t1 = time.monotonic()
        seen = set()
        sample = [(q, g) for q, g, _ in every
                  if g and not (g in seen or seen.add(g))]
        for q, gold in sample:
            if not gold:
                continue
            ls = pg.evaluate("t => wall.lines(t)", gold)
            r = pg.evaluate("([q,ls,t]) => wall._pickLine(q, ls, t)", [q, ls, gold])
            i = ls.index(r["line"]) if r["line"] in ls else None
            first_pick += (i == 0)
            lines_seen.setdefault(gold, set()).add(i)
            line_rows.append((q, gold, i, r["line"]))
            print("  %-44s -> %s  %s" % (q[:44], str(i), str(r["line"])[:48]))
        two = time.monotonic() - t1

        # Call three is reached in the page in exactly two places: when call
        # one found nothing above the threshold, and when call two answered
        # NONE. Both are put to it here, and what comes back is the page's own
        # _improvise -- including its reason for throwing a sentence away,
        # which only the page knows.
        print("\ncall three -- its own sentence, where nothing was written for it")
        t2 = time.monotonic()
        three_rows = []
        asks = [(q, None) for q, g, _hit, _w, _id, _sim in rows if not g]
        asks += [(q, g) for q, g, i, l in line_rows if i is None]
        for q, tile in asks:
            t, why = pg.evaluate(
                "([q,t]) => wall._improvise(q, t).then(s => [s, wall._lastToss])",
                [q, tile])
            three_rows.append((q, tile, t, why))
            print("  %-40s -> %s" % ((q[:40] or "(empty)"),
                                     (t[:52] if t else "thrown away (%s)" % why)))
        three = time.monotonic() - t2
        b.close()

    report(rows, lines_seen, first_pick, line_rows, sets, one, two,
           three_rows, three)
    return rows


def sweep(rows):
    """What the threshold is worth, over the 141 already put through call one.

    No model runs for this: every question's nearest subject and its score are
    already in rows, so moving the threshold is arithmetic. Kept in the eval
    rather than in a note because the answer changes every time the nine
    subjects are rewritten.
    """
    out = []
    for th in (0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.20):
        on = sum(1 for q, g, hit, w, id_, sim in rows
                 if g and id_ == g and sim >= th and not id_.startswith("_"))
        off = sum(1 for q, g, hit, w, id_, sim in rows
                  if not g and not (sim >= th and not id_.startswith("_")))
        out.append((th, on, off))
    return out


def report(rows, lines_seen, first_pick, line_rows, sets, one, two,
           three_rows=(), three=0.0):
    onw = [r for r in rows if r[1]]
    off = [r for r in rows if not r[1]]
    onhit = sum(1 for r in onw if r[2] == r[1])
    offhit = sum(1 for r in off if r[2] is None)
    picked = sum(len(v) for v in lines_seen.values())

    md = ["# The three calls, measured\n",
          "`python src/eval_flow.py` presses the real button in a real browser and",
          "scores the real calls. Nothing here is a reimplementation, so it cannot",
          "drift from what ships.\n",
          "## Call one, the router: all-MiniLM-L6-v2, 23 MB\n",
          "Every question anybody has written for this wall, %d of them.\n" % len(rows),
          "| set | what it is | on the wall | refuses |", "|---|---|---|---|"]
    WHAT = {"CASES": "written next to the patterns",
            "HARD": "written blind",
            "FRESH": "shown to neither router while being written",
            "WEIRD": "what people actually type"}
    for name in ("CASES", "HARD", "FRESH", "WEIRD"):
        got = [r for r in rows if r[3] == name]
        a_ = [r for r in got if r[1]]; b_ = [r for r in got if not r[1]]
        md.append("| %s | %s | **%d / %d** | %s |"
                  % (name, WHAT[name], sum(1 for r in a_ if r[2] == r[1]), len(a_),
                     ("**%d / %d**" % (sum(1 for r in b_ if r[2] is None), len(b_)))
                     if b_ else "--"))
    md += ["| **all** | | **%d / %d** | **%d / %d** |" % (onhit, len(onw), offhit, len(off)),
           "", "%.0f ms a question.\n" % (1000 * one / max(1, len(rows))),
           "## Call two, the reply: Qwen2.5-0.5B, 483 MB\n",
           "One question per tile. Scored on whether it chooses at all, since ten",
           "sentences about one subject have no single right answer.\n",
           "| | |", "|---|---|",
           "| distinct lines reached, over %d tiles | **%d** |" % (len(lines_seen), picked),
           "| took the first option | **%d / %d** |" % (first_pick, len(line_rows)),
           "", "%.1f s a question.\n" % (two / max(1, len(line_rows))),
           "## Call three, the one that writes: Qwen2.5-0.5B, 483 MB\n",
           "Put to it: every question call one refused, and every tile question",
           "call two answered NONE. A sentence is thrown away for a digit, for an",
           "assistant, for looping, or for coming out the wrong length -- and the",
           "reason is the page's own, not this file's guess at it.\n",
           "| | |", "|---|---|",
           "| asked | **%d** |" % len(three_rows),
           "| kept | **%d** |" % sum(1 for r in three_rows if r[2]),
           "| thrown away | **%d** |" % sum(1 for r in three_rows if not r[2])]
    for why in ("digit", "assistant", "loop", "length"):
        n = sum(1 for r in three_rows if not r[2] and r[3] == why)
        if n:
            md.append("| ... for a %s | %d |" % (why, n))
    md += ["", "%.1f s a question.\n" % (three / max(1, len(three_rows))),
           "## What the threshold is worth\n",
           "Swept over the same 141, no model re-run. The page ships 0.10.\n",
           "| threshold | on the wall | refuses | total |", "|---|---|---|---|"]
    for th_, on_, off_ in sweep(rows):      # not on/off: report already holds
        mark = "**" if abs(th_ - 0.10) < 1e-9 else ""   # the lists of both
        md.append("| %s%.2f%s | %d / %d | %d / %d | %d |"
                  % (mark, th_, mark, on_, len(onw), off_, len(off), on_ + off_))
    md += ["", "## Every answer call one gave\n",
           "| question | set | wanted | got | nearest | score |",
           "|---|---|---|---|---|---|"]
    for q, g, hit, which, id_, sim in rows:
        md.append("| %s | %s | %s | %s | %s | %.2f |"
                  % ((q or "(empty)").replace("|", "\\|"), which, g or "NONE",
                     hit or "NONE", id_, sim))
    md += ["", "## Every reply call two chose\n", "| question | tile | line |", "|---|---|---|"]
    for q, g, i, l in line_rows:
        md.append("| %s | %s | %s -- %s |" % (q, g, i, str(l)[:70]))
    if three_rows:
        md += ["", "## Every sentence call three wrote\n",
               "| question | tile | what came back |", "|---|---|---|"]
        for q, tile, t, why in three_rows:
            md.append("| %s | %s | %s |"
                      % ((q or "(empty)").replace("|", "\\|"), tile or "--",
                         t if t else "*thrown away -- %s*" % why))
    open(OUT, "w").write("\n".join(md) + "\n")

    print("\n  call one   on the wall %d/%d, refuses %d/%d, %d questions"
          % (onhit, len(onw), offhit, len(off), len(rows)))
    print("  call two   %d distinct lines over %d tiles, first option %d/%d"
          % (picked, len(lines_seen), first_pick, len(line_rows)))
    if three_rows:
        kept = sum(1 for r in three_rows if r[2])
        why = {}
        for r in three_rows:
            if not r[2]:
                why[r[3]] = why.get(r[3], 0) + 1
        print("  call three kept %d of %d%s"
              % (kept, len(three_rows),
                 (", thrown away for " + ", ".join("%s x%d" % (k, v)
                  for k, v in sorted(why.items()))) if why else ""))
    print("  threshold  " + "  ".join("%.2f:%d+%d" % (t, a, b_) for t, a, b_ in sweep(rows)))
    print("  wrote", OUT)


if __name__ == "__main__":
    main()
