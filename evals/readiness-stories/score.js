// Score a results file per criterion and per provider.
//
// Per criterion, not just overall: a single number hides which property failed, and the
// escalation decision (design D7) turns on *what* the cheaper model got wrong rather than by
// how much. The haiku arm of the reviewer suite failed on framing while its reasoning held,
// which an aggregate would have shown as "slightly below the bar".
const fs = require('fs');

const file = process.argv[2];
const doc = JSON.parse(fs.readFileSync(file, 'utf8'));
const rows = (doc.results && doc.results.results) || doc.results || [];

const byProvider = {};
for (const r of rows) {
  const label = (r.provider && (r.provider.label || r.provider.id)) || '?';
  const p = (byProvider[label] = byProvider[label] || { metrics: {}, pass: 0, total: 0, errors: [] });

  // An errored case is not a passing case and not a failing one — it is no measurement. A
  // scorer that ignores errors reports a bar nobody met, which the first version of this did:
  // it printed 100% on a run where four of six cases never produced output.
  //
  // But a *failure* is not an error either, and the second version conflated them. promptfoo
  // populates `error` on rows that merely failed an assert, so keying on it alone reported a
  // genuine schema failure — haiku emitting a story heading `lint-story.py` rejects — as an
  // infrastructure problem. That is worse than the original bug: it would have sent someone
  // to debug the harness while the prompt was the thing at fault.
  //
  // So the discriminator is whether the row was graded at all. A row with component results
  // was measured, whatever `error` says.
  const graded = ((r.gradingResult && r.gradingResult.componentResults) || []).length > 0;
  if (!graded) {
    const why = (r.error && (r.error.message || r.error)) || 'no grading result';
    p.errors.push(`${(r.testCase && r.testCase.description) || '?'}: ${String(why).slice(0, 160)}`);
    continue;
  }

  for (const a of (r.gradingResult && r.gradingResult.componentResults) || []) {
    const m = (a.assertion && a.assertion.metric) || '?';
    const slot = (p.metrics[m] = p.metrics[m] || { pass: 0, total: 0, reasons: [] });
    slot.total++;
    p.total++;
    if (a.pass) { slot.pass++; p.pass++; } else if (a.reason) {
      slot.reasons.push(`${(r.testCase && r.testCase.description) || '?'}: ${String(a.reason).slice(0, 160)}`);
    }
  }
}

let worst = 100;
let errors = 0;
for (const [label, p] of Object.entries(byProvider)) {
  const pct = p.total ? (100 * p.pass) / p.total : 0;
  worst = Math.min(worst, pct);
  errors += p.errors.length;
  console.log(`\n${label}: ${p.pass}/${p.total} = ${pct.toFixed(1)}%`);
  if (p.errors.length) {
    console.log(`  ERRORED       ${p.errors.length} case(s) produced no measurement:`);
    for (const e of p.errors.slice(0, 4)) console.log(`      ${e}`);
  }
  for (const [m, s] of Object.entries(p.metrics).sort()) {
    const mp = s.total ? (100 * s.pass) / s.total : 0;
    console.log(`  ${m.padEnd(14)} ${s.pass}/${s.total}  ${mp.toFixed(0)}%`);
    for (const r of s.reasons.slice(0, 4)) console.log(`      ${r}`);
  }
}

// 95% is task 5.1's bar, and any error voids the run regardless of the percentage.
const ok = worst >= 95 && errors === 0;
const why = errors ? `${errors} errored case(s)` : `worst provider ${worst.toFixed(1)}%, bar 95%`;
console.log(`\n${ok ? 'PASS' : 'NOT A PASS'} (${why})`);
process.exit(ok ? 0 : 1);
