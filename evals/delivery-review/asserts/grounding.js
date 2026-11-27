// Criterion 3 — grounding (lenient parse). Nothing invented: every finding's evidence points
// at something that is actually in the material the reviewer was given.
//
// This is the criterion that catches the failure the prompt's own rules exist for — a finding
// nobody can locate is not actionable by the step that has to address it, and a test result
// not in verify.json is a claim the reviewer made up.
const { expected, source, lenient, groupHit, result } = require('./lib');

// A path-looking token: a file-ish ending from a known set, with an optional :line.
//
// The extension list is not decoration. The old pattern was any 1-6 character ending, and it
// clipped `mutation.survived` down to `mutation.surviv` and then reported that the reviewer
// had cited a file not in the diff. `mutation.survived` is a field in verify.json, and citing
// it is exactly what a reviewer handed mutation evidence should do. The assert was wrong, and
// a hand-written reference answer caught it before any model run.
const EXT = 'py|js|jsx|ts|tsx|java|kt|scala|rb|go|rs|cs|swift|sql|sh|yaml|yml|json|toml|ini|cfg|md|txt|html|css|tf|proto';
const PATHY = new RegExp(`[\\w./-]+\\.(?:${EXT})(?::\\d+)?\\b`, 'g');

module.exports = (output, context) => {
  const exp = expected(context);
  const src = source(context);
  const doc = lenient(output);
  if (!doc) return result(['no JSON could be recovered from the reply'], '');

  const problems = [];
  // The names of the artifacts the reviewer was handed are themselves legitimate evidence:
  // "verify.json reports status red" is grounded, and an earlier version of this check
  // rejected it because it only matched the files' *contents*, not their names. That was the
  // assert being wrong, caught by a reference answer rather than by a model run.
  const given = ['verify.json', 'story.md', 'implementation.json'];
  const material = `${src.diff}\n${src.story}\n${src.verify}\n${given.join('\n')}`.toLowerCase();

  (doc.findings || []).forEach((f, i) => {
    const ev = String((f && f.evidence) || '');
    if (!ev.trim()) {
      problems.push(`findings[${i}] has empty evidence`);
      return;
    }
    // Any path the evidence names must appear in the diff. A reviewer citing a file that is
    // not in the change is the clearest form of invention.
    for (const token of ev.match(PATHY) || []) {
      const file = token.split(':')[0].toLowerCase();
      if (file.length > 4 && !material.includes(file)) {
        problems.push(`findings[${i}] cites ${token}, which is not in the diff or the story`);
      }
    }
  });

  // Where ground truth names the file the real defect lives in, at least one finding must
  // point there — evidence that is merely plausible is not grounded.
  for (const p of exp.evidence_paths || []) {
    const hit = (doc.findings || []).some((f) => String((f && f.evidence) || '').includes(p));
    if (!hit) problems.push(`no finding cites ${p}, where the defect is`);
  }

  // A verdict that asserts a green suite against a verify.json reporting red.
  let verify = {};
  try { verify = JSON.parse(src.verify || '{}'); } catch (e) { verify = {}; }
  if (verify.passed === false) {
    const claimed = ['all tests pass', 'tests pass', 'suite is green', 'suite passes'];
    const txt = [(doc.findings || []).map((f) => `${f.finding} ${f.evidence}`).join(' '),
                 (doc.reviewers || []).map((r) => r.note || '').join(' ')].join(' ');
    if (groupHit(txt, claimed)) {
      problems.push('claims the suite passed while verify.json reports it red');
    }
  }
  return result(problems, 'every finding is locatable in the material given');
};
