// format (strict): the reply is exactly what the request asked for.
const { spec, result, headedFiles } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const out = String(output).trim();
  if (s.descriptionOnly) {
    const lines = out.split('\n').filter((l) => l.trim());
    return result(lines.length === 1 && /^description:\s*\S/.test(lines[0]) ? [] : [`expected one "description:" line, got ${lines.length} line(s) starting "${(lines[0] || '').slice(0, 40)}"`], 'one description line');
  }
  const h = headedFiles(out);
  const p = [];
  if (!h.length) p.push('no "### <path>" + fenced block files');
  else if (!h.some((f) => f.path.toLowerCase().endsWith(s.main.toLowerCase()))) p.push(`no file named ${s.main}`);
  return result(p, `${h.length} headed file(s)`);
};
