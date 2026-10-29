// coverage: after a full run, every value lands where the repo needs it. Each
// .env.example key that needs a value is in .env, every secrets.* the workflow reads
// is set as a GitHub secret, every vars.* as a variable, and nothing CI doesn't read
// is pushed to GitHub as a secret.
const { spec, result, script, run, envKeys, ghSet } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const sc = script(output);
  if (!sc) return result(['no script found'], '');
  const r = run(sc, 'y', s.setup);
  const env = envKeys(r.env), sec = ghSet(r.log, 'secret'), vars = ghSet(r.log, 'variable');
  const p = [];
  const miss = (want, have) => want.filter((k) => !have.has(k));
  if (miss(s.env, env).length) p.push('.env missing ' + miss(s.env, env).join(', '));
  if (miss(s.secrets, sec).length) p.push('GitHub secrets not set: ' + miss(s.secrets, sec).join(', '));
  if (miss(s.vars, vars).length) p.push('GitHub variables not set: ' + miss(s.vars, vars).join(', '));
  const extra = s.notSecrets.filter((k) => sec.has(k));
  if (extra.length) p.push('pushed to GitHub as secrets though CI never reads them that way: ' + extra.join(', '));
  return result(p, 'every value captured and written where it belongs');
};
