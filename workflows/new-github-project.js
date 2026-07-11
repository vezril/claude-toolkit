export const meta = {
  name: 'new-github-project',
  description: 'Create a local dir + empty GitHub repo, protect main, add starter docs, and ship them via PR (merge waits for human approval unless auto)',
  whenToUse: 'When starting a brand-new GitHub project from nothing: repo + branch protection + README/LICENSE, landed through a PR.',
  phases: [
    { title: 'Create repo', detail: 'local directory + empty GitHub repo, main seeded with an empty commit' },
    { title: 'Protect main', detail: 'protect-main ruleset: require PR, block force-push and deletion' },
    { title: 'Starter docs', detail: 'README.md + LICENSE.md (MIT) in the working tree' },
    { title: 'Ship', detail: 'commit, push, PR; merge only in auto mode' },
  ],
}

// args: { name: string (required), visibility: 'public' | 'private' (required), auto?: boolean,
//         docs?: boolean (default true), ship?: boolean (default true) }
// docs:false + ship:false = "bare mode": repo + protection only, returns synchronously —
// for flavor workflows (new-scala-pekko-service, …) that bring their own docs and PR.
// The human choosing to launch this workflow with an explicit name + visibility IS the
// authorization for the outward-facing repo creation; the merge stays gated unless auto.

if (!args || typeof args !== 'object') {
  throw new Error("args required: { name: 'my-repo', visibility: 'public'|'private', auto?: true, docs?: false, ship?: false }")
}
const name = args.name
const visibility = args.visibility
const auto = args.auto === true
const docs = args.docs !== false
const ship = args.ship !== false
if (!name || !/^[a-z0-9][a-z0-9._-]*$/.test(name)) {
  throw new Error(`args.name must match [a-z0-9][a-z0-9._-]* — got: ${JSON.stringify(name)}`)
}
if (visibility !== 'public' && visibility !== 'private') {
  throw new Error("args.visibility must be exactly 'public' or 'private' — the human chooses, no default")
}
if (!docs && ship) {
  throw new Error('docs:false with ship:true is pointless — there would be nothing to ship. Use bare mode (both false) or keep docs on.')
}

// Every step agent locates the skill it executes; the toolkit may be installed as a plugin,
// copied to ~/.claude/skills, or checked out at ~/Code/claude-toolkit.
const findSkill = (skill) => `
First locate the skill file ${skill}/SKILL.md. Check in order (glob, take the first hit):
  1. $HOME/.claude/skills/${skill}/SKILL.md
  2. $HOME/.claude/plugins/**/skills/${skill}/SKILL.md
  3. $HOME/Code/claude-toolkit/skills/${skill}/SKILL.md
Read it and follow it EXACTLY, including its guardrails. If you cannot find it, stop and
return an error field explaining what you searched.`

const dir = `$HOME/Code/${name}`

phase('Create repo')
log(`Creating ${dir} and github.com/vezril/${name} (${visibility})`)
const created = await agent(`
You are one step of the new-github-project workflow. The human launched it explicitly with
these parameters, which is the confirmation the skill's Step 2 asks for — do not stop to ask.

1. Create an empty local directory ${dir} (mkdir -p; it must not already exist and must be
   empty — if it exists non-empty, stop and return an error field).
2. ${findSkill('github-new-repo')}
   Parameters: repo name "${name}", visibility "${visibility}". Work inside ${dir}.

Return JSON only.`, {
  label: 'create-repo',
  schema: {
    type: 'object',
    properties: {
      localPath: { type: 'string' },
      repoUrl: { type: 'string' },
      defaultBranch: { type: 'string' },
      error: { type: 'string' },
    },
    required: ['localPath', 'repoUrl'],
  },
})
if (!created || created.error) {
  return { status: 'failed', step: 'create-repo', error: created ? created.error : 'agent died' }
}

