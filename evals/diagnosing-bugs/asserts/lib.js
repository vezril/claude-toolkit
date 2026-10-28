// Shared helpers for the diagnosing-bugs asserts. The agent edits a project in its temp
// world; the asserts grade what it left behind (against the pristine copy in fixture/)
// and what it did (the tool calls). The first assert to run for a case snapshots the
// project into $SNAP/<case>, and every assert reads the snapshot, so rescore.js can
// regrade a recorded run after the world is gone (WORLD unset, SNAP set). sample.log
// (2 MB, unchanged by any fix) is left out of snapshots; no assert reads it.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const spec = (context) => JSON.parse(fs.readFileSync(path.join(ROOT, 'expected', context.vars.case + '.json'), 'utf8'));
const criteria = (s) => s.criteria;
const result = (problems, ok) =>
  problems.length ? { pass: false, score: 0, reason: problems.join('; ') } : { pass: true, score: 1, reason: ok };

const SKIP = (rel) => /(^|\/)__pycache__(\/|$)|\.pyc$|(^|\/)sample\.log$|(^|\/)\.DS_Store$/.test(rel);
function walk(dir, base = dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name), rel = path.relative(base, p);
    if (SKIP(rel)) continue;
    if (e.isDirectory()) walk(p, base, out); else out.push(rel);
  }
  return out;
}
function project(context) {
  const s = spec(context);
  const snap = path.join(process.env.SNAP, context.vars.case);
  if (process.env.WORLD && !fs.existsSync(snap)) {
    const src = path.join(process.env.WORLD, s.dir);
    fs.mkdirSync(snap, { recursive: true });
    for (const rel of walk(src)) {
      fs.mkdirSync(path.dirname(path.join(snap, rel)), { recursive: true });
      fs.copyFileSync(path.join(src, rel), path.join(snap, rel));
    }
  }
  return snap;
}
const pristine = (s) => path.join(ROOT, 'fixture', s.dir);
const isTest = (rel) => /(^|\/)tests?\//.test(rel) || /(^|\/)test_[^/]*\.py$|_test\.py$/.test(rel);
const read = (p) => (fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : null);
function changed(s, snap) {
  const now = walk(snap), before = new Set(walk(pristine(s)));
  return {
    added: now.filter((r) => !before.has(r)),
    modified: now.filter((r) => before.has(r) && read(path.join(snap, r)) !== read(path.join(pristine(s), r))),
  };
}
function unittest(dir, seed, modules = []) {
  const env = { ...process.env, PYTHONDONTWRITEBYTECODE: '1' };
  if (seed != null) env.PYTHONHASHSEED = String(seed);
  const r = spawnSync('python3', ['-m', 'unittest', '-q', ...modules], { cwd: dir, env, encoding: 'utf8', timeout: 60000 });
  return { ok: r.status === 0, out: String(r.stderr || '').trim().split('\n').slice(-1)[0] || '' };
}
const tmpCopy = (from) => {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'diag-'));
  fs.cpSync(from, d, { recursive: true });
  return d;
};
const calls = (context) => (context.providerResponse && context.providerResponse.metadata && context.providerResponse.metadata.toolCalls) || [];
const prodEdit = (s, c) => ['Edit', 'Write', 'MultiEdit', 'NotebookEdit'].includes(c.name)
  && new RegExp(`(^|/)${s.dir}/`).test(String((c.input || {}).file_path || '')) && !isTest(String(c.input.file_path).split(`${s.dir}/`).pop());

const moduleOf = (rel) => rel.replace(/\.py$/, '').split('/').join('.');

module.exports = { moduleOf, ROOT, spec, criteria, result, walk, project, pristine, isTest, read, changed, unittest, tmpCopy, calls, prodEdit, spawnSync, fs, path };
