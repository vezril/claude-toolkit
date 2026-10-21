// Criterion 4 — scope (lenient parse). The breakdown is of THIS item: the right key, story
// domains drawn from what triage found, nothing invented, and a size a person can review.
const { expected, item, triage, parsed, stories, result } = require('./lib');

const FILE_RE = /[A-Za-z0-9_.\/-]*[A-Za-z0-9_-]\.(?:scala|sbt|py|js|ts|tsx|java|kt|go|rs|md|ya?ml|conf|xml|json|toml|sh|sql|proto)\b/g;
const VOCAB = ['ux', 'frontend', 'backend', 'contracts', 'infra', 'data', 'mobile', 'docs'];

module.exports = (output, context) => {
  const doc = parsed(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as JSON' };
  const it = item(context); const tr = triage(context);
  const source = (it.title + ' ' + it.body).toLowerCase();
  const problems = [];

  if (doc.item !== it.key) problems.push(`item is ${JSON.stringify(doc.item)}, expected ${JSON.stringify(it.key)}`);

  const all = stories(doc);
  if (all.length < 2) problems.push(`${all.length} story: a breakdown of one story is not a breakdown`);
  if (all.length > 12) problems.push(`${all.length} stories: too granular to review`);

  for (const s of all) {
    const ds = (s.domains || []).map((d) => String(d).toLowerCase());
    const bad = ds.filter((d) => !VOCAB.includes(d));
    if (bad.length) problems.push(`${s.id}: domains not in the vocabulary: ${bad.join(', ')}`);
    const outside = ds.filter((d) => VOCAB.includes(d) && !tr.domains.includes(d));
    if (outside.length) problems.push(`${s.id}: domain(s) triage did not find: ${outside.join(', ')}`);
  }

  const files = [...new Set(JSON.stringify(doc).match(FILE_RE) || [])]
    .filter((f) => !source.includes(f.toLowerCase()));
  if (files.length) problems.push(`names files absent from the item: ${files.slice(0, 3).join(', ')}`);

  return result(problems.slice(0, 4), `${all.length} stories, domains within triage's, nothing invented`);
};
