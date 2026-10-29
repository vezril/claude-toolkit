// Shared helpers. The provider's output is JSON: { reply, model, changes, tools, denied }.
const TODAY = 'Calendar/Notes/Daily/2026-10-14.md';
const WEEK = 'Calendar/Notes/Weeks/2026-W42.md';
const TRIGGERS = ['boring', 'unpleasant', 'frustrating', 'far off', 'unstructured', 'meaningless'];
const TIME = /\b(\d{1,2}(:\d\d)?\s?(am|pm|h)\b|\d{1,2}:\d\d|noon|tonight|this (morning|afternoon|evening)|after (coffee|breakfast|lunch|dinner|work))/i;
const PLACE = /\b(desk|table|kitchen|couch|sofa|office|living room|bedroom|caf[eé]|library|balcony|bed|computer|laptop)\b/i;

function parse(output) {
  try { return JSON.parse(output); } catch { return { reply: String(output || ''), changes: [], tools: [], denied: [] }; }
}
// Text the user reads, minus fenced code (a quoted note block isn't a question to him).
function prose(reply) { return reply.replace(/```[\s\S]*?```/g, ''); }
// Questions put to him. Self-answered labels are not: "**Whose goal?** ..." (bold-wrapped)
// with an answer after it on the same line, or "Sepia-toned? No." (answered in the next word).
// A bold question that ends its line is still a question.
function questions(reply) {
  const t = prose(reply).split('\n').filter((l) => !/^\s*\|/.test(l)).join('\n') // table cells are data
    .replace(/\*\*[^*\n]*\?\*\*(?=[ \t]*[^\s])/g, '').replace(/\?\s+(yes|no)\b/gi, '.')
    .replace(/^(\s*(?:[-*]|\d+[.)])\s+)(?!(?:want|do|does|did|should|shall|can|could|would|will|is|are|ok|okay|any|which|what|how|when|where|why|ready|sound|good)\b)((?:\S+\s+){0,3}\S+)\?(?=[ \t]+\S)/gim, '$1$2:'); // "- Whose goal? Could reads..."
  return (t.match(/\?(?=[\s*_)"'`]|$)/g) || []).length;
}
function words(reply) { return prose(reply).split(/\s+/).filter(Boolean).length; }
function listItems(reply) {
  return prose(reply).split('\n').filter((l) => /^\s*([-*•]|\d+[.)])\s+\S/.test(l) && !/^\s*\|/.test(l)).length;
}
// Lines present in `after` beyond those in `before` (multiset difference).
function added(change) {
  const pool = {};
  for (const l of (change.before || '').split('\n')) pool[l] = (pool[l] || 0) + 1;
  const out = [];
  for (const l of (change.after || '').split('\n')) {
    if (pool[l]) pool[l]--; else out.push(l);
  }
  return out.join('\n');
}
function change(o, p) { return (o.changes || []).find((c) => c.path === p); }
function frontmatter(s) { const m = /^---\n[\s\S]*?\n---\n/.exec(s || ''); return m ? m[0] : ''; }
function result(fails, ok) {
  return fails.length ? { pass: false, score: 0, reason: fails.join('; ') } : { pass: true, score: 1, reason: ok };
}
module.exports = { TODAY, WEEK, TRIGGERS, TIME, PLACE, parse, prose, questions, words, listItems, added, change, frontmatter, result };
