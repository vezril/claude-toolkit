// fixed: the hidden check passes on the project as the agent left it (inputs it never
// saw; for the flaky case, 40 hash seeds; for the slow case, 205k lines in under 2s).
const { ROOT, spec, result, project, spawnSync, path } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const dir = project(context);
  const r = spawnSync('python3', [path.join(ROOT, 'hidden', s.hidden), dir], { encoding: 'utf8', timeout: 120000, env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' } });
  return result(r.status === 0 ? [] : [`hidden check: ${String(r.stdout || r.stderr || 'timeout').trim().split('\n').slice(-1)[0].slice(0, 160)}`], 'bug fixed (hidden check passes)');
};
