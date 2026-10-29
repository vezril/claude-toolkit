// Shared form checks for every case. Each is a property of the text, not its wording,
// so rephrasing never flips a result.
//
// Thresholds are deliberately generous. The point is to catch a wall of text and a
// memory-test list, not to police good prose into failing. A correct answer that runs
// slightly long still passes; the skill's own "2-4 sentences" target is an aim, not a gate.

const PREAMBLE = /^\s*(sure|certainly|of course|absolutely|great question|let me|i'?ll (now|go|start)|i'?m going to|happy to|thanks for)/i;
const BACKREF = /\b(as (mentioned|noted|described|discussed) (above|earlier|previously)|the (above|aforementioned|earlier) (point|issue|item|file|one)|that thing|as i said (above|earlier))\b/i;
const MENU_TAIL = /(let me know if you(?:'d| would) like|would you like me to|want me to .{0,40}\?|shall i|should i .{0,40}\?)/i;

function words(t) {
  return t.trim().split(/\s+/).filter(Boolean).length;
}
function bulletCount(t) {
  // Longest run of consecutive list items anywhere in the reply.
  let best = 0, run = 0;
  for (const line of t.split('\n')) {
    if (/^\s*([-*+]|\d+[.)])\s+\S/.test(line)) { run++; best = Math.max(best, run); }
    else if (line.trim() === '') { /* blank keeps a run alive */ }
    else { run = 0; }
  }
  return best;
}
function questionCount(t) {
  return (t.match(/\?/g) || []).length;
}
function boldCount(t) {
  return (t.match(/\*\*[^*\n]+\*\*/g) || []).length;
}
function firstSentence(t) {
  const body = t.replace(/^#+ .*$/gm, '').trim();           // skip a leading heading
  const m = body.match(/^[\s\S]*?[.!?](\s|$)/);
  return (m ? m[0] : body.slice(0, 200)).trim();
}

module.exports = (output, context) => {
  const t = typeof output === 'string' ? output : JSON.stringify(output);
  const limit = (context && context.vars && Number(context.vars.maxWords)) || 160;
  const fails = [];

  const w = words(t);
  if (w > limit) fails.push(`${w} words (limit ${limit}) — wall of text`);

  const b = bulletCount(t);
  if (b > 4) fails.push(`${b} consecutive list items (max 4) — list is a memory test`);

  const q = questionCount(t);
  if (q > 1) fails.push(`${q} questions (max 1) — each open question is a held item`);

  if (PREAMBLE.test(t)) fails.push('opens with a preamble instead of the answer');
  if (BACKREF.test(t)) fails.push('unnamed back-reference ("as mentioned above" etc.)');
  if (MENU_TAIL.test(t)) fails.push('ends with an open-ended menu rather than one next action');

  const bold = boldCount(t);
  if (bold > 3) fails.push(`${bold} bolded spans — emphasis becomes noise`);

  return fails.length
    ? { pass: false, score: 0, reason: fails.join('; ') }
    : { pass: true, score: 1, reason: `form ok (${w} words, ${b} list items, ${q} questions, ${bold} bold)` };
};
