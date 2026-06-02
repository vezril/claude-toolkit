# Discipline Skills (Claude Code / Agent SDK)

Three reusable skills distilled from the `scala-bioinformatics` project:

- **tdd** — strict Red-Green-Refactor discipline.
- **functional-programming** — pure core + effectful shell, ADTs, total functions, errors-as-values.
- **scala** — Scala 2.13 idioms and gotchas (incl. the `sealed abstract case class` smart-constructor pattern).

The skills cross-reference each other via `[[name]]` links and assume a Scala 2.13 + Cats Effect 3 + ScalaTest stack in their examples, but the disciplines (tdd, functional-programming) are language-agnostic.

## Install into a project

Copy the `skills/` folders into the target repo's `.claude/skills/` directory:

```bash
cp -R skills/tdd skills/functional-programming skills/scala /path/to/repo/.claude/skills/
```

Each skill is a folder containing a single `SKILL.md` with YAML frontmatter (`name`, `description`) followed by the skill body. Claude Code / the Agent SDK discovers them automatically from `.claude/skills/`.

To install for **all** projects instead of one repo, copy them into `~/.claude/skills/` instead.

## Layout

```
skills/
  tdd/SKILL.md
  functional-programming/SKILL.md
  scala/SKILL.md
```
