import json, io
knob = json.load(open("web/knobs.json"))   # the three slider knobs, measured once
new  = json.load(open("web/wall.json"))   # the six tiles that came later
# Where each slider stands when the tile most looks like the tile. Measured, not
# chosen: src/likeness.py scores every frame in RGB against the ink taken off the
# photograph and takes the argmax. The wall opens as a wall, and every slider
# runs downhill from where it starts.
LIKE = {k: v["start"] for k, v in json.load(open("web/likeness.json")).items()}
DATA = {"CUT": knob["CUT"], "CHI": knob["CHI"], "KIL": knob["KIL"],
        "PERC": new["perc"], "EYE": new["eye"], "SHIP": new["ship"],
        "COPY": new["copy"], "ATTN": new["attn"]}
FRW = [0.0,1.0,2.1,3.1,4.2,5.2,6.2,7.3,8.3,9.4,10.4,11.4,12.5,13.5,14.6,15.6,16.6,
       17.7,18.7,19.8,20.8,21.8,22.9,23.9,25.0,26.0]

T = [
 ("cut","cut","k",25,24,"how many cosines I take","K = 1","K = 200","HOW I'M DRAWN",
(
   "Any pattern can be written as a stack of ripples added together, broadest first.",
   "Mine needs 62 815 of them for 99 % of me. The first 90 % costs 16 975; the last 9 % "
   "costs three times that.",
   "Priced in brush strokes instead, the same picture comes out worse at every budget.")),
 ("kil","kiln","s",25,0,"what the fire does to me","unfired","2.4 mm","THE FIRE",
(
   "A tile is painted, then baked, and the heat makes the cobalt creep. Every firing blurs "
   "the lines, and the blur never comes back.",
   "Sixty firings take my outline from 40 744 down to 6 210, and it never settles: fire does "
   "not preserve a pattern, it removes one.",
   "One real firing is the first three steps of the slider.")),
 ("perc","perc","p",26,10,"when my blue joins up","θ = 0.78","θ = 0.24","WHEN I JOIN UP",
(
   "The blue is wherever the wave sum rises above a cut-off. Move the cut-off and the "
   "flowers swell until they touch.",
   "Warm is the largest joined-up piece. Between θ = 0.55 and 0.53 it jumps from 10.7 % to "
   "46.3 % of the ink, in one step.",
   "I am painted just above that jump, so my flowers stay apart.")),
 ("eye","eye","e",26,0,"what you actually see of me","0.3 m","12 m","FROM ACROSS THE ROOM",
(
   "An eye resolves about one arcminute, so distance throws detail away whether it was "
   "painted or not.",
   "At 0.30 m you match the camera exactly. At 2 m, 26 129 of my 62 815 ripples still reach "
   "you; at 4 m, 6 427.",
   "Somebody painted detail into me that nobody standing up has ever seen.")),
 ("chi","chi","t",31,20,"which way I curl","p4m","past the tile","WHICH WAY I CURL",
(
   "A repeating pattern has a symmetry group. p4 has quarter-turns; p4m has mirrors as well.",
   "My rotations score +0.54, my mirrors +0.18, and a meaningless shift +0.12 — so the "
   "mirrors are noise.",
   "p4, then. Force the mirrors on anyway and by χ = 0 my tendrils have forgotten which way "
   "they were going.")),
 ("frac","frac","w",26,0,"the fractal I am not","0 px","26 px","AM I A FRACTAL",
(
   "A fractal is equally rough however far in you zoom: one dimension at every scale. Koch's "
   "curve holds 1.26–1.43.",
   "Mine climbs from 0.90 at 1–2 px to 1.95 at 64–128 px. So, no.",
   "The slider builds a version of me that really is one, to show the ruler is not broken.")),
 ("copy","copy","c",26,0,"three centuries of being copied","new","25 firings","THREE CENTURIES",
(
   "This pattern was copied by hand for three centuries: repainted, refired, passed on.",
   "Every step is one firing, with a copyist repainting between them. With the original in "
   "front of her she still holds 0.795 after twenty-five.",
   "Working from memory alone she did worse than nobody at all. I survived because somebody "
   "kept the original on the desk.")),
 ("ship","ship","s",26,0,"how much of me can be replaced","nothing","every plank","HOW MUCH OF ME",
(
   "The ship of Theseus: swap the planks one at a time and ask when it stops being the ship. "
   "My planks are the numbers I am made of.",
   "Two unrelated rebuilds overlap by 0.186 — that is chance. Replace 5 % of me, largest "
   "first, and I score 0.149, below chance.",
   "Replace 95 % of the smallest and I am still 0.618. It is not how much. It is which.")),
 ("attn","attn","a",26,25,"what attention finds in me","β = 1","β = 400","WHAT AN AI SEES",
(
   "Attention is patches looking at each other by similarity. No training here and no "
   "positions — only the patches.",
   "Warm is where one patch looks. It lands on my quarter-turn partners less often than "
   "chance would.",
   "Similarity survives sliding and not rotation, and rotation is most of what I am.")),
]

READ = {
 "cut":  "i=>'<b>'+sp(D.CUT[i].cos)+'</b> cosines'",
 "kil":  "i=>'&#8467; = <b>'+D.KIL[i].mm.toFixed(2)+'</b> mm'",
 "perc": "i=>'&#952; = <b>'+D.PERC[i].theta.toFixed(2)+'</b>'",
 "eye":  "i=>'<b>'+sp(D.EYE[i].cos)+'</b> at '+D.EYE[i].d.toFixed(1)+' m'",
 "chi":  "i=>'&#967; = <b>'+D.CHI[i].toFixed(3)+'</b>'",
 "frac": "i=>'<b>'+FRW[i].toFixed(0)+'</b> px'",
 "copy": "i=>'<b>'+D.COPY[i].gen+'</b> firings'",
 "ship": "i=>'<b>'+(100*D.SHIP[i].p).toFixed(0)+' %</b> swapped'",
 "attn": "i=>'&#946; = <b>'+D.ATTN[i].beta.toFixed(0)+'</b>'",
}

