# vault-graphrag — recall algorithm

Deterministic graph retrieval: from a new ticket's context to a compact
`prior-incidents.md` artifact. Plain-text tooling only (`rg`, YAML parsing);
at vault scale (hundreds to low thousands of notes) this runs in milliseconds
and needs no index.

## Inputs

- The new ticket's structured context (the calling pipeline's `ticket.json` or
  equivalent: summary/digest text, environment, any service names present).
- The binding (`vault.path`, `graph_root`, `client`, `entity_vocabulary`).

## Algorithm

**1. Candidate entities.** Match the ticket text (summary + digest + reproduction
notes) against the binding vocabulary's `name` + `aliases`, case-insensitive,
word-boundary. Also match against any entity notes' `aliases` on disk (the vault
may know informal names the binding doesn't yet). Result: the entity set E.

**2. Symptom keywords.** Take the 3–6 most distinctive content words from the
symptom/digest — concrete observables ("silence", "timeout", "transfer",
"duplicate"), never scaffolding words ("bug", "issue", "error", "customer",
"PROD"). When in doubt, fewer and sharper.

**3. Scan.** Over `<graph_root>/incidents/` filtered to the binding's `client`:

- For each entity in E: files whose frontmatter links it
  (`rg -l '\[\[<entity>\]\]' incidents/`).
- For each keyword: files whose `symptom` or `root_cause` frontmatter line
  contains it (`rg -il '^(symptom|root_cause):.*<kw>' incidents/`).

**4. Score each candidate incident.**

```
score = 3 × (entity links shared with E)
      + 1 × (symptom keywords matched)
      + 2 if it shares a pattern with any incident already scoring ≥3
```

Tie-break by recency (`date` field, newest first). Exclude the ticket being
investigated. Take the top 5; drop anything scoring below 2 — a weak match
presented as relevant is worse than an honest empty result.

**5. Emit the artifact** — `prior-incidents.md` in the calling pipeline's
working directory, ≤60 lines:

```markdown
# Prior incidents: <NEW-TICKET-KEY>

## Matches (best first)
- **ABC-390** (fixed, 2026-05-14) — score: 2 services + 2 keywords
  - Symptom: caller heard nothing after agreeing to a transfer
  - Root cause: transfer handler awaited a downstream ack with no timeout
  - Resolution: 3s timeout plus spoken filler
  - Note: [[ABC-390]]

## Patterns seen across matches
- [[silent-downstream-await]] — 2 of 3 matches link it

## Search coverage
- Entities matched: voice-gateway, TelephonyCo · Keywords: silence, transfer
- Incidents scanned: 41 · Weak matches dropped: 2
```

Rules:

- **Frontmatter fields only** — symptom/root_cause/resolution lines come straight
  from the incident notes' frontmatter. Never inline note bodies; the `[[key]]`
  link is there if the analyst wants depth.
- The **Patterns seen** rollup is the highest-value line in the artifact: it's
  the difference between "similar things happened" and "this is a known shape
  with a known fix shape".
- **Search coverage is mandatory.** Recall that silently searched narrowly reads
  as "nothing exists" — state what was matched, scanned, and dropped.
- Empty result: keep the artifact, state the entities/keywords tried, one line.
  ("No prior incidents link these entities or symptoms. First of its kind in
  this vault.")

## What recall is not

No root-cause suggestion, no "this is probably the same bug". The artifact
reports graph facts; judgment belongs to the analysis phase reading it.

## v2 escalation path (only when v1 provably misses)

Symptom keyword matching is the weak joint — synonyms ("dead air" vs "silence")
defeat `rg`. If real usage shows recall missing incidents a human finds, add an
embedding index over ONLY the three frontmatter payload lines (symptom,
root_cause, resolution) per incident: small corpus, cheap to rebuild, and the
schema doesn't change — v2 replaces step 3's keyword scan, nothing else. Resist
indexing note bodies; that's how retrieval drifts from the curated payload to
unvetted prose.
