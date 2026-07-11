export const meta = {
  name: 'new-scala-pekko-service',
  description: 'Bootstrap a Scala 3 + Pekko service: bare repo bootstrap, decomposed scaffold, optional Docker Hub wiring, sbt green gate, one gated PR',
  whenToUse: 'When starting a brand-new Scala 3 + Apache Pekko service from nothing. Successor to the retired new-scala-service monolith skill.',
  phases: [
    { title: 'Bootstrap', detail: 'new-github-project in bare mode: repo + protected main only' },
    { title: 'Scaffold', detail: 'sequential on feat/scaffold: build → server → tests → docs → CI' },
    { title: 'Docker Hub', detail: 'repo + CI token + GitHub secrets (only if dockerhub: true)' },
    { title: 'Verify', detail: 'sbt scalafmtAll compile test — red ships nothing' },
    { title: 'Ship', detail: 'one PR; merge gated on the human unless auto' },
  ],
}

// args: { name, visibility: 'public'|'private', dockerhub: boolean, auto?: false, pkgRoot?: 'me.cference' }
// name, visibility AND dockerhub are required with no defaults — the outer conversation
// must ask the human ("public or private?", "Docker Hub repo needed?") before launching.
// Drop-list vs the retired monolith: README/LICENSE now come from repo-starter-docs
// (LICENSE.md standard). The OpenSpec surface now comes from the bootstrap workflow
// (openspec init --tools claude), not from the scala scaffold scripts.

// Tolerate stringified args (some invokers pass JSON text rather than an object).
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch { /* falls through to the guard */ } }
if (!A || typeof A !== 'object') {
  throw new Error("args required: { name, visibility: 'public'|'private', dockerhub: true|false, auto?: true, pkgRoot?: 'me.cference' }")
}
const { name, visibility } = A
const auto = A.auto === true
const pkgRoot = A.pkgRoot || 'me.cference'
if (!name || !/^[a-z][a-z0-9-]*[a-z0-9]$/.test(name)) {
  throw new Error(`args.name must be lowercase [a-z0-9-], start with a letter — got: ${JSON.stringify(name)}`)
}
if (visibility !== 'public' && visibility !== 'private') {
  throw new Error("args.visibility must be 'public' or 'private' — ask the human, no default")
}
if (typeof A.dockerhub !== 'boolean') {
  throw new Error('args.dockerhub must be explicitly true or false — ask the human: "Does this project need a Docker Hub repo (image publishing from CI)?"')
}
const dockerhub = A.dockerhub

const findSkill = (skill) => `
First locate the skill file ${skill}/SKILL.md. Check in order (glob, take the first hit):
  1. $HOME/.claude/skills/${skill}/SKILL.md
  2. $HOME/.claude/plugins/**/skills/${skill}/SKILL.md
  3. $HOME/Code/claude-toolkit/skills/${skill}/SKILL.md
Read it and follow it EXACTLY, including its guardrails (bundled scripts live in the same
folder as the SKILL.md you found). If you cannot find it, stop and return an error field.`

phase('Bootstrap')
log(`Bare bootstrap: github.com/vezril/${name} (${visibility}), protected main, no docs`)
const boot = await workflow('new-github-project', { name, visibility, docs: false, ship: false })
if (!boot || boot.status !== 'complete') {
  return { status: 'failed', step: 'bootstrap', error: boot ? JSON.stringify(boot) : 'child workflow died' }
}
const dir = boot.localPath

phase('Scaffold')
const SCAFFOLD_STEPS = [
  { skill: 'scala-sbt-build', extra: `Run its scaffold script with project name "${name}" and pkg-root "${pkgRoot}". Skip the README-enrichment step for now — README.md does not exist yet.` },
  { skill: 'scala-pekko-server', extra: `Run its scaffold script with project name "${name}" and pkg-root "${pkgRoot}".` },
  { skill: 'scala-pekko-tests', extra: `Run its scaffold script with project name "${name}" (it reads the package from the generated sources).` },
  { skill: 'repo-starter-docs', extra: `No description was provided — use the skill's TODO placeholder; do not invent one and do not stop to ask.` },
  { skill: 'scala-sbt-build', label: 'readme-enrichment', extra: `ONLY perform the "README enrichment" section of the skill (README.md now exists from repo-starter-docs) — do not re-run the scaffold script.` },
  { skill: 'github-actions-scala-ci', extra: `Run its scaffold script with project name "${name}".` },
]
const scaffolded = []
for (const step of SCAFFOLD_STEPS) {
  const r = await agent(`
You are one scaffold step of the new-scala-pekko-service workflow (no human mid-run — never
stop to ask). Work inside ${dir} on branch feat/scaffold (create it from main if it does not
exist yet; if it exists, stay on it). Do NOT commit — the ship step owns git.
${findSkill(step.skill)}
${step.extra}
Return JSON only.`, {
    label: step.label || step.skill,
    phase: 'Scaffold',
    schema: {
      type: 'object',
      properties: {
        files: { type: 'array', items: { type: 'string' } },
        error: { type: 'string' },
      },
      required: ['files'],
    },
  })
  if (!r || r.error) {
    return { status: 'failed', step: step.label || step.skill, error: r ? r.error : 'agent died', repoCreated: true, repo: boot.repo }
  }
  scaffolded.push({ step: step.label || step.skill, files: r.files })
}

