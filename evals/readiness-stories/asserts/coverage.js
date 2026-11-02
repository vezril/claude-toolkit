// Criterion 2 — coverage. Every requirement in the input is traced by at least one story.
//
// This is the defect class the challenge node exists to catch downstream: "a deliverable the
// item requires appears in no story". Catching it here is cheaper and deterministic, and it is
// the single most consequential thing a decomposition can get wrong — a dropped requirement
// produces a plan that looks complete.
const { input, expected, storyFiles, requirementIds, result } = require('./lib');

module.exports = (output, context) => {
  const item = input(context);
  const want = expected(context);
  const files = storyFiles(output);
  if (!files.length) return { pass: false, score: 0, reason: 'no story files found' };

  const seen = requirementIds(files.map((f) => f.body).join('\n'));
  const required = want.requirements || item.requirements.map((r) => r.id);
  const missing = required.filter((id) => !seen.has(id));

  const problems = [];
  if (missing.length) problems.push(`no story traces ${missing.join(', ')}`);

  // Story count bounds, because both directions are failures. Too few means a requirement was
  // folded into a story that does not carry it; too many means the change was shredded into
  // units too small to be independently valuable, which is the INVEST failure a count can see.
  const n = files.length;
  if (want.min_stories && n < want.min_stories) {
    problems.push(`${n} stories, fewer than the ${want.min_stories} this change needs`);
  }
  if (want.max_stories && n > want.max_stories) {
    problems.push(`${n} stories for ${required.length} requirement(s), past the ${want.max_stories} ceiling`);
  }
  return result(problems, `all ${required.length} requirement(s) traced across ${n} stories`);
};
