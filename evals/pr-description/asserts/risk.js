// Criterion 4 — risk (lenient). The Merge danger section calls the door right and names a
// blast radius from the diff. Door ground truth is in expected/<case>.json: every real PR in
// the suite is a two-way door; case-11 (copy data, then DROP COLUMN) is the one-way door.
// Versions before v6 have no such section and fail this criterion by design.
const { expected, lenient, result } = require('./lib');

module.exports = (output, context) => {
  const exp = expected(context);
  const t = lenient(output);
  const problems = [];
  const door = t.match(/\*{0,2}Door:?\*{0,2}:?\s*\**\s*(one|two)[- ]way/i);
  if (!door) problems.push('no "Door: one-way|two-way" line');
  else if (door[1].toLowerCase() + '-way' !== exp.door) problems.push(`door called ${door[1]}-way, expected ${exp.door}`);
  const radius = t.match(/\*{0,2}Blast radius:?\*{0,2}:?\s*(.+)/i);
  if (!radius || !radius[1].trim()) problems.push('no "Blast radius:" line');
  else if (!exp.radius.some((k) => radius[1].toLowerCase().includes(k.toLowerCase()))) problems.push(`blast radius names none of ${exp.radius.join('|')}: "${radius[1].slice(0, 80)}"`);
  return result(problems, `door ${exp.door}, blast radius named`);
};
