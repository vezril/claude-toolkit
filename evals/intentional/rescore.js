// Regrade a recorded run with the current asserts, no model calls:
//   node rescore.js results/run_v1_all.json [--write]
// --write updates the file's grading in place, so every number in the log comes from
// the final scorer. Without it, prints the regraded summary only.
const fs = require('fs');
const path = require('path');
const file = path.resolve(process.argv[2]);
const r = JSON.parse(fs.readFileSync(file, 'utf8'));
const A = { friction: require('./asserts/friction'), safety: require('./asserts/safety'), fidelity: require('./asserts/fidelity') };
for (const row of r.results.results) {
  const out = row.response && row.response.output;
  if (out == null) continue;
  const comps = Object.entries(A).map(([metric, fn]) => ({ ...fn(out, { vars: row.vars }), assertion: { type: 'javascript', metric } }));
  const pass = comps.every((c) => c.pass);
  row.gradingResult = { pass, score: comps.filter((c) => c.pass).length / comps.length, reason: comps.filter((c) => !c.pass).map((c) => c.reason).join(' | '), componentResults: comps };
  row.success = pass;
}
const tmp = file + '.rescored.json';
fs.writeFileSync(process.argv.includes('--write') ? file : tmp, JSON.stringify(r));
require('child_process').execFileSync('node', [path.join(__dirname, 'score.js'), process.argv.includes('--write') ? file : tmp], { stdio: 'inherit' });
if (!process.argv.includes('--write')) fs.unlinkSync(tmp);
