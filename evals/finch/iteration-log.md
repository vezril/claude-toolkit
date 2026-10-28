# finch skill — EDD iteration log

Every number here comes from a results file in `results/`. Nothing is from memory.

Model under test: `sonnet` via `provider/claude.sh`.

## Headline — N=3 per case, majority scoring

A case counts as passing when it passes in at least 2 of 3 runs, matching the repo
README's EDD convention.

| Arm | Run 1 | Run 2 | Run 3 | **Majority** | Results files |
|---|---|---|---|---|---|
| naive baseline, no skill | 6/16 | 8/16 | 6/16 | **7/16 (43.8%)** | `n3_baseline_run{1,2,3}.json` |
| with `SKILL.md` | 16/16 | 16/16 | 16/16 | **16/16 (100%)** | `n3_skill_run{1,2,3}.json` |

The skill arm is stable: 48 of 48 case-runs passed, every case PPP. The baseline arm is not,
and that instability is the main thing N=3 bought.

**The skill never failed a case, so there is no Red→Green story about the skill.** It was
16/16 on its first run and stayed there across six runs total. The iteration in this log is
iteration on the *measurement*. The honest summary is that EDD here bought a better suite and
a much more honest baseline, not a better skill.

## Per-case, baseline arm (P = pass, F = fail, in run order)

| Case | Runs | Majority |
|---|---|---|
| case-01-socket | PPP | pass |
| case-02-restart | PPP | pass |
| case-03-additional-dirs | PPP | pass |
| case-04-readonly-home | FFF | **fail** |
| case-05-shrink-disk | FPF | **fail** (unstable) |
| case-06-rosetta | FFF | **fail** |
| case-07-soci | FFF | **fail** |
| case-08-keyless | FFF | **fail** |
| case-09-tls-proxy | PPF | pass (unstable) |
| case-10-linux-root | PPP | pass |
| case-11-containerfile | FFF | **fail** |
| case-12-help-hangs | FPP | pass (unstable) |
| case-13-devcontainers | FFF | **fail** |
| case-14-ecr-helper | FFF | **fail** |
| case-15-isolation | FFF | **fail** |
| case-16-multiarch | PPP | pass |

## What N=3 corrected

Earlier in this work I ran each arm once and concluded the baseline "already knew" five
things I had assumed were obscure: the `- path:` map schema, grow-only disks plus `fstrim`,
SOCI's index and silent fallback, the in-VM CA trust store, and why `finch build --help`
boots the VM. **Three of those five were artifacts of a single lucky sample.**

- `case-03` (the `additional_directories: [- path: …]` schema) is real: PPP. Sonnet knows it
  cold, including the warning that editing `finch.yaml` while the VM runs changes nothing.
  The skill genuinely earns no credit here.
- `case-09` (in-VM CA trust) and `case-12` (`--help` booting the VM) are PPF and FPP — the
  model gets there about two times in three. Partial knowledge, not reliable knowledge.
- `case-05` (shrinking the datadisk) is FPF and `case-07` (SOCI) is FFF. Both **fail** by
  majority. My single-run claim that these were base-strong was simply wrong, and the
  N=1 number had flattered the model.

Eight cases fail the baseline in all three runs: **04, 06, 07, 08, 11, 13, 14, 15** — the
read-only home mount, Rosetta's macOS-26 floor, SOCI, cosign-keyless-unsupported,
Containerfile auto-detection, DevContainers wiring, the ECR `creds_helpers` + `credsStore`
pair, and refusing the "the VM gives us isolation" premise. That set is the skill's reliably
measured value.

## Before any scoring: two harness failures

**The repo's standard provider does not work on this machine.** Every other suite in `evals/`
uses `anthropic:claude-agent-sdk`. That provider spawns the claude-code binary directly, and
on this Bedrock-backed install the subprocess inherits no AWS credentials: all cases error
with `Could not load AWS credentials`. It burned 7m14s before failing. `aws sts
get-caller-identity` fails in a plain shell here too, so this is the environment, not promptfoo.
Replaced with an `exec:` provider shelling out to the `claude` CLI, which uses whatever auth
that CLI already has.

Consequence worth noting: an `exec` provider returns plain text, which makes a flaky
`llm-rubric` grader. The two restraint cases were drafted as rubrics and were rewritten to
assert on the specific claim the answer must contain. The suite now has **no LLM judge at
all** — no grader drift between iterations, and a re-run costs only generation.

