// Thin adapters over grade.py. All grading is in that one Python script, which reads the
// story the same way `check-test-scope.py` does in production — so the suite cannot drift
// from what the flow actually enforces. These files exist only because promptfoo needs JS.
const { execFileSync } = require('child_process');
const path = require('path');

const ROOT = path.join(__dirname, '..');

function grade(output, context) {
  const id = context && context.vars && context.vars.case;
  if (!id) throw new Error('test is missing vars.case');
  // The agent worked in fixture/<case> via working_dir; promptfoo copies nothing, so the
  // tree it left IS that directory.
  // .work/<case> is the copy the provider made and the agent edited; fixture/<case> is the
  // pristine baseline grade.py diffs against.
  // Must match the provider's layout: keyed by case and model, because they run in parallel.
  const label = (context && context.provider && (context.provider.label || context.provider.id))
    || 'sonnet';
  const work = path.join(ROOT, '.work', `${id}-${label}`);
  // The agent's reply goes to grade.py via a temp file, so ALL grading stays in that one
  // script. One criterion reads what the agent said (a disputed priority has to be reported,
  // not merely acted on), and splitting that into JS would put grading in two places.
  const os = require('os');
  const fs = require('fs');
  const replyPath = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'reply-')), 'reply.txt');
  fs.writeFileSync(replyPath, String(output === undefined || output === null ? '' : output));
  const out = execFileSync('python3', ['-I', path.join(ROOT, 'grade.py'), id,
                                       '--work', work, '--output-file', replyPath, '--json'],
                           { encoding: 'utf8', timeout: 600000 });
  return JSON.parse(out);
}

function criterion(name) {
  return (output, context) => {
    const g = grade(output, context);
    const pass = Boolean(g.scores[name]);
    return { pass, score: pass ? 1 : 0, reason: g.reasons[name] || `${name}: no reason given` };
  };
}

module.exports = { grade, criterion };
