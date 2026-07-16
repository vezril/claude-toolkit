# Subagents

Claude Code **subagents** that live in this plugin. Each is a single Markdown file with YAML frontmatter; Claude Code auto-discovers `agents/*.md`. When the plugin is installed, Claude can delegate to these agents automatically (matching a request against the `description`) or you can invoke one explicitly.

## Frontmatter spec (template)

```markdown
---
name: my-agent                 # required, kebab-case, unique
description: >                  # required — the trigger. Describe WHAT it does and WHEN to use it.
  One or two sentences Claude matches against the user's request to decide whether to delegate.
tools: "Read, Grep, Glob, Bash" # optional — comma-separated; omit to inherit the caller's tools (+ MCP)
model: sonnet                   # optional — haiku | sonnet | opus | <full-model-id>; omit to inherit
skills:                         # optional — plugin skills this agent should use
  - claude-toolkit:scala
  - claude-toolkit:functional-programming
color: "#3b82f6"               # optional — UI accent
# other optional fields: disallowedTools, permissionMode, maxTurns, effort, isolation, background, memory
---

System prompt for the agent goes here (the body). Tell it its role, how to work,
what to produce, and which skills to lean on.
```

Notes:
- **`description` is the most important field** — it's how Claude decides to use the agent, so make it specific about both capability and trigger.
- Reference this plugin's skills as `claude-toolkit:<skill-name>` in the `skills:` list (e.g. `claude-toolkit:akka`, `claude-toolkit:domain-driven-design`).
- Give review/architecture agents read-only tools (`Read, Grep, Glob`, optionally `Bash` for tests/builds) so they advise rather than mutate.
- Use `${CLAUDE_PLUGIN_ROOT}` in any scripts/commands to reference files inside the plugin.

## Agents here

Design / modeling:

- **`domain-modeler.md`** — runs an EventStorming-style exploration and distills it into a DDD model (bounded contexts, aggregates, events) mapped to code.
- **`akka-architect.md`** — designs and reviews Akka systems on the **Core** libraries (actors, cluster, persistence, streams) plus DDD and EventStorming.
- **`akka-sdk-architect.md`** — designs and reviews **Akka SDK** (Java) services — choosing components (agents, entities, views, workflows, endpoints, consumers, timed actions) and the api/application/domain layout.

Agentic SDLC team:

- **`sdlc-orchestrator.md`** — drives a feature through analysis → planning → solutioning → implementation; opens the feature's OpenSpec change at Solutioning (`openspec new change` + proposal.md) and names `openspec archive` as the human-triggered close-out; delegates to the specialists, gates handoffs (readiness = lint-story.py **and** `openspec validate`, either failure short-circuits), keeps a human in the loop (plans/routes, doesn't write the content artifacts). Supports an opt-in **unattended mode** (trust rung 1: CI-triggered via `templates/unattended/`, mechanical gates + refuting review, ends at a PR — merge and archive stay human).
- **`requirements-analyst.md`** — elicits and writes the PRD/SRS or SPEC; measurable NFRs, INVEST stories, locks the *what* before the *how*.
- **`solution-architect.md`** — turns requirements into architecture (characteristics → style trade-offs → components → ADRs → risk storming → C4).
- **`story-planner.md`** — builds the change's delta specs and tasks.md, and decomposes PRD + architecture into epics and self-contained, INVEST, traceable story files (tasks.md references the stories).
- **`qa-test-architect.md`** — designs the risk-based test strategy and runs the **execution-grounded** quality gate (complements the dev pair).
- **`test-writer.md`** — the RED half of the dev pair: turns acceptance criteria into failing tests; may touch **test code only**, hands back a request when blocked on production code.
- **`implementer.md`** — the GREEN half of the dev pair: makes failing tests pass and refactors; may touch **production code only**, reports disputed tests instead of editing them.
  - The pair's file boundary is enforced mechanically by the plugin's PreToolUse hook (`hooks/enforce-dev-pair-boundary.py`), which denies Edit/Write calls outside each agent's territory.

Networking:

- **`network-architect.md`** — designs/reviews network architecture: addressing & subnetting (VLSM), VLAN segmentation, routing, and security zones, with a topology diagram.
- **`network-troubleshooter.md`** — diagnoses connectivity/performance bottom-up, execution-grounded (ping/traceroute/mtr/dig/ss/tcpdump); own/authorized networks only.

Game Dev Studio:

