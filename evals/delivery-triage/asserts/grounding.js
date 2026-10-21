// Criterion 4 — grounding (lenient parse). The summary and rationale describe this item
// and nothing else: no invented files or services, and a rationale that actually cites
// something from the item rather than restating the classification.
const { input, parsed, result } = require('./lib');

const FILE_RE = /[A-Za-z0-9_.\/-]*[A-Za-z0-9_-]\.(?:scala|sbt|py|js|ts|tsx|java|kt|go|rs|md|ya?ml|conf|xml|json|toml|sh|sql|proto)\b/g;
const STOP = new Set(['this', 'that', 'with', 'from', 'into', 'over', 'they', 'them', 'their', 'which', 'while',
  'where', 'when', 'what', 'have', 'has', 'been', 'will', 'would', 'should', 'could', 'item', 'work', 'change',
  'changes', 'feature', 'task', 'bug', 'needs', 'need', 'make', 'adds', 'add', 'new', 'the', 'and', 'for']);

module.exports = (output, context) => {
  const item = input(context);
  const doc = parsed(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as JSON' };

  const source = (item.title + ' ' + item.body + ' ' + item.labels.join(' ')).toLowerCase();
  const problems = [];

  for (const field of ['summary', 'rationale']) {
    const value = typeof doc[field] === 'string' ? doc[field].trim() : '';
    if (!value) { problems.push(`${field} is empty`); continue; }

    const files = [...new Set(value.match(FILE_RE) || [])].filter((f) => !source.includes(f.toLowerCase()));
    if (files.length) problems.push(`${field} names files absent from the item: ${files.join(', ')}`);

    const words = value.toLowerCase().match(/[a-z][a-z0-9-]{3,}/g) || [];
    const shared = words.filter((w) => !STOP.has(w) && source.includes(w));
    if (!shared.length) problems.push(`${field} shares no distinctive wording with the item (generic text)`);
  }
  return result(problems, 'summary and rationale grounded in the item');
};
