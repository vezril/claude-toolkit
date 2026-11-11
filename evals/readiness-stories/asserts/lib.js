// Shared helpers for the readiness (story-planner) suite.
//
// The node under test emits a *set of markdown story files*, not JSON. That is what the
// readiness segment actually hands on — `story.json` was retired with `render-stories.py` —
// and it is what `lint-story.py` gates on the edge. So the asserts parse markdown, and the
// schema criterion shells out to the real linter rather than reimplementing its rules. An
// eval that judged stories by its own copy of the schema could pass a set the edge would
// reject, which is the exact gap this suite exists to close.

const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const PLUGIN_ROOT = path.join(ROOT, '..', '..');
const LINT_STORY = path.join(PLUGIN_ROOT, 'scripts', 'lint-story.py');

function caseId(context) {
  const id = context && context.vars && context.vars.case;
  if (!id) throw new Error('test is missing vars.case');
  return id;
}

const input = (c) => JSON.parse(fs.readFileSync(path.join(ROOT, 'inputs', caseId(c) + '.json'), 'utf8'));
const expected = (c) => JSON.parse(fs.readFileSync(path.join(ROOT, 'expected', caseId(c) + '.json'), 'utf8'));

// Lenient split, for the same reason the triage suite parses leniently: a formatting mistake
// should be penalised once, by the schema criterion, not again by every criterion that needs
// to read the content.
//
// The convention is `=== <relative path> ===` on its own line before each file. Fenced blocks
// are tolerated because models reach for them unprompted, and rejecting that would make the
// suite measure fence discipline instead of decomposition.
function storyFiles(output) {
  const text = String(output).replace(/\r\n/g, '\n');
  const parts = text.split(/^[=\-]{2,}\s*(\S+\.md)\s*[=\-]{2,}\s*$/m);
  const files = [];
  for (let i = 1; i < parts.length; i += 2) {
    let body = parts[i + 1] || '';
    body = body.replace(/^\s*```(?:markdown|md)?\s*\n/, '').replace(/\n```\s*$/, '');
    files.push({ name: parts[i].trim(), body: body.trim() + '\n' });
  }
  return files;
}

// Write the story set plus the source documents it may reference into a throwaway root, so
// `lint-story.py --root` can resolve `[Source: docs/prd.md#FR-1]`. Without the sources on
// disk every reference would fail and the schema criterion would measure the fixture rather
// than the node.
function materialise(files, sources) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'readiness-'));
  for (const [rel, body] of Object.entries(sources || {})) {
    const p = path.join(dir, rel);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, body);
  }
  const written = [];
  for (const f of files) {
    // Never outside the root: a model naming `../../etc/x.md` must not write there.
    const safe = path.normalize(f.name).replace(/^(\.\.(\/|\\|$))+/, '');
    const p = path.join(dir, safe);
    if (!p.startsWith(dir)) continue;
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, f.body);
    written.push(p);
  }
  return { dir, written };
}

// The real linter, as the edge runs it. Returns its stdout and exit code.
function lintStory(paths, root) {
  try {
    const out = execFileSync('python3', [LINT_STORY, ...paths, '--root', root],
      { encoding: 'utf8', timeout: 120000 });
    return { code: 0, out };
  } catch (e) {
    return { code: e.status === undefined ? -1 : e.status, out: (e.stdout || '') + (e.stderr || '') };
  }
}

// Requirement ids mentioned anywhere in a story set.
function requirementIds(text) {
  return new Set((String(text).match(/\b(?:FR|CAP)-\d+\b/g) || []));
}

const result = (problems, ok) => (problems.length
  ? { pass: false, score: 0, reason: problems.join('; ') }
  : { pass: true, score: 1, reason: ok });

module.exports = {
  ROOT, PLUGIN_ROOT, caseId, input, expected,
  storyFiles, materialise, lintStory, requirementIds, result,
};
