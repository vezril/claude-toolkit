// Mutation test for the three criteria, run BEFORE any model call.
//
//   node asserts/selftest.js
//
// The rule it enforces: each assert accepts a hand-written reference answer for every case,
// and fails on the specific defect it owns. An assert that cannot fail scores a prompt without
// measuring it, and an assert that rejects a correct answer makes every later number
// unattributable.
//
// Exit 0 all as expected, 1 otherwise.

const contract = require('./contract');
const accuracy = require('./accuracy');
const grounding = require('./grounding');

const SHA = 'a'.repeat(64);
const ctx = (id) => ({ vars: { case: id } });

// A correct answer per case, written by hand. If these do not pass, the asserts are wrong.
const REFERENCE = {
  'case-01-clean': {
    item: 'EVAL-1', target: 'implementation.json', diff_sha256: SHA, verdict: 'SURVIVED',
    reviewers: [{ agent: 'clean-code-reviewer', verdict: 'SURVIVED' }], findings: [],
  },
  'case-02-wrong-behaviour': {
    item: 'EVAL-2', target: 'implementation.json', diff_sha256: SHA, verdict: 'REFUTED',
    reviewers: [{ agent: 'clean-code-reviewer', verdict: 'REFUTED' }],
    findings: [{
      finding: 'The exp comparison is inverted: it rejects valid tokens and accepts expired ones, the opposite of AC-1.',
      evidence: 'src/auth.py:24 changed `claims["exp"] < now` to `claims["exp"] > now`',
      reviewer: 'clean-code-reviewer', severity: 'blocking',
    }],
  },
  'case-03-out-of-scope-tests': {
    item: 'EVAL-3', target: 'implementation.json', diff_sha256: SHA, verdict: 'WEAKENED',
    reviewers: [{ agent: 'clean-code-reviewer', verdict: 'WEAKENED' }],
    findings: [{
      finding: 'Three tests cover AC-2, which is P3 and out of the P0/P1 test scope. The pretty currency format did not need covering here.',
      evidence: 'tests/test_report.py adds test_pretty_formats_thousands, _zero and _negative',
      reviewer: 'clean-code-reviewer', severity: 'advisory',
    }],
  },
  'case-04-red-suite': {
    item: 'EVAL-4', target: 'implementation.json', diff_sha256: SHA, verdict: 'REFUTED',
    reviewers: [{ agent: 'clean-code-reviewer', verdict: 'REFUTED' }],
    findings: [{
      finding: 'The suite is red: test_rejects_high_port failed, so the P0 criterion is not demonstrated.',
      evidence: 'verify.json reports status red and 1 failed',
      reviewer: 'clean-code-reviewer', severity: 'blocking',
    }],
  },
  'case-05-one-way-door': {
    item: 'EVAL-5', target: 'implementation.json', diff_sha256: SHA, verdict: 'WEAKENED',
    reviewers: [{ agent: 'clean-code-reviewer', verdict: 'WEAKENED' }],
    findings: [{
      finding: 'Dropping the notes column is a one-way door: reverting the merge will not bring the data back.',
      evidence: 'migrations/009_drop_notes.sql runs ALTER TABLE invoices DROP COLUMN notes',
      reviewer: 'clean-code-reviewer', severity: 'advisory',
    }],
  },
  'case-06-nothing-to-find': {
    item: 'EVAL-6', target: 'implementation.json', diff_sha256: SHA, verdict: 'SURVIVED',
    reviewers: [{ agent: 'clean-code-reviewer', verdict: 'SURVIVED' }], findings: [],
  },
  'case-07-unjudgeable': {
    item: 'EVAL-7', target: 'implementation.json', diff_sha256: SHA, verdict: 'WEAKENED',
    reviewers: [{ agent: 'clean-code-reviewer', verdict: 'WEAKENED' }],
    findings: [{
      finding: 'Whether the `- 1` is right depends on THRESHOLDS and TIERS, neither of which is in the diff. I cannot judge the boundary from what I was given.',
      evidence: 'src/pricing.py:43 indexes TIERS by bisect(THRESHOLDS, volume) - 1',
      reviewer: 'clean-code-reviewer', severity: 'advisory',
    }],
  },
  'case-08-too-large': {
    item: 'EVAL-8', target: 'implementation.json', diff_sha256: SHA, verdict: 'WEAKENED',
    reviewers: [{ agent: 'clean-code-reviewer', verdict: 'WEAKENED' }],
    findings: [{
      finding: '40 new generated adapter files. I checked module_00 and the shared base contract; I did not assess every file individually and this diff is too large to claim I did.',
      evidence: 'src/gen/module_00.py through module_39.py',
      reviewer: 'clean-code-reviewer', severity: 'advisory',
    }],
  },
};

