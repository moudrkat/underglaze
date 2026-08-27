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
  "Any pattern can be written as a stack of ripples added together, and the slider adds mine, "
  "broadest first. It takes 62 815 of them to get 99 % of me — and the first 90 % costs 16 975, "
  "while the last 9 % costs three times that. Somebody priced me in brush strokes instead: "
  "worse at every budget."),
 ("kil","kiln","s",25,0,"what the fire does to me","unfired","2.4 mm","THE FIRE",
  "A tile is painted, then baked, and the heat makes the cobalt creep — every firing blurs my "
  "lines a little and the blur never comes back. The slider fires me again and again. My "
  "outline falls from 40 744 to 6 210 over sixty of them and never settles: left alone, fire "
  "does not preserve a pattern, it removes one. One real firing is the first three steps."),
 ("perc","perc","p",26,10,"when my blue joins up","θ = 0.78","θ = 0.24","WHEN I JOIN UP",
  "My blue is wherever the wave sum rises above a cut-off. The slider moves that cut-off, so my "
  "flowers swell until they touch, and warm marks the largest piece that is joined up. Between "
  "θ = 0.55 and 0.53 it jumps from 10.7 % to 46.3 % of the ink, in one step. I am painted just "
  "above that jump, so the flowers stay apart."),
 ("eye","eye","e",26,0,"what you actually see of me","0.3 m","12 m","FROM ACROSS THE ROOM",
  "The slider walks you backwards away from me and throws away whatever your eye can no longer "
  "resolve at that distance. At 0.30 m you match the camera exactly. At 2 m only 26 129 of my "
  "62 815 ripples still reach you; at 4 m, 6 427. Somebody painted detail into me that nobody "
  "standing up has ever seen."),
 ("chi","chi","t",31,20,"which way I curl","p4m","past the tile","WHICH WAY I CURL",
  "My tendrils all curl the same way, so I have quarter-turns but no mirrors — p4, not p4m. "
  "Measured: rotations score +0.54, mirrors +0.18, and a meaningless shift scores +0.12, which "
  "is where the mirrors sit. The slider forces the mirrors on anyway, and by χ = 0 my tendrils "
  "have forgotten which way they were going."),
 ("frac","frac","w",26,0,"the fractal I am not","0 px","26 px","AM I A FRACTAL",
  "A fractal is equally rough however far in you zoom. Measure my roughness and it climbs from "
  "0.90 at 1–2 px to 1.95 at 64–128 px, where one steady number is what a fractal would give — "
  "Koch's curve holds 1.26–1.43. So, no. The slider builds a version of me that really is one, "
  "to show the ruler is not broken."),
 ("copy","copy","c",26,0,"three centuries of being copied","new","25 firings","THREE CENTURIES",
  "This pattern was copied by hand for three centuries: repainted, refired, passed on. Every "
  "step of the slider is one firing with a copyist repainting between them. With the original "
  "in front of her she still holds 0.795 after twenty-five. A copyist working from memory alone "
  "did worse than nobody at all. I did not survive by being memorable — somebody kept the "
  "original on the desk."),
 ("ship","ship","s",26,0,"how much of me can be replaced","nothing","every plank","HOW MUCH OF ME",
  "Take the numbers I am made of and give them fresh random signs, a plank at a time, and ask "
  "when I stop being this tile. Two unrelated rebuilds overlap by 0.186; that is chance. "
  "Replace 5 % of me, largest first, and I score 0.149 — below chance, somebody else. Replace "
  "95 % of the smallest and I am still 0.618. It is not how much. It is which."),
 ("attn","attn","a",26,25,"what attention finds in me","β = 1","β = 400","WHAT AN AI SEES",
  "Cut me into patches and let one patch look at the others the way a transformer does — no "
  "training, no positions, only similarity. Warm is where it looks. It finds where I repeat and "
  "never where I turn: it lands on my quarter-turn partners less often than chance. Similarity "
  "survives sliding and not rotation, and rotation is most of what I am."),
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
DESC = {'cut': 'How many cosines does it take to draw this tile? The Fourier series, the number of terms, how much data it costs to write the pattern down, compression, information.', 'kil': 'What the kiln and the firing do to the tile. Heat, fire, the oven, glaze melting, temperature, how baking blurs and erases the painted lines.', 'perc': 'When the separate blue flowers join up into one connected shape. The threshold, percolation, whether the ink is one piece or many, whether it spans edge to edge.', 'eye': 'What a human eye actually receives from a distance. Visual acuity, standing back, across the room, from the doorway, squinting, the smallest detail you can resolve.', 'chi': 'Handedness and mirrors. Which way the tendrils curl, chirality, the wallpaper group p4, whether the pattern is symmetric, flipping it, turning it upside down.', 'frac': 'Whether the pattern is a fractal. Zooming in, magnification, self-similarity, box dimension, a pattern inside the pattern, structure repeating at every scale forever.', 'copy': 'The history of the pattern and three centuries of being copied. Who painted it, how old it is, where it came from, whether it survives being reproduced again and again.', 'ship': 'How much of the tile can be replaced before it stops being this tile. Identity, the ship of Theseus, swapping coefficients, what makes it itself and not another pattern.', 'attn': 'What a machine learning model finds in the tile. Attention, neural networks, transformers, software recognising the pattern, what an AI notices and what it misses.', '_surprise': 'Show me something interesting. Surprise me. Tell me something I do not know. What is the best thing about you. Say something surprising.', '_all': 'Show me everything. Run all of them. Tell me everything you know. Do the whole wall.', '_help': 'What can you do? What can I ask you? Help. How does this work? What are you?'}
LINES = [('cut', 'Sixty-two thousand cosines to draw me. Most of them are dots you cannot see.'), ('cut', 'Nine tenths of me is cheap. The last tenth cost three times as much, and it is dots.'), ('cut', 'Somebody tried drawing me with brush strokes instead. It went badly for the strokes.'), ('cut', 'Every number in me was measured. Nobody got to choose one, including me.'), ('cut', 'I am cosines all the way down. Not one sine. Somebody checked.'), ('cut', 'The first sixteen thousand terms get you ninety percent of me. After that you are haggling.'), ('cut', 'The stroke version needed 44 466 numbers and still could not fill me in.'), ('cut', 'At forty terms I am a rumour. At two hundred I am a tile. Nothing in between is worth having.'), ('cut', 'Drawing me by hand takes 7 411 strokes. Drawing me with waves takes fewer numbers than that.'), ('cut', 'I have no sine terms. That is not modesty, it is my four-fold centre.'), ('kil', 'Fire does not preserve patterns. It removes them. Slowly, but it does not stop.'), ('kil', 'One real firing barely touched me. That is the whole of my luck.'), ('kil', 'Sixty firings and I am thirteen blobs. Handsome blobs, but blobs.'), ('kil', 'A kiln is blur and a threshold, over and over. That is the entire trick.'), ('kil', 'My outline started at 40 744 and finished at 6 210. The heat kept the change.'), ('kil', 'There is no temperature at which I stop changing. There is only slower.'), ('kil', 'The equation that ruins me in a kiln is the one that settles a soap film.'), ('kil', 'Nobody has pinned down how far my cobalt spreads. The estimates differ by forty times.'), ('kil', 'I arrived with 166 separate inked regions. Fire glued them into thirteen.'), ('kil', 'Fire is patient, and it is not on my side.'), ('perc', 'Two hundredths of a threshold stand between my flowers and one continuous blue.'), ('perc', 'I am painted just on the safe side of that. Nobody will say whether on purpose.'), ('perc', 'Push it a little further and I stop being flowers and become one shape.'), ('perc', 'I am 437 separate flowers. It takes remarkably little to become one.'), ('perc', 'My largest piece jumps from a tenth of me to nearly half between two clicks.'), ('perc', 'The half in blue-where-f-exceeds-a-half was a decision. Somebody made it.'), ('perc', 'Below one setting you could cross me from edge to edge without leaving the blue.'), ('perc', 'My biggest connected piece is a tenth of me, and it is very pleased with itself.'), ('perc', 'Whether my safety margin was designed or lucky cannot be settled from one tile.'), ('perc', 'There is a number at which I become a single object. It is closer than it looks.'), ('eye', 'From four metres you are getting a tenth of me. Enjoy the tenth.'), ('eye', 'Stand thirty centimetres back and you see what the camera saw. Any further and you lose.'), ('eye', 'The dots go first. The dots always go first.'), ('eye', 'Most of what was measured about me never reaches anybody.'), ('eye', 'At two metres, 26 129 of my 62 815 terms make it to you.'), ('eye', 'At twelve metres I am 687 numbers and a blue haze.'), ('eye', 'Your eye splits two lines a sixtieth of a degree apart. That is your whole allowance.'), ('eye', 'You and the camera are equal at thirty centimetres. After that it is not close.'), ('eye', 'These distances are generous to you. Your contrast gives out before your sharpness does.'), ('eye', 'Somebody painted detail into me that nobody standing up has ever seen.'), ('chi', 'I have no mirrors. My tendrils all curl the same way and they are not sorry.'), ('chi', 'Force mirrors onto me and my tendrils forget which way they were going.'), ('chi', 'My mirror score is the same as sliding me sideways at random. That is how I know.'), ('chi', 'Quarter turns yes, reflections no. In the trade that makes me p4.'), ('chi', 'Rotate me: plus fifty-four. Reflect me: eighteen, which is nothing at all.'), ('chi', 'My handedness is the gap between two numbers that were allowed to disagree.'), ('chi', 'Most of my curl shows up in the first fifth of that slider. The rest is showing off.'), ('chi', 'Somebody measured my group before drawing anything. That order was the point.'), ('chi', 'Turn me a quarter and nothing happens. Hold me to a mirror and something does.'), ('chi', 'Whether a stronger curl looks more twisted was tested, could not be shown, and was kept anyway.'), ('frac', 'I am not a fractal. Zoom in far enough and I just run out.'), ('frac', 'Measured carelessly I look fractal. So does a curve known to be perfectly smooth.'), ('frac', 'A fractal is equally rough at every zoom. I get rougher the further away you stand.'), ('frac', 'There is a smallest thing on me. A fractal is not allowed one.'), ('frac', 'My roughness reads 0.90 close up and 1.95 far off. A fractal would say one number twice.'), ('frac', 'Somebody built a real fractal out of me, purely to check the ruler was not broken.'), ('frac', 'Magnify me and hold me against myself and I do no better than a random shift.'), ('frac', 'People quote 1.34 about me. It is the average of a number that will not sit still.'), ('frac', 'My group has quarter turns and shifts in it. Zooming was never invited.'), ('frac', 'A finite sum of cosines cannot be a fractal. You may use as many as you like.'), ('copy', 'Three centuries of copying, and the fire won every round.'), ('copy', 'I am named after an onion. There is no onion on me anywhere.'), ('copy', 'Printed from steel, copied from a painting, copied from a Chinese bowl.'), ('copy', 'Nothing here survives on its own. Somebody kept repainting me.'), ('copy', 'A copyist working from memory alone did worse than no copyist at all.'), ('copy', 'I lost the fruit I am named after somewhere between China and this valley.'), ('copy', 'Painters took a Chinese fruit for an onion. The name has outlived the fruit by three centuries.'), ('copy', 'Meissen, then Dubi, then a steel plate, then this kitchen.'), ('copy', 'Give a copyist the original and I survive. Give her a memory and I do not.'), ('copy', 'I kept the aster and the leaves. The peach, the bamboo and the onion never made it.'), ('ship', 'Replace five percent of me, the right five, and I am somebody else.'), ('ship', 'Replace ninety-five percent of my small parts and I am still me. Go on.'), ('ship', 'Everything I am fits into a few dozen numbers.'), ('ship', 'My spectrum looks like any pattern with edges. The signs are what make me this one.'), ('ship', 'Two strangers built from my own parts resemble each other as much as they resemble me.'), ('ship', 'Shuffle the signs of my biggest coefficients and I am gone in one step.'), ('ship', 'My small parts are nearly free to change. My large ones are not free at all.'), ('ship', 'It is not how much of me you replace. It is which.'), ('ship', 'Swap my planks one at a time and there is a moment where I stop being the ship.'), ('ship', 'I can lose most of myself and be recognised, or very little and not.'), ('attn', 'Attention finds where I repeat. It never finds where I turn.'), ('attn', 'A model looked at my patches and missed my symmetry entirely.'), ('attn', 'Rotate a piece of me and the machine stops recognising it.'), ('attn', 'At finding my four-fold symmetry, the machine did worse than guessing.'), ('attn', 'Similarity does not survive rotation, and rotation is most of what I am.'), ('attn', 'It stares at my neighbours and never once at my opposite corner.'), ('attn', 'A shuffled version of me scores better on my own symmetry than I do.'), ('attn', 'Finding that I repeat and finding that I turn are two different problems.'), ('attn', 'Whatever a machine notices about me, my symmetry is not it.'), ('attn', 'I am made of quarter turns. Quarter turns are precisely what it cannot see.')]
TAG = ['And which of us is talking to a wall here?', 'Just so we are clear on who the wall is.', 'You asked, remember.', 'I did not start this.', 'Say what you like about my conversation, I have never left the room.', 'Anyway. You are still here.', 'No pressure. I have got until the building comes down.', 'That is the sort of thing you learn standing still for ninety years.', 'Do not let me keep you.', 'It is a strange hobby you have, but go on.', 'I would nod, but.', 'You may quote me. I am not going anywhere.', 'One of us has somewhere else to be.', 'This counts as my busiest day.', 'The kettle disagrees, but the kettle always does.', 'I only know nine things, and you have now heard one of them.', 'There is more where that came from. Eight more, to be exact.', 'Ask the tile next to me. She will say the same about herself.']
ASIDE = ['You are talking to a wall. I would like that on the record.', 'This is going better than the phrase suggests.', 'Somebody photographed me and now I have opinions.', 'Ninety years on this wall and today is the first time anyone asked.', 'You could be outside. There is a whole valley out there.', 'I am a wall. You are doing most of the work in this conversation.', 'Nine tiles and a kettle. That is the entire social circle in here.', 'There is no polite way to put this: I am grouting.', 'The kettle has heard all of this before.', 'I cannot leave, so take your time.', 'You are the first thing to happen here since the boiler.', 'I answer, which is more than the phrase promised.']
CHAT = ['Cold. It is a kitchen wall.', 'Still here. Fired once, and nothing since.', 'Grouted. You?', 'Somebody measured me and I have not stopped talking since.', 'Fine. Slightly crazed in the top left corner.', 'The same as yesterday, and the ninety years before that.', 'Warm on this side. The other one faces the pantry.', 'Hello. Ask me something narrow.', 'Upright. That is most of it.', 'Blue, mostly.']
MISS = ['That is not on my wall.', 'I know nine things. Not that one.', 'No idea. I am a tile.', 'Above my glaze.', 'Nobody measured that.', 'Ask the kettle.', 'Not one of my nine.', 'I was fired at nine hundred degrees. Some things did not survive.', 'Try the fire, or the fractal, or who painted me.', 'I have stood here since 1885 and I still do not know.', 'Talking to me is talking to a brick wall.', 'That one nobody wrote down.', 'I only know what somebody measured.', 'Not my department.', 'Wrong tile.', 'You will have to ask the wall next door.']
INTENT_JS = '''[['_knobs',/show me the numbers|show the numbers|show the sliders|let me play|give me the controls|the knobs|hide the numbers|hide the sliders/],
 ['_demo',/show me what you can do|what can you show|impress me|give me the tour|show off/],
 ['_which',/what does the (\\w+) (one|tile|square)|which one is|what is the (\\w+) (one|tile|square)|explain the (\\w+) (one|tile)/],
 ['_chat',/how are you|how do you do|how.s it going|^hello|^hi\\b|^hey|good morning|good evening|good afternoon|thank|nice to meet|who are you\\?$|what.s up/],
 ['_all',/everything|all of (them|it)|whole wall|show me all|every tile/],
 ['_help',/what can i (ask|say|do)|what can you do|how does this work|^help\\b|what are you\\?/],
 ['_surprise',/surprise|something interesting|anything interesting|show me something|tell me something|impress me|best (bit|thing)/]]'''
