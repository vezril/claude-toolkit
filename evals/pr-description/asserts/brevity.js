// Criterion 5 — brevity. The description stays inside v7's stated length limits, so a
// reviewer who scans it still reaches the Merge danger section.
//
// Every limit here is a line in the prompt's `# Length` section (plus the graded-adjective
// rule in `# Constraints`). Nothing is measured that the prompt does not ask for, and nothing
// the prompt asks for is left unmeasured — that correspondence is what load-bearing.md
// records, and it is the reason this criterion exists at all: v7 added length instructions,
// and an instruction no assert measures is not certified behaviour.
//
// Deliberately NOT a word count over the whole reply. A single total would let a bloated
// Changes list hide behind a terse What, and the section that gets skipped is the one at the
// bottom. Each section carries its own limit.
//
// Versions before v7 have no `# Length` section and are expected to fail this criterion on
// the wordier cases; that is the measurement v7 exists to move, not a defect in the suite.
const { lenient, result } = require('./lib');

// Every cap is set at or just above the median of v6's own 66 unconstrained outputs, so each
// is a real constraint the long tail violates badly rather than a limit the model already
// respects. Measured from results/run_v6_all*.json before v7 was written:
//
//   What words     median 23-25, p90 32, max 37   -> 25
//   Why sentences  median 2,     p90 3-4          -> 2
//   bullet words   median 20-25, p75 29, max 84   -> 25
//   bullets/case   median 3-4,   p90 6, max 8     -> 5
//   Door / radius  median 1,     p90 2, max 3     -> 1
//
// The bullet cap was 20 in the first draft and is 25 here. At 20 it sat *below* the median and
// was the dominant failure on 26-32 of 33 cases; on a six-file case it also pushed against
// `coverage`, which requires every changed file to appear. A cap that can only be met by
// dropping a file would have traded one criterion for another.
const WHAT_WORDS = 25;
const WHY_SENTENCES = 2;
const MAX_BULLETS = 5;
const BULLET_WORDS = 25;

// Graded adjectives the prompt bans. A reviewer reads one as a claim the diff must support.
const PROMOTIONAL = ['comprehensive', 'robust', 'significantly', 'seamlessly',
                     'greatly', 'leverage', 'utilize', 'extensive', 'thorough'];

const words = (s) => s.trim().split(/\s+/).filter(Boolean).length;

// Sentence count that does not trip over `v1.2.3`, `e.g.` or a trailing period.
const sentences = (s) =>
  s.replace(/\b\d+\.\d+/g, '0').replace(/\b(?:e\.g|i\.e|etc|vs|Dr|Mr)\./gi, '$1')
   .split(/[.!?]+(?:\s|$)/).map((x) => x.trim()).filter(Boolean).length;

function section(text, heading) {
  const re = new RegExp(`^##\\s*${heading}\\s*$([\\s\\S]*?)(?=^##\\s|\\Z)`, 'im');
  const m = text.match(re);
  return m ? m[1].trim() : null;
}

module.exports = (output, context) => {
  const t = lenient(output);
  const problems = [];

  const what = section(t, 'What');
  if (what === null) problems.push('no "## What" section to measure');
  else if (words(what) > WHAT_WORDS) problems.push(`What is ${words(what)} words (max ${WHAT_WORDS})`);

  const why = section(t, 'Why');
  if (why === null) problems.push('no "## Why" section to measure');
  else if (sentences(why) > WHY_SENTENCES) problems.push(`Why is ${sentences(why)} sentences (max ${WHY_SENTENCES})`);

  const changes = section(t, 'Changes');
  if (changes === null) {
    problems.push('no "## Changes" section to measure');
  } else {
    const lines = changes.split('\n').map((l) => l.replace(/\s+$/, '')).filter((l) => l.trim());
    const top = lines.filter((l) => /^\s{0,1}[-*+]\s/.test(l));
    const nested = lines.filter((l) => /^\s{2,}[-*+]\s/.test(l));
    if (nested.length) problems.push(`${nested.length} sub-bullet(s); bullets must be flat`);
    if (top.length > MAX_BULLETS) problems.push(`${top.length} bullets (max ${MAX_BULLETS})`);
    const longest = top.map((l) => words(l.replace(/^\s*[-*+]\s/, '')))
                       .reduce((a, b) => Math.max(a, b), 0);
    if (longest > BULLET_WORDS) problems.push(`longest bullet is ${longest} words (max ${BULLET_WORDS})`);
  }

  // The two risk lines, one sentence each. Measured off the labels rather than the section,
  // because the Merge danger heading is sometimes dropped — that omission belongs to the
  // contract criterion, and penalising it here too would double-count one mistake.
  for (const label of ['Door', 'Blast radius']) {
    const m = t.match(new RegExp(`\\*{0,2}${label}:?\\*{0,2}:?\\s*(.+)`, 'i'));
    if (m && sentences(m[1]) > 1) problems.push(`${label} is ${sentences(m[1])} sentences (max 1)`);
  }

  const found = PROMOTIONAL.filter((w) => new RegExp(`\\b${w}`, 'i').test(t));
  if (found.length) problems.push(`graded adjective(s): ${found.join(', ')}`);

  return result(problems, `within length limits (What <= ${WHAT_WORDS}w, <= ${MAX_BULLETS} bullets <= ${BULLET_WORDS}w)`);
};
