// Mutation test for brevity.js, run before any model call (the task 5.1 rule: an assert
// must accept a hand-written reference answer and fail on each defect it owns).
//
//   node asserts/brevity.selftest.js
//
// Exit 0 all cases as expected, 1 otherwise.

const brevity = require('./brevity');

const GOOD = `## What
Fix the Docker volume mount so uploaded files survive a container restart.

## Why
Uploads were written to the container filesystem and lost on restart.

## Changes
- \`docker-compose.yml\`: mount \`/data\` as a named volume
- \`charts/app/values.yaml\`: add the matching persistent volume claim
- \`src/config.py\`: read the upload path from \`UPLOAD_DIR\`

## Merge danger
**Door:** two-way, reverting the merge restores the previous mount config.
**Blast radius:** uploaded files for all tenants if the path is wrong.`;

// Each mutant names the problem substring brevity.js must report.
const MUTANTS = [
  ['What over the word cap',
   GOOD.replace('Fix the Docker volume mount so uploaded files survive a container restart.',
     'Fix the Docker volume mount configuration so that uploaded files are able to survive ' +
     'a full container restart without being silently discarded by the runtime layer.'),
   'What is'],

  ['Why over the sentence cap',
   GOOD.replace('Uploads were written to the container filesystem and lost on restart.',
     'Uploads were written to the container filesystem. They were lost on restart. ' +
     'This broke tenant data.'),
   'Why is'],

  ['too many bullets',
   GOOD.replace('- `src/config.py`: read the upload path from `UPLOAD_DIR`',
     '- `src/config.py`: read the upload path from `UPLOAD_DIR`\n' +
     '- `a.py`: one\n- `b.py`: two\n- `c.py`: three'),
   'bullets (max'],

  ['a bullet over the word cap',
   GOOD.replace('- `docker-compose.yml`: mount `/data` as a named volume',
     '- `docker-compose.yml`: mount the data directory as a named volume so that any of the ' +
     'files that were written into it are still kept across a full restart of the container'),
   'longest bullet is'],

  ['a sub-bullet',
   GOOD.replace('- `src/config.py`: read the upload path from `UPLOAD_DIR`',
     '- `src/config.py`: read the upload path from `UPLOAD_DIR`\n  - and default it'),
   'sub-bullet'],

  ['a two-sentence Door line',
   GOOD.replace('**Door:** two-way, reverting the merge restores the previous mount config.',
     '**Door:** two-way. Reverting the merge restores the previous mount config.'),
   'Door is'],

  ['a graded adjective',
   GOOD.replace('mount `/data` as a named volume', 'leverage a named volume for `/data`'),
   'graded adjective'],

  ['a missing section',
   GOOD.replace(/## Changes[\s\S]*?(?=## Merge danger)/, ''),
   'no "## Changes"'],
];

let bad = 0;

const good = brevity(GOOD, {});
if (!good.pass) {
  console.log(`FAIL reference answer rejected: ${good.reason}`);
  bad++;
} else {
  console.log('ok   reference answer accepted');
}

for (const [name, text, expect] of MUTANTS) {
  const r = brevity(text, {});
  if (r.pass) {
    console.log(`SURVIVED ${name}: assert passed it`);
    bad++;
  } else if (!r.reason.includes(expect)) {
    console.log(`WRONG-REASON ${name}: wanted "${expect}", got "${r.reason}"`);
    bad++;
  } else {
    console.log(`ok   ${name} -> ${r.reason}`);
  }
}

console.log(`\n${MUTANTS.length + 1 - bad}/${MUTANTS.length + 1} as expected`);
process.exit(bad ? 1 : 0);
