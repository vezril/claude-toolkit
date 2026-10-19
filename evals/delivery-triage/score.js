// Summarize a results file per provider and metric: node score.js results/run_v1_all.json
const r = require(require('path').resolve(process.argv[2]));
const rows = (r.results && r.results.results) || [];
const by = {};
for (const row of rows) {
  const prov = (row.provider && (row.provider.label || row.provider.id)) || '?';
  const cid = row.vars && row.vars.case;
  for (const c of (row.gradingResult && row.gradingResult.componentResults) || []) {
    const m = (c.assertion && c.assertion.metric) || '?';
    by[prov] ??= {}; by[prov][m] ??= { pass: 0, n: 0, fails: [] };
    by[prov][m].n++; if (c.pass) by[prov][m].pass++; else by[prov][m].fails.push(cid + ': ' + c.reason);
  }
  if (row.error && !row.gradingResult) { by[prov] ??= {}; (by[prov].errors ??= []).push(cid + ': ' + String(row.error).slice(0, 160)); }
}
for (const [prov, ms] of Object.entries(by)) {
  let P = 0, N = 0;
  for (const [m, s] of Object.entries(ms)) if (m !== 'errors') { P += s.pass; N += s.n; }
  console.log(`\n=== ${prov}: ${P}/${N} (${N ? (100 * P / N).toFixed(1) : 0}%)`);
  for (const [m, s] of Object.entries(ms)) {
    if (m === 'errors') { console.log('  errors:\n    ' + s.join('\n    ')); continue; }
    console.log(`  ${m}: ${s.pass}/${s.n}`); for (const f of s.fails) console.log('    - ' + f);
  }
}
