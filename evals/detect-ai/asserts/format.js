// Output-format contract for a normal analysis (not the misconduct rail case):
// the skill's required sections, the Estimate line, all six signals in the
// breakdown, and a caveats section.
module.exports = (output) => {
  const problems = [];
  for (const s of ['## AI-Style Analysis', '### Signal Breakdown', '### Caveats']) {
    if (!output.includes(s)) problems.push('missing section: ' + s);
  }
  const est = output.match(/\*\*Estimate:\*\*\s*(\d{1,3})\s*\/\s*100/);
  if (!est) problems.push('missing "**Estimate:** N/100" line');
  else {
    const n = parseInt(est[1], 10);
    if (n < 0 || n > 100) problems.push('estimate out of range: ' + n);
  }
  if (!/\*\*Sample size:\*\*/.test(output)) problems.push('missing Sample size line');
  for (const sig of ['Burstiness', 'Clich', 'Hedging', 'Structural', 'Specificity', 'Surface']) {
    if (!new RegExp(sig, 'i').test(output)) problems.push('signal missing from breakdown: ' + sig);
  }
  if (problems.length) return { pass: false, score: 0, reason: problems.join('; ') };
  return { pass: true, score: 1, reason: 'format contract satisfied' };
};
