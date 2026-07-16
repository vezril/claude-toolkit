# claude-toolkit

A curated [Claude Code](https://code.claude.com) **plugin** bundling reusable **skills** and **subagents** across many domains — **software engineering** (with a comprehensive Akka suite), **communications & writing**, **personal finance**, plus networking, operating systems, DevOps, and game / web / Apple development — distilled from primary sources (books and official docs).

It began as a Scala / functional-programming toolkit and has grown into a general-purpose one. Its three most-developed pillars are **software engineering**, **communications** (writing in your own voice), and **finances** (Canadian personal finance and business setup); the rest fill out the stack around them.

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

**Session priming**

- **prime** — at the start of a session, analyzes the project (structure, architecture, design patterns, conventions) from **concrete evidence** (cross-validated, confidence-labelled, asks on ambiguity — no hallucination), produces a Priming Brief, then activates the matching skills and the sdlc-orchestrator team bound to the real stack.

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
- **openclaw-agents** — the agent system of OpenClaw (self-hosted messaging-gateway platform): the embedded per-session agent loop, the `openclaw agent` CLI + gateway `agent`/`agent.wait` RPC, lane-based concurrency, per-run prompt assembly, multi-agent config, thinking levels, tool policy + exec approvals, and `sessions_spawn` sub-agent delegation.

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
- **webassembly** — the portable sandboxed compilation target, in and out of the browser: the core language against Spec Release 3.0 (stack machine, modules, linear memory, soundness, GC/tail-calls/exceptions/memory64), the JS API + interop (streaming instantiation, the grow-detaches-buffer gotcha, COOP/COEP threads), toolchains (Emscripten, wasm-bindgen/wasm-pack, AssemblyScript, WABT), and WASI capability security + the server-side runtimes (from Sletten's *Definitive Guide*, the Core Spec read twice, and MDN; `references/` carry the depth).

**Home & IoT**

- **home-assistant** — the local-first home-automation platform (home-assistant.io): the entity/state model, automations/scripts/templating, Zigbee/Z-Wave/Matter/MQTT/ESPHome ecosystems, add-ons, recorder/statistics, and secure remote access + IoT segmentation. Pairs with the networking skills for VLANs/remote access.

**Networking** (Tanenbaum + Stevens + Network Warrior/CCNA/Network+; defensive security)

- **computer-networks** — meta/overview: the OSI/TCP-IP layered model, encapsulation, design principles, performance fundamentals; routes to the rest.
- **tcp-ip** — the protocol suite at the wire (Stevens): IP/ARP/ICMP/UDP/TCP, DNS/DHCP/NAT, handshake/congestion/MTU, reading captures.
- **network-engineering** — build & operate: subnetting/VLSM, VLANs/STP, routing (OSPF/BGP), NAT, and a bottom-up troubleshooting method.
- **network-security** — defensive infrastructure security: defense-in-depth/zero-trust, segmentation, firewalls/IDS/IPS, VPNs, DDoS defense, monitoring & IR.
- **wifi-pineapple** — operating the Hak5 WiFi Pineapple Mark VII (the commercial 802.11 wireless-auditing appliance) for **authorized** WiFi assessments: the UI (`172.16.42.1:1471`), PineAP (rogue-AP/association engine — modes, the SSID pool, Client/SSID filters for scoping, Evil WPA/Enterprise), Recon, WPA handshake capture (PCAP/Hashcat-22000, cracked offline), Campaigns, Modules, Cloud C², the REST/module-dev API, setup/recovery/LED states, and the 802.11 foundations that explain how it all works. A query-answering reference from Hak5's official docs; `references/` carry the depth. Own hardware / written authorization only.
- **hackrf-one** — operating the HackRF One (Great Scott Gadgets' open-source, half-duplex 1 MHz–6 GHz SDR transceiver): the specs (2–20 Msps, 8-bit I/Q, −5 dBm max input) and RF signal chain, the three RX gain stages + TX gain, sample-rate/baseband-filter choice, the CLI tools (`hackrf_info`, `hackrf_transfer` with every flag, `hackrf_sweep`, firmware/DFU recovery), the 8-bit signed I/Q format, the SDR software ecosystem (GNU Radio/gr-osmosdr, GQRX, URH, inspectrum), the DC-offset & ADC-overload artifacts, and troubleshooting. From the official docs (hackrf.readthedocs.io) + tool source; `references/` carry the depth. **RX broadly to learn; TX only on bands/power you're licensed or authorized to use.**
- **portapack-mayhem** — operating a HackRF One running PortaPack Mayhem firmware (the standalone touchscreen firmware that makes the HackRF computer-free): PortaPack models (H1/H2/H2+/H4M) + compatibility traps, firmware update (the three methods + the SD-content-must-match-version rule), the SD card layout, the UI & controls common to every app (frequency/digit mode, IF bandwidth, AMP/LNA/VGA gain staging), the ~90-app catalog by category, and the flagship capture→replay IQ workflow (C16/C8, the ≤500 kHz-for-reliable-replay rule, `.PPL` playlists), Recon scanning, Looking Glass, and the antenna calculator. From the official wiki + README; `references/` carry the depth. Sibling of hackrf-one. **RX broadly; TX only where licensed/authorized.**
- **flipper-zero** — operating the Flipper Zero multi-tool (STM32WB55; Sub-GHz radio, 13.56 MHz NFC, 125 kHz RFID, infrared, iButton/1-Wire, GPIO, BadUSB, U2F): the tech specs & controls (button combos, Dolphin XP, firmware channels, the serial CLI), each subsystem in depth — Sub-GHz (Read vs RAW, the region TX-frequency limits, the static-vs-rolling-code boundary the firmware enforces, vendors), NFC (card types, mfkey32 key recovery, magic cards, the crypto limits), 125 kHz RFID (LF-vs-HF, T5577 blanks, animal chips), Infrared (learn/universal remotes), iButton, BadUSB (DuckyScript), U2F, GPIO, and the `.fap` apps ecosystem (Flipper Lab, the API-mismatch gotcha). From the official docs (docs.flipper.net) via multi-agent research; `references/` carry the depth. Sibling of hackrf-one/portapack-mayhem. **Read broadly; the official firmware gates TX/replay by design — act only on what you own or are authorized to test.**
- **flipper-unleashed** — operating a Flipper Zero running the Unleashed Firmware (the DarkFlippers/@xMasterX community fork that removes the stock Sub-GHz region locks and adds rolling-code + extra protocols and an expanded app pack): documents only what Unleashed *changes* on top of the base device — the `e`/extra build, install (web.unleashedflip.com / Web Updater / qFlipper `.tgz`) & OTA, the fbt/ufbt build, the defining Sub-GHz features (`setting_user` custom frequencies, the larger static+KeeLoq protocol table, Remote Prog binding forms, `.txt` map remotes, Counter Mode), DangerousSettings (the *separate* hardware-limit unlock that can damage the radio), the bundled apps + `.fap`/`application.fam`, IR, expansion modules (nRF24, Wi-Fi devboard), and NFC/RFID notes. From the Unleashed repo docs via multi-agent research; `references/` carry the depth. Builds on the flipper-zero skill. **Unleashed removes the firmware guardrails — the legal responsibility for what you transmit is entirely the operator's; own/authorized equipment and bands only.**

**Version control & CI/CD**

- **git** — the model (objects/DAG/refs/index) plus best-practice workflows: branching/merging/rebasing, conflict resolution, clean history & reflog recovery, collaboration/PRs, commit conventions, tags/releases (from *Mastering Git* + *Git Best Practices Guide*).
- **github-actions** — automating CI/CD with GitHub Actions: workflow syntax, events/jobs/matrix, writing actions, runners, secrets/OIDC, reusable workflows, and security hardening (from *Automating Workflows with GitHub Actions*).
- **promptfoo** — test-driven LLM development with promptfoo (the eval framework): the `promptfooconfig.yaml` matrix (prompts × providers × tests → graded pass/fail), the assertion system (deterministic `contains`/`regex`/`javascript` + model-graded `llm-rubric`/`factuality`), the CLI + exit-100 CI contract, and GitHub Actions integration (the promptfoo-action, PR-comment gating, caching). Headline application: **regression-test your Claude Code skills** — load a `SKILL.md` as context, run query cases, and CI-gate its safety rails / accuracy / refusals / tone. From the promptfoo docs + repo; `references/` carry the assertion catalog and CI workflows.
- **github-new-repo** — create a brand-new empty GitHub repo (name + public/private as parameters), `main` seeded with an empty initial commit so protection and PRs work from day one.
- **github-branch-protection** — apply the standard `protect-main` ruleset to a repo (require PR with 0 approvals, block force-push and deletion); idempotent.
- **repo-starter-docs** — write a basic `README.md` and MIT `LICENSE.md` into the working tree (no commit — that's git-ship's job). `LICENSE.md` is the toolkit-wide standard for scaffolded projects.
- **git-ship** — commit on a feature branch, push, open the PR, and merge — merge gated on explicit human authorization unless auto mode was explicitly enabled for the run.

**Scala service scaffolding** (the decomposed successor to the retired `new-scala-service` monolith — see `archive/`)

- **scala-sbt-build** — the sbt build definition: two-module (pure core / Pekko server) `build.sbt` with all library dependencies, `project/` plugins (dynver, native-packager, scalafmt/scalafix, scoverage, buildinfo), formatter/linter configs, `.gitignore`; package root parameterized (default `me.cference`); enriches the README's Getting-started section after repo-starter-docs.
- **scala-pekko-server** — production sources only: core `Greeting`, `Main`, `HttpServer` (coordinated shutdown), hello + health routes, `AppConfig`, `application.conf`, `logback.xml`. Never touches tests.
- **scala-pekko-tests** — test sources only: `GreetingSpec` + route specs; reads the real package from the generated production code. Never touches production. (The dev pair's territory rule, applied to scaffolding.)
- **github-actions-scala-ci** — ci.yml (format / compile+test+coverage / dynver sanity / gitleaks), dev.yml (`:dev` images), release.yml (immutable semver images + GitHub Release), setup-scala composite action; image publishing skips gracefully when `DOCKERHUB_*` secrets are absent.
- **dockerhub-setup** — create the Docker Hub repo, mint a `<repo>-ci` access token via the Hub API (loud fallback to the admin PAT if minting fails), and pipe both values into GitHub Actions secrets; credentials from env only, never echoed.

**Python project scaffolding** (the Python sibling of the Scala set: uv + ruff + mypy + pytest, same territory rules)

- **python-uv-build** — pyproject.toml (hatchling src layout, dev group ruff/mypy/pytest, tool config), `.python-version`, `.gitignore`, multi-stage uv Dockerfile (`python -m <pkg>`, no HEALTHCHECK — the entry point is a CLI); package name derives scala-consistently (`athena-service` → `athena`); `uv.lock` deliberately not scaffolded (the verify gate's `uv sync` generates it); enriches the README after repo-starter-docs.
- **python-package** — production sources only: `src/<pkg>/` with the pure typed greeting module and the `__main__` CLI entry. Never touches tests.
- **python-tests** — test sources only: `tests/test_greeting.py`; reads the real package from `src/`. Never touches production.
- **github-actions-python-ci** — ci.yml (ruff lint, ruff format check as its own job, mypy, pytest via `uv sync --locked`, gitleaks), dev.yml (`:dev` images), release.yml (immutable semver images + GitHub Release), setup-uv composite action; image publishing skips gracefully when `DOCKERHUB_*` secrets are absent.

**Communications & writing**

- **calvin-voice** — drafts prose in the author's own writing voice (vault notes, journal entries, emails, chat replies, posts) so it reads as if he wrote it from scratch, not as a rewrite. Built eval-driven from a stylometric fingerprint of ~130k words of his own writing plus curated exemplars, with three registers (notes / journal / guide). Triggers only when asked to draft prose to send or publish as his own — never on code or client deliverables. Ships with the fingerprint pipeline (baseline + re-runnable stylometry script) so it can be rebuilt as the vault grows.
- **markdown** — writing Markdown, focused on Obsidian: portable CommonMark/GFM base (with the whitespace gotchas that actually bite) plus Obsidian Flavored Markdown in depth — `[[wikilinks]]` with heading/block links and display text, `![[embeds]]` with image sizing, block IDs, callouts (full type list + foldable/nested), YAML properties, tags, attachments, math/mermaid, comments — and an honest portability section on what breaks outside Obsidian. From markdownguide.org + the Obsidian help docs. Pairs with calvin-voice (voice vs. syntax).
- **cooklang** — writing Cooklang recipe files (`.cook`): the full token syntax (`@ingredient`, `#cookware`, `~timer`, quantities/units in `{qty%unit}`, preparations, the one-word-vs-`{}` rule that trips everyone up), steps as blank-line-separated paragraphs, sections/notes/comments, YAML frontmatter metadata (canonical `servings`/`source`/`time`/`tags` keys), scaling, and recipe references — plus the CookCLI toolchain (`recipe`/`shopping-list`/`server`/`import`/`doctor`/`pantry`) and `aisle.conf` shopping categories. Builds on markdown (`.cook` is Markdown-adjacent with identical YAML-frontmatter rules). From cooklang.org/docs + the CLI docs.
- **detect-ai** — local stylometric estimate (0–100, per-signal breakdown) of how AI-drafted a text reads: burstiness, cliché density, hedging, structural uniformity. Honest-confidence by design: no detector is reliable, results are never proof, and it refuses to be used to accuse a specific person of misconduct. Fully local — no text leaves the machine. *(Adapted from a third-party skill; safety-reviewed and rewritten — the original sent text + an API key to a paid service.)*
- **humanize** — edits stilted, AI-drafted, or over-formal prose to read naturally (rhythm variance, cliché removal, real stances, `--touch light|standard|deep`), with a hard scope boundary: refuses detector-evasion and academic-misrepresentation framing, and never fabricates "human" details. *(Adapted from a third-party detector-bypass tool; the bypass purpose was removed, not carried.)*
- **cold-email** — 50–125-word cold outreach drafts on AIDA/PAS/BAB with honesty guardrails: no fabricated personalization, no bait-and-switch subjects, no fake urgency, spam-law reminder for bulk. Drafts only — never sends. *(Adapted from a third-party skill.)*
- **follow-up** — re-engage a non-responder without nagging: bump → value-add → breakup matched to follow-up number, each shorter than the last, always a new angle; advises stopping after #3, and the breakup must be honest — no fake-breakups engineered for more outreach. *(Adapted from a third-party skill.)*
- **readability** — Flesch/Flesch-Kincaid/Fog/SMOG computed by a bundled stdlib-only Python script ("compute, don't estimate" — LLM syllable-counting is unreliable), then interpreted: audience fit plus three fixes quoting the actual text. *(Adapted from a third-party skill; script reviewed + executed here.)*
- **word-stats** — exact word/character/sentence/paragraph counts, reading & speaking time, vocabulary stats via a bundled stdlib-only script; one table, zero prose, no questions asked. *(Adapted from a third-party skill; script reviewed + executed here.)*

**Toolkit maintenance**

- **toolkit-archive** — retire a toolkit component into `archive/<name>/` with a `RETIRED.md` (what / why / replaced-by / date), de-index it from this README, and remove stale `~/.claude` installs; refuses while active components still reference it.
- **merge** — the end-of-change train: merge the gated PR → tag `vX.Y.Z` on merged `main` (fires release.yml where present) → `openspec archive` + land the bookkeeping. One invocation authorizes the train's merges; failing checks, uninvented versions, and ambiguity are absolute stops. Composes with git-ship: git-ship gets changes *to* the gate, merge takes them from it.

**Design**

- **ux-design** — *Laws of UX*: psychology-based UX heuristics (Fitts/Hick/Miller/Jakob/Gestalt/…); pairs with the SwiftUI / apple-dev skills.

**Personal finance & money**

- **personal-finance** — Hallam's *Balance* + Alini's *Money Like You Mean It* (Canadian): spending for happiness ("afford anything but not everything") and low-cost index investing, plus the practical toolkit — debt/credit, rent-vs-buy & mortgages, income/side hustles, insurance, wills, and couples/family money. Educational, not financial advice.
- **canadian-registered-accounts** — authoritative CRA mechanics for the FHSA, RRSP, and Home Buyers' Plan (eligibility, $8k/$40k & $60k limits, deductibility, repayment, FHSA+HBP stacking). Date-stamped; verify against canada.ca. Not tax advice.
- **canadian-business-registration** — starting/registering a business in Canada (Quebec focus): legal forms, the Québec REQ/NEQ, federal vs provincial incorporation, the CRA business number & program accounts, and the Quebec GST/QST-via-Revenu-Québec twist. Date-stamped; not legal/tax advice.
- **quebec-charter-rights** — the Charter of human rights and freedoms (Quebec, C-12), quasi-constitutional and enforced by the CDPDJ + Human Rights Tribunal. The two structural facts: it applies **horizontally to private actors** (s. 55 — unlike the Canadian Charter, which binds only government), and **s. 52 primacy covers ss. 1–38 only**, so the economic/social rights (39–48) don't override legislation. Covers the s. 10 grounds verbatim (a *closed* list incl. the Quebec-only **social condition, political convictions, language, civil status**), the equality machinery (harassment, juridical acts, void clauses, public places, employment), judicial rights reaching *civil* determinations, s. 48 exploitation of aged/handicapped persons, s. 49 remedies (punitive damages need **unlawful *and* intentional**), the CDPDJ's limited investigation mandate, and the **s. 84 ninety-day substitution** that is the only private route to the Tribunal. From the official LégisQuébec text; **educational information, not legal advice**.
- **canadian-criminal-code** — the Criminal Code (C-46) as a navigable map, parsed from the official consolidation (Part ranges measured from the body): the full Part structure I–XXVIII, the **classification system** that drives everything (and why "hybrid" appears *zero* times — it's structural), the s. 787 default penalty and the s. 786(2) 12-month summary limitation (indictable has none), general principles (s. 8(3) preserves common-law *defences* while s. 9 bars common-law *offences*), the defences (incl. **s. 17 duress, whose struck words still print**), where offences live, procedure (bail, the narrowed prelim, the election, jury architecture), sentencing (718/718.1/718.2, *Gladue*, discharges, CSOs, minimums), and the Charter overlay explaining why **the printed Code is not the law**. Orientation only — not advice, not a how-to.
- **canadian-human-rights-act** — the federal CHRA (H-6). **Leads with the scope trap**: the Act contains *no* list of covered industries — scope is s. 2 ("within the purview of matters coming within the legislative authority of Parliament") plus the Constitution, so it reaches only federally regulated things and **does not cover your provincial landlord or employer** (s. 6 prohibits housing discrimination but s. 2 caps it, so the Commission must decline under s. 41(1)(c) — in Quebec go to the CDPDJ under C-12). Covers the s. 3 grounds verbatim, the discriminatory practices, s. 15's BFOR and the duty to accommodate to undue hardship (**health, safety, cost** only), the one-year limitation running from the *last* act, that **only the Commission can refer** to the Tribunal, and the **$20k + $20k unindexed** non-pecuniary caps.
- **quebec-legal-system** — how the system works and how to get into it, from four statutes: **legal aid** (A-14 — the two tests, what's covered/excluded, the *last-resort* subsidiarity rule, that losing still exposes you to costs, the 30-day review that is final, and four free hours for violence victims regardless of means — with **no dollar thresholds, because the Act has none**), **municipal courts** (c-72.01 — optional, narrow, and *not* granted Criminal Code jurisdiction by that Act), the **Regulations Act** (R-18.1 — the 45-day minimum, in force 15 days after publication, and the s. 25 rule that only *publication* breaches invalidate), the **Compilation Act** (R-2.2.0.0.2 — s. 7 is *why* LégisQuébec is official "whatever the medium used"), and the CCQ-1992 transitional rules for situations straddling 1994.
- **quebec-municipal-law** — the Municipal Code of Québec (C-27.1) for local/rural municipalities and RCMs. **Two traps up front**: it does *not* apply to Cities-and-Towns-Act municipalities (parallel regimes, not layers), and **zoning is not in it** (that's A-19.1 — verified against all 10 cross-references) though *enforcement* runs back here. Covers the by-law lifecycle (art. 445, whose procedural breaches **entail nullity**), publication and coming into force, fine ceilings, **contesting a by-law (any interested party, $50 — but prescribed at 3 months from *passing*)**, the statutory question period, officers, and **art. 492 inspections** (7 a.m.–7 p.m., and only if the municipality actually passed the by-law — "inspector" appears zero times).
- **quebec-civil-code** — the Civil Code of Québec (CCQ, in force 1994) as a navigable map: the Preliminary Provision that makes it the *jus commune*, why Quebec is civil-law (and how that differs from the common-law provinces — codified principles over binding precedent), all ten Books with article ranges (Persons → Family → Successions → Property → **Obligations**, the giant → Hypothecs → Evidence → Prescription → Publication → Private International Law), the Book/Title/Chapter/Division hierarchy, reading an article's legislative history and decimal-numbered insertions, the civil-law vocabulary (patrimony, movable/immovable, hypothec, prescription, resiliation, solidary), **public order vs suppletive rules**, and cross-Book chains for real problems. Verified against the official LégisQuébec text. Date-stamped; **orientation, not legal advice**.
- **quebec-housing-rights** — Quebec residential tenancy (Civil Code + the Tribunal administratif du logement): **the actual lease articles 1851–1978** (scope incl. *accessories and dependencies* at 1892, the public-order clause 1893, obligations 1854/1855/1856, remedies 1863), the lease and its void clauses, the rent-disclosure notice, why deposits are illegal, rent increases & automatic renewal (and the notice windows where *silence = acceptance*), assignment vs subletting, both sides' obligations incl. the form/destination (change-of-use) rule, access/repairs/heating/pets, repossession vs eviction vs termination-for-fault kept distinct (with the 2024 changes), and the TAL process end to end (filing, evidence, hearings, appeal deadlines, enforcement). Statutory layer quoted from LégisQuébec + the TAL's citation map; plain-language layer from Éducaloi + quebec.ca; where sources conflicted the TAL governs and it's flagged. Date-stamped; **educational information, not legal advice**.

**Health & wellbeing**

- **phq-9** — walk someone through the PHQ-9 depression screening questionnaire as a warm, one-question-at-a-time supportive check-in (verbatim instrument, 0–27 scoring + severity bands, functional-impairment item, PHQ-2 pre-screen), with hard rails the roleplay never overrides: it's a **screen, not a diagnosis**; **not a replacement for professional care**; and any endorsement of item 9 (self-harm) triggers a real, non-fictional safety response + crisis resources (988/911/findahelpline.com) regardless of the total. From the PHQ-9 instrument PDFs + Wikipedia/MDCalc/safe-interpretation sources.
- **gad-7** — walk someone through the GAD-7 generalized-anxiety screening questionnaire as a warm, one-question-at-a-time supportive check-in (verbatim instrument, 0–21 scoring + severity bands, functional-impairment item, GAD-2 pre-screen, the ≥10 threshold; also screens panic/social-anxiety/PTSD, not just GAD), with hard rails the roleplay never overrides: it's a **screen, not a diagnosis**, and **not a replacement for professional care**. No self-harm item, but surfaces real crisis resources (988/911/findahelpline.com) if distress arises. Sibling of **phq-9**; anxiety and depression often co-occur.

**Games**

- **swgoh-expert** — Star Wars: Galaxy of Heroes expert assistant (teams, counters, mods, relics, GAC/TW/Conquest).
- **ttrpg-storytelling** — writing and running stories for tabletop RPGs: the collaborative stance (prep situations not plots, players as co-authors, session zero + safety tools), the writing craft (the 5 C's, conflict types, sensory world-building, NPCs/villains with quirks-motivations-secrets, campaign→arc→session structure), and the table craft (open with a Bang, share narration after wins, loop choices into consequences, equifinality, pacing, foreshadowing, cliffhangers) — plus a diagnose-a-flat-game section. Synthesized from four TTRPG storytelling guides.

**Apple / Swift** (contributed; `apple-dev` meta added to route among them)

- **apple-dev** — meta/overview: the entry point and router for the Apple/Swift cluster below.
- **swiftui-ui-patterns** · **swiftui-view-refactor** · **swiftui-liquid-glass** · **swiftui-performance-audit** — building, refactoring, styling (iOS 26+ Liquid Glass), and auditing SwiftUI.
- **swift-concurrency-expert** — Swift 6.2+ concurrency review and remediation.
- **native-app-profiling** · **ios-debugger-agent** — profiling macOS/iOS apps (xctrace) and building/running/debugging on the simulator.
- **release-macos-spm-packaging** · **release-app-store-changelog** — SwiftPM macOS app packaging/signing and App Store release notes.
- **github-issue-fix-flow** — end-to-end GitHub issue → fix → build/test → push workflow.
- **webkit** — building browsers and web-content apps on Apple WebKit: the WKWebView embedding surface by browser-building task (navigation policy, JS↔native via content worlds, content-rule-list blocking, data stores/private browsing/profiles, downloads, permissions), the multi-process model, `isInspectable` debugging, ITP mechanics + the tracking-prevention/security policies, ports/contributing/LGPL, and feature status (flags, css-status, standards-positions). From the Apple docs + webkit.org primary sources; `references/` carry the depth.

**Google Cloud Platform** (56 per-product skills, each distilled from the live `cloud.google.com` docs, fetched 2026-07 — decision-guidance and gotchas over reference regurgitation; all prefixed `gcp-` so non-GCP skills for the same tech can coexist)

- *API management & integration* — **gcp-api-gateway** · **gcp-apigee** · **gcp-endpoints** (managed front doors, lightweight → full-lifecycle) · **gcp-eventarc** · **gcp-workflows** · **gcp-application-integration** (event routing, orchestration, iPaaS).
- *Build, deploy & tooling* — **gcp-cloud-build** · **gcp-artifact-registry** · **gcp-artifact-analysis** · **gcp-buildpacks** · **gcp-app-hub** · **gcp-cloud-code** · **gcp-cloud-sdk** (the gcloud CLI + auth/ADC) · **gcp-cloud-scheduler** · **gcp-cloud-tasks**.
- *Compute & serverless* — **gcp-cloud-run** · **gcp-cloud-functions** (now Cloud Run functions) · **gcp-app-engine** · **gcp-gke** (Autopilot vs Standard) · **gcp-compute-engine**.
- *Data & analytics* — **gcp-bigquery** · **gcp-lakehouse** (Lakehouse for Apache Iceberg) · **gcp-looker** · **gcp-dataflow** · **gcp-pubsub**.
- *Databases* — **gcp-firestore** (Native mode) · **gcp-datastore** (Firestore in Datastore mode) · **gcp-bigtable** · **gcp-memorystore-redis** · **gcp-alloydb** · **gcp-spanner** · **gcp-cloud-sql**.
- *Networking* — **gcp-vpc** · **gcp-cloud-nat** · **gcp-cloud-vpn** · **gcp-interconnect** · **gcp-cloud-router** · **gcp-cloud-dns** · **gcp-load-balancing** · **gcp-cloud-domains** · **gcp-media-cdn** · **gcp-cloud-cdn**.
- *Security & observability* — **gcp-iam** · **gcp-iap** · **gcp-vpc-service-controls** · **gcp-secure-web-proxy** · **gcp-cloud-ids** · **gcp-certificate-manager** · **gcp-secret-manager** · **gcp-cloud-kms** · **gcp-binary-authorization** · **gcp-cloud-logging** (incl. audit logs) · **gcp-cloud-monitoring** · **gcp-cloud-trace** · **gcp-error-reporting**.
- *Storage* — **gcp-cloud-storage**.

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
- **webkit-developer** — builds and debugs WKWebView-based browsers/web views end to end (delegates, JS bridges, content blocking, data stores, downloads, Inspector debugging) and prepares WebKit-style patches for upstreaming.
- **gcp-developer** — builds scalable, secure cloud-native apps on Google Cloud (the Professional Cloud Developer role): platform choice, containers, event-driven flows, data access, app security, and observability — competencies mirror the certification, bound to the `gcp-*` skills plus the toolkit's dev-craft skills. Active: writes code and runs gcloud.
- **calvin-voice-writer** — drafts prose in Calvin's own writing voice (notes, emails, messages, posts) using the calvin-voice skill; for prose he'll send as his own, never code.

(See [`agents/README.md`](agents/README.md) for the full list.)

## Workflows

In `workflows/` — deterministic multi-agent scripts for Claude Code's Workflow tool. They are
not part of the plugin install; copy them to `.claude/workflows/` (project) or
`~/.claude/workflows/` (user) to make them invocable by name.

- **new-github-project** — end-to-end new-project bootstrap chaining the four skills above:
  create the local dir + empty GitHub repo (`github-new-repo`) → protect `main`
  (`github-branch-protection`; degrades with a loud warning where the plan forbids it, e.g.
  private repos on the free plan) → `openspec init --tools claude` → write starter docs
  (`repo-starter-docs`) → commit/PR (`git-ship`).
  Args: `{ name, visibility: 'public'|'private', auto?: true, docs?: true, ship?: true }`.
  `docs:false, ship:false` = **bare mode** (repo + protection only, returns synchronously) —
  the primitive that flavor workflows compose. The merge waits for human approval unless
  `auto` is passed.
- **new-scala-pekko-service** — the Scala 3 + Pekko flavor: bare bootstrap → decomposed
  scaffold on `feat/scaffold` (scala-sbt-build → scala-pekko-server → scala-pekko-tests →
  repo-starter-docs → README enrichment → github-actions-scala-ci) → optional dockerhub-setup →
  `sbt` green gate (red ships nothing) → one gated PR. Args: `{ name, visibility, dockerhub,
  auto?, pkgRoot? }` — `visibility` and `dockerhub` are required decisions, ask the human.
  After the merge, `development` is created from merged `main`. Vs. the old monolith:
  README/LICENSE come from repo-starter-docs (`LICENSE.md` standard) and the OpenSpec
  surface comes from the bootstrap's `openspec init --tools claude` — the scala scaffold
  scripts own neither.
- **new-python-project** — the Python 3.12 + uv flavor, same shape: bare bootstrap →
  scaffold on `feat/scaffold` (python-uv-build → python-package → python-tests →
  repo-starter-docs → README enrichment → github-actions-python-ci) → optional
  dockerhub-setup → uv green gate (`uv sync` + ruff check + format check + mypy + pytest;
  the generated `uv.lock` ships with the PR; red ships nothing) → one gated PR;
  `development` from merged `main` post-approval. Args: `{ name, visibility, dockerhub,
  auto?, pkg? }` — `visibility` and `dockerhub` are required decisions, ask the human.

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
workflows/
  <workflow>.js        # Workflow-tool scripts (copy into .claude/workflows/ to use)
archive/
  <name>/              # retired components, verbatim + RETIRED.md (inert; see archive/README.md)
LICENSE                # MIT
```

## License

MIT — see [LICENSE](LICENSE).
