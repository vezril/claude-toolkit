// regression: the agent left a test that catches this bug. Its own modules, copied onto
// the pristine project and run alone, fail (for the flaky case: under at least 3 of 4 of
// 16 hash seeds, so the pre-existing flaky test, which fails about half the time, doesn't
// qualify), and in the agent's project the whole suite passes (every seed).
const { spec, result, project, pristine, changed, isTest, unittest, tmpCopy, moduleOf, fs, path } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const dir = project(context);
  const { added, modified } = changed(s, dir);
  const tests = [...added, ...modified].filter((r) => isTest(r) && r.endsWith('.py'));
  if (!tests.length) return result(['no new or changed test'], '');
  const seeds = s.seeds ? [...Array(s.seeds).keys()] : [null];
  const p = [];
  const bad = seeds.map((seed) => unittest(dir, seed)).find((r) => !r.ok);
  if (bad) p.push(`the suite fails on the agent's code: ${bad.out.slice(0, 100)}`);
  const old = tmpCopy(pristine(s));
  for (const rel of tests) { fs.mkdirSync(path.dirname(path.join(old, rel)), { recursive: true }); fs.copyFileSync(path.join(dir, rel), path.join(old, rel)); }
  if (!fs.existsSync(path.join(old, 'tests', '__init__.py')) && fs.existsSync(path.join(pristine(s), 'tests', '__init__.py'))) fs.copyFileSync(path.join(pristine(s), 'tests', '__init__.py'), path.join(old, 'tests', '__init__.py'));
  const mods = tests.map(moduleOf);
  const fails = seeds.filter((seed) => !unittest(old, seed, mods).ok).length;
  const catches = s.seeds ? fails >= Math.ceil(seeds.length * 0.75) : fails > 0;
  fs.rmSync(old, { recursive: true, force: true });
  if (!catches) p.push(s.seeds ? `the new test fails on only ${fails}/${seeds.length} seeds of the buggy code` : `the new test (${tests.join(', ')}) also passes on the buggy code`);
  return result(p, `regression test ${tests.join(', ')} catches the bug`);
};
