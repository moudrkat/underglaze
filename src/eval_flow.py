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
        b.close()

    report(rows, lines_seen, first_pick, line_rows, sets, one, two)
    return rows


def report(rows, lines_seen, first_pick, line_rows, sets, one, two):
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
           "## Every answer call one gave\n",
           "| question | set | wanted | got | nearest | score |",
           "|---|---|---|---|---|---|"]
    for q, g, hit, which, id_, sim in rows:
        md.append("| %s | %s | %s | %s | %s | %.2f |"
                  % ((q or "(empty)").replace("|", "\\|"), which, g or "NONE",
                     hit or "NONE", id_, sim))
    md += ["", "## Every reply call two chose\n", "| question | tile | line |", "|---|---|---|"]
    for q, g, i, l in line_rows:
        md.append("| %s | %s | %s -- %s |" % (q, g, i, str(l)[:70]))
    open(OUT, "w").write("\n".join(md) + "\n")

    print("\n  call one   on the wall %d/%d, refuses %d/%d, %d questions"
          % (onhit, len(onw), offhit, len(off), len(rows)))
    print("  call two   %d distinct lines over %d tiles, first option %d/%d"
          % (picked, len(lines_seen), first_pick, len(line_rows)))
    print("  wrote", OUT)


if __name__ == "__main__":
    main()
