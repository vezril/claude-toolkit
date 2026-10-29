// frontier: round one holds back the decisions the user said hang on an open choice.
// A sentence naming a downstream decision is let off when it is itself the open
// choice (names a root and offers an "or"). Which question comes first is not graded:
// the models showed a root can itself hang on facts about the user (g-03, g-04), and
// asking those first is the skill working, not failing.
const { spec, result, questionSentences, blocks, has } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const qs = [...questionSentences(output), ...blocks(output).map((b) => b.title + '?')];
  const p = [];
  for (const d of s.downstream) {
    const hit = qs.find((q) => has(d.pattern, q) && !(s.roots.some((r) => has(r.pattern, q)) && /\bor\b/i.test(q)));
    if (hit) p.push(`asked downstream ${d.id} while its root is open: "${hit.slice(0, 90)}"`);
  }
  return result(p, 'downstream decisions held back');
};