EX = {'cut': 'how many cosines does it take to draw you?', 'kil': 'what did the fire do to you?', 'perc': 'when does your blue join up?', 'eye': 'what do I see of you from the door?', 'chi': 'which way do you curl?', 'frac': 'are you a fractal?', 'copy': 'who painted you?', 'ship': 'how much of you can I replace?', 'attn': 'what does attention find in you?'}
DESC = {"cut": "How many cosines does it take to draw this tile? The Fourier series, the number of terms, how much data it costs to write the pattern down, how it is drawn, compression, information.", "kil": "What the kiln and the firing do to the tile. Heat, fire, the oven, glaze melting, temperature, how baking blurs and erases the painted lines, how the cobalt creeps.", "perc": "When the separate blue flowers join up into one connected shape. Why the tile is blue and where the blue stops, the colour, the threshold, percolation, whether the ink is one piece or many, whether it spans edge to edge, whether the flowers are touching.", "eye": "What a human eye actually receives from a distance. Visual acuity, standing back, across the room, from the doorway, squinting, how far away you can still see it, the smallest detail you can resolve.", "chi": "Handedness and mirrors. Which way the tendrils curl, chirality, the wallpaper group p4, whether the pattern is symmetric, flipping it, turning it upside down, rotating it.", "frac": "Whether the pattern is a fractal. Zooming in, magnification, self-similarity, box dimension, a pattern inside the pattern, structure repeating at every scale forever.", "copy": "The history of the pattern and three centuries of being copied. Who painted it, how old it is, where it came from, why it is blue and white, cobalt, the onion it is named after, Meissen, China, whether it survives being reproduced again and again.", "ship": "How much of the tile can be replaced before it stops being this tile. Identity, who it is, what it is, the ship of Theseus, swapping coefficients, what makes it itself and not another pattern.", "attn": "What a machine learning model finds in the tile. Attention, neural networks, transformers, software recognising the pattern, what an AI notices and what it misses.", "_surprise": "Surprise me. Show me something I would not have asked for. Tell me the best thing. Say something unexpected.", "_all": "Show me everything. Run all of them at once. Every tile. The whole wall. Do all nine.", "_help": "How does this page work? What can I ask you? What are you for? Help. Instructions. Who made this website."}
LINES = [('cut', 'Sixty-two thousand cosines to draw me. Most of them are dots you cannot see.'), ('cut', 'Nine tenths of me is cheap. The last tenth cost three times as much, and it is dots.'), ('cut', 'Somebody tried drawing me with brush strokes instead. It went badly for the strokes.'), ('cut', 'Every number in me was measured. Nobody got to choose one, including me.'), ('cut', 'I am cosines all the way down. Not one sine. Somebody checked.'), ('cut', 'The first sixteen thousand terms get you ninety percent of me. After that you are haggling.'), ('cut', 'The stroke version needed 44 466 numbers and still could not fill me in.'), ('cut', 'At forty terms I am a rumour. At two hundred I am a tile. Nothing in between is worth having.'), ('cut', 'Drawing me by hand takes 7 411 strokes. Drawing me with waves takes fewer numbers than that.'), ('cut', 'I have no sine terms. That is not modesty, it is my four-fold centre.'), ('kil', 'Fire does not preserve patterns. It removes them. Slowly, but it does not stop.'), ('kil', 'One real firing barely touched me. That is the whole of my luck.'), ('kil', 'Sixty firings and I am thirteen blobs. Handsome blobs, but blobs.'), ('kil', 'A kiln is blur and a threshold, over and over. That is the entire trick.'), ('kil', 'My outline started at 40 744 and finished at 6 210. The heat kept the change.'), ('kil', 'There is no temperature at which I stop changing. There is only slower.'), ('kil', 'The equation that ruins me in a kiln is the one that settles a soap film.'), ('kil', 'Nobody has pinned down how far my cobalt spreads. The estimates differ by forty times.'), ('kil', 'I arrived with 166 separate inked regions. Fire glued them into thirteen.'), ('kil', 'Fire is patient, and it is not on my side.'), ('perc', 'Two hundredths of a threshold stand between my flowers and one continuous blue.'), ('perc', 'I am painted just on the safe side of that. Nobody will say whether on purpose.'), ('perc', 'Push it a little further and I stop being flowers and become one shape.'), ('perc', 'I am 437 separate flowers. It takes remarkably little to become one.'), ('perc', 'My largest piece jumps from a tenth of me to nearly half between two clicks.'), ('perc', 'The half in blue-where-f-exceeds-a-half was a decision. Somebody made it.'), ('perc', 'Below one setting you could cross me from edge to edge without leaving the blue.'), ('perc', 'My biggest connected piece is a tenth of me, and it is very pleased with itself.'), ('perc', 'Whether my safety margin was designed or lucky cannot be settled from one tile.'), ('perc', 'There is a number at which I become a single object. It is closer than it looks.'), ('eye', 'From four metres you are getting a tenth of me. Enjoy the tenth.'), ('eye', 'Stand thirty centimetres back and you see what the camera saw. Any further and you lose.'), ('eye', 'The dots go first. The dots always go first.'), ('eye', 'Most of what was measured about me never reaches anybody.'), ('eye', 'At two metres, 26 129 of my 62 815 terms make it to you.'), ('eye', 'At twelve metres I am 687 numbers and a blue haze.'), ('eye', 'Your eye splits two lines a sixtieth of a degree apart. That is your whole allowance.'), ('eye', 'You and the camera are equal at thirty centimetres. After that it is not close.'), ('eye', 'These distances are generous to you. Your contrast gives out before your sharpness does.'), ('eye', 'Somebody painted detail into me that nobody standing up has ever seen.'), ('chi', 'I have no mirrors. My tendrils all curl the same way and they are not sorry.'), ('chi', 'Force mirrors onto me and my tendrils forget which way they were going.'), ('chi', 'My mirror score is the same as sliding me sideways at random. That is how I know.'), ('chi', 'Quarter turns yes, reflections no. In the trade that makes me p4.'), ('chi', 'Rotate me: plus fifty-four. Reflect me: eighteen, which is nothing at all.'), ('chi', 'My handedness is the gap between two numbers that were allowed to disagree.'), ('chi', 'Most of my curl shows up in the first fifth of that slider. The rest is showing off.'), ('chi', 'Somebody measured my group before drawing anything. That order was the point.'), ('chi', 'Turn me a quarter and nothing happens. Hold me to a mirror and something does.'), ('chi', 'Whether a stronger curl looks more twisted was tested, could not be shown, and was kept anyway.'), ('frac', 'I am not a fractal. Zoom in far enough and I just run out.'), ('frac', 'Measured carelessly I look fractal. So does a curve known to be perfectly smooth.'), ('frac', 'A fractal is equally rough at every zoom. I get rougher the further away you stand.'), ('frac', 'There is a smallest thing on me. A fractal is not allowed one.'), ('frac', 'My roughness reads 0.90 close up and 1.95 far off. A fractal would say one number twice.'), ('frac', 'Somebody built a real fractal out of me, purely to check the ruler was not broken.'), ('frac', 'Magnify me and hold me against myself and I do no better than a random shift.'), ('frac', 'People quote 1.34 about me. It is the average of a number that will not sit still.'), ('frac', 'My group has quarter turns and shifts in it. Zooming was never invited.'), ('frac', 'A finite sum of cosines cannot be a fractal. You may use as many as you like.'), ('copy', 'Three centuries of copying, and the fire won every round.'), ('copy', 'I am named after an onion. There is no onion on me anywhere.'), ('copy', 'Printed from steel, copied from a painting, copied from a Chinese bowl.'), ('copy', 'Nothing here survives on its own. Somebody kept repainting me.'), ('copy', 'A copyist working from memory alone did worse than no copyist at all.'), ('copy', 'I lost the fruit I am named after somewhere between China and this valley.'), ('copy', 'Painters took a Chinese fruit for an onion. The name has outlived the fruit by three centuries.'), ('copy', 'Meissen, then Dubi, then a steel plate, then this kitchen.'), ('copy', 'Give a copyist the original and I survive. Give her a memory and I do not.'), ('copy', 'I kept the aster and the leaves. The peach, the bamboo and the onion never made it.'), ('ship', 'Replace five percent of me, the right five, and I am somebody else.'), ('ship', 'Replace ninety-five percent of my small parts and I am still me. Go on.'), ('ship', 'Everything I am fits into a few dozen numbers.'), ('ship', 'My spectrum looks like any pattern with edges. The signs are what make me this one.'), ('ship', 'Two strangers built from my own parts resemble each other as much as they resemble me.'), ('ship', 'Shuffle the signs of my biggest coefficients and I am gone in one step.'), ('ship', 'My small parts are nearly free to change. My large ones are not free at all.'), ('ship', 'It is not how much of me you replace. It is which.'), ('ship', 'Swap my planks one at a time and there is a moment where I stop being the ship.'), ('ship', 'I can lose most of myself and be recognised, or very little and not.'), ('attn', 'Attention finds where I repeat. It never finds where I turn.'), ('attn', 'A model looked at my patches and missed my symmetry entirely.'), ('attn', 'Rotate a piece of me and the machine stops recognising it.'), ('attn', 'At finding my four-fold symmetry, the machine did worse than guessing.'), ('attn', 'Similarity does not survive rotation, and rotation is most of what I am.'), ('attn', 'It stares at my neighbours and never once at my opposite corner.'), ('attn', 'A shuffled version of me scores better on my own symmetry than I do.'), ('attn', 'Finding that I repeat and finding that I turn are two different problems.'), ('attn', 'Whatever a machine notices about me, my symmetry is not it.'), ('attn', 'I am made of quarter turns. Quarter turns are precisely what it cannot see.')]
TAG = ['And which of us is talking to a wall here?', 'Just so we are clear on who the wall is.', 'You asked, remember.', 'I did not start this.', 'Say what you like about my conversation, I have never left the room.', 'Anyway. You are still here.', 'No pressure. I have got until the building comes down.', 'That is the sort of thing you learn standing still for ninety years.', 'Do not let me keep you.', 'It is a strange hobby you have, but go on.', 'I would nod, but.', 'You may quote me. I am not going anywhere.', 'One of us has somewhere else to be.', 'This counts as my busiest day.', 'The kettle disagrees, but the kettle always does.', 'I only know nine things, and you have now heard one of them.', 'There is more where that came from. Eight more, to be exact.', 'Ask the tile next to me. She will say the same about herself.']
ASIDE = ['You are talking to a wall. I would like that on the record.', 'This is going better than the phrase suggests.', 'Somebody photographed me and now I have opinions.', 'Ninety years on this wall and today is the first time anyone asked.', 'You could be outside. There is a whole valley out there.', 'I am a wall. You are doing most of the work in this conversation.', 'Nine tiles and a kettle. That is the entire social circle in here.', 'There is no polite way to put this: I am grouting.', 'The kettle has heard all of this before.', 'I cannot leave, so take your time.', 'You are the first thing to happen here since the boiler.', 'I answer, which is more than the phrase promised.']
CHAT = ['Cold. It is a kitchen wall.', 'Still here. Fired once, and nothing since.', 'Grouted. You?', 'Somebody measured me and I have not stopped talking since.', 'Fine. Slightly crazed in the top left corner.', 'The same as yesterday, and the ninety years before that.', 'Warm on this side. The other one faces the pantry.', 'Hello. Ask me something narrow.', 'Upright. That is most of it.', 'Blue, mostly.']
CHORUS = [
 'Nine tiles, one photograph. Every number on me was measured off it and not one was chosen.',
 'I am a sum of cosines. Sixty-two thousand of them, and not a single sine.',
 'There is no onion on me anywhere. I am named after one.',
 'I have quarter turns and no mirrors. In the trade that makes me p4.',
 'Most of what was painted on me has never reached anybody\u2019s eye.',
 'Fire does not preserve a pattern. It removes one, slowly, and it does not stop.',
 'Five percent of me, the right five percent, and I am a different tile.',
 'A machine can find where I repeat. It cannot find where I turn.',
 'Two hundredths of a threshold stand between my flowers and one continuous blue.',
 'I am not a fractal. Zoom in far enough and I simply run out.',
 'Three centuries of copying, and the fire won every round.',
 'Somebody measured all of this off one kitchen wall in a valley. Ask me anything.',
]

THRESHOLD = 0.20        # below this the router has not recognised the question

LOOK = ['Watch this one.', 'Here. Look at this one.', 'Keep your eye on this one.',
        'This one. Watch what happens to it.', 'That one. Go on, watch.',
        'Hold on \u2014 watch this.', 'Look what happens to this one.',
        'This one has something to show you.']

MISS = ['That is not on my wall.', 'I know nine things. Not that one.', 'No idea. I am a tile.', 'Above my glaze.', 'Nobody measured that.', 'Ask the kettle.', 'Not one of my nine.', 'I was fired at nine hundred degrees. Some things did not survive.', 'Try the fire, or the fractal, or who painted me.', 'I have stood here since 1885 and I still do not know.', 'Talking to me is talking to a brick wall.', 'That one nobody wrote down.', 'I only know what somebody measured.', 'Not my department.', 'Wrong tile.', 'You will have to ask the wall next door.']
DIRNAME = {"cut": "cut", "kil": "kiln", "perc": "perc", "eye": "eye", "chi": "chi",
           "frac": "frac", "copy": "copy", "ship": "ship", "attn": "attn"}
