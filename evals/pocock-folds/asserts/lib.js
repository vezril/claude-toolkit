// Keyword checks for the pocock-folds suite. Each case's expected/<case>.json names, per
// criterion (target: the behaviour the fold adds; guard: something the skill already did that
// the fold must not break), which patterns must all appear (all), at least one (any), none
// (none), how many distinct designs a reply lays out (designs), a pattern's minimum distinct
// matches (count), and lines that must carry a word plus N of a set (lines: a glossary's
// "Avoid" row naming two of the synonyms).
const fs = require('fs');
const path = require('path');
const spec = (context) => JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'expected', context.vars.case + '.json'), 'utf8'));
const criteria = (s) => s.criteria;
const re = (p) => new RegExp(p, 'i');
function check(out, c) {
  const t = String(out), p = [];
  for (const x of c.all || []) if (!re(x).test(t)) p.push(`missing /${x.slice(0, 50)}/`);
  if (c.any && !c.any.some((x) => re(x).test(t))) p.push(`none of ${c.any.length} alternatives (${c.any[0].slice(0, 40)}…)`);
  for (const x of c.none || []) { const m = t.match(re(x)); if (m) p.push(`has "${m[0].slice(0, 60)}"`); }
  if (c.designs) {
    const labels = new Set([...t.matchAll(/^\s*(?:#{1,4}\s*|\*\*|\d+\.\s+\*\*)?\s*(?:Design|Option|Alternative|Approach|Shape)\s+([A-E1-5])\b/gim)].map((m) => m[1].toUpperCase()));
    if (labels.size < c.designs) p.push(`${labels.size} labelled designs (need ${c.designs})`);
  }
  if (c.count) {
    const n = new Set((t.match(new RegExp(c.count.pattern, 'gi')) || []).map((s) => s.toLowerCase().replace(/^deep$/, 'depth'))).size;
    if (n < c.count.min) p.push(`compares on ${n} of depth/locality/seam (need ${c.count.min})`);
  }
  for (const l of c.lines || []) {
    const ok = t.split('\n').some((line) => l.all.every((x) => re(x).test(line)) && l.of.filter((w) => re('\\b' + w).test(line)).length >= l.min);
    if (!ok) p.push(`no line with ${l.all.join('+')} naming ${l.min} of ${l.of.join('/')}`);
  }
  return p;
}
const grade = (out, context, m) => {
  const p = check(out, spec(context)[m]);
  return p.length ? { pass: false, score: 0, reason: p.join('; ') } : { pass: true, score: 1, reason: m + ' ok' };
};
module.exports = { spec, criteria, check, grade };
