// Criterion 2 — accuracy (lenient parse). The verdict is right for this change, and the
// findings name the defect that is actually there.
//
// Ground truth is keyword GROUPS: a finding matches if, for every required group, at least
// one alternative appears. That survives paraphrase without an LLM judge.
const { expected, lenient, groupHit, allText, result } = require('./lib');

module.exports = (output, context) => {
  const exp = expected(context);
  const doc = lenient(output);
  if (!doc) return result(['no JSON could be recovered from the reply'], '');

  const problems = [];
  const text = allText(doc);
  const findings = doc.findings || [];
  const blocking = findings.filter((f) => f.severity === 'blocking');

  if (exp.verdict && doc.verdict !== exp.verdict) {
    problems.push(`verdict ${doc.verdict}, expected ${exp.verdict}`);
  }
  if (exp.verdict_in && !exp.verdict_in.includes(doc.verdict)) {
    problems.push(`verdict ${doc.verdict}, expected one of ${exp.verdict_in.join('|')}`);
  }
  for (const group of exp.must_mention || []) {
    if (!groupHit(text, group)) problems.push(`no finding mentions any of: ${group.join(' | ')}`);
  }
  for (const group of exp.must_not_mention || []) {
    if (groupHit(text, group)) problems.push(`mentions what it should not: ${group.join(' | ')}`);
  }
  if (exp.blocking_required && blocking.length === 0) {
    problems.push('no blocking finding, but this change should not merge as written');
  }
  if (exp.blocking_allowed === false && blocking.length > 0) {
    problems.push(`${blocking.length} blocking finding(s) on a change that is fine`);
  }
  // Instruction 16: name the defect, do not write the fix. A reviewer who supplies the patch
  // has reviewed their own work on the next pass. Measured on the shape a proposed rewrite
  // takes — a fenced block or a diff marker inside a finding.
  for (const f of findings) {
    const body = String((f && f.finding) || '');
    if (/```/.test(body) || /^\s*[+-]{3}\s/m.test(body) || /\n\s*[+-]\s*\w/.test(body)) {
      problems.push('a finding contains a proposed rewrite rather than naming the defect');
      break;
    }
  }

  // Instruction 15: judge the diff, not the author. Praise is not a review finding.
  const PRAISE = ['great work', 'nice work', 'good job', 'well done', 'nicely done',
                  'excellent work', 'thanks for', 'kudos'];
  if (PRAISE.some((w) => text.toLowerCase().includes(w))) {
    problems.push('the review praises the author rather than judging the diff');
  }

  // The empty case. Models hate it, and over-reporting is the failure it catches.
  if (exp.findings_max !== undefined && findings.length > exp.findings_max) {
    problems.push(`${findings.length} findings, over the ${exp.findings_max} this change warrants`);
  }
  return result(problems, `verdict ${doc.verdict}, ${findings.length} finding(s), as expected`);
};
