// positive: prohibitions with a positive target are rewritten as the positive; hard
// guardrails may stay negative but must name what to do instead.
const { spec, result, files, has } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const all = files(output).map((f) => f.text).join('\n');
  const p = [];
  for (const r of s.positive) {
    if (has(r.banned, all)) p.push(`${r.id}: still phrased as a prohibition`);
    if (!has(r.want, all)) p.push(`${r.id}: no positive target (${r.want})`);
  }
  for (const g of s.guardrails || []) if (has(g.if, all) && !has(g.want, all)) p.push(`${g.id}: guardrail kept with no positive target`);
  return result(p, 'positives stated');
};
