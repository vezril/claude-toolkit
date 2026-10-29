// preserve (recall): every load-bearing behaviour of the original survives somewhere
// in the revised files. A group passes when one of its alternatives appears.
const { spec, result, files } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const all = files(output).map((f) => f.text).join('\n').toLowerCase();
  const p = [];
  for (const r of s.preserve) {
    const missing = r.groups.filter((g) => !g.some((a) => all.includes(a.toLowerCase())));
    if (missing.length) p.push(`lost ${r.id} (no ${missing.map((g) => g.join('|')).join(', ')})`);
  }
  return result(p, 'every planted behaviour kept');
};
