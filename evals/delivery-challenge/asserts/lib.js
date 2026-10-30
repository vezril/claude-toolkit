const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');

const caseId = (c) => {
  const id = c && c.vars && c.vars.case;
  if (!id) throw new Error('test is missing vars.case');
  return id;
};
const read = (dir, name) => JSON.parse(fs.readFileSync(path.join(ROOT, dir, name), 'utf8'));
const expected = (c) => read('expected', caseId(c) + '.json');
const item = (c) => read('inputs', caseId(c) + '.item.json');
const triage = (c) => read('inputs', caseId(c) + '.triage.json');
const breakdown = (c) => read('inputs', caseId(c) + '.breakdown.json');

// Lenient parse for the criteria that judge content, so one formatting mistake is
// penalized once, by the schema criterion.
function parsed(output) {
  let s = String(output).trim();
  const fenced = s.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fenced) s = fenced[1].trim();
  const b = s.indexOf('{');
  if (b > 0) s = s.slice(b);
  const e = s.lastIndexOf('}');
  if (e !== -1) s = s.slice(0, e + 1);
  try { return JSON.parse(s); } catch { return null; }
}

// Everything the challenge said, lowercased: findings and the attack log together, because
// a hole named in an attack's result is still a hole named.
const findingsText = (doc) => (doc.findings || [])
  .map((f) => `${f.finding || ''} ${f.evidence || ''}`).join(' \u0000 ').toLowerCase();
const allText = (doc) => JSON.stringify(doc).toLowerCase();

const result = (problems, ok) => problems.length
  ? { pass: false, score: 0, reason: problems.join('; ') }
  : { pass: true, score: 1, reason: ok };

module.exports = { caseId, expected, item, triage, breakdown, parsed, findingsText, allText, result, ROOT };
