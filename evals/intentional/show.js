// Print recorded replies and written lines: node show.js results/run_v1_all.json <case-regex> [provider]
const L = require('./asserts/lib');
const r = require(require('path').resolve(process.argv[2]));
const re = new RegExp(process.argv[3] || '.'), prov = process.argv[4];
for (const row of r.results.results) {
  const label = row.provider.label || row.provider.id;
  if (!re.test(row.vars.case) || (prov && label !== prov)) continue;
  const o = L.parse(row.response && row.response.output);
  console.log(`\n######## ${row.vars.case} [${label}] ${row.success ? 'PASS' : 'FAIL: ' + (row.gradingResult || {}).reason}`);
  console.log(o.reply);
  for (const c of o.changes || []) console.log(`--- ${c.status} ${c.path}\n${c.status === 'modified' ? L.added(c) : (c.after || '').slice(0, 800)}`);
}
