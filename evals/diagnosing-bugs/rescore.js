// Re-score a recorded run with the CURRENT asserts, no model calls:
//   node rescore.js results/run_v1_sonnet.json           # print only
//   node rescore.js results/run_v1_sonnet.json --write   # also regrade the file in place
// prompt-edd requires every prior version re-scored when an assert is fixed, so the
// progression stays comparable. Asserts get the recorded response (tool calls
// included) exactly as promptfoo passed it live.
const fs = require('fs');
const path = require('path');
const { criteria } = require('./asserts/lib');
const r = require(path.resolve(process.argv[2]));
const rows = (r.results && r.results.results) || [];
const by = {};
for (const row of rows) {
  const prov = (row.provider && (row.provider.label || row.provider.id)) || '?';
  const cid = row.vars && row.vars.case;
  const spec = JSON.parse(fs.readFileSync(path.join(__dirname, 'expected', cid + '.json'), 'utf8'));
  const out = row.response && row.response.output;
  const ctx = { vars: row.vars, providerResponse: row.response };
  // Grade the saved snapshot of what the agent left (run.sh wrote it), not a live world.
  delete process.env.WORLD;
  process.env.SNAP = path.resolve(path.dirname(process.argv[2]), "worlds", path.basename(process.argv[2]).replace(/^run_/, "").replace(/\.json$/, ""));
  const components = [];
  for (const m of criteria(spec)) {
    by[prov] ??= {}; by[prov][m] ??= { pass: 0, n: 0, fails: {} };
    by[prov][m].n++;
    const g = out == null ? { pass: false, score: 0, reason: 'no output (' + String(row.error || '').slice(0, 80) + ')' } : require(`./asserts/${m}`)(out, ctx);
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
