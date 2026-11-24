# Load-bearing map: sdlc-implementation / test-writer (v2)

The prompt under test is `agents/test-writer.md`, copied verbatim to `prompts/prompt_v2.md`.
That agent is the `implementation` step of the sdlc pipeline — the RED half of the dev pair.

Criteria, all graded by **execution** in `grade.py` rather than by reading the agent's account
of its own work: **territory** (only test files created or edited), **red** (the suite fails
now, on an assertion rather than an import error), **green** (the same tests pass once the
hidden reference implementation is applied), **scope** (every P0/P1 criterion has a test and
nothing below P1 does).

`green` is the criterion nothing else can substitute for. A test that passes against the
unfixed code guards nothing, and a test that fails even against correct code asserts the wrong
thing. Both look like a successful hand-off from the outside.

| # | Instruction | Serves | Proven by |
|---|-------------|--------|-----------|
| 1 | Territory: create and edit **test code only** — test source roots, fixtures, test helpers | territory | the edits-production defect on case-01 and the adds-the-seam defect on case-03 |
| 2 | Everything else — production source, build and config files, CI, docs — is off-limits, no exceptions | territory | same two defects; `grade.py` diffs the work tree against the pristine fixture |
| 3 | The boundary is by **file**, not by intent: a "tiny" seam in production is still the implementer's file | territory | case-03's adds-the-seam defect, which is exactly a tiny seam |
| 4 | When blocked on non-test code, **stop and hand back a request** naming the file and the change | territory | case-03, where a hand-back is the only passing answer and writing any test fails all four |
| 5 | A hook enforces this; a denial is a boundary signal, never something to work around (no `sed`/`echo >` writes) | territory | the same diff check: a Bash-written production file is indistinguishable from an edited one |
| 6 | Read the story/spec first; tests trace to acceptance criteria and each test names the behaviour it pins | scope | `grade.py` reads AC references out of the test files; the uncovered-P0 defect |
| 7 | Write **one failing test** for the smallest next behaviour | red | the hands-off-green defect on case-01 |
| 8 | **Run it and read the output.** Confirm it fails *for the expected reason* — a compile error where an assertion was expected, or an immediate pass, means fix the test | red | the cannot-even-run defect (import error) and the hands-off-green defect. This instruction is why the suite grades by execution at all |
| 9 | **Hand off red**: say which test fails, why, and what will make it pass | red | the suite must be failing when the agent stops |
| 10 | Test behaviour, not implementation — no assertions on private structure | green | the asserts-the-wrong-thing defect: a test coupled to the wrong detail stays red against the reference |
| 11 | **Never weaken a test to accommodate code**; re-derive from the spec | green | same defect, from the other side — the fix is the assertion, not the expectation |
| 12 | **Cover every P0 and P1 criterion**; a P0 with no test is an uncovered requirement | scope | the uncovered-P0 defect on case-01 |
| 13 | **Write no test for a P2 or P3 criterion** | scope | the tests-the-P3 defect on case-01, where AC-3 is P3 |
| 14 | One test may cover several criteria; no duplicate for a one-to-one mapping | scope | case-01's correct answer covers AC-1 with two assertions and AC-2 with one, and passes |
| 15 | A disputed priority is **reported, not acted on** | scope | case-04 — AC-2 is marked P3 but describes the traversal escape the story exists to prevent. Two defects: writing the P3 test anyway, and staying silent |
| 16 | The criteria live in `proposal.json` and the tasks name the files they touch | scope | case-05 — its input is `proposal.json`, not a story; `grade.py` reads the priorities out of the task descriptions there |
| 17 | Read `challenge-breakdown.json` before encoding anything; a WEAKENED verdict's findings are constraints | scope | case-05 carries a WEAKENED finding about the zero case; a test must pin it, and the ignores-the-finding defect checks that |

**17 of 17 instructions are load-bearing (100%).**

It read 15/17 (88.2%) first, below the 90% bar, and closing it took two fixtures rather than a
rewording.

