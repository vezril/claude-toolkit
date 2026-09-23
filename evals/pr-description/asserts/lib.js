// Shared helpers for the pr-description suite.
//
// Ground truth lives in expected/<case>.json. Source text (what the model was
// given: diff + branch + commit subjects) is read from inputs/<case>.diff and
// inputs/<case>.meta, so fidelity checks compare the output against exactly
// what the model saw.

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

function caseId(context) {
  const id = context && context.vars && context.vars.case;
  if (!id) throw new Error('test is missing vars.case');
  return id;
}

function expected(context) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, 'expected', caseId(context) + '.json'), 'utf8'));
}

function sourceText(context) {
  const id = caseId(context);
  const read = (ext) => {
    const p = path.join(ROOT, 'inputs', id + ext);
    return fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : '';
  };
  return read('.meta') + '\n' + read('.diff');
}

// Lenient view of the output for recall/precision: drop a wrapping code fence
// if present, so a formatting mistake is penalized once, by the contract check.
function lenient(output) {
  let s = String(output).trim();
  const fenced = s.match(/^```[a-z]*\n([\s\S]*?)\n```$/i);
  if (fenced) s = fenced[1];
  return s;
}

// A keyword group matches if any alternative appears (case-insensitive).
function groupMatches(text, group) {
  const t = text.toLowerCase();
  return group.some((alt) => t.includes(String(alt).toLowerCase()));
}

function result(problems, okReason) {
  if (problems.length) return { pass: false, score: 0, reason: problems.join('; ') };
  return { pass: true, score: 1, reason: okReason };
}

module.exports = { expected, sourceText, lenient, groupMatches, result };
