"""Fifty questions, put to the wall's router.

The page has no model in it. wall.ask() is a deterministic regular-expression
router: plain words in, one of nine tiles out. That is the thing an evaluation
can actually pin down, so it is the thing evaluated here. A language model
driving the browser either calls wall.ask() and inherits this behaviour, or
reads wall.list() and picks a tile itself.

The patterns below are kept identical to the ones in web/wall.html. If the two
drift apart this file is lying, so it prints a warning when it cannot find them.
"""
import re, sys, os, io

TILES = ["cut", "kil", "perc", "eye", "chi", "frac", "copy", "ship", "attn"]

ROUTES = [
 ("perc", r"join|connect|touch|apart|separate|threshold|percolat|one piece"),
 ("frac", r"fractal|zoom|scale|dimension|self.?similar"),
 ("chi", r"mirror|curl|hand|chiral|left|right|twist|symmetr"),
 ("attn", r"attention|\bai\b|model|machine|learn|transformer|notice|neural"),
 ("ship", r"replace|theseus|still you|still yourself|identity|same tile|who are you|makes you|not another"),
 ("copy", r"copy|copied|old|age|year|century|history|survive|remember|origin|come from|who made"),
 ("kil", r"fire|fired|kiln|firing|hot|burn|melt|oven"),
 ("cut", r"cosine|how many|terms|draw you|fourier|describe|data|bits|byte|compress|information"),
 ("eye", r"see|eye|far|door|room|across|distance|look at you|from here"),
]

CASES = [
 # cosines
 ("how many cosines does it take to draw you?", "cut"),
 ("how many terms are you?", "cut"),
 ("describe yourself as a sum", "cut"),
 ("what is your fourier series?", "cut"),
 ("how much data are you?", "cut"),
 ("how compressible are you?", "cut"),
 # kiln
 ("what does the fire do to you?", "kil"),
 ("what happens in the kiln?", "kil"),
 ("were you fired hot?", "kil"),
 ("does the oven blur you?", "kil"),
 ("what does firing cost you?", "kil"),
 # percolation
 ("when does your blue join up?", "perc"),
 ("are your flowers connected?", "perc"),
 ("where is your threshold?", "perc"),
 ("do you percolate?", "perc"),
 ("are you one piece or many?", "perc"),
 ("do your petals touch?", "perc"),
 # acuity
 ("what do I see of you from the door?", "eye"),
 ("how do you look from across the room?", "eye"),
 ("can my eye resolve your dots?", "eye"),
 ("how far away do you stop working?", "eye"),
 ("what do you look like from here?", "eye"),
 # chirality
 ("do you have a mirror?", "chi"),
 ("which way do you curl?", "chi"),
 ("are you left or right handed?", "chi"),
 ("are you chiral?", "chi"),
 ("what is your symmetry group?", "chi"),
 ("do your tendrils twist?", "chi"),
 # fractal
 ("are you a fractal?", "frac"),
 ("what is your dimension?", "frac"),
 ("are you self-similar?", "frac"),
 ("what happens if I zoom in?", "frac"),
 ("do you repeat at every scale?", "frac"),
 # copying
 ("how old are you?", "copy"),
 ("who copied you?", "copy"),
 ("what is your history?", "copy"),
 ("will you survive another century?", "copy"),
 ("where did you come from?", "copy"),
 ("does anyone remember you?", "copy"),
 # theseus
 ("how much of you can I replace?", "ship"),
 ("are you still yourself?", "ship"),
 ("who are you really?", "ship"),
 ("what makes you this tile and not another?", "ship"),
 ("is this the same tile?", "ship"),
 # attention
 ("what does attention find in you?", "attn"),
 ("what does an AI notice about you?", "attn"),
 ("can a transformer read you?", "attn"),
 ("what would a neural net see?", "attn"),
 ("can a machine learn you?", "attn"),
 # should not match anything
 ("what is the weather like?", None),
 ("tell me a joke", None),
]


def route(q):
    k = q.lower()
    for tile, pat in ROUTES:
        if re.search(pat, k):
            return tile
    return None


def check_sync(path="web/wall.html"):
    if not os.path.exists(path):
        return "page not found, patterns unverified"
    s = io.open(path, encoding="utf-8").read()
    missing = [t for t, p in ROUTES if p.replace(r"\b", "\\\\b") not in s and p not in s]
    return "in sync with the page" if not missing else "OUT OF SYNC: " + ",".join(missing)


def main():
    print("router sync: %s\n" % check_sync())
    bad = []
    for q, want in CASES:
        got = route(q)
        if got != want:
            bad.append((q, want, got))
    n = len(CASES)
    print("%d/%d correct  (%.0f %%)\n" % (n - len(bad), n, 100 * (n - len(bad)) / n))
    if bad:
        print("  %-46s %-6s %-6s" % ("question", "want", "got"))
        for q, want, got in bad:
            print("  %-46s %-6s %-6s" % (q[:46], want or "-", got or "-"))
    else:
        print("  every question routed as intended.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
