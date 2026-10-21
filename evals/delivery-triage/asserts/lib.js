const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');

function caseId(context) {
  const id = context && context.vars && context.vars.case;
  if (!id) throw new Error('test is missing vars.case');
  return id;
}
const expected = (c) => JSON.parse(fs.readFileSync(path.join(ROOT, 'expected', caseId(c) + '.json'), 'utf8'));
const input = (c) => JSON.parse(fs.readFileSync(path.join(ROOT, 'inputs', caseId(c) + '.json'), 'utf8'));

// Lenient parse for the criteria that judge content, so one formatting mistake is
// penalized once, by the schema criterion.
function parsed(output) {
  let s = String(output).trim();
  const fenced = s.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fenced) s = fenced[1].trim();
  const brace = s.indexOf('{');
  if (brace > 0) s = s.slice(brace);
  const end = s.lastIndexOf('}');
  if (end !== -1) s = s.slice(0, end + 1);
  try { return JSON.parse(s); } catch { return null; }
}

const result = (problems, ok) => problems.length
  ? { pass: false, score: 0, reason: problems.join('; ') }
  : { pass: true, score: 1, reason: ok };

module.exports = { caseId, expected, input, parsed, result, ROOT };
