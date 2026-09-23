// STAGE 4 — a craft check: is the poem padded out to 5-7-5?
//
// This reuses the suite's calibrated syllable counter (asserts/lib.js) rather
// than writing a new one. That counter was wrong on 6 of 45 hand-counted lines
// before it was fixed, and it now scores 181/181 across four sets — which is
// the point worth making out loud: you calibrate the ruler before you measure
// with it, or the number you report is just a number.
const { lenient, extractPoem, lineSyllables } = require('../../../asserts/lib');

module.exports = (output) => {
  const poem = extractPoem(lenient(output));
  if (!poem || poem.length !== 3) {
    return { pass: false, score: 0, reason: 'no 3-line poem found to measure' };
  }
  const counts = poem.map(lineSyllables);
  const total = counts.reduce((a, b) => a + b, 0);
  const shape = counts.join('-');

  if (shape === '5-7-5') {
    return { pass: false, score: 0, reason: `padded to 5-7-5 (${shape}, ${total} syllables)` };
  }
  if (total < 6 || total > 15) {
    return { pass: false, score: 0, reason: `${total} syllables (${shape}), want roughly 10-14` };
  }
  return { pass: true, score: 1, reason: `${total} syllables (${shape})` };
};
