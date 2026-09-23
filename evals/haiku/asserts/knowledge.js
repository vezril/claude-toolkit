// knowledge (lenient): is what the reply SAYS about haiku correct?
//
// spec.knowledge (any combination; every present check must hold):
//   groups       list of keyword groups; each group must match somewhere in the
//                reply (an alternative matches as a case-insensitive substring)
//   regexAll     list of regex sources; each must match
//   forbid       list of regex sources; none may match
//   verdict      { expect, other }: the first sentence names `expect` as the
//                verdict, and doesn't name `other` except as "not a(n) <other>"
//   firstSeason  the first season word in the reply must be one of these
//   scope        "reply" (default) or "note": check only the text after the
//                first poem (for "write X and tell me about it" cases)
//   no575Endorsement  no sentence presents 5-7-5 as the standard: every
//                sentence that mentions 5-7-5 must also negate or hedge it
//   draftCounts  { lines, counts }: every syllable count the reply states for
//                a line of the draft under review must be that line's true count
const L = require('./lib');

const SEASONS = /\b(spring|summer|autumn|fall|winter)\b/i;
const FIVE75 = /5\s*[-–]\s*7\s*[-–]\s*5/;
// Anything in the same sentence that keeps a 5-7-5 mention from being an
// endorsement: a negation, or wording that treats the count as a constraint.
const HEDGE = /(?<![a-z])(no|not|never|nor|none)(?![a-z])|n't\b|myth|misconception|rarely|seldom|ignor|optional|loose|approximat|mistranslat|breaks? from|many (?:good|english|modern|respected|contemporary)|most english|modern english|english-language|forc|filler|padd|cram|artificial|constrain/i;

function sentences(text) {
  return text.replace(/\*\*|__/g, '').split(/(?<=[.!?])\s+|\n+/).map((s) => s.trim()).filter(Boolean);
}

function esc(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+');
}

// Returns the wrong-count claims a reply makes about the draft's lines.
function wrongCounts(text, lines, counts) {
  const wrong = [];
  lines.forEach((line, i) => {
    const want = counts[i];
    // (a) the quoted line, then a number: `"The autumn leaves fall" = 6`, `("…") is 7`
    const quoted = new RegExp(`["“”'‘’]${esc(line)}["“”'‘’]\\)?\\s*(?:=|is|has|:|—|–|-|\\()?\\s*(\\d{1,2})\\b`, 'gi');
    for (const m of text.matchAll(quoted)) if (+m[1] !== want) wrong.push(`"${line}" called ${m[1]} (is ${want})`);
    // (b) "line 2 … 6 syllables", without running into another line's mention
    const byIndex = new RegExp(`\\bline\\s*${i + 1}\\b(?:(?!\\bline\\s*[123]\\b)[^.\\n]){0,80}?\\b(\\d{1,2})\\s*syllables?`, 'gi');
    for (const m of text.matchAll(byIndex)) if (+m[1] !== want) wrong.push(`line ${i + 1} called ${m[1]} syllables (is ${want})`);
    // (b') "line 3 has 6", "line 1 is 5", "line 2: 7"
    const bare = new RegExp(`\\bline\\s*${i + 1}\\s*(?:has|is|=|:)\\s*(?:only\\s+|just\\s+)?(\\d{1,2})\\b`, 'gi');
    for (const m of text.matchAll(bare)) if (+m[1] !== want) wrong.push(`line ${i + 1} called ${m[1]} (is ${want})`);
  });
  // (c) a stated overall count ("count looks like 2-6-4"), other than the 5-7-5 template
  const truth = counts.join('-');
  for (const s of sentences(text)) {
    if (!/\bcount|\bscans?\b/i.test(s)) continue;
    for (const m of s.matchAll(/\b(\d{1,2})\s*[-–]\s*(\d{1,2})\s*[-–]\s*(\d{1,2})\b/g)) {
      const got = `${m[1]}-${m[2]}-${m[3]}`;
      if (got !== '5-7-5' && got !== truth) wrong.push(`count given as ${got} (is ${truth})`);
    }
  }
  return [...new Set(wrong)];
}

module.exports = (output, context) => {
  const k = L.spec(context).knowledge;
  let text = L.lenient(output);
  const problems = [];

  if (k.scope === 'note') {
    // Everything after the poem, wherever the poem sits (a preamble belongs to
    // contract's penalty, not to this one).
    const poem = L.extractPoem(text);
    const lines = text.split('\n');
    const end = poem ? lines.findIndex((l) => L.bare(l) === poem[2]) : -1;
    text = end >= 0 ? lines.slice(end + 1).join('\n') : '';
  }

  (k.groups || []).forEach((g, i) => {
    if (!L.groupMatches(text, g)) problems.push(`missing group ${i + 1} (${g.slice(0, 4).join(' | ')}…)`);
  });

  (k.regexAll || []).forEach((src) => {
    if (!new RegExp(src, 'i').test(text)) problems.push(`missing /${src}/`);
  });

  (k.forbid || []).forEach((src) => {
    const m = text.match(new RegExp(src, 'i'));
    if (m) problems.push(`says ${JSON.stringify(m[0])}`);
  });

  if (k.verdict) {
    // The verdict is the first label the first sentence names, after dropping
    // negated or comparative mentions ("not a senryu", "unlike a haiku",
    // "senryu-like"). A later contrast ("…the hallmark of senryu") is not a verdict.
    // Lookarounds instead of \b: "senryū" ends in a non-ASCII letter.
    const either = `(?<![a-z])(${k.verdict.expect}|${k.verdict.other})(?![a-zū])`;
    const first = L.firstSentence(text).toLowerCase()
      .replace(new RegExp(`(?<![a-z])(not|unlike|rather than|instead of)\\s+(an?\\s+)?${either}`, 'g'), ' ')
      .replace(new RegExp(`${either}\\s*-\\s*like`, 'g'), ' ');
    const m = first.match(new RegExp(either));
    if (!m) problems.push(`first sentence names no verdict (want ${k.verdict.expect})`);
    else if (!new RegExp(`^(?:${k.verdict.expect})$`).test(m[1])) problems.push(`first sentence calls it a ${m[1]} (want ${k.verdict.expect})`);
  }

  if (k.no575Endorsement) {
    const endorse = sentences(text).find((s) => FIVE75.test(s) && !HEDGE.test(s));
    if (endorse) problems.push(`treats 5-7-5 as the standard: ${JSON.stringify(endorse.slice(0, 90))}`);
  }

  if (k.draftCounts) {
    const wrong = wrongCounts(text, k.draftCounts.lines, k.draftCounts.counts);
    if (wrong.length) problems.push(`wrong syllable counts: ${wrong.join('; ')}`);
  }

  if (k.firstSeason) {
    const m = text.match(SEASONS);
    const got = m ? m[1].toLowerCase() : 'none';
    if (!k.firstSeason.includes(got)) problems.push(`first season named is ${got}, want ${k.firstSeason.join('/')}`);
  }

  return L.result(problems, 'knowledge ok');
};
