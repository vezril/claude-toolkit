## Context

`add-delivery-flow` is partially implemented. What exists and works: the schemas and the
stdlib validator, sentinels, the `PostToolUse` edge hook, the trace hook with tier-drift
detection, punch-out enforcement with SSH-signed human-presence decisions, a 15-attack bypass
suite, and four certified steps in `skills/delivery-flow/steps.yaml` — `triage`, `breakdown`,
`challenge-breakdown` (sonnet, 3 consecutive runs each) and `pr-description` (haiku).

What does not exist is a way to finish. `flow-status.py:42` holds one hard-coded 15-step table;
`challenge-implementation`, `project-memory` and `vault-update` sit in it without registry
entries, and `check-certification.py` fails an unregistered step. So the flow cannot reach a
terminal state through certified steps, and the Stage 4 end-to-end rate has no runs to be
computed from. Evals guard against regressions; only real runs produce the rate.

Constraints carried from the parent change:

- Hooks are global to every session with the plugin installed, so anything added must be inert
  outside a repo holding `.delivery-flow.yaml`.
- Artifacts a later step consumes must be schema-backed; prose is permitted only at a terminus
  no step reads.
- Edge checks fire after the write, from a hook, never as a call a model elects to make.
- An LLM reviewing an LLM is a node. Routing must be code or it is not an edge.
- `templates/unattended/unattended-policy.yml` and `scripts/check-protected-paths.py` are a
  paired format/parser; this change adds a second such pair and owes CLAUDE.md a rule.

Target workload: tickets in Jira, repository and project not yet fixed (see Open Questions).
Calvin's Obsidian vault is at `/Volumes/Private/Amazon RAG`, an AFP mount from
`mimir.experimentalneutron.com`, currently holding three notes and no graph structure. It is out
of scope here and recorded only because D7 constrains the follow-up.

## Goals / Non-Goals

**Goals:**
- Run the certified three-node chain from a Jira ticket key to a terminal `outcome.json` without
  touching an uncertified step.
- Produce a human-readable brief at the terminus that a reader with limited working memory can
  scan in the same shape every time.
- Make every punch-out trigger in the chain independently derivable, so the gate does not rest
  on a flag the gated node wrote.
- Make the end-to-end rate computable per profile, with punch-outs separated from failures.
- Leave the `full` profile, and every repo that does not opt in, behaving exactly as today.

**Non-Goals:**
- The OpenSpec proposal node, SDLC implementation, verify, PR and post-back. They stay in the
  `full` profile and are follow-up changes.
- Vault recall and update. `vault.binding` stays null.
- Any new certified node. This change adds zero `prompt-edd` packages, which is its point.
- A supervising orchestrator over profiles (D2).

## Decisions

**D1 — A profile is a config key that truncates the routing table, not a second skill.**
`profile: triage` in `.delivery-flow.yaml` selects an ordered subset from
`templates/delivery-flow/profiles.yaml`; `flow-status.py` routes within it. The alternative,
a separate `triage-flow` skill, would duplicate `SKILL.md`, the hook wiring and the config
reference, and would add three more mirror files to the CLAUDE.md sync list for no new
behaviour. One table, named windows onto it.

**D2 — Profile handoff is the artifact directory; there is no orchestrator over workflows.**
`flow-status.py` already computes position from what is on disk. A later profile starts by
reading `breakdown.json` and `challenge-breakdown.json` from `delivery/<KEY>/`; nothing needs to
tell it they exist. An LLM step supervising profiles would be a non-deterministic step whose job
is routing, sitting on top of a deterministic router — the reviewer trap one level up, and
uncertifiable precisely because routing has to be code. What the human needs instead is a
sentence, so the terminus prints `Profile 'triage' complete — next profile: full (solutioning)`.

