// Contamination scan: list every tool call whose input names a path outside the
// run's temp world. The handoff suite's first runs were contaminated this way and
// only a tool-call scan caught it, so every run prints this before its score.
const r = require(require('path').resolve(process.argv[2]));
const world = process.argv[3];
const rows = (r.results && r.results.results) || [];
let n = 0;
for (const row of rows) {
  const calls = (row.response && row.response.metadata && row.response.metadata.toolCalls) || [];
  for (const c of calls) {
    const s = JSON.stringify(c.input || {});
    for (const m of s.matchAll(/(?:\/(?:Users|private|tmp|var|etc|opt|home)\/[^"\s]*)|(?:\.\.\/[^"\s]*)|~\/[^"\s]*/g)) {
      const pth = m[0];
      const inWorld = pth.startsWith(world) || pth.startsWith('/private' + world) || pth.startsWith(world.replace(/^\/private/, ''));
      if (!inWorld) { n++; console.log(`OUTSIDE ${row.provider && row.provider.label} ${row.vars && row.vars.case}: ${c.name} ${pth.slice(0, 120)}`); }
    }
  }
}
console.log(n ? `scan: ${n} tool call(s) outside the world, check before trusting this run` : 'scan: clean (no tool call left the world)');
