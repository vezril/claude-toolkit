// Criterion 3 — acceptance criteria (lenient parse). The schema proves ACs exist; this
// proves they are worth having: distinct, specific, and about observable outcomes.
const { parsed, stories, result } = require('./lib');

const VAGUE = /^(it works|works correctly|the system works|no errors|everything works|the feature works|success)\.?$/i;

module.exports = (output) => {
  const doc = parsed(output);
  if (!doc) return { pass: false, score: 0, reason: 'output did not parse as JSON' };
  const problems = []; const all = stories(doc); const seenStory = new Set();

  for (const s of all) {
    const stmt = String(s.statement || '').trim().toLowerCase();
    if (seenStory.has(stmt)) problems.push(`duplicate story: "${stmt.slice(0, 50)}"`);
    seenStory.add(stmt);

    const acs = s.acceptance_criteria || [];
    const ids = acs.map((a) => a.id);
    if (new Set(ids).size !== ids.length) problems.push(`${s.id}: duplicate acceptance-criterion ids`);
    // Criteria may share an outcome when the precondition differs — a missing token and an
    // expired token both end in "rejected". Only a repeated given+when+then is a duplicate.
    const seenTriple = new Set();
    for (const ac of acs) {
      const then = String(ac.then || '').trim();
      if (VAGUE.test(then)) problems.push(`${s.id}/${ac.id}: "then" is vague ("${then}")`);
      if (then.split(/\s+/).length < 3) problems.push(`${s.id}/${ac.id}: "then" is too short to assert anything`);
      const triple = [ac.given, ac.when, ac.then].map((x) => String(x || '').trim().toLowerCase()).join(' | ');
      if (seenTriple.has(triple)) problems.push(`${s.id}: two criteria are the same criterion`);
      seenTriple.add(triple);
      if (String(ac.given || '').trim().toLowerCase() === then.toLowerCase()) {
        problems.push(`${s.id}/${ac.id}: "given" and "then" are the same text`);
      }
    }
  }
  if (!all.length) problems.push('no stories');
  return result(problems.slice(0, 4), `${all.length} stories, criteria distinct and specific`);
};
