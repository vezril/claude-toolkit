---
name: test-strategy
description: Test strategy and quality architecture — designing what to test, at what level, and in what priority, distinct from the red-green-refactor mechanics of TDD. Covers risk-based prioritization (P0–P3 by impact × likelihood), the test pyramid / levels (unit, integration, contract, e2e) and where coverage belongs, acceptance-test-driven development (ATDD) from acceptance criteria, requirements-to-test traceability, regression-suite design (proactive, before testing begins), test-case structure, what to automate vs not, flaky/self-healing-test concerns, and the principle that quality gates must be execution-grounded (run the tests, measure real coverage) not LLM-judgment. Adapted from the BMAD Test Architect (TEA) module and risk-based testing practice. Use when planning a test strategy, prioritizing tests by risk, designing a regression suite, turning acceptance criteria into tests, deciding test levels/what to automate, or setting up a quality gate. Complements tdd (the inner loop) and consumes requirements-engineering's acceptance criteria; part of the sdlc-orchestration Implementation phase.
---

# Test Strategy

Decide **what to test, at which level, and in what order of priority** — the quality-architecture layer above the moment-to-moment discipline of [[tdd]]. [[tdd]] is the inner loop (write a failing test, make it pass, refactor); **test-strategy** is the outer plan (risk, levels, coverage, regression, gates). Adapted from the BMAD **Test Architect (TEA)** module and risk-based testing practice.

Sits in the Implementation phase of [[sdlc-orchestration]]; consumes acceptance criteria from [[requirements-engineering]] / [[spec-driven-development]].

## Risk-based prioritization (P0–P3)

You cannot test everything equally; prioritize by **risk = impact × likelihood**:

- **P0** — critical paths, money/data-loss/security/safety; a failure here is unacceptable. Must have thorough automated coverage; blocks release.
- **P1** — core features, common flows; high coverage.
- **P2** — secondary features, less-common paths; moderate coverage.
- **P3** — cosmetic/edge, rare; minimal or manual.

Drive the priority from the **architecture characteristics** ([[software-architecture]]) and the **functional requirements** ([[requirements-engineering]]): the higher a requirement's criticality, the higher its tests' priority. Spend the test budget where the risk is.

## Test levels (the pyramid)

Put each test at the **lowest level that can catch the bug** — cheaper, faster, less flaky:

- **Unit** — pure logic, one component, no I/O. The broad base. Fast, deterministic. (Where [[tdd]] mostly lives; trivial for the pure core of [[functional-programming]].)
- **Integration** — components + real collaborators (DB, queue) at a boundary.
- **Contract** — the agreement between services/consumers (critical for microservices/distributed [[software-architecture]]).
- **End-to-end (e2e)** — full system through the UI/API. The thin top: high value, high cost/flakiness — reserve for critical journeys.

Anti-shape: the **ice-cream cone** (mostly slow e2e, few unit) — slow, brittle, expensive. Aim for a pyramid.

## ATDD — acceptance criteria become tests

Acceptance-Test-Driven Development closes the loop with [[requirements-engineering]]: each story's **acceptance criteria** (Given/When/Then) become **automated acceptance tests** written *before* implementation, agreed in the "three amigos" (PO + dev + QA). A story is done when its acceptance tests pass — making "done" objective.

## Traceability

Maintain a **requirements → tests** map: every P0/P1 requirement (`FR-N`/`CAP-N`) has at least one test that references it, and every test traces back to a requirement. This proves coverage of *what matters* (not just line coverage) and surfaces untested critical requirements and orphan tests. It's the bridge from [[requirements-engineering]]'s stable IDs to the suite.

## Regression-suite design (proactive)

Build the regression suite **before** testing begins and **as requirements evolve**, not reactively by recording sessions. For each requirement/story, design cases that protect the behavior going forward. A regression test case carries: **ID, title, preconditions, steps, test data, expected result, priority, traces-to (FR/AC)**. Keep the suite curated — prune obsolete cases, keep it fast enough to run in CI.

## What to automate (and what not)

Automate: P0/P1 paths, anything run repeatedly, deterministic checks, contract tests. Don't over-automate: rarely-changing P3 cosmetics, one-off exploratory checks, things cheaper to verify by eye. Exploratory/manual testing still has a place for usability and discovering the unknown.

## Flakiness & self-healing

Flaky tests destroy trust in the suite — quarantine and fix them (usually timing/order/shared-state). Modern tooling offers **self-healing** selectors and AI-assisted maintenance for UI tests; useful, but treat them as aids, not a license for brittle e2e. Prefer stability at lower levels over heroics at the top.

## Execution-grounded gates (the non-negotiable)

A quality gate must **run the tests and measure real coverage** — never an LLM's *opinion* that the code "looks tested." This is the explicit fix for the source frameworks' weakness ([[sdlc-orchestration]]): the qa/checker step executes the suite, reports pass/fail and coverage against the P0/P1 traceability map, and blocks on real failures. "Looks correct" is not a gate; a green run is.

## Anti-patterns

- Flat coverage targets ("80% everywhere") instead of risk-weighted depth.
- Ice-cream-cone suites (mostly e2e); over-reliance on slow, flaky end-to-end tests.
- Tests with no traceability — can't tell if critical requirements are covered.
- Reactive, record-and-playback regression suites that rot.
- **Judging quality by reading code instead of running tests** (the cardinal sin).
- Chasing line coverage as the goal rather than risk coverage.
- Ignoring flaky tests until the team stops trusting CI.

## Always-apply

1. Prioritize by **risk (P0–P3)**, driven by requirement criticality and architecture characteristics.
2. Put each test at the **lowest sufficient level**; aim for a **pyramid**.
3. Turn **acceptance criteria into automated tests (ATDD)**; maintain **requirements→test traceability**.
4. Design the **regression suite proactively**; keep it fast and curated.
5. **Gate on real execution + coverage**, never on judgment.

## Related

- [[tdd]] — the inner red-green-refactor loop this strategy frames.
- [[requirements-engineering]] / [[spec-driven-development]] — acceptance criteria and IDs that become tests.
- [[software-architecture]] — characteristics that set test priorities; contract tests for distributed styles.
- [[functional-programming]] — pure/total functions make the unit base trivial to test.
- [[github-actions]] / [[devops]] — running the gates in CI; DORA quality signals.
- [[sdlc-orchestration]] — the Implementation-phase QA step this owns.
- Source: BMAD Test Architect (TEA) module (MIT); risk-based testing / ISTQB practice.