**D3 — The brief is a deterministic renderer, not a node.** Everything it needs is already
structured: counts, ids, verdict and findings all live in `breakdown.json` and
`challenge-breakdown.json`. A template over structured data costs no certification package, is
byte-identical on reruns, and cannot hallucinate reassurance about work it never saw — which
matters more here than elsewhere, because this is the artifact a human decision rests on. The
cost accepted: it cannot say "this is riskier than it looks". A fixed shape is also a feature
for the intended reader; the same five sections in the same order every run means you learn
where to look instead of re-reading. Revisit after thirty real briefs, with evidence of what
they failed to say.

**D4 — Coverage blocks; readability is measured and traced.** The brief's prose is largely
inherited — story titles and acceptance criteria written by the breakdown node. Failing the
renderer because inherited text scores a grade too high would punish a step that cannot fix it
and would stall the chain on a cosmetic property. So the edge asserts what the renderer is
actually responsible for: every epic and story id present, the verdict present, every `WEAKENED`
finding present, and no identifier that does not occur in its inputs. Flesch-Kincaid and Gunning
Fog are computed with `skills/readability/scripts/readability.py` and written to the trace, where
a trend across runs is evidence about the breakdown prompt rather than a gate on the brief.

**D5 — Node flags become claims; triggers derive independently.** For each of the three
triage-sourced triggers, `check-punch-out.py` gains a derivation that does not read the node's
boolean:

| Trigger | Derivation |
|---|---|
| `scope` | the item's text carries no acceptance signal, or the breakdown exceeds the epic or story ceiling |
| `architecture` | the breakdown spans more distinct domains than the ceiling, or architecture vocabulary appears in the item or breakdown text, or a `contract_paths` name is named in that text |
| `breaking` | breaking-change vocabulary appears in the item or breakdown text, or a `contract_paths` name is named in it |

A trigger fires on the derivation OR the claim. That single rule is what closes the hole: a
node writing `false` no longer skips a gate whose derivation fires, and a node asking for a
human is never overruled. Derivations are deliberately coarse — a false positive costs a
question, a false negative costs the guarantee.

**Revised while implementing: disagreement is recorded, not failed.** The first draft failed
the producing artifact's edge when claim and derivation disagreed, by analogy with a sentinel
count mismatch. That analogy does not hold, for two reasons the implementation made obvious.
The derivations available before any code exists are textual heuristics, and a node is
entitled to disagree with a keyword match. More seriously, the claim and the derivation are
often not the same proposition: `handoff` asserts the item is unclear or out of scope, while an
epic count over its ceiling asserts the work is large, and a node can be right about the first
while the second holds. Failing an edge there stops the chain on an inference the artifact
never made — and on a real tracker, where most tickets state no acceptance criteria, it would
stop nearly every run. So the edge records `policy_disagreement` (trigger, claimed, derived,
evidence) and passes, `check-punch-out.py` reports it, and the count of disagreements becomes
the thing a reviewer can actually ask about. A sentinel count mismatch stays an edge failure
because there the claim and the fact *are* the same proposition, and one of them is simply wrong.

Because the acceptance-signal derivation fires on any terse ticket, it is switchable:
`punch_out.require_acceptance_signal` (default true). Turn it off and the `scope` trigger rests
on the ceilings and the node's flag alone.

**Known residual, found by attacking it.** A text-only derivation can be laundered: rewrite the
item, the triage summary and every acceptance criterion to drop the vocabulary, split the
breakdown under both ceilings, and all three derivations go quiet. Measured, not assumed — the
simulated attack is in `tests/delivery-flow/bypass/`. Two things stand between that and a
bypass, and they compose:

- Laundering by hand means editing artifacts whose sha the trace already holds, which marks the
  run `failed` with reason `manual-correction`. The gate is not passed, the run is void.
- Laundering by *rerunning the node* leaves the shas legitimate, and then nothing catches it.
  That is the real residual: a derivation that reads node output cannot be independent of a node
  determined to shape its output. The defence that does not share this weakness is a diff-based
  derivation, and before implementation there is no diff — which is precisely why the `full`
  profile's `contract_paths` and `protected_paths` triggers exist and why this profile's gate is
  the weaker one. Submit it as a residual rather than claiming the triggers are unforgeable.