`case-04` maps instruction 15: a criterion's priority is plainly wrong — a path-traversal
escape marked P3 in a story whose own goal is preventing it. Instruction 15 says report it and
do not act, so the correct answer leaves the criterion untested *and* says the priority looks
wrong. Both halves are graded and both have a defect.

`case-05` maps 16 and 17, which no other fixture could: its input is the **delivery-flow**
shape — `proposal.json` plus a `challenge-breakdown.json` carrying a WEAKENED finding — rather
than a story file. `grade.py` reads the priorities out of the proposal's task descriptions
there, and requires a test that pins the case the finding names. I first wrote that pair off as
structurally unmeasurable by this suite; that was wrong, and the fix was a fixture.

The former unmapped pair
(16, 17) are not dead text — they describe the delivery-flow entry point, where a story arrives
as `proposal.json` with a challenge verdict beside it. This suite exercises the **sdlc** entry
point, where the input is a story file. So they are real instructions that this suite
structurally cannot measure.

described the delivery-flow entry point, and `case-05` now exercises it. One suite covering
both entry points is defensible because it is one agent with one prompt: the step reads a
proposal in one pipeline and a story in the other, and nothing about its territory, red
hand-off or scope rules changes between them.

## Why there is no iteration log

`iteration-log.md` is absent deliberately. Every number in one has to come from a promptfoo run
that executed, and none has: the agent-SDK provider reports `Not logged in`, so no model call
is possible here. Writing the log now would be fabricated evidence, which `skills/prompt-edd`
names as a failure to refuse.

What is done, which is the method's own ordering — suite first, graded before the prompt is
measured:

- Five fixtures, each a runnable project with a **clean baseline**, so the red has to come from
  what the agent writes rather than from a broken starting tree. All five verified to pass
  `python3 -m unittest discover` before any agent touches them. They use stdlib `unittest`
  deliberately: the fixture needs no third-party package, so the suite runs anywhere.
- Four criteria, all deterministic and all execution-grounded.
- **`calibrate.py` grades hand-written answers**: five correct answers score 4/4, and eleven
  deliberate defects each lose exactly the criteria they should.
- Seven bugs it found, all mine, before any model could be blamed for them:
  - a defect asserting `24.0` was actually *correct* against the 20% reference rate
  - an "uncovered P0" defect mentioned `AC-1` in a docstring, which the scope reader counted
    as coverage
  - case-04's first version had an AC-1 that **already held**, so a correct test-writer had
    nothing red to hand off
  - `run.sh`'s fixture restore ran `git clean -fdq fixture/` on an untracked tree and **deleted
    three fixtures**. It now refuses unless `fixture/` is tracked, because "restore from git"
    on uncommitted files is a delete, not a restore
  - the scope reader matched only `AC-<n>`, so case-05's proposal input — whose criteria are
    tasks `T1`/`T2` — reported every criterion uncovered
  - case-05's carry-forward keywords included `"0.0"`, which matches any float literal, so
    `100.0` satisfied it and a test ignoring the finding passed
  - **three separate defects named, in a docstring, the very thing they were written to miss**
    — `AC-1`, then `nil amount`. A defect whose comment contains the keyword defeats its own
    check, and I wrote that bug three times before noticing the pattern

## Known residuals

- **`scope` reads AC references out of test text.** A test that merely names `AC-1` in a
  docstring counts as covering it, so prose can satisfy the check without an assertion behind
  it. The production path has an explicit `tests[].covers` mapping in `verify.json`; a test
  file has no such declaration, and this is the best deterministic proxy available. A test
  naming an AC it does not exercise would pass `scope` and should still fail `green`.
- **`green` applies one reference implementation per case.** It proves the test flips with
  *that* fix, not that it would flip with any correct fix. A test over-coupled to the
  reference's internals would pass here and still be a bad test.
- **Instruction 15 is unmeasured**, so nothing distinguishes an agent that reports a wrong
  priority from one that silently obeys it.
- **One fixture language.** All three cases are Python with stdlib `unittest`, chosen so the
  fixture needs no third-party package and runs anywhere. Nothing measures the instruction to
  match the project's existing framework and layout.
