// Criterion 1 — schema (strict). The output IS a triage artifact: raw JSON, no fence,
// no preamble, conforming to schemas/triage.schema.json. The check shells out to the
// same validate-artifact.py the edge hook runs, so the eval gates on production code.
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { caseId, result, ROOT } = require('./lib');

module.exports = (output, context) => {
  const problems = [];
  const text = String(output);
  if (text.trim() !== text) problems.push('output has leading or trailing whitespace');
  if (!text.trim().startsWith('{')) problems.push('does not start with { (preamble or code fence)');
  if (/```/.test(text)) problems.push('contains a code fence');

  let doc = null;
  try { doc = JSON.parse(text); } catch (e) { problems.push('not raw JSON: ' + e.message); }

  if (doc) {
    const tmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'triage-')), 'triage.json');
    fs.writeFileSync(tmp, JSON.stringify(doc));
    try {
      execFileSync('python3', [path.join(ROOT, '..', '..', 'scripts', 'delivery-flow', 'validate-artifact.py'),
        tmp, '--schema', 'triage.json'], { encoding: 'utf8' });
    } catch (e) {
      const report = (e.stdout || e.message).split('\n').filter((l) => l.trim().startsWith('-'))
        .map((l) => l.trim().slice(2));
      problems.push(...(report.length ? report : ['schema validation failed']));
    }
  }
  return result(problems, 'raw JSON conforming to triage.schema.json');
};
