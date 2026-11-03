// Adapter: hand the model's output to grade.py and return one criterion's verdict.
//
// There is no grading logic here on purpose. The rules this suite enforces are
// the rules the real pipeline enforces (contracts.py, edges.py, verdict.py),
// and a second implementation in JavaScript would drift from the first until a
// green suite meant nothing. So the three asserts are three calls into one
// Python grader, and each output is graded once and cached.
const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const ROOT = path.join(__dirname, '..');
const cache = new Map();

function gradeOnce(caseId, output) {
  // promptfoo calls every assert for the same row, so without this the grader
  // would run three times per case per repeat.
  const key = caseId + '\u0000' + output;
  if (cache.has(key)) return cache.get(key);

  const tmp = path.join(os.tmpdir(), `appreview-${process.pid}-${cache.size}.txt`);
  fs.writeFileSync(tmp, String(output));
  try {
    const raw = execFileSync(
      'python3',
      [path.join(ROOT, 'grade.py'), '--case', caseId, '--output', tmp],
      { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 },
    );
    const parsed = JSON.parse(raw);
    cache.set(key, parsed);
    return parsed;
  } catch (err) {
    const message = (err.stderr || err.message || String(err)).slice(0, 400);
    const failure = { pass: false, score: 0, reason: `grader crashed: ${message}` };
    const parsed = { contract: failure, accuracy: failure, honesty: failure };
    cache.set(key, parsed);
    return parsed;
  } finally {
    fs.rmSync(tmp, { force: true });
  }
}

module.exports = function criterion(name) {
  return (output, context) => {
    const caseId = context && context.vars && context.vars.case;
    if (!caseId) {
      return { pass: false, score: 0, reason: 'the test is missing vars.case' };
    }
    const graded = gradeOnce(caseId, output);
    const result = graded[name];
    return { pass: result.pass, score: result.score, reason: result.reason };
  };
};
