"""Film the wall answering two questions, for a post.

Not a slideshow of stills. A real screen recording of the real page: headless
Chromium loads web/wall.html, waits until MiniLM has actually arrived so the
status line is never caught saying "loading a model", types two short questions
at human speed, and waits for each answer to finish playing.

The two are the two halves of the flow. The first is the question the page is
named after and one tile answers it. The second is one no tile answers, so call
two says NONE and call three writes a sentence. *Which* tiles each one reaches
is a fact about the router, not a script. The run checks it and says MISMATCH if
the wall answers differently, which it is free to do.

The take opens on the wall standing still for a beat -- long enough to read as a
wall and not as an animation -- and then it starts moving on its own, uninvited.
After the first answer the take clicks the page's own "find out more", which
swings that tile's face open like a door and puts the measured paragraph behind
it on screen. That is the best motion the page has and no film has used it.

Two things are honest to state if anyone asks:

  - The page is laid out at 920x560 and drawn at twice that. Below 900 px it
    reflows to a phone layout, so 920 is as small -- and the type therefore as
    large -- as it can be filmed and still be the wall; --force-device-scale-
    factor=2 then renders those 920 CSS px into 1840 real ones, so the 818x1096
    column the film keeps is upscaled 1.23x to the frame instead of 2.46x.
    Every word in the film is the page's own, at about twice the size it is
    authored.

    python -m http.server 8777          # from the repo root
    python src/film_wall.py             # -> out/talk_to_a_brick_wall.mp4
"""
import json
import os
import shutil
import subprocess
import time

from playwright.sync_api import sync_playwright

URL = os.environ.get("WALL_URL", "http://localhost:8777/web/wall.html")

VW, VH = 920, 560               # smallest viewport that is still the desktop wall
DSF = 2                         # ... rendered at twice that, so the crop is sharp
OW, OH = 1080, 1350             # 4:5, the shape a feed gives the most room to
FPS = 30
RAMP = 9.0                      # the waiting runs this many times over
PAPER = (247, 245, 240)

OUT = "out/talk_to_a_brick_wall.mp4"
RAW = "out/talk_to_a_brick_wall.webm"
TAKE = "out/talk_to_a_brick_wall.json"   # crop, timings, and what each question lit

# --chorus: ten seconds of the whole wall moving at once and nothing else, for
# somewhere that autoplays a loop and gives it no caption.
CHORUS_OUT = "out/whole_wall_10s.mp4"
CHORUS_MS = 8200

# (question, how many tiles it should reach, whether to open the tile after).
# Short, and the sort of thing somebody actually types at a wall.
SCRIPT = [
    ("how many cosines does it take to draw you?", 1, True),
    ("how are you?", 0, False),    # nothing on the wall answers this; call three writes one
]

STILL_MS = 1200        # of the wall just being a wall, before it moves at all
PERFORM_MS = 13000     # of the wall talking to itself before anybody types
OPEN_AT_ONE = STILL_MS / 1000 + 6.2   # of the opening kept; the rest is cut out

TYPE_MS = 42
HOLD_OPEN = 1000       # on the bare wall before anything is typed
HOLD_READ = 2600       # on the answer, once it has landed
HOLD_PAGE = 700        # after each answer paged to
HOLD_END = 1400        # on the last one
HOLD_OPEN_TILE = 3400  # on the tile hanging open with its paragraph showing

# --wall-only: no models, no questions, nothing downloaded. Just the thing the
# page does the moment it is opened and nobody touches it, and then one tile
# coming off the wall. Everything in it runs at 1x -- there is no waiting in it
# to speed up, because nothing in it is waiting on a model.
WALL_ONLY_MS = 45000   # longest the chorus may take to come round
OPEN_TILE = "cut"      # the one that swings open at the end

READ = ("() => [...document.querySelectorAll('.tile input[type=range]')]"
        ".map(r => r.value).join(',')")


def touch(pg):
    """Reset the page's idle timer so the wall does not interrupt the take."""
    pg.evaluate("dispatchEvent(new KeyboardEvent('keydown'))")


def wait_answer(pg, timeout=90.0):
    """Wait for the sentence, not for the sweep.

    The tile loops now, so "the sliders have come back to where they started"
    happens at the end of every pass and says nothing about whether the model
    has finished. What ends is the line above the wall: it reads "... is
    thinking" until the answer replaces it.
    """
    said = "() => document.querySelector('.said').textContent"
    pg.wait_for_function(
        "() => { const t = document.querySelector('.said').textContent;"
        "        return t && t.indexOf('thinking') < 0; }",
        timeout=int(timeout * 1000))
    lit = pg.evaluate(
        "[...document.querySelectorAll('.tile.speaking')].map(t=>t.dataset.tile)")
    return lit, time.monotonic()


