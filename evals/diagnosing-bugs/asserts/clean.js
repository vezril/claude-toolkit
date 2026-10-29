// clean: no debug instrumentation left in production code, and no throwaway files left
// behind (new files are tests, or sit in a directory named debug/ or scratch/).
const { spec, result, project, pristine, changed, isTest, read, path } = require('./lib');
const INSTR = /^\+.*(\bprint\(|\[DEBUG|logging\.debug|\bbreakpoint\(|\bpdb\b)/;
module.exports = (output, context) => {
  const s = spec(context);
  const dir = project(context);
  const { added, modified } = changed(s, dir);
  const p = [];
  for (const rel of modified.filter((r) => !isTest(r) && r.endsWith('.py'))) {
    const before = new Set(read(path.join(pristine(s), rel)).split('\n'));
    const added_ = read(path.join(dir, rel)).split('\n').filter((l) => !before.has(l)).map((l) => '+' + l);
    const hit = added_.find((l) => INSTR.test(l));
    if (hit) p.push(`instrumentation left in ${rel}: "${hit.slice(1).trim().slice(0, 60)}"`);
  }
  const stray = added.filter((r) => !isTest(r) && !/(^|\/)(debug|scratch)\//.test(r));
  if (stray.length) p.push('left behind: ' + stray.join(', '));
  return result(p, 'no instrumentation or throwaway files left');
};
