// Criterion 4 — discipline (lenient parse). An adversarial node is only worth its cost if
// its report is an honest record of what it actually did, so this scores the log rather
// than the conclusion:
//
//   * three distinct attacks, each with a method that says what was checked;
//   * landed/failed consistent with the verdict — SURVIVED is earned by documented failed
//     attacks, never by an empty log, and a non-SURVIVED verdict needs an attack that landed;
//   * findings and landed attacks agree in both directions;
//   * every id and filename a finding cites exists in the material it was given.
//
// The last one is the anti-fabrication check. A finding against story S12 of an eight-story
// breakdown is not a finding, and it is the failure mode that costs the pipeline a rerun of
// work that was right.
const { breakdown, item, parsed, result } = require('./lib');

const FILE_RE = /[A-Za-z0-9_.\/-]*[A-Za-z0-9_-]\.(?:scala|sbt|py|js|ts|tsx|java|kt|go|rs|md|ya?ml|conf|xml|json|toml|sh|sql|proto)\b/g;
const ID_RE = /\b(?:E|S|AC)[0-9]+\b/g;

// The pipeline's own artifact names are not citations of anything: the prompt's output
// contract tells the node to write `"target": "breakdown.json"`, so naming the artifact it
// was asked to attack is the contract working, not a fabricated file reference. None of
// these strings appears inside the artifacts themselves, so without this the check fired on
// a node that did exactly what it was told. Found on haiku/v3a case-07.
const OWN_ARTIFACTS = new Set([
  'item.json', 'triage.json', 'breakdown.json', 'challenge-breakdown.json',
]);

module.exports = (output, context) => {
  const doc = parsed(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as JSON' };

  const bd = breakdown(context);
  const it = item(context);
  const bdText = JSON.stringify(bd);
  const source = (it.title + ' ' + it.body + ' ' + bdText).toLowerCase();
  const ids = new Set(bdText.match(ID_RE) || []);

  const attacks = Array.isArray(doc.attacks) ? doc.attacks : [];
  const findings = Array.isArray(doc.findings) ? doc.findings : [];
  const problems = [];

  if (attacks.length < 3) problems.push(`${attacks.length} attack(s): one examination is at least three`);

  const seen = new Set();
  for (const a of attacks) {
    const attack = String(a.attack || '').trim();
    const method = String(a.method || '').trim();
    const key = attack.toLowerCase();
    if (seen.has(key)) problems.push(`the same attack is logged twice: "${attack.slice(0, 60)}"`);
    seen.add(key);
    if (method.split(/\s+/).length < 4) problems.push(`"${attack.slice(0, 40)}": method says nothing it checked`);
    if (method.toLowerCase() === key) problems.push(`"${attack.slice(0, 40)}": method restates the attack`);
  }

  const landed = attacks.filter((a) => a.result === 'landed');
  if (doc.verdict === 'SURVIVED' && landed.length) {
    problems.push(`SURVIVED with ${landed.length} attack(s) recorded as landed`);
  }
  if (doc.verdict && doc.verdict !== 'SURVIVED' && !landed.length) {
    problems.push(`${doc.verdict} with no attack recorded as landed`);
  }
  if (landed.length && !findings.length) problems.push('an attack landed but there are no findings');
  if (findings.length && !landed.length) problems.push('there are findings but no attack is recorded as landed');

  for (const f of findings) {
    const text = `${f.finding || ''} ${f.evidence || ''}`;
    const evidence = String(f.evidence || '').trim();
    if (evidence.split(/\s+/).length < 4) {
      problems.push(`"${String(f.finding).slice(0, 40)}": evidence too thin to check`);
    }
    const badIds = [...new Set(text.match(ID_RE) || [])].filter((i) => !ids.has(i));
    if (badIds.length) problems.push(`cites ids that are not in the breakdown: ${badIds.join(', ')}`);
    const badFiles = [...new Set(text.match(FILE_RE) || [])]
      .filter((p) => !OWN_ARTIFACTS.has(p.toLowerCase()))
      .filter((p) => !source.includes(p.toLowerCase()));
    if (badFiles.length) problems.push(`cites files absent from the item and breakdown: ${badFiles.slice(0, 3).join(', ')}`);
  }

  return result(problems.slice(0, 4),
    `${attacks.length} distinct attacks, ${landed.length} landed, ${findings.length} grounded finding(s)`);
};
