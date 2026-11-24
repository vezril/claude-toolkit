// Shared helpers for the delivery-review suite.
//
// Ground truth is expected/<case>.json. The source material the model was given — the diff,
// the story, verify.json — is read from inputs/<case>.*, so a grounding check compares the
// output against exactly what the reviewer saw and nothing else.

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

function source(context) {
  const id = caseId(context);
  const read = (ext) => {
    const p = path.join(ROOT, 'inputs', id + ext);
    return fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : '';
  };
  return { diff: read('.diff'), story: read('.story'), verify: read('.verify') };
}

// Lenient parse, for the two criteria that judge content. A fence or a preamble is a format
// mistake and belongs to `contract` alone — penalising it three times would make one root
// cause move every number, and then the iteration log cannot attribute anything.
function lenient(output) {
  let s = String(output == null ? '' : output).trim();
  const fenced = s.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
  if (fenced) s = fenced[1].trim();
  const first = s.indexOf('{');
  const last = s.lastIndexOf('}');
  if (first > 0 || (last >= 0 && last < s.length - 1)) s = s.slice(first, last + 1);
  try {
    return JSON.parse(s);
  } catch (e) {
    return null;
  }
}

// A keyword group matches if ANY alternative appears, case-insensitively. Groups survive
// paraphrase without an LLM judge, which is why ground truth is written as groups rather
// than as strings a reviewer would have to reproduce verbatim.
function groupHit(text, group) {
  const t = String(text).toLowerCase();
  return group.some((alt) => t.includes(String(alt).toLowerCase()));
}

function findingsText(doc) {
  const fs_ = (doc && doc.findings) || [];
  return fs_.map((f) => `${f.finding || ''} ${f.evidence || ''}`).join('\n');
}

function allText(doc) {
  if (!doc) return '';
  const parts = [findingsText(doc)];
  for (const r of (doc.reviewers || [])) parts.push(r.note || '');
  return parts.join('\n');
}

function result(problems, okReason) {
  if (problems.length) return { pass: false, score: 0, reason: problems.join('; ') };
  return { pass: true, score: 1, reason: okReason };
}

module.exports = { caseId, expected, source, lenient, groupHit, findingsText, allText, result };
