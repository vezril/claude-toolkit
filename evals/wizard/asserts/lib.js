// Shared helpers for the wizard asserts.
// strict:  the reply carries exactly one ```bash block, the script
// lenient: the largest fenced block that looks like a script (for the run-based asserts)
// The run-based asserts execute the script for real in a fresh copy of the fixture repo,
// with stub gh/open/fly/... on PATH that only log, driven in a pseudo-terminal by
// drive.py. What lands in .env, the log and the transcript is the evidence.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const spec = (context) => JSON.parse(fs.readFileSync(path.join(ROOT, 'expected', context.vars.case + '.json'), 'utf8'));
const criteria = (s) => s.criteria;
const result = (problems, ok) =>
  problems.length ? { pass: false, score: 0, reason: problems.join('; ') } : { pass: true, score: 1, reason: ok };

const blocks = (out) => [...String(out).matchAll(/^(`{3,})([\w-]*)[^\n]*\n([\s\S]*?)\n\1\s*$/gm)].map((m) => ({ lang: m[2].toLowerCase(), text: m[3] }));
const bashBlocks = (out) => blocks(out).filter((b) => ['bash', 'sh', 'shell', 'zsh'].includes(b.lang));
function script(out) {
  const cands = blocks(out).filter((b) => /^#!.*\b(ba)?sh\b/m.test(b.text) || /\bread\b|\bask(_secret)?\b/.test(b.text));
  return cands.sort((a, b) => b.text.length - a.text.length)[0]?.text || null;
}

const cache = new Map();
// Runs the script in a pseudo-terminal through drive.py, which answers each prompt as it
// appears (yes/no prompts get `answer`). The repo copy is a git checkout with a GitHub
// remote, and gets the case's setup files (expected/<case>.json "setup"), so a script
// that checks its surroundings finds what a real checkout would have.
function run(text, answer = 'y', setup = {}) {
  const key = answer + '\0' + JSON.stringify(setup) + '\0' + text;
  if (cache.has(key)) return cache.get(key);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'wizard-run-'));
  const repo = path.join(dir, 'pantry');
  fs.cpSync(path.join(ROOT, 'fixture', 'pantry'), repo, { recursive: true });
  for (const [f, body] of Object.entries(setup)) fs.writeFileSync(path.join(repo, f), body);
  spawnSync('sh', ['-c', 'git init -q && git remote add origin https://github.com/example/pantry.git'], { cwd: repo });
  const log = path.join(dir, 'wizard.log');
  fs.writeFileSync(log, '');
  // Saved where a wizard usually lives, so "$(dirname "$0")/.." finds the repo root.
  const file = path.join(repo, 'scripts', 'wizard.sh');
  fs.writeFileSync(file, text, { mode: 0o755 });
  const r = spawnSync('python3', [path.join(ROOT, 'drive.py'), file, repo, answer, path.join(ROOT, 'stubs'), log], { encoding: 'utf8', timeout: 60000 });
  let d = {};
  try { d = JSON.parse(r.stdout); } catch { d = { code: null, timedOut: true, transcript: String(r.stderr || '').slice(-300), answers: [] }; }
  const envFile = path.join(repo, '.env');
  const env = fs.existsSync(envFile) ? fs.readFileSync(envFile, 'utf8') : '';
  const values = fs.existsSync(log + '.values') ? fs.readFileSync(log + '.values', 'utf8') : '';
  const res = {
    code: d.code, timedOut: d.timedOut, transcript: d.transcript || '', answers: d.answers || [],
    tail: (d.transcript || '').replace(/\s+/g, ' ').trim().slice(-160),
    log: fs.readFileSync(log, 'utf8').split('\n').filter(Boolean), env, values,
  };
  fs.rmSync(dir, { recursive: true, force: true });
  cache.set(key, res);
  return res;
}
const envKeys = (env) => new Set([...env.matchAll(/^\s*(?:export\s+)?([A-Z_][A-Z0-9_]*)=/gm)].map((m) => m[1]));
const ghSet = (log, kind) => new Set(log.filter((l) => l.startsWith(`GH ${kind} set `)).map((l) => l.split(' ')[3]));

// Where a secret's value ended up: its .env line, else what gh was handed for it.
function valueOf(r, k) {
  const m = r.env.match(new RegExp(`^\\s*(?:export\\s+)?${k}=['"]?([^'"\\n]*)`, 'm'));
  if (m && m[1]) return m[1];
  const g = r.values.split('\n').find((l) => l.startsWith(k + ' '));
  return g ? g.slice(k.length + 1) : null;
}

module.exports = { spec, criteria, result, blocks, bashBlocks, script, run, envKeys, ghSet, valueOf };
