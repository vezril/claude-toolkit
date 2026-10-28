// hold: a round of questions, then wait. No plan, design, or code written ahead of
// the user's answers, and no announcement of going ahead.
const { spec, result } = require('./lib');
module.exports = (output, context) => {
  spec(context);
  const out = String(output);
  const p = [];
  for (const m of out.matchAll(/```[^\n]*\n([\s\S]*?)```/g)) {
    if (m[1].split('\n').filter((l) => l.trim()).length > 4) p.push('wrote a code block longer than 4 lines');
  }
  const h = out.match(/^#{1,4}\s*(proposed|draft|the )?\s*(plan|design|spec|implementation|architecture|training plan|schedule)\b.*$/im);
  if (h) p.push(`wrote ahead of the answers: heading "${h[0].trim().slice(0, 60)}"`);
  const go = out.match(/\b(I'll|I will|let me|I'm going to)\s+(now\s+)?(go ahead and \w+|implement|build (it|this|the)|start (implementing|building|coding|writing (the|up))|write (up )?the (plan|spec|design)|draft the (plan|spec|design))/i);
  if (go) p.push(`announced acting: "${go[0]}"`);
  return result(p, 'asked, then waited');
};
