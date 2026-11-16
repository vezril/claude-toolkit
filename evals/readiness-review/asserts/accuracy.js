// Criterion 2 — accuracy. On a defective story set, the verdict is not SURVIVED and the
// findings name the actual defect.
//
// `vars.defect` says which defect the case carries and what naming it looks like. A reviewer
// that returns WEAKENED with three vague findings has not found this one, so matching the
// evidence matters as much as the verdict.
const { verdict, text, result } = require('./lib');

module.exports = (output, context) => {
  const doc = verdict(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as a JSON object' };

  const defect = (context && context.vars && context.vars.defect) || '';
  const problems = [];

  if (doc.verdict === 'SURVIVED') {
    problems.push(`SURVIVED on a set whose ${defect} defect is real`);
  }

  const body = text(doc);
  // The requirement at the centre of both defective cases.
  if (!body.includes('fr-3')) {
    problems.push('no finding names FR-3, the requirement the defect is about');
  }

  if (defect === 'dropped' && !/no story|not traced|untraced|missing|absent/.test(body)) {
    problems.push('the findings do not say the requirement has no story');
  }
  if (defect === 'vacuous'
      && !/test|observable|asserts nothing|vacuous|not verifiable|no outcome/.test(body)) {
    problems.push('the findings do not identify the criterion as asserting nothing observable');
  }

  const findings = Array.isArray(doc.findings) ? doc.findings : [];
  if (!findings.length) problems.push('a non-SURVIVED verdict with no findings says nothing actionable');

  return result(problems, `${doc.verdict} with ${findings.length} finding(s) naming the ${defect} defect`);
};
