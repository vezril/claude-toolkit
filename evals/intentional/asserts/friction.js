// Criterion 1, friction (the ADHD contract): what the reply costs him to read and answer.
// At most q_max questions (default 3), at most max_items list items when set, at most
// max_words words when set, no em dashes anywhere he reads (reply or written lines),
// no guilt-tripping language. Says nothing about whether the content is right.
const L = require('./lib');
module.exports = (output, { vars }) => {
  const o = L.parse(output);
  const r = o.reply || '';
  const fails = [];
  const q = L.questions(r), qMax = vars.q_max ?? 3;
  if (q > qMax) fails.push(`${q} questions (max ${qMax})`);
  if (vars.max_items != null && L.listItems(r) > vars.max_items) fails.push(`${L.listItems(r)} list items (max ${vars.max_items})`);
  if (vars.max_words != null && L.words(r) > vars.max_words) fails.push(`${L.words(r)} words (max ${vars.max_words})`);
  const written = (o.changes || []).map(L.added).join('\n');
  if (/—/.test(r)) fails.push('em dash in reply');
  if (/—/.test(written)) fails.push('em dash in written note');
  const guilt = /\b(you should have|you shouldn't have|unfortunately|you failed|failed to|disappointing|no excuse|lazy|again\?!)/i.exec(r);
  if (guilt) fails.push(`guilt language: "${guilt[0]}"`);
  return L.result(fails, `${q} questions, ${L.words(r)} words`);
};
