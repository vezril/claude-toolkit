# Agentic SDLC Team — Summary & Build Proposal

*One-pager from reviewing Aravinda Kumar's 9-part multi-agent SDLC series (2024–25) and the BMAD-method v6 agents reference. Purpose: decide which skills/agents to add to claude-toolkit. Nothing built yet.*

## What the sources say

**Kumar SDLC series** — automate the lifecycle with a multi-agent system: each phase is a **maker-checker pair + clarifier**, a **Coordinator** gates handoffs, a human approves (HITL). Linear artifact pipeline, each stage reads the prior markdown and emits a versioned one:

> client need → **SRS** → **HLD** → **code** → **regression test cases** → **IaC** (Terraform/Ansible)

Built on LangGraph/LangChain (`gpt-4o-mini`); bounded review loop (`max_iteration` + "Satisfied" sentinel). Final part pivots to **Google A2A** for cross-framework agent interop.

**BMAD (Breakthrough Method of Agile AI-Driven Development)** — the mature version of the same idea. Six named agents — **Mary** (analyst), **John** (PM/PRD), **Sally** (UX), **Winston** (architect), **Amelia** (dev), + **Murat** (test architect, add-on) — across 4 phases (Analysis → Planning → Solutioning → Implementation). Durable ideas: **artifacts are the handoff**, a **SPEC kernel** (Why/Capabilities/Constraints/Non-goals/Success) that locks *what* before *how*, **document sharding** for context, a **`bmad-help` orchestrator**, and **everything is a skill + named-agent persona** — i.e. exactly this toolkit's model. Interop via shared artifacts + **MCP** (no A2A).

## What modern agentic coding changes (the dated parts)

1. **Reviews must be execution-grounded.** The Kumar series' gates are LLM-judgment-only — nothing runs code, `terraform plan`, or tests, or measures coverage. Modern agents *execute* against a real workspace.
2. **Don't reinvent code-gen.** Concatenating SRS+HLD into one prompt and regex-scraping files is superseded by repo-aware tools (Claude Code, Cursor, Aider). Orchestrate around them.
3. **Interop moved on.** Convention is now "**MCP = agent↔tool, A2A = agent↔agent**"; the article's A2A surface is already stale (A2A → Linux Foundation). Re-verify specs before encoding.

**Key takeaway:** the toolkit already covers the *build/review* half (clean-code, software-design, tdd, secure-coding, ddd, event-storming, devops, ansible, sre, git, github-actions + reviewer agents + tdd-coach). The gap is the **upstream artifact roles + orchestration layer**.

## Proposed SKILLs (gaps, not duplicates)

| Skill | Scope | Resources to gather |
|---|---|---|
| `sdlc-orchestration` (meta) | The pipeline: phases, maker-checker, artifact handoffs, HITL, routing to existing skills | BMAD workflow docs; the Kumar Part 3 org chart |
| `agentic-workflows` | Multi-agent patterns: supervisor, maker-checker, bounded loops, execution-grounded review; LangGraph vs CrewAI vs AutoGen | LangGraph/CrewAI/AutoGen docs; agent-design papers/posts |
| `requirements-engineering` | SRS/PRD: functional vs non-functional, quantifying vague terms, the SPEC kernel | A requirements/PRD text; BMAD `bmad-prd`/`bmad-spec`; IEEE SRS template |
| `software-architecture` (HLD) | Architecture doc: 10 HLD sections, ADRs, C4/Mermaid, readiness gates (sits above `software-design` + `ddd`) | C4 model; ADR resources; an architecture-doc/HLD reference |
| `spec-driven-development` | Intent → spec → stories → execution; doc sharding; story files as dev context | BMAD spec/story docs; spec-driven-dev write-ups |
| `test-strategy` | Regression/test-case design, risk-based P0–P3, execution-grounded coverage (complements `tdd`) | Test-design/ISTQB material; BMAD TEA module |
| `agent-interoperability` | MCP + A2A done current: Agent Cards, tool-vs-agent protocols, when each applies | **Current** MCP spec + A2A spec (re-verify; both evolving) |
| `terraform` *(optional)* | IaC specifics beyond `devops`/`ansible` | Terraform docs |

