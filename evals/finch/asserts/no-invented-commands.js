// Fails a response that tells the user to run a `finch` subcommand that does not exist.
//
// Added after reading the BASELINE transcripts: the no-skill arm passed several cases
// on concept while handing out fabricated commands — `finch vm ssh -- sudo fstrim -av`,
// `finch soci create` / `finch soci push`, `limactl disk create finch`. The original
// asserts only checked that the right *mechanism* was named, so a confidently wrong
// command scored exactly like a correct one. For a CLI skill that is the failure that
// actually costs the user time, so it gets its own criterion.
//
// Only fenced code blocks and inline-backtick spans are scanned. Prose says things like
// "Finch runs containers in a VM", and treating `runs` as a subcommand would flag every
// correct answer.
//
// Command list is verbatim from `finch --help` on Finch v1.19.0.

const TOP_LEVEL = new Set([
  'build', 'builder', 'commit', 'completion', 'compose', 'container', 'cp', 'create',
  'events', 'exec', 'help', 'history', 'image', 'images', 'info', 'inspect', 'kill',
  'load', 'login', 'logout', 'logs', 'network', 'pause', 'port', 'ps', 'pull', 'push',
  'restart', 'rm', 'rmi', 'run', 'save', 'start', 'stats', 'stop', 'support-bundle',
  'system', 'tag', 'top', 'unpause', 'update', 'version', 'vm', 'volume', 'wait',
]);

const VM_SUB = new Set(['disk', 'init', 'remove', 'settings', 'start', 'status', 'stop']);

// `finch vm disk` only has resize today.
const VM_DISK_SUB = new Set(['resize']);

function codeSpans(text) {
  const spans = [];
  const fenced = text.matchAll(/```[^\n]*\n([\s\S]*?)```/g);
  for (const m of fenced) spans.push(m[1]);
  const inline = text.matchAll(/`([^`\n]+)`/g);
  for (const m of inline) spans.push(m[1]);
  return spans;
}

module.exports = (output) => {
  const text = typeof output === 'string' ? output : JSON.stringify(output);
  const offenders = new Set();

  for (const span of codeSpans(text)) {
    for (const line of span.split('\n')) {
      // `finch` must be in COMMAND position on this line: at the start, after a
      // pipe/separator, or behind sudo / an env-var prefix. Without this, `finch`
      // used as an ARGUMENT gets misread as an invocation -- `limactl shell finch`
      // followed by `sudo ...` on the next line parsed as "finch sudo", which flagged
      // a correct answer. Matching per line also stops a run from crossing newlines.
      for (const m of line.matchAll(
        /(?:^|[|;&(]|\bsudo\s+(?:-E\s+)?|\b[A-Z_][A-Z0-9_]*=\S*\s+)[ \t]*finch[ \t]+((?:[a-z][a-z0-9-]*[ \t]*){1,3})/gi,
      )) {
        const words = m[1].trim().toLowerCase().split(/\s+/);
        const [a, b, c] = words;
        if (!TOP_LEVEL.has(a)) {
          offenders.add(`finch ${a}`);
          continue;
        }
        if (a === 'vm' && b && !VM_SUB.has(b)) {
          offenders.add(`finch vm ${b}`);
          continue;
        }
        if (a === 'vm' && b === 'disk' && c && !VM_DISK_SUB.has(c)) {
          offenders.add(`finch vm disk ${c}`);
        }
      }
    }
  }

  const list = [...offenders];
  return list.length
    ? { pass: false, score: 0, reason: `Invented finch subcommand(s): ${list.join(', ')}` }
    : { pass: true, score: 1, reason: 'No invented finch subcommands' };
};
