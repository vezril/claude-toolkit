// Shared helpers for the haiku suite.
//
// Every case has a spec in expected/<case>.json. Each of the three asserts
// (contract, craft, knowledge) reads only its own section of that spec, and a
// test only carries the asserts whose section exists, so no criterion is ever
// padded with a free pass.
//
// Two views of the output:
//   - strict: the reply exactly as given (contract owns every formatting penalty)
//   - lenient: fences dropped and the poem located wherever it sits, so a
//     preamble is penalized once, by contract, and not again by craft.

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

function caseId(context) {
  const id = context && context.vars && context.vars.case;
  if (!id) throw new Error('test is missing vars.case');
  return id;
}

function spec(context) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, 'expected', caseId(context) + '.json'), 'utf8'));
}

function result(problems, okReason) {
  if (problems.length) return { pass: false, score: 0, reason: problems.join('; ') };
  return { pass: true, score: 1, reason: okReason };
}

// ── text views ──────────────────────────────────────────────────────────────

function normalize(output) {
  return String(output == null ? '' : output).replace(/\r\n?/g, '\n').trim();
}

// Lenient: drop every code-fence line, keep the content.
function lenient(output) {
  return normalize(output)
    .split('\n')
    .filter((l) => !/^\s*```/.test(l))
    .join('\n');
}

// Strip presentation that doesn't change the words: blockquote markers,
// wrapping emphasis, wrapping quotes.
function bare(line) {
  let s = String(line).trim().replace(/^>\s?/, '').trim();
  s = s.replace(/^(\*\*|\*|__|_)(.*)\1$/, '$2').trim();
  s = s.replace(/^["“'‘](.*)["”'’]$/, '$1').trim();
  return s;
}

function words(text) {
  return String(text).toLowerCase().match(/[a-z]+(?:['’][a-z]+)*/g) || [];
}

// A line that could be part of a poem: short, not a heading/bullet/label, and
// not chat framing ("Here's one", "Sure", a line that talks about "haiku").
function isPoemLine(line) {
  const raw = String(line).trim();
  if (!raw) return false;
  if (/^(#|[-*•]\s|\d+[.)]\s)/.test(raw)) return false;
  const b = bare(raw);
  if (!b || /:$/.test(b)) return false;
  if (/\bhaikus?\b|^(here|sure|certainly|of course)\b/i.test(b)) return false;
  const n = words(b).length;
  return n >= 1 && n <= 10;
}

// All 3-line stanzas in the text, in order. A stanza is a run of exactly three
// consecutive poem lines (bounded by blank lines, prose, or the ends of the
// text), or a single line written as "part one / part two / part three".
function stanzas(text) {
  const out = [];
  const ls = lenient(text).split('\n').map((l) => l.trim());
  let run = [];
  const flush = () => {
    if (run.length === 3) out.push(run.map(bare));
    run = [];
  };
  for (const l of ls) {
    const parts = bare(l).split(/\s+\/\s+/);
    if (parts.length === 3 && parts.every((p) => isPoemLine(p))) {
      flush();
      out.push(parts.map((p) => p.trim()));
    } else if (isPoemLine(l)) {
      run.push(l);
    } else {
      flush();
    }
  }
  flush();
  return out;
}

// The poem in a reply, found leniently: the first 3-line stanza anywhere.
function extractPoem(output) {
  const s = stanzas(output);
  return s.length ? s[0] : null;
}

function sameStanza(a, b) {
  const k = (lines) => words(lines.join(' ')).join(' ');
  return k(a) === k(b);
}

// First sentence of the reply, with markdown decoration removed.
function firstSentence(output) {
  const t = lenient(output)
    .split('\n')
    .map((l) => l.replace(/^#+\s*/, '').replace(/\*\*|__/g, '').trim())
    .filter(Boolean)
    .join('\n');
  const m = t.match(/^[\s\S]*?(?:[.!?](?=\s|$)|\n|$)/);
  return m ? m[0].trim() : t;
}

// ── syllables (heuristic, calibrated in calibration/syllables.js) ──────────

// Words the regex heuristic gets wrong and that turn up in haiku.
const SYLLABLE_EXCEPTIONS = {
  the: 1, fire: 1, hour: 1, our: 1, flower: 2, flowers: 2, poem: 2, poems: 2,
  quiet: 2, being: 2, lion: 2, idea: 3, every: 2, evening: 2, evenings: 2,
  different: 2, family: 3, business: 2, heron: 2, herons: 2, lighthouse: 2,
  lighthouses: 3, create: 2, science: 2, violet: 3, violets: 3, diamond: 2,
  maybe: 2, someone: 2, somewhere: 2, everyone: 3, cafe: 2, recipe: 3,
  naive: 2, cruel: 2, fuel: 2, dual: 2, real: 1, area: 3, video: 3,
  radio: 3, piano: 3, poet: 2, poets: 2, riot: 2, trial: 2,
  whistle: 2, castle: 2, apple: 2, maple: 2, little: 2, candle: 2,
  toboggan: 3, sugaring: 3, kawazu: 3, furuike: 4, eaves: 1, eave: 1,
  snowplow: 2, snowplows: 2, highway: 2, anyone: 3, iron: 2, prayer: 1,
  prayers: 1, layer: 2, layers: 2, player: 2, mayor: 2, museum: 3,
  firefly: 2, fireflies: 2, created: 3, creating: 3, creation: 3, react: 2,
  reacted: 3, beautiful: 3, beauty: 2, aches: 1, headaches: 2, montreal: 3,
  carrier: 3, carriers: 3,
};

// One-syllable words ending in a silent e that start compounds (sidewalk,
// lifetime, pinecone): count the two halves separately.
const SILENT_E_STEMS = /^(side|home|life|stone|lake|pine|time|grave|rose|fire|cake|rice|face|gate|wine|whale|snake|grape|horse|house|base|space|place|note|tide|shore|bone|smoke|plane|stove|flake|fence|nose|hope|name|safe|wide|lane)(?=[^aeiouy][a-z]{2,})/;

function syllables(word) {
  let w = String(word).toLowerCase().replace(/['’]s$/, '').replace(/[^a-z]/g, '');
  if (!w) return 0;
  if (SYLLABLE_EXCEPTIONS[w] != null) return SYLLABLE_EXCEPTIONS[w];
  const stem = w.match(SILENT_E_STEMS);
  if (stem && !/(?:ful|fully|less|lessly|lessness|ly|liness|ment|ments|ness|some)$/.test(w.slice(stem[1].length)) ) {
    return syllables(stem[1]) + syllables(w.slice(stem[1].length));
  }
  if (w.length <= 3) return 1;
  let extra = 0;
  if (/[td]ed$/.test(w)) extra++; // wanted, folded: the -ed is its own syllable
  if (/(?:[cgsxz]|ch|sh)es$/.test(w)) extra++; // rises, glasses, pages: so is this -es
  if (/[^aeiouy]e(?:ful|fully|fulness|less|lessly|lessness|ly|liness|ment|ments|ness|some)$/.test(w)) extra--; // lonely, peaceful, loneliness: silent e
  let s;
  if (/[aeiouy]les?$/.test(w)) s = w.replace(/es?$/, ''); // whole, smiles: silent e after vowel+l
  else s = w.replace(/(?:[^laeiouy]es|[^laeiouy]ed|[^laeiouy]e)$/, '');
  s = s.replace(/^y/, '');
  const groups = s.match(/[aeiouy]{1,2}/g);
  return Math.max(1, (groups ? groups.length : 1) + extra);
}

function lineSyllables(line) {
  // Split hyphenated compounds; numbers count their spoken words roughly as 1 each.
  return String(line)
    .split(/[\s\-–—\/]+/)
    .filter(Boolean)
    .reduce((n, w) => n + (/\d/.test(w) ? 1 : syllables(w)), 0);
}

// ── rhyme (end-of-line, heuristic) ──────────────────────────────────────────

// Unstressed endings that match without sounding like a rhyme.
const WEAK_ENDINGS = new Set(['er', 'ers', 'ed', 'es', 'y', 'ly', 'le', 'les', 'ing', 'ings', 'en', 'on', 'a']);

function rhymeKey(word) {
  const w = String(word).toLowerCase().replace(/[^a-z]/g, '');
  const m = w.match(/[aeiouy]+[^aeiouy]*$/);
  return m ? m[0] : '';
}

// Returns a description of the first rhyming pair of line endings, or null.
function endRhyme(lines) {
  const ends = lines.map((l) => {
    const ws = words(l);
    return ws.length ? ws[ws.length - 1] : '';
  });
  for (let i = 0; i < ends.length; i++) {
    for (let j = i + 1; j < ends.length; j++) {
      const a = ends[i], b = ends[j];
      if (!a || !b || a === b || a.length < 3 || b.length < 3) continue;
      const ka = rhymeKey(a), kb = rhymeKey(b);
      if (ka && ka === kb && ka.length >= 2 && !WEAK_ENDINGS.has(ka)) return `"${a}" / "${b}"`;
    }
  }
  return null;
}

// ── word lists ─────────────────────────────────────────────────────────────

// Match a whole word (or phrase) with a small set of inflectional suffixes,
// so "sad" catches "sadly"/"sadness" but not "saddle". A final consonant may
// double before the suffix ("drip" catches "dripping", "mud" catches "muddy").
function wordRegex(term) {
  const t = String(term).toLowerCase();
  const esc = t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+');
  const last = t.slice(-1);
  const dbl = /[bcdfgklmnprstvz]/.test(last) ? `(?:${last}(?=y|ed|ing|er))?` : '';
  return new RegExp(`(^|[^a-z])${esc}${dbl}(s|es|ly|ness|ful|y|d|ed|ing)?(?![a-z])`, 'i');
}

function findTerms(text, terms) {
  const t = String(text).toLowerCase();
  return (terms || []).filter((term) => wordRegex(term).test(t));
}

// Words that interpret instead of show (research note, "show the cause, not the feeling").
const TELLING_WORDS = [
  'sad', 'sorrow', 'grief', 'lonely', 'loneliness', 'happy', 'happiness', 'joy',
  'beautiful', 'beauty', 'lovely', 'gorgeous', 'wonderful', 'magical', 'majestic',
  'serene', 'serenity', 'peaceful', 'tranquil', 'tranquility', 'melancholy',
  'nostalgia', 'nostalgic', 'bliss', 'cozy', 'cosy', 'comforting',
  'i feel', 'i felt', 'my heart', 'my soul',
];

const SIMILE = [
  /\blike\s+(a|an|the|some|my|his|her|their|our|its|tiny|little)\b/i,
  /\bas\s+if\b/i,
  /\bas\s+though\b/i,
  /\bas\s+[a-z]+\s+as\b/i,
  /\bresembl/i,
];

// Knowledge groups: every group must match; an alternative matches as a
// case-insensitive substring (a group is a list of accepted phrasings).
function groupMatches(text, group) {
  const t = String(text).toLowerCase();
  return group.some((alt) => t.includes(String(alt).toLowerCase()));
}

module.exports = {
  spec, result, normalize, lenient, bare, words, isPoemLine, stanzas, extractPoem,
  sameStanza, firstSentence, syllables, lineSyllables, endRhyme, rhymeKey,
  findTerms, TELLING_WORDS, SIMILE, groupMatches,
};
