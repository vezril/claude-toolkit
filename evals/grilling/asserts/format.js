// format (strict): the round is the skill's numbered block format, each question
// carrying a recommended answer.
const { spec, result, blocks } = require('./lib');
module.exports = (output, context) => {
  spec(context);
  const bs = blocks(output);
  const p = [];
  if (!bs.length) p.push('no "❓ **Qn** - **title**:" question blocks');
  bs.forEach((b, i) => {
    if (b.n !== i + 1) p.push(`question ${i + 1} is numbered Q${b.n}`);
    if (!b.rec) p.push(`Q${b.n} ("${b.title.slice(0, 40)}") has no ➡️ recommendation`);
  });
  return result(p, `${bs.length} numbered questions, each with a recommendation`);
};