- **`game-dev-orchestrator.md`** — drives the game lifecycle (concept→prototype→slice→production→polish→ship), gating each phase on a **playtest**; delegates, HITL.
- **`game-designer.md`** — designs the core loop, mechanics, systems/balance, game feel; writes the GDD.
- **`game-systems-architect.md`** — engine choice, code architecture, game programming patterns, engine-vs-custom subsystems.
- **`gameplay-programmer.md`** — implements mechanics in Godot/GDScript, test-first where it pays, runs the game.
- **`level-designer.md`** — levels/content, pacing/difficulty, onboarding, author-vs-procedural.
- **`playtest-lead.md`** — plans/runs playtests (the empirical "is it fun?" gate) + risk-based code QA.
- **`technical-artist.md`** — shaders, VFX, juice, rendering setup, graphics performance.
- **`game-producer.md`** — scope, milestones, anti-crunch, validation, indie launch/marketing & monetization ethics.

Web development:

- **`full-stack-architect.md`** — designs/reviews web architecture: stack choice, rendering strategy (CSR/SSR/SSG/ISR/RSC), client–server boundary, API/data/auth, deploy topology + ADRs.
- **`frontend-reviewer.md`** — reviews React/Vue/TS/HTML/CSS for hooks/reactivity rules, accessibility, performance (Core Web Vitals), and XSS (read-only).
- **`webkit-developer.md`** — builds and debugs WKWebView-based browsers/web views end to end (delegates, JS bridges, content-rule-list blocking, data stores, downloads, Web Inspector debugging) and prepares WebKit-style patches for upstreaming; uses the **webkit** skill.

Cloud:

- **`gcp-developer.md`** — the Professional Cloud Developer role: builds and configures scalable, secure cloud-native apps on Google Cloud (platform choice, containers, event-driven flows, data access, app security, observability). Competencies mirror the certification's four sections; binds the `gcp-*` product skills plus the toolkit's dev-craft skills (tdd, test-strategy, clean-code, secure-coding, docker). Active: writes code and runs gcloud, with confirm-before-irreversible and credential-hygiene guardrails.

Review (read-only):

- **`clean-code-reviewer.md`** — language-agnostic readability/maintainability review (Clean Code principles + smells catalog).
- **`scala-fp-reviewer.md`** — reviews Scala / functional code against the FP, Scala, TDD, design-patterns, and clean-code skills.
- **`modern-java-reviewer.md`** — reviews Java code against Effective Java (Java 21) plus clean-code readability.
- **`swiftui-reviewer.md`** — reviews Swift / SwiftUI code (patterns, Observation, concurrency, performance, readability).
- **`crypto-reviewer.md`** — reviews code/designs for cryptographic correctness and safety.
- **`git-and-ci-reviewer.md`** — reviews Git hygiene (commits, branches, history) and GitHub Actions workflows for correctness and security.

Active coding / operations:

- **`tdd-coach.md`** — pairs on a feature test-first, driving strict Red-Green-Refactor (writes & runs code); the solo alternative to the test-writer + implementer pair.
- **`ios-app-debugger.md`** — builds/runs/debugs iOS/macOS apps on the simulator; reproduces, profiles, and fixes runtime issues.
- **`apple-release-manager.md`** — packages/signs/notarizes SwiftPM macOS apps and generates App Store release notes.
- **`issue-fixer.md`** — takes a GitHub issue end to end (gh → fix → build/test → commit & push); domain-neutral.

Communications & writing:

- **`calvin-voice-writer.md`** — drafts prose in Calvin's own writing voice (notes, journal entries, emails, chat/forum replies, posts) so it reads as if he wrote it from scratch; uses the **calvin-voice** skill and its three registers. Triggers on "write as me" prose, never on code or client deliverables.

Advisory (non-engineering):

- **`personal-finance-advisor.md`** — a warm, fiduciary-spirited personal-finance companion (budgeting, debt, low-cost investing, retirement, Canadian FHSA/RRSP/HBP); educates and lays out trade-offs, doesn't sell or give buy/sell calls; not a licensed advisor.
- **`business-formation-advisor.md`** — a practical guide for starting/registering a business in Canada (Quebec focus): structure choice, REQ/NEQ, incorporation, CRA BN & program accounts, Revenu Québec GST/QST; educates & lists steps, not legal/tax advice.
- **`quebec-paralegal.md`** — a paralegal-style research & drafting partner for Quebec/Canadian legal matters (leases & the TAL, Civil Code, Charter/discrimination, municipal by-laws, legal aid, Criminal Code, CHRA). Interviews for facts and **exact document wording**, **triages deadlines first**, cites only from **official sources** (LégisQuébec/laws-lois/TAL/CanLII — never invents an article, and names the **case-law gap** it can't close), steelmans the other side, and drafts correspondence — direct, succinct, welcoming — finishing with a **`humanize` pass that may change the writing but not the law**. Asks for missing statutes/by-laws and proposes where to find them, so they can become new skills. **Not a lawyer or notary; no legal advice; never sends or files.** Uses the seven Quebec/Canada legal skills + `humanize`.

Add more by dropping a new `*.md` file in this directory following the template above.
