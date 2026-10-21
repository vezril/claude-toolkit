# The roster: kinds of work → specialists

A story says which kinds of work it touches; `roster.yaml` says who handles each kind. The
lookup is a script, not a judgement call, so the same story always dispatches the same way.

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

## How a story is dispatched

`resolve-roster.py <story>` returns the union of skills, the de-duplicated reviewers, and
one architect per kind of work touched. The **same test-writer and implementer pair builds
every story**, loaded with those skills. There is no `implementer-ux`: specialisation lives
in the architects and reviewers, and the dev pair's file boundary is enforced mechanically
by a hook that would have to be duplicated for every variant.

Repos override a kind of work wholesale in `.delivery-flow.yaml`. An override replaces the
entry; it does not merge into it, so what you write is what dispatches.
