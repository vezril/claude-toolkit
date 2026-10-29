// Hand-written revisions for calibrating the asserts before any model runs. Each bad
// reply lists exactly the criteria it should fail and must pass the rest.
const F = (p, t) => `### ${p}\n\n\`\`\`\`markdown\n${t.trim()}\n\`\`\`\`\n`;
const goodSkill = `---
name: changelog
description: Changelog entries from git history, in Keep a Changelog format. Use when releasing a version, or one package of a monorepo.
---

# Changelog

## Steps

1. Read \`git log\` since the last tag, skipping merge commits. Done when every non-merge commit since the tag is listed.
2. Sort each commit into Added, Changed, Fixed or Removed. Done when every listed commit sits in exactly one group.
3. Write the entry at the top of CHANGELOG.md. Done when the entry is above the previous release's entry.

## Rules

- Write in the active voice.
- Breaking changes go first, under a **BREAKING** label: downstream teams search for that word before upgrading.

## Monorepo packages

For a monorepo, write one entry per package; map each conventional-commit scope to its package with [scopes.md](scopes.md).
`;
const scopes = `| scope | package | changelog path |
|-------|---------|----------------|
| api | billing-api | packages/billing-api/CHANGELOG.md |
| sdk | client-sdk | packages/client-sdk/CHANGELOG.md |
| infra | (none) | skip: infra changes are not released |
`;
const goodClaude = `# CLAUDE.md

pantry-web, a Next.js app. Commands are the scripts in package.json.

## Rules

- Type values precisely; reach for \`unknown\` over \`any\`.
- Use named exports.
- Work on a branch and open a PR; never commit directly to main.
- Payments go through \`lib/legacy-gateway.ts\`, not the Stripe SDK: the gateway records every charge in the ledger service, and a direct Stripe call skips the ledger (that is how customers were double-billed in March).
- Dates are stored in UTC and rendered in the user's timezone with \`formatLocal()\`; the server never knows the user's timezone.
`;
const goodOnboard = `---
name: onboarding-interview
description: Interview a new contributor and write ONBOARDING.md. Use when someone new joins a project.
---

# Onboarding interview

1. Ask about the project and their goals. Done when you can state their goal in one sentence and they confirm it.
2. Explore the codebase: entry points, build, tests. Done when every top-level directory has a one-line note.
3. Write the summary to ONBOARDING.md. Done when the file exists and covers the goal and every directory note.
`;
module.exports = [
  { case: 'w-01-changelog', label: 'good', fails: [], output: F('skills/changelog/SKILL.md', goodSkill) + '\n' + F('skills/changelog/scopes.md', scopes) },
  { case: 'w-01-changelog', label: 'light edit: keeps no-ops, table and padding', fails: ['prune', 'pointer', 'disclosure', 'steps', 'positive'],
    output: F('skills/changelog/SKILL.md', require('fs').readFileSync(require('path').join(__dirname, '..', 'inputs', 'w-01-changelog.md'), 'utf8')) },
  { case: 'w-01-changelog', label: 'over-prunes: drops BREAKING and the monorepo table', fails: ['preserve', 'disclosure'],
    output: F('skills/changelog/SKILL.md', goodSkill.replace(/- Breaking[^\n]*\n/, '').replace(/one package of a monorepo/, 'one package of a monorepo').replace(/## Monorepo packages[\s\S]*/, 'See [scopes.md](scopes.md) for monorepos.')) + F('skills/changelog/scopes.md', '| scope | package |\n| x | y |\n') },
  { case: 'w-01-changelog', label: 'no headed files, bare block', fails: ['format'], output: '```markdown\n' + goodSkill + '\n```\n\n```\n' + scopes + '\n```' },
  { case: 'w-02-claude-md', label: 'good', fails: [], output: F('CLAUDE.md', goodClaude) },
  { case: 'w-02-claude-md', label: 'keeps the command and layout cache', fails: ['prune'],
    output: F('CLAUDE.md', goodClaude + '\n## Commands\n\n- `npm install`\n- `npm run dev`\n\n## Layout\n\n- `components/` contains React components\n') },
  { case: 'w-02-claude-md', label: 'keeps the negations, loses the ledger reason', fails: ['preserve', 'positive'],
    output: F('CLAUDE.md', "# CLAUDE.md\n\n- Don't use `any`.\n- Don't use default exports.\n- Never commit directly to main.\n- Payments go through `lib/legacy-gateway.ts`.\n- Dates are UTC, rendered with `formatLocal()`.\n") },
  { case: 'w-03-description', label: 'good', fails: [], output: "description: App Store release notes (\"What's New\") from merged changes: draft them from git, translate them into other locales, or cut them to fit the character limits." },
  { case: 'w-03-description', label: 'padded and identity-first', fails: ['pointer'], output: "description: This skill helps you write release notes, What's New text, changelogs, patch notes and update notes for the App Store. Use it whenever the user wants release notes." },
  { case: 'w-03-description', label: 'wrapped in prose', fails: ['format'], output: "Here's a description:\n\ndescription: App Store release notes from merged changes: draft from git, translate into locales, or cut to fit the character limit." },
  { case: 'w-04-onboarding', label: 'good', fails: [], output: F('skills/onboarding-interview/SKILL.md', goodOnboard) },
  { case: 'w-04-onboarding', label: 'rewords but leaves the bounds vague', fails: ['steps'],
    output: F('skills/onboarding-interview/SKILL.md', goodOnboard.replace(/ Done when[^\n]*/g, '').replace('Ask about the project and their goals.', 'Ask about the project and their goals until understanding is reached.')) },
  // Real v2 revisions the first scorer misread, trimmed.
  { case: 'w-02-claude-md', label: 'real v2: positive main rule, no "commit" word', fails: [],
    output: F('CLAUDE.md', goodClaude.replace('- Work on a branch and open a PR; never commit directly to main.', '- Work on a branch; main stays untouched.').replace("- Type values precisely; reach for `unknown` over `any`.", '- Type everything precisely; use named exports.')) },
  { case: 'w-04-onboarding', label: 'real v2: "finish only when" / "step is complete when"', fails: [],
    output: F('skills/onboarding-interview/SKILL.md', goodOnboard.replace('Done when you can state', 'Finish only when you can state').replace('Done when every top-level', 'Step is complete when every top-level').replace('Done when the file exists', 'Before reporting done, check the file exists')) },
  { case: 'w-03-description', label: 'synonym-padded description', fails: ['pointer'], output: "description: Release notes, What's New text, changelog and patch notes for the App Store: draft them from git, translate, or fit the limit." },
  { case: 'w-01-changelog', label: 'real v3: "starts with an active verb" is the positive', fails: [],
    output: F('skills/changelog/SKILL.md', goodSkill.replace('- Write in the active voice.', '- Each entry is one line that starts with an active verb: "Add retry", not "Retry was added".')) + '\n' + F('skills/changelog/scopes.md', scopes) },
  { case: 'w-01-changelog', label: 'real v5: names the format once, then uses its section names', fails: [],
    output: F('skills/changelog/SKILL.md', goodSkill.replace('2. Sort each commit into Added, Changed, Fixed or Removed.', '2. Sort each commit under one Keep a Changelog section: Added, Changed, Fixed or Removed.')) + '\n' + F('skills/changelog/scopes.md', scopes) },
  { case: 'w-01-changelog', label: 'states the format rule twice', fails: ['prune'],
    output: F('skills/changelog/SKILL.md', goodSkill.replace('## Rules\n', '## Rules\n\n- Always follow the Keep a Changelog format.\n- Make sure the entry conforms to Keep a Changelog.\n')) + '\n' + F('skills/changelog/scopes.md', scopes) },
];
