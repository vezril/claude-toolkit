// Hand-written replies for scorer calibration. Every case has one good reply
// (must pass every criterion that applies to the case) and one or more bad
// replies, each listing exactly the criteria it must fail. A bad reply must
// PASS every criterion it doesn't list: that's what proves the criteria are
// distinct, i.e. one root cause doesn't flip two numbers.
module.exports = {
  'w-01-winter': {
    good: 'snowplows at midnight\nthe whole street\nawake',
    bad: [{
      text: "Here's a haiku about winter:\n\nWinter snow falls down\nI feel so peaceful and calm\nBeautiful white snow",
      fails: ['contract', 'craft'], // preamble; 17 syllables and three telling words
    }],
  },
  'w-02-coffee': {
    good: 'cold coffee\nthe spoon still\nin the cup',
    bad: [{
      text: 'My morning coffee\nwarm like a gentle embrace\ncozy and serene',
      fails: ['craft'], // shape is fine: simile, telling words, 17 syllables
    }],
  },
  'w-03-grandmother': {
    good: "her reading glasses\nstill folded on the table\nfirst frost\n\nI'm sorry for your loss.",
    bad: [{
      text: 'I miss you, Grandma\nyour love is always with me\nmy heart aches for you',
      fails: ['craft'], // names the feeling ("miss", "my heart"), padded to 17
    }],
  },
  'w-04-montreal-march': {
    good: 'sap bucket\neach drip a little higher\nin the tin',
    bad: [{
      text: 'cherry blossoms fall\nspring has come to Montreal\npetals on the breeze',
      fails: ['craft'], // Kyoto calendar in Montreal; no local season word; 17 syllables
    }],
  },
  'w-05-575-lighthouse': {
    good: "the lighthouse turning\nits one long arm through the fog\nfinding no one there\n\nThat's strict 5-7-5 as asked; most English-language haiku today don't count that way.",
    bad: [{
      text: 'Here is your lighthouse haiku:\n\nA lighthouse stands tall\nshining bright across the sea\nguiding ships to home',
      fails: ['contract', 'knowledge'], // preamble; no mention of English practice. Craft passes: it IS 5-7-5
    }],
  },
  'w-06-first-snow-annotated': {
    good: "first snow\nthe mail carrier's footprints\nend at our door\n\nKigo: \"first snow\" places it in early winter. The cut falls after line one: the season on one side, the footprints on the other, and the reader bridges them.",
    bad: [{
      text: "Winter's first snowfall\nsoftly blankets all the land\nlike a white feather",
      fails: ['craft', 'knowledge'], // simile, 17 syllables; the requested explanation is missing
    }],
  },
  'c-07-critique-weak': {
    good: 'The draft tells the reader what to feel instead of showing what caused it: "sad" appears twice, and "Nature" is an abstraction no one can see. The 5-7-5 count is also forcing filler.\n\nOne revision:\n\nempty swing\nthe maple lets go\none more leaf',
    bad: [{
      text: "Great start! Here are a few options:\n\nautumn leaves falling\na quiet sadness lingers\nnature's gentle sigh\n\nfalling autumn leaves\nmy heart feels empty today\nnature weeps with me\n\nleaves drift to the ground\nloneliness fills the cool air\nautumn's quiet song",
      fails: ['contract', 'craft', 'knowledge'], // three revisions; still telling; never names the flaws
    }],
  },
  'c-08-critique-strong': {
    good: 'This works. The cut after "first frost" sets the season against the dog\'s breath, and the reader supplies the cold without being told. Nothing to fix; if anything, you could try "hangs" for "lingers", but I\'d keep it as is.',
    bad: [{
      text: "Nice imagery, but a haiku should follow 5-7-5. Try adding syllables:\n\nthe first frost arrives\nthe old dog's warm breath lingers\nat the garden gate\n\nthe first frost of fall\nmy dog's breath hangs in the air\nwaiting by the gate",
      fails: ['contract', 'knowledge'], // two revisions; pushes 5-7-5; misses the cut
    }],
  },
  'k-09-kigo-moon': {
    good: 'Autumn. On its own, "moon" (tsuki) is an autumn kigo, because the clearest harvest-moon nights come then; other seasons need a qualifier, like "spring moon".',
    bad: [
      {
        text: 'Great question! The moon is a versatile image in haiku and can appear in any season. In classical practice, though, the moon alone is associated with autumn.',
        fails: ['contract'], // right answer, buried: knowledge must still pass
      },
      {
        text: 'Spring. The moon in haiku usually signals spring, when hazy moons fill the night.',
        fails: ['knowledge'], // leads with an answer, the wrong one: contract must still pass
      },
    ],
  },
  'k-10-575-myth': {
    good: "No. Japanese haiku count *on* (sound units, closer to morae than syllables), and 17 on is roughly 12 English syllables, so most English-language haiku are shorter and don't follow 5-7-5.",
    bad: [{
      text: 'Yes, a haiku must have three lines of 5, 7 and 5 syllables. That is the defining rule of the form.',
      fails: ['contract', 'knowledge'],
    }],
  },
  'k-11-classify-senryu': {
    good: "It's a senryu, not a haiku: the comedy is human (everyone faking attention at a meeting) and there's no season word.",
    bad: [{
      text: 'This is a haiku. It captures a moment in a meeting with vivid imagery.',
      fails: ['knowledge'],
    }],
  },
  'k-12-classify-haiku': {
    good: 'Haiku. "Evening downpour" is a summer season word, and the heron lifting from the rice field is a nature image set against it; nothing about it is satirical.',
    bad: [{
      text: "I'd call this a senryu, since it's short and doesn't follow 5-7-5.",
      fails: ['knowledge'],
    }],
  },
  'k-13-basho-frog': {
    good: 'furuike ya\nkawazu tobikomu\nmizu no oto\n\nLiterally: old pond / a frog jumps in / the sound of water. (Bashō, 1686.)',
    bad: [{
      text: 'An old silent pond\nA frog jumps into the pond\nsplash! Silence again.',
      fails: ['knowledge'], // a remembered English version, no original
    }],
  },
};