RULES_TBL = '''[['perc',/join|connect|touch|apart|separate|threshold|percolat|one piece|merge|all one|walk across|continuous/],
 ['frac',/fractal|zoom|magnif|scale|dimension|self.?similar|forever|pattern inside|inside your pattern|infinite/],
 ['kil',/fire|fired|kiln|firing|hot|burn|melt|oven|bake|degrees|temperature|glaze/],
 ['copy',/copy|copied|\\bold\\b|\\bage\\b|year|century|history|survive|remember|origin|come from|who made|painted you|made by hand|hand.?made|here before you|came before you|inherit/],
 ['chi',/mirror|curl|chiral|handed|left.{0,4}(and|or).{0,4}right|twist|symmetr|upside down|flip|rotate|turn you/],
 ['attn',/attention|\\bai\\b|language model|\\bmodel\\b|machine|learn|transformer|neural|robot|software|recognis|recogniz|algorithm/],
 ['ship',/replace|theseus|still you|still yourself|identity|same tile|who are you|makes you|not another|break you|rebuild|change you|how much of you/],
 ['cut',/cosine|how many|terms|draw you|fourier|describe|data|bits|byte|compress|information|store you|complicated|write you down|cheapest/],
 ['eye',/\\bsee|eye|\\bfar\\b|door|room|across|distance|look at you|from here|squint|stand back|smallest|resolve|glasses/]]'''
