export const meta = {
  name: 'new-python-project',
  description: 'Bootstrap a Python 3.12 + uv project: bare repo bootstrap, decomposed scaffold, optional Docker Hub wiring, uv green gate, one gated PR',
  whenToUse: 'When starting a brand-new Python project from nothing (uv + ruff + mypy + pytest, optional Docker publishing). The Python sibling of new-scala-pekko-service.',
  phases: [
    { title: 'Bootstrap', detail: 'new-github-project in bare mode: repo + protected main + openspec init' },
    { title: 'Scaffold', detail: 'sequential on feat/scaffold: build → package → tests → docs → CI' },
    { title: 'Docker Hub', detail: 'repo + CI token + GitHub secrets (only if dockerhub: true)' },
    { title: 'Verify', detail: 'uv sync + ruff check + ruff format --check + mypy + pytest — red ships nothing' },
    { title: 'Ship', detail: 'one PR (uv.lock included); merge gated on the human unless auto' },
  ],
}

// args: { name, visibility: 'public'|'private', dockerhub: boolean, auto?: false, pkg?: derived }
// name, visibility AND dockerhub are required with no defaults — the outer conversation
// must ask the human. Package derives scala-consistently (name minus -service/-svc,
// hyphens -> underscores); override with pkg.

// Tolerate stringified args (some invokers pass JSON text rather than an object).
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch { /* falls through to the guard */ } }
if (!A || typeof A !== 'object') {
  throw new Error("args required: { name, visibility: 'public'|'private', dockerhub: true|false, auto?: true, pkg?: 'mytool' }")
}
const { name, visibility } = A
const auto = A.auto === true
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
const pkg = A.pkg || null // scripts derive the default themselves
const pkgArg = pkg ? ` and package-name "${pkg}"` : ''

const findSkill = (skill) => `
First locate the skill file ${skill}/SKILL.md. Check in order (glob, take the first hit):
  1. $HOME/.claude/skills/${skill}/SKILL.md
  2. $HOME/.claude/plugins/**/skills/${skill}/SKILL.md
  3. $HOME/Code/claude-toolkit/skills/${skill}/SKILL.md
Read it and follow it EXACTLY, including its guardrails (bundled scripts live in the same
folder as the SKILL.md you found). If you cannot find it, stop and return an error field.`

phase('Bootstrap')
log(`Bare bootstrap: github.com/vezril/${name} (${visibility}), protected main, openspec init, no docs`)
const boot = await workflow('new-github-project', { name, visibility, docs: false, ship: false })
if (!boot || boot.status !== 'complete') {
  return { status: 'failed', step: 'bootstrap', error: boot ? JSON.stringify(boot) : 'child workflow died' }
}
const dir = boot.localPath

phase('Scaffold')
const SCAFFOLD_STEPS = [
  { skill: 'python-uv-build', extra: `Run its scaffold script with project name "${name}"${pkgArg}. Skip the README-enrichment step for now — README.md does not exist yet.` },
  { skill: 'python-package', extra: `Run its scaffold script with project name "${name}"${pkgArg}.` },
  { skill: 'python-tests', extra: `Run its scaffold script with project name "${name}" (it reads the package from src/).` },
  { skill: 'repo-starter-docs', extra: `No description was provided — use the skill's TODO placeholder; do not invent one and do not stop to ask.` },
  { skill: 'python-uv-build', label: 'readme-enrichment', extra: `ONLY perform the "README enrichment" section of the skill (README.md now exists from repo-starter-docs) — do not re-run the scaffold script.` },
  { skill: 'github-actions-python-ci', extra: `Run its scaffold script with project name "${name}".` },
]
const scaffolded = []
for (const step of SCAFFOLD_STEPS) {
  const r = await agent(`
You are one scaffold step of the new-python-project workflow (no human mid-run — never
stop to ask). Work inside ${dir} on branch feat/scaffold (create it from main if it does
not exist yet; if it exists, stay on it). Do NOT commit — the ship step owns git.
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
You are the Docker Hub step of the new-python-project workflow (no human mid-run).
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
You are the green gate of the new-python-project workflow. In ${dir} (branch feat/scaffold),
run exactly, in order, stopping at the first failure:
  uv sync
  uv run ruff check .
  uv run ruff format --check .
  uv run mypy src
  uv run pytest
Note: uv sync GENERATES uv.lock — that is intended; the lockfile ships with the PR.
Report honestly. If any command exits non-zero, capture its output (last ~50 lines). Do NOT
push, commit, or "fix" anything — the gate only observes. Return JSON only.`, {
  label: 'uv-green-gate',
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
    status: 'failed', step: 'uv-green-gate', repoCreated: true, repo: boot.repo, localPath: dir,
    scaffolded, failureOutput: gate ? gate.failureOutput || gate.summary : 'gate agent died',
    note: `The remote repo ${boot.repo} contains only the empty seed commit — delete it or re-run after fixing.`,
  }
}
log(`Gate is GREEN: ${gate.summary}`)

phase('Ship')
const ship = await agent(`
You are the final step of the new-python-project workflow.
${findSkill('git-ship')}
Work inside ${dir}, branch feat/scaffold (already contains the full scaffold; the uv gate
is green). Stage the scaffold explicitly (this is a freshly scaffolded repo — every file
was just created deliberately; include uv.lock and the OpenSpec configuration from
bootstrap — openspec/ and .claude/ — if present; never stage .venv/), commit, push, open
the PR against main titled
"Scaffold ${name}: Python 3.12 + uv project (build, package, tests, docs, CI)".
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
