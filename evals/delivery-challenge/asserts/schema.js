// Criterion 1 — schema (strict): raw JSON conforming to challenge.schema.json, checked by
// the same validate-artifact.py the edge hook runs. The verdict enum and the three-attack
// floor are in the schema, so a reply that argues instead of reporting fails here.
const { execFileSync } = require('child_process');
const fs = require('fs'); const os = require('os'); const path = require('path');
const { result, ROOT } = require('./lib');

module.exports = (output) => {
  const problems = []; const text = String(output);
  if (text.trim() !== text) problems.push('output has leading or trailing whitespace');
  if (!text.trim().startsWith('{')) problems.push('does not start with { (preamble or code fence)');
  if (/```/.test(text)) problems.push('contains a code fence');

  let doc = null;
  try { doc = JSON.parse(text); } catch (e) { problems.push('not raw JSON: ' + e.message); }

  if (doc) {
    const tmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'ch-')), 'challenge-breakdown.json');
    fs.writeFileSync(tmp, JSON.stringify(doc));
    try {
      execFileSync('python3', [path.join(ROOT, '..', '..', 'scripts', 'delivery-flow', 'validate-artifact.py'),
        tmp, '--schema', 'challenge-breakdown.json'], { encoding: 'utf8' });
    } catch (e) {
      const rep = (e.stdout || e.message).split('\n').filter((l) => l.trim().startsWith('-'))
        .map((l) => l.trim().slice(2));
      problems.push(...(rep.length ? rep.slice(0, 4) : ['schema validation failed']));
    }
  }
  return result(problems, 'raw JSON conforming to challenge.schema.json');
};
