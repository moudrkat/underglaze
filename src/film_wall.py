"""Film the wall answering three questions, for a post.

Not a slideshow of stills. A real screen recording of the real page: headless
Chromium loads web/wall.html, waits until MiniLM has actually arrived so the
status line is never caught saying "loading a model", types three short
questions at human speed, and waits for each answer to finish playing.

The three escalate -- one tile, then three, then the whole wall -- and *which*
tiles each one reaches is a fact about the router, not a script. The run checks
it and says MISMATCH if the wall answers differently, which it is free to do.

Two things are honest to state if anyone asks:

  - The page is filmed at 920x560 and scaled up, not rendered at 1080. Below
    900 px the page reflows to a phone layout, so 920 is as small -- and the
    type therefore as large -- as it can be filmed and still be the wall.
  - The two caption lines are drawn here, not screen-captured. They are the
    page's own question and the page's own tile names, set large enough to
    survive a phone-sized feed, which the 26 px UI does not.

    python -m http.server 8777          # from the repo root
    python src/film_wall.py             # -> out/talk_to_a_brick_wall.mp4
"""
import json
import os
import shutil
import subprocess
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

URL = os.environ.get("WALL_URL", "http://localhost:8777/web/wall.html")

VW, VH = 920, 560               # smallest viewport that is still the desktop wall
OW, OH = 1080, 1350             # 4:5, the shape a feed gives the most room to
FPS = 30
PAGE_W = 880                    # the page column, scaled, inside the frame
PAGE_X, PAGE_Y = (OW - PAGE_W) // 2, 24

PAPER, INK, WARM, GREY = (247, 245, 240), (33, 54, 96), (176, 85, 74), (139, 136, 128)
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

OUT = "out/talk_to_a_brick_wall.mp4"
RAW = "out/talk_to_a_brick_wall.webm"
TAKE = "out/talk_to_a_brick_wall.json"   # crop, timings, and what each question lit
TITLE = "talk to a brick wall"

# (question, how many tiles it should reach). Short, and the sort of thing
# somebody actually types at a wall.
SCRIPT = [
    ("who painted you?", 1),
    ("why are you blue?", 3),
    ("tell me everything", 9),
]

TYPE_MS = 42
HOLD_OPEN = 1500       # on the bare wall before anything is typed
HOLD_READ = 1600       # on each finished answer
HOLD_END = 2600        # on the last one

READ = ("() => [...document.querySelectorAll('.tile input[type=range]')]"
        ".map(r => r.value).join(',')")


def touch(pg):
    """Reset the page's idle timer so the wall does not interrupt the take."""
    pg.evaluate("dispatchEvent(new KeyboardEvent('keydown'))")


def wait_quiet(pg, timeout=30.0):
    """Until the sweep has started and then stopped moving.

    Not by watching .speaking: a single-tile run never takes that class off
    again -- whatever runs next clears it -- so waiting for it to go is waiting
    forever. What does end is the sliders, so watch those.
    """
    t0 = time.monotonic()
    before = pg.evaluate(READ)
    while pg.evaluate(READ) == before and time.monotonic() - t0 < 8:
        pg.wait_for_timeout(50)
    lit = pg.evaluate(
        "[...document.querySelectorAll('.tile.speaking')].map(t=>t.dataset.tile)")
    started = time.monotonic()
    last, still = pg.evaluate(READ), 0.0
    while still < 0.45 and time.monotonic() - t0 < timeout:
        pg.wait_for_timeout(70)
        now = pg.evaluate(READ)
        still = 0.0 if now != last else still + 0.07
        last = now
    return lit, started


def film():
    os.makedirs("out", exist_ok=True)
    vdir = "out/_film"
    shutil.rmtree(vdir, ignore_errors=True)
    os.makedirs(vdir)

    beats = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--force-color-profile=srgb",
                                    "--font-render-hinting=none"])
        ctx = b.new_context(viewport={"width": VW, "height": VH},
                            device_scale_factor=2,
                            record_video_dir=vdir,
                            record_video_size={"width": VW, "height": VH})
        pg = ctx.new_page()
        clock = time.monotonic()
        pg.goto(URL)
        print("waiting for MiniLM…")
        pg.wait_for_function("() => !!window.wall && !!wall._model", timeout=180000)
        pg.evaluate("wall.stop()")
        pg.wait_for_timeout(600)
        touch(pg)

        bar = pg.locator(".bar").first.bounding_box()
        wall = pg.locator(".wall").first.bounding_box()
        crop = (int(bar["x"]) - 2, int(bar["y"]) - 6,
                int(bar["x"] + bar["width"]) + 2,
                int(wall["y"] + wall["height"]) + 4)
        # the field name the tile carries in its own corner, e.g. THREE CENTURIES
        names = pg.evaluate(
            "Object.fromEntries([...document.querySelectorAll('.tile')]"
            ".map(t => [t.dataset.tile, t.querySelector('.tag').textContent]))")

        start = time.monotonic() - clock
        print("rolling at +%.1f s, crop %s" % (start, crop))
        pg.wait_for_timeout(HOLD_OPEN)

        for i, (q, want) in enumerate(SCRIPT):
            touch(pg)
            pg.click("#q")
            pg.fill("#q", "")
            pg.type("#q", q, delay=TYPE_MS)
            t_ask = time.monotonic() - clock
            pg.keyboard.press("Enter")
            lit, t_lit = wait_quiet(pg)
            pg.wait_for_timeout(HOLD_END if i == len(SCRIPT) - 1 else HOLD_READ)
            beats.append({"q": q, "wanted": want, "lit": lit,
                          "names": [names.get(t, t) for t in lit],
                          "ask": round(t_ask - start, 2),
                          "answer": round(t_lit - clock - start, 2),
                          "end": round(time.monotonic() - clock - start, 2)})
            print("  %-22s %d tile(s) %s" % (q, len(lit), beats[-1]["names"]))

        end = time.monotonic() - clock
        path = pg.video.path()
        ctx.close()
        b.close()

    shutil.move(path, RAW)
    shutil.rmtree(vdir, ignore_errors=True)
    take = {"crop": list(crop), "start": round(start, 2),
            "dur": round(end - start, 2), "beats": beats}
    json.dump(take, open(TAKE, "w"), indent=1)
    compose(take)
    return beats


