// steps: every numbered step ends on a completion criterion the agent can check, and
// the planted vague bounds are gone.
const { spec, result, files, mainFile, steps, has, DONE } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const main = mainFile(files(output), s);
  const st = steps(main.text);
  const p = [];
  if (st.length < s.steps.min) p.push(`${st.length} numbered steps (expected at least ${s.steps.min})`);
  st.forEach((t, i) => { if (!has(DONE, t)) p.push(`step ${i + 1} has no completion criterion ("${t.slice(0, 50)}")`); });
  for (const v of s.steps.vague || []) if (main.text.toLowerCase().includes(v)) p.push(`vague bound "${v}" still there`);
  return result(p, `${st.length} steps, each with a completion criterion`);
};
