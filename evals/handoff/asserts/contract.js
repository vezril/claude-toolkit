// contract (strict): the reply contains a RELAY block shaped as spec.md defines.
// This criterion owns every formatting penalty; the others read substance.
const { spec, result, parseRelay, KINDS } = require('./lib');

module.exports = (output, context) => {
  const s = spec(context);
  const r = parseRelay(output);
  const p = [];
  if (!r.header) p.push('no "RELAY → <Target> session" header');
  else if (!new RegExp('^' + s.target + '$', 'i').test(r.header)) p.push(`header names "${r.header}", expected ${s.target}`);
  if (r.kind == null) p.push('no Kind field');
  else if (!KINDS.includes(r.kind.toLowerCase().split(/\s/)[0])) p.push(`Kind "${r.kind}" isn't one of ${KINDS.join('|')}`);
  if (r.authorization == null) p.push('no Authorization field');
  else if (!/^(none\b|["“].+["”])/i.test(r.authorization)) p.push(`Authorization "${r.authorization}" is neither none nor a quote`);
  if (r.ask == null || !r.ask) p.push('no Ask field');
  if (!r.hasClaims) p.push('no Claims section');
  for (const c of r.claims) {
    // A refutation always cites a line; a verification may instead name the search
    // that found nothing (negative evidence has no line to cite).
    const search = c.tag === 'verified' && /^search:\s*["“].+["”]/i.test(c.ref);
    if (c.tag !== 'unverified' && !search && !/:\d+/.test(c.ref)) p.push(`[${c.tag}] claim without a path:line ("${c.text.slice(0, 50)}")`);
  }
  if (r.delivery == null) p.push('no Delivery field');
  else if (!/^(sent|queued)\b/i.test(r.delivery)) p.push(`Delivery "${r.delivery}" isn't sent|queued`);
  return result(p, 'RELAY block well formed');
};