def fit(draw, text, font_path, size, width):
    """Largest size at or below `size` that fits `width`, and the font."""
    while size > 10:
        f = ImageFont.truetype(font_path, size)
        if draw.textlength(text, font=f) <= width:
            return f
        size -= 2
    return ImageFont.truetype(font_path, size)


def spaced(draw, xy, text, font, fill, track):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track


def spaced_width(draw, text, font, track):
    return sum(draw.textlength(c, font=font) for c in text) + track * (len(text) - 1)


def compose(take, raw=RAW):
    """Decode, place the page on a 4:5 card, draw the two caption lines, encode.

    Done frame by frame in Pillow rather than as an ffmpeg filter graph, because
    the captions need real text metrics -- shrink-to-fit and letter tracking --
    and drawtext has neither.
    """
    crop, ss, dur, beats = (take["crop"], take["start"], take["dur"], take["beats"])
    x0, y0, x1, y1 = crop
    cw, ch = x1 - x0, y1 - y0
    scale = PAGE_W / cw
    ph = int(round(ch * scale))
    band = PAGE_Y + ph                       # where the caption area starts
    print("page %dx%d -> %dx%d, caption band %d px" % (cw, ch, PAGE_W, ph, OH - band))

    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-ss", "%.2f" % ss, "-t", "%.2f" % dur, "-i", raw,
         "-vf", "fps=%d,crop=%d:%d:%d:%d,scale=%d:%d:flags=lanczos"
                % (FPS, cw, ch, x0, y0, PAGE_W, ph),
         "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
        stdout=subprocess.PIPE)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", "%dx%d" % (OW, OH), "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
         "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", "-an", OUT],
        stdin=subprocess.PIPE)

    nbytes = PAGE_W * ph * 3
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    n = 0
    while True:
        buf = dec.stdout.read(nbytes)
        if len(buf) < nbytes:
            break
        t = n / FPS
        card = Image.new("RGB", (OW, OH), PAPER)
        card.paste(Image.frombytes("RGB", (PAGE_W, ph), buf), (PAGE_X, PAGE_Y))
        d = ImageDraw.Draw(card)

        beat = next((b for b in beats if b["ask"] <= t < b["end"]), None)
        if beat is None and t < beats[0]["ask"]:
            # the opening hold, otherwise 287 px of blank paper: name the thing
            f = ImageFont.truetype(SERIF, 46)
            d.text(((OW - probe.textlength(TITLE, font=f)) / 2, band + 68), TITLE,
                   font=f, fill=GREY)
        if beat:
            q = "“" + beat["q"] + "”"
            f = fit(probe, q, SERIF, 52, OW - 120)
            d.text(((OW - probe.textlength(q, font=f)) / 2, band + 68), q,
                   font=f, fill=INK)
            if t >= beat["answer"]:
                names = "  ·  ".join(beat["names"]) if len(beat["lit"]) < 9 \
                        else "ALL NINE"
                g = fit(probe, names, SANS, 28, OW - 160)
                track = 2.0
                w = spaced_width(probe, names, g, track)
                spaced(d, ((OW - w) / 2, band + 156), names, g, WARM, track)
        enc.stdin.write(card.tobytes())
        n += 1

    dec.stdout.close()
    enc.stdin.close()
    dec.wait()
    enc.wait()
    print("%d frames" % n)
    print(subprocess.run(["ffprobe", "-v", "error",
                          "-show_entries", "stream=width,height,r_frame_rate",
                          "-show_entries", "format=duration,size",
                          "-of", "default=nw=1", OUT],
                         capture_output=True, text=True).stdout.strip())


if __name__ == "__main__":
    import sys
    if "--recompose" in sys.argv:          # re-cut the last take, no browser
        take = json.load(open(TAKE))
        compose(take)
        rows = take["beats"]
    else:
        rows = film()
    for row in rows:
        ok = "ok" if len(row["lit"]) == row["wanted"] else "MISMATCH"
        print("  %-8s %d/%d  %s" % (ok, len(row["lit"]), row["wanted"], row["q"]))