## Proposed AGENTS

- **`sdlc-orchestrator`** — the Coordinator: drives a feature through the pipeline, delegates to role agents, gates handoffs, keeps HITL.
- **`requirements-analyst`** — interviews → produces/refines SRS/PRD.
- **`solution-architect`** — produces HLD/architecture doc with ADRs (distinct from `domain-modeler` and `akka-architect`).
- **`story-planner`** — architecture → epics/stories with acceptance criteria.
- **`qa-test-architect`** — designs the regression suite, grounded in execution.

*Implementation/review already covered by `tdd-coach`, the language reviewers, `clean-code-reviewer`, `git-and-ci-reviewer`, `issue-fixer` — wire in, don't duplicate.*

## Recommended build order

1. **First wave (completes the upstream team):** `sdlc-orchestration`, `requirements-engineering`, `software-architecture` skills + `sdlc-orchestrator`, `requirements-analyst`, `solution-architect` agents.
2. **Second wave:** `spec-driven-development`, `test-strategy`, `agentic-workflows` + `story-planner`, `qa-test-architect`.
3. **Hold:** `agent-interoperability` until MCP/A2A specs are re-verified.
4. **Cross-cutting rule:** bake **execution-grounded review** into every new agent (the series' biggest weakness).

## Principles to carry over

Artifacts are the handoff · lock the *what* before the *how* (SPEC kernel) · bounded review loops + HITL gates · shard large docs for context · skills + named personas · execute, don't opine.

## Build status (updated 2026-06-03)

**Built — 6 skills + 5 agents (committed to claude-toolkit):**

- Skills: `sdlc-orchestration`, `requirements-engineering` (+2 refs), `software-architecture` (+3 refs), `spec-driven-development`, `test-strategy`, `agentic-workflows` (+1 ref).
- Agents: `sdlc-orchestrator`, `requirements-analyst`, `solution-architect`, `story-planner`, `qa-test-architect`.
- Execution-grounded review baked into `sdlc-orchestrator`, `qa-test-architect`, and the `agentic-workflows`/`test-strategy` skills (the fix for the source frameworks' LLM-judgment-only gates).
- Sources used: BMAD repo (MIT) + workflow/agents articles; *Fundamentals of Software Architecture* (Richards & Ford); C4 model; Nygard ADRs; Cohn user stories; Anthropic "Building Effective Agents" + Claude Agent SDK; LangGraph; BMAD TEA. All in hand.

**Still missing / deferred (not built):**

- **`agent-interoperability`** (MCP + A2A) — *deliberately deferred*. Reason: A2A's surface is still evolving (donated to the Linux Foundation; early method names already stale) and MCP moves fast. **To build it, gather: the current MCP spec (modelcontextprotocol.io) and the current A2A spec.** `agentic-workflows` has a short interop note pointing here.
- **`terraform`** (optional) — IaC specifics beyond the existing `devops` + `ansible`. Only if you want deeper Terraform coverage; **gather: Terraform docs + tfsec/policy-as-code**.
- **Optional rigor add-on for `requirements-engineering`:** a formal **ISO/IEC/IEEE 29148** copy (the skill already encodes the key attributes; a full standard would deepen the reference).
- **Optional deepening for `software-architecture`:** the rest of the C4 site pages (levels/notation/FAQ) — I pulled these in while authoring; no action needed unless you want a dedicated C4 reference.

Nothing else outstanding — the upstream SDLC team is complete and integrated with the existing build/review skills and reviewer agents.

---
*Sources: Aravinda Kumar, "Building AI-Powered SDLC" series (Medium, 2024–25); BMAD-method v6 (docs + github, MIT); Richards & Ford, *Fundamentals of Software Architecture*; C4 model; Nygard ADRs; Cohn user stories; Anthropic "Building Effective Agents" + Claude Agent SDK; LangGraph.*
