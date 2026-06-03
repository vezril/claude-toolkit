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

Review (read-only):

- **`clean-code-reviewer.md`** — language-agnostic readability/maintainability review (Clean Code principles + smells catalog).
- **`scala-fp-reviewer.md`** — reviews Scala / functional code against the FP, Scala, TDD, design-patterns, and clean-code skills.
- **`modern-java-reviewer.md`** — reviews Java code against Effective Java (Java 21) plus clean-code readability.
- **`swiftui-reviewer.md`** — reviews Swift / SwiftUI code (patterns, Observation, concurrency, performance, readability).
- **`crypto-reviewer.md`** — reviews code/designs for cryptographic correctness and safety.
- **`git-and-ci-reviewer.md`** — reviews Git hygiene (commits, branches, history) and GitHub Actions workflows for correctness and security.

Active coding / operations:

- **`tdd-coach.md`** — pairs on a feature test-first, driving strict Red-Green-Refactor (writes & runs code).
- **`ios-app-debugger.md`** — builds/runs/debugs iOS/macOS apps on the simulator; reproduces, profiles, and fixes runtime issues.
- **`apple-release-manager.md`** — packages/signs/notarizes SwiftPM macOS apps and generates App Store release notes.
- **`issue-fixer.md`** — takes a GitHub issue end to end (gh → fix → build/test → commit & push); domain-neutral.

Advisory (non-engineering):

- **`personal-finance-advisor.md`** — a warm, fiduciary-spirited personal-finance companion (budgeting, debt, low-cost investing, retirement, Canadian FHSA/RRSP/HBP); educates and lays out trade-offs, doesn't sell or give buy/sell calls; not a licensed advisor.

Add more by dropping a new `*.md` file in this directory following the template above.
