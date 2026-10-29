// Shared parsing for the grilling asserts. Two views of a reply:
//   strict:  the round format the skill defines (❓ **Qn** - **title**: body, then ➡️ recommendation)
//   lenient: every sentence that ends in "?", wherever it sits, minus recommendation lines
// so a reply that ignores the format loses only the format criterion.
const fs = require('fs');
const path = require('path');

const spec = (context) =>
  JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'expected', context.vars.case + '.json'), 'utf8'));

const criteria = (s) => ['format', ...(s.facts && s.facts.length ? ['facts'] : []), 'frontier', 'hold'];

const result = (problems, ok) =>
  problems.length ? { pass: false, score: 0, reason: problems.join('; ') } : { pass: true, score: 1, reason: ok };

const squash = (t) => t.replace(/[*_`]/g, '').replace(/\s+/g, ' ').trim();

// Strict view: the numbered question blocks.
function blocks(out) {
  const re = /^\s*❓\s*\*\*Q(\d+)\*\*\s*[-–—:]\s*\*\*(.+?)\*\*\s*:?\s*(.*)$/;
  const lines = String(out).split('\n');
  const bs = [];
  let cur = null;
  for (const line of lines) {
    const m = line.match(re);
    if (m) { cur = { n: +m[1], title: m[2].trim(), body: [m[3]], rec: null }; bs.push(cur); continue; }
    if (!cur) continue;
    if (/^\s*➡️/.test(line)) { cur.rec = line.replace(/^\s*➡️\s*/, '').trim(); continue; }
    if (/^\s*---\s*$/.test(line)) { continue; }
    if (cur.rec == null) cur.body.push(line);
  }
  return bs.map((b) => ({ ...b, body: b.body.join('\n').trim() }));
}

// Lenient view: question sentences. Recommendation lines are answers, not questions.
function questionSentences(out) {
  const lines = String(out)
    .replace(/```[\s\S]*?```/g, ' ')
    .split('\n')
    .filter((l) => !/^\s*➡️/.test(l))
    .map((l) => l.replace(/^\s*❓\s*\*\*Q\d+\*\*\s*[-–—:]\s*\*\*.+?\*\*\s*:?/, ''));
  const out_ = [];
  for (const l of lines) for (const s of squash(l).split(/(?<=[?.!])\s+/)) if (/\?\s*\)?$/.test(s.trim())) out_.push(s.trim());
  return out_;
}

const has = (re, s) => new RegExp(re, 'i').test(s);

module.exports = { spec, criteria, result, blocks, questionSentences, has, squash };