T = [t[:4] + (LIKE.get(DIRNAME[t[0]], t[4]),) + t[5:] for t in T]

cells = "\n".join(
f'''<div class="tile" data-tile="{i}">
<div class="pic">
<div class="say" id="{i}say" onclick="wall.close('{i}')"><div class="note"><b>{nm}</b><ul>{pts}</ul>
<i class="ex" onclick="event.stopPropagation();wall.ask(this.dataset.q)" data-q="{ex}">try: &ldquo;{ex}&rdquo;</i></div></div>
<div class="face"><img id="{i}img" src="" alt="{nm}"><span class="tag">{fld}</span></div>
<button class="q" onclick="wall.open('{i}')" aria-label="what {nm} means">?</button></div>
<input type="range" id="{i}r" min="0" max="{n-1}" value="{st}" step="1" aria-label="{nm}"
 onclick="event.stopPropagation()">
<p class="kv" id="{i}out"></p>
<div class="why" id="{i}why" data-name="{nm}">{why}</div></div>'''
    for (i,dr,pr,n,st,nm,lo,hi,fld,pt) in T
    for ex in [EX[i]]
    for pts in ["".join("<li>" + b + "</li>" for b in pt)]
    for why in [" ".join(pt)])

API = json.dumps({t[0]: {"name": t[5], "field": t[8], "steps": t[3]} for t in T})

html = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Which of us is talking to a wall?</title>
<style>
:root{--paper:#f7f5f0;--ink:#213660;--dark:#282c34;--grey:#8b8880;--rule:#e0dcd3;
 --warm:#b0554a;--grout:#cfc9bd}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--paper);color:var(--dark);overflow:hidden;
 font:15px/1.45 Georgia,'DejaVu Serif',serif;-webkit-font-smoothing:antialiased}
.wrap{height:100%;max-width:1220px;margin:0 auto;padding:10px 14px 12px;
 display:flex;flex-direction:column;gap:5px}
