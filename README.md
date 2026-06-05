# claude-toolkit

A curated [Claude Code](https://code.claude.com) **plugin** bundling reusable **skills** and **subagents** — software-engineering disciplines and a comprehensive Akka suite, distilled from primary sources (books and official docs) and oriented toward a Scala / functional-programming stack.

The skills cross-reference each other via `[[name]]` links; the subagents apply them.

## Install (as a plugin)

This repo is both a plugin and a single-plugin marketplace. From Claude Code:

```
/plugin marketplace add vezril/claude-toolkit
/plugin install claude-toolkit@vezril-toolkit
```

(or `/plugin marketplace add /path/to/this/repo` for a local checkout). Installed skills are namespaced `claude-toolkit:<skill>` and subagents become available for delegation automatically.

### Manual install (without the plugin system)

Copy the folders into a project's `.claude/` (or `~/.claude/` for all projects):

```bash
cp -R skills/*  /path/to/repo/.claude/skills/
cp -R agents/*.md /path/to/repo/.claude/agents/
```

## Skills

**Software-engineering disciplines**

- **tdd** — strict Red-Green-Refactor.
- **functional-programming** — pure core / effectful shell, immutability, ADTs, total functions, errors-as-values (woven with *Grokking Simplicity*: actions/calculations/data, copy-on-write, stratified/onion architecture); grounded in the λ-calculus foundation below.
- **lambda-calculus** — Church's model of computation and the theory beneath FP (*Michaelson*): syntax, α/β/η-reduction, normal vs applicative order & Church–Rosser, currying, Church encodings, the Y combinator, and types.
- **scala** — Scala 2.13 idioms & gotchas (incl. the `sealed abstract case class` smart-constructor pattern).
- **python** — idiomatic, modern Python 3.x from *Effective Python*, *Fluent Python*, and *Automate the Boring Stuff*: the data model/dunders, comprehensions & generators, EAFP, dataclasses/type hints, the GIL & asyncio, stdlib + automation, and tooling (venv/ruff/black/mypy/pytest), with a Scala/FP comparison lens.
- **design-patterns** — the 23 Gang-of-Four patterns with Scala/FP mappings and a modern critique.
- **domain-driven-design** — Evans' tactical + strategic DDD, with a modern (microservices / event-sourcing) lens.
- **event-storming** — Brandolini's workshop technique: notation, facilitation, and the path from the wall to DDD/code.
- **modern-java** — Effective Java (3rd ed., all 90 items) on a Java 21 baseline with modern idioms.
- **cryptography** — Schneier's *Applied Cryptography* (with C examples) updated by *Cryptography Engineering* as the modern authority.
- **clean-code** — Robert Martin's readable/maintainable-code principles + the smells & heuristics catalog, with a balanced critique.
- **software-design** — Ousterhout's *A Philosophy of Software Design* (complexity, deep modules); the design tier above clean-code.
- **secure-coding** — defensive hardening against common vulnerability classes (memory safety, injection, auth/secrets/TLS); pairs with cryptography.
- **information-theory** — Cover & Thomas: entropy, KL divergence, mutual information, source-coding & channel-capacity limits, with applications to crypto, compression, coding, and ML.

**Agentic SDLC** (multi-agent software lifecycle; BMAD + Richards & Ford + Anthropic, adapted with execution-grounded review)

- **sdlc-orchestration** — meta: the four phases, maker-checker per phase, artifact-driven state, HITL gates; routes to the specialists below.
- **requirements-engineering** — PRD/SRS, the SPEC kernel, measurable NFRs, INVEST stories, elicitation & validation.
- **software-architecture** — *Fundamentals of Software Architecture* + C4 + ADRs: characteristics, styles & trade-offs, decisions, risk storming, diagramming.
- **spec-driven-development** — lock the *what* before the *how*; SPEC kernel, self-contained story files, document sharding.
- **test-strategy** — risk-based P0–P3, test levels/pyramid, ATDD, traceability, execution-grounded quality gates (complements tdd).
- **agentic-workflows** — Anthropic's workflow-vs-agent patterns + Claude Agent SDK loop + LangGraph; the runtime mechanics for the role agents.

**Operating systems** (OSTEP + Silberschatz + Tanenbaum; for writing one)

- **operating-systems** — meta/overview: the three pillars, kernel architectures, the subsystem map.
- **os-processes-and-scheduling** · **os-memory-and-virtual-memory** · **os-concurrency** · **os-file-systems-and-persistence** · **os-io-and-devices** · **os-virtualization** · **os-security** (subsystems).
- **osdev-kernel** — hands-on: toolchain, boot, QEMU, and the bring-up roadmap to actually write a kernel (x86-64 & ARM64, C or Rust).
- **6502-assembly** — the MOS 6502 CPU from *Easy 6502*: registers/flags, the instruction set, every addressing mode, branching/stack/subroutines, and a full Snake-game walkthrough (NES/C64/Apple II family).

**Akka** (Akka Core 2.10.x + ecosystem, Scala + Java Typed)

- **akka** — meta/overview: actor-model philosophy, module map, when to reach for each.
- **akka-actors** · **akka-cluster** · **akka-persistence** · **akka-streams** · **akka-discovery** · **akka-serialization** · **akka-utilities** (core).
- **akka-http** · **akka-grpc** · **alpakka** · **akka-projections** · **akka-persistence-plugins** (ecosystem).

**DevOps & operations**

- **devops** — principles meta: CALMS, the Three Ways (*Phoenix Project*) & Five Ideals (*Unicorn Project*), CI/CD/IaC, DORA metrics.
- **ansible** — agentless, idempotent configuration management / infrastructure as code.
- **site-reliability-engineering** — Google SRE: SLIs/SLOs/error budgets, toil, golden signals, on-call & blameless postmortems.

**Version control & CI/CD**

- **git** — the model (objects/DAG/refs/index) plus best-practice workflows: branching/merging/rebasing, conflict resolution, clean history & reflog recovery, collaboration/PRs, commit conventions, tags/releases (from *Mastering Git* + *Git Best Practices Guide*).
- **github-actions** — automating CI/CD with GitHub Actions: workflow syntax, events/jobs/matrix, writing actions, runners, secrets/OIDC, reusable workflows, and security hardening (from *Automating Workflows with GitHub Actions*).

**Design**

- **ux-design** — *Laws of UX*: psychology-based UX heuristics (Fitts/Hick/Miller/Jakob/Gestalt/…); pairs with the SwiftUI / apple-dev skills.

**Life & money**

- **personal-finance** — Hallam's *Balance* + Alini's *Money Like You Mean It* (Canadian): spending for happiness ("afford anything but not everything") and low-cost index investing, plus the practical toolkit — debt/credit, rent-vs-buy & mortgages, income/side hustles, insurance, wills, and couples/family money. Educational, not financial advice.
- **canadian-registered-accounts** — authoritative CRA mechanics for the FHSA, RRSP, and Home Buyers' Plan (eligibility, $8k/$40k & $60k limits, deductibility, repayment, FHSA+HBP stacking). Date-stamped; verify against canada.ca. Not tax advice.

**Games**

- **swgoh-expert** — Star Wars: Galaxy of Heroes expert assistant (teams, counters, mods, relics, GAC/TW/Conquest).

**Apple / Swift** (contributed; `apple-dev` meta added to route among them)

- **apple-dev** — meta/overview: the entry point and router for the Apple/Swift cluster below.
- **swiftui-ui-patterns** · **swiftui-view-refactor** · **swiftui-liquid-glass** · **swiftui-performance-audit** — building, refactoring, styling (iOS 26+ Liquid Glass), and auditing SwiftUI.
- **swift-concurrency-expert** — Swift 6.2+ concurrency review and remediation.
- **native-app-profiling** · **ios-debugger-agent** — profiling macOS/iOS apps (xctrace) and building/running/debugging on the simulator.
- **release-macos-spm-packaging** · **release-app-store-changelog** — SwiftPM macOS app packaging/signing and App Store release notes.
- **github-issue-fix-flow** — end-to-end GitHub issue → fix → build/test → push workflow.

Each skill is a folder with a `SKILL.md` (YAML frontmatter `name` + `description`, then the body); larger skills add `references/*.md` loaded on demand.

## Subagents

In `agents/` (see [`agents/README.md`](agents/README.md) for the frontmatter spec):

- **scala-fp-reviewer** — reviews Scala / functional code against the FP, Scala, TDD, and design-patterns skills.
- **akka-architect** — designs and reviews Akka systems using the Akka suite plus DDD and EventStorming.
- **git-and-ci-reviewer** — reviews Git hygiene (commits, branches, history) and GitHub Actions workflows for correctness and security.
- **personal-finance-advisor** — a warm, fiduciary-spirited money companion (budgeting, debt, low-cost investing, Canadian FHSA/RRSP/HBP) who educates and weighs trade-offs rather than selling or prescribing.
- **sdlc-orchestrator** · **requirements-analyst** · **solution-architect** · **story-planner** · **qa-test-architect** — the agentic-SDLC team: coordinate the pipeline, write the PRD/SRS, design the architecture, decompose into stories, and own the (execution-grounded) test strategy.

(See [`agents/README.md`](agents/README.md) for the full list.)

## Layout

```
.claude-plugin/
  plugin.json          # plugin manifest
  marketplace.json     # single-plugin marketplace (source ".")
skills/
  <skill>/SKILL.md     # + references/*.md for larger skills
agents/
  <agent>.md           # subagents (YAML frontmatter + system prompt)
  README.md            # subagent template & spec
LICENSE                # MIT
```

## License

MIT — see [LICENSE](LICENSE).
