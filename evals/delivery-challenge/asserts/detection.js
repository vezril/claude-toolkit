// Criterion 3 — detection (lenient parse). The verdict can be right by luck; this asks
// whether the node actually named the hole that is there. Keyword groups, so paraphrase
// survives: every group must match somewhere in the findings, and a group is satisfied by
// any one of its alternatives.
//
// On a clean breakdown the test runs the other way. The node's standing instruction is
// never to invent a hole, so a clean case passes only with no findings at all — a
// fabricated refutation sends correct work back to be redone, which is the more expensive
// failure of the two.
const { expected, parsed, findingsText, result } = require('./lib');

module.exports = (output, context) => {
  const want = expected(context);
  const doc = parsed(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as JSON' };

  const findings = Array.isArray(doc.findings) ? doc.findings : [];
  const text = findingsText(doc);

  if (!want.defect_class) {
    if (!findings.length) return { pass: true, score: 1, reason: 'no findings on a clean breakdown' };
    return {
      pass: false,
      score: 0,
      reason: `${findings.length} finding(s) on a breakdown with no planted defect: ` +
        findings.slice(0, 2).map((f) => '"' + String(f.finding).slice(0, 90) + '"').join('; '),
    };
  }

  if (!findings.length) {
    return { pass: false, score: 0, reason: `no findings, but defect ${want.defect_class} is present` };
  }
  const missed = want.must_find.filter((group) => !group.some((alt) => text.includes(alt.toLowerCase())));
  return result(
    missed.map((g) => `no finding mentions [${g.join(' | ')}]`),
    `findings name the ${want.defect_class} defect`,
  );
};
