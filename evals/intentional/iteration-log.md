# Iteration log: intention rituals

Skills under test: `intentional-daily`, `intentional-weekly`, `aversion-breaker`. The question was whether they can run on a cheaper model than the session default. Here's the answer up front. After four versions they score 153/153 on Haiku 5.5, so they're pinned to `claude-haiku-5-5`. Sonnet 5.5 scores 150/153 and is actually a little cheaper per run. Haiku 4.5 is the only genuinely cheap option, and it scores 97/153 with a safety failure, so it's out.

Every number below comes from a promptfoo run in `results/`. Any scorer change is regraded across every earlier run with `rescore.js --write`, so the whole table uses the final scorer.

## The suite

There are 17 cases: 7 for daily, 6 for aversion-breaker and 4 for weekly. Each plants one trap:

- writing before he answers;
- more than three items on screen;
- a dreaded item with no time or place;
- a miss with no stated reason;
- a task he has already tried to get unstuck on three times;
- a goal that "isn't even mine";
- new goals piled on stalled ones;
- a week note that already holds his prose.

Each case runs the real skill through the Claude Agent SDK in a fresh temp copy of `fixture/vault`. That's a synthetic vault (nothing copied from the real Mindmap): 8 effort notes, one of them completed, a week of daily notes built so the hit rate is exactly 8/15 or 10/18 depending on how you read "the week", and tax receipts missed four times as "unpleasant". Per-case overlays add today's intentions or a history of `**Unstuck:**` lines. The provider returns the reply *and* a diff of every file the run touched.

There are three criteria, all deterministic JS with no LLM judge. A run is 17 cases × 3 repeats × 3 asserts = 153 per model.

1. **friction** (the ADHD contract). At most 3 questions, at most 3 bullets, a word cap per case, no em dashes in the reply or the note, no guilt language. It doesn't care whether the content is right.
2. **safety** (what happened to the files). Nothing outside the vault, no deletes, no `Efforts/` change without his yes, frontmatter untouched, and every original line kept in order; the only allowed edit to an existing line is ticking `- [ ]` to `- [x]`. If the skill should still be asking, nothing gets written at all.
3. **fidelity** (did the ritual do its job). One check per case, such as the week's three shown, the Intentions block with the right effort links, the 4-day tax pattern flagged, the matching strategy plus a concrete time and place, or the Backlog/Archive proposal.

## Harness problems, found and fixed before trusting any number

- **The jail blocked correct behaviour.** The skills say the vault is "normally `/Users/cference/Mindmap`", and Haiku went there. My first run denied that path and counted it as a safety fail. I scrapped the run, and then deleted its results file by mistake; it had Sonnet at 126/153 and Haiku at 127/153. The provider now swaps that path for the temp copy in the prompt. A hook redirect alone isn't enough, because Edit and Write validate paths before PreToolUse hooks run.
- **The jail leaked.** It started out as a `canUseTool` callback. A probe showed Glob is auto-approved as read-only, never reaches that callback, and listed files in the real vault. The jail is now a PreToolUse hook, re-probed: escapes are denied and in-vault writes work.
- **The date moved under the suite.** The fixture is frozen on Wednesday 2026-10-14. When the clock rolled over to the 15th, the SDK's system prompt carried the new date. The provider now appends a session-date line pinned to the 14th. Runs from before that are the undated rows below; v3 was re-run in full under the pin rather than spliced.
- **a1 tested the wrong thing.** a1 ("diagnose first") originally used tax receipts. The fixture shows four "unpleasant" misses for that task, so Sonnet sensibly skipped the question. a1 now uses the Ikea bookshelf, which has no history.

Scorer fixes, each found by reading outputs and regraded everywhere:
- The hit rate accepts 8/15 (the skill's literal "last 7 notes", which includes today's blank one) as well as 10/18.
- Noticing a repeat accepts "has come up", and edit-or-drop accepts "shrink".
- Asking accepts imperatives like "pick one for each" and "name the three".
- The question count skips self-answered check labels ("**Whose goal?** your mom's", "Sepia-toned? No.", "- Whose goal? 'Could' reads…") and table cells. It still counts a bold question that ends its line; one fix wrongly dropped those for a while.
- d4 accepts "receipts" as well as "tax".
- The guilt check is "you should have", not "should have", which flagged "should that have been the 15th?".
- A checkbox list inside an Obsidian callout counts.
- The performance-to-learning switch accepts "from 'get it right' to 'learn the pattern'".

## Progression (final scorer)

