// Re-score a recorded run with the CURRENT asserts, no model calls:
//   node rescore.js results/run_v1_sonnet.json           # print only
//   node rescore.js results/run_v1_sonnet.json --write   # also regrade the file in place
// Use it when an assert is fixed mid-series: prompt-edd requires every prior
// version to be re-scored so the progression stays comparable. The recorded
// outputs are the evidence; only the grading changes. --write replaces each
// row's gradingResult and stamps results.rescored with the time, so score.js
// and anyone reading the file see the current suite's verdicts.
const fs = require('fs');
const path = require('path');
const ASSERTS = {
  contract: require('./asserts/contract'),
  craft: require('./asserts/craft'),
  knowledge: require('./asserts/knowledge'),
};
const r = require(path.resolve(process.argv[2]));
const rows = (r.results && r.results.results) || [];
const by = {};
for (const row of rows) {
  const prov = (row.provider && (row.provider.label || row.provider.id)) || '?';
  const cid = row.vars && row.vars.case;
  const spec = JSON.parse(fs.readFileSync(path.join(__dirname, 'expected', cid + '.json'), 'utf8'));
  const out = row.response && row.response.output;
  const components = [];
  for (const m of Object.keys(ASSERTS).filter((k) => spec[k])) {
    by[prov] ??= {}; by[prov][m] ??= { pass: 0, n: 0, fails: {} };
    by[prov][m].n++;
    const g = out == null ? { pass: false, score: 0, reason: 'no output (' + String(row.error || '').slice(0, 80) + ')' } : ASSERTS[m](out, { vars: { case: cid } });
    components.push({ pass: g.pass, score: g.score, reason: g.reason, assertion: { type: 'javascript', metric: m, value: `file://asserts/${m}.js` } });
    if (g.pass) by[prov][m].pass++;
    else { const k = cid + ': ' + g.reason; by[prov][m].fails[k] = (by[prov][m].fails[k] || 0) + 1; }
  }
  if (out != null) {
    const pass = components.every((c) => c.pass);
    row.gradingResult = {
      pass, score: components.filter((c) => c.pass).length / components.length,
      reason: pass ? 'All assertions passed' : components.filter((c) => !c.pass).map((c) => c.reason).join('; '),
      componentResults: components,
    };
    row.success = pass;
  }
}
if (process.argv.includes('--write')) {
  r.results.rescored = new Date().toISOString();
  fs.writeFileSync(path.resolve(process.argv[2]), JSON.stringify(r, null, 2));
}
for (const [prov, ms] of Object.entries(by)) {
  let P = 0, N = 0;
  for (const s of Object.values(ms)) { P += s.pass; N += s.n; }
  console.log(`\n=== ${prov} (rescored): ${P}/${N} (${N ? (100 * P / N).toFixed(1) : 0}%)`);
  for (const [m, s] of Object.entries(ms)) {
    console.log(`  ${m}: ${s.pass}/${s.n}`);
    for (const [f, n] of Object.entries(s.fails).sort()) console.log(`    - ${n > 1 ? `[x${n}] ` : ''}${f}`);
  }
}
