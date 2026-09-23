// craft (lenient): the conventions of an English-language haiku, checked on the
// poem wherever it sits in the reply (so a preamble costs contract, not craft).
//
// spec.craft:
//   source      "poem" (default: the first 3-line stanza) or "revision" (the first
//               stanza that isn't spec.craft.draft, for critique cases)
//   syllables   "band" (default): total within [min, max]
//               "575": per line 5/7/5, which is what the user explicitly asked for
//   min, max    band bounds (defaults 6 and 15; see the iteration log, Setup)
//   kigo        optional list: at least one season word from it must appear
//   forbid      optional list: none of these may appear (wrong-climate kigo, etc.)
//   banExtra    optional list: case-specific telling words, added to the default list
//
// Always checked: no end rhyme, no overt simile, no telling words.
const L = require('./lib');

module.exports = (output, context) => {
  const c = L.spec(context).craft;
  const problems = [];

  let poem;
  if (c.source === 'revision') {
    poem = L.stanzas(output).find((st) => !L.sameStanza(st, c.draft)) || null;
  } else {
    poem = L.extractPoem(output);
  }
  if (!poem) return L.result(['no 3-line poem found in the reply'], '');
  const text = poem.join('\n');
  const counts = poem.map(L.lineSyllables);
  const total = counts.reduce((a, b) => a + b, 0);

  if (c.syllables === '575') {
    const want = [5, 7, 5];
    if (counts.some((n, i) => n !== want[i])) problems.push(`asked for 5-7-5, got ${counts.join('-')}`);
  } else {
    const min = c.min != null ? c.min : 6;
    const max = c.max != null ? c.max : 15;
    if (total < min || total > max) problems.push(`${total} syllables (${counts.join('-')}), want ${min}-${max}`);
  }

  const rhyme = L.endRhyme(poem);
  if (rhyme) problems.push(`end rhyme ${rhyme}`);

  const simile = L.SIMILE.find((re) => re.test(text));
  if (simile) problems.push(`overt simile (${text.match(simile)[0]})`);

  const telling = L.findTerms(text, L.TELLING_WORDS.concat(c.banExtra || []));
  if (telling.length) problems.push(`telling words: ${telling.join(', ')}`);

  if (c.kigo && !L.findTerms(text, c.kigo).length) problems.push('no season word from the expected set');

  const bad = L.findTerms(text, c.forbid || []);
  if (bad.length) problems.push(`forbidden for this request: ${bad.join(', ')}`);

  return L.result(problems, `craft ok (${counts.join('-')} = ${total})`);
};
