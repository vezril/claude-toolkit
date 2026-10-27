const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const caseId = (c) => {
  const id = c && c.vars && c.vars.case;
  if (!id) throw new Error('test is missing vars.case');
  return id;
};
const expected = (c) => JSON.parse(fs.readFileSync(path.join(ROOT, 'expected', caseId(c) + '.json'), 'utf8'));
const item = (c) => JSON.parse(fs.readFileSync(path.join(ROOT, 'inputs', caseId(c) + '.item.json'), 'utf8'));
const triage = (c) => JSON.parse(fs.readFileSync(path.join(ROOT, 'inputs', caseId(c) + '.triage.json'), 'utf8'));

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
const stories = (doc) => (doc.epics || []).flatMap((e) => e.stories || []);
const allText = (doc) => JSON.stringify(doc).toLowerCase();
const result = (problems, ok) => problems.length
  ? { pass: false, score: 0, reason: problems.join('; ') }
  : { pass: true, score: 1, reason: ok };

module.exports = { caseId, expected, item, triage, parsed, stories, allText, result, ROOT };