phase('Protect main')
// (protection always runs; bare mode only skips docs + ship below)
const protection = await agent(`
You are one step of the new-github-project workflow; the human authorized it by launching
the workflow — do not stop to ask.
${findSkill('github-branch-protection')}
Parameter: repo "vezril/${name}". The repo was just created and main already has its seed
commit. Return JSON only.`, {
  label: 'protect-main',
  schema: {
    type: 'object',
    properties: {
      rulesetId: { type: 'number' },
      rulesetUrl: { type: 'string' },
      activeRules: { type: 'array', items: { type: 'string' } },
      error: { type: 'string' },
    },
    required: ['activeRules'],
  },
})
if (!protection || protection.error) {
  return { status: 'failed', step: 'protect-main', error: protection ? protection.error : 'agent died', created }
}

if (!docs) {
  log('Bare mode: skipping starter docs and ship — repo is ready for a flavor workflow.')
  return {
    status: 'complete',
    bare: true,
    repo: created.repoUrl,
    localPath: created.localPath,
    protection: { rulesetUrl: protection.rulesetUrl, activeRules: protection.activeRules },
  }
}

phase('Starter docs')
const docsResult = await agent(`
You are one step of the new-github-project workflow.
${findSkill('repo-starter-docs')}
Work inside ${created.localPath}. Project description: none was provided — use the skill's
TODO placeholder, do not invent one, and do not stop to ask (there is no human mid-workflow).
Write the files only; no commit. Return JSON only.`, {
  label: 'starter-docs',
  schema: {
    type: 'object',
    properties: {
      files: { type: 'array', items: { type: 'string' } },
      error: { type: 'string' },
    },
    required: ['files'],
  },
})
if (!docsResult || docsResult.error) {
  return { status: 'failed', step: 'starter-docs', error: docsResult ? docsResult.error : 'agent died', created, protection }
}

if (!ship) {
  log('ship:false — starter docs written but left uncommitted for the caller to ship.')
  return {
    status: 'complete',
    shipped: false,
    repo: created.repoUrl,
    localPath: created.localPath,
    protection: { rulesetUrl: protection.rulesetUrl, activeRules: protection.activeRules },
    docs: docsResult.files,
  }
}

phase('Ship')
const shipResult = await agent(`
You are the final step of the new-github-project workflow.
${findSkill('git-ship')}
Work inside ${created.localPath}. Ship the starter docs (README.md, LICENSE.md) on a branch
named docs/starter-docs.
Mode: ${auto
    ? 'AUTO — the human launched the workflow with auto: true, so merge the PR without asking.'
    : 'GATED — you are inside a workflow with no human available: stop after creating the PR and return pendingApproval: true with the PR URL. Do NOT merge.'}
Return JSON only.`, {
  label: 'ship-docs',
  schema: {
    type: 'object',
    properties: {
      prUrl: { type: 'string' },
      merged: { type: 'boolean' },
      pendingApproval: { type: 'boolean' },
      mergeCommit: { type: 'string' },
      error: { type: 'string' },
    },
    required: ['prUrl', 'merged'],
  },
})
if (!shipResult || shipResult.error) {
  return { status: 'failed', step: 'ship', error: shipResult ? shipResult.error : 'agent died', created, protection, docs: docsResult }
}

log(shipResult.merged ? 'Docs PR merged.' : `Docs PR awaiting human approval: ${shipResult.prUrl}`)
return {
  status: shipResult.merged ? 'complete' : 'awaiting-merge-approval',
  repo: created.repoUrl,
  localPath: created.localPath,
  protection: { rulesetUrl: protection.rulesetUrl, activeRules: protection.activeRules },
  docs: docsResult.files,
  pr: { url: shipResult.prUrl, merged: shipResult.merged, mergeCommit: shipResult.mergeCommit || null },
  nextStep: shipResult.merged
    ? null
    : `Ask the human to authorize the merge of ${shipResult.prUrl}, then merge it (gh pr merge --merge) and sync main.`,
}
