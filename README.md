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
- **cqrs-event-sourcing** — the event-driven data/consistency patterns (CQRS, Event Sourcing, Sagas, Domain Events) from Richardson's microservices.io + the CQRS community; why database-per-service forces them, and when not to.
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
- **agent-interoperability** — MCP (agent↔tool, rev 2025-11-25) + A2A (agent↔agent, v1.0): primitives, Agent Cards, transports, and when to use which.

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
- **terraform** — declarative IaC: providers/resources/state/modules, write→plan→apply, remote state & locking, policy-as-code & security scanning (provisioning; complements ansible's config management).
- **docker** — containerizing apps (*Docker in Action*): containers vs VMs, image layers & Dockerfiles, volumes, networking, Docker Compose, and an orchestration intro.
- **site-reliability-engineering** — Google SRE: SLIs/SLOs/error budgets, toil, golden signals, on-call & blameless postmortems.

**Game development** (Godot engine; Schell/Nystrom/Millington/Lengyel/Akenine-Möller + Gaffer/Red Blob) — a "Game Dev Studio" mirroring the SDLC team

- **game-development** — meta: the lifecycle (concept→prototype→vertical slice→production→polish→ship), find-the-fun-first, **playtesting as the quality gate**; routes to the rest.
- **game-design** — the Lenses (Schell), Theory of Fun, Game Feel, MDA, balance, the GDD.
- **game-programming-patterns** — Nystrom's catalog (game loop, component, state, observer, object pool, spatial partition…).
- **godot** — the engine: nodes/scenes/signals, GDScript lifecycle, 2D/3D, subsystems, Godot 3→4.
- **game-math** · **game-graphics** · **game-ai** · **game-physics** · **multiplayer-networking** · **procedural-generation** · **game-audio** — the technical specialties.
- **game-production** — scoping, milestones, anti-crunch, indie launch/marketing (monetization-ethics flagged).

**Web development** (Flanagan/Vanderkam/Wieruch + React/Next.js/Vue/TypeScript docs)

- **web-development** — meta/overview: how the stack fits together, the rendering-strategy spectrum (CSR/SSR/SSG/ISR/RSC), the client–server boundary, build/state/perf/security/deploy; routes to the rest.
- **javascript** — modern JS (ES2020+): types/coercion, closures, prototypes, `this`, the event loop, async/await, modules (Flanagan 7th + JS&jQuery).
- **typescript** — JS with static types: structural typing, generics, narrowing/discriminated unions, utility types, strict tsconfig (Effective TypeScript + docs).
- **html-css** — semantic HTML5 + modern CSS: the cascade/box model, Flexbox & Grid, responsive/mobile-first, typography, a11y.
- **react** — components/JSX, hooks & the Rules, "you might not need an effect", Suspense, RSC (Road to React + react.dev v19).
- **nextjs** — the App Router: Server Components, data fetching/streaming, Server Actions, rendering/caching (from the docs).
- **vue** — Vue 3: reactivity (ref/computed/watch), SFCs, Composition API, directives, Pinia/Vue Router.
- **nodejs** — JS on the server: the event loop, streams, modules, Express APIs, MongoDB (Node in Action).
- **nginx** — web server / reverse proxy / load balancer: config tree, TLS, proxying, load balancing, caching, rate limiting.

**Home & IoT**

- **home-assistant** — the local-first home-automation platform (home-assistant.io): the entity/state model, automations/scripts/templating, Zigbee/Z-Wave/Matter/MQTT/ESPHome ecosystems, add-ons, recorder/statistics, and secure remote access + IoT segmentation. Pairs with the networking skills for VLANs/remote access.

**Networking** (Tanenbaum + Stevens + Network Warrior/CCNA/Network+; defensive security)

- **computer-networks** — meta/overview: the OSI/TCP-IP layered model, encapsulation, design principles, performance fundamentals; routes to the rest.
- **tcp-ip** — the protocol suite at the wire (Stevens): IP/ARP/ICMP/UDP/TCP, DNS/DHCP/NAT, handshake/congestion/MTU, reading captures.
- **network-engineering** — build & operate: subnetting/VLSM, VLANs/STP, routing (OSPF/BGP), NAT, and a bottom-up troubleshooting method.
- **network-security** — defensive infrastructure security: defense-in-depth/zero-trust, segmentation, firewalls/IDS/IPS, VPNs, DDoS defense, monitoring & IR.

**Version control & CI/CD**

- **git** — the model (objects/DAG/refs/index) plus best-practice workflows: branching/merging/rebasing, conflict resolution, clean history & reflog recovery, collaboration/PRs, commit conventions, tags/releases (from *Mastering Git* + *Git Best Practices Guide*).
- **github-actions** — automating CI/CD with GitHub Actions: workflow syntax, events/jobs/matrix, writing actions, runners, secrets/OIDC, reusable workflows, and security hardening (from *Automating Workflows with GitHub Actions*).

**Design**

- **ux-design** — *Laws of UX*: psychology-based UX heuristics (Fitts/Hick/Miller/Jakob/Gestalt/…); pairs with the SwiftUI / apple-dev skills.

**Life & money**

- **personal-finance** — Hallam's *Balance* + Alini's *Money Like You Mean It* (Canadian): spending for happiness ("afford anything but not everything") and low-cost index investing, plus the practical toolkit — debt/credit, rent-vs-buy & mortgages, income/side hustles, insurance, wills, and couples/family money. Educational, not financial advice.
- **canadian-registered-accounts** — authoritative CRA mechanics for the FHSA, RRSP, and Home Buyers' Plan (eligibility, $8k/$40k & $60k limits, deductibility, repayment, FHSA+HBP stacking). Date-stamped; verify against canada.ca. Not tax advice.
- **canadian-business-registration** — starting/registering a business in Canada (Quebec focus): legal forms, the Québec REQ/NEQ, federal vs provincial incorporation, the CRA business number & program accounts, and the Quebec GST/QST-via-Revenu-Québec twist. Date-stamped; not legal/tax advice.

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
- **network-architect** · **network-troubleshooter** — design networks (addressing/segmentation/routing/zones) and diagnose connectivity/performance issues (execution-grounded: ping/traceroute/dig/tcpdump).
- **game-dev-orchestrator** · **game-designer** · **game-systems-architect** · **gameplay-programmer** · **level-designer** · **playtest-lead** · **technical-artist** · **game-producer** — the Game Dev Studio: drive the lifecycle, design, architect, implement (Godot), design levels/PCG, run playtests (the fun gate), shaders/juice, and production/launch.
- **frontend-reviewer** · **full-stack-architect** — review React/Vue/TS/HTML/CSS (hooks rules, a11y, perf, XSS) and design full-stack web architecture (stack, rendering strategy, API/data/auth, deploy).

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
