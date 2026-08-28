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
    type therefore as large -- as it can be filmed and still be the wall. Every
    word in the film is the page's own, at about twice the size it is authored.

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
OW, OH = 1080, 1350             # 4:5, the shape a feed gives the most room to
FPS = 30
PAPER = (247, 245, 240)

OUT = "out/talk_to_a_brick_wall.mp4"
RAW = "out/talk_to_a_brick_wall.webm"
TAKE = "out/talk_to_a_brick_wall.json"   # crop, timings, and what each question lit

# (question, how many tiles it should reach). Short, and the sort of thing
# somebody actually types at a wall.
SCRIPT = [
    ("why are you blue?", 1, 0),
]

PERFORM_MS = 13000     # of the wall talking to itself before anybody types

TYPE_MS = 42
HOLD_OPEN = 1000       # on the bare wall before anything is typed
HOLD_READ = 700        # after each finished pass
HOLD_PAGE = 700        # after each answer paged to
HOLD_END = 1400        # on the last one

READ = ("() => [...document.querySelectorAll('.tile input[type=range]')]"
        ".map(r => r.value).join(',')")


def touch(pg):
    """Reset the page's idle timer so the wall does not interrupt the take."""
    pg.evaluate("dispatchEvent(new KeyboardEvent('keydown'))")


def wait_pass(pg, timeout=40.0):
    """Wait for exactly one sweep: out to the far end and back.

    The page no longer stops after a pass -- it loops until somebody touches
    something -- so waiting for the wall to go quiet waits for twelve of them.
    A pass is over when every slider is back on the value it was authored with,
    which is where the return leg puts it and where nothing else does.
    """
    ALL = "[...document.querySelectorAll('.tile input[type=range]')]"
    at_rest = "() => %s.every(r => r.value === r.defaultValue)" % ALL
    moved = "() => %s.some(r => r.value !== r.defaultValue)" % ALL
    pg.wait_for_function(moved, timeout=int(timeout * 1000))
    lit = pg.evaluate(
        "[...document.querySelectorAll('.tile.speaking')].map(t=>t.dataset.tile)")
    started = time.monotonic()
    pg.wait_for_function(at_rest, timeout=int(timeout * 1000))
    return lit, started


def film():
    """Roll on the wall talking to itself, then ask it two things.

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
                                    "--font-render-hinting=none"])
        ctx = b.new_context(viewport={"width": VW, "height": VH},
                            device_scale_factor=2,
                            record_video_dir=vdir,
                            record_video_size={"width": VW, "height": VH})
        pg = ctx.new_page()
        clock = time.monotonic()
        pg.goto(URL)
        pg.wait_for_timeout(1000)
        pg.evaluate("wall.stop()")
        print("fetching both models…")
        pg.click("#speak")
        pg.wait_for_function("() => !!window.wall._model", timeout=600000)
        # the 483 MB fetch fails about one attempt in two from a headless
        # browser, so it gets three
        for attempt in range(3):
            pg.click("#write")
            pg.wait_for_function(
                "() => !!window.wall._improvise || (document.getElementById('write')"
                " && document.getElementById('write').textContent === 'could not load')",
                timeout=1800000)
            if pg.evaluate("() => !!window.wall._improvise"):
                break
            print("  writer attempt %d failed, retrying" % (attempt + 1))
            pg.wait_for_timeout(2000)
        if not pg.evaluate("() => !!window.wall._improvise"):
            raise SystemExit("the writer did not load")
        print("both up")
        pg.evaluate("wall.stop(); wall.reset(); wall.say('')")
        pg.wait_for_timeout(500)

        bar = pg.locator(".bar").first.bounding_box()
        wall = pg.locator(".wall").first.bounding_box()
        crop = (int(bar["x"]) - 2, int(bar["y"]) - 6,
                int(bar["x"] + bar["width"]) + 2,
                int(wall["y"] + wall["height"]) + 4)

        start = time.monotonic() - clock
        print("rolling at +%.1f s, crop %s" % (start, crop))

        # the wall, uninvited
        pg.evaluate("() => { wall.perform(); }")
        pg.wait_for_timeout(PERFORM_MS)
        pg.evaluate("wall.stop()")
        pg.wait_for_timeout(500)

        for i, (q, want, pages) in enumerate(SCRIPT):
            touch(pg)
            pg.click("#q")
            pg.fill("#q", "")
            pg.type("#q", q, delay=TYPE_MS)
            t_ask = time.monotonic() - clock
            pg.keyboard.press("Enter")
            lit, t_lit = wait_pass(pg)
            pg.wait_for_timeout(HOLD_READ)
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
    compose(take)
    return beats


def compose(take, raw=RAW):
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
    # nothing is faked, but those stretches run at 8x, because a minute of a
    # tile going out and back says the same thing as five seconds of it. The
    # typing, the sentence landing, and the wall's own performance stay at 1x.
    fast = [(b["ask"] + 1.6, b["answer"] - 0.8) for b in beats
            if b["answer"] - b["ask"] > 4.4]
    segs, filt, k, t = [], [], 0, 0.0
    for a, z in fast + [(dur, dur)]:
        for lo, hi, rate in ((t, a, 1.0), (a, z, 8.0)):
            if hi - lo <= 0.04:
                continue
            filt.append("[0:v]trim=%.3f:%.3f,setpts=(PTS-STARTPTS)/%.1f[v%d]"
                        % (lo, hi, rate, k))
            segs.append("[v%d]" % k); k += 1
        t = z
    graph = ";".join(filt) + ";" + "".join(segs) + \
            "concat=n=%d:v=1:a=0[cut];" % len(segs)
    print("%d segments, %d of them at 8x" % (len(segs), len(fast)))

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
        "-movflags", "+faststart", "-an", OUT,
    ], check=True)
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
