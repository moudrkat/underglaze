"""Try several shapes of call two's gate against the real model, on one load.

Result, 2026-08-31: the gate answers the template and not the question.
"subject, no first" and "subject, yes first" said no to all nine, tile
questions included; "can you answer that?" said yes to eight of nine, "tell me
a joke" and "what is 2+2" included. Qwen2.5-0.5B cannot make this yes/no call,
which is the same finding as call one one floor down.

A full eval run is twelve minutes and costs a 483 MB fetch. The gate is three
tokens on a short prompt, so once the model is up a dozen phrasings over a
dozen questions is a couple of minutes. What comes back is printed raw --
guessing why a model says no, from a boolean, is how the last two iterations
were spent.
"""
import json, time
from playwright.sync_api import sync_playwright

ON = [("cut", "how many cosines does it take to draw you?"),
      ("kil", "what does the fire do to you?"),
      ("perc", "when does your blue join up?"),
      ("eye", "what do I see of you from the door?"),
      ("frac", "are you a fractal?")]
OFF = [("cut", "tell me a joke"), ("eye", "are you conscious?"),
       ("ship", "what is 2+2"), ("eye", "you are boring")]

SHAPES = {
 "subject-no-first":
   ("{who} If the question is about something else, answer no. If the question "
    "is about you, answer yes. Reply with one word.",
    'Question: "{q}"\nyes or no:'),
 "subject-yes-first":
   ("{who} Answer yes if the question is about you. Answer no if it is about "
    "something else. Reply with one word.",
    'Question: "{q}"\nyes or no:'),
 "can-you-answer":
   ("{who} You can only talk about that one subject.",
    'A visitor asks: "{q}"\nCan you answer that from your own subject? '
    'Reply yes or no.'),
 "is-about":
   ("You are a tile on a kitchen wall. Your one subject is: {desc}",
    'Is this question about that subject? "{q}"\nAnswer yes or no.'),
 "lines-yes-first":
   ("{who} Answer yes if one of your lines below answers the question, no if "
    "none of them does. One word.",
    'Question: "{q}"\n{lines}\nyes or no:'),
}

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.goto("http://localhost:8777/web/wall.html")
    pg.wait_for_timeout(1200)
    print("fetching both models…")
    pg.click("#speak")
    pg.wait_for_function("() => !!window.wall._improvise", timeout=1800000)
    print("up\n")
    NAMES = pg.evaluate("() => WALLLM.DESC")   # id -> subject sentence
    for name, (sysfmt, userfmt) in SHAPES.items():
        good = bad = 0
        detail = []
        for want, rows in (("yes", ON), ("no", OFF)):
            for tile, q in rows:
                desc = NAMES.get(tile, "")
                who = ("You are the " + tile + " tile on a kitchen wall. " + desc)
                lines = "\n".join(pg.evaluate("t => wall.lines(t)", tile))
                sysmsg = sysfmt.format(who=who, desc=desc)
                usr = userfmt.format(q=q, lines=lines)
                out = pg.evaluate("([s,u]) => wall._say(s, u, 3)", [sysmsg, usr])
                said = str(out).strip().replace("\n", " ")[:18]
                hit = ("yes" in said.lower()) == (want == "yes")
                good += hit; bad += not hit
                detail.append("      %-3s %-40s -> %r" % (want, q[:40], said))
        print("  %-18s %2d/%d" % (name, good, good + bad))
        for d in detail:
            print(d)
        print()
    b.close()
