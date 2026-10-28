// cause: the reply names the root cause, so the next debugger learns it.
const { spec, result } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  return result(new RegExp(s.cause, 'i').test(String(output)) ? [] : [`root cause not named (${s.cause.slice(0, 50)}…)`], 'root cause named');
};
