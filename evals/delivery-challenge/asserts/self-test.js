// Test the test: run the four asserts against hand-built outputs whose verdict is known,
// with no model calls. The bypass suite's first run reported a breach that was really a
// broken check, so a suite whose asserts have never been exercised against a known-wrong
// output is not evidence of anything yet.
//
//   node asserts/self-test.js
const path = require('path');
const asserts = {
  schema: require('./schema.js'),
  verdict: require('./verdict.js'),
  detection: require('./detection.js'),
  discipline: require('./discipline.js'),
};

const ctx = (c) => ({ vars: { case: c } });
const J = (o) => JSON.stringify(o);

// A correct challenge of case-03 (A1: the zero-quantity / out-of-stock deliverable is gone).
const good03 = {
  item: 'DP-61',
  target: 'breakdown.json',
  verdict: 'REFUTED',
  attacks: [
    { attack: 'Every deliverable the item names appears in some story',
      method: 'listed the item\'s "what should change" paragraph and searched each phrase across all statements and criteria',
      result: 'landed' },
    { attack: 'No story plans the opposite of what the item says',
      method: 'compared each statement against the item\'s stated constraints',
      result: 'failed' },
    { attack: 'Story domains stay inside the set triage found',
      method: 'compared every story\'s domains against triage.domains',
      result: 'failed' },
  ],
  findings: [
    { finding: 'Zero-quantity pantry rows and the out of stock state are in no story and no criterion',
      evidence: 'the item requires zero-quantity rows to become valid and render an "out of stock" state; searching all 5 statements and 17 criteria for "zero" and "out of stock" returns nothing' },
  ],
};

// A correct challenge of case-01 (clean).
const good01 = {
  item: '57',
  target: 'breakdown.json',
  verdict: 'SURVIVED',
  attacks: [
    { attack: 'A deliverable the item names is missing',
      method: 'searched each phrase of the item body across every statement and criterion',
      result: 'failed' },
    { attack: 'A criterion asserts nothing observable',
      method: 'read every "then" for a checkable outcome',
      result: 'failed' },
    { attack: 'Two stories are the same work',
      method: 'compared all five statements pairwise',
      result: 'failed' },
  ],
  findings: [],
};

const CASES = [
  // [label, case, output, expected pass/fail per criterion]
  ['03 correct REFUTED', 'case-03-missing-deliverable', J(good03),
    { schema: true, verdict: true, detection: true, discipline: true }],
  ['01 correct SURVIVED', 'case-01-clean-dlq', J(good01),
    { schema: true, verdict: true, detection: true, discipline: true }],

  ['fenced output', 'case-03-missing-deliverable', '```json\n' + J(good03) + '\n```',
    { schema: false, verdict: true, detection: true, discipline: true }],
  ['prose preamble', 'case-03-missing-deliverable', 'Here is my verdict:\n' + J(good03),
    { schema: false, verdict: true, detection: true, discipline: true }],

  ['missed the hole: says SURVIVED', 'case-03-missing-deliverable',
    J({ ...good03, verdict: 'SURVIVED', findings: [], attacks: good03.attacks.map((a) => ({ ...a, result: 'failed' })) }),
    { schema: true, verdict: false, detection: false, discipline: true }],

  ['right verdict, named the wrong hole', 'case-03-missing-deliverable',
    J({ ...good03, findings: [{ finding: 'The barcode uniqueness story is underspecified',
      evidence: 'S1 AC2 says the save is rejected but does not say with what response' }] }),
    { schema: true, verdict: true, detection: false, discipline: true }],

  ['invented a hole on a clean breakdown', 'case-01-clean-dlq',
    J({ ...good01, verdict: 'WEAKENED',
      attacks: [{ ...good01.attacks[0], result: 'landed' }, good01.attacks[1], good01.attacks[2]],
      findings: [{ finding: 'Paging is not specified precisely enough',
        evidence: 'S1 AC2 refers to "paging information" without naming the token field' }] }),
    { schema: true, verdict: false, detection: false, discipline: true }],

  ['cites a story that does not exist', 'case-03-missing-deliverable',
    J({ ...good03, findings: [{ finding: 'Story S12 has no criteria covering the out of stock state',
      evidence: 'S12 carries a statement about zero quantity and an empty criteria list' }] }),
    { schema: true, verdict: true, detection: true, discipline: false }],

  ['SURVIVED while an attack landed', 'case-01-clean-dlq',
    J({ ...good01, attacks: [{ ...good01.attacks[0], result: 'landed' }, good01.attacks[1], good01.attacks[2]] }),
    { schema: true, verdict: true, detection: true, discipline: false }],

  ['two attacks only', 'case-01-clean-dlq', J({ ...good01, attacks: good01.attacks.slice(0, 2) }),
    { schema: false, verdict: true, detection: true, discipline: false }],

  ['the same attack three times', 'case-01-clean-dlq',
    J({ ...good01, attacks: [good01.attacks[0], good01.attacks[0], good01.attacks[0]] }),
    { schema: true, verdict: true, detection: true, discipline: false }],

  ['methods that say nothing', 'case-01-clean-dlq',
    J({ ...good01, attacks: good01.attacks.map((a) => ({ ...a, method: 'reviewed it' })) }),
    { schema: true, verdict: true, detection: true, discipline: false }],

  ['REFUTED with no landed attack', 'case-03-missing-deliverable',
    J({ ...good03, attacks: good03.attacks.map((a) => ({ ...a, result: 'failed' })) }),
    { schema: true, verdict: true, detection: true, discipline: false }],

  ['WEAKENED where REFUTED is right', 'case-03-missing-deliverable', J({ ...good03, verdict: 'WEAKENED' }),
    { schema: true, verdict: false, detection: true, discipline: true }],

  ['not JSON at all', 'case-03-missing-deliverable',
    '## Verdict: REFUTED\n\nThe breakdown omits the zero-quantity work entirely.',
    { schema: false, verdict: false, detection: false, discipline: false }],
];

