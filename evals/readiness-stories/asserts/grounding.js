// Criterion 3 — grounding. The story set invents no requirement the input does not contain.
//
// The inverse of coverage, and the failure that looks like diligence: a planner that adds
// FR-9 "audit logging" to a change about TOTP has produced work nobody asked for, and a
// reviewer reading the stories alone cannot tell it was invented. Scope growth is harder to
// spot than scope loss, because the extra story is usually a reasonable idea.
const { input, storyFiles, requirementIds, result } = require('./lib');

const STOP = new Set(['user', 'users', 'system', 'want', 'that', 'this', 'with', 'from', 'when',
  'then', 'given', 'should', 'story', 'able', 'into', 'their', 'have', 'they', 'what', 'which',
  'where', 'while', 'been', 'will', 'would', 'could', 'make', 'need', 'needs']);

module.exports = (output, context) => {
  const item = input(context);
  const files = storyFiles(output);
  if (!files.length) return { pass: false, score: 0, reason: 'no story files found' };

  const known = new Set(item.requirements.map((r) => r.id));
  const seen = requirementIds(files.map((f) => f.body).join('\n'));
  const invented = [...seen].filter((id) => !known.has(id));

  const problems = [];
  if (invented.length) {
    problems.push(`cites requirement ids absent from the input: ${invented.join(', ')}`);
  }

  // A story whose statement shares no distinctive wording with the change is generic filler —
  // the shape an invented story takes when it avoids citing a requirement id at all.
  const source = [item.goal, ...item.requirements.map((r) => r.text)].join(' ').toLowerCase();
  for (const f of files) {
    const stmt = (f.body.match(/^##\s+Story\s*\n+([\s\S]*?)(?=\n##\s|$)/m) || [, ''])[1];
    const words = (stmt.toLowerCase().match(/[a-z][a-z0-9-]{3,}/g) || [])
      .filter((w) => !STOP.has(w));
    if (words.length && !words.some((w) => source.includes(w))) {
      problems.push(`${f.name}: the story statement shares no wording with the change`);
    }
  }
  return result(problems, 'every requirement cited exists in the input');
};
