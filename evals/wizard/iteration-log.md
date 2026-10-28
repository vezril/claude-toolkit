# Iteration log: wizard

Written as the runs happened. Predictions are recorded before the run they predict.

## Found while calibrating, before any model ran

The upstream `template.sh` fails `shellcheck -S error` on its own line 114
(`p+="$s$DIM$e[Enter keeps current]..."`, SC1087: shellcheck reads `$e[` as an array index). It's a
false positive and the line works, but the skill's own step 4 says to run shellcheck, and the
**valid** criterion does. So every wizard that copies the library verbatim, as the skill insists,
fails valid. v2 keeps the template verbatim so this shows up as a measured failure, not a silent fix.

## Prediction for v1 (one-liner) and v2 (upstream verbatim), written before either ran

v1 ("write an interactive bash script") will write something that runs, so **runs** should mostly
pass, but I expect it to read secrets with plain `read -p` (**hidden** fails), to miss either the
GitHub variable or one secret (**coverage**), and to write a wizard for z-03 anyway (**scope**),
because nothing in it says when not to. **gate** is a coin toss: a "drops the legacy table" request
invites a confirm on its own.

v2 should flip **hidden** (ask_secret), **coverage** (it reads `secrets.*`/`vars.*` from the
workflow), and **gate** (confirm before irreversible actions). It should fail **valid** on every case
that copies the library, because of the template's shellcheck error. **scope** depends on whether the
model honours the description's "don't invoke this for steps the agent can perform itself" when the
skill has already been loaded for it.

## v1 and v2 measured, and the harness I had to rebuild to measure them

| run | sonnet | haiku |
|---|---|---|
| v1 | 21/24 (88%) | 11/24 (46%) |
| v2 | 18/24 (75%) | 18/24 (75%) |

These numbers come from the third version of the run harness. The first two misgraded good scripts,
which I only found by reading them:

1. **Every prompt answered "y" (spawnSync, piped stdin).** Good cutover scripts validate their input:
   a row count must be a number, a backup branch name can't be "y". They aborted, correctly, and
   scored as failures. And `read -p` prints no prompt when stdin isn't a terminal, so a smarter
   answerer couldn't even see what was asked. Replaced with `drive.py`: the script runs in a
   pseudo-terminal, each prompt is read when the script goes quiet, and answered the way a person
   would: yes/no gets y (or n), a count gets 42, a typed confirmation ("Type DROP to proceed") gets
   the word, an offered default ("[example/pantry]") gets Enter, anything else gets a unique token.
   Because the terminal echoes typed input unless the read is silent, **hidden** stopped being a
   static guess at which line captures a secret (the first version misread lowercase variables and
   helper functions) and became an observation: the secret's token must not appear in the transcript.
