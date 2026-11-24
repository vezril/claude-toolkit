# The roster: kinds of work → specialists

A story says which kinds of work it touches; `roster.yaml` says who handles each kind. The
lookup is a script, not a judgement call, so the same story always dispatches the same way.

The shipped roster is `templates/delivery-flow/roster.yaml`, parsed by `load_roster` in
`scripts/delivery-flow/common.py`. Every name in it resolves to a real agent in `agents/` or a
real skill in `skills/`, and `tests/delivery-flow/test_roster.py` fails if one stops doing so —
a name that does not exist is not a typo, it is a story that silently gets no reviewer.

```yaml
backend:
  architect: solution-architect
  skills: [scala, functional-programming]
  reviewers: [scala-fp-reviewer, clean-code-reviewer]
ux:
  architect: full-stack-architect
  skills: [react, nextjs, ux-design]
  reviewers: [frontend-reviewer]
infra:
  architect: solution-architect
  skills: [terraform, docker, github-actions]
  reviewers: [git-and-ci-reviewer]
  deploy: helm-deployer
```

The vocabulary is fixed: `ux`, `frontend`, `backend`, `contracts`, `infra`, `data`,
`mobile`, `docs`. A label outside it fails the resolve, which is the point — an invented
domain would dispatch to nobody.

`architect: null` is a kind of work that needs no architecture step — `docs` is the one. It is
written out rather than left absent, because an absent key reads as an omission and the resolve
treats it as one.

## How a story is dispatched

`resolve-roster.py <kind> [<kind> …]` (or `--from-proposal <path>`) returns the union of
skills, the de-duplicated reviewers, and one architect per kind of work touched. The **same
test-writer and implementer pair builds every story**, loaded with those skills. There is no
`implementer-ux`: specialisation lives in the architects and reviewers, and the dev pair's file
boundary is enforced mechanically by a hook that would have to be duplicated for every variant.

**Who dispatches the reviewers.** The `review` step, which runs after
`challenge-implementation` and before `pr-description`. It resolves the reviewers for the
story's work kind and fans out to each in its own fresh context.

This page described that resolve for a long time while **neither the script nor a consumer
existed** — `resolve-roster.py` was documented here and absent from `scripts/`, and no profile
step read `reviewers:` at all. The field was declared, documented and dispatched by nothing.
Both exist now; this note stays because a reader comparing an old run against this page would
otherwise conclude the reviewers had simply been skipped.

**A kind whose entry names no reviewer is an error**, not a kind that skips review — including
when a `roster_overrides:` entry drops the last one. The resolve refuses rather than returning
an empty list, because a silent skip makes the review step decorative: the run looks reviewed
and nobody read the diff.

Repos override a kind of work wholesale in `.delivery-flow.yaml`. An override replaces the
entry; it does not merge into it, so what you write is what dispatches.
