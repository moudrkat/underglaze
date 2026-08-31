"""Eight cold visits to the page, pressing only what a visitor can press.

No model is fetched, so this runs in a minute and can be run after every build.
It is the half of the evaluation that is not about what a model decides: does
the page load without an error, does the wall take turns and then sing, does it
go back to how it was found when it stops, can somebody who never presses the
506 MB button still reach the sliders and the writing.

Two things it has already caught: pressing play a second time left all nine
sliders part way along their travel, and the wall-only take opened part way
into a beat because the page starts performing 1.4 s after it loads.

    python -m http.server 8777        # from the repo root
    python src/eval_page.py
"""
from playwright.sync_api import sync_playwright
import time

URL = "http://localhost:8777/web/wall.html"
fails = []

def visit(b, name, body, width=920, height=560):
    errs = []
    pg = b.new_page(viewport={"width": width, "height": height})
    pg.on("pageerror", lambda e: errs.append("JS: " + e.message))
    pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
    pg.on("requestfailed", lambda r: errs.append("404: " + r.url.split("/")[-1]))
    pg.goto(URL)
    notes = []
    try:
        body(pg, notes)
    except Exception as e:
        notes.append("EXCEPTION " + str(e)[:120]); errs.append("threw")
    # the invariant is "after it stops it is back", not "it never moves" -- a
    # tile mid sweep is off its rest position because that is the animation
    pg.evaluate("wall.stop()"); pg.wait_for_timeout(900)
    off = pg.evaluate("() => [...document.querySelectorAll('.tile input[type=range]')]"
                      ".filter(r=>r.value!==r.defaultValue).length")
    notes.append("back at rest once stopped: %s%s" % (off == 0,
                 "  (the slider was dragged on purpose)" if "sliders" in name else ""))
    print("\n%s" % name)
    for n in notes:
        print("   " + n)
    if errs:
        print("   ERRORS: %s" % errs[:3]); fails.append(name)
    else:
        print("   no errors")
    pg.close()

def watch(pg, notes):
    """opens it and does nothing at all"""
    pg.wait_for_timeout(9000)
    n = pg.locator(".tile.speaking").count()
    notes.append("after 9 s untouched, %d tile(s) speaking" % n)
    notes.append("line reads: %r" % pg.locator("#said").inner_text()[:70])

def play_first(pg, notes):
    """presses play before anything else"""
    pg.wait_for_timeout(600)
    pg.click("#play")
    pg.wait_for_timeout(2500)
    notes.append("play -> %d speaking" % pg.locator(".tile.speaking").count())
    pg.click("#play"); pg.wait_for_timeout(1500)
    notes.append("play again -> %d speaking, %d off rest"
                 % (pg.locator(".tile.speaking").count(),
                    pg.evaluate("() => [...document.querySelectorAll('.tile input[type=range]')]"
                                ".filter(r=>r.value!==r.defaultValue).length")))

def tile_first(pg, notes):
    """clicks a tile's ? straight away, while the wall is still performing"""
    pg.wait_for_timeout(1800)
    pg.click('[data-tile="frac"] .q')
    pg.wait_for_timeout(1200)
    notes.append("%d tile open" % pg.locator(".tile.open").count())
    notes.append("behind it: %r" % pg.locator(".tile.open .say").inner_text()[:60].replace("\n"," "))
    pg.click('[data-tile="frac"] .q'); pg.wait_for_timeout(800)
    notes.append("clicked again -> %d open" % pg.locator(".tile.open").count())

def sliders(pg, notes):
    """finds the sliders and drags one"""
    pg.wait_for_timeout(5000)
    pg.evaluate("wall.stop()")
    if pg.locator("text=move it yourself").count():
        pg.click("text=move it yourself")
    else:
        pg.click("#knobs")
    pg.wait_for_timeout(500)
    notes.append("sliders visible: %s" % pg.locator("#cutr").is_visible())
    r = pg.locator("#cutr")
    r.fill("18"); pg.wait_for_timeout(600)
    notes.append("dragged cut to 18, image now %r"
                 % pg.get_attribute("#cutimg", "src").split("/")[-1])

def type_without_model(pg, notes):
    """tries to ask something without pressing the button"""
    pg.wait_for_timeout(1200)
    q = pg.locator("#q")
    notes.append("box disabled: %s" % q.is_disabled())
    notes.append("placeholder: %r" % q.get_attribute("placeholder"))
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(600)
    notes.append("return pressed anyway, line: %r" % pg.locator("#said").inner_text()[:50])

def interrupt(pg, notes):
    """clicks around while the wall is mid sweep"""
    pg.wait_for_timeout(2500)
    for sel in ("#play", '[data-tile="kil"] .q', "#knobs", "#play"):
        pg.click(sel); pg.wait_for_timeout(500)
    pg.evaluate("wall.stop()"); pg.wait_for_timeout(1200)
    notes.append("survived four rapid clicks mid sweep")

def phone(pg, notes):
    """a phone"""
    pg.wait_for_timeout(3000)
    w = pg.evaluate("() => document.body.scrollWidth")
    notes.append("body scrollWidth %d in a %d viewport" % (w, 390))
    notes.append("wall visible: %s" % pg.locator(".wall").is_visible())
    notes.append("bar visible: %s" % pg.locator("#speak").is_visible())

def about(pg, notes):
    """presses the ? in the bar"""
    pg.wait_for_timeout(1500)
    pg.click("button[onclick='wall.about()']")
    pg.wait_for_timeout(800)
    notes.append("bubble open: %s" % pg.evaluate("() => document.getElementById('bub').classList.contains('on')"))
    notes.append("bubble says: %r" % pg.locator("#bubt").inner_text()[:70].replace("\n"," "))

with sync_playwright() as b0:
    b = b0.chromium.launch()
    visit(b, "1. opens it and watches", watch)
    visit(b, "2. presses play, then play again", play_first)
    visit(b, "3. takes a tile off the wall straight away", tile_first)
    visit(b, "4. finds the sliders and drags one", sliders)
    visit(b, "5. tries to ask without pressing the button", type_without_model)
    visit(b, "6. clicks four things mid sweep", interrupt)
    visit(b, "7. on a phone", phone, width=390, height=780)
    visit(b, "8. presses the ?", about)
    b.close()

print("\n%d visits with errors" % len(fails), fails if fails else "")
