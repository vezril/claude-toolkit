# Load-bearing map: wizard (v4)

The certified `skills/wizard/SKILL.md` is upstream plus one sentence (marked **added**); `template.sh`
differs from upstream at line 114.
Each instruction, the criterion it serves, and what the runs show. "Guard": no run of any version
failed it, so the evidence shows a regression would be caught, not that the instruction caused anything.

| Instruction | Criterion | Evidence |
|---|---|---|
| Description: "Don't invoke this for steps the agent can perform itself" | scope | v1 → v2: 0/3 → 3/3 on both models (v1 wrote a wizard for a `cp .env.example .env` job every time) |
| The template library: stages, `ask_secret`, `write_env`, `set_secret`/`set_var`, `confirm` | hidden, coverage, runs | Haiku v1 → v2: hidden 1/3 → 3/3, coverage 1/3 → 3/3, runs 3/6 → 6/6 (its v1 helpers dropped secrets via a shadowed `local`). Sonnet passed these unprompted in v1, so for Sonnet they're guards |
| Never hand-edit the library above the marker | valid | v2: every script copied it, which is why the template's own shellcheck error failed **valid** 6/6; v3's one-line template fix → 6/6 (Sonnet), 5/6 (Haiku, the miss is a second bash block) |
| Step 1: read the repo first (`.env*`, workflows' `secrets.*`/`vars.*`); confirm the stages | coverage | Haiku v1 asked the user to type the migration command and table name the README gives. "Confirm with the user" is **not measured** (single-turn eval) |
| **added** for a migration, the repo's scripts/README/runbooks name the command and objects; never ask for what the repo states | runs, gate | v3 → v4 on Haiku: 45/48 → 46/48 over two samples; the v3 s2 miss (an invented `recipes_legacy` and a demanded `MIGRATE_CMD`) didn't recur. Sonnet 48/48 both ways, a guard there |
| Step 2: never invent UI steps you don't know | (none) | **not measured** |
| Step 3: `confirm` before any irreversible action; open the URL before asking for its value | gate | Haiku v1 gate 0/3 → v2 3/3. Sonnet v1 already gated (3/3), a guard there |
| Step 4: `bash -n`, shellcheck, `chmod +x`, trace statically, don't run it | valid | the eval agent has no Bash, so the step can't run here; **valid** grades its outcome |
