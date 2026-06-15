# Priming playbook — checklists, evidence table, brief template

The concrete procedure for the `prime` skill. All steps are **read-only**; verify by reading files and running safe inspection commands. Never assert without evidence.

## Evidence-gathering commands (safe, read-only)
```bash
# Tree & inventory (respects .gitignore via git)
git ls-files | head -200
git ls-files | sed 's@/[^/]*$@@' | sort -u        # directories
tree -L 3 -I 'node_modules|.git|target|dist|build|.venv' 2>/dev/null

# History & activity (what's real/active, not aspirational)
git log --oneline -20
git log --since="3 months ago" --pretty=format: --name-only | sort | uniq -c | sort -rn | head  # hot files
git shortlog -sn | head            # who/what areas

# Manifests / config (ground truth for stack)
cat package.json tsconfig.json 2>/dev/null
cat build.sbt pom.xml build.gradle* 2>/dev/null
cat pyproject.toml requirements.txt setup.cfg 2>/dev/null
cat go.mod Cargo.toml Gemfile 2>/dev/null
ls .github/workflows/ && cat .github/workflows/*.yml 2>/dev/null
cat Dockerfile docker-compose*.yml 2>/dev/null

# Conventions docs
cat README* CLAUDE.md AGENTS.md CONTRIBUTING* 2>/dev/null; ls docs/ adr/ doc/ 2>/dev/null

# Verify the build/test actually work (execution-grounded) — only if quick/safe
<the test command from the manifest, e.g. npm test / sbt test / pytest / go test ./...>
```
Use `Grep`/`Glob` to trace imports and find patterns (e.g. who imports the `domain` package, where repositories/interfaces live).

## Per-ecosystem: what to read
| Stack | Manifest / signals | Read for stack & layout |
|------|--------------------|--------------------------|
| **JS/TS** | `package.json` (deps/scripts), `tsconfig.json`, lockfile, `.github/workflows` | framework (react/next/vue/express/nest), `strict` TS, test runner, `src/` layout → [[web-development]] cluster |
| **Python** | `pyproject.toml`/`requirements.txt`, `ruff`/`mypy` cfg, `tox`/`pytest.ini` | web framework (django/flask/fastapi), packaging, `src/` layout → [[python]] |
| **JVM/Scala** | `build.sbt`/`build.gradle`/`pom.xml`, `project/plugins.sbt` | Cats/ZIO/Akka/Spring, modules, test fw → [[scala]]/[[functional-programming]]/[[akka]]/[[modern-java]] |
| **Go** | `go.mod`, `cmd/`, `internal/` | std layout, frameworks → (no skill yet — analyze generically) |
| **Rust** | `Cargo.toml`, workspace members | crates/workspace |
| **Infra** | `Dockerfile`/compose, `*.tf`, `ansible/`, `k8s/` | [[docker]]/[[terraform]]/[[ansible]]/[[devops]] |

## Architecture-evidence table (signal → what actually confirms it)
| Claim | A folder name is NOT enough — confirm with… |
|------|----------------------------------------------|
| **Layered (n-tier)** | imports flow one direction across `controller→service→repository`; no upward deps |
| **Hexagonal / ports & adapters** | a `domain`/`core` with **interfaces (ports)** + separate `adapters`/`infra` implementing them; domain imports nothing outward |
| **Microservices** | multiple independently deployable services, each with its own build + **own datastore** (database-per-service → [[cqrs-event-sourcing]]); inter-service calls over HTTP/queue, not in-process |
| **Modular monolith** | one deployable, but clear internal module boundaries + enforced dep rules |
| **Event-driven / CQRS / ES** | a message bus/broker, event types, handlers/projections, an event store/append-only log ([[cqrs-event-sourcing]]) |
| **DDD** | aggregates/entities/value objects, repositories, a ubiquitous-language glossary, bounded-context boundaries ([[domain-driven-design]]) — in code, not just folders |
| **DI / IoC** | a container/wiring module or constructor-injection throughout |
| **Functional core** | immutable types, ADTs/sealed hierarchies, pure functions, effects at the edge ([[functional-programming]]) |
Each: cite the **file(s)** and a snippet. If only one weak signal → **Low confidence**, or "unknown."

## The Priming Brief (template)
```markdown
# Priming Brief — <repo>

## What it is
<purpose, 1–2 lines>. Stack: <langs/frameworks> [evidence: package.json:…].
Build: `…`  · Test: `…`  · Run: `…`   (verified ✓ / not run)

## Architecture
Style: <e.g. modular monolith, layered> — **confidence: High/Med/Low**
Evidence: <dir layout path>, <dependency direction observed in path:line>.
[Mermaid container/module diagram — only verified elements]
Modules/boundaries: <list with paths>.

## Patterns & key abstractions
- <Repository> — `path:line`
- <ADT / aggregate / DI> — `path:line`
Data flow: entry (`path`) → core (`path`) → persistence (`path`). Error handling: <style>. Concurrency: <model>.

## Conventions
Tests: <fw>, run `…`, in `path/` [evidence]. Style/lint: <tool> [cfg path]. Git: <branch/commit convention> [from git log]. CI: <what .github/workflows does>.

## Confidence & gaps
High: … · Medium: … · Low/unknown: …

## Open questions (need your answer)
1. …
2. …
```
Persist (with the user's OK) to `CLAUDE.md` or `docs/project-context.md`.

## Stack → skills/agents routing (step 5)
| Detected | Activate skills | SDLC team binding |
|----------|-----------------|-------------------|
| Web (React/Next/Vue/Node/TS) | [[web-development]] + [[react]]/[[nextjs]]/[[vue]]/[[nodejs]]/[[typescript]]/[[html-css]] | solutioning → **full-stack-architect**; review → **frontend-reviewer** |
| Scala / FP | [[scala]], [[functional-programming]], [[akka]] (if present) | review → **scala-fp-reviewer**; design → **solution-architect**/**domain-modeler** |
| JVM / Java | [[modern-java]] | review → **modern-java-reviewer** |
| Python | [[python]] | solution-architect; clean-code-reviewer |
| Apple/Swift | [[apple-dev]] + swift skills | swiftui-reviewer / ios-app-debugger |
| Any | [[software-architecture]], [[design-patterns]], [[clean-code]], [[test-strategy]], [[git]] | **sdlc-orchestrator** to drive; **requirements-analyst** / **story-planner** / **qa-test-architect**; **tdd-coach**, **clean-code-reviewer**, **git-and-ci-reviewer** |
Always: bind to what the **evidence** shows, not what's fashionable; if the stack has no dedicated skill, analyze generically with the architecture/design skills and say so.
