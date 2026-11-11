// Criterion 1 — schema. Every story the node emits must pass `scripts/lint-story.py`, the
// same script the readiness edge runs.
//
// Shelling out to the real linter rather than reimplementing its rules is the point. A suite
// carrying its own copy of the schema can pass a story set the edge rejects, and then the
// certification number describes a bar nobody enforces.
const { input, storyFiles, materialise, lintStory } = require('./lib');

module.exports = (output, context) => {
  const item = input(context);
  const files = storyFiles(output);
  if (!files.length) {
    return {
      pass: false,
      score: 0,
      reason: 'no story files found; expected `=== stories/<name>.md ===` before each',
    };
  }

  const { dir, written } = materialise(files, item.sources);
  if (!written.length) return { pass: false, score: 0, reason: 'no story file could be written' };

  const { code, out } = lintStory(written, dir);
  if (code === 0) {
    return { pass: true, score: 1, reason: `${written.length} story file(s) lint clean` };
  }

  const detail = out.split('\n').filter((l) => l.trim().startsWith('-')).slice(0, 6)
    .map((l) => l.trim());
  return {
    pass: false,
    score: 0,
    reason: `lint-story.py rejected the set: ${detail.join('; ') || out.trim().slice(0, 300)}`,
  };
};
