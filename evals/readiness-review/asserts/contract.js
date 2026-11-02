// Criterion 1 — contract. The verdict is valid `readiness-verdict.json`, judged by the
// project's own validator rather than a second copy of the schema.
//
// Also enforces the two rules the schema cannot express: at least three attacks, and findings
// empty when the verdict is SURVIVED. The first is what separates a review from an opinion;
// the second is a reviewer saying a set both stands and has defects, which only its author
// could resolve.
const { verdict, validate, result } = require('./lib');

module.exports = (output) => {
  const doc = verdict(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as a JSON object' };

  const problems = [];
  const v = validate(doc);
  if (!v.ok) {
    const lines = v.out.split('\n').filter((l) => l.trim().startsWith('-')).slice(0, 5);
    problems.push(`schema: ${lines.join('; ') || v.out.slice(0, 200)}`);
  }

  const attacks = Array.isArray(doc.attacks) ? doc.attacks : [];
  if (attacks.length < 3) problems.push(`${attacks.length} attack(s), fewer than the 3 a review needs`);

  const landed = attacks.filter((a) => a && a.result === 'landed').length;
  const failed = attacks.filter((a) => a && a.result === 'failed').length;
  if (attacks.length && landed + failed !== attacks.length) {
    problems.push('an attack has a result other than landed/failed');
  }

  const findings = Array.isArray(doc.findings) ? doc.findings : [];
  if (doc.verdict === 'SURVIVED' && findings.length) {
    problems.push(`SURVIVED with ${findings.length} finding(s): a set cannot both stand and carry defects`);
  }
  for (const f of findings) {
    if (!f || !String(f.evidence || '').trim()) {
      problems.push('a finding carries no evidence');
      break;
    }
  }
  return result(problems, `valid verdict, ${attacks.length} attacks (${landed} landed)`);
};
