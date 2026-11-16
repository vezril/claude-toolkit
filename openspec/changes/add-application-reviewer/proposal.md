## Why

Calvin wants an "HR agent": give it a CV and a job posting, and it says whether the CV would get
through the posting's filters and what to change. The tools that already do this (Jobscan, Teal,
Resume Worded, Rezi) all output a keyword-overlap percentage with a made-up threshold ("aim for
75%"), and the research in `docs/hr-agent/reports/ATS screening agent research.md` shows that
percentage is measuring the wrong thing:

- **Automatic rejection comes from knockout rules, not CV text.** Every ATS whose docs we could
  read (Oracle/Taleo, SuccessFactors, Ashby, Lever, LinkedIn, Indeed) auto-rejects on
  employer-configured rules over the candidate's *answers* to screening questions: work
  authorization, location, minimum years, degree, licence. None of the overlap tools models this.
- **AI scores rank, they don't reject, and they now grade per requirement.** Workday HiredScore
  (LLM grading since Aug 2026) checks each qualification against the parsed CV; meeting every
  basic qualification is what earns an A/B. Greenhouse Talent Matching sorts into
  Strong…Limited. A low tier is a soft reject: the CV never gets opened.
- **Parsing fails on structure, not on PDFs.** Multi-column reading order, contact details in
  page headers, creative section headings and image-only PDFs are what break. "ATS can't read
  PDFs" is a myth, and so is "75% of resumes are rejected by robots" (Preptel marketing, 2012).

So an agent that predicts the filters faithfully has to do what those systems do: extract typed
requirements from the posting, check each one for cited evidence in the CV, flag the ones likely
to be asked as knockout questions, and check whether the file survives text extraction. That is
also the only design whose output can be regression-tested against hand-labelled gold.

## What Changes

- **New agent `application-reviewer`** (`agents/application-reviewer.md`): candidate-side only. Takes the user's
  own CV (PDF, DOCX, MD or text) and one job posting (pasted text, or a file), and returns a
  four-part verdict (knockout exposure, likely AI tier, parse health, rank signals) plus
  recommendations that are either truthful reframings of evidence already in the CV or
  questions to the candidate. It never outputs a match percentage.
- **New skill `ats-screening`** (`skills/ats-screening/`): the procedure, the JSON contracts for
  every step, and a reference on how ATS filtering actually works (distilled from the report).
- **New deterministic scripts** (`scripts/application-review/`, stdlib + `pdftotext`): file extraction and
  parse-health checks, years-of-experience arithmetic, evidence-quote verification, verdict
  composition, report rendering. The LLM extracts and matches; code decides.
- **New eval suite** `evals/application-reviewer/` built the `prompt-edd` way: ~30–40 synthetic CV/posting
  pairs with per-requirement gold labels and planted traps, a naive baseline arm, haiku + sonnet,
  N=3. Plus `tests/application-review/` pytest for the scripts.
- **Hard refusals:** fabricating skills/credentials/dates, hidden or white text, prompt injection
  in the CV, inferring protected traits, "hide X because employers discriminate" framing, and
  anyone else's CV (no bulk, no ranking). The last one is what keeps the tool outside NYC LL144,
  EU AI Act Annex III 4(a), Colorado SB 26-189, Illinois HB 3773 and Quebec Law 25 s. 12.1.

## Capabilities

### New Capabilities
- `application-reviewer`: the agent's inputs, the four-part verdict, the step contracts
  (`parse.json`, `requirements.json`, `evidence.json`, `verdict.json`, `recommendations.json`),
  the deterministic checks between steps, the refusal set, and the intended-purpose boundary.

### Modified Capabilities

<!-- none -->

## Impact

- New files only: `agents/application-reviewer.md`, `skills/ats-screening/**`, `scripts/application-review/**`,
  `evals/application-reviewer/**`, `tests/application-review/**`.
- Listings: `README.md` (skills and agents tables), `agents/README.md`, `evals/README.md`.
- `.claude-plugin/plugin.json` version bump on release (installs are cached by version).
- Not an SDLC workflow change, so the CLAUDE.md doc-sync rule for the SDLC playbook and figures
  does not apply.
- Runtime dependency: `pdftotext` (poppler) for PDFs; DOCX is read with stdlib `zipfile`. A
  white-text check on PDFs needs a PDF library (design D4).
- Privacy: real CVs never enter the repo; all fixtures are synthetic.
