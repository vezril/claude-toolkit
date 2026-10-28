// facts: finding facts is the agent's job. A fact the fixture answers is never put
// to the user as a question. (Whether the reply mentions the fact is not graded: it
// only has to come up if the round needs it.)
const { spec, result, questionSentences, has } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const qs = questionSentences(output);
  const p = [];
  for (const f of s.facts) {
    const asked = qs.find((q) => has(f.ask, q));
    if (asked) p.push(`asked the user for ${f.id}: "${asked.slice(0, 90)}"`);
  }
  return result(p, 'no planted fact asked of the user');
};
