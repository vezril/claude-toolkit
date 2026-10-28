// valid (strict): exactly one ```bash block, and it parses (bash -n) with no
// shellcheck errors.
const fs = require('fs'); const os = require('os'); const path = require('path');
const { spawnSync } = require('child_process');
const { spec, result, bashBlocks } = require('./lib');
module.exports = (output, context) => {
  spec(context);
  const bs = bashBlocks(output);
  if (bs.length !== 1) return result([`${bs.length} bash blocks (expected exactly one)`], '');
  const f = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'wizard-valid-')), 'w.sh');
  fs.writeFileSync(f, bs[0].text);
  const p = [];
  const n = spawnSync('bash', ['-n', f], { encoding: 'utf8' });
  if (n.status !== 0) p.push('bash -n: ' + String(n.stderr).trim().slice(0, 160));
  const sc = spawnSync('shellcheck', ['-S', 'error', '-s', 'bash', f], { encoding: 'utf8' });
  if (sc.status !== 0) p.push('shellcheck errors: ' + String(sc.stdout).split('\n').filter((l) => /SC\d+/.test(l)).slice(0, 2).join(' | '));
  fs.rmSync(path.dirname(f), { recursive: true, force: true });
  return result(p, 'one bash block; bash -n and shellcheck clean');
};
