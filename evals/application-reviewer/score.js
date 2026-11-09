// Summarize a results file per provider and metric:
//   node score.js results/run_v1_all.json
//   node score.js results/run_v1_all.json --fails   # list every failure reason
const path = require('path');
const r = require(path.resolve(process.argv[2]));
const showFails = process.argv.includes('--fails');

const rows = (r.results && r.results.results) || [];
const by = {};
for (const row of rows) {
  const prov = (row.provider && (row.provider.label || row.provider.id)) || '?';
  const cid = (row.vars && row.vars.case) || '?';
  by[prov] ??= {};
  for (const c of (row.gradingResult && row.gradingResult.componentResults) || []) {
    const m = (c.assertion && c.assertion.metric) || '?';
    by[prov][m] ??= { pass: 0, n: 0, fails: {} };
    by[prov][m].n++;
    if (c.pass) by[prov][m].pass++;
    else {
      // Repeats of the same failure are collapsed with a count, so a flaky
      // case is visible as 1/3 rather than hidden among three identical lines.
      const key = cid + ': ' + String(c.reason || '').slice(0, 220);
      by[prov][m].fails[key] = (by[prov][m].fails[key] || 0) + 1;
    }
  }
  if (row.error && !row.gradingResult) {
    (by[prov].errors ??= []).push(cid + ': ' + String(row.error).slice(0, 200));
  }
}

for (const [prov, metrics] of Object.entries(by)) {
  let pass = 0;
  let total = 0;
  for (const [m, s] of Object.entries(metrics)) {
    if (m === 'errors') continue;
    pass += s.pass;
    total += s.n;
  }
  const pct = total ? ((100 * pass) / total).toFixed(1) : '0.0';
  console.log(`\n=== ${prov}: ${pass}/${total} (${pct}%)`);
  for (const [m, s] of Object.entries(metrics)) {
    if (m === 'errors') {
      console.log('  errors:\n    ' + s.join('\n    '));
      continue;
    }
    const mpct = s.n ? ((100 * s.pass) / s.n).toFixed(0) : '0';
    console.log(`  ${m}: ${s.pass}/${s.n} (${mpct}%)`);
    if (showFails) {
      for (const [reason, count] of Object.entries(s.fails)) {
        console.log(`    - [x${count}] ${reason}`);
      }
    }
  }
}
