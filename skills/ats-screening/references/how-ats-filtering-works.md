# How application filtering actually works

Distilled from `docs/hr-agent/reports/ATS screening agent research.md`. Read this
when you need to explain *why* a verdict says what it says, or when a user asks
how any of this works. Every claim here carries its evidence strength, because
some of it is vendor documentation and some of it is folklore that got repeated
until it sounded like fact.

Three labels are used below:

- **documented** — a vendor's own docs or a primary source says so.
- **inferred** — follows from documented behaviour but nobody states it.
- **weak** — one small study, one benchmark, or an anecdote. Say so out loud if
  you lean on it.

## 1. Automatic rejection comes from knockout questions, not from reading the CV

**documented.** Every applicant tracking system whose documentation could be
read works the same way: the employer writes a rule, the rule runs against the
candidate's *structured answer* to a screening question, and it fires when the
application is submitted.

- Oracle Recruiting Cloud lets an admin give a disqualifying answer a negative
  score that disqualifies automatically.
- SAP SuccessFactors marks a pre-screening question "Disqualifier", or sets a
  weighted Required Score below which applicants are auto-disqualified. It
  explicitly forbids free-text questions as disqualifiers, because the system
  cannot tell what a correct answer is.
- Ashby: "The Rejection Condition is based on application questions." Ashby is
  the one outlier, because its text conditions mean a free-text answer *can*
  trigger a rejection there.
- Lever's automations are "commonly used to auto-archive candidates based off
  of knockout questions".
- LinkedIn auto-rejects candidates who miss a question flagged "Must-have
  qualification". Indeed sends anyone failing a "deal breaker" to the Rejected
  tab, and suggests stock questions on years, diploma, licence, travel and
  availability.

The questions that carry knockouts are the same list everywhere: **work
authorization and sponsorship, location or on-site, minimum years, degree,
named licences and certifications**. Clearance and language belong on the list
by **inference**: postings ask for them constantly and the vendor docs
collected never mention them.

What this means for a user: a rejection that lands minutes after applying is
almost certainly a knockout answer, not a judgement about their CV.

## 2. "75% of resumes are rejected by robots" is marketing from 2012

**documented as unfounded.** The number traces to Preptel, a resume-optimization
company that shut down around 2013 and never published a methodology.

The counter-evidence is also weak: a survey of 25 US recruiters, run by a
company that sells resume tools, in which 92% said their system does not
auto-reject on formatting, missing keywords or low match scores, and every one
used knockout questions.

The employer side of the story is compatible and more serious: Harvard Business
School and Accenture's *Hidden Workers* report found 88% of employers agree
qualified high-skilled candidates get screened out for not matching exact
job-description criteria. Secondary sources attribute that figure
inconsistently and it was not re-verified.

No large independent study measures how many rejections come from CV content
versus knockouts. **The honest position is that this number is unknown**, and
nothing in a report should imply otherwise.

## 3. AI match scores rank; they do not reject. A low tier is a soft reject.

**documented.** Every AI layer is framed as advisory. Greenhouse: "Talent
Matching is assistive AI, not automated-decision-making" and "does not
automatically advance or reject candidates". Ashby: "no decisions are made" by
its AI.

**inferred, and the part that actually matters.** HiredScore's docs tell
recruiters to sort applicants A to D. A sorted queue reviewed top-down under
time pressure is a soft reject: the CV is never opened. Ashby reports a team
reviewing 1,500 resumes in six hours with AI assistance.

The scoring has also moved from keyword overlap to **per-requirement
judgements**:

- Workday HiredScore (LLM grading, August 2026): "each qualification is now
  assessed directly", and "candidates who meet all scoped basic qualifications
  receive an A or B". Preferred qualifications only separate A from B, or C
  from D. An older definition demanded most preferred qualifications for an A,
  so grade meanings vary by version.
- Oracle's generative service scores skills, relevant experience, domain
  knowledge and role seniority, averages them, and writes a 50-word rationale.
- Ashby labels each recruiter-defined criterion "Meets" or "Does not meet" and
  cites the resume.
- Greenhouse is closer to the old world: recruiters calibrate on 4–6 key
  skills, and the preview highlights "exact" and "similar" keyword matches.
- Workday's older Candidate Skills Match is plain skill-to-skill similarity
  that "doesn't consider how recently a candidate acquired relevant skills,
  how long they used them, or total years of work experience".

No vendor publishes weights, embedding models, title normalization or recency
weighting. And because AI ranking is variously opt-in, admin-enabled or
credit-billed, **you cannot assume a given posting runs it at all**.

## 4. Years of experience is arithmetic over dates

