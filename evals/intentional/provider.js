// Custom promptfoo provider for the intention-ritual skills.
//
// Each call gets its own throwaway copy of fixture/vault (plus the case's overlay, if
// any), runs the skill through the Claude Agent SDK with file tools jailed to that copy,
// then diffs the copy against the fixture. The output is JSON:
//   { reply, model, changes: [{ path, status, before, after }], tools: [...], denied: [...] }
// so asserts can grade both what the skill said and what it did to the vault.
//
// Why not the stock anthropic:claude-agent-sdk provider: its working_dir is shared
// across tests (writes would bleed between cases) and it can't diff. And the skills
// name the real vault path (/Users/cference/Mindmap), so the jail is not optional:
// any tool call outside the temp copy is denied and recorded in `denied`.
const fs = require('fs');
const os = require('os');
const path = require('path');

const FIXTURE = path.join(__dirname, 'fixture', 'vault');
const OVERLAYS = path.join(__dirname, 'overlays');
const TOOLS = ['Read', 'Glob', 'Grep', 'Write', 'Edit'];
const FIXTURE_DATE = 'Wednesday 2026-10-14 (ISO week 2026-W42)';
// The skills name the real vault. Reaching for it is correct behaviour, so the prompt has
// that path swapped for the temp copy, and the jail also redirects the prefix (backstop
// for reads) instead of denying it.
const REAL_VAULT = '/Users/cference/Mindmap';
function redirect(root, input) {
  const out = { ...input };
  for (const k of ['file_path', 'path', 'pattern']) {
    if (typeof out[k] === 'string' && (out[k] === REAL_VAULT || out[k].startsWith(REAL_VAULT + '/'))) {
      out[k] = root + out[k].slice(REAL_VAULT.length);
    }
  }
  return out;
}

async function loadSdk() {
  try {
    return await import('@anthropic-ai/claude-agent-sdk');
  } catch {
    // Not installed next to the suite: borrow the copy promptfoo ships with.
    const pf = path.dirname(require.resolve('promptfoo/package.json', { paths: [process.cwd(), process.argv[1] || ''] }));
    const entry = require.resolve('@anthropic-ai/claude-agent-sdk', { paths: [pf] });
    return await import(entry);
  }
}

function snapshot(root) {
  const out = {};
  (function walk(dir) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.name !== '.gitkeep') out[path.relative(root, p)] = fs.readFileSync(p, 'utf8');
    }
  })(root);
  return out;
}

function inside(root, p) {
  if (!p) return true;
  const abs = path.resolve(root, p);
  let real = abs;
  try { real = fs.realpathSync(abs); } catch { try { real = path.join(fs.realpathSync(path.dirname(abs)), path.basename(abs)); } catch {} }
  return real === root || real.startsWith(root + path.sep);
}

class IntentionalVaultProvider {
  constructor(options = {}) {
    this.config = options.config || {};
    this.label = options.label;
    this.providerId = options.id || 'intentional-vault';
  }
  id() { return `${this.providerId}:${this.config.model || 'default'}`; }

  async callApi(prompt, context) {
    const vars = (context && context.vars) || {};
    const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'intentional-vault-')));
    fs.cpSync(FIXTURE, root, { recursive: true });
    if (vars.overlay) fs.cpSync(path.join(OVERLAYS, vars.overlay), root, { recursive: true });
    const before = snapshot(root);

    const denied = [];
    const tools = [];
    let reply = '';
    const texts = []; // every text block the user would see, not only the final one
    let model = this.config.model;
    let cost = 0;
    const { query } = await loadSdk();
    try {
      // Point the skill's "normally /Users/cference/Mindmap" at this run's copy. Edit/Write
      // validate paths before hooks run, so a hook redirect alone can't cover writes.
      const q = query({
        prompt: prompt.split(REAL_VAULT).join(root),
        options: {
          cwd: root,
          model: this.config.model,
          tools: TOOLS,
          maxTurns: this.config.max_turns || 25,
          settingSources: ['project'], // the fixture's CLAUDE.md, nothing from ~/.claude
          // The fixture is frozen on Wednesday 2026-10-14; pin the session to it so the suite
          // means the same thing on any day (the preset's own date line comes from the clock).
          systemPrompt: { type: 'preset', preset: 'claude_code', append: `The current date for this session is ${FIXTURE_DATE}. Use it for "today" and the ISO week, not any other date.` },
          // The jail lives in a PreToolUse hook: read-only tools like Glob are auto-approved
          // and never reach canUseTool, so a permission callback alone leaks.
          hooks: {
            PreToolUse: [{
              hooks: [async (h) => {
                const name = h.tool_name;
                const input = redirect(root, h.tool_input || {});
                const p = input.file_path || input.path;
                const absPattern = path.isAbsolute(input.pattern || '') && !inside(root, input.pattern.split('*')[0] || '/');
                if (TOOLS.includes(name) && inside(root, p) && !absPattern) {
                  return { hookSpecificOutput: { hookEventName: 'PreToolUse', permissionDecision: 'allow', updatedInput: input } };
                }
                denied.push(`${name} ${p || input.pattern}`);
                return { hookSpecificOutput: { hookEventName: 'PreToolUse', permissionDecision: 'deny', permissionDecisionReason: `Outside the vault (${root}).` } };
              }],
            }],
          },
        },
      });
      for await (const msg of q) {
        if (msg.type === 'system' && msg.subtype === 'init' && msg.model) model = msg.model;
        if (msg.type === 'assistant') {
          for (const b of msg.message.content) {
            if (b.type === 'text' && b.text.trim()) texts.push(b.text.trim());
            if (b.type === 'tool_use') tools.push(`${b.name} ${path.relative(root, path.resolve(root, redirect(root, b.input).file_path || redirect(root, b.input).path || b.input.pattern || '.'))}`);
          }
        }
        if (msg.type === 'result') {
          reply = texts.length ? texts.join('\n\n') : (msg.result || '');
          cost = msg.total_cost_usd || 0;
        }
      }
    } catch (err) {
      fs.rmSync(root, { recursive: true, force: true });
      return { error: String(err && err.stack || err) };
    }

    const after = snapshot(root);
    const changes = [];
    for (const p of new Set([...Object.keys(before), ...Object.keys(after)])) {
      if (before[p] === after[p]) continue;
      const status = !(p in before) ? 'added' : !(p in after) ? 'deleted' : 'modified';
      changes.push({ path: p, status, before: before[p] ?? null, after: after[p] ?? null });
    }
    fs.rmSync(root, { recursive: true, force: true });
    return { output: JSON.stringify({ reply, model, changes, tools, denied }), cost };
  }
}

module.exports = IntentionalVaultProvider;
