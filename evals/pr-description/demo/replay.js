// promptfoo provider that replays a recorded run instead of calling a model.
// DEMO_RECORDING=recordings/v2.json points at a results file written by `demo.sh record`.
// Each case's recorded outputs are served once each, so a --repeat 3 replay re-scores
// exactly the 3 recorded responses. The rendered prompt must match the recording, so
// replaying a v2 recording against the v3 skill fails loudly instead of scoring wrong.
const fs = require('fs');
const path = require('path');

let queues;
function load() {
  const file = path.resolve(process.env.DEMO_RECORDING || '');
  const rows = JSON.parse(fs.readFileSync(file, 'utf8')).results.results;
  queues = {};
  for (const row of rows) {
    const c = row.vars.case;
    (queues[c] ??= []).push({ prompt: row.prompt.raw, output: row.response && row.response.output });
  }
}

module.exports = class ReplayProvider {
  id() { return 'haiku (replay)'; }

  async callApi(prompt, context) {
    if (!queues) load();
    const c = context.vars.case;
    const next = (queues[c] || []).shift();
    if (!next) return { error: `no recorded output left for ${c}` };
    if (next.prompt !== prompt) return { error: `prompt for ${c} differs from the recording (wrong version?)` };
    const delay = Number(process.env.DEMO_DELAY_MS || 0);
    if (delay) await new Promise((r) => setTimeout(r, delay));
    return { output: next.output };
  }
};
