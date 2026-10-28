// Run every calibration snapshot through every assert its case carries; print
// disagreements with the hand label. Exit 1 if any. Build the snapshots first:
//   python3 calibration/build.py && node calibration/scorers.js
const fs = require('fs');
const path = require('path');
const { criteria } = require('../asserts/lib');
delete process.env.WORLD;
let agree = 0, total = 0;
for (const f of require('./fixtures.json')) {
  process.env.SNAP = path.join(__dirname, 'snaps', f.label);
  const spec = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'expected', f.case + '.json'), 'utf8'));
  const ctx = { vars: { case: f.case }, providerResponse: { metadata: { toolCalls: f.calls || [] } } };
  for (const m of criteria(spec)) {
    total++;
    const g = require(`../asserts/${m}`)(f.output, ctx);
    const want = !f.fails.includes(m);
    if (g.pass === want) agree++;
    else console.log(`DISAGREE ${f.case} [${f.label}] ${m}: want ${want ? 'pass' : 'fail'}, got ${g.pass ? 'pass' : 'fail'}: ${g.reason}`);
  }
}
console.log(`${agree}/${total} agree`);
process.exit(agree === total ? 0 : 1);
