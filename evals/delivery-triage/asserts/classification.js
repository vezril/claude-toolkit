// Criterion 2 — classification (lenient parse). The decisions the rest of the flow
// branches on: item type, path, and the three policy flags that drive punch-outs.
const { expected, input, parsed, result } = require('./lib');

module.exports = (output, context) => {
  const want = expected(context);
  const item = input(context);
  const doc = parsed(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as JSON' };

  const problems = [];
  if (doc.item !== item.key) problems.push(`item is ${JSON.stringify(doc.item)}, expected ${JSON.stringify(item.key)}`);
  for (const field of ['type', 'path', 'handoff', 'architecture_change', 'breaking_change']) {
    if (doc[field] !== want[field]) {
      problems.push(`${field} is ${JSON.stringify(doc[field])}, expected ${JSON.stringify(want[field])} (${want.note})`);
    }
  }
  return result(problems, `type=${doc.type} path=${doc.path} and all three flags correct`);
};