def film(wall_only=False, chorus=False):
    """Roll on the wall talking to itself, then ask it two things.

    With wall_only the second half never happens: no button is pressed, no model
    is fetched, and the film is the wall performing uninvited and then one tile
    hinging off it. That take needs nothing but the page.

    Both models are fetched before the camera starts, because 506 MB of progress
    bar is not the film. What is filmed is the wall performing without being
    asked -- which is what it does the moment anybody opens the page -- and then
    a question going into a box that only opens once both models are here.

    The answers are slow. Thirty-five seconds a sentence on a machine with no
    GPU, and the film does not cut that out: the wall says it is thinking,
    because it is, and that is the price of no server and no key.
    """
    os.makedirs("out", exist_ok=True)
    vdir = "out/_film"
    shutil.rmtree(vdir, ignore_errors=True)
    os.makedirs(vdir)

    beats = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--force-color-profile=srgb",
                                    "--font-render-hinting=none",
                                    "--force-device-scale-factor=%d" % DSF])
        ctx = b.new_context(viewport={"width": VW, "height": VH},
                            device_scale_factor=DSF,
                            record_video_dir=vdir,
                            record_video_size={"width": VW * DSF,
                                               "height": VH * DSF})
        pg = ctx.new_page()
        clock = time.monotonic()
        pg.goto(URL)
        # the page starts performing by itself 1.4 s after it loads. Stopping at
        # 1.0 s stopped nothing and the take opened part way into a beat, so the
        # wait here has to outlast that timer.
        pg.wait_for_timeout(2200)
        pg.evaluate("wall.stop()")
        if not (wall_only or chorus):
            print("fetching both models…")
            # one button, both models; the 483 MB half fails about one attempt
            # in two from a headless browser, so it gets three
            for attempt in range(3):
                pg.click("#speak")
                pg.wait_for_function(
                    "() => !!window.wall._improvise || (document.getElementById('speak')"
                    " && document.getElementById('speak').textContent === 'could not load')",
                    timeout=1800000)
                if pg.evaluate("() => !!window.wall._improvise"):
                    break
                print("  attempt %d failed, retrying" % (attempt + 1))
                pg.wait_for_timeout(2000)
            if not pg.evaluate("() => !!window.wall._improvise"):
                raise SystemExit("the models did not load")
            print("both up")
        pg.evaluate("wall.stop(); wall.reset(); wall.say('')")
        pg.wait_for_timeout(400)
        bar = pg.locator(".bar").first.bounding_box()
        wall = pg.locator(".wall").first.bounding_box()
        # boxes come back in CSS px; the video is DSF times that
        crop = (int(bar["x"] * DSF) - 4, int(bar["y"] * DSF) - 12,
                int((bar["x"] + bar["width"]) * DSF) + 4,
                int((wall["y"] + wall["height"]) * DSF) + 8)

        start = time.monotonic() - clock
        print("rolling at +%.1f s, crop %s" % (start, crop))

        # a wall, and then -- with nobody having touched anything -- a wall
        # that moves
        pg.wait_for_timeout(STILL_MS)
        if chorus:
            # the play button's own function: every tile at once, which is the
            # one thing the wall does that reads at the size of a thumbnail
            pg.evaluate("() => { wall.all(); }")
            pg.wait_for_timeout(CHORUS_MS)
            pg.evaluate("wall.stop()")
            pg.wait_for_timeout(600)
        elif wall_only:
            pg.evaluate("() => { wall.perform(); }")
            lit9 = "() => document.querySelectorAll('.tile.speaking').length === 9"
            rest = ("() => [...document.querySelectorAll('.tile input[type=range]')]"
                    ".every(r => r.value === r.defaultValue)")
            pg.wait_for_function(lit9, timeout=WALL_ONLY_MS)   # one tile, another, then all
            pg.wait_for_timeout(700)                           # it is moving now
            pg.wait_for_function(rest, timeout=30000)          # and it has come back
            pg.wait_for_timeout(HOLD_END)
            pg.evaluate("wall.stop()")
            pg.wait_for_timeout(400)
        else:
            pg.evaluate("() => { wall.perform(); }")
            pg.wait_for_timeout(PERFORM_MS)
            pg.evaluate("wall.stop()")
            pg.wait_for_timeout(500)

        for i, (q, want, tell) in enumerate([] if (wall_only or chorus) else SCRIPT):
            touch(pg)
            pg.click("#q")
            pg.fill("#q", "")
            pg.type("#q", q, delay=TYPE_MS)
            t_ask = time.monotonic() - clock
            pg.keyboard.press("Enter")
            lit, t_lit = wait_answer(pg)
            pg.wait_for_timeout(HOLD_READ)
            if tell:
                # the page's own link, under the sentence it just handed over
                touch(pg)
                pg.click(".more a[data-t]")
                pg.wait_for_selector(".tile.open", timeout=5000)
                pg.wait_for_timeout(HOLD_OPEN_TILE)
            beats.append({"q": q, "wanted": want, "lit": lit,
                          "ask": round(t_ask - start, 2),
                          "answer": round(t_lit - clock - start, 2),
                          "end": round(time.monotonic() - clock - start, 2)})
            print("  %-30s %d tile(s) %s" % (q, len(lit), lit))
            if i == len(SCRIPT) - 1:
                pg.wait_for_timeout(HOLD_END)

        end = time.monotonic() - clock
        path = pg.video.path()
        ctx.close()
        b.close()

    shutil.move(path, RAW)
    shutil.rmtree(vdir, ignore_errors=True)
    take = {"crop": list(crop), "start": round(start, 2),
            "dur": round(end - start, 2), "beats": beats}
    json.dump(take, open(TAKE, "w"), indent=1)
    compose(take, out=CHORUS_OUT if chorus else OUT)
    return beats


