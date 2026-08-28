// The contract, in one place: the nine subjects the router is compared against,
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
  const THRESHOLD = 0.14;
  const DESC = {
  "cut": "How many numbers it takes to write this tile down. Cosines, Fourier terms, how much data and information it costs to store or describe the pattern, compression, the shortest description, brush strokes against waves.",
  "kil": "What the kiln and the firing do to it. Heat, fire, the oven, baking, nine hundred degrees, glaze melting, how firing blurs and erases the painted lines, how the cobalt creeps and spreads.",
  "perc": "When the separate blue flowers join up into one connected shape. The cut-off, the threshold, percolation, why the tile is blue and where the blue stops, whether the ink is one piece or many, whether the flowers touch each other, whether it spans edge to edge.",
  "eye": "What a person standing in the room actually receives. Distance in metres, standing back, across the room, from the doorway, squinting, eyesight and visual acuity, an arcminute, how much of the painting never reaches anybody at all.",
  "chi": "Handedness and mirrors. Which way the tendrils curl, chirality, the wallpaper group p4, quarter turns, reflections, whether the pattern is the same the whole way round, flipping it, turning it upside down.",
  "frac": "Whether the pattern is a fractal. Zooming in, looking closer, magnification, self-similarity, box dimension, roughness at every scale, detail all the way down, a pattern inside the pattern, going on forever.",
  "copy": "The history of the pattern and three centuries of being copied by hand. Who painted it, how old it is, where it came from, cobalt and blue and white, the onion it is named after, Meissen and China, whether it survives being reproduced again and again.",
  "ship": "How much of the tile can be replaced before it stops being this tile. Identity, what is essential about it, what makes it itself and not another pattern, the ship of Theseus, swapping and shuffling its coefficients, rebuilding it.",
  "attn": "What a machine learning model finds in the tile. Attention, transformers, neural networks, embeddings, software recognising or reading the pattern, what an AI notices and what it misses."
};
  const CHORUS = [
 "Nine tiles, one photograph. Every number on me was measured off it and not one was chosen.",
 "I am a sum of cosines. Sixty-two thousand of them, and not a single sine.",
 "There is no onion on me anywhere. I am named after one.",
 "I have quarter turns and no mirrors. In the trade that makes me p4.",
 "Most of what was painted on me has never reached anybody\u2019s eye.",
 "Fire does not preserve a pattern. It removes one, slowly, and it does not stop.",
 "Five percent of me, the right five percent, and I am a different tile.",
 "A machine can find where I repeat. It cannot find where I turn.",
 "Two hundredths of a threshold stand between my flowers and one continuous blue.",
 "I am not a fractal. Zoom in far enough and I simply run out.",
 "Three centuries of copying, and the fire won every round.",
 "Somebody measured all of this off one kitchen wall in a valley. Ask me anything."
];
  const LOOK = [
 "Watch this one.",
 "Here. Look at this one.",
 "Keep your eye on this one.",
 "This one. Watch what happens to it.",
 "That one. Go on, watch.",
 "Hold on \u2014 watch this.",
 "Look what happens to this one.",
 "This one has something to show you."
];
  const LINES = [
 [
  "cut",
  "Sixty-two thousand cosines to draw me. Most of them are dots you cannot see."
 ],
 [
  "cut",
  "Nine tenths of me is cheap. The last tenth cost three times as much, and it is dots."
 ],
 [
  "cut",
  "Somebody tried drawing me with brush strokes instead. It went badly for the strokes."
 ],
 [
  "cut",
  "Every number in me was measured. Nobody got to choose one, including me."
 ],
 [
  "cut",
  "I am cosines all the way down. Not one sine. Somebody checked."
 ],
 [
  "cut",
  "The first sixteen thousand terms get you ninety percent of me. After that you are haggling."
 ],
 [
  "cut",
  "The stroke version needed 44 466 numbers and still could not fill me in."
 ],
 [
  "cut",
  "At forty terms I am a rumour. At two hundred I am a tile. Nothing in between is worth having."
 ],
 [
  "cut",
  "Drawing me by hand takes 7 411 strokes. Drawing me with waves takes fewer numbers than that."
 ],
 [
  "cut",
  "I have no sine terms. That is not modesty, it is my four-fold centre."
 ],
 [
  "kil",
  "Fire does not preserve patterns. It removes them. Slowly, but it does not stop."
 ],
 [
  "kil",
  "One real firing barely touched me. That is the whole of my luck."
 ],
 [
  "kil",
  "Sixty firings and I am thirteen blobs. Handsome blobs, but blobs."
 ],
 [
  "kil",
  "A kiln is blur and a threshold, over and over. That is the entire trick."
 ],
 [
  "kil",
  "My outline started at 40 744 and finished at 6 210. The heat kept the change."
 ],
 [
  "kil",
  "There is no temperature at which I stop changing. There is only slower."
 ],
 [
  "kil",
  "The equation that ruins me in a kiln is the one that settles a soap film."
 ],
 [
  "kil",
  "Nobody has pinned down how far my cobalt spreads. The estimates differ by forty times."
 ],
 [
  "kil",
  "I arrived with 166 separate inked regions. Fire glued them into thirteen."
 ],
 [
  "kil",
  "Fire is patient, and it is not on my side."
 ],
 [
  "perc",
  "Two hundredths of a threshold stand between my flowers and one continuous blue."
 ],
 [
  "perc",
  "I am painted just on the safe side of that. Nobody will say whether on purpose."
 ],
 [
  "perc",
  "Push it a little further and I stop being flowers and become one shape."
 ],
 [
  "perc",
  "I am 437 separate flowers. It takes remarkably little to become one."
 ],
 [
  "perc",
  "My largest piece jumps from a tenth of me to nearly half between two clicks."
 ],
 [
  "perc",
  "The half in blue-where-f-exceeds-a-half was a decision. Somebody made it."
 ],
 [
  "perc",
  "Below one setting you could cross me from edge to edge without leaving the blue."
 ],
 [
  "perc",
  "My biggest connected piece is a tenth of me, and it is very pleased with itself."
 ],
 [
  "perc",
  "Whether my safety margin was designed or lucky cannot be settled from one tile."
 ],
 [
  "perc",
  "There is a number at which I become a single object. It is closer than it looks."
 ],
 [
  "eye",
  "From four metres you are getting a tenth of me. Enjoy the tenth."
 ],
 [
  "eye",
  "Stand thirty centimetres back and you see what the camera saw. Any further and you lose."
 ],
 [
  "eye",
  "The dots go first. The dots always go first."
 ],
 [
  "eye",
  "Most of what was measured about me never reaches anybody."
 ],
 [
  "eye",
  "At two metres, 26 129 of my 62 815 terms make it to you."
 ],
 [
  "eye",
  "At twelve metres I am 687 numbers and a blue haze."
 ],
 [
  "eye",
  "Your eye splits two lines a sixtieth of a degree apart. That is your whole allowance."
 ],
 [
  "eye",
  "You and the camera are equal at thirty centimetres. After that it is not close."
 ],
 [
  "eye",
  "These distances are generous to you. Your contrast gives out before your sharpness does."
 ],
 [
  "eye",
  "Somebody painted detail into me that nobody standing up has ever seen."
 ],
 [
  "chi",
  "I have no mirrors. My tendrils all curl the same way and they are not sorry."
 ],
 [
  "chi",
  "Force mirrors onto me and my tendrils forget which way they were going."
 ],
 [
  "chi",
  "My mirror score is the same as sliding me sideways at random. That is how I know."
 ],
 [
  "chi",
  "Quarter turns yes, reflections no. In the trade that makes me p4."
 ],
 [
  "chi",
  "Rotate me: plus fifty-four. Reflect me: eighteen, which is nothing at all."
 ],
 [
  "chi",
  "My handedness is the gap between two numbers that were allowed to disagree."
 ],
 [
  "chi",
  "Most of my curl shows up in the first fifth of that slider. The rest is showing off."
 ],
 [
  "chi",
  "Somebody measured my group before drawing anything. That order was the point."
 ],
 [
  "chi",
  "Turn me a quarter and nothing happens. Hold me to a mirror and something does."
 ],
 [
  "chi",
  "Whether a stronger curl looks more twisted was tested, could not be shown, and was kept anyway."
 ],
 [
  "frac",
  "I am not a fractal. Zoom in far enough and I just run out."
 ],
 [
  "frac",
  "Measured carelessly I look fractal. So does a curve known to be perfectly smooth."
 ],
 [
  "frac",
  "A fractal is equally rough at every zoom. I get rougher the further away you stand."
 ],
 [
  "frac",
  "There is a smallest thing on me. A fractal is not allowed one."
 ],
 [
  "frac",
  "My roughness reads 0.90 close up and 1.95 far off. A fractal would say one number twice."
 ],
 [
  "frac",
  "Somebody built a real fractal out of me, purely to check the ruler was not broken."
 ],
 [
  "frac",
  "Magnify me and hold me against myself and I do no better than a random shift."
 ],
 [
  "frac",
  "People quote 1.34 about me. It is the average of a number that will not sit still."
 ],
 [
  "frac",
  "My group has quarter turns and shifts in it. Zooming was never invited."
 ],
 [
  "frac",
  "A finite sum of cosines cannot be a fractal. You may use as many as you like."
 ],
 [
  "copy",
  "Three centuries of copying, and the fire won every round."
 ],
 [
  "copy",
  "I am named after an onion. There is no onion on me anywhere."
 ],
 [
  "copy",
  "Printed from steel, copied from a painting, copied from a Chinese bowl."
 ],
 [
  "copy",
  "Nothing here survives on its own. Somebody kept repainting me."
 ],
 [
  "copy",
  "A copyist working from memory alone did worse than no copyist at all."
 ],
 [
  "copy",
  "I lost the fruit I am named after somewhere between China and this valley."
 ],
 [
  "copy",
  "Painters took a Chinese fruit for an onion. The name has outlived the fruit by three centuries."
 ],
 [
  "copy",
  "Meissen, then Dubi, then a steel plate, then this kitchen."
 ],
 [
  "copy",
  "Give a copyist the original and I survive. Give her a memory and I do not."
 ],
 [
  "copy",
  "I kept the aster and the leaves. The peach, the bamboo and the onion never made it."
 ],
 [
  "ship",
  "Replace five percent of me, the right five, and I am somebody else."
 ],
 [
  "ship",
  "Replace ninety-five percent of my small parts and I am still me. Go on."
 ],
 [
  "ship",
  "Everything I am fits into a few dozen numbers."
 ],
 [
  "ship",
  "My spectrum looks like any pattern with edges. The signs are what make me this one."
 ],
 [
  "ship",
  "Two strangers built from my own parts resemble each other as much as they resemble me."
 ],
 [
  "ship",
  "Shuffle the signs of my biggest coefficients and I am gone in one step."
 ],
 [
  "ship",
  "My small parts are nearly free to change. My large ones are not free at all."
 ],
 [
  "ship",
  "It is not how much of me you replace. It is which."
 ],
 [
  "ship",
  "Swap my planks one at a time and there is a moment where I stop being the ship."
 ],
 [
  "ship",
  "I can lose most of myself and be recognised, or very little and not."
 ],
 [
  "attn",
  "Attention finds where I repeat. It never finds where I turn."
 ],
 [
  "attn",
  "A model looked at my patches and missed my symmetry entirely."
 ],
 [
  "attn",
  "Rotate a piece of me and the machine stops recognising it."
 ],
 [
  "attn",
  "At finding my four-fold symmetry, the machine did worse than guessing."
 ],
 [
  "attn",
  "Similarity does not survive rotation, and rotation is most of what I am."
 ],
 [
  "attn",
  "It stares at my neighbours and never once at my opposite corner."
 ],
 [
  "attn",
  "A shuffled version of me scores better on my own symmetry than I do."
 ],
 [
  "attn",
  "Finding that I repeat and finding that I turn are two different problems."
 ],
 [
  "attn",
  "Whatever a machine notices about me, my symmetry is not it."
 ],
 [
  "attn",
  "I am made of quarter turns. Quarter turns are precisely what it cannot see."
 ]
];
  const MISS = [
 "That is not on my wall.",
 "I know nine things. Not that one.",
 "No idea. I am a tile.",
 "Above my glaze.",
 "Nobody measured that.",
 "Ask the kettle.",
 "Not one of my nine.",
 "I was fired at nine hundred degrees. Some things did not survive.",
 "Try the fire, or the fractal, or who painted me.",
 "I have stood here since 1885 and I still do not know.",
 "Talking to me is talking to a brick wall.",
 "That one nobody wrote down.",
 "I only know what somebody measured.",
 "Not my department.",
 "Wrong tile.",
 "You will have to ask the wall next door."
];
  const CHAT = [
 "Cold. It is a kitchen wall.",
 "Still here. Fired once, and nothing since.",
 "Grouted. You?",
 "Somebody measured me and I have not stopped talking since.",
 "Fine. Slightly crazed in the top left corner.",
 "The same as yesterday, and the ninety years before that.",
 "Warm on this side. The other one faces the pantry.",
 "Hello. Ask me something narrow.",
 "Upright. That is most of it.",
 "Blue, mostly."
];
  const ASIDE = [
 "You are talking to a wall. I would like that on the record.",
 "This is going better than the phrase suggests.",
 "Somebody photographed me and now I have opinions.",
 "Ninety years on this wall and today is the first time anyone asked.",
 "You could be outside. There is a whole valley out there.",
 "I am a wall. You are doing most of the work in this conversation.",
 "Nine tiles and a kettle. That is the entire social circle in here.",
 "There is no polite way to put this: I am grouting.",
 "The kettle has heard all of this before.",
 "I cannot leave, so take your time.",
 "You are the first thing to happen here since the boiler.",
 "I answer, which is more than the phrase promised."
];
  const TAG = [
 "And which of us is talking to a wall here?",
 "Just so we are clear on who the wall is.",
 "You asked, remember.",
 "I did not start this.",
 "Say what you like about my conversation, I have never left the room.",
 "Anyway. You are still here.",
 "No pressure. I have got until the building comes down.",
 "That is the sort of thing you learn standing still for ninety years.",
 "Do not let me keep you.",
 "It is a strange hobby you have, but go on.",
 "I would nod, but.",
 "You may quote me. I am not going anywhere.",
 "One of us has somewhere else to be.",
 "This counts as my busiest day.",
 "The kettle disagrees, but the kettle always does.",
 "I only know nine things, and you have now heard one of them.",
 "There is more where that came from. Eight more, to be exact.",
 "Ask the tile next to me. She will say the same about herself."
];
  const WAIT = 'Fetch the two models above and I can read what you type. Until '
             + 'then I will keep talking, and every tile still comes off the wall.';
  return { THRESHOLD, DESC, LINES, MISS, CHAT, ASIDE, TAG, LOOK, CHORUS, WAIT };
})();
