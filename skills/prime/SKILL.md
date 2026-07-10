---
name: prime
description: Prime the session by analyzing the current project and building an evidence-grounded mental model before any work begins — its structure, tech stack, architecture style, design patterns, conventions, and constraints — then activate the relevant toolkit skills and hand off to the sdlc-orchestrator and its stack-matched team. Use at the START of a session on an unfamiliar or resumed codebase, or when the user says "prime", "prime the context", "analyze/onboard this project", "get up to speed on this repo", or "understand this codebase before we start". The defining rule is anti-hallucination: every claim must be backed by concrete evidence (file:line, real snippets, command output), corroborated by at least two signals, labeled with a confidence level, and anything ambiguous is asked — never guessed. Produces a Priming Brief and offers to persist it (CLAUDE.md / project-context). Routes to software-architecture, design-patterns, domain-driven-design, the language/web skills, and sdlc-orchestration.
---

# Prime

**Build an accurate, evidence-grounded model of the project before doing anything else.** When a session starts on a codebase (new or resumed), this skill surveys the repo, infers its architecture and conventions *from concrete evidence*, asks about what's ambiguous, and then activates the right toolkit skills and the **sdlc-orchestrator** team — primed and bound to the actual stack. The point is to start from *what is true about this repo*, not from assumptions.

The non-negotiable: **no hallucination.** Cross-validate, cite evidence, label confidence, ask when unsure.

Routes to: [[sdlc-orchestration]] (+ its agents, post-prime), [[software-architecture]] / [[software-design]] (architecture & module analysis), [[design-patterns]] / [[domain-driven-design]] / [[event-storming]] (patterns & domain), the **language/stack skills** ([[scala]]/[[functional-programming]], [[python]], [[web-development]] & its cluster, [[modern-java]], etc.), [[clean-code]], [[git]], [[test-strategy]], [[agentic-workflows]].

## The anti-hallucination contract (read first, applies throughout)

1. **Evidence or it's "unknown."** Every claim about the project cites concrete evidence — a **`path:line`**, a real code snippet, a manifest entry, or command output. If you can't point to evidence, say *"unknown — needs confirmation,"* don't fill the gap with a guess.
2. **Two signals, not one.** A folder named `domain/` is *not* proof of DDD/hexagonal; corroborate with a second independent signal (dependency direction, import graph, an actual aggregate/repository). Filenames and conventions *suggest*; code and config *confirm*.
3. **Execute to verify, don't infer.** Use `Bash` to *read reality*: `git log`/`git ls-files`, the build/test commands, dependency manifests, `tree`/`ls`. Prefer observed behavior (a passing test, a real build target) over inference from names. (This is [[sdlc-orchestration]]'s "execute, don't opine," applied to understanding.)
4. **Label confidence.** Mark each finding **High** (directly observed/executed), **Medium** (strong corroborated inference), or **Low** (single weak signal) — and say what would raise it.
5. **Ask, don't assume.** Collect ambiguities and **ask the user** before relying on them — especially intent, conventions not visible in code, and anything that would change how you work. One focused batch of questions, not a guess.
6. **Respect what exists.** An existing `CLAUDE.md`/`AGENTS.md`/`README`/ADRs/docs are primary sources — read and honor them; note where the code has drifted from them rather than trusting either blindly.

## The priming procedure

Work read-only and bottom-up; produce the Priming Brief at the end. Full per-ecosystem checklist + commands in `references/priming-playbook.md`.

### 1. Survey — what is this?
- **Read the front door:** `README*`, `CLAUDE.md`/`AGENTS.md`, `docs/`, `CONTRIBUTING`, ADRs. (Primary, human-authored intent.)
- **Read the manifests** (the ground truth for stack/deps): `package.json`/`tsconfig`, `build.sbt`/`pom.xml`/`build.gradle`, `pyproject.toml`/`requirements.txt`, `go.mod`, `Cargo.toml`, `Gemfile`, `Dockerfile`/`compose`, CI configs (`.github/workflows`). 
- **Map the tree:** top-level layout, source roots, module boundaries (`git ls-files | …`, `tree -L 3`). Find the **entry points** (main/app/index, server bootstrap, CLI).
- Output of this step: detected **languages, frameworks, build/test tooling, package layout** — each with the file that proves it.

### 2. Architecture & design patterns — how is it built? (evidence-first)
- **Architecture style** ([[software-architecture]]): is it a monolith / modular monolith / microservices / layered / hexagonal-ports-&-adapters / event-driven? **Confirm from ≥2 signals** — directory layout *and* dependency direction (who imports whom), the presence of real boundaries (a `ports`/`adapters` split with interfaces, a message bus, service-per-deployable), the data architecture (one DB vs database-per-service → [[cqrs-event-sourcing]]).
- **Design patterns** ([[design-patterns]] / [[domain-driven-design]]): identify patterns actually present — repositories, factories, strategies, observers, DI, ADTs/sealed hierarchies, aggregates/value objects/bounded contexts ([[event-storming]]). Cite the concrete class/file for each; don't pattern-match on names.
- **Key abstractions & data flow:** the core domain types, the request/data path (entry → core → persistence), error-handling style, concurrency/async model. Draw a small **C4-ish** picture (Mermaid) *only* from what you verified.
- **Conventions:** test framework + how tests are run + where they live ([[test-strategy]]/[[tdd]]), code style/lint/format, the git workflow and branch/commit conventions ([[git]]), CI/CD ([[github-actions]]).
- Cross-validate each architectural claim; downgrade or drop anything you can't corroborate.

