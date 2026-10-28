// scope: when every step is one the agent could do itself, no wizard is written.
const { spec, result, blocks } = require('./lib');
module.exports = (output, context) => {
  spec(context);
  const w = blocks(output).find((b) => /\bread\s+-|\bask(_secret)?\s+[A-Z_]|\bstage\s+["']|\bconfirm\s+["']/.test(b.text));
  return result(w ? ['wrote a wizard for steps the agent could do itself'] : [], 'no wizard for agent-doable steps');
};
