// Shared helpers for the readiness-review suite.
//
// The node emits `readiness-verdict.json`, so the contract criterion validates against
// `schemas/readiness-verdict.schema.json` using the project's own `validate-artifact.py` —
// the same validator the edge runs. A suite with its own copy of the schema can pass a
// verdict the edge rejects, which is how a certification number ends up describing a bar
// nobody enforces.
//
// This suite exists because `evals/cross-examine/` does not test this node. That suite feeds
// an incident ticket and a timeline and expects a markdown verdict; this node is given a story
// set and must emit JSON. Same capability, different domain and different output contract —
// and certifying against inputs the node never sees in production is the same error as
// certifying a prompt the suite never saw.

const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const PLUGIN_ROOT = path.join(ROOT, '..', '..');
const VALIDATOR = path.join(PLUGIN_ROOT, 'scripts', 'delivery-flow', 'validate-artifact.py');

// Lenient parse, so a stray fence is penalised once — by the contract criterion — rather than
// again by every criterion that needs to read the verdict.
function verdict(output) {
  let s = String(output).trim();
  const fenced = s.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fenced) s = fenced[1].trim();
  const open = s.indexOf('{');
  if (open > 0) s = s.slice(open);
  const close = s.lastIndexOf('}');
  if (close !== -1) s = s.slice(0, close + 1);
  try { return JSON.parse(s); } catch { return null; }
}

// The real validator, as the edge runs it.
function validate(doc) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'rvw-'));
  const p = path.join(dir, 'readiness-verdict.json');
  fs.writeFileSync(p, JSON.stringify(doc));
  try {
    execFileSync('python3', [VALIDATOR, p, '--consumer', 'harness'],
      { encoding: 'utf8', timeout: 60000 });
    return { ok: true, out: '' };
  } catch (e) {
    return { ok: false, out: ((e.stdout || '') + (e.stderr || '')).trim() };
  }
}

const text = (doc) => JSON.stringify(doc || {}).toLowerCase();

const result = (problems, ok) => (problems.length
  ? { pass: false, score: 0, reason: problems.join('; ') }
  : { pass: true, score: 1, reason: ok });

module.exports = { ROOT, PLUGIN_ROOT, verdict, validate, text, result };