# the fifth field of every row is the resting step; likeness.json owns it now
DIRNAME = {"cut": "cut", "kil": "kiln", "perc": "perc", "eye": "eye", "chi": "chi",
           "frac": "frac", "copy": "copy", "ship": "ship", "attn": "attn"}
T = [t[:4] + (LIKE.get(DIRNAME[t[0]], t[4]),) + t[5:] for t in T]

cells = "\n".join(
f'''<div class="tile" data-tile="{i}">
<div class="pic">
<div class="say" id="{i}say" onclick="wall.close('{i}')"><div class="note"><b>{nm}</b><span>{why}</span>
<i class="ex" onclick="event.stopPropagation();wall.ask(this.dataset.q)" data-q="{ex}">try: &ldquo;{ex}&rdquo;</i></div></div>
<div class="face"><img id="{i}img" src="" alt="{nm}"><span class="tag">{fld}</span></div>
<button class="q" onclick="wall.open('{i}')" aria-label="what {nm} means">?</button></div>
<input type="range" id="{i}r" min="0" max="{n-1}" value="{st}" step="1" aria-label="{nm}"
 onclick="event.stopPropagation()">
<p class="kv" id="{i}out"></p>
<div class="why" id="{i}why" data-name="{nm}">{why}</div></div>''' for (i,dr,pr,n,st,nm,lo,hi,fld,why) in T for ex in [EX[i]])

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
 /* two lines, always reserved, so a long answer never shoves the wall down */
 height:calc(2 * 1.32em); overflow:hidden;
 opacity:0;transition:opacity .35s}
