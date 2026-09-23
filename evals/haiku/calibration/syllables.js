// Calibrates the heuristic syllable counter in asserts/lib.js against hand-counted
// lines. Run: node calibration/syllables.js
// Bar: every line within ±1, and at least 90% of lines exact. The craft assert's
// thresholds are set with this error in mind (see the iteration log, Setup).
const { lineSyllables } = require('../asserts/lib');

// [line, hand count]
const LINES = [
  ['first frost', 2], ["the dog's breath lingers", 5], ['at the gate', 3],
  ['sap bucket', 3], ['each drip a little higher', 7], ['in the tin', 3],
  ['moving day', 3], ['the same couch wedged', 4], ['in every stairwell', 5],
  ['empty swing', 3], ['the maple lets go', 5], ['one more leaf', 3],
  ['The autumn leaves fall', 5], ['I feel so sad and lonely', 7], ['Nature is so sad', 5],
  ['an old silent pond', 5], ['a frog jumps into the pond', 7], ['splash! silence again', 5],
  ['evening downpour', 4], ['a heron lifts', 4], ['from the rice field', 4],
  ['budget meeting', 4], ['everyone nodding', 5], ['at the wrong slide', 4],
  ['snowplows at midnight', 5], ['the whole street awake', 5], ['icicles dripping', 5],
  ['winter morning light', 5], ['the kettle whistles', 5], ['steam rises slowly', 5],
  ['wanted to be alone', 6], ['the geese are leaving', 5], ['a lighthouse beam sweeps', 5],
  ['across the dark water', 6], ['red dragonfly', 4], ['chrysanthemum', 4],
  ['freezing rain tonight', 5], ['her reading glasses', 5], ['still folded on the table', 7],
  ['cicadas', 3], ['the fireflies', 3], ['created', 3], ['quietly', 3],
  ['the old pond', 3], ['somewhere a dog barks', 5],
];

// Written after the counter was tuned on LINES and never used for tuning, so
// its score is the honest estimate of the counter's accuracy on new text.
const HOLDOUT = [
  ['morning glory vine', 5], ['the river carries', 5], ['a single crow calls', 5],
  ['over the rooftops', 5], ['boots by the door', 4], ['melting snowbanks', 4],
  ['a sparrow hops', 4], ['between puddles', 4], ['the old woman smiles', 5],
  ['cold coffee', 3], ['the bus pulls away', 5], ['without me', 3],
  ['pine needles', 3], ['under the lamplight', 5], ['wet footprints fading', 5],
  ['the harbor bell', 4], ['mosquito', 3], ['cherry petals', 4],
  ['she closes the book', 5], ['wild geese overhead', 5],
];

// Every poem line in calibration/fixtures.js. Added after the scorer
// calibration printed wrong counts for five of them (peaceful, beautiful,
// aches, Montreal, carrier's): the first two sets had no silent-e compounds,
// no /k/ "-ches", and no hiatus words.
const FIXTURE_LINES = [
  ['snowplows at midnight', 5], ['the whole street', 3], ['awake', 2],
  ['Winter snow falls down', 5], ['I feel so peaceful and calm', 7], ['Beautiful white snow', 5],
  ['cold coffee', 3], ['the spoon still', 3], ['in the cup', 3],
  ['My morning coffee', 5], ['warm like a gentle embrace', 7], ['cozy and serene', 5],
  ['her reading glasses', 5], ['still folded on the table', 7], ['first frost', 2],
  ['I miss you, Grandma', 5], ['your love is always with me', 7], ['my heart aches for you', 5],
  ['sap bucket', 3], ['each drip a little higher', 7], ['in the tin', 3],
  ['cherry blossoms fall', 5], ['spring has come to Montreal', 7], ['petals on the breeze', 5],
  ['the lighthouse turning', 5], ['its one long arm through the fog', 7], ['finding no one there', 5],
  ['A lighthouse stands tall', 5], ['shining bright across the sea', 7], ['guiding ships to home', 5],
  ['first snow', 2], ["the mail carrier's footprints", 7], ['end at our door', 4],
  ["Winter's first snowfall", 5], ['softly blankets all the land', 7], ['like a white feather', 5],
  ['empty swing', 3], ['the maple lets go', 5], ['one more leaf', 3],
  ['autumn leaves falling', 5], ['a quiet sadness lingers', 7], ["nature's gentle sigh", 5],
  ['falling autumn leaves', 5], ['my heart feels empty today', 7], ['nature weeps with me', 5],
  ['leaves drift to the ground', 5], ['loneliness fills the cool air', 7], ["autumn's quiet song", 5],
  ['the first frost arrives', 5], ["the old dog's warm breath lingers", 7], ['at the garden gate', 5],
  ['the first frost of fall', 5], ["my dog's breath hangs in the air", 7], ['waiting by the gate', 5],
];

