// Criterion 2 — coverage (recall, lenient). Everything that changed is there:
// - every file the skill requires by name (deleted/renamed ones, plus the key
//   source files listed in expected/<case>.json -> files_required);
// - deleted/renamed files are called out as such (word check);
// - every key change, as keyword groups (any alternative counts) -> facts.

const { expected, lenient, groupMatches, result } = require('./lib');

module.exports = (output, context) => {
  const exp = expected(context);
  const text = lenient(output);
  const problems = [];

  for (const f of exp.files_required || []) {
    if (!text.toLowerCase().includes(f.toLowerCase())) problems.push('file not mentioned: ' + f);
  }
  for (const r of exp.deleted_or_renamed || []) {
    if (!text.toLowerCase().includes(r.name.toLowerCase())) problems.push(r.kind + ' path not named: ' + r.name);
    const verb = r.kind === 'deleted' ? /delet|remov/i : /renam|mov|archiv/i;
    if (!verb.test(text)) problems.push(r.kind + ' not called out as ' + r.kind);
  }
  (exp.facts || []).forEach((group, i) => {
    if (!groupMatches(text, group)) problems.push('missing fact ' + (i + 1) + ': one of [' + group.join(' | ') + ']');
  });

  const n = (exp.files_required || []).length + (exp.deleted_or_renamed || []).length + (exp.facts || []).length;
  return result(problems, 'coverage ok: ' + n + ' required items present');
};