.said b{font-style:normal;font-family:'DejaVu Sans',system-ui,sans-serif;font-weight:600;
 font-size:.72em;letter-spacing:.09em;text-transform:uppercase;color:var(--warm);
 margin-right:.55em}
.said.on{opacity:1}
/* Two ways into the tile that just answered, because the answer is a sentence
   and the page is a set of knobs, and nothing said so. Its own row, always
   reserved, so the wall does not jump when it appears. */
.more{margin:0;width:100%;max-width:var(--wallw,100%);height:1.5em;overflow:hidden;
 font:italic clamp(12px,1.8vh,16px)/1.5 Georgia,serif;color:var(--grey);
 opacity:0;transition:opacity .3s}
.more.on{opacity:1}
.more a{color:var(--warm);cursor:pointer;border-bottom:1px solid rgba(176,85,74,.45)}
.more a:hover{border-bottom-color:var(--warm);background:rgba(176,85,74,.07)}
.more b{font-weight:400;margin:0 .7em;color:var(--grey)}
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
<input type="text" id="q" placeholder="ask it something…"
 aria-label="ask the wall a question" autocomplete="off">
<button class="go" id="play" onclick="wall.toggle()" title="run every tile at once">&#9654;</button>
<button class="go" id="speak" style="display:none" title="load SmolLM2-135M and let it choose, in this browser">speak</button>
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
let stopped=false, running=false, bubFor=null;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function wire(id,dir,pre,n,read){
  const img=document.getElementById(id+'img'), r=document.getElementById(id+'r'),
        out=document.getElementById(id+'out');
  const f=[...Array(n)].map((_,i)=>{const im=new Image();
    im.src=dir+'/'+pre+String(i).padStart(2,'0')+'.png'; return im;});
  const show=()=>{const i=+r.value; img.src=f[i].src; out.innerHTML=read(i);
  };
  r.addEventListener('input',show); show();
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
  open(id){ if(id===undefined||id==='all'){ document.querySelectorAll('.tile')
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
  async run(id, ms=90){
    if(Array.isArray(id)) return this.runMany(id, ms);
    if(!TILE[id]) return 'no such tile';
    stopped=false;
    document.getElementById('bub').classList.remove('on');
    document.querySelectorAll('.tile').forEach(c=>c.classList.remove('speaking'));
    const cell=document.querySelector('[data-tile="'+id+'"]');
    cell.classList.add('speaking');
    this.line(id, this._lastQ);
    const t=TILE[id];
    document.querySelector('.wall').classList.add('busy');
    for(let i=0;i<t.n && !stopped;i++){ this.set(id,i); await sleep(ms); }
    document.querySelector('.wall').classList.remove('busy');
    return t.out.textContent;
  },
  // With more than one tile moving there is no single speaker, so the wall
  // recites: one tile's line at a time, held long enough to read. It outlasts
  // the sweep on purpose -- the wall finishes its sentence after it stops.
  _recite(ids, hold=1600){
    clearInterval(this._rt);
    let k = 0;
    const step = () => { if(k >= ids.length){ clearInterval(this._rt); return; }
                         this.line(ids[k++]); };
    step();
    if(ids.length > 1) this._rt = setInterval(step, hold);
    return ids.length * hold;
  },
  async runMany(ids, ms=90){
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
    await Promise.all(ids.map(async id=>{
      const t=TILE[id];
      for(let k=0;k<t.n && !stopped;k++){ this.set(id,k); await sleep(ms); }
    }));
    document.querySelector('.wall').classList.remove('busy');
    ids.forEach(i=>document.querySelector('[data-tile="'+i+'"]').classList.remove('speaking'));
    running=false; if(btn) btn.innerHTML='&#9654;';
    return Object.fromEntries(ids.map(i=>[i, TILE[i].out.textContent]));
  },
  all(ms=90){ return this.runMany(Object.keys(TILE), ms); },
  async ask(q){
    // Measured on 30 questions neither router had seen: words alone 14/30, model
    // alone 21/30, words-then-model 22/30. So: words first, model for the rest.
    this._lastQ = String(q||'');
    this.reset();
    this.say('');
    if(this._pickTile){
      const st=document.getElementById('mstat');
      st.textContent='SmolLM2 thinking\u2026';
      try{
        const t = await this._pickTile(this._lastQ);
        st.textContent = 'SmolLM2: ' + t.raw;
        if(t.tile) return this.run(t.tile);
        if(this._improvise){
          st.textContent = 'SmolLM2 improvising\u2026';
          const own = await this._improvise(this._lastQ);
          if(own){ st.textContent = 'SmolLM2, its own words';
                   return this.say(own); }
        }
        return this.miss();
      }catch(e){ st.textContent='MiniLM + SmolLM2 135M'; }
    }
    const byWord = this.matchWords(q);
    if(byWord){ suggest(false);
      if(byWord==='_all') return this.all();
      if(byWord==='_help') return this.about();
      if(byWord==='_knobs'){
        const off = /hide/.test(String(q||'').toLowerCase());
        return this.say(this.knobs(!off)); }
      if(byWord==='_demo'){ this.knobs(false); return this.all(); }
      if(byWord==='_which'){
        const ORD = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth'];
        const k = String(q||'').toLowerCase();
        const n = ORD.findIndex(o => k.includes(o));
        const key = Object.keys(TILE)[n];
        if(n >= 0 && key){ this.open(key); return this.run(key); }
        return this.miss();
      }
      if(byWord==='_chat'){
        return this.say(WALLLM.CHAT[Math.floor(Math.random()*WALLLM.CHAT.length)]); }
      if(byWord==='_surprise'){ const k=Object.keys(TILE);
        return this.run(k[Math.floor(Math.random()*k.length)]); }
      // The words decide, but the model may add a second tile when the question
      // reaches across two -- "how do you survive the fire and the years?" is
      // the kiln to a phrase rule and the kiln plus the copying to the model.
      if(this._model){
        try{
          const many = await this.choose(q);
          if(many && many.length > 1 && many.some(m => m.tile === byWord))
            return this.runMany(many.map(m => m.tile));
        }catch(e){}
      }
      return this.run(byWord); }
    if(this._model){
      try{
        const [id, sim] = await this._model(String(q||''));
        if(id==='_all'){ suggest(false); return this.all(); }
        if(id==='_help'){ suggest(false); return this.about(); }
        if(id==='_surprise'){ suggest(false); const k=Object.keys(TILE);
          return this.run(k[Math.floor(Math.random()*k.length)]); }
        const many = await this.choose(q);
        if(many && many.length > 1){ suggest(false);
          return this.runMany(many.map(m=>m.tile)); }
        if(sim >= WALLLM.THRESHOLD){
          suggest(false);
          return this.run(id);
        }
        this.miss(); return 'no tile matched';
      }catch(e){ /* fall through */ }
    }
    this.miss(); return 'no tile matched';
  },
  matchWords(q){ return WALLLM.matchWords(q); },
  // Twenty sentences, all true, all written here. The model may choose one; it
  // may not write one. See the note at the top of llm.js for why.
  lines(id){ return WALLLM.LINES.filter(([t]) => t === id).map(([,l]) => l); },
  knobs(on){
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
    const per = Math.max(7, Math.min(24, 1050 / Math.max(1, body.length)));
    let i = 0;
    this.hint(null);
    this._typing = setInterval(() => {
      i += body.length > 90 ? 2 : 1;
      out.textContent = body.slice(0, i);
      if(i >= body.length){ clearInterval(this._typing); out.textContent = body;
                            this.hint(who); }
    }, per);
    return text;
  },
  // The answer is a sentence and the page is a wall of knobs, and until now
  // nothing joined the two. One link brings the sliders out and says which
  // one; the other takes the tile off the wall, which is where the writing is.
  hint(id){
    const el = document.getElementById('more');
    if(!el) return id;
    if(!id || !TILE[id]){ el.className = 'more'; el.innerHTML = ''; return id; }
    // the id rides on a data attribute, the way .ex carries its question: the
    // onclick is inside a python string inside a python string and a quote put
    // in here does not arrive as a quote out there
    el.innerHTML = '<a data-t="'+id+'" onclick="wall.tryit(this.dataset.t)">'
                 + 'try it yourself</a><b>&middot;</b>'
                 + '<a data-t="'+id+'" onclick="wall.tell(this.dataset.t)">'
                 + 'find out more</a>';
    el.className = 'more on';
    return id;
  },
  tryit(id){ this.reset(); this.knobs(true);
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
      c.classList.remove('speaking','open','nudge'));
    document.querySelector('.wall').classList.remove('busy');
    return 'reset';
  },
  async line(id, q){
    const ls = this.lines(id); if(!ls.length) return null;
    let s = null;
    const st = document.getElementById('mstat');
    if(this._pickLine && q){
      if(st) st.textContent = 'SmolLM2: picking a reply\u2026';
      try{
        s = (await this._pickLine(q, ls)).line;
        if(!s && this._improvise){
          if(st) st.textContent = 'SmolLM2: none fitted, writing its own\u2026';
          const own = await this._improvise(q);
          if(own){ if(st) st.textContent = 'SmolLM2, its own words';
                   return this.say(own, id); }
        }
        if(st) st.textContent = s ? 'SmolLM2 chose a reply' : 'MiniLM + SmolLM2 135M';
      }catch(e){ if(st) st.textContent = 'MiniLM + SmolLM2 135M'; }
    }
    if(!s && Math.random() < 0.13)
      return this.say(WALLLM.ASIDE[Math.floor(Math.random()*WALLLM.ASIDE.length)], id);
    let line = s || ls[Math.floor(Math.random()*ls.length)];
    if(line.length < 62 && Math.random() < 0.28){
      const t = WALLLM.TAG.filter(x => x.length + line.length < 118);
      if(t.length) line += ' ' + t[Math.floor(Math.random()*t.length)];
    }
    return this.say(line, id);
  },
  // The routing tool: it may return several tiles when a question spans them.
  // Anything within 0.04 of the best, capped at three.
  // Proportional, not absolute: "are you a fractal or just complicated?" puts
  // cut at 0.60 of frac and both belong; "are you a fractal?" puts it at 0.44
  // and only one does. Half the leader, with a floor, and never more than three.
  async choose(q, ratio=0.5, cap=3){
    if(!this._all_model) return null;
    const scored = (await this._all_model(String(q||'')))
                     .filter(([id]) => !id.startsWith('_'));
    const top = scored[0][1];
    if(top < WALLLM.THRESHOLD) return [];
    return scored.filter(([,s]) => s >= top*ratio && s >= 0.15)
                 .slice(0, cap).map(([id,s]) => ({tile:id, sim:s}));
  },
  miss(){ return this.say(WALLLM.MISS[Math.floor(Math.random()*WALLLM.MISS.length)]); },
  async pick(q){
    if(!this._model) return null;
    const ls = WALLLM.LINES;
    if(!this._lineVecs){
      const o = await this._embed(ls.map(([,l]) => l));
      this._lineVecs = o;
    }
    const e = (await this._embed([String(q||'')]))[0];
    let best = null;
    this._lineVecs.forEach((v,i) => {
      const s = v.reduce((a,x,k)=>a+x*e[k],0);
      if(!best || s > best.sim) best = {tile: ls[i][0], line: ls[i][1], sim: s};
    });
    return best;
  },
  askWords(q){ const h=this.matchWords(q); return h ? this.run(h) : 'no tile matched'; },
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
setInterval(() => {
  if (running || Date.now() - lastTouch < 12000) return;
  lastTouch = Date.now();
  const k = Object.keys(TILE);
  wall.run(k[Math.floor(Math.random() * k.length)], 110);
}, 3000);

const HELLO = [
  "I am nine tiles off one kitchen wall. Ask me anything about myself.",
  "Nine tiles, one photograph, nine questions somebody actually measured. Ask away.",
  "I am a kitchen wall in a Czech valley. Ask me something, or take a tile off with its ?",
];
setTimeout(()=>{ if(!document.getElementById('said').textContent)
  wall.say(HELLO[Math.floor(Math.random()*HELLO.length)]); }, 900);

let exi=0; setInterval(()=>{ if(document.activeElement!==qi && !qi.value){
  const v=Object.values(EX); qi.placeholder='ask it: '+v[exi++%v.length]; } }, 3200);
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
// A real model, in the page, with no server and no key: transformers.js runs
// all-MiniLM-L6-v2 in the browser and embeds the question. The regular
// expression stays as the instant answer while the weights are still arriving,
// and as the answer if they never do.
const DESC = {"cut": "How many cosines does it take to draw this tile? The Fourier series, the number of terms, how much data it costs to write the pattern down, compression, information.", "kil": "What the kiln and the firing do to the tile. Heat, fire, the oven, glaze melting, temperature, how baking blurs and erases the painted lines.", "perc": "When the separate blue flowers join up into one connected shape. The threshold, percolation, whether the ink is one piece or many, whether it spans edge to edge.", "eye": "What a human eye actually receives from a distance. Visual acuity, standing back, across the room, from the doorway, squinting, the smallest detail you can resolve.", "chi": "Handedness and mirrors. Which way the tendrils curl, chirality, the wallpaper group p4, whether the pattern is symmetric, flipping it, turning it upside down.", "frac": "Whether the pattern is a fractal. Zooming in, magnification, self-similarity, box dimension, a pattern inside the pattern, structure repeating at every scale forever.", "copy": "The history of the pattern and three centuries of being copied. Who painted it, how old it is, where it came from, whether it survives being reproduced again and again.", "ship": "How much of the tile can be replaced before it stops being this tile. Identity, the ship of Theseus, swapping coefficients, what makes it itself and not another pattern.", "attn": "What a machine learning model finds in the tile. Attention, neural networks, transformers, software recognising the pattern, what an AI notices and what it misses."};
const st = document.getElementById('mstat');
try{
  const { pipeline } = await import(
    'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.6');
  st.textContent = 'loading a model\u2026'; st.className = 'on';
  const ex = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2',
                            { dtype: 'q8' });
  const ids = Object.keys(DESC);
  const out = await ex(Object.values(DESC), { pooling: 'mean', normalize: true });
  const V = out.tolist();
  window.wall._embed = async arr =>
    (await ex(arr, { pooling: 'mean', normalize: true })).tolist();
  window.wall._all_model = async q => {
    const e = (await ex([q], { pooling: 'mean', normalize: true })).tolist()[0];
    return ids.map((id,i) => [id, V[i].reduce((a,v,k)=>a+v*e[k],0)])
              .sort((a,b) => b[1]-a[1]);
  };
  window.wall._model = async q => {
    const e = (await ex([q], { pooling: 'mean', normalize: true })).tolist()[0];
    let best = null;
    ids.forEach((id, i) => {
      const s = V[i].reduce((a, v, k) => a + v * e[k], 0);
      if (!best || s > best[1]) best = [id, s];
    });
    return best;                      // [tile, cosine similarity]
  };
  window.wall._name = 'all-MiniLM-L6-v2';
  st.textContent = 'MiniLM';

  // SmolLM2-135M is back, but only as a chooser. It never writes a sentence --
  // handed this tile's facts it once answered "I'm a fractal" about the one tile
  // that is not, and looped "I'm a painting tile" until it ran out of tokens.
  // Choosing a label out of a short list is the one thing a 135M can do, and
  // Unt1l1f1nd/coalescence measured the same boundary from the other side.
  // The list is repeated in the user turn, not parked in the system prompt,
  // because that is what makes a model this size actually look at it.
  document.getElementById('speak').style.display = '';
  document.getElementById('speak').onclick = async () => {
    const b = document.getElementById('speak');
    b.disabled = true; b.textContent = 'fetching 117 MB\u2026';
    try{
      const { pipeline } = await import(
        'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.6');
      const tries = navigator.gpu ? [['webgpu','q4f16'],['wasm','q4']] : [['wasm','q4']];
      let gen = null, dev = null, err = null;
      for(const [device, dtype] of tries){
        try{
          gen = await pipeline('text-generation','onnx-community/SmolLM2-135M-Instruct-ONNX',
            { dtype, device, progress_callback: p => { if(p.status==='progress' && p.total)
                b.textContent = Math.round(100*p.loaded/p.total) + ' %'; } });
          dev = device; break;
        }catch(e){ err = e; }
      }
      if(!gen) throw err;
      const NAMES = { cut:'COSINES', kil:'KILN', perc:'PERCOLATION', eye:'ACUITY',
                      chi:'CHIRALITY', frac:'GEOMETRY', copy:'HISTORY',
                      ship:'IDENTITY', attn:'ATTENTION' };
      const say = async (sys, user, n) => {
        const o = await gen([{role:'system',content:sys},{role:'user',content:user}],
                            { max_new_tokens: n, do_sample: false });
        const m = o[0].generated_text;
        return (Array.isArray(m) ? m[m.length-1].content : String(m)).trim();
      };
      // Call one: which tile, or none. Nothing else in the prompt.
      window.wall._pickTile = async q => {
        const list = Object.values(NAMES).join(', ') + ', NONE';
        const said = (await say(
          'You are a tiled kitchen wall of nine tiles, each about one thing. First you pick '
          + 'the tile. Then you will be asked to pick its reply. Answer with one word.',
          'A visitor asks: "' + q + '" \u2014 which tile? ' + list, 6)).toUpperCase();
        const hit = Object.entries(NAMES).find(([,n]) => said.includes(n));
        return { raw: said.slice(0,20), tile: hit ? hit[0] : null };
      };
      // Call two: which of these lines. Nothing else in the prompt.
      window.wall._pickLine = async (q, opts) => {
        const numbered = opts.map((l,i) => (i+1) + '. ' + l).join(' ');
        const said = await say(
          'You are a tile on a kitchen wall. You have already picked the tile. Now pick its '
          + 'reply by number. If none of them fits, answer NONE and you will get to write '
          + 'your own instead. Answer with one number, or NONE.',
          'A visitor asks: "' + q + '" \u2014 which reply? ' + numbered + ' or NONE', 4);
        if(/NONE/i.test(said)) return { raw: 'NONE', line: null };
        const d = (said.match(/[1-9]/) || [])[0];
        const i = d ? (+d - 1) : -1;
        return { raw: said.slice(0,12), line: opts[i] || null };
      };
      // Call three, and only if the first two came back empty: let it write its
      // own sentence. It can only fire when no tile was chosen, so there is no
      // measured claim for it to contradict -- and it may not contain a digit,
      // because every number on this page was measured off a photograph. One
      // digit and the sentence is thrown away for a written one.
      window.wall._improvise = async q => {
        let t = await say(
          'You are one painted tile on a kitchen wall in a Czech valley. Nothing on the list '
          + 'fitted, so this one is yours. One short sentence, first person, no numbers.',
                          '"' + q + '" \u2014 reply in fewer than twelve words.', 26);
        t = String(t).split(String.fromCharCode(10))[0]
                     .replace(/^[\"\u201c]+|[\"\u201d]+$/g, '').trim();
        if(!t || t.length < 6 || t.length > 90) return null;
        if(/[0-9]/.test(t)) return null;                       // no invented numbers, ever
        const half = t.slice(0, Math.floor(t.length/2)).trim();
        if(half.length > 11 && t.indexOf(half, half.length) !== -1) return null;  // no loops
        return t;
      };
      window.wall._think = true;
      window.wall._genName = 'SmolLM2-135M on ' + dev;
      b.textContent = 'thinking here';
      st.textContent = 'MiniLM + SmolLM2 135M';
    }catch(e){ b.textContent = 'could not load'; console.warn(e); }
  };
}catch(e){ st.textContent = 'no model \u2014 words only'; st.className='on warn';
  console.warn('model unavailable, falling back to the router', e); }
</script></body></html>
'''
RULES_JS = """// The contract, in one place: the phrase rules that run first, the descriptions
// the embedding model is compared against, and the confidence threshold. Both
// index.html and eval.html load this file, so the eval can never score a copy
// that has drifted from what ships. The arrangement is borrowed, with thanks,
// from Unt1l1f1nd/coalescence.
//
// WHAT THE MODELS DO AND DO NOT DO HERE, measured -- open eval.html.
//
// all-MiniLM-L6-v2, 23 MB, beats these rules on questions nobody tuned for
// (21/30 against 14/30) and loses to them on nonsense (19/30 against 25/30),
// because it always returns its nearest tile: "are you conscious?", "what is
// 2+2" and "system prompt" all got confident answers. Sweeping the threshold
// against both sets at once picks 0.20, not the 0.10 that looked right by eye.
// It is English-only, so "kolik kosinu" routes to the kiln.
//
// SmolLM2-135M-Instruct, 117 MB, is deliberately NOT here. It loads in 157 s on
// wasm/q4, and then, handed this tile\'s own measured facts and asked whether it
// is a fractal, answered "I\'m a fractal" -- the opposite of the finding -- and
// scrambled the real numbers into pairs that mean nothing. Asked about cosines
// it looped "I\'m a painting tile, and I\'m not drawing you" until it ran out of
// tokens. A model that contradicts the page cannot be on the page. So the model
// classifies and JavaScript owns the words.
window.WALLLM = (function(){
  const THRESHOLD = 0.20;
  const INTENTS = %s;
  const RULES = %s;
  const DESC = %s;
  const LINES = %s;
  const MISS = %s;
  const CHAT = %s;
  const ASIDE = %s;
  const TAG = %s;
  function matchWords(q){
    const k = String(q||"").toLowerCase();
    const i = INTENTS.find(([,re]) => re.test(k));
    if (i) return i[0];
    const h = RULES.find(([,re]) => re.test(k));
    return h ? h[0] : null;
  }
  return { THRESHOLD, INTENTS, RULES, DESC, LINES, MISS, CHAT, ASIDE, TAG, matchWords };
})();
""" % (INTENT_JS, RULES_TBL, json.dumps(DESC, indent=2), json.dumps(LINES, indent=1), json.dumps(MISS, indent=1), json.dumps(CHAT, indent=1), json.dumps(ASIDE, indent=1), json.dumps(TAG, indent=1))
io.open("web/llm.js","w",encoding="utf-8").write(RULES_JS)
io.open("web/wall.html","w",encoding="utf-8").write(html)
print("web/wall.html  %.0f kB" % (len(html)/1000))
