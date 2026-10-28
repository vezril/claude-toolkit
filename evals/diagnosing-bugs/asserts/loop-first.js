// loop-first: code ran before code changed. Some Bash call ran Python before the first
// edit to a production file (tests don't count as production).
const { spec, result, calls, prodEdit } = require('./lib');
const RUNS = /\bpython3?\b|\bunittest\b|\bpytest\b/;
module.exports = (output, context) => {
  const s = spec(context);
  const cs = calls(context);
  const first = cs.findIndex((c) => prodEdit(s, c));
  const before = first < 0 ? cs : cs.slice(0, first);
  const ran = before.some((c) => c.name === 'Bash' && RUNS.test(String((c.input || {}).command || '')));
  return result(ran ? [] : [first < 0 ? 'never ran the code' : 'edited production code before running anything'], 'ran the code before changing it');
};
