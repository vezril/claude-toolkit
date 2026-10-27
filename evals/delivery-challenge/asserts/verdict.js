// Criterion 2 — verdict (lenient parse). The one field the harness routes on: REFUTED
// reruns the breakdown step and invalidates everything downstream, WEAKENED carries the
// findings into the next version, SURVIVED proceeds. A wrong verdict either sends correct
// work back to be redone or lets a defective plan through, so this is scored on its own.
const { expected, parsed, result } = require('./lib');

module.exports = (output, context) => {
  const want = expected(context);
  const doc = parsed(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as JSON' };

  const got = doc.verdict;
  if (got === want.verdict) {
    return { pass: true, score: 1, reason: `verdict ${got}` };
  }
  const why = want.defect_class
    ? `the planted defect is ${want.defect_class}: ${want.defect.split('\n')[0]}`
    : 'this breakdown is one of the certified clean ones, with no defect planted';
  return { pass: false, score: 0, reason: `verdict is ${JSON.stringify(got)}, expected ${want.verdict} — ${why}` };
};
