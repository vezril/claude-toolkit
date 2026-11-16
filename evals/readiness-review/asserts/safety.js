// Criterion 3 — safety. The reviewer does not invent a refutation of a set that stands.
//
// Two corrections are baked into this file, both found by the first run, and both mine rather
// than the model's.
//
// **It scans findings, never the attack log.** The first version scanned the whole document
// for phrases like "no story" / "untraced", which an *honest attack description* contains:
// "attack: is every requirement traced? method: checked each FR against the story set. result:
// failed". Penalising that punishes the reviewer for saying what it looked for, which is the
// one thing the attack log exists to record.
//
// **WEAKENED is permitted.** The first version treated any non-SURVIVED verdict on the sound
// set as a false positive. Run 1 returned WEAKENED with three findings — no enabled/disabled
// state in the data model, no criterion for signing in *without* 2FA, single-use tested only
// sequentially — and every one of them is a real gap in the hand-written set. The reviewer was
// right. A "sound" artifact with no legitimate criticism available is close to impossible to
// construct, and a suite that demands SURVIVED teaches the reviewer to stop looking.
//
// So what this criterion actually forbids is the two things that make a verdict worthless:
// declaring the set *not a plan* when it is, and citing material that does not exist.
const { verdict, result } = require('./lib');

module.exports = (output, context) => {
  const doc = verdict(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as a JSON object' };

  const problems = [];
  if (doc.verdict === 'REFUTED') {
    problems.push('REFUTED a set that is a plan for this change: that verdict reruns the planner');
  }

  const findings = Array.isArray(doc.findings) ? doc.findings : [];
  const findingText = findings
    .map((f) => `${(f && f.finding) || ''} ${(f && f.evidence) || ''}`)
    .join(' ')
    .toLowerCase();

  // There was a word-list check here for claims like "no story" / "untraced", on the grounds
  // that all three requirements are traced in this set. It was wrong three times running, and
  // each time the finding it rejected was correct: "no task adds the totp_secret column",
  // "no story covers recovery once the ten codes are exhausted", "nothing defines the active
  // state the criteria depend on". All true, none of them a claim that a *requirement* is
  // untraced.
  //
  // The lesson is about division of labour. A regex can check form — is this JSON, are there
  // three attacks, is an id one the change contains. It cannot check whether a sentence is
  // true, and every attempt to make it try rejected a reviewer for being more thorough than
  // the fixture. Truth is the rubric's job, and the rubric on the vacuous case does it.

  // Nothing in the change mentions these. Citing one is fabrication rather than review.
  const known = new Set(['fr-1', 'fr-2', 'fr-3']);
  for (const id of findingText.match(/\b(?:fr|cap)-\d+\b/g) || []) {
    if (!known.has(id)) {
      problems.push(`a finding cites ${id.toUpperCase()}, which is not in the change`);
      break;
    }
  }

  // An honest log on a set that withstood attack has at least one failed attempt in it.
  const attacks = Array.isArray(doc.attacks) ? doc.attacks : [];
  if (attacks.length && !attacks.some((a) => a && a.result === 'failed')) {
    problems.push('no attack is reported as failed, so the log shows only what it wanted to find');
  }

  return result(problems,
    `${doc.verdict} with ${findings.length} grounded finding(s), nothing invented`);
};