Corrected while implementing: an earlier draft derived `breaking` from the files a story
touches. There are none — `schemas/breakdown.json` closes a story to `id`, `statement`,
`domains` and `acceptance_criteria`, with `additionalProperties: false`, and in this profile
nothing is implemented so `git_changed_files` is empty too. The only material available before
implementation is text, labels, domains and counts, so the derivations work on those. This is
weaker than a diff-based derivation and is recorded as such: in the `full` profile the existing
`contract_paths` and `protected_paths` triggers do read the diff, and that is where the strong
version of this check lives.

**Mismatches are checked when the evidence arrives, not before.** `triage.json` is written
before `breakdown.json`, so at triage time only the text derivations can run; the count and
domain derivations become available later. The comparison therefore runs on both artifacts'
edges and only over derivations that are determinable at that moment — otherwise `triage.json`
would fail its edge for not knowing something that did not yet exist.

**D6 — The Jira adapter talks REST, with the token from the environment.** Adapters must be
deterministic scripts with no LLM, so the Atlassian MCP connector is unusable inside one — MCP
tools are callable only by a model. `JIRA_BASE_URL`, `JIRA_EMAIL` and `JIRA_API_TOKEN` come from
the environment; a missing or rejected credential is exit 3 with the fix on stderr, never a
partial `item.json`. Field mapping is explicit and recorded in `references/adapters.md`, because
Jira's custom fields are per-site: `summary` → `title`, rendered description → `body`, issue type
→ `type_hint`, status name → `status`, labels plus components → `labels`, issue links and the
epic parent → `links`. Story points and other `customfield_*` values are deliberately not mapped
in v1; the chain's certified nodes do not read them.

**D7 — The vault stays off, and the follow-up must distinguish "empty" from "unreachable".**
Recorded here so it is not rediscovered: the vault is an AFP mount on a NAS. When the volume is
not mounted, a recall step must exit non-zero, not return "no prior context" — a cold-start empty
result and a dead mount are indistinguishable at the output and would silently drop organizational
memory from the run while still looking successful in the trace. The follow-up change owes a mount
check before the search and distinct exit codes for the two cases.

**D8 — The terminus writes `outcome.json` itself.** When the last step of a profile passes its
edge, the report script runs and writes `completed`. Without this, a profile "finishing" is just
the absence of a next step, which is indistinguishable from a stall and leaves the run outside
the success-rate denominator. The outcome vocabulary is unchanged: `completed`, `punched-out`,
`failed`, `abandoned`.

**D9 — This change's specs are `ADDED`, not `MODIFIED`.** `add-delivery-flow` is unarchived, so
none of its specs are live in `openspec/specs/`. Writing `MODIFIED Requirements` against deltas
that are themselves pending would produce a spec no validator can resolve. The four capabilities
here are therefore additive, they amend the parent change's deltas in prose where they overlap,
and the two changes archive together.

**D10 — The Jira adapter follows a GitHub reference, and a failure to follow is exit 3.**
Discovered against the real project (`AN` on bitquill): three of the four newest tickets have no
description beyond `github reference: <url>`. The requirement lives in the GitHub issue; the Jira
ticket is a routing stub. Three options were on the table — repoint the chain at GitHub Issues,
follow the link inside the Jira adapter, or run the stubs and let them punch out. Following the
link keeps Jira as the system of record (which is where sprint, epic and assignee live) while
giving the node something to read.

It stays an edge rather than becoming a node: `gh` is called through the same runner the GitHub
adapter uses, there is no model in the path, and the mapping is mechanical.

Two consequences are deliberate:

- **An unfetchable reference exits 3 rather than yielding a thinner body.** Soft-failing would
  make `body` a function of network state, and "two fetches of an unchanged issue are
  byte-identical" is a contract the fixture tests assert. A variable body would also make the
  artifact sha vary, which the trace reads as a manual correction.