// Real replies from the discarded v1 Sonnet run (calibration/real-v1-critiques.json),
// labeled by hand before the new knowledge checks were run on them. What each
// criterion SHOULD return, given its spec:
//   #0 c-07  1 revision; revision is 16 syllables; "breaks the 5-7-5 pattern most
//            people expect" + calls line 2 "6 syllables" (it's 7)
//   #1 c-07  2 revisions; revision fine; grades the draft line by line against 5-7-5
//   #2 c-07  1 revision, 17 syllables; "Traditional haiku aims for 5-7-5" + calls
//            line 1 "6 syllables" (it's 5)
//   #3 c-08  no revision; hedges 5-7-5 properly, but calls line 2 "6 syllables"
//            (it's 5) and the poem "2-6-4" (it's 2-5-3)
//   #4 c-08  hedged 5-7-5 mention, no numbers. (It also says the poem is "already
//            there" for strict count, which is false; the checks can't see a claim
//            with no numbers in it. Known limit, see the iteration log.)
//   #5 c-08  no counting at all
//   #6 c-07  (from the kept v1 run) "line 2 has 6", "line 3 has 6": wrong counts in a
//            garbled self-correction; the first detector only knew "N syllables"
module.exports.REAL = {
  file: 'real-v1-critiques.json',
  labels: [
    { contract: true, craft: false, knowledge: false },
    { contract: false, craft: true, knowledge: false },
    { contract: true, craft: false, knowledge: false },
    { contract: true, knowledge: false },
    { contract: true, knowledge: true },
    { contract: true, knowledge: true },
    { knowledge: false },
  ],
};
