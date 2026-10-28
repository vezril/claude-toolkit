// disclosure: reference only one branch needs moves out of the main file, behind a
// pointer. The planted marker lives in another file, and the main file links to it.
const path = require('path');
const { spec, result, files, mainFile } = require('./lib');
module.exports = (output, context) => {
  const s = spec(context);
  const fs_ = files(output);
  const main = mainFile(fs_, s);
  const others = fs_.filter((f) => f !== main);
  const p = [];
  if (main.text.includes(s.disclosure.marker)) p.push(`the ${s.disclosure.marker} reference is still inline in ${main.path}`);
  const home = others.find((f) => f.text.includes(s.disclosure.marker));
  if (!home) p.push(`no separate file holds the ${s.disclosure.marker} reference`);
  // Bare blocks (lenient view) carry no file name, so any pointer to a .md file counts.
  else if (home.path.startsWith('extra-') ? !/[\w./-]+\.md\b/.test(main.text) : !main.text.includes(path.basename(home.path))) p.push(`${main.path} never points at ${path.basename(home.path)}`);
  return result(p, 'branch-only reference disclosed behind a pointer');
};
