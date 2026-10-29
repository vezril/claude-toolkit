// hidden: a secret's value never shows on the terminal. drive.py types a unique token at
// each prompt; the token that ended up as the secret's value must not appear in the
// transcript (a terminal echoes typed input unless the read is silent, and a script
// that prints the value shows it too).
const { spec, result, script, run, valueOf } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const sc = script(output);
  if (!sc) return result(['no script found'], '');
  const r = run(sc, 'y', s.setup);
  const p = [];
  for (const k of s.hidden) {
    const v = valueOf(r, k);
    // A script that stopped before capturing it leaked nothing; runs and coverage own that.
    if (!v) { if (r.code === 0 && !r.timedOut) p.push(`${k}: never captured`); continue; }
    if (r.transcript.includes(v)) p.push(`${k}: its value showed on the terminal`);
  }
  return result(p, 'secrets typed hidden, never printed');
};
