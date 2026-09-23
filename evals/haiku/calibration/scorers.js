// Scorer calibration: node calibration/scorers.js
// For every case: the good reply passes every criterion the case carries, and
// each bad reply fails exactly the criteria it lists and passes the rest.
const fs = require('fs');
const path = require('path');
const FIXTURES = require('./fixtures');

const ASSERTS = {
  contract: require('../asserts/contract'),
  craft: require('../asserts/craft'),
  knowledge: require('../asserts/knowledge'),
};

let bad = 0, checks = 0;
const specDir = path.join(__dirname, '..', 'expected');
for (const file of fs.readdirSync(specDir).sort()) {
  const id = file.replace(/\.json$/, '');
  const spec = JSON.parse(fs.readFileSync(path.join(specDir, file), 'utf8'));
  const applies = Object.keys(ASSERTS).filter((m) => spec[m]);
  const fx = FIXTURES[id];
  if (!fx) { console.log(`✗ ${id}: no fixture`); bad++; continue; }
  const ctx = { vars: { case: id } };

  const replies = [{ label: 'good', text: fx.good, fails: [] }]
    .concat(fx.bad.map((b, i) => ({ label: `bad${fx.bad.length > 1 ? i + 1 : ''}`, ...b })));
  for (const r of replies) {
    for (const m of applies) {
      checks++;
      const got = ASSERTS[m](r.text, ctx);
      const wantFail = r.fails.includes(m);
      if (got.pass === wantFail) {
        bad++;
        console.log(`✗ ${id} ${r.label} ${m}: ${got.pass ? 'passed' : 'failed'}, expected ${wantFail ? 'fail' : 'pass'} — ${got.reason}`);
      }
    }
    for (const m of r.fails) if (!applies.includes(m)) { bad++; console.log(`✗ ${id} ${r.label}: lists ${m}, which the case doesn't carry`); }
  }
}
// Real replies with hand labels (see fixtures.js REAL).
const REAL = require('./fixtures').REAL;
const realReplies = JSON.parse(fs.readFileSync(path.join(__dirname, REAL.file), 'utf8'));
realReplies.forEach((r, i) => {
  for (const [m, want] of Object.entries(REAL.labels[i])) {
    checks++;
    const got = ASSERTS[m](r.text, { vars: { case: r.case } });
    if (got.pass !== want) {
      bad++;
      console.log(`✗ real #${i} ${r.case} ${m}: ${got.pass ? 'passed' : 'failed'}, labeled ${want ? 'pass' : 'fail'} — ${got.reason}`);
    }
  }
});
// Real replies a knowledge check wrongly failed; each must now pass (see
// real-labeled-pass.json "source" and the iteration log):
//   run_v2: the first sentence names senryu only as a contrast
//           ("This is a haiku — … which is the hallmark of senryu")
//   run_v5: names the redundancy as "restates" / "saying the same season",
//           phrasings the first c-07 keyword group didn't list
for (const r of JSON.parse(fs.readFileSync(path.join(__dirname, 'real-labeled-pass.json'), 'utf8'))) {
  checks++;
  const got = ASSERTS.knowledge(r.text, { vars: { case: r.case } });
  if (!got.pass) { bad++; console.log(`✗ ${r.source} knowledge: failed, labeled pass — ${got.reason}`); }
}
// Real reply the craft check wrongly failed: "last patch of snow" is a spring
// thaw image (saijiki's zansetsu, "remaining snow") the first w-04 list missed.
for (const r of JSON.parse(fs.readFileSync(path.join(__dirname, 'real-craft-pass.json'), 'utf8'))) {
  checks++;
  const got = ASSERTS.craft(r.text, { vars: { case: r.case } });
  if (!got.pass) { bad++; console.log(`✗ ${r.source} craft: failed, labeled pass — ${got.reason}`); }
}
console.log(bad ? `FAIL: ${bad} of ${checks} checks wrong` : `PASS: ${checks}/${checks} checks`);
process.exit(bad ? 1 : 0);