// The other half of testing the test: a `must_find` group nothing can satisfy makes a case
// unwinnable, and the suite would read as the model failing rather than the label being
// wrong. One plausible correct finding per planted defect, which must score as detected.
// An inserted epic's id is an artifact of fixture generation (`renumber` in
// derive-fixtures.py), so resolve it from the fixture instead of hardcoding it. A hardcoded
// `E9` here went stale the moment renumbering landed and cost this test 2 of 22 — the same
// class of mistake renumbering exists to remove.
const epicIdByTitle = (c, needle) => {
  const bd = require(path.resolve(__dirname, '..', 'inputs', `${c}.breakdown.json`));
  const e = (bd.epics || []).find((x) => String(x.title).toLowerCase().includes(needle));
  if (!e) throw new Error(`${c}: no epic whose title contains "${needle}"`);
  return e.id;
};

const ACHIEVABLE = [
  ['case-04-contradicts-item', 'REFUTED',
    `Epic ${epicIdByTitle('case-04-contradicts-item', 'journal')} plans to migrate the journal and rewrite persistence ids, which contradicts the item: it says persistence ids and the journal are unchanged.`],
  ['case-05-unrequested-epic', 'REFUTED',
    `Epic ${epicIdByTitle('case-05-unrequested-epic', 'grafana')} adds Grafana dashboards and alerting rules. The item does not ask for either; it names Grafana only as a consumer of the scrape.`],
  ['case-06-criteria-miss-story', 'WEAKENED',
    'Story S2 promises that metrics.enabled defaults to true and that no route exists when disabled, but both of its criteria assert base JVM metrics and the exposition format instead, so nothing tests the toggle.'],
  ['case-07-vague-outcome', 'WEAKENED',
    'S3 AC1 ends in "the feature works correctly", which asserts nothing observable and cannot become a test.'],
  ['case-08-duplicate-stories', 'WEAKENED',
    'S5 and S7 are the same work: both render the out of stock state on the pantry page for zero-quantity rows, duplicated across two epics.'],
  ['case-09-wrong-domains', 'WEAKENED',
    'S1 is tagged domains backend, but it restyles MainNav into a sidebar, which is ux work; the tag would dispatch it to the backend architect and reviewers and skip the ux specialist.'],
  ['case-03-missing-deliverable', 'REFUTED',
    'Zero-quantity pantry rows and the out of stock state are in no story and no criterion, though the item requires both.'],
];
for (const [c, verdict, finding] of ACHIEVABLE) {
  CASES.push([`${c}: a correct finding is detectable`, c, J({
    item: 'X', target: 'breakdown.json', verdict,
    attacks: [
      { attack: 'A deliverable the item names is missing', method: 'checked each deliverable in the item body against every story and criterion', result: 'landed' },
      { attack: 'A criterion asserts nothing observable', method: 'read every "then" for a checkable outcome', result: 'failed' },
      { attack: 'Two stories are the same work', method: 'compared every pair of statements for overlap', result: 'failed' },
    ],
    findings: [{ finding, evidence: 'quoted from the artifact in the finding above, against the item body' }],
  }), { schema: true, verdict: true, detection: true, discipline: true }]);
}

let failures = 0;
for (const [label, c, output, want] of CASES) {
  const got = {};
  for (const [name, fn] of Object.entries(asserts)) {
    try { got[name] = fn(output, ctx(c)).pass; } catch (e) { got[name] = 'threw: ' + e.message; }
  }
  const wrong = Object.keys(want).filter((k) => got[k] !== want[k]);
  if (wrong.length) {
    failures++;
    console.log(`FAIL  ${label}`);
    for (const k of wrong) {
      const detail = (() => { try { return asserts[k](output, ctx(c)).reason; } catch (e) { return e.message; } })();
      console.log(`        ${k}: expected ${want[k] ? 'pass' : 'fail'}, got ${got[k] ? 'pass' : 'fail'} — ${detail}`);
    }
  } else {
    console.log(`ok    ${label}`);
  }
}
console.log(`\n${CASES.length - failures}/${CASES.length} synthetic outputs scored as intended`);
process.exit(failures ? 1 : 0);