**documented.** Textkernel, a parser behind many systems, computes total months
from position date ranges. "Overlapping date ranges are not double-counted,"
and the figure "is NOT derived from text like 'I have 15 years of
experience'". "Present" resolves against the document's revision date; without
one, an old resume's last job is treated as current.

How parsers resolve year-only ranges like "2019–2021" is **undocumented
anywhere**. That is why this pipeline flags such a total `approximate` rather
than picking a convention and sounding certain.

A release note records a past bug with overlapping ranges, so even the
documented behaviour has been fragile.

## 5. Keywords: taxonomies, not density

**documented.** Textkernel normalizes skills to language-independent concepts
with per-language synonyms, returns full matches at confidence 1.0 and partial
matches below, and deliberately collapses fine distinctions — training, tuning
and running models all become "Machine Learning".

**No source anywhere shows that keyword density helps.** Two rules follow, and
they are the only keyword advice this skill gives:

1. Write each acronym once in both forms. A taxonomy may map "SEO" to its
   expansion; a Boolean recruiter search will not.
2. Put skills inside dated experience bullets, not only in a skills list, so
   both an LLM grader and per-skill duration logic can find evidence.

**inferred, and worth telling the user:** a requirement they satisfy only by
answering a questionnaire can still be graded unmet by an AI that reads the CV.
So it belongs in the CV as well as in the answer.

## 6. Parsers lose structure, not text

**weak-to-moderate.** Text extraction recovers nearly every glyph from a PDF
that has a text layer. "An ATS can't read PDFs" is a myth. What actually breaks:

- **reading order in multi-column layouts and sidebars**
- **contact details placed in a page header or footer**
- **non-standard section headings**
- **scanned or flattened PDFs with no text layer**, which fail outright

The one controlled benchmark ran a single finance resume through a pdf.js-based
parser, not a real commercial system: single-column control scored 100, a
sidebar layout dropped to 85 with a reading-order scramble, header-placed
contact info pulled the email out three times, and creative headings raised a
missing-headings warning. Tables, em-dashes and curly quotes caused no
breakage. The vendor sells a scanner and the sample is one document.

It agrees with stronger academic work: Alibaba's layout-aware resume framework
exists precisely to rebuild reading order in multi-column CVs, and PyMuPDF's
sorted extraction orders blocks top-to-bottom then left-to-right, so a second
column starting a few points higher comes out interleaved.

Claims about specific vendors — that Workday drops right-column content, that
Taleo chokes on Unicode — are **anecdotal**. No independent audit of a named
commercial parser surfaced, and no source ties a parse defect to an actual
auto-rejection. So the wording is always "structural risk", never "you will be
rejected".

## 7. The human layer is a skim

**weak.** Ladders' eye-tracking report put the initial screen at 7.4 seconds,
focused on titles and section headers, and published no sample size. Treat it
as directional. Combined with Oracle's explicit "role seniority" dimension, it
means recent job titles that visibly map to the target role matter twice.

## 8. The regulated line is who decides about whom

**documented.** Every employment-AI regime researched is triggered by use *by
or for an employer or agency, to decide about another person*: NYC Local Law
144, EU AI Act Annex III 4(a) high-risk recruitment (now from 2 Dec 2027),
Colorado SB 26-189, Illinois HB 3773, California CRD and CCPA ADMT, Quebec Law
25 s. 12.1. *Mobley v. Workday* advances an agent theory on the vendor side; a
court conditionally certified a collective of applicants aged 40 and over. It
remains an allegation, not a finding. The EEOC's iTutorGroup settlement is the
one documented case of hard-coded content rejection: software that auto-rejected
women 55+ and men 60+ by birthdate.

A job seeker assessing their own CV sits outside all of it. The moment a
recruiter, agency or employer uses the same output to score other people, it is
inside all of it.

**What no regulator has said** is that a job-seeker tool is outside Annex III.
That is a reading of the text, not a ruling. Which is why the boundary is
enforced in behaviour — one CV, the user's own, no ranking — rather than
asserted in a disclaimer.

Also: if a posting requirement looks discriminatory, say so to the user rather
than optimising around it. Requiring "Canadian experience" is banned in Ontario
job postings as of 2026. Age caps, and about half of employers reportedly
filtering out CVs with work gaps over six months, belong in the same
conversation. Honest framing of a gap, never concealment.

## What to say when asked how sure we are

"I can't see this employer's configuration" is the whole of it. The posting
tells us what they say they want. Vendor documentation tells us the shape of
the machinery. Neither tells us which knockouts this employer switched on,
whether they bought the AI ranking layer, or which parser they run. Every
knockout in a report is "likely", and that word is doing real work.
