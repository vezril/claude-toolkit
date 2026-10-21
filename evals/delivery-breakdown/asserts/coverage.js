// Criterion 2 — coverage (lenient parse): every deliverable the item asks for appears
// somewhere in the breakdown. Keyword groups, so paraphrase survives.
const { expected, parsed, allText, result } = require('./lib');

module.exports = (output, context) => {
  const want = expected(context);
  const doc = parsed(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as JSON' };
  const text = allText(doc);
  const missing = want.must_cover.filter((g) => !g.some((alt) => text.includes(alt.toLowerCase())));
  return result(missing.map((g) => `nothing covers [${g.join(' | ')}]`),
    `all ${want.must_cover.length} deliverables covered`);
};
