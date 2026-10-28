// Unit checks for no-invented-commands.js.
//
// An assert with a bug corrupts every score it ever produces, silently and in the
// direction that looks like a result. The first version of this assert crossed
// newlines and treated `finch` used as an ARGUMENT as an invocation, so it flagged
// a correct answer lifted straight out of SKILL.md. Hence these.
//
// Run: node evals/finch/asserts/no-invented-commands.test.js

const assertFn = require('./no-invented-commands.js');

const fence = (s) => '```\n' + s + '\n```';

const CASES = [
  // Must NOT flag — `finch` as a trailing argument, not a command.
  [fence('finch vm stop\nlimactl disk delete finch\nlimactl disk create finch'), true,
    'finch as a trailing argument'],
  [fence('/Applications/Finch/lima/bin/limactl shell finch\nsudo fstrim -v /mnt/lima-finch'), true,
    'the fstrim snippet from SKILL.md'],
  // Must NOT flag — real invocations in every shape they appear in.
  [fence('sudo finch build -t app:1.0 .'), true, 'sudo prefix'],
  [fence('aws ecr get-login-password | finch login --username AWS'), true, 'piped into finch'],
  [fence('AWS_PROFILE=prod finch login --username AWS'), true, 'env-var prefix'],
  [fence('finch vm disk resize --size 100GiB'), true, 'finch vm disk resize'],
  [fence('finch push --snapshotter soci registry/app:1.0'), true, 'soci as a flag value'],
  ['Finch runs containers inside a Lima VM, and finch uses nerdctl.', true, 'prose, not code'],
  // MUST flag — subcommands that do not exist on Finch v1.19.0.
  [fence('finch vm ssh -- sudo fstrim -av'), false, 'finch vm ssh'],
  [fence('finch soci create img'), false, 'finch soci'],
  [fence('finch vm disk shrink --size 50GiB'), false, 'finch vm disk shrink'],
];

let failures = 0;
for (const [input, wantPass, label] of CASES) {
  const got = assertFn(input);
  if (got.pass !== wantPass) {
    failures++;
    console.error(`FAIL ${label}: wanted pass=${wantPass}, got pass=${got.pass} (${got.reason})`);
  } else {
    console.log(`ok   ${label}`);
  }
}

if (failures) {
  console.error(`\n${failures} of ${CASES.length} checks failed`);
  process.exit(1);
}
console.log(`\nall ${CASES.length} checks passed`);
