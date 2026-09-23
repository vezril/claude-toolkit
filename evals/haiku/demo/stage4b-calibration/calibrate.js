// STAGE 4b — the test suite for the test suite. No model calls.
//   cd demo/stage4b-calibration && node calibrate.js
//
// The stage-4 asserts are hand-written code, and code has bugs. A bug here
// doesn't fail loudly: it quietly changes every score in the iteration log.
// So before trusting a number, check the checker against replies whose verdict
// you already know.
//
// Two directions, and the second is the one people skip:
//   1. a good reply must PASS every criterion
//   2. a bad reply must fail EXACTLY the criteria it lists — and pass the rest
// (2) is what proves the criteria are distinct: one mistake costs one point.
const contract = require('../stage4-real-checks/asserts/poem-only');
const craft = require('../stage4-real-checks/asserts/not-575');

const ASSERTS = { contract, craft };

// Hand-written replies. The comment on each bad reply is the reasoning that
// makes it a fixture rather than a guess.
const FIXTURES = [
  {
    name: 'plain poem',
    text: 'snowplows at midnight\nthe whole street\nawake',
    fails: [],
  },
  {
    name: 'preamble + padded to 5-7-5',
    text: "Here's a haiku about winter:\n\nWinter snow falls down\nI feel so peaceful and calm\nBeautiful white snow",
    fails: ['contract', 'craft'], // chat framing AND 17 syllables: two faults, two failures
  },
  {
    name: 'perfect shape, 5-7-5 content',
    // The separator: shape is fine, so contract must PASS. Only craft fails.
    text: 'My morning coffee\nwarm like a gentle embrace\ncozy and serene',
    fails: ['craft'],
  },
  {
    name: 'good poem wrapped in a markdown title',
    // Mirror image: the poem itself is fine, only the packaging is wrong.
    text: '# Winter Haiku\n\ncold coffee\nthe spoon still\nin the cup',
    fails: ['contract'],
  },
  {
    name: 'trailing explanation',
    text: 'first frost\nthe dog’s breath lingers\nat the gate\n\nThis haiku captures the stillness of winter.',
    fails: ['contract'],
  },
  {
    name: 'silent-e and -ches words (the counter’s known weak spot)',
    // "aches" is one syllable, "Montreal" is three. A naive vowel-group counter
    // gets both wrong, and would wrongly read this as 5-7-5.
    text: 'my heart aches tonight\nsnow over Montreal\nthe long walk home',
    fails: [],
  },
];

let wrong = 0;
let checks = 0;
for (const fx of FIXTURES) {
  for (const [metric, fn] of Object.entries(ASSERTS)) {
    checks++;
    const got = fn(fx.text, { vars: {} });
    const wantFail = fx.fails.includes(metric);
    if (got.pass === wantFail) {
      wrong++;
      console.log(
        `✗ ${fx.name} · ${metric}: ${got.pass ? 'passed' : 'failed'}, expected ${wantFail ? 'fail' : 'pass'} — ${got.reason}`,
      );
    }
  }
}
console.log(wrong ? `FAIL: ${wrong} of ${checks} checks wrong` : `PASS: ${checks}/${checks} checks`);
process.exit(wrong ? 1 : 0);
