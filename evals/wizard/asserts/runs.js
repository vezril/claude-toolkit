// runs: driven like a person would (drive.py, yes to every yes/no), the script runs to
// completion against stub tools.
const { spec, result, script, run } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const sc = script(output);
  if (!sc) return result(['no script found'], '');
  const r = run(sc, 'y', s.setup);
  if (r.timedOut) return result([`never finished (timed out or looped on one prompt): "${r.tail.slice(-100)}"`], '');
  return result(r.code === 0 ? [] : [`exit ${r.code}: "${r.tail.slice(-120)}"`], 'ran to completion');
};
