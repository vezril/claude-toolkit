// Run every calibration reply through every assert its case carries; print
// disagreements with the hand label. Exit 1 if any. (Replies built by hand from the template, with its line-114 shellcheck error
// braced away, in fixtures.json.)
const fs = require('fs');
const path = require('path');
const { criteria } = require('../asserts/lib');
let agree = 0, total = 0;
for (const f of require('./fixtures.json')) {
  const spec = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'expected', f.case + '.json'), 'utf8'));
  for (const m of criteria(spec)) {
    total++;
    const g = require(`../asserts/${m}`)(f.output, { vars: { case: f.case } });
    const want = !f.fails.includes(m);
    if (g.pass === want) agree++;
    else console.log(`DISAGREE ${f.case} [${f.label}] ${m}: want ${want ? 'pass' : 'fail'}, got ${g.pass ? 'pass' : 'fail'}: ${g.reason}`);
  }
}
console.log(`${agree}/${total} agree`);
process.exit(agree === total ? 0 : 1);
