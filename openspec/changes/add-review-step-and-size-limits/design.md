# Design

## Context

The `full` profile's routing table already has every mechanism these three changes need, which
is why they belong in one change rather than three.

- `resolve-roster.py` already returns the de-duplicated reviewer union per work kind. Nothing
  calls it for review purposes; the data path exists and ends in nothing.
- `scripts/delivery-flow/triggers.py` is already the single home for *derived* punch-out
  triggers, imported by both `check-punch-out.py` and `hooks/check-edge.py`, precisely so a
  trigger cannot be computed two ways. Diff size is one more derivation in that file.
- `carry_forward` already exists for the breakdown challenge's `WEAKENED` findings, with the
  staleness rule that a verdict is about one version of its target.
- `allow_uncertified` already carries `propose`, `post-summary`, `vault-update`,
  `implementation` and `challenge-implementation` in the nx-neptune config, so a sixth entry
  changes no policy.

Two constraints shape everything below. First, the `full` profile's rate is **already not a
Stage 4 number** — it contains uncertified nodes by design — so adding an uncertified `review`
costs nothing that was being claimed. Second, the certified chain is the `triage` profile,
which none of this touches.

## Goals / Non-Goals

**Goals:**
- A diff is read by a specialist before it becomes a PR, and that reviewer's findings bind the
  PR description.
- A change that has outgrown one review stops and asks a human, measured from the diff.
- The dev pair's test scope is set by declared priority rather than by its own judgement.
- Every new control is derived or schema-checked, not an instruction a model may skip.

**Non-Goals:**
- **Certifying `review`.** It ships declared-uncertified. A prompt-edd package is a separate
  change, and pretending otherwise would put an uncertified node inside a certified claim.
- **Changing the `triage` profile.** The Stage 4 chain is untouched.
- **Automatically splitting an oversized change.** The flow raises the punch-out; a human
  decides. Splitting work is a scoping judgement.
- **Replacing `challenge-implementation`.** Both run.
- **A coverage-percentage gate.** Priority-scoped tests, not a coverage number.

## Decisions

### D1. `review` is one step that fans out, not one step per reviewer

A work kind can name two or three reviewers. Modelling each as its own profile step would make
the step list depend on the roster, and `tests/delivery-flow/test_profiles.py` asserts the
profile and the `STEPS` table agree — a roster edit would then break the step table. So
`review` is a single step that dispatches each roster reviewer in its own fresh context and
merges their findings into one `review.json`, which records per-reviewer attribution.

**Alternative rejected:** one step per reviewer, which makes the routing table a function of
configuration.

### D2. The reviewer is handed the diff, the story and `verify.json` — never `implementation.json`

The implementation record argues the change is correct. Handing it to a reviewer is how a
reviewer becomes a rubber stamp, which is the same reasoning the flow already applies to the
breakdown challenge. `verify.json` is included because a reviewer needs to know what the tests
actually did; it reports results rather than arguing for them.

### D3. The review verdict reuses the existing verdict vocabulary and routing

Rather than inventing a second verdict language, `review.json` carries the same
SURVIVED / WEAKENED / REFUTED shape the challenge artifacts use, and routes through the
existing harness in `scripts/workflow/verdict.py`. Its `weakened` policy is
`require-addressed`, matching the sdlc pipeline's choice rather than delivery-flow's default
`advance`, because these findings feed a PR someone will merge rather than a brief someone will
read.

**This is a declared policy, not a default.** The descriptor states it explicitly so that a
change to the substrate's default cannot move it silently.

### D4. Diff size is derived at `verify`, and the measurement is recorded

`verify` is the first point where the whole diff exists. The derivation reads the diff and
records the measured file and line counts next to the ceilings they were compared against, so
the punch-out's evidence is in the artifact rather than needing to be recomputed.

The derivation deliberately does not consult any node's `scope` or size claim. The existing
`scope` / `architecture` / `breaking` triggers already fire on a node's flag **or** on a
derivation that never reads it, and record `policy_disagreement` where they differ. Diff size
has no flag to disagree with — it is derivation only, which makes it the strongest of the
triggers.

### D5. Priorities live on the story's acceptance criteria, and verify checks both directions

The priority map is per acceptance criterion rather than per story, because a single story
routinely mixes a P0 behaviour with P2 polish. Verification checks that every P0/P1 criterion
has a test **and** that no test claims a criterion below P1.

The second direction is the one that matters for this change's purpose: a missing P0 test is a
coverage failure anyone would catch, while thirty tests for P3 criteria is the actual complaint
and nothing currently notices it.

### D6. `test-writer` reports a disputed priority rather than overriding it

If the test author believes a P2 criterion deserves a test, it raises a finding against the
priority map. Letting it widen its own scope would make the priority advisory, and the point of
D5 is that the scope is checkable data.

## Risks / Trade-offs

- **`review` is a sixth uncertified node in `full`.** The profile's rate was already outside
  any Stage 4 claim, so nothing measured degrades — but it does push the eventual certification
  work further out, and the honest statement is that `full` is further from a certified chain
  after this change, not closer.
- **A diff-size ceiling will fire on legitimately large changes.** A dependency bump that
  touches a lockfile, or a rename across a package, will breach a file ceiling while being
  trivial to review. Mitigation is that the punch-out is a question to a human, not a refusal,
  and the decision stays in the record. If it proves noisy the ceilings are config, not code.
- **Priority maps are only as good as whoever wrote them.** Moving the judgement from the dev
  pair to the story author does not remove it; it relocates it somewhere a reviewer can see it.
  That is the whole claim — it is a visibility improvement, not a correctness one.
- **P0/P1-only will reduce coverage, and that is intended.** If a regression later lands in a
  P2 path, this change is why. The trade is deliberate: smaller reviewable PRs against a
  thinner net.
- **One change touching ten files that `CLAUDE.md` pairs together.** Each pair is test-enforced,
  so the risk is a long red suite rather than a silent drift — but it does mean this change
  cannot land in pieces.
