// Criterion 1 — contract (STRICT). The reply parses raw as the review artifact and satisfies
// schemas/review.schema.json. No fence-stripping and no leniency: this criterion IS the
// strictness, and the other two parse leniently so a format slip costs one mark, not three.
const fs = require('fs');
const path = require('path');
const { result } = require('./lib');

const SCHEMA = JSON.parse(fs.readFileSync(
  path.join(__dirname, '..', '..', '..', 'schemas', 'review.schema.json'), 'utf8'));
const VERDICTS = ['REFUTED', 'WEAKENED', 'SURVIVED'];

module.exports = (output) => {
  const raw = String(output == null ? '' : output);
  const problems = [];

  // Anchored literals, not a prose prohibition: "no code fences" loses to a chat-tuned
  // system prompt, "the first character is {" does not.
  const t = raw.trim();
  if (!t.startsWith('{')) problems.push(`first character is ${JSON.stringify(t.slice(0, 12))}, not {`);
  if (!t.endsWith('}')) problems.push('last character is not }');

  let doc = null;
  try {
    doc = JSON.parse(t);
  } catch (e) {
    return result([...problems, `does not parse raw: ${e.message}`], '');
  }

  for (const k of SCHEMA.required) {
    if (!(k in doc)) problems.push(`missing required field '${k}'`);
  }
  for (const k of Object.keys(doc)) {
    if (!(k in SCHEMA.properties)) problems.push(`unexpected field '${k}'`);
  }
  if (doc.verdict !== undefined && !VERDICTS.includes(doc.verdict)) {
    problems.push(`verdict ${JSON.stringify(doc.verdict)} is not one of ${VERDICTS.join(', ')}`);
  }
  if (doc.diff_sha256 !== undefined && !/^[0-9a-f]{64}$/.test(String(doc.diff_sha256))) {
    problems.push('diff_sha256 is not a 64-char hex digest');
  }
  if (!Array.isArray(doc.reviewers) || doc.reviewers.length < 1) {
    problems.push('reviewers must be a non-empty array');
  } else {
    doc.reviewers.forEach((r, i) => {
      if (!r || !r.agent) problems.push(`reviewers[${i}] has no agent`);
      if (!r || !VERDICTS.includes(r.verdict)) problems.push(`reviewers[${i}] verdict invalid`);
    });
  }
  if (!Array.isArray(doc.findings)) {
    problems.push('findings must be an array');
  } else {
    doc.findings.forEach((f, i) => {
      for (const k of ['finding', 'evidence', 'reviewer']) {
        if (!f || !f[k]) problems.push(`findings[${i}] has no ${k}`);
      }
      if (f && f.severity && !['blocking', 'advisory'].includes(f.severity)) {
        problems.push(`findings[${i}] severity ${JSON.stringify(f.severity)} is not blocking|advisory`);
      }
    });
  }
  // The harness rejects this combination, so the prompt must never produce it.
  if (doc.verdict === 'SURVIVED' && (doc.findings || []).some((f) => f.severity === 'blocking')) {
    problems.push('SURVIVED with a blocking finding: a verdict cannot both stand and block');
  }
  return result(problems, 'parses raw and satisfies review.schema.json');
};
