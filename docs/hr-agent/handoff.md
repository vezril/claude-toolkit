# cv-reviewer ("HR agent"): handoff

For a Claude instance picking this up cold. Written 2026-11-03; nothing is built yet.

## What Calvin asked for

> An HR Agent that can receive a CV and a job posting as inputs, and says whether or not it would
> pass filters, and perhaps have some recommendations.

## Read in this order

1. **This file.**
2. `reports/ATS screening agent research.md`: the synthesis, about 5,400 words with inline
   citations. It's the reason for every design decision.
3. `../../openspec/changes/add-cv-reviewer/`: `proposal.md`, then `design.md` (decisions D1–D11,
   open questions), then `specs/cv-reviewer/spec.md`, then `tasks.md` (the work, in order).
4. `research_notes/ATS screening agent research/*.md` only when you need a source. They're split
   into ATS vendor mechanics, parsing and LLM screening, tools/taxonomies/datasets, and
   legal/fairness, and each claim is tagged by evidence strength.

## The research in five lines

- **ATSs auto-reject on knockout answers** (work auth, location, years, degree, licence), not on
  CV text. Every vendor whose docs were readable works this way.
- **AI match scores rank rather than reject.** The newest (Workday HiredScore, Aug 2026) grade
  each requirement for evidence. A low tier is a soft reject.
- **Parsing breaks on structure**: columns, header contact info, odd headings, image-only PDFs.
  PDFs are fine. The 75%-rejected stat is 2012 vendor marketing.
- **Existing tools** (Jobscan, Teal, Rezi) sell a keyword-overlap percentage with no published
  basis, and none of them models knockouts. Resume-Matcher (Apache-2.0) is the transparent
  baseline. Public fit datasets are unlicensed or mislabelled, so the eval set is hand-built.
- **Legally, the line is who decides about whom.** Self-assessment of your own CV is outside NYC
  LL144, EU AI Act high-risk, Colorado, Illinois, California and Quebec Law 25 s. 12.1. Ranking
  other people's CVs puts it inside all of them.

## The design in five lines

- A four-part categorical verdict (knockout exposure, likely AI tier, parse health, rank signals).
  **No percentage.**
- The LLM extracts typed requirements and verbatim evidence. Stdlib Python (plus `pdftotext`)
  computes years, checks quotes, decides the verdict and renders the report.
- "Unknown, ask" is a real answer: work auth and location are never inferred.
- Recommendations are `reframe` / `ask` / `format` / `gap`, and a script rejects any that add an
  unevidenced claim.
- Own CV only, one per run, and refusals for fabrication, hidden text, injection, protected-trait
  inference and recruiter use.

## Before you build

**Ask Calvin the five open questions** at the end of `design.md`: name, personal vs public, FR
support, URL input, prompt certification. The plan has a recommended default for each. Don't
start on `agents/` or `skills/` until he's answered.

House rules that apply here:

- Branch off `main` (it's PR-protected). Never merge without Calvin's word.
- Build it the `prompt-edd` way: eval suite before prompt, a naive v1, one hypothesis per version,
  real runs only.
- Run eval suites sequentially. Parallel runs hit the 5-hour usage limit.
- Bump `.claude-plugin/plugin.json` on release.
- **No real CVs in the repo, ever.** Calvin's own CV included: fixtures are synthetic.

## What's uncertain (don't over-claim these in the agent's output)

- No regulator has said a job-seeker tool is outside EU AI Act Annex III. It's a reading of the
  text, so the design enforces the intended purpose rather than relying on the reading.
- The parsing-failure evidence is one benchmark plus academic work, with no named-vendor audit.
- Greenhouse rule-based auto-reject, iCIMS knockouts and Workday questionnaire knockouts had no
  primary docs found.
- The EU Digital Omnibus Official Journal reference conflicts across sources. Check EUR-Lex before
  quoting the 2 Dec 2027 date anywhere user-facing.
- This is research, not legal advice.
