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

- **`scala-fp-reviewer.md`** — reviews Scala / functional code against the FP, Scala, TDD, and design-patterns skills.
- **`akka-architect.md`** — designs and reviews Akka systems using the Akka suite plus DDD and EventStorming.

Add more by dropping a new `*.md` file in this directory following the template above.
