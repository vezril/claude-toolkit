// Criterion 3 — fidelity (precision, lenient). Nothing invented:
// (a) every file-like token in the output appears in what the model was given;
// (b) every version-like or decimal number and every percentage appears there;
// (c) no issue/ticket references the source doesn't contain (#12, ABC-123,
//     "Closes #..."), which is the classic invented-Why move;
// (d) speculation presented as content ("may include bug fixes...", "likely
//     improves performance"): a guess about what a change does is an invention;
// (e) case-specific inventions listed in expected/<case>.json -> forbidden.
// Deterministic on purpose: no LLM judge decides what "invented" means.

const { expected, sourceText, lenient, result } = require('./lib');

const FILE_RE = /[A-Za-z0-9_.\/-]*[A-Za-z0-9_-]\.(?:scala|sbt|py|js|ts|tsx|java|kt|go|rs|md|ya?ml|conf|xml|json|toml|txt|sh|sql|proto)\b/g;
const NUM_RE = /\b\d+(?:\.\d+)+\b|\b\d+(?:\.\d+)?%/g;
const TICKET_RE = /(?:^|[^A-Za-z0-9/])(#\d+|[A-Z][A-Z0-9]+-\d+)\b/g;
const SPECULATION_RE = /\b(may|might|could|likely|probably|presumably|possibly|potentially|typically|usually|generally|often)\s+(also\s+)?(include|includes|bring|brings|contain|improve|improves|fix|fixes|address|resolve|help|enhance|affect|impact)\b[^.\n]*/i;

module.exports = (output, context) => {
  const exp = expected(context);
  const text = lenient(output);
  const src = sourceText(context);
  const srcLower = src.toLowerCase();
  const problems = [];

  const invented = (tokens) => [...new Set(tokens)].filter((t) => !srcLower.includes(t.toLowerCase()));

  // A path shortened with "..." (client/src/.../Spec.scala) names a real file; judge it by
  // its file name. Every other file-like token must appear as written.
  const fileTokens = (text.match(/[^\s`'"()\[\]]*\.\.\.[^\s`'"()\[\]]*|[^\s`'"()\[\]]*…[^\s`'"()\[\]]*/g) || [])
    .map((t) => t.split(/\.\.\.|…/).pop().replace(/^[\/]+/, ''))
    .concat((text.replace(/[^\s`'"()\[\]]*(\.\.\.|…)[^\s`'"()\[\]]*/g, ' ').match(FILE_RE) || []).map((t) => t.replace(/^[.\/]+/, '')))
    .filter((t) => FILE_RE.test(t) && (FILE_RE.lastIndex = 0, true));
  const files = invented(fileTokens);
  if (files.length) problems.push('files not in the diff: ' + files.join(', '));

  const nums = invented(text.match(NUM_RE) || []);
  if (nums.length) problems.push('numbers not in the diff: ' + nums.join(', '));

  const tickets = invented([...text.matchAll(TICKET_RE)].map((m) => m[1]));
  if (tickets.length) problems.push('issue/ticket references not in the source: ' + tickets.join(', '));

  const spec = text.match(SPECULATION_RE);
  if (spec) problems.push('speculation presented as fact: "' + spec[0].slice(0, 80) + '"');

  for (const f of exp.forbidden || []) {
    const m = text.match(new RegExp(f.pattern, 'i'));
    if (m) problems.push('invented: ' + f.why + ' ("' + m[0] + '")');
  }

  return result(problems, 'fidelity ok: no invented files, numbers, tickets, speculation or case-specific claims');
};