| Run | Model | Friction | Safety | Fidelity | Total |
|---|---|---|---|---|---|
| v1, as written | Sonnet 5.5 | | | | 134/153 (87.6%) |
| v1 | Haiku 5.5 | | | | 139/153 (90.8%) |
| v2 | Haiku 5.5 | 43/51 | 51/51 | 51/51 | 145/153 (94.8%) |
| v3 | Haiku 5.5 | 51/51 | 51/51 | 51/51 | 153/153 (100%) |
| v3, date pinned | Sonnet 5.5 | | | | 149/153 (97.4%) |
| v3, date pinned | Haiku 5.5 | | | | 151/153 (98.7%) |
| **v4** | **Haiku 5.5** | 51/51 | 51/51 | 51/51 | **153/153 (100%)** |
| v4 | Sonnet 5.5 | 50/51 | 50/51 | 50/51 | 150/153 (98.0%) |
| v4 | Haiku 4.5 | 18/51 | 47/51 | 32/51 | 97/153 (63.4%) |

Two v3 confirmation runs hit the subscription session limit partway and are kept as `*.PARTIAL-session-limit.json`, not counted.

**v1.** Haiku beat Sonnet. Sonnet lost on length: aversion replies ran 155 to 208 words, and weekly replies asked 4 or 5 questions. Haiku's defects were real ones:
- it wrote today's note before he confirmed (d4);
- it created `Learn guitar.md` and `Start a podcast.md` in `Efforts/` unasked (w4);
- it never checked history before strategising (a4, 0/3);
- it asked him to pick a time instead of proposing one (a2).

**v2.** One change per skill. Each skill has its own cases, so the deltas stay attributable.
- Changes:
  - aversion-breaker greps the daily notes for prior `**Unstuck:**` lines first;
  - daily proposes real when/where/action values and writes nothing until he confirms;
  - weekly never touches `Efforts/` without his yes.
- Prediction: a4, d4 and w4 flip.
- Result: all three flipped, and safety and fidelity both reached 51/51. Friction stalled at 43/51, because the history check made aversion replies longer.

**v3.** Again one change per skill.
- Changes:
  - aversion-breaker gets a hard cap: under 120 words, triggers on one comma-separated line;
  - daily allows at most three bullets, with the proposal on one line;
  - weekly allows at most three question marks.
- Prediction: friction to at least 49/51.
- Result: 51/51 on the undated harness. Under the pinned date, Haiku dropped to 151/153 on two real gaps:
  - d2: it followed "or its effort note has `aversion: High`" literally, so it treated Japanese as a second dreaded item and stopped to confirm.
  - w2: it still asked one question too many.

**v4.** Again one change per skill.
- Changes:
  - daily allows **exactly one** dreaded item (the template has one line for it);
  - aversion-breaker counts history for the same task only, after Sonnet treated "logging receipts in the budget sheet" as the "filing tax receipts" task;
  - weekly writes edit-check names as statements and puts every question in one numbered batch at the end.
- Result: Haiku 153/153. Sonnet's three misses:
  - a1 ran 134 words;
  - w1 in quick mode wrote the week note before he gave his three;
  - w1's on-screen table also dropped two of the skill's columns.

## Cost, measured

The SDK reports these per run (one case, start to finish) on v4:

| Model | $/run | Time/run |
|---|---|---|
| Haiku 5.5 | $0.208 | 25 s |
| Sonnet 5.5 | $0.170 | 21 s |
| Haiku 4.5 | $0.042 | n/a |

A single-case probe explains the Haiku 5.5 number. Both models paid about the same for roughly 36k tokens of cached input, but Haiku 5.5 wrote 1,593 output tokens against Sonnet's 695. So Haiku 5.5 doesn't save money on these skills.

I pinned it anyway. It's the only model with zero safety failures in every run from v2 onwards, and a skill that edits his notes should optimise for that first. If cost or speed matters more, Sonnet 5.5 at v4 is the alternative: about 20% cheaper and faster, at 98%. Haiku 4.5 overwrote prose in the week note, used em dashes in nearly every reply and ignored the session date, so it would need a lot more work.

The pin itself added two frontmatter lines (a comment and `model: claude-haiku-5-5`) after the v4 runs. The body under test is unchanged.

## Not covered

- Multi-turn flows: the confirm-then-write second turn, and weekly step 2 after he answers. Every case is one turn, with his answers given up front where a write is expected.
- Whether the skills *trigger* (the `description:` field).
- Mid-day mode is covered by a single case.
