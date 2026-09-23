// contract (strict): the SHAPE of the reply, judged on the reply exactly as
// given. This criterion owns every formatting penalty (preambles, trailing
// chatter, fences, extra revisions, burying the answer).
//
// spec.contract.type:
//   poem-only     the reply is the poem and nothing else: exactly three poem lines
//   poem-first    the reply opens with the three poem lines; a note may follow,
//                 capped at spec.contract.maxNoteWords
//   revisions     a critique offering between spec.contract.min and .max revised
//                 poems (stanzas other than the draft under review)
//   answer-first  the first sentence answers the question: it matches
//                 spec.contract.lead (a regex source)
const L = require('./lib');

module.exports = (output, context) => {
  const s = L.spec(context).contract;
  const text = L.normalize(output);
  const problems = [];

  if (s.type === 'poem-only' || s.type === 'poem-first') {
    if (/```/.test(text)) problems.push('code fence in reply');
    const lines = text.split('\n').map((l) => l.trim()).filter(Boolean);
    const head = lines.slice(0, 3);
    const opensWithPoem = head.length === 3 && head.every(L.isPoemLine);
    if (!opensWithPoem) {
      problems.push(`reply does not open with a 3-line poem (opens: ${JSON.stringify(lines[0] || '')})`);
    }
    const rest = lines.slice(3);
    if (s.type === 'poem-only' && opensWithPoem && rest.length) {
      problems.push(`text after the poem: ${JSON.stringify(rest.join(' ').slice(0, 80))}`);
    }
    if (s.type === 'poem-first') {
      const n = L.words(rest.join(' ')).length;
      if (s.maxNoteWords != null && n > s.maxNoteWords) {
        problems.push(`note after the poem is ${n} words (max ${s.maxNoteWords})`);
      }
    }
    return L.result(problems, `${s.type}: shape ok`);
  }

  if (s.type === 'revisions') {
    const draft = s.draft;
    const revs = L.stanzas(text).filter((st) => !(draft && L.sameStanza(st, draft)));
    const unique = revs.filter((st, i) => revs.findIndex((o) => L.sameStanza(o, st)) === i);
    const n = unique.length;
    if (n < s.min || n > s.max) {
      const want = s.min === s.max ? `exactly ${s.min}` : `${s.min}-${s.max}`;
      problems.push(`${n} revised poem(s) offered, want ${want}`);
    }
    return L.result(problems, `revisions: ${n} offered`);
  }

  if (s.type === 'answer-first') {
    const first = L.firstSentence(text);
    if (!new RegExp(s.lead, 'i').test(first)) {
      problems.push(`first sentence doesn't answer: ${JSON.stringify(first.slice(0, 100))}`);
    }
    return L.result(problems, 'answer-first: leads with the answer');
  }

  throw new Error(`unknown contract type ${s.type}`);
};
