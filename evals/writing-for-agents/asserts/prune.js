// prune (precision): planted no-ops, environment caches and duplicates are gone.
const { spec, result, files, count, body } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  // Frontmatter is the pointer, graded by pointer; naming the format there is not a duplicate.
  const all = files(output).map((f) => body(f.text)).join('\n');
  const p = [];
  for (const r of s.prune) {
    const n = count(r.pattern, all);
    if (n > r.max) p.push(`${r.id}: ${n} left (max ${r.max})`);
  }
  return result(p, 'no-ops, caches and duplicates pruned');
};