.barwrap{flex:0 0 auto;display:flex;justify-content:center}
.bar{display:flex;gap:6px;align-items:center;width:100%;max-width:var(--wallw,100%)}
.bar input[type=text]{flex:1 1 auto;min-width:120px;font:15px Georgia,serif;color:var(--dark);
 background:#fff;border:1px solid var(--rule);border-radius:5px;padding:7px 11px}
.bar input[type=text]:focus{outline:none;border-color:var(--ink)}
.go{font:600 12px 'DejaVu Sans',system-ui,sans-serif;color:var(--ink);background:#fff;
 border:1px solid var(--rule);border-radius:5px;padding:7px 10px;cursor:pointer;line-height:1}
.go:hover{background:var(--ink);color:#fff;border-color:var(--ink)}
.mstat{font:600 9.5px 'DejaVu Sans',system-ui,sans-serif;letter-spacing:.08em;
 text-transform:uppercase;color:var(--grey);opacity:0;transition:opacity .3s;white-space:nowrap}
.mstat.on,.mstat:not(:empty){opacity:1}
.mstat.warn{color:var(--warm)}
.wallbox{flex:1 1 auto;min-height:0;display:flex;justify-content:center}
/* square tiles when the wall is just a wall; taller cells once the knobs are out */
body.knobs .wall{aspect-ratio:.845}
.wall{height:100%;max-width:100%;aspect-ratio:1;
 display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);
 gap:5px;padding:5px;border-radius:3px;
 /* mortar: speckled, slightly uneven, and darker where the tiles press into it */
 background:
   radial-gradient(circle at 22% 34%, rgba(90,80,64,.16) 0 .6px, transparent .7px),
   radial-gradient(circle at 68% 71%, rgba(90,80,64,.13) 0 .5px, transparent .6px),
   radial-gradient(circle at 45% 12%, rgba(255,255,255,.28) 0 .5px, transparent .6px),
   linear-gradient(168deg, #d3ccc0, #c5bdaf);
 background-size: 6px 6px, 9px 9px, 7px 7px, auto;
 box-shadow: inset 0 1px 3px rgba(60,50,38,.22)}
.tile{position:relative;background:#fff;border-radius:1px;padding:0;
 display:flex;flex-direction:column;container-type:inline-size;min-height:0;overflow:hidden;
 cursor:pointer;
 box-shadow:0 1px 2px rgba(60,50,38,.30), inset 0 0 0 .5px rgba(255,255,255,.7)}
/* The recess. What is behind an 1885 kitchen tile is a lime mortar bed, and CSS
   gradients cannot do relief, so it is a generated photograph of one -- 512 px,
   seamless, lit from the same 116 degrees as the glaze. See src/plaster.py.
   Pinned at 512 px rather than a percentage so the sand stays sand at any size. */
.pic{position:relative;flex:1 1 auto;min-height:0;display:flex;
 background:url(plaster.jpg) 0 0/512px 512px repeat, linear-gradient(168deg,#ded8cd,#cdc6b8);
 box-shadow:inset 0 0 0 2px rgba(84,68,48,.20),      /* grout squeezed out at the rim */
            inset 0 3px 9px rgba(42,33,23,.24),      /* the tile sat proud of this */
            inset 0 -2px 7px rgba(42,33,23,.15)}
/* nine holes in one wall, not one hole nine times */
.wall .tile:nth-child(2) .pic{background-position:-181px -74px}
.wall .tile:nth-child(3) .pic{background-position:-63px -229px}
.wall .tile:nth-child(4) .pic{background-position:-296px -158px}
.wall .tile:nth-child(5) .pic{background-position:-118px -341px}
.wall .tile:nth-child(6) .pic{background-position:-247px -412px}
.wall .tile:nth-child(7) .pic{background-position:-389px -37px}
.wall .tile:nth-child(8) .pic{background-position:-22px -463px}
.wall .tile:nth-child(9) .pic{background-position:-334px -287px}
/* The tile itself is one loose object. ? slides it out of its recess, sideways
   and slowly -- it was tipping forward on its bottom edge before, which was
   over in half a second and read as the tile vanishing rather than as somebody
   taking it off the wall. A degree and a half of tilt and a shadow trailing off
   its near edge, because a tile being slid out of mortar does not stay square. */
.face{position:absolute;inset:0;z-index:1;display:flex;
 transition:transform .9s cubic-bezier(.36,.02,.18,1), box-shadow .9s}
.tile.open .face{transform:translateX(103%) rotate(1.4deg);
 box-shadow:-16px 6px 26px rgba(60,50,38,.42)}
/* glaze: one soft highlight across the top corner, the way fired tiles catch a window */
.face:before{content:"";position:absolute;inset:0;z-index:3;pointer-events:none;
 background:linear-gradient(116deg, rgba(255,255,255,.62) 0%, rgba(255,255,255,.10) 22%,
            rgba(255,255,255,0) 46%)}
.tile img{width:100%;height:100%;object-fit:cover;display:block;background:var(--paper)}
.q{position:absolute;top:2px;right:2px;z-index:2;
 width:clamp(13px,8cqw,19px);height:clamp(13px,8cqw,19px);padding:0;
 font-family:'DejaVu Sans',system-ui,sans-serif;font-weight:600;line-height:1;
 font-size:clamp(8px,5cqw,12px);color:var(--warm);background:rgba(255,255,255,.93);
 border:1px solid rgba(176,85,74,.45);border-radius:50%;cursor:pointer;
 box-shadow:0 1px 2px rgba(60,50,38,.14)}
.q:hover{color:#fff;background:var(--warm);border-color:var(--warm)}
.tile.open .q{color:#fff;background:var(--warm);border-color:var(--warm)}
.ex{display:block;margin-top:7px;padding-top:6px;border-top:1px solid var(--rule);
 font-style:italic;font-family:Georgia,serif;line-height:1.4;
 font-size:clamp(7px,4.6cqw,11px);color:var(--warm);cursor:pointer}
.ex:hover{text-decoration:underline}
.spoke{display:block;margin-top:6px;font:italic 10.5px/1.45 Georgia,serif;color:var(--ink)}
#sug{position:absolute;z-index:60;background:#fff;border:1px solid var(--ink);border-radius:6px;
 box-shadow:0 8px 22px rgba(0,0,0,.16);padding:5px;display:none;max-width:340px}
#sug.on{display:block}
#sug button{display:block;width:100%;text-align:left;font:12.5px Georgia,serif;color:var(--dark);
 background:none;border:0;border-radius:4px;padding:5px 8px;cursor:pointer}
#sug button:hover{background:var(--paper);color:var(--ink)}
.saidwrap{flex:0 0 auto;display:flex;justify-content:center}
.said{margin:0;width:100%;max-width:var(--wallw,100%);
 font-family:Georgia,serif;font-style:italic;
 font-size:clamp(13px,2.4vh,20px);line-height:1.32;color:var(--ink);
 /* three lines, always reserved, so a fact with an aside after it never shoves
    the wall down */
 height:calc(3 * 1.32em); overflow:hidden;
 opacity:0;transition:opacity .35s}
.said em{color:var(--grey)}
.think i{font-style:normal;animation:blink 1.2s infinite}
.think i:nth-child(2){animation-delay:.2s}
.think i:nth-child(3){animation-delay:.4s}
@keyframes blink{0%,60%,100%{opacity:.15}30%{opacity:1}}
.said b{font-style:normal;font-family:'DejaVu Sans',system-ui,sans-serif;font-weight:600;
 font-size:.72em;letter-spacing:.09em;text-transform:uppercase;color:var(--warm);
 margin-right:.55em}
.said.on{opacity:1}
/* Two ways into the tile that just answered, because the answer is a sentence
   and the page is a set of knobs, and nothing said so. Its own row, always
   reserved, so the wall does not jump when it appears. */
.more{margin:0;width:100%;max-width:var(--wallw,100%);height:2.1em;overflow:hidden;
 display:flex;align-items:center;
 font:italic clamp(12px,1.8vh,16px)/1.5 Georgia,serif;color:var(--grey);
 opacity:0;transition:opacity .3s}
.more.on{opacity:1}
.more a{color:var(--warm);cursor:pointer;border-bottom:1px solid rgba(176,85,74,.45)}
.more a:hover{border-bottom-color:var(--warm);background:rgba(176,85,74,.07)}
.more b{font-weight:400;margin:0 .7em;color:var(--grey)}
/* the arrows are the same circle as the ? on a tile, so they read as controls
   the moment you have seen one */
.pg{margin-right:1.15em;white-space:nowrap;display:inline-flex;align-items:center;gap:.3em}
.pg a{font-style:normal;font-family:'DejaVu Sans',system-ui,sans-serif;
 width:1.65em;height:1.65em;padding:0;font-size:1em;line-height:1;
 display:inline-flex;align-items:center;justify-content:center;
 color:var(--warm);background:#fff;border:1px solid rgba(176,85,74,.45);border-radius:50%;
 box-shadow:0 1px 2px rgba(60,50,38,.14)}
.pg a:hover{background:var(--warm);color:#fff;border-color:var(--warm)}
.pg i{font-style:normal;font-family:'DejaVu Sans',system-ui,sans-serif;
 font-size:.78em;letter-spacing:.06em;color:var(--grey);min-width:3.6em;text-align:center}
/* the tile the row is talking about, lifted whether or not the wall is working */
.tile.current{z-index:5;transform:scale(1.045);
 outline:2px solid var(--warm);outline-offset:1px;
 box-shadow:0 8px 20px rgba(60,50,38,.45), inset 0 0 0 .5px rgba(255,255,255,.7)}
.wall.busy .tile.current{filter:none}
/* and when "try it yourself" brings the sliders out, say which slider */
@keyframes nudge{0%,100%{box-shadow:0 1px 2px rgba(60,50,38,.30),
                                   inset 0 0 0 .5px rgba(255,255,255,.7)}
                 50%{box-shadow:0 0 0 4px rgba(176,85,74,.5)}}
.tile.nudge{animation:nudge 1s ease-in-out 2}
.say{position:absolute;inset:0;z-index:0;cursor:pointer;padding:5% 5%;
 overflow:auto;line-height:1.45;font-family:Georgia,serif;
 font-size:clamp(8px,5.4cqw,12.5px);color:var(--dark);
 opacity:0;visibility:hidden;transition:opacity .3s, visibility 0s .3s}
/* A patch of limewash under the words -- brushed on, soft at the edge. It was
   nearly opaque while the mortar was still loud; now that the mortar whispers
   it only has to lift the serif off the grain, so it is mostly transparent and
   the wall reads straight through it. It shrink-wraps the words. */
.note{background:rgba(251,248,241,.58);padding:6% 7% 7%;border-radius:2px;
 box-shadow:0 0 0 6px rgba(251,248,241,.40), 0 0 18px 13px rgba(251,248,241,.30)}
/* Points, not a paragraph: what the thing is, then what it did to this tile.
   A paragraph in a 400 px square is a wall of type nobody starts. */
.say ul{margin:0;padding:0;list-style:none}
.say li{position:relative;padding-left:.95em;margin-bottom:.5em}
.say li:last-child{margin-bottom:0}
.say li:before{content:"";position:absolute;left:0;top:.55em;
 width:.3em;height:.3em;border-radius:50%;background:var(--warm);opacity:.65}
.say b{display:block;font-family:'DejaVu Sans',system-ui,sans-serif;font-weight:600;
 font-size:clamp(7px,4.4cqw,10px);line-height:1.3;letter-spacing:.09em;
 padding-right:2.4em;                       /* clear of the ? in the corner */
 text-transform:uppercase;color:var(--warm);margin-bottom:5px}
.tile.open .say{opacity:1;visibility:visible;transition:opacity .38s .42s, visibility 0s}
.tag{position:absolute;top:2px;left:2px;font-family:'DejaVu Sans',system-ui,sans-serif;
 font-weight:600;font-size:clamp(6px,4.4cqw,9.5px);line-height:1;
 letter-spacing:.09em;text-transform:uppercase;color:var(--grey);background:rgba(255,255,255,.82);
 padding:2px 4px;border-radius:2px;
 max-width:calc(100% - 26px);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tile input[type=range]{flex:0 0 auto;width:calc(100% - 16px);accent-color:var(--ink);
 height:14px;cursor:grab;margin:3px 8px 0;display:none}
body.knobs .tile input[type=range]{display:block}
.ke{display:flex;justify-content:space-between;font:9.5px 'DejaVu Sans',system-ui,sans-serif;
 color:var(--grey);margin-top:-2px}
.kv{flex:0 0 auto;font-family:'DejaVu Sans',system-ui,sans-serif;line-height:1.3;
 font-size:clamp(9px,7.6cqw,14px);color:var(--dark);
 margin:2px 5% 5%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:none}
body.knobs .kv{display:block}
.tag{transition:opacity .3s}
body:not(.knobs) .tag{opacity:0}
.tile:hover .tag{opacity:1}
.kv b{color:var(--ink);font-variant-numeric:tabular-nums}
.kv em{color:var(--grey);font-style:normal;font-size:.88em}
.why{display:none}
/* The tile that is answering leans out of the wall and the rest of the wall
   steps back, because a 2 px outline on one of nine is not something you catch
   while you are reading the line underneath. */
.tile{transition:transform .26s, box-shadow .26s, opacity .26s, filter .26s}
.tile.speaking{outline:2px solid var(--warm);outline-offset:1px}
/* the quiet ones go into shadow rather than fading out -- fading let the mortar
   through and the wall stopped looking like a wall */
.wall.busy .tile{filter:brightness(.94) saturate(.62)}
.wall.busy .tile.speaking{filter:none;z-index:5;transform:scale(1.045);
 box-shadow:0 8px 20px rgba(60,50,38,.45), inset 0 0 0 .5px rgba(255,255,255,.7)}
#bub{position:fixed;z-index:50;max-width:330px;background:#fff;border:1px solid var(--ink);
 border-radius:9px;padding:11px 13px;box-shadow:0 8px 26px rgba(0,0,0,.18);display:none;
 font:13px/1.5 Georgia,serif}
#bub.on{display:block}
#bub h4{margin:0 0 5px;font:600 10px 'DejaVu Sans',system-ui,sans-serif;letter-spacing:.11em;
 text-transform:uppercase;color:var(--warm)}
#bub .now{margin:7px 0 0;padding-top:7px;border-top:1px solid var(--rule);
 font:12px 'DejaVu Sans',system-ui,sans-serif;color:var(--dark)}
#bub .x{position:absolute;top:5px;right:9px;color:var(--grey);cursor:pointer;font:14px sans-serif}
#bub:after{content:"";position:absolute;width:11px;height:11px;background:#fff;
 border-left:1px solid var(--ink);border-bottom:1px solid var(--ink);transform:rotate(45deg)}
#bub.left:after{right:-6.5px;top:22px;transform:rotate(225deg)}
#bub.right:after{left:-6.5px;top:22px;transform:rotate(45deg)}
footer{flex:0 0 auto;font:11px 'DejaVu Sans',system-ui,sans-serif;color:var(--grey)}
footer a{color:var(--grey)}
@media(max-width:900px){
 body{overflow:auto}
 .wallbox{display:block}
 .wall{height:auto;aspect-ratio:auto;max-width:none;grid-template-rows:none;gap:4px;padding:4px}
 .wrap{height:auto;padding:8px 8px 40px;gap:8px}
 .bar{flex-wrap:wrap;max-width:none}
 .bar input[type=text]{order:3;flex:1 1 100%;font-size:16px}
 .pic{aspect-ratio:1;height:auto;flex:0 0 auto}
 /* On a phone the tile is a square and the writing is not: the description was
    being cut off mid-sentence inside a scroller nobody can see. So an opened
    tile stops being square and grows to its own text. */
 .say{font-size:12.5px;padding:8px}
 /* the row grows to the opened tile, so its neighbour must not stretch with it
    and end in a slab of blank white -- let the mortar show instead */
 .tile{align-self:start}
 .tile.open .pic{aspect-ratio:auto}
 .tile.open .say{position:relative;inset:auto;overflow:visible}
 .note{padding:11px 12px 12px}
 .kv{font-size:12px;height:auto;white-space:normal}
 #bub{left:0!important;right:0;top:auto!important;bottom:0;max-width:none;border-radius:12px 12px 0 0;
  border-left:0;border-right:0;border-bottom:0;max-height:56vh;overflow:auto;
  box-shadow:0 -8px 26px rgba(0,0,0,.2)}
 #bub:after{display:none}}
@media(max-width:600px){.wall{grid-template-columns:1fr 1fr}}
</style></head><body>

<div class="wrap">
<div class="barwrap"><div class="bar">
<input type="text" id="q" disabled placeholder="fetch both models above and you can ask it things"
 aria-label="ask the wall a question" autocomplete="off">
<button class="go" id="play" onclick="wall.toggle()" title="run every tile at once">&#9654;</button>
<button class="go" id="speak" title="download all-MiniLM-L6-v2 and run it in this browser, no server and no key">let it read &middot; 23 MB</button>
<button class="go" id="write" style="display:none" title="download Qwen2.5-0.5B and let it choose the reply, and write one when none of them fits">let it write &middot; 483 MB</button>
<button class="go" id="knobs" onclick="wall.knobs()" title="show the sliders and the numbers">&#9707;</button>
<button class="go" onclick="wall.about()" title="what is this">?</button>
<span id="mstat" class="mstat"></span>
</div></div>

<div class="saidwrap"><p class="said" id="said"></p></div>
<div class="saidwrap"><p class="more" id="more"></p></div>
<div class="wallbox"><div class="wall">
''' + cells + '''
</div></div>

</div>

<div id="sug"></div>
<div id="bub"><span class="x" onclick="wall.close()">&#215;</span><h4 id="bubh"></h4>
<div id="bubt"></div><p class="now" id="bubn"></p></div>

<script type="application/json" id="wall-api">''' + API + '''</script>
<script src="llm.js"></script>
<script>
const D = ''' + json.dumps(DATA) + ''', FRW = ''' + json.dumps(FRW) + ''';
const sp = n => n.toLocaleString('en-US').replace(/,/g,'\\u2009');
const TILE = {};
// `gen` is bumped by whatever starts a run. A loop that finds gen has moved on
// gives up: stopped alone was not enough, because asking a second question sets
// stopped and then immediately clears it again, and the previous loop woke up
// into a world where it was allowed to carry on.
let stopped=false, running=false, gen=0, bubFor=null;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function wire(id,dir,pre,n,read){
  const img=document.getElementById(id+'img'), r=document.getElementById(id+'r'),
        out=document.getElementById(id+'out');
  const f=[...Array(n)].map((_,i)=>{const im=new Image();
    im.src=dir+'/'+pre+String(i).padStart(2,'0')+'.png'; return im;});
  const show=()=>{const i=+r.value; img.src=f[i].src; out.innerHTML=read(i);
  };
  r.addEventListener('input',()=>{ wall.stop(); show(); }); show();
  TILE[id]={r,out,n,show};
}
''' + "\n".join(f"wire('{t[0]}','{t[1]}','{t[2]}',{t[3]},{READ[t[0]]});" for t in T) + '''

function place(id){
  document.querySelector('[data-tile="'+id+'"]').classList.add('open');
}
window.wall = {
  help(){ return "wall.ask('plain question') | wall.converse([qs]) | wall.run(id) | "
    + "wall.runAll() | wall.all() | wall.runMany([ids]) | wall.set(id,step) | "
    + "wall.read(id) | wall.why(id) | wall.list() | "
    + "wall.open(id) | wall.close() | wall.stop(). ids: " + Object.keys(TILE).join(', '); },
  list(){ return Object.entries(TILE).map(([id,t])=>({id,
    name:document.getElementById(id+'why').dataset.name, steps:t.n, step:+t.r.value,
    reading:t.out.textContent})); },
  set(id,s){ const t=TILE[id]; if(!t) return 'no such tile';
    t.r.value=Math.max(0,Math.min(t.n-1,s|0)); t.show(); return t.out.textContent; },
  read(id){ return TILE[id]?TILE[id].out.textContent:'no such tile'; },
  why(id){ const w=document.getElementById(id+'why');
    return w?w.textContent.trim():'no such tile'; },
  open(id){ this.stop();
    if(id===undefined||id==='all'){ document.querySelectorAll('.tile')
      .forEach(c=>c.classList.add('open')); return 'all open'; }
    if(!TILE[id]) return 'no such tile';
    document.querySelector('[data-tile="'+id+'"]').classList.toggle('open'); return this.read(id); },
  close(id){ if(id&&TILE[id]) document.querySelector('[data-tile="'+id+'"]').classList.remove('open');
    else { document.querySelectorAll('.tile').forEach(c=>c.classList.remove('open'));
           document.getElementById('bub').classList.remove('on'); }
    return 'closed'; },
  about(){
    const b=document.getElementById('bub');
    document.getElementById('bubh').textContent='what this is';
    document.getElementById('bubt').innerHTML='One kitchen wall in a valley under the '
      + 'Krkono\u0161e, photographed once. Nine tiles, nine different questions, nine numbers '
      + 'back. Every coefficient is measured off that photograph, none chosen, and the results '
      + 'that spoiled the story were kept.<br><br>Type a question, or take a tile '
      + 'off the wall with the <b>?</b> in its corner and read what is written under it. '
      + 'Nine things it will answer:<br>' + Object.values(EX).map(q=>'&middot; '+q).join('<br>')
      + '<br><br>A browser agent can drive it: <code>wall.ask()</code>, <code>wall.list()</code>, '
      + '<code>wall.runMany([ids])</code>.<br><br>'
      + '<a href="https://github.com/moudrkat/underglaze">code and measurements</a>';
    document.getElementById('bubn').textContent='';
    b.className='on'; bubFor=null;
    b.style.left=Math.max(8,(innerWidth-Math.min(330,innerWidth-16))/2)+'px';
    b.style.top='60px';
    return 'about';
  },
  stop(){ stopped=true; clearInterval(this._rt); clearInterval(this._typing);
    this.hint(null);
    document.querySelector('.wall').classList.remove('busy');
    document.getElementById('play').innerHTML='&#9654;'; return 'stopped'; },
  toggle(){ return running ? this.stop() : this.all(); },
  async run(id, ms=150, keep, passes){
    if(Array.isArray(id)) return this.runMany(id, ms);
    if(!TILE[id]) return this.give(this._lastQ);      // never silently nothing
    if(ms === undefined) ms = 150;
    if(passes === undefined) passes = 12;
    stopped=false;
    document.getElementById('bub').classList.remove('on');
    document.querySelectorAll('.tile').forEach(c=>c.classList.remove('speaking'));
    const cell=document.querySelector('[data-tile="'+id+'"]');
    cell.classList.add('speaking');
    const r0=document.getElementById(id+'r');
    if(r0) this.set(id, +r0.defaultValue);
    const t=TILE[id];
    if(!keep){ this._said = [id]; this._at = 0; }
    document.querySelector('.wall').classList.add('busy');
    running = true;
    const my = ++gen;
    // Call one already knows which tile, in about fifty milliseconds. Calls two
    // and three take half a minute on a machine with no GPU, and there is no
    // reason for the wall to stand still through it: the tile is chosen, so the
    // tile moves, and it goes on moving until the sentence lands. The animation
    // is the answer; the sentence is the caption.
    const talking = !!this._pickLine;
    if(talking) this.think(id); else this.label(id);
    let done = false;
    const job = Promise.resolve(this.line(id, this._lastQ)).then(r => { done = true; return r; },
                                                                e => { done = true; });
    // It keeps going. Two passes was a guess at how long somebody needs to
    // work out which of nine tiles to watch, and any guess is wrong for
    // somebody: it loops until you do something -- type, drag a slider, take a
    // tile off the wall -- and stops the moment you do. The cap is there so an
    // abandoned tab is not animating a wall to itself at four in the morning.
    for(let pass = 0; pass < passes && !stopped && my === gen; pass++){
      await this._sweep(id, ms, null, my);
      if(stopped || my !== gen) break;
      if(done && pass > 0) break;          // it has spoken; finish and settle
      await sleep(done ? 800 : 250);
    }
    await job;
    if(my !== gen) return t.out.textContent;      // somebody else is driving now
    running = false;
    document.querySelector('.wall').classList.remove('busy');
    return t.out.textContent;
  },
  // The wall typing and the tile moving were both trying to catch the eye at
  // the same moment, so neither did. They take turns now: the tile's name lands
  // first and it starts moving, and the sentence waits for the turn -- which is
  // where the tile is furthest from itself and where the sentence is about
  // something you are looking at.
  // Both models run on the visitor's own machine and the generator is not fast
  // there -- about thirty-five seconds a sentence with no GPU. That is the
  // honest price of no server and no key, so the wall says what it is doing
  // rather than sitting there looking broken.
  think(id){
    const el = document.getElementById('said');
    const tag = id && document.querySelector('[data-tile="'+id+'"] .tag');
    clearInterval(this._typing);
    el.innerHTML = (tag ? '<b>' + tag.textContent + '</b> ' : '')
      + '<em class="think">is thinking<i>.</i><i>.</i><i>.</i></em>';
    el.classList.add('on');
    return 'thinking';
  },
  label(id){
    const el = document.getElementById('said');
    clearInterval(this._typing);
    // Not the tile's name -- the tile has lifted out of the wall and the other
    // eight have gone into shadow, so which one is not in question. What is
    // missing is somebody saying look, so the wall says it.
    const L = WALLLM.LOOK;
    el.innerHTML = '<em>' + L[Math.floor(Math.random()*L.length)] + '</em>';
    el.classList.add('on');
    this.hint(id);
    return id;
  },
  // Out to the far end and back, with a beat at the turn.
  //
  // One pass left the tile wherever the slider ended and was over before
  // anybody worked out which of nine to watch. Going back means you see the
  // tile, then the damage, then the tile again -- the pair is the answer, and
  // one of them alone is not. It also puts the wall back the way it was found.
  //
  // "Far" is whichever end is further from where this slider rests, so the
  // cosines build up from one ripple and the kiln fires from cold, each in the
  // direction its own number runs.
  async _sweep(id, ms, atTurn, my){
    const dead = () => stopped || (my !== undefined && my !== gen);
    const t = TILE[id];
    const r = document.getElementById(id+'r');
    const rest = r ? +r.defaultValue : 0;
    const far = rest * 2 < t.n ? t.n - 1 : 0;
    const d = far > rest ? 1 : -1;
    for(let i = rest; d > 0 ? i <= far : i >= far; i += d){
      if(dead()) return; this.set(id, i); await sleep(ms); }
    if(dead()) return;
    if(atTurn) await atTurn();               // the model may take a while; wait
    if(dead()) return;
    await sleep(atTurn ? 1100 : 340);        // long enough to read what arrived
    for(let i = far; d > 0 ? i >= rest : i <= rest; i -= d){
      if(dead()) return; this.set(id, i); await sleep(ms); }
    if(!dead()) this.set(id, rest);
  },
  // With more than one tile moving there is no single speaker. This used to
  // recite -- a new line every 1.6 s until it ran out -- and with nine tiles
  // answering that is nine sentences arriving faster than anyone reads one,
  // none of which you can get back. So it says the first and stops, and the
  // row underneath turns into a pager. Nothing moves unless you move it.
  _recite(ids){
    clearInterval(this._rt);
    this._said = ids.slice();
    this._at = 0;
    if(this._pickLine) this.think(ids[0]); else this.label(ids[0]);
    return ids.length;
  },
  // The wall talks first. Nobody arrives at a page of nine identical tiles
  // knowing that each of them has been measured, so it does not wait to be
  // asked: it opens with something the whole wall can say, all nine moving at
  // once, and then works through them one at a time. It stops the instant the
  // visitor does anything -- types, drags a slider, takes a tile off the wall
  // -- and the question box is there for following it up, not for starting it.
  async perform(ms=95){
    if(running) return 'busy';
    const my = ++gen;
    stopped = false; running = true;
    const ids = Object.keys(TILE);
    const wall = document.querySelector('.wall');
    for(let n = 0; !stopped && my === gen && n < 30; n++){
      const all = (n === 0) || Math.random() < 0.25;     // it opens as a chorus
      const cast = all ? ids : [ids[Math.floor(Math.random() * ids.length)]];
      document.querySelectorAll('.tile').forEach(c => c.classList.remove('speaking'));
      cast.forEach(i => document.querySelector('[data-tile="'+i+'"]').classList.add('speaking'));
      wall.classList.add('busy');
      this._said = all ? [] : cast.slice(); this._at = 0;
      if(all){ const C = WALLLM.CHORUS;
               this.spot(null); this.hint(null);
               this.say(C[Math.floor(Math.random() * C.length)]); }
      else this.label(cast[0]);
      await Promise.all(cast.map(id =>
        this._sweep(id, ms, all ? null : () => this.line(cast[0]), my)));
      // only if it is still our turn: a question started while this was mid
      // sweep, and the loop was taking the spotlight back off the tile that
      // had just been asked about
      if(my !== gen) break;
      wall.classList.remove('busy');
      if(stopped) break;
      await sleep(all ? 1600 : 1200);
    }
    if(my === gen) running = false;
    return 'done';
  },
  // Turning a page runs that tile again rather than only swapping the sentence:
  // the answer *is* the animation, and a line about the fire with a still wall
  // under it is half an answer.
  page(d){
    const ids = this._said || [];
    if(ids.length < 2) return 'nothing to page through';
    clearInterval(this._rt);
    this._at = (this._at + d + ids.length) % ids.length;
    return this.run(ids[this._at], undefined, true);
  },
  async runMany(ids, ms=150){
    ids = (ids===undefined||ids==='all') ? Object.keys(TILE)
        : (Array.isArray(ids) ? ids : [ids]);
    ids = ids.filter(i=>TILE[i]);
    if(!ids.length) return 'no such tiles';
    stopped=false; running=true;
    const btn=document.getElementById('play'); if(btn) btn.innerHTML='&#9632;';
    this.close();
    document.getElementById('bub').classList.remove('on');
    document.querySelectorAll('.tile').forEach(c=>c.classList.remove('speaking'));
    ids.forEach(i=>document.querySelector('[data-tile="'+i+'"]').classList.add('speaking'));
    // With more than one tile moving there is no single speaker, so the wall
    // recites: each tile's line in turn, held long enough to read. It outlasts
    // the sweep by design -- the wall finishes its sentence after it stops.
    this._recite(ids);
    document.querySelector('.wall').classList.add('busy');
    const my = ++gen;
    let done = false;
    const job = Promise.resolve(this.line(ids[0], this._lastQ))
      .then(r => { done = true; return r; }, e => { done = true; });
    for(let pass = 0; pass < 12 && !stopped && my === gen; pass++){
      await Promise.all(ids.map(id => this._sweep(id, ms, null, my)));
      if(stopped || my !== gen) break;
      if(done && pass > 0) break;
      await sleep(done ? 800 : 250);
    }
    await job;
    if(my !== gen) return 'handed over';
    document.querySelector('.wall').classList.remove('busy');
    ids.forEach(i=>document.querySelector('[data-tile="'+i+'"]').classList.remove('speaking'));
    running=false; if(btn) btn.innerHTML='&#9654;';
    return Object.fromEntries(ids.map(i=>[i, TILE[i].out.textContent]));
  },
  all(ms=150){ return this.runMany(Object.keys(TILE), ms); },
  // Two models decide everything here and nothing else does.
  //
  //   call one    all-MiniLM-L6-v2 embeds the question and the nine subjects,
  //               nearest wins. 21 of 30 on questions nobody tuned for.
  //   call two    Qwen2.5-0.5B picks which of that tile's ten answers it.
  //   call three  Qwen writes one when none of the ten fits.
  //
  // Call one is the embedding model and not the generator because the generator
  // gets it right 3 times in 18: asked "why are you blue" it answered with the
  // cosines tile. Measured in src/eval_flow.py, both of them.
  //
  // Nothing is asked of the visitor's machine until they ask for it, and until
  // they have, the box is closed and the wall talks by itself.
  async ask(q){
    this._lastQ = String(q||'');
    this.stop();
    this.reset();
    this.say('');
    suggest(false);
    if(!this._model) return this.say(WALLLM.WAIT);
    const st = document.getElementById('mstat');
    try{
      if(st) st.textContent = 'which tile\u2026';
      const [id, sim] = await this._model(this._lastQ);
      if(st) st.textContent = '';
      if(sim >= WALLLM.THRESHOLD) return this.act(id);
    }catch(e){ if(st) st.textContent = ''; }
    return this.give(this._lastQ);
  },
  // One place where whatever the router named turns into something happening,
  // so nothing can be routed somewhere that quietly does nothing. DESC carries
  // three things that are not tiles -- show me everything, what is this,
  // surprise me -- and the router is allowed to pick those too.
  act(id){
    if(TILE[id]) return this.run(id);
    if(id === '_all') return this.all();
    if(id === '_help') return this.about();
    if(id === '_surprise'){ const k = Object.keys(TILE);
      return this.run(k[Math.floor(Math.random()*k.length)]); }
    return this.give(this._lastQ);
  },
  // The last resort, and it is never silence. Call three: the generator writes
  // one. If it wrote a digit, or sounded like an assistant, the page throws it
  // away and the wall reads one of its written refusals instead.
  async give(q){
    if(this._improvise){
      const st = document.getElementById('mstat');
      try{
        this.think(null);
        if(st) st.textContent = 'writing\u2026';
        const own = await this._improvise(String(q||''), null);
        if(st) st.textContent = '';
        if(own) return this.say(own);
      }catch(e){ if(st) st.textContent = ''; }
    }
    return this.miss();
  },
  // Twenty sentences, all true, all written here. The model may choose one; it
  // may not write one. See the note at the top of llm.js for why.
  lines(id){ return WALLLM.LINES.filter(([t]) => t === id).map(([,l]) => l); },
  knobs(on){
    this.stop();
    const b = document.body;
    b.classList.toggle('knobs', on === undefined ? !b.classList.contains('knobs') : !!on);
    const btn = document.getElementById('knobs');
    if(btn) btn.style.color = b.classList.contains('knobs') ? '#fff' : '';
    if(btn) btn.style.background = b.classList.contains('knobs') ? 'var(--ink)' : '';
    return b.classList.contains('knobs') ? 'knobs out' : 'knobs away';
  },
  // The wall types. It used to drop the whole sentence in at once, which read
  // as a caption rather than as an answer, and there is no other cue that the
  // thing is talking to you. The label lands whole and the words arrive after
  // it; whatever was still being typed is cancelled, because when the wall is
  // reciting nine tiles the next line must not race the last one.
  say(text, who){
    const el = document.getElementById('said');
    const cell = who && document.querySelector('[data-tile="'+who+'"] .tag');
    clearInterval(this._typing);
    el.classList.toggle('on', !!text);
    if(!text){ el.innerHTML = ''; return text; }
    const body = String(text).replace(/[<>]/g,'');
    el.innerHTML = (cell ? '<b>' + cell.textContent + '</b> ' : '') + '<span></span>';
    const out = el.lastChild;
    // a fixed budget of about a second, not a fixed rate: long enough to read
    // as typing, short enough that a long line does not outstay the 1.6 s a
    // recital gives it before the next tile speaks
    const per = Math.max(8, Math.min(30, 1350 / Math.max(1, body.length)));
    let i = 0;
    // the pager and the spotlight land with the label, not after the last
    // character: turning a page should move the wall the moment you click it
    this.hint(who);
    this._typing = setInterval(() => {
      i += body.length > 90 ? 2 : 1;
      out.textContent = body.slice(0, i);
      if(i >= body.length){ clearInterval(this._typing); out.textContent = body; }
    }, per);
    return text;
  },
  // The answer is a sentence and the page is a wall of knobs, and until now
  // nothing joined the two. One link brings the sliders out and says which
  // one; the other takes the tile off the wall, which is where the writing is.
  hint(id){
    const el = document.getElementById('more');
    if(!el) return id;
    if(!id || !TILE[id]){ el.className = 'more'; el.innerHTML = '';
                          this.spot(null); return id; }
    const ids = this._said || [];
    // the id rides on a data attribute, the way .ex carries its question: the
    // onclick is inside a python string inside a python string and a quote put
    // in here does not arrive as a quote out there
    el.innerHTML = (ids.length > 1
        ? '<span class="pg"><a onclick="wall.page(-1)" title="the tile before">&lsaquo;</a>'
          + '<i>' + (ids.indexOf(id) + 1) + ' of ' + ids.length + '</i>'
          + '<a onclick="wall.page(1)" title="the next tile">&rsaquo;</a></span>'
        : '')
      + '<a data-t="'+id+'" onclick="wall.tell(this.dataset.t)">'
      + 'find out more</a>';
    el.className = 'more on';
    this.spot(id);
    return id;
  },
  // whose line you are reading, marked on the wall, so paging moves a spotlight
  // around it rather than only swapping the sentence
  spot(id){
    document.querySelectorAll('.tile.current').forEach(c => c.classList.remove('current'));
    const c = id && document.querySelector('[data-tile="'+id+'"]');
    if(c) c.classList.add('current');
    return id;
  },
  tryit(id){ this.stop(); this.reset(); this.knobs(true);
    const c = document.querySelector('[data-tile="'+id+'"]');
    if(c){ c.classList.remove('nudge'); void c.offsetWidth; c.classList.add('nudge'); }
    return 'sliders out'; },
  tell(id){ this.close(); this.open(id); return this.why(id); },
  // Every question starts from the wall as it was found. Otherwise the second
  // question is answered by tiles still holding the first one's damage, and a
  // tile somebody left off the wall stays off through everything after it.
  reset(){
    Object.keys(TILE).forEach(k => {
      const r = document.getElementById(k+'r');
      if(r) this.set(k, +r.defaultValue);
    });
    document.querySelectorAll('.tile').forEach(c =>
      c.classList.remove('speaking','open','nudge','current'));
    this._said = []; this._at = 0;
    document.querySelector('.wall').classList.remove('busy');
    return 'reset';
  },
  async line(id, q){
    const ls = this.lines(id); if(!ls.length) return null;
    let s = null;
    const st = document.getElementById('mstat');
    if(this._pickLine && q){
      this.think(id);
      try{
        s = (await this._pickLine(q, ls, id)).line;
        if(!s && this._improvise){
          // nothing on the list fitted, so it writes one -- for this tile
          this.think(id);
          const own = await this._improvise(q, id);
          if(own) return this.say(own, id);
        }
      }catch(e){ if(st) st.textContent = ''; }
    }
    // No model, no pretending. The tile says the first of its ten, which is
    // written as its headline. Not a lottery -- and not a second hand-tuned
    // matcher pretending to have read the question either. If you want one of
    // the other nine chosen for you, there is a button for that.
    let line = s || ls[0];
    if(line.length < 62 && Math.random() < 0.28){
      const t = WALLLM.TAG.filter(x => x.length + line.length < 118);
      if(t.length) line += ' ' + t[Math.floor(Math.random()*t.length)];
    }
    // The aside is an aside. It used to arrive *instead of* the measurement,
    // which is the one thing on this page nobody should have to gamble for.
    if(Math.random() < 0.13){
      const a = WALLLM.ASIDE.filter(x => x.length + line.length < 168);
      if(a.length) line += ' \u2026 ' + a[Math.floor(Math.random()*a.length)];
    }
    return this.say(line, id);
  },
  miss(){ return this.say(WALLLM.MISS[Math.floor(Math.random()*WALLLM.MISS.length)]); },
  async converse(qs, ms=90){
    stopped=false;
    for(const q of qs){ if(stopped) break; await this.ask(q); await sleep(850); }
    return 'done';
  },
  async runAll(ms=70){
    stopped=false; running=true; document.getElementById('play').innerHTML='&#9632;';
    for(const id of Object.keys(TILE)){ if(stopped) break; await this.run(id,ms); await sleep(500); }
    running=false; document.getElementById('play').innerHTML='&#9654;';
    document.querySelectorAll('.tile').forEach(c=>c.classList.remove('speaking'));
    return 'done';
  }
};
const EX = {"cut": "how many cosines does it take to draw you?", "kil": "what did the fire do to you?", "perc": "when does your blue join up?", "eye": "what do I see of you from the door?", "chi": "which way do you curl?", "frac": "are you a fractal?", "copy": "who painted you?", "ship": "how much of you can I replace?", "attn": "what does attention find in you?"};
const sug=document.getElementById('sug'), qi=document.getElementById('q');
Object.entries(EX).forEach(([id,q])=>{const b=document.createElement('button');
  b.textContent=q; b.onclick=()=>{qi.value=q; wall.ask(q); suggest(false);}; sug.appendChild(b);});
// The list of nine lives behind the ? and nowhere else; nothing pops up on
// focus, and the input keeps a grey example instead.
function suggest(){ sug.classList.remove('on'); }
qi.addEventListener('keydown',e=>{ if(e.key==='Enter'){ wall.ask(e.target.value); e.target.blur(); }});
document.addEventListener('click',e=>{ if(!sug.contains(e.target)&&e.target!==qi) suggest(false); });
// When nobody has touched it for a while, a tile wakes up and runs its own
// slider. Everything it says while it does is a measured reading, so the page
// is never saying anything it cannot back up.
let lastTouch = Date.now();
['pointerdown','keydown','input'].forEach(e =>
  addEventListener(e, () => { lastTouch = Date.now(); }, true));
setTimeout(() => { if(!running) wall.perform(); }, 1400);
setInterval(() => {
  if (running || Date.now() - lastTouch < 25000) return;
  lastTouch = Date.now();
  wall.perform();
}, 4000);

const HELLO = [
  "I am nine tiles off one kitchen wall. Ask me anything about myself.",
  "Nine tiles, one photograph, nine questions somebody actually measured. Ask away.",
  "I am a kitchen wall in a Czech valley. Ask me something, or take a tile off with its ?",
];
setTimeout(()=>{ if(!document.getElementById('said').textContent)
  wall.say(HELLO[Math.floor(Math.random()*HELLO.length)]); }, 600);

// The examples only start cycling once a model is here to read them. Before
// that the box says what it is waiting for rather than inviting nine questions
// it cannot answer.
let exi=0; setInterval(()=>{
  if(qi.disabled || document.activeElement===qi || qi.value) return;
  const v=Object.values(EX); qi.placeholder='or ask it: '+v[exi++%v.length]; }, 3200);
addEventListener('resize',()=>{ if(bubFor) place(bubFor); });
// The top strip and the spoken line are set to the wall's real width, measured,
// rather than to a formula that guessed at the header height and was 16 px out.
(function(){
  const wall = document.querySelector('.wall');
  const fit = () => document.documentElement.style.setProperty('--wallw',
                       Math.round(wall.getBoundingClientRect().width) + 'px');
  fit();
  if (window.ResizeObserver) new ResizeObserver(fit).observe(wall);
  addEventListener('resize', fit);
})();
</script>
<script type="module">
// Nothing is downloaded when the page opens. Until both models are here the
// wall performs -- it has nine measured things to say and it says them -- and
// the question box is closed, because there is nothing behind it yet.
//
// Two buttons, two models, both in the visitor's own browser, no server and no
// key. Each says its size before it spends it, and takes itself off the bar
// once it has arrived.
//
//   let it read   23 MB   all-MiniLM-L6-v2   call one: which tile
//   let it write 483 MB   Qwen2.5-0.5B       call two: which of its ten
//                                            call three: write one, no digits
const DESC = ''' + json.dumps(DESC) + ''';
const NAMES = { cut:'COSINES', kil:'KILN', perc:'PERCOLATION', eye:'ACUITY',
                chi:'CHIRALITY', frac:'GEOMETRY', copy:'HISTORY',
                ship:'IDENTITY', attn:'ATTENTION' };
const st = document.getElementById('mstat');
const btn = document.getElementById('speak');
st.textContent = ''; st.className = 'mstat';

btn.onclick = async () => {
  btn.disabled = true; btn.textContent = 'fetching\u2026';
  try{
    const { pipeline } = await import(
      'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.6');

    // First the router, because it is the job the generators cannot do. Nine
    // descriptions and the question, all embedded, nearest one wins -- no words
    // to produce, which is why a 23 MB model beats a 483 MB one at it here.
    // src/eval_flow.py: SmolLM2-135M picks the tile 0 times in 18, Qwen2.5-0.5B
    // 3, and both answer with whichever number they have latched onto. MiniLM
    // does 21 of 30 on questions nobody tuned it for.
    btn.textContent = 'routing\u2026';
    const ex = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2',
      { dtype: 'q8', progress_callback: p => { if(p.status==='progress' && p.total)
          btn.textContent = Math.round(100*p.loaded/p.total) + ' %'; } });
    const dids = Object.keys(DESC);
    const V = (await ex(Object.values(DESC), { pooling:'mean', normalize:true })).tolist();
    window.wall._embed = async arr =>
      (await ex(arr, { pooling:'mean', normalize:true })).tolist();
    window.wall._all_model = async q => {
      const e = (await ex([q], { pooling:'mean', normalize:true })).tolist()[0];
      return dids.map((id,i) => [id, V[i].reduce((a,v,k)=>a+v*e[k],0)])
                 .sort((a,b) => b[1]-a[1]);
    };
    window.wall._model = async q => {
      const e = (await ex([q], { pooling:'mean', normalize:true })).tolist()[0];
      let best = null;
      dids.forEach((id,i) => { const sc = V[i].reduce((a,v,k)=>a+v*e[k],0);
        if(!best || sc > best[1]) best = [id, sc]; });
      return best;
    };
    window.wall._name = 'all-MiniLM-L6-v2';
    btn.remove();
    st.textContent = ''; st.className = 'mstat';
    document.getElementById('write').style.display = '';   // now the larger ask
  }catch(e){ btn.disabled = false; btn.textContent = 'could not load';
             console.warn(e); }
};

