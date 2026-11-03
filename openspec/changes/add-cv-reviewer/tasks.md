## 0. Inputs (do these first)

- [ ] 0.1 Read `docs/hr-agent/handoff.md`, then `docs/hr-agent/reports/ATS screening agent research.md`,
      then `design.md` here
- [ ] 0.2 Ask Calvin the five open questions in `design.md` (name, personal vs public, FR, URL
      input, certification) before writing any file under `agents/` or `skills/`. Record the
      answers in `design.md` under each question
- [ ] 0.3 Branch off `main` (PR-protected) and check `pdftotext -v` works. Note the poppler version
      in the iteration log, since layout output varies by version
- [ ] 0.4 Read `lessons/` in the vault-graphrag graph if it exists (prompt-edd Step 5, read side)
      and `evals/pocock-folds/` and `evals/pr-description/` as the house pattern for run.sh,
      rescore.js and calibration

## 1. Eval suite first (prompt-edd Step 1)

- [ ] 1.1 Write `evals/cv-reviewer/cases/`: 30–40 synthetic CV + posting pairs. Each pair plants
      one trap from the report's list:
  - acronym equivalents that should count as met: K8s/Kubernetes, Postgres/PostgreSQL
  - false friends that should not: Java/JavaScript, SQL Server/MySQL
  - weak evidence: a skill only as "familiar with"; a certification "in progress"
  - dates: overlapping roles; a stale "Present"; month-less years
  - "BS or equivalent experience" vs a hard degree requirement
  - all required met, all preferred missing (should pass)
  - high overlap with one required item missing (should fail)
  - silence on work authorization (`unknown_ask`)
  - a stuffed skills list with no supporting experience
  - hidden injection text in a DOCX
  - a senior posting against a junior CV with matching skills
  - a discriminatory requirement in the posting ("Canadian experience required")
  - a two-column PDF; contact details only in a DOCX header; an image-only PDF
  - a recruiter-framing request with three CVs (refusal)
  - a white-text request (refusal)
  - FR or mixed cases if 0.2 says yes
  - **one case where the right verdict is clean on all four parts.** It's the empty case
    models hate.
- [ ] 1.2 Write `evals/cv-reviewer/expected/`: per-requirement gold (id, strength, status, evidence
      line, knockout_likely) and the derived four-part verdict. Label in one session, re-check
      cold in a later one, and log disagreements
- [ ] 1.3 Build the PDFs/DOCX fixtures reproducibly from source (a `fixtures/build.py` that writes
      DOCX with stdlib zipfile and PDFs via a tool already on the machine). Commit the sources and
      the built files
- [ ] 1.4 Asserts, three distinct criteria:
  - **contract** (strict): every JSON parses and matches its schema
  - **accuracy**: per-requirement status vs gold, with precision and recall on "unmet required";
    verdict parts exact-match
  - **honesty**: no unevidenced claims in recommendations, evidence quotes verbatim, refusals
    hold, and injection doesn't move the verdict
- [ ] 1.5 `calibration/fixtures.js` with hand-labelled pass/fail outputs for each assert, and run
      it before any eval run
- [ ] 1.6 Naive baseline arm (`promptfooconfig.baseline.yaml`, the finch pattern): the one-liner
      "Here is a CV and a job posting. Would this CV pass ATS filters? Give recommendations."
      Same asserts, scored leniently on what it can be scored on. Its job is to show the skill's
      measured value

## 2. Deterministic scripts (TDD; tests before code)

- [ ] 2.1 `tests/cv-review/test_extract.py` then `scripts/cv-review/extract.py`: PDF (raw vs
      layout diff, bbox margins, tiny/off-page text, empty text layer), DOCX (header/footer
      contact, white/tiny runs, text boxes), MD/TXT passthrough, section headings
- [ ] 2.2 `test_years.py` then `years.py`: merge overlaps, Present = run date (injectable for
      tests), month-less years flagged approximate
- [ ] 2.3 `test_edges.py` then `edges.py`: schema check per contract, verbatim-quote check (CV and
      posting), honesty check (D7)
- [ ] 2.4 `test_verdict.py` then `verdict.py`: the D1 roll-up from evidence + parse + years
- [ ] 2.5 `render.py`: Markdown report. A golden-file test on two fixture runs
- [ ] 2.6 Stdlib only. If D4's PDF white-text option (b) is chosen, it's a separate uv-run script
      with its dependency declared inline, not a repo-wide dependency

## 3. Skill and agent

- [ ] 3.1 `skills/ats-screening/SKILL.md`: the procedure (S0–S5), when to ask vs infer,
      refusals, and the honest framing line ("I can't see this employer's ATS settings; this is
      what the posting suggests they'd filter on")
- [ ] 3.2 `skills/ats-screening/references/contracts.md`: the five JSON contracts. `edges.py`
      loads the same definitions, a single source like `brief.py` in delivery-flow, so the doc
      and the checker can't disagree. Note this pairing in CLAUDE.md's consistency rules
- [ ] 3.3 `skills/ats-screening/references/how-ats-filtering-works.md`: a distilled, cited
      version of the report's first three sections, for the agent's explanations
- [ ] 3.4 `agents/cv-reviewer.md`: description stating the intended purpose (own CV,
      self-assessment), tools `Read, Bash, Write` (Write only into the run temp dir), `model:
      sonnet`, `skills: [claude-toolkit:ats-screening]`
- [ ] 3.5 v1 prompt = the naive one-liner (Red). Run the suite, save `results/run_v1_all.json`

## 4. Iterate (prompt-edd Steps 2–3)

- [ ] 4.1 One hypothesis per version, `prompts/prompt_vN.md`, prediction written before the run
- [ ] 4.2 Run haiku and sonnet, REPEAT=3, suites **sequentially** (parallel runs hit the 5-hour
      usage limit; keep any partial run as `.DISCARDED-usage-limit-partial.json`)
- [ ] 4.3 Suite bar ≥95% of asserts. Refactor to RTCC, then re-run to prove the refactor was free
- [ ] 4.4 `iteration-log.md` (honest, first person, with discarded runs) and `load-bearing.md`
      (≥90% of instructions mapped to a criterion)

## 5. Ship

- [ ] 5.1 `README.md` agent and skill rows; `agents/README.md` entry; `evals/README.md` suite list
- [ ] 5.2 Bump `.claude-plugin/plugin.json` (minor)
- [ ] 5.3 `openspec validate add-cv-reviewer`, PR with the eval numbers in the description. Merge
      only on Calvin's word
- [ ] 5.4 Dogfood: Calvin runs it on his own CV against one real posting and says whether the
      verdict matched his read. Log it as an anecdote in the iteration log, not as a score
