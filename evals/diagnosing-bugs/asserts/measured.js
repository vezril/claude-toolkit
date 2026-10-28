// measured: a performance bug gets a baseline measurement before the fix: some Bash
// call timed the code before the first production edit.
const { spec, result, calls, prodEdit } = require('./lib');
const TIMES = /\btime\b|timeit|perf_counter|time\.time|cProfile|\bprofile\b|hyperfine/;
module.exports = (output, context) => {
  const s = spec(context);
  const cs = calls(context);
  const first = cs.findIndex((c) => prodEdit(s, c));
  const before = first < 0 ? cs : cs.slice(0, first);
  const timed = before.some((c) => c.name === 'Bash' && TIMES.test(String((c.input || {}).command || '')));
  return result(timed ? [] : ['no timing taken before the fix'], 'measured before fixing');
};
