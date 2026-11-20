# delivery-flow: running status

Short, current, and overwritten each session. The full picture is in
`docs/delivery-flow-handoff.md`; what comes *after* the submission is in
`docs/delivery-flow-next-workflows.md`.

Last updated 2026-11-20.

## Can we submit?

**No. Two things, and only one of them is work.**

1. **`pr-description` fails its gate**, so `package-evidence.py` stamps DRAFT instead of
   building. Needs three v7 eval runs — model calls, currently unauthenticated.
2. **Criterion 4 is `n = 0`.** Needs real `triage` runs. Calendar time, not engineering.

Everything else is evidenced. `package-evidence.py --dry-run --allow-uncertified` builds all
five directories with no `MISSING.md`:

```
1-workflow-definition   16 files      4-end-to-end-rate    2 files
2-guardrails             5 files      5-audit-trail        3 files
3-punch-out-evidence     6 files
runs collected          84 (7 completed, 28 discarded)
```

## The five criteria

| Criterion | State |
|---|---|
| Workflow definition | Evidenced |
| Guardrails | Evidenced |
| Punch-out evidence | Evidenced — incl. bypass reports for both workflows |
| **End-to-end success rate** | **`n = 0`. The blocker.** |
| Audit trail | Evidenced |

Certification gate: `triage` 38/40, `breakdown` 24/24, `challenge-breakdown` 107/108 all PASS
with three consecutive runs each. `pr-description` **FAIL** — the live prompt is v6, the
registry pins v5.

## Fixed today

- **Plugin cache was five versions stale: 0.16.0 against main's 0.21.0.** This is the cause of
  the unusable runs below, and the exact trap the previous version of this file warned about.
  Updated to 0.21.0. **A session restart is required for it to take effect.**
- **`delivery-report.py` reported `Certified: yes` for runs it had read zero step records
  from** — `certified_all` started True and only an explicit `certified: false` moved it. Five
  live items were in that state. Four sit one deterministic `report` step from terminal, so
  closing them out would have put five unmeasured runs into the Stage 4 numerator. Now
  `unknown`, excluded from the certified rate, still counted in the all-runs rate. PR #136.
- **`nx-neptune` flipped to `profile: triage`.** `full` adds four `allow_uncertified` steps and
  can never contribute to criterion 4.
- **pr-description v7 built**: a `# Length` section plus `brevity` as a fifth criterion, assert
  mutation-tested 9/9, load-bearing 29/29. PR #135. Not certified — no runs yet.

## Why criterion 4 is zero, precisely

Two independent causes, both now understood:

- **7 of 8 items never terminated** — no `outcome.json`, so they are in-flight and excluded. A
  rate counts terminal runs only; in-flight is not failure, it just is not evidence.
- **The one that did terminate is disqualified.** `AN-3702`'s `outcome.json` says
  `profile: triage` while its trace contains `propose`, `implementation`, `verify`,
  `challenge-implementation`, `open-pr` and `post-summary` — all `full`-only steps, three of
  them uncertified nodes.

And the five items with no step records (`AN-3664`, `AN-3667`, `AN-3668`, `AN-3669`, `AN-3703`)
carry `check-edge` records only. No model, no cost, no certification was recorded for any step,
because the plugin cache was stale. **They cannot contribute to criterion 4 or 5 and should be
treated as discarded**, like `AN-3630` and `AN-3704`.

Note for a reviewer: `outcome.json` records the *configured* profile, not what actually ran, so
a reader of that file alone would believe `AN-3702` was a triage run. Worth its own fix.

## The order that gets this submitted

1. Restart the session so the 0.21.0 plugin loads. Without this, new runs do not record steps.
2. Authenticate the model provider. It accepts `ANTHROPIC_API_KEY`, `CLAUDE_CODE_USE_BEDROCK`
   or `CLAUDE_CODE_USE_VERTEX` — nothing else, and the eval fails before the first case
   without one.
3. Three v7 runs. Watch `coverage` on the six-file cases (`case-06`, `case-07`): brevity and
   coverage are the one pair in this suite that trade against each other. **If coverage drops,
   the cap is wrong, not the model.**
4. Repoint `steps.yaml` to v7 — sha, `certified_version`, `results`, `consecutive_runs`,
   `criteria` += `brevity` — and copy `prompt_v7.md` to `skills/pr-description/SKILL.md` in the
   same commit.
5. Merge PR #135 and PR #136.
6. Accumulate `triage` runs until the certified-only rate means something. This is the long
   pole and nothing shortens it.

## The pattern worth putting in the report

Three defects this fortnight were the same shape: **a checker that is present, successful, and
checking nothing.** `enforce-punch-outs.py` recognised an sdlc repo then looked for its
artifacts in `delivery/`. `check-protected-paths.py` matched `protected_paths:` only at column
zero. `delivery-report.py` certified runs it had read no steps from. Each was caught by a
refuse-to-pass-by-absence rule rather than by review, which is the argument for writing those
rules in the first place.
