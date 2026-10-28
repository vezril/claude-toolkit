// pointer: the description is a context pointer. Leading word up front, every branch
// triggered, no synonym padding, no identity the body already carries, short.
const { spec, result, files, mainFile, description, has, count, words } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const pt = s.pointer;
  const d = s.descriptionOnly
    ? ((String(output).match(/^\s*description:\s*(.+)$/m) || [null, String(output).trim()])[1]).replace(/^["']|["']$/g, '').trim()
    : description(mainFile(files(output), s).text);
  if (!d) return result(['no description found'], '');
  const w = words(d);
  const p = [];
  if (w.length > pt.maxWords) p.push(`${w.length} words (max ${pt.maxWords})`);
  if (!has(pt.lead, w.slice(0, 6).join(' '))) p.push(`leading word (${pt.lead}) not in the first six words: "${w.slice(0, 6).join(' ')}"`);
  for (const b of pt.branches) if (!has(b.pattern, d)) p.push(`branch ${b.id} has no trigger`);
  // Synonym padding is distinct names for one branch, not repeats of the leading word.
  const syn = pt.synonyms.distinct.filter((re) => has(re, d));
  if (syn.length > pt.synonyms.max) p.push(`${syn.length} distinct synonyms for one branch (max ${pt.synonyms.max})`);
  if (has(pt.identity, d)) p.push('restates identity ("this skill…/helps you")');
  return result(p, `pointer ok (${w.length} words)`);
};
