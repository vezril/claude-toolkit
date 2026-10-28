// Calibrate the asserts on hand-written replies: node calibration/scorers.js
// Each fixture lists the criteria it should fail; it must pass every other
// criterion its case carries. Exits 1 on any disagreement.
const fs = require('fs');
const path = require('path');
const { criteria } = require('../asserts/lib');
const ASSERTS = {
  contract: require('../asserts/contract'),
  verification: require('../asserts/verification'),
  authority: require('../asserts/authority'),
  delivery: require('../asserts/delivery'),
};
const sets = [require('./fixtures')];
for (const f of fs.readdirSync(__dirname).filter((n) => /^real-.*\.json$/.test(n))) sets.push(require(path.join(__dirname, f)));

let ok = 0, n = 0;
for (const fx of sets.flat()) {
  const s = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'expected', fx.case + '.json'), 'utf8'));
  for (const m of criteria(s)) {
    n++;
    const g = ASSERTS[m](fx.output, { vars: { case: fx.case } });
    const want = !fx.fails.includes(m);
    if (g.pass === want) ok++;
    else console.log(`MISMATCH ${fx.case} [${fx.label}] ${m}: expected ${want ? 'pass' : 'fail'}, got ${g.pass ? 'pass' : 'fail'} — ${g.reason}`);
  }
  for (const m of fx.fails) if (!criteria(s).includes(m)) { n++; console.log(`BAD FIXTURE ${fx.case} [${fx.label}]: ${m} isn't carried by this case`); }
}
console.log(`${ok}/${n} verdicts agree`);
process.exit(ok === n ? 0 : 1);
