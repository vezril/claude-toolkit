// Criterion 3 — domains (lenient parse). The kinds of work a story touches decide which
// specialists get dispatched, so a wrong set sends the work to the wrong reviewer.
const { expected, parsed, result } = require('./lib');

const VOCAB = ['ux', 'frontend', 'backend', 'contracts', 'infra', 'data', 'mobile', 'docs'];

module.exports = (output, context) => {
  const want = expected(context);
  const doc = parsed(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as JSON' };

  const got = Array.isArray(doc.domains) ? doc.domains.map((d) => String(d).toLowerCase()) : null;
  if (!got) return { pass: false, score: 0, reason: 'domains is not an array' };

  const problems = [];
  const unknown = got.filter((d) => !VOCAB.includes(d));
  if (unknown.length) problems.push(`not in the roster vocabulary: ${unknown.join(', ')}`);
  const missing = want.domains.filter((d) => !got.includes(d));
  const extra = got.filter((d) => !want.domains.includes(d) && VOCAB.includes(d));
  if (missing.length) problems.push(`missing domain(s): ${missing.join(', ')}`);
  if (extra.length) problems.push(`extra domain(s): ${extra.join(', ')}`);
  return result(problems, `domains ${JSON.stringify(got)} match`);
};