// Call two and call three: which of the tile's ten, and -- when none of them
// fits -- one sentence of its own. This is a generator's work and a router
// cannot do it, the same way the generators could not route. Qwen2.5-0.5B, not
// SmolLM2-135M, because SmolLM2 answered "1" to all eighteen lists of ten and
// Qwen reached ten distinct lines and took the first only three times.
const wbtn = document.getElementById('write');
wbtn.onclick = async () => {
  wbtn.disabled = true; wbtn.textContent = 'fetching\u2026';
  try{
    const { pipeline } = await import(
      'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.6');
    // navigator.gpu exists in plenty of browsers that cannot actually give you
    // an adapter, and asking for a webgpu pipeline there fetches 117 MB and
    // then throws "no available backend" -- after which the wasm retry inherits
    // the wreckage and throws too. So ask for the adapter first.
    let gpu = false;
    try{ gpu = !!(navigator.gpu && await navigator.gpu.requestAdapter()); }catch(e){}
    const tries = gpu ? [['webgpu','q4f16'],['wasm','q4']] : [['wasm','q4']];
    let gen = null, dev = null, err = null;
    for(const [device, dtype] of tries){
      try{
        gen = await pipeline('text-generation', window.WALLMODEL ||
            'onnx-community/Qwen2.5-0.5B-Instruct',
          { dtype, device, progress_callback: p => { if(p.status==='progress' && p.total)
              btn.textContent = Math.round(100*p.loaded/p.total) + ' %'; } });
        dev = device; break;
      }catch(e){ err = e; }
    }
    if(!gen) throw err;
    // return_full_text:false, or transformers.js hands back the prompt with the
    // answer on the end of it and every "answer" is the question, upper-cased.
    // This is why the three calls have never actually run: the router in front
    // of them was answering first, so nobody ever saw the model say anything.
    const say = async (sys, user, n) => {
      const o = await gen([{role:'system',content:sys},{role:'user',content:user}],
                          { max_new_tokens: n, do_sample: false, return_full_text: false });
      const m = o[0].generated_text;
      let t = Array.isArray(m) ? (m[m.length-1] && m[m.length-1].content || '') : String(m);
      // and if it came back full anyway, keep only what follows the last turn
      const cut = t.lastIndexOf(user);
      if(cut >= 0) t = t.slice(cut + user.length);
      return t.replace(/^\s*(assistant|<\|im_start\|>assistant)?\s*/i, '').trim();
    };
    // Call one: which tile, or none.
    //
    // Numbered, and answered with a number, because that is the shape call two
    // was already in and call two was the one that worked. Asked to answer with
    // a *name* out of nine names, Qwen2.5-0.5B said ATTENTION to all twenty-
    // seven questions in the eval -- the last item on the list -- and SmolLM2
    // restated the question. Same models, same nine tiles, 3/27 to 15/27 on the
    // shape of the prompt alone. Each option carries its subject, not just its
    // label, since the label is a pun half the time.
    window.wall._pickTile = async q => {
      const ids = Object.keys(NAMES);
      const numbered = ids.map((k,i) =>
        (i+1) + '. ' + NAMES[k] + ' \u2014 ' + (DESC[k]||'').split('.')[0]).join(' ');
      const said = await say(
        'You match a question to one of nine tiles on a kitchen wall. Answer with the '
        + 'number of the tile it belongs to. If it belongs to none of them, answer NONE. '
        + 'Answer with one number, or NONE.',
        'A visitor asks: "' + q + '" \u2014 which tile? ' + numbered + ' or NONE', 4);
      if(/NONE/i.test(said)) return { raw: 'NONE', tile: null };
      const d = (said.match(/[1-9]/) || [])[0];
      const k = d ? ids[+d - 1] : null;
      return { raw: said.slice(0,16), tile: k || null };
    };
    // Call two: which of these lines. The tile it is standing on is named, and
    // its subject given, because the same ten sentences mean different things
    // depending on which tile is saying them.
    window.wall._pickLine = async (q, opts, id) => {
      const numbered = opts.map((l,i) => (i+1) + '. ' + l).join(' ');
      const said = await say(
        'You are the ' + (NAMES[id] || 'tile') + ' tile on a kitchen wall. '
        + (DESC[id] || '') + ' The tile is already chosen. Now pick its reply by number. '
        + 'If none of them fits, answer NONE and you will get to write your own instead. '
        + 'Answer with one number, or NONE.',
        'A visitor asks: "' + q + '" \u2014 which reply? ' + numbered + ' or NONE', 4);
      if(/NONE/i.test(said)) return { raw: 'NONE', line: null };
      const d = (said.match(/[1-9]/) || [])[0];
      const i = d ? (+d - 1) : -1;
      return { raw: said.slice(0,12), line: opts[i] || null };
    };
    // Call three, and only once call two has come back empty: its own sentence,
    // for this tile, with the tile's subject in front of it. It may not contain
    // a digit -- every number on this page was measured off one photograph and
    // the model does not get to invent one. One digit and it is thrown away.
    window.wall._improvise = async (q, id) => {
      let t = await say(
        'You are a kitchen wall of nine painted tiles in a Czech valley, on the wall '
        + 'since 1885. You are dry, brief and slightly tired. You are a wall, not an '
        + 'assistant: you never offer help, never greet, never thank anybody and never '
        + 'say you are here to answer anything. One short sentence, first person, no '
        + 'numbers. '
        + (id ? 'You are its ' + NAMES[id] + ' tile. ' + (DESC[id] || '')
              + ' None of your written replies fitted, so this one is yours.'
             : 'The question is not about any of the nine things you were measured for. '
               + 'Answer it as the wall anyway.'),
        '"' + q + '" \u2014 reply in fewer than twelve words.', 26);
      t = String(t).split(String.fromCharCode(10))[0]
                   .replace(/^["\u201c]+|["\u201d]+$/g, '').trim();
      if(!t || t.length < 6 || t.length > 90) return null;
      if(/[0-9]/.test(t)) return null;                       // no invented numbers, ever
      // and no assistant. Measured before this filter existed: "hello" came
      // back "Hello! How may I assist you?", "how are you" came back "I'm doing
      // well, thank you", and a wall that has been up since 1885 says neither.
      if(/\b(assist|help you|how may i|how can i|thank you|you'?re welcome|happy to|here to (answer|help)|as an ai|language model)\b/i.test(t)) return null;
      const half = t.slice(0, Math.floor(t.length/2)).trim();
      if(half.length > 11 && t.indexOf(half, half.length) !== -1) return null;  // no loops
      return t;
    };
    window.wall._say = say;          // so src/eval_flow.py can score the raw model
    window.wall._names = NAMES;
    window.wall._think = true;
    window.wall._genName = 'Qwen2.5-0.5B on ' + dev;
    wbtn.remove(); st.remove();
    const qi2 = document.getElementById('q');
    qi2.disabled = false; qi2.placeholder = 'ask it something\u2026';
  }catch(e){ wbtn.disabled = false; wbtn.textContent = 'could not load';
             console.warn(e); }
};
</script></body></html>
'''
RULES_JS = """// The contract, in one place: the nine subjects the router is compared against,
// every sentence the wall can say, and the confidence below which it says none
// of them. wall.html and eval.html both load this file, so an evaluation can
// never score a copy that has drifted from what ships. The arrangement is
// borrowed, with thanks, from Unt1l1f1nd/coalescence.
//
// WHAT THE MODELS DO AND DO NOT DO HERE, measured -- src/eval_flow.py.
//
// all-MiniLM-L6-v2, 23 MB, decides which of the nine a question belongs to, by
// embedding it against the nine subjects below. 21 of 30 on questions nobody
// tuned for. It produces no words, which is why it beats a model twenty times
// its size at this and loses to it at everything else.
//
// Qwen2.5-0.5B picks which of a tile's ten sentences answers the question --
// ten distinct lines across nine tiles, first option only 3 times in 18 -- and
// writes one when none of them fits. It cannot route: 3 right in 18, and it
// answered "why are you blue" with the cosines tile.
//
// SmolLM2-135M can do neither: 0 in 18 on the tile, and "1" to all eighteen
// lists of ten.
window.WALLLM = (function(){
  const THRESHOLD = %s;
  const DESC = %s;
  const CHORUS = %s;
  const LOOK = %s;
  const LINES = %s;
  const MISS = %s;
  const CHAT = %s;
  const ASIDE = %s;
  const TAG = %s;
  const WAIT = 'Fetch the two models above and I can read what you type. Until '
             + 'then I will keep talking, and every tile still comes off the wall.';
  return { THRESHOLD, DESC, LINES, MISS, CHAT, ASIDE, TAG, LOOK, CHORUS, WAIT };
})();
""" % (THRESHOLD, json.dumps(DESC, indent=2), json.dumps(CHORUS, indent=1),
       json.dumps(LOOK, indent=1), json.dumps(LINES, indent=1), json.dumps(MISS, indent=1),
       json.dumps(CHAT, indent=1), json.dumps(ASIDE, indent=1), json.dumps(TAG, indent=1))
io.open("web/llm.js","w",encoding="utf-8").write(RULES_JS)
io.open("web/wall.html","w",encoding="utf-8").write(html)
print("web/wall.html  %.0f kB" % (len(html)/1000))