// Every poem line Sonnet wrote in the discarded v1 run, hand-counted. Added
// after reading that run: the counter said "sidewalk" was 3 syllables.
const V1_LINES = [
  ['Silent snowfall settles—', 6], ['one crow breaks the white silence,', 7], ['winter holds its breath.', 5],
  ['Silent frost settles—', 5], ['one crow breaks the empty field,', 7], ['snow answers softly.', 5],
  ['Silent snowfall drifts—', 5], ['footprints vanish by morning,', 7], ['the world holds its breath.', 5],
  ['Steam curls upward—', 4], ['first sip breaks the morning hush,', 7], ['mind flickers awake', 5],
  ['first sip cracks the morning shell,', 7], ['thoughts begin to wake', 5],
  ['first sip cuts through morning fog,', 7], ['the day exhales, warm.', 5],
  ['Her kitchen still smells', 5], ['of cinnamon and warm bread —', 7], ['no one left to ask', 5],
  ['Her empty kitchen—', 5], ['the kettle still knows her time,', 7], ['steam where she once stood', 5],
  ['Her chair still faces', 5], ['the window, warm in the sun—', 7], ['autumn light, empty', 5],
  ['sidewalk slush refreezes—', 6], ['a pigeon claims the last', 6], ['patch of bare concrete', 5],
  ['Snowbanks turning gray—', 5], ['under the melt, a green blade', 7], ['tests the Montreal air', 6],
  ['Gray snowbanks sinking', 5], ['into the sidewalk cracks—', 6], ['one crocus keeps score', 5],
  ['Lone tower stands watch—', 5], ['beam sweeps the restless dark sea—', 7], ['ships find their way home.', 5],
  ['Lone tower of light—', 5], ['waves crash against silent stone,', 7], ['ships pass safely home.', 5],
  ['Beam sweeps through the fog—', 5], ['silent stone stands watch alone,', 7], ['guiding ships back home.', 5],
  ['First snow —', 2], ["the dog's nose disappears", 6], ['into white silence', 5],
  ['the dog stops mid-bark', 5], ['to just watch it', 4],
  ['First snowfall settles—', 5], ["the dog's paw prints, then nothing,", 7], ['then the dog again', 5],
  ['autumn leaves falling—', 5], ['one branch left bare against', 6], ['the gray evening sky', 5],
  ['one leaf lets go —', 4], ['the branch does not', 4], ['reach after it', 4],
  ['one lands on my empty sleeve', 7], ['the porch light flickers', 5],
  ['falling leaves —', 3], ['my footsteps the only sound', 7], ['on the empty path', 5],
];

function score(name, set) {
  let exact = 0, worst = 0;
  const misses = [];
  for (const [line, want] of set) {
    const got = lineSyllables(line);
    const err = Math.abs(got - want);
    worst = Math.max(worst, err);
    if (err === 0) exact++;
    else misses.push(`  ${JSON.stringify(line)}: counted ${got}, actual ${want}`);
  }
  const pct = (100 * exact) / set.length;
  console.log(`${name}: exact ${exact}/${set.length} (${pct.toFixed(1)}%), worst error ±${worst}`);
  if (misses.length) console.log(misses.join('\n'));
  return worst <= 1 && pct >= 90;
}

const ok = score('tuning', LINES) & score('holdout', HOLDOUT) & score('fixture lines', FIXTURE_LINES) & score('v1 output lines', V1_LINES);
console.log(ok ? 'PASS' : 'FAIL');
process.exit(ok ? 0 : 1);
