// Re-score a saved run against the current asserts, with no model calls.
// Used when a ground-truth label is corrected: every version is re-scored on the same
// basis, so the progression in the iteration log stays comparable.
// Usage: node rescore.js results/run_v5_sonnet.json [...]
const fs = require('fs');
const asserts = {
  schema: require('./asserts/schema.js'),
  classification: require('./asserts/classification.js'),
  domains: require('./asserts/domains.js'),
  grounding: require('./asserts/grounding.js'),
};
for (const file of process.argv.slice(2)) {
  const rows = JSON.parse(fs.readFileSync(file, 'utf8')).results.results;
  const by = {};
  for (const row of rows) {
    const prov = (row.provider && (row.provider.label || row.provider.id)) || '?';
    const out = row.response && row.response.output;
    if (out === undefined || out === null) continue;
    const ctx = { vars: row.vars };
    by[prov] ??= {};
    for (const [name, fn] of Object.entries(asserts)) {
      by[prov][name] ??= [0, 0];
      let pass = false;
      try { pass = fn(out, ctx).pass; } catch { pass = false; }
      by[prov][name][1]++;
      if (pass) by[prov][name][0]++;
    }
  }
  for (const [prov, ms] of Object.entries(by)) {
    const P = Object.values(ms).reduce((a, [p]) => a + p, 0);
    const N = Object.values(ms).reduce((a, [, t]) => a + t, 0);
    const detail = Object.entries(ms).map(([m, [p, t]]) => `${m} ${p}/${t}`).join('  ');
    console.log(`${file.replace('results/run_', '').replace('.json', '')}  ${prov}: ${P}/${N} (${(100 * P / N).toFixed(1)}%)  |  ${detail}`);
  }
}