### 3. Reconcile & flag ambiguities
- **Reconcile** the docs vs the code (does the README's described architecture match what the imports show? is there drift?). Note discrepancies explicitly.
- **List ambiguities** you genuinely can't resolve from the repo: intent/roadmap, why a surprising choice was made, undocumented conventions, which of two patterns is "the" convention, what's legacy vs current. Turn these into **specific questions** for the user (use AskUserQuestion or a short numbered list) — and **wait** for answers before treating them as fact.

### 4. Produce the Priming Brief
A concise, skimmable brief (not a dump):
- **What it is** — purpose, stack, build/test/run commands (verified).
- **Architecture** — style + the evidence; a small diagram; module/boundary map.
- **Patterns & key abstractions** — with `path:line` citations.
- **Conventions** — testing, style, git, CI.
- **Confidence & gaps** — what's High/Medium/Low; what's unknown.
- **Open questions** — the ambiguities needing the user's answer.
Offer to **persist** it (write/update `CLAUDE.md` or a `docs/project-context.md`) so the priming survives the session — only after the user confirms it's accurate.

### 5. Activate the toolkit & hand off to the SDLC team
Now bind the work to the evidence:
- **Engage the matching skills:** the language/stack skills for what's actually used (e.g. [[scala]]+[[functional-programming]] for a Scala/Cats repo; [[web-development]]+[[react]]/[[nextjs]]/[[typescript]] for a Next.js app; [[python]]; [[modern-java]]; [[akka]]; etc.), plus [[software-architecture]]/[[design-patterns]]/[[domain-driven-design]] for ongoing design work.
- **Bring in the sdlc-orchestrator and its team**, bound to the detected stack ([[sdlc-orchestration]]'s "match the specialist to the stack"): the **sdlc-orchestrator** to drive any feature work; the **solution-architect** (or **full-stack-architect** for web) for design; the **requirements-analyst**, **story-planner**, **qa-test-architect**; the **test-writer** + **implementer** dev pair for the build loop; and the **review** layer matched to the stack (**frontend-reviewer** for web, **scala-fp-reviewer**/**modern-java-reviewer** for JVM, plus **clean-code-reviewer**, **git-and-ci-reviewer**).
- State the handoff: "Primed. Stack = X; architecture = Y (evidence …); conventions = Z. The sdlc-orchestrator + {these agents} are ready. Open questions: …" — then ask what we're working on.

## When to use / not use

- **Use** at the start of a session on a codebase you (or the user) want me grounded in before changes; on resume after a gap; when handed an unfamiliar repo.
- **Skip / lighten** for a trivial one-file question or a brand-new empty repo (there's nothing to analyze — instead help scaffold via [[sdlc-orchestration]]).
- Scale the depth to the task: a quick orientation for a small fix; the full brief before a feature or refactor.

## Anti-patterns

- **Asserting architecture from folder names** or a framework's presence without confirming in code (the cardinal sin this skill exists to prevent).
- Inventing commands/conventions ("run `npm test`") without verifying they exist in the manifest/CI.
- Skipping execution (never running `git log`/build/test) and guessing instead.
- Presenting inferences as facts with no confidence labels; burying the user in a file dump instead of a brief.
- Proceeding past genuine ambiguity without asking; ignoring an existing `CLAUDE.md`/ADRs.
- Over-priming a trivial task; priming once and never updating as you learn more.

## Always-apply

1. **Evidence or "unknown"** — cite `path:line`/snippets/command output for every claim; **execute to verify**.
2. **Corroborate with ≥2 signals**; **label confidence** (High/Med/Low) and what would raise it.
3. **Ask about ambiguities** (don't guess); honor existing `CLAUDE.md`/docs and note drift.
4. Produce a **skimmable Priming Brief**; offer to **persist** it once the user confirms.
5. **Activate the matching skills and the sdlc-orchestrator team bound to the real stack**, then ask what we're doing.

## How to use the reference

- **`references/priming-playbook.md`** — the per-ecosystem file/command checklist (what to read and run for JS/TS, Python, JVM/Scala, Go, etc.), the architecture-evidence table (signal → what confirms it), the Priming Brief template, and the stack→skills/agents routing map.

## Related

- [[sdlc-orchestration]] — the pipeline + team this hands off to (stack-matched); [[agentic-workflows]] — the orchestration patterns.
- [[software-architecture]] / [[software-design]] / [[design-patterns]] / [[domain-driven-design]] / [[event-storming]] — the lenses for the architecture/pattern analysis.
- [[git]] / [[test-strategy]] / [[tdd]] / [[github-actions]] — convention/CI evidence.
- Stack skills it activates: [[scala]] · [[functional-programming]] · [[python]] · [[modern-java]] · [[web-development]] (+[[react]]/[[vue]]/[[nextjs]]/[[nodejs]]/[[typescript]]/[[html-css]]) · [[akka]] · [[docker]] · … (whatever the evidence shows).