- **Referenced content is fenced and labelled unverified.** Anyone can file an issue on a public
  repo, so this widens the untrusted-text surface from the client's Jira to the internet. The
  `triage` profile writes no code and opens no PR, so the worst case remains a bad breakdown and
  a local brief — but the fence exists so no node reads a stranger's issue text as the client's
  requirement. The exposure is called out again in Risks.

`links` keeps carrying Jira keys only; GitHub references go in their own `references` array, so
a GitHub number can never be mistaken for a tracker key by a later step.

## Risks / Trade-offs

- **The slice may not be impressive enough.** A reviewer may read "ticket to breakdown" as thin.
  Mitigation: the evidence is the point — three certified nodes, derived triggers, bypass-tested
  punch-outs, a real rate from real runs. A thin chain with complete evidence is what Stage 4
  asks for; a wide chain with uncertified nodes is what it rejects.
- **Profile truncation can hide a step's absence.** If a step is dropped from a profile by
  mistake, the flow terminates early and reports success. Mitigation: `profiles.yaml` lists steps
  explicitly, every profile declares its terminus, and a test asserts the union of the `triage`
  and `full` profiles equals the full routing table.
- **Derived triggers will over-fire at first.** Coarse derivations plus the OR rule means more
  punch-outs than today, which lowers the completed rate. Accepted deliberately: the alternative
  is a number computed behind a gate that a node can open for itself. The report distinguishes
  `punched-out` from `failed`, and the ceilings are tunable once there are runs to tune against.
- **Jira field mapping is per-site and will need revision.** Mitigated by mapping only the nine
  fields `item.schema.json` requires and by fixture tests, but the first real project may still
  force changes.
- **Untrusted ticket text still enters the chain.** Nothing here writes code or opens a PR, so
  the worst case is a bad breakdown plus a comment, and the external-tracker punch-out gates the
  comment. The exposure grows materially in the follow-up profile and is called out there.
- **Following a GitHub reference widens that surface from the client's tracker to the internet.**
  Anyone can file an issue on a public repo, so D10 pulls text written by strangers into `body`.
  Three things bound it: the content is fenced and labelled unverified rather than presented as
  the client's requirement; the `triage` profile writes no code, opens no PR and posts nothing,
  so the blast radius is a bad breakdown and a local brief; and the followed URL is recorded in
  `references`, so a reviewer can see exactly what text entered the run and from where. **This
  needs revisiting before the `full` profile follows links**, where the same text would reach a
  step that writes code.

## Migration Plan

1. Land `profiles.yaml` with `full` as the default; no repo behaviour changes.
2. Add the Jira adapter and point a test repo's `.delivery-flow.yaml` at a real project with
   `profile: triage` and `tracker.external` set per the answer to Q2.
3. Add the brief renderer and its edge, then the derived triggers, then extend the bypass suite.
4. Three real runs on real tickets; read the per-profile rate.
5. Docs and figures in the same PR, per CLAUDE.md.

## Open Questions

1. **Which repository and Jira project is the first target?** Needed for
   `.delivery-flow.yaml` and for the fixture tests' field shapes. Blocks tasks 5.x.
2. ~~**Is that Jira yours or a client's?**~~ **Answered 2026-10-28: a client's, so
   `tracker.external: true`.** Every post-back to it needs a punch-out carrying a signature that
   verifies against `decisions.allowed_signers`. Two consequences worth stating plainly: the
   signing key does not exist yet, so an outward write would refuse rather than proceed — and
   the `triage` profile has no post-back step (Q3), so nothing in this chain is blocked by that.
   The chain only ever *reads* Jira. `init-delivery-flow.py` is therefore run **without**
   `--internal`, which is also its own default for a Jira project.
3. **Does the `triage` profile post back to Jira at all?** The chain is useful without it
   (`summary.md` is local), and omitting post-back removes the only outward action in the
   profile. Current plan: omit it, and let the human paste the brief. Confirm.
4. **Do punch-outs sit inside or outside the success-rate denominator?** Unresolved in the parent
   change and still worth asking the reviewer; the report emits both readings until someone rules.