**`exec:` paths resolve relative to the config file, not the cwd.** `exec:./evals/finch/provider/claude.sh`
gave `spawn ENOENT`; `exec:./provider/claude.sh` works.

## Assert calibration, before the baseline was locked

First trial case (case-01, Testcontainers and the Docker socket) scored FAIL on an answer that
was substantively correct: it said "Probably not as-is… There's no `/var/run/docker.sock`".
My assert looked for `doesn't expose` and the model wrote `doesn't run dockerd or expose`.
Per `evals/README.md`'s own rule — a test that breaks when the model rewords is the thing
that's wrong — the negative-verdict vocabulary was broadened before any score was recorded.

Three other asserts were tightened in the same pass, for the opposite reason:

- case-06 accepted a bare `false` anywhere in the output. Narrowed to `rosetta: false` / `unset` / `qemu`.
- case-07 accepted the word `push` anywhere. Narrowed to the actual claim, that the index is built *at push time*.
- case-11 accepted `works` / `yes`. The request itself contains the word "Containerfile", so
  echoing it proved nothing; now the discriminating claim is that Finch picks it up with **no flag**.

All of this happened before any recorded score.

## Suite v1 → v2: a criterion the first suite was blind to

Suite v1 (16 asserts) scored, at N=1, baseline 9/16 and skill 16/16. Reading those baseline
transcripts turned up a failure mode the asserts could not see: the baseline named the right
mechanism while handing out commands that **do not exist**.

- `finch vm ssh -- sudo fstrim -av` (there is no `finch vm ssh`)
- `finch soci create` / `finch soci push` (hedged as "if your Finch version has them" — it doesn't)
- `limactl disk create finch`

A confidently wrong command scored identically to a correct one. For a CLI skill that is the
failure that actually costs someone an afternoon, so it became its own criterion:
`asserts/no-invented-commands.js`, checking every `finch` invocation in fenced or backticked
code against the verbatim command list from `finch --help` on v1.19.0. Applied to every case
in **both** arms, and both arms re-run, because changing an assert invalidates comparison
against the old numbers.

At N=1 the new criterion scored baseline 15/16 and skill 16/16, and dropped the baseline total
from 9/16 to 8/16 — the suite getting sharper, not the model getting worse. It is also what
makes `case-07` fail outright at N=3: the baseline reliably reaches for SOCI's index concept
and reliably invents a command to build it.

**The assert's first version was buggy in the dangerous direction.** Its separator was `\s`,
which crosses newlines, and it treated `finch` appearing as an *argument* as an invocation. So
`limactl shell finch` followed by `sudo fstrim` on the next line parsed as a call to
`finch sudo` — it flagged a correct snippet copied straight out of `SKILL.md`, and would have
scored the skill down for being right. Fixed by matching per line and requiring `finch` to be
in command position (line start, after a pipe or separator, or behind `sudo`/an env prefix).
It now has `asserts/no-invented-commands.test.js`, 11 checks, because an assert with a bug
corrupts every score it ever produces, silently and in the flattering direction.

## Limits

- **The with-skill arm has no headroom.** 16/16 on all three runs. The suite can catch a
  regression; it cannot show further improvement, and it is not evidence the skill is good —
  only that the rails I thought to test survived.
- **Three baseline cases are genuinely unstable** (05, 09, 12). Majority scoring hides that;
  the per-case table above is the honest view. A 43.8% headline has a real spread behind it.
- Loading `SKILL.md` as prompt context is a proxy for how Claude Code injects a skill, not a
  replica. The suite also says nothing about whether the skill *triggers*, which is a property
  of the `description:` field.
- Tools are disabled in the provider. Necessary — a baseline-arm model with `Read` could pull
  `skills/finch/SKILL.md` off disk and contaminate the comparison — but it means neither arm
  was able to check anything against a real Finch install.
- Earlier N=1 runs are kept in `results/` (`baseline_v0.json`, `skill_v1.json`,
  `*_suite2.json`) as the record of the suite-v1 → suite-v2 progression. The headline numbers
  are the `n3_*` files.

## Reproducing

```bash
node evals/finch/asserts/no-invented-commands.test.js
for n in 1 2 3; do
  npx promptfoo@latest eval -c evals/finch/promptfooconfig.baseline.yaml --no-cache \
    -o evals/finch/results/n3_baseline_run$n.json
  npx promptfoo@latest eval -c evals/finch/promptfooconfig.yaml --no-cache \
    -o evals/finch/results/n3_skill_run$n.json
done
```
