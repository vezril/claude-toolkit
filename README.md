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
- **functional-programming** — pure core / effectful shell, immutability, ADTs, total functions, errors-as-values (woven with *Grokking Simplicity*: actions/calculations/data, copy-on-write, stratified/onion architecture).
- **scala** — Scala 2.13 idioms & gotchas (incl. the `sealed abstract case class` smart-constructor pattern).
- **design-patterns** — the 23 Gang-of-Four patterns with Scala/FP mappings and a modern critique.
- **domain-driven-design** — Evans' tactical + strategic DDD, with a modern (microservices / event-sourcing) lens.
- **event-storming** — Brandolini's workshop technique: notation, facilitation, and the path from the wall to DDD/code.
- **modern-java** — Effective Java (3rd ed., all 90 items) on a Java 21 baseline with modern idioms.
- **cryptography** — Schneier's *Applied Cryptography* (with C examples) updated by *Cryptography Engineering* as the modern authority.

**Akka** (Akka Core 2.10.x + ecosystem, Scala + Java Typed)

- **akka** — meta/overview: actor-model philosophy, module map, when to reach for each.
- **akka-actors** · **akka-cluster** · **akka-persistence** · **akka-streams** · **akka-discovery** · **akka-serialization** · **akka-utilities** (core).
- **akka-http** · **akka-grpc** · **alpakka** · **akka-projections** · **akka-persistence-plugins** (ecosystem).

Each skill is a folder with a `SKILL.md` (YAML frontmatter `name` + `description`, then the body); larger skills add `references/*.md` loaded on demand.

## Subagents

In `agents/` (see [`agents/README.md`](agents/README.md) for the frontmatter spec):

- **scala-fp-reviewer** — reviews Scala / functional code against the FP, Scala, TDD, and design-patterns skills.
- **akka-architect** — designs and reviews Akka systems using the Akka suite plus DDD and EventStorming.

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
