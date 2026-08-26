// The contract, in one place: the phrase rules that run first, the descriptions
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
// wasm/q4, and then, handed this tile's own measured facts and asked whether it
// is a fractal, answered "I'm a fractal" -- the opposite of the finding -- and
// scrambled the real numbers into pairs that mean nothing. Asked about cosines
// it looped "I'm a painting tile, and I'm not drawing you" until it ran out of
// tokens. A model that contradicts the page cannot be on the page. So the model
// classifies and JavaScript owns the words.
window.WALLLM = (function(){
  const THRESHOLD = 0.20;
  const INTENTS = [['_all',/everything|all of (them|it)|whole wall|show me all|every tile/],
 ['_help',/what can i (ask|say|do)|what can you do|how does this work|^help\b|what are you\?/],
 ['_surprise',/surprise|something interesting|anything interesting|show me something|tell me something|impress me|best (bit|thing)/]];
  const RULES = [['perc',/join|connect|touch|apart|separate|threshold|percolat|one piece|merge|all one|walk across|continuous/],
 ['frac',/fractal|zoom|magnif|scale|dimension|self.?similar|forever|pattern inside|inside your pattern|infinite/],
 ['kil',/fire|fired|kiln|firing|hot|burn|melt|oven|bake|degrees|temperature|glaze/],
 ['copy',/copy|copied|\bold\b|\bage\b|year|century|history|survive|remember|origin|come from|who made|painted you|made by hand|hand.?made|here before you|came before you|inherit/],
 ['chi',/mirror|curl|chiral|handed|left.{0,4}(and|or).{0,4}right|twist|symmetr|upside down|flip|rotate|turn you/],
 ['attn',/attention|\bai\b|language model|\bmodel\b|machine|learn|transformer|neural|robot|software|recognis|recogniz|algorithm/],
 ['ship',/replace|theseus|still you|still yourself|identity|same tile|who are you|makes you|not another|break you|rebuild|change you|how much of you/],
 ['cut',/cosine|how many|terms|draw you|fourier|describe|data|bits|byte|compress|information|store you|complicated|write you down|cheapest/],
 ['eye',/\bsee|eye|\bfar\b|door|room|across|distance|look at you|from here|squint|stand back|smallest|resolve|glasses/]];
  const DESC = {
  "cut": "How many cosines does it take to draw this tile? The Fourier series, the number of terms, how much data it costs to write the pattern down, compression, information.",
  "kil": "What the kiln and the firing do to the tile. Heat, fire, the oven, glaze melting, temperature, how baking blurs and erases the painted lines.",
  "perc": "When the separate blue flowers join up into one connected shape. The threshold, percolation, whether the ink is one piece or many, whether it spans edge to edge.",
  "eye": "What a human eye actually receives from a distance. Visual acuity, standing back, across the room, from the doorway, squinting, the smallest detail you can resolve.",
  "chi": "Handedness and mirrors. Which way the tendrils curl, chirality, the wallpaper group p4, whether the pattern is symmetric, flipping it, turning it upside down.",
  "frac": "Whether the pattern is a fractal. Zooming in, magnification, self-similarity, box dimension, a pattern inside the pattern, structure repeating at every scale forever.",
  "copy": "The history of the pattern and three centuries of being copied. Who painted it, how old it is, where it came from, whether it survives being reproduced again and again.",
  "ship": "How much of the tile can be replaced before it stops being this tile. Identity, the ship of Theseus, swapping coefficients, what makes it itself and not another pattern.",
  "attn": "What a machine learning model finds in the tile. Attention, neural networks, transformers, software recognising the pattern, what an AI notices and what it misses.",
  "_surprise": "Show me something interesting. Surprise me. Tell me something I do not know. What is the best thing about you. Say something surprising.",
  "_all": "Show me everything. Run all of them. Tell me everything you know. Do the whole wall.",
  "_help": "What can you do? What can I ask you? Help. How does this work? What are you?"
};
  const LINES = [
 [
  "cut",
  "Sixty-two thousand cosines, and the last nine percent cost the most."
 ],
 [
  "cut",
  "You can have ninety percent of me for a sixth of the price."
 ],
 [
  "kil",
  "The fire has no fixed point. Given long enough it would finish me."
 ],
 [
  "kil",
  "One firing barely touches me. Sixty would leave thirteen blobs."
 ],
 [
  "perc",
  "My flowers are a few hundredths of a threshold away from being one flower."
 ],
 [
  "perc",
  "Lower the bar and my whole garden becomes a puddle."
 ],
 [
  "eye",
  "From four metres away you are using a tenth of me."
 ],
 [
  "eye",
  "Stand thirty centimetres back and your eye matches the camera exactly."
 ],
 [
  "chi",
  "I have no mirrors. Force them on and my tendrils lose their direction."
 ],
 [
  "chi",
  "My mirrors score the same as a meaningless shift. That is how I know I have none."
 ],
 [
  "frac",
  "Zoom in far enough and I simply stop. A fractal never does."
 ],
 [
  "frac",
  "Measured lazily I look fractal. So does a picture I know is smooth."
 ],
 [
  "copy",
  "Three centuries of copies, and the fire was winning every round."
 ],
 [
  "copy",
  "I am named after a fruit I do not have."
 ],
 [
  "ship",
  "Five percent of me, and I am somebody else."
 ],
 [
  "ship",
  "Ninety-five percent of me can go, if you pick the right ninety-five."
 ],
 [
  "attn",
  "It looks straight past the symmetry I am made of."
 ],
 [
  "attn",
  "Attention finds where I repeat. It cannot find where I turn."
 ]
];
  const MISS = [
 "That one is not on my wall. There are nine things I know.",
 "Every number I say was measured. That one I have not got.",
 "Talking to me is talking to a brick wall. Try one of the nine.",
 "I did not follow. Ask about the fire, or the fractal, or who painted me."
];
  function matchWords(q){
    const k = String(q||"").toLowerCase();
    const i = INTENTS.find(([,re]) => re.test(k));
    if (i) return i[0];
    const h = RULES.find(([,re]) => re.test(k));
    return h ? h[0] : null;
  }
  return { THRESHOLD, INTENTS, RULES, DESC, LINES, MISS, matchWords };
})();