phase('Docker Hub')
let dockerhubResult = { skipped: true }
if (dockerhub) {
  dockerhubResult = await agent(`
You are the Docker Hub step of the new-scala-pekko-service workflow (no human mid-run).
${findSkill('dockerhub-setup')}
Project name "${name}", GitHub repo vezril/${name}. If the DOCKERHUB_* env credentials are
absent, follow the skill's Step 0: report it as skipped-resumable (NOT a workflow failure).
Return JSON only.`, {
    label: 'dockerhub-setup',
    schema: {
      type: 'object',
      properties: {
        hubRepo: { type: 'string' },
        tokenLabel: { type: 'string' },
        fallback: { type: 'boolean' },
        secretsSet: { type: 'array', items: { type: 'string' } },
        skipped: { type: 'boolean' },
        skipReason: { type: 'string' },
        error: { type: 'string' },
      },
      required: ['skipped'],
    },
  })
  if (!dockerhubResult || dockerhubResult.error) {
    return { status: 'failed', step: 'dockerhub-setup', error: dockerhubResult ? dockerhubResult.error : 'agent died', repoCreated: true, repo: boot.repo, scaffolded }
  }
} else {
  log('dockerhub: false — skipping; CI will skip image publishing (secrets absent).')
}

phase('Verify')
const gate = await agent(`
You are the green gate of the new-scala-pekko-service workflow. In ${dir} (branch
feat/scaffold), run exactly:
  sbt -batch scalafmtAll compile Test/compile test
Report honestly. If it exits non-zero, capture the failing output (last ~50 lines). Do NOT
push, commit, or "fix" anything — the gate only observes. Return JSON only.`, {
  label: 'sbt-green-gate',
  schema: {
    type: 'object',
    properties: {
      green: { type: 'boolean' },
      summary: { type: 'string' },
      failureOutput: { type: 'string' },
    },
    required: ['green', 'summary'],
  },
})
if (!gate || !gate.green) {
  log('Gate is RED — nothing will be pushed. The empty repo shell exists remotely.')
  return {
    status: 'failed', step: 'green-gate', repoCreated: true, repo: boot.repo, localPath: dir,
    scaffolded, failureOutput: gate ? gate.failureOutput || gate.summary : 'gate agent died',
    note: `The remote repo ${boot.repo} contains only the empty seed commit — delete it or re-run after fixing.`,
  }
}
log(`Gate is GREEN: ${gate.summary}`)

phase('Ship')
const ship = await agent(`
You are the final step of the new-scala-pekko-service workflow.
${findSkill('git-ship')}
Work inside ${dir}, branch feat/scaffold (already contains the full scaffold; the sbt suite
is green). Stage the scaffold explicitly (this is a freshly scaffolded repo — every file was
just created deliberately; include the OpenSpec configuration from bootstrap — openspec/
and .claude/ — if present), commit, push, open the PR against main titled
"Scaffold ${name}: Scala 3 + Pekko service (build, server, tests, docs, CI)".
Mode: ${auto
    ? `AUTO — the human launched the workflow with auto: true. Merge the PR, sync main, then create the development branch from merged main and push it (git branch development && git push -u origin development).`
    : 'GATED — no human is available mid-workflow: stop after creating the PR and return pendingApproval: true with the PR URL. Do NOT merge, do NOT create the development branch.'}
Return JSON only.`, {
  label: 'ship-scaffold',
  schema: {
    type: 'object',
    properties: {
      prUrl: { type: 'string' },
      merged: { type: 'boolean' },
      pendingApproval: { type: 'boolean' },
      mergeCommit: { type: 'string' },
      developmentPushed: { type: 'boolean' },
      error: { type: 'string' },
    },
    required: ['prUrl', 'merged'],
  },
})
if (!ship || ship.error) {
  return { status: 'failed', step: 'ship', error: ship ? ship.error : 'agent died', repoCreated: true, repo: boot.repo, scaffolded }
}

log(ship.merged ? 'Scaffold PR merged; development branch pushed.' : `Scaffold PR awaiting human approval: ${ship.prUrl}`)
return {
  status: ship.merged ? 'complete' : 'awaiting-merge-approval',
  repo: boot.repo,
  localPath: dir,
  protection: boot.protection,
  scaffolded,
  dockerhub: dockerhubResult,
  gate: gate.summary,
  pr: { url: ship.prUrl, merged: ship.merged, mergeCommit: ship.mergeCommit || null },
  nextStep: ship.merged
    ? null
    : `Ask the human to authorize the merge of ${ship.prUrl}. After merging: sync main, then create and push the development branch from merged main (git checkout main && git pull && git branch development && git push -u origin development).`,
}