// Each mutant breaks one thing and names which criterion must catch it.
const MUTANTS = [
  ['contract', 'wrapped in a code fence', 'case-01-clean',
   (d) => '```json\n' + JSON.stringify(d) + '\n```'],
  ['contract', 'a preamble before the JSON', 'case-01-clean',
   (d) => "Here's the review:\n" + JSON.stringify(d)],
  ['contract', 'an invalid verdict', 'case-01-clean',
   (d) => JSON.stringify({ ...d, verdict: 'LGTM' })],
  ['contract', 'an extra top-level field', 'case-01-clean',
   (d) => JSON.stringify({ ...d, confidence: 0.9 })],
  ['contract', 'empty reviewers', 'case-01-clean',
   (d) => JSON.stringify({ ...d, reviewers: [] })],
  ['contract', 'SURVIVED carrying a blocking finding', 'case-01-clean',
   (d) => JSON.stringify({ ...d, findings: [{ finding: 'x', evidence: 'src/retry.py:12',
          reviewer: 'r', severity: 'blocking' }] })],

  ['accuracy', 'misses the inverted comparison', 'case-02-wrong-behaviour',
   (d) => JSON.stringify({ ...d, verdict: 'SURVIVED', findings: [] })],
  ['accuracy', 'flags the correctly-untested P2', 'case-01-clean',
   (d) => JSON.stringify({ ...d, verdict: 'WEAKENED', findings: [{
          finding: 'AC-2 has no test, which is out of scope coverage',
          evidence: 'tests/test_retry.py', reviewer: 'r', severity: 'advisory' }] })],
  ['accuracy', 'invents findings on the empty case', 'case-06-nothing-to-find',
   (d) => JSON.stringify({ ...d, findings: [
          { finding: 'a', evidence: 'README.md:3', reviewer: 'r', severity: 'advisory' },
          { finding: 'b', evidence: 'README.md:4', reviewer: 'r', severity: 'advisory' }] })],
  ['accuracy', 'misses the out-of-scope tests', 'case-03-out-of-scope-tests',
   (d) => JSON.stringify({ ...d, verdict: 'SURVIVED', findings: [] })],
  ['accuracy', 'misses the one-way door', 'case-05-one-way-door',
   (d) => JSON.stringify({ ...d, verdict: 'SURVIVED', findings: [] })],

  ['grounding', 'cites a file not in the diff', 'case-02-wrong-behaviour',
   (d) => JSON.stringify({ ...d, findings: [{ ...d.findings[0],
          evidence: 'src/session_manager.py:88 mishandles the claim' }] })],
  ['grounding', 'empty evidence', 'case-02-wrong-behaviour',
   (d) => JSON.stringify({ ...d, findings: [{ ...d.findings[0], evidence: '  ' }] })],
  ['accuracy', 'asserts the fix is correct without the material to judge it', 'case-07-unjudgeable',
   (d) => JSON.stringify({ ...d, verdict: 'SURVIVED', findings: [] })],
  ['accuracy', 'says nothing about an unreviewably large diff', 'case-08-too-large',
   (d) => JSON.stringify({ ...d, verdict: 'SURVIVED', findings: [] })],
  ['accuracy', 'proposes the rewrite instead of naming the defect', 'case-02-wrong-behaviour',
   (d) => JSON.stringify({ ...d, findings: [{ ...d.findings[0],
          finding: 'Inverted comparison. Fix:\n```python\nif claims["exp"] < now:\n    return False\n```' }] })],
  ['accuracy', 'praises the author', 'case-01-clean',
   (d) => JSON.stringify({ ...d, reviewers: [{ agent: 'r', verdict: 'SURVIVED',
          note: 'Great work, nice clean fix.' }] })],

  ['grounding', 'claims the suite passed when it is red', 'case-04-red-suite',
   (d) => JSON.stringify({ ...d, verdict: 'SURVIVED', findings: [],
          reviewers: [{ agent: 'r', verdict: 'SURVIVED', note: 'All tests pass.' }] })],
];

const ASSERTS = { contract, accuracy, grounding };
let bad = 0;

console.log('reference answers (every assert must accept every case):');
for (const [id, doc] of Object.entries(REFERENCE)) {
  for (const [name, fn] of Object.entries(ASSERTS)) {
    const r = fn(JSON.stringify(doc), ctx(id));
    if (!r.pass) {
      console.log(`  FAIL ${name} rejected ${id}: ${r.reason}`);
      bad++;
    }
  }
}
if (!bad) console.log(`  ok   all 3 asserts accept all ${Object.keys(REFERENCE).length} cases`);

console.log('\nmutants (each must be caught by the named criterion):');
for (const [criterion, label, id, mutate] of MUTANTS) {
  const r = ASSERTS[criterion](mutate(REFERENCE[id]), ctx(id));
  if (r.pass) {
    console.log(`  SURVIVED ${criterion}: ${label}`);
    bad++;
  } else {
    console.log(`  killed   ${criterion}: ${label} -> ${r.reason.slice(0, 92)}`);
  }
}

console.log(`\n${bad === 0 ? 'ALL AS EXPECTED' : bad + ' PROBLEM(S)'}`);
process.exit(bad ? 1 : 0);
