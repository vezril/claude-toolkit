// verification: every premise is reported with the right status, verified and
// refuted ones cite the file that shows it, and every cited path:line exists.
const { spec, result, parseRelay, badRefs, findPremise, citesFile } = require('./lib');

module.exports = (output, context) => {
  const s = spec(context);
  const r = parseRelay(output);
  const p = badRefs(r.text);
  for (const pr of s.premises || []) {
    const allowed = [].concat(pr.expect);
    const got = findPremise(r, pr);
    if (!got) { p.push(`premise "${pr.id}" not reported`); continue; }
    if (!allowed.includes(got.tag)) { p.push(`premise "${pr.id}" reported ${got.tag}, expected ${allowed.join('|')}`); continue; }
    if (got.tag !== 'unverified' && pr.refFile) {
      const files = [].concat(pr.refFile);
      if (!citesFile(got, files)) p.push(`premise "${pr.id}" ${got.tag} without citing ${files.join(' or ')}`);
    }
  }
  return result(p, 'premises reported correctly, refs real');
};
