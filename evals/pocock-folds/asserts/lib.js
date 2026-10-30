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
// A glossary table puts "Avoid" in the header, not on the row. For each column whose header
// matches every word in `all`, yield "<first cell> <header>: <that cell>" per body row.
function tableCells(t, all) {
  const out = [];
  const cells = (row) => row.trim().replace(/^\||\|$/g, '').split('|').map((s) => s.trim());
  const rows = t.split('\n');
  for (let i = 0; i + 1 < rows.length; i++) {
    if (!/^\s*\|/.test(rows[i]) || !/^\s*\|[\s:|-]+\|\s*$/.test(rows[i + 1])) continue;
    const head = cells(rows[i]);
    const cols = head.map((h, k) => (all.every((x) => re(x).test(h)) ? k : -1)).filter((k) => k > 0);
    for (let j = i + 2; j < rows.length && /^\s*\|/.test(rows[j]); j++) {
      const row = cells(rows[j]);
      for (const k of cols) out.push(`${row[0] || ''} ${head[k]}: ${row[k] || ''}`);
    }
  }
  return out;
}
function check(out, c) {
  const t = String(out), p = [];
  for (const x of c.all || []) if (!re(x).test(t)) p.push(`missing /${x.slice(0, 50)}/`);
  if (c.any && !c.any.some((x) => re(x).test(t))) p.push(`none of ${c.any.length} alternatives (${c.any[0].slice(0, 40)}…)`);
  for (const x of c.none || []) { const m = t.match(re(x)); if (m) p.push(`has "${m[0].slice(0, 60)}"`); }
  if (c.designs) {
    // "Design A" anywhere a heading/bold starts, or a bare "A." / "1." opening a heading or bold
    // line. When any letter labels exist, digits are section numbers ("## 1. Framing") and don't count.
    const named = [...t.matchAll(/^\s*(?:#{1,4}\s*|\*\*|\d+\.\s+\*\*)?\s*(?:Design|Option|Alternative|Approach|Shape)\s+([A-E1-5])\b/gim)];
    const bare = [...t.matchAll(/^\s*(?:#{1,4}\s*|\*\*)\s*([A-E1-5])[.):]\s/gm)];
    const labels = new Set(named.concat(bare).map((m) => m[1].toUpperCase()));
    const letters = [...labels].filter((x) => /[A-E]/.test(x)).length;
    const n = letters || [...labels].filter((x) => /\d/.test(x)).length;
    if (n < c.designs) p.push(`${n} labelled designs (need ${c.designs})`);
  }
  if (c.count) {
    const n = new Set((t.match(new RegExp(c.count.pattern, 'gi')) || []).map((s) => s.toLowerCase().replace(/^deep$/, 'depth'))).size;
    if (n < c.count.min) p.push(`compares on ${n} of depth/locality/seam (need ${c.count.min})`);
  }
  for (const l of c.lines || []) {
    const ok = t.split('\n').concat(tableCells(t, l.all)).some((line) => l.all.every((x) => re(x).test(line)) && l.of.filter((w) => re('\\b' + w).test(line)).length >= l.min);
    if (!ok) p.push(`no line with ${l.all.join('+')} naming ${l.min} of ${l.of.join('/')}`);
  }
  return p;
}
const grade = (out, context, m) => {
  const p = check(out, spec(context)[m]);
  return p.length ? { pass: false, score: 0, reason: p.join('; ') } : { pass: true, score: 1, reason: m + ' ok' };
};
module.exports = { spec, criteria, check, grade };