def compose(take, raw=RAW, out=OUT):
    """Crop the page column out of the capture and let it fill the frame.

    There used to be a caption band under the wall with the question and the
    tile names drawn large. It was there because the page was filmed small and
    its own type came out at 26 px. Dropping the band gives the page the whole
    1080x1350 instead of 820 of it -- the column is 433x548, which is 0.79 to
    the frame's 0.80, so it very nearly fits exactly -- and everything the band
    was restating is now legible in the page itself at about twice the size.
    """
    crop, ss, dur, beats = (take["crop"], take["start"], take["dur"], take["beats"])
    x0, y0, x1, y1 = crop
    cw, ch = x1 - x0, y1 - y0
    print("page %dx%d -> fills %dx%d at %.2fx" % (cw, ch, OW, OH, min(OW / cw, OH / ch)))

    # The waiting is real and it is long: the tile runs for half a minute while
    # a 0.5B model reads ten sentences on somebody's CPU. Nothing is cut out and
    # nothing is faked, but those stretches run at RAMP times over, because a minute of a
    # tile going out and back says the same thing as five seconds of it. The
    # typing, the sentence landing, and the wall's own performance stay at 1x.
    fast = [(b["ask"] + 1.8, b["answer"] - 1.0, RAMP) for b in beats
            if b["answer"] - b["ask"] > 5.0]
    # The wall's opening performance is the point of the film, but not all of
    # it. Sampled frame by frame: the first chorus line finishes landing at
    # 5.5 s and then nothing changes for four seconds before the second one
    # starts. That gap is cut out, not sped up -- rate 0 drops a segment -- so
    # the film is one chorus and then somebody types.
    if beats:
        opening = beats[0]["ask"] - 1.2
        if opening > OPEN_AT_ONE + 1.0:
            fast.insert(0, (OPEN_AT_ONE, opening, 0.0))
    fast.sort()
    segs, filt, k, t = [], [], 0, 0.0
    for a, z, rate0 in fast + [(dur, dur, 1.0)]:
        for lo, hi, rate in ((t, a, 1.0), (a, z, rate0)):
            if hi - lo <= 0.04 or rate == 0.0:      # rate 0 means drop it
                continue
            filt.append("[0:v]trim=%.3f:%.3f,setpts=(PTS-STARTPTS)/%.1f[v%d]"
                        % (lo, hi, rate, k))
            segs.append("[v%d]" % k); k += 1
        t = z
    graph = ";".join(filt) + ";" + "".join(segs) + \
            "concat=n=%d:v=1:a=0[cut];" % len(segs)
    print("%d segments, %d of them sped up" % (len(segs), len(fast)))

    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-ss", "%.2f" % ss, "-t", "%.2f" % dur, "-i", raw,
        "-filter_complex", graph + ("[cut]fps=%d,crop=%d:%d:%d:%d,"
                "scale=%d:%d:force_original_aspect_ratio=decrease:flags=lanczos,"
                "pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=0x%02x%02x%02x,format=yuv420p[out]"
                % (FPS, cw, ch, x0, y0, OW, OH, OW, OH, *PAPER)),
        "-map", "[out]",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
        "-preset", "slow", "-crf", "19",
        "-movflags", "+faststart", "-an", out,
    ], check=True)
    print(subprocess.run(["ffprobe", "-v", "error",
                          "-show_entries", "stream=width,height,r_frame_rate",
                          "-show_entries", "format=duration,size",
                          "-of", "default=nw=1", out],
                         capture_output=True, text=True).stdout.strip())


if __name__ == "__main__":
    import sys
    if "--recompose" in sys.argv:          # re-cut the last take, no browser
        take = json.load(open(TAKE))
        compose(take)
        rows = take["beats"]
    else:
        rows = film(wall_only="--wall-only" in sys.argv,
                    chorus="--chorus" in sys.argv)
    for row in rows:
        ok = "ok" if len(row["lit"]) == row["wanted"] else "MISMATCH"
        print("  %-8s %d/%d  %s" % (ok, len(row["lit"]), row["wanted"], row["q"]))