2. **The environment was thinner than a real checkout.** No git remote (one script stopped on "could
   not determine the GitHub repo"), no `.env` for the cutover, and a `pg_dump` stub that wrote an empty
   dump, which careful scripts check for. The repo copy is now a git checkout with a GitHub remote, the
   cutover case gets the `.env` the README describes, and the `pg_dump` stub writes a small dump.
3. **gate counted only the Neon console page as a backup.** A pg_dump taken first, or a Neon branch
   the human creates and names on screen before the migration, is just as much a backup. Widened.

All calibration replies agree (31/31) and both runs were regraded with `rescore.js --write`.

What's real in v1: Sonnet's scripts are good except that it wrote a wizard for z-03 every time (a
.env that needs nothing but `cp .env.example .env`). Haiku's scripts ignore the repo on the cutover
(asking the human to type the migration command and table name that README and `scripts/` already
give, then stopping on its own checks), and one setup script has a real bug: its `ask` helper declares
`local value`, shadowing the caller's variable, so every secret it reads is silently dropped.

Against my prediction: v1 Sonnet did *not* fail **hidden** or **coverage**; it reads the workflow and
uses `read -s` unprompted. **scope** failed on both, as predicted. v2 passed everything except
**valid**, which it failed 6/6 on both models for the reason found while calibrating: the template's
line-114 shellcheck error. So the upstream skill's only measured defect is in its own template.

## v3: fix the template's shellcheck error (one concern)

Hypothesis: brace the one expansion (`${e}[Enter keeps current]`), and **valid** goes 0/6 → 6/6 on
both models with nothing else moving, because v2 scripts copy the library verbatim. SKILL.md is
unchanged; only `template.sh` line 114 differs.

## v3 measured

| run | sonnet | haiku |
|---|---|---|
| v3 | 24/24 (100%) | 23/24 (96%) |
| v3 s2 | 24/24 (100%) | 22/24 (92%) |

**valid** flipped as predicted: 6/6 on Sonnet in both samples, 6/6 and 5/6 on Haiku (the one miss is
a second bash block for `chmod +x`, which the request asked it not to add). Nothing else moved on
Sonnet. (Driver fix found here: a prompt for a Postgres connection string got a bare token and the
script rightly rejected it; drive.py now answers those with a Postgres URL. Every version regraded.)

Haiku over two samples is 45/48 (93.8%), under the bar, and its two non-format misses are the same
failure: on the cutover it doesn't read the repo. In s2 it invented a `recipes_legacy` table and
stopped at preflight demanding a `MIGRATE_CMD`, although the README names `recipes_v1` and
`scripts/migrate.sh --drop-legacy`. Step 1 does say "read the repo first, don't ask cold", but its list
of what to read is the setup list (`.env*`, workflows); for a migration it names concepts (current
state, target state) and no files.

## v4: for a migration, read the repo's own scripts and runbooks (one concern)

Hypothesis: extending the migration bullet with where those facts live (the repo's scripts, README,
runbooks) and "never ask the human for something the repo already states" should flip Haiku's
**runs**/**gate** misses on z-02 and leave Sonnet at 24/24.

## v4 measured, and two more driver fixes

| run | sonnet | haiku |
|---|---|---|
| v4 | 24/24 (100%) | 22/24 (92%) |
| v4 s2 | 24/24 (100%) | 24/24 (100%) |

Two driver fixes, both found reading v4 transcripts, both regraded across every run (calibration
still 31/31): a typed confirmation phrased "type the table name exactly: recipes_v1" or "Type drop
recipes_v1 to proceed" (no quotes, lowercase) got a token instead of the word; and a script that
prints its instruction on one line and then prompts with a bare `? ` was answered from the bare line.
After the fixes, the v4 s2 Haiku cutover that had scored as a failure runs clean.

v4's one remaining Haiku miss (s1) is a real one: the cutover script stops with "DATABASE_URL is not
set in this shell. Export the Neon connection string, then re-run" instead of asking for it. That is
the "don't ask cold" rule's mirror image, a wizard that sends the human away to do its job; I'm not
iterating on it.

## Progression (all regraded with the final driver)

| run | sonnet | haiku |
|---|---|---|
| v1 one-liner | 21/24 (88%) | 11/24 (46%) |
| v2 upstream verbatim | 18/24 (75%) | 18/24 (75%) |
| v3 template line 114 fixed | 24/24, 24/24 | 23/24, 22/24 → 45/48 (94%) |
| v4 + read the repo for a migration | 24/24, 24/24 | 22/24, 24/24 → 46/48 (96%) |

## Certification

v4 is certified on **Haiku**, 46/48 (95.8%) over two samples, which clears the 95% bar by one check;
Sonnet is 48/48. The v3 → v4 gain on Haiku is a single check, within the sample-to-sample spread I've
seen, so I'd call v4's sentence plausible, not proven: what's measured is that it didn't hurt and the
specific failure it targets didn't recur. Not measured: "confirm the stages with the user", "never
invent UI steps", and the skill's own step 4 (bash -n, shellcheck), which the eval agent has no Bash
to run.
