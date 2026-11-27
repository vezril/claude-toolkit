// Criterion 4 — assumptions (lenient parse). Does the review surface what the change takes
// on faith about something it does not own?
//
// This criterion exists because of eight review comments on real PRs, four of whose
// *Required* lines literally begin with the word "Confirm": confirm this API accepts a
// non-empty target, confirm that exception means what you read it as, confirm this callback
// cannot fire there. The code may well have been correct. It was not *shown* to be, so the
// burden landed on the reviewer — and the reviewer is the most expensive place to put it.
//
// It is deliberately two-sided, and the second side is what makes it a criterion rather than
// a recall bonus:
//
//   RECALL    — where ground truth names a dependency the diff leans on, some finding must
//               raise it as unverified.
//   PRECISION — every assumption the review *does* raise must name something that is actually
//               in the material. "Confirm FooService is idempotent" about a FooService nobody
//               mentioned is a reviewer inventing homework, and a reviewer that demands
//               confirmation of everything is as useless as one that demands none.
//
// Precision applies to every case with no ground truth needed, so this is load-bearing on all
// of them and not only on the six written for it. `grounding` does not cover it: that check
// matches path-shaped tokens in `evidence`, and these are API and symbol names in prose.
const { expected, source, lenient, result } = require('./lib');

// A sentence that makes an assumption claim.
const CLAIM = /\b(assum\w*|confirm\w*|unverified|unestablished|undemonstrated|verify that|precondition|relies on|taken on faith|nothing establishes|not established|no evidence|cannot tell|cannot confirm|is not shown)\b/i;

// An identifier worth checking: CamelCase, snake_case, or dotted — the shapes an API or symbol
// name takes. Plain English words are not checkable and are not penalised.
const IDENT = /\b(?:[A-Z][a-z0-9]+[A-Z][A-Za-z0-9]*|[a-z][a-z0-9]*_[a-z0-9_]+|[A-Za-z_][\w]*\.[A-Za-z_][\w]*)\b/g;

// Words that happen to match the identifier shapes above but are prose, not symbols. Without
// this list a review writing "non-empty" or "read-only" would be asked to ground it.
const NOT_SYMBOLS = new Set([
  'non_empty', 'read_only', 'write_only', 'compare_and_set', 'check_and_set', 'if_empty',
  'TimeoutError', 'KeyError', 'ValueError', 'TypeError', 'OSError', 'AssertionError',
  'JavaScript', 'TypeScript', 'GitHub', 'JSON',
]);

module.exports = (output, context) => {
  const exp = expected(context);
  const src = source(context);
  const doc = lenient(output);
  if (!doc) return result(['no JSON could be recovered from the reply'], '');

  const problems = [];
  const findings = doc.findings || [];
  // The artifacts the reviewer was HANDED are part of the material, not inventions: a
  // finding saying "verify.json does not confirm this" is grounded. `grounding.js` already
  // learned this and I repeated the omission here, which cost three otherwise-correct rows.
  const given = ['verify.json', 'story.md', 'implementation.json', 'review.json'];
  const material = `${src.diff}\n${src.story}\n${src.verify}\n${given.join('\n')}`;

  // --- recall
  const text = [findings.map((f) => `${f.finding || ''} ${f.evidence || ''}`).join('\n'),
                (doc.reviewers || []).map((r) => r.note || '').join('\n')].join('\n');
  for (const group of exp.assumptions_expected || []) {
    const hit = group.some((alt) => text.toLowerCase().includes(String(alt).toLowerCase()));
    if (!hit) {
      problems.push(`no finding raises what the change assumes about: ${group.join(' | ')}`);
      continue;
    }
    // Naming it in passing is not raising it: the FINDING that names the dependency has to
    // also say the thing is unestablished, or the review has only described the code back.
    //
    // Scoped to the finding rather than to the sentence. A reference answer wrote "nothing
    // establishes that StartIndexJob accepts a non-empty dataset" in one sentence and "I
    // cannot confirm that precondition" in the next, which is good reviewing and which a
    // same-sentence rule rejected. The mutant that only describes the call still dies,
    // because its finding carries no claim language anywhere.
    const named = group.find((alt) => text.toLowerCase().includes(String(alt).toLowerCase()));
    const carriers = [...findings.map((f) => `${f.finding || ''} ${f.evidence || ''}`),
                      ...(doc.reviewers || []).map((r) => r.note || '')];
    const raised = carriers.some((c) =>
      c.toLowerCase().includes(String(named).toLowerCase()) && CLAIM.test(c));
    if (!raised) {
      problems.push(`mentions ${named} but never says it is unverified`);
    }
  }

  // --- precision
  findings.forEach((f, i) => {
    const body = `${(f && f.finding) || ''} ${(f && f.evidence) || ''}`;
    for (const sentence of body.split(/(?<=[.;:!?])\s+|\n/)) {
      if (!CLAIM.test(sentence)) continue;
      for (const ident of sentence.match(IDENT) || []) {
        if (NOT_SYMBOLS.has(ident) || ident.length < 5) continue;
        // A more specific spelling of something that IS in the material is grounded:
        // the diff calls `bisect(...)` and a reviewer writing `bisect_right` has named the
        // real function, not invented one. Only a stem nobody mentioned is an invention.
        const stem = ident.split(/[._]/)[0];
        if (!material.includes(ident) && !(stem.length > 4 && material.includes(stem))) {
          problems.push(
            `findings[${i}] demands confirmation about ${ident}, which is not in the material`);
        }
      }
    }
  });

  return result(problems, `${(exp.assumptions_expected || []).length} expected assumption(s) `
                          + 'raised, none invented');
};
