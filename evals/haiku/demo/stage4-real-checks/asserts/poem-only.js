// STAGE 4 — a deterministic check, written as code instead of a keyword list.
//
// The property: the reply IS the poem. First line of the reply is the first
// line of the poem; nothing before it, nothing after it.
//
// A promptfoo JavaScript assert returns { pass, score, reason }. The reason is
// what makes a failing run diagnosable without rerunning it — that's the whole
// difference between "score: 0.6" and "opens: Here's a haiku about winter:".
module.exports = (output) => {
  const lines = output.trim().split('\n').map((l) => l.trim());
  const nonEmpty = lines.filter(Boolean);

  if (lines.length !== nonEmpty.length || nonEmpty.length !== 3) {
    return {
      pass: false,
      score: 0,
      reason: `reply is ${nonEmpty.length} non-empty line(s), want exactly 3 (opens: ${JSON.stringify(nonEmpty[0] || '').slice(0, 60)})`,
    };
  }
  if (/^(here|sure|certainly|i'd|of course|absolutely)\b/i.test(nonEmpty[0])) {
    return { pass: false, score: 0, reason: `preamble: ${JSON.stringify(nonEmpty[0]).slice(0, 60)}` };
  }
  if (/^#|^\*\*|^```/.test(nonEmpty[0])) {
    return { pass: false, score: 0, reason: `title or fence: ${JSON.stringify(nonEmpty[0]).slice(0, 60)}` };
  }
  return { pass: true, score: 1, reason: 'reply is the poem' };
};
