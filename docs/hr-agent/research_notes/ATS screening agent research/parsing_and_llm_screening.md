# Resume Parsing Failure Modes and LLM-Based Resume Screening (2025–2026)

Evidence-strength labels used throughout:
- **[tested]**: a controlled experiment or measurement with stated method (peer-reviewed or preprint with data).
- **[documented]**: vendor or tool documentation describing how the system behaves.
- **[anecdotal]**: practitioner or vendor-blog claims, single-author tests, press coverage without published method.

Research date: 2026-11-03. Seventeen tool calls; several primary pages (MIT order-bias paper, Harvard "Hidden Workers" report, a DEV.to five-ATS test) could not be retrieved. See Gaps.

---

## 1. Which parsers dominate, which layouts break them, and what is evidence vs myth?

### Takeaway
The only *mechanism-level* evidence I found that holds up is this: text extraction recovers almost every glyph from a text-based PDF, so the "PDFs are unreadable" claim is a myth. What actually breaks is **structure**. Multi-column reading order gets scrambled, headers and footers get duplicated or dropped, and non-standard headings miss section detection. Scanned or flattened PDFs (images of text) fail outright. The evidence on specific named ATSs (Workday, Taleo, iCIMS) is almost entirely anecdotal, and I found no independent audit of named commercial parsers.

### Cited Findings
- **Market players.** Textkernel publishes the "Tx Platform" resume parser. Its SDK models include `ExperienceSummary.MonthsOfWorkExperience` [documented]. — [Textkernel Tx .NET SDK docs](https://textkernel.github.io/tx-dotnet/sdk/Textkernel.Tx.Models.Resume.Employment.ExperienceSummary.html); [Tx getting started](https://developer.textkernel.com/tx-platform/v9/resume-parser/overview/getting-started/)
- **"PDF is unreadable" is outdated.** The real failure is scanned or flattened files. The recommended check: if you can select and copy the text in the PDF, a parser can read it [anecdotal, vendor blog]. — [atsverification.com, ATS myths debunked](https://atsverification.com/blog/ats-resume-myths-debunked/)
- **Layout benchmark, one resume (2026-06).** One finance resume was run through a pdf.js-based "ATS-style" parser, not a real commercial ATS, with only the layout varied. Scores [tested, n=1 base document, vendor-run]:
  - single-column control: 100/A, nothing fired;
  - two-column with sidebar: 85/B, with a **critical reading-order scramble**;
  - contact info in a repeated page header: 95, **email extracted 3 times**;
  - creative section headings: 95, "missing standard headings";
  - skills laid out as a table or grid: 100, no breakage;
  - em-dashes and curly quotes: 100, no breakage.
  - Core text was extracted in every variant, so all failures were structural. Not tested: text boxes, icons, skill bars, image text, fonts. The site sells a scanner (Tanzeel Labs, LLC) and is not affiliated with Workday, Greenhouse, Taleo or iCIMS.
  — [atsverification.com ATS parsing benchmark 2026](https://atsverification.com/blog/ats-parsing-benchmark-2026/)
- **Columns, per system.** Multi-column layouts make parsers read *across* columns instead of down them. For Workday, one guide says right-column content is "often lost entirely". Taleo is described as struggling with Unicode, special symbols and anything beyond single-column. iCIMS is described as "more forgiving than Taleo but less sophisticated" [anecdotal]. — [search synthesis of jobshinobi / resumegeni / atsverification two-column guides](https://atsverification.com/blog/two-column-resume-ats-friendly/); [jobshinobi on columns](https://jobshinobi.com/blog/ats-optimized-resume-should-you-use-columns)
- **DOCX vs PDF.** A single-author DEV Community test of 5 platforms reported cleaner parses from DOCX than PDF on Workday and iCIMS [anecdotal; the page returned 404 when fetched, so this rests on the search snippet only]. — [DEV Community, "I reverse-engineered 5 ATS systems"](https://dev.to/charliemorrison/i-reverse-engineered-5-ats-systems-here-is-what-your-resume-actually-looks-like-to-them-36ce)
- **Common causes of wrong reading order.** Multi-column layouts, text boxes and image-based text. Suggested quick check: paste all the PDF text into a plain editor [anecdotal]. — [resumemaker.online, parser formatting problems](https://resumemaker.online/blog/resume-parser-formatting-problems)
- **Academic confirmation that reading order is the hard part.** Alibaba's layout-aware framework (arXiv 2510.09722) fuses PDF metadata with OCR and uses a fine-tuned layout parser specifically to rebuild reading order in multi-column resumes [tested]. A PUC-Rio thesis treats reading order as a template-identification problem [tested]. — [arXiv 2510.09722](https://arxiv.org/html/2510.09722v1); [PUC-Rio thesis](https://www.maxwell.vrac.puc-rio.br/69660/69660.PDF)
- **The "75% of resumes are never seen by a human / auto-rejected" figure is a myth.** It traces to Preptel, a resume-services company, around 2012, with no published methodology. A 2025 Enhancv survey of 25 US recruiters found ATSs almost never auto-eliminate resumes. An HR.com-attributed headline says 92% of recruiters confirm ATSs do not auto-reject [anecdotal or secondary; the original Preptel material was not found]. — [The Interview Guys on the 75% myth](https://blog.theinterviewguys.com/?p=1967); [HiringThing](https://blog.hiringthing.com/applicant-tracking-system-myths); [IT Brief UK on the Enhancv study](https://itbrief.co.uk/story/study-reveals-ats-rarely-auto-rejects-cvs-debunks-75-myth); [resumegeni on the 92% figure](https://resumegeni.com/blog/why-92-percent-recruiters-say-ats-doesnt-auto-reject)
- **Filters that do exist.** HBS/Accenture "Hidden Workers: Untapped Talent" (2021) surveyed 8,000+ hidden workers and 2,250+ executives in the US, UK and Germany. Secondary sources report that roughly half of employers filtered out resumes with a work gap of more than 6 months. The widely cited "88%" figure is attributed inconsistently: to employers in some sources, to hidden workers in others [secondary; the report itself was not retrieved]. — [Next Avenue](https://www.nextavenue.org/hidden-workers-ai-getting-hired/); [TechTarget](https://www.techtarget.com/enterprise-software/news/252506931/Recruiting-AI-systems-under-fire-for-excluding-workers?amp=1); [SBJ](https://www.sbj.net/stories/hidden-workers-may-be-answer-to-hiring-woes,78404); [ERE critique of overstated headlines](https://ere.net/are-evil-ats-robots-secretly-eating-peoples-resumes)

### Inferences
- **Checklist of layout risks, ordered by the strength of the evidence:**
  - **High confidence:** image-only or scanned PDFs, where no text layer means near-total failure. Multi-column or sidebar layouts scramble reading order. These are the only failures with converging tested and academic evidence.
  - **Medium:** contact info placed only in the page header or footer, where it gets duplicated or may be dropped by some parsers. Non-standard section headings miss section detection.
  - **Low or unverified:** tables, curly quotes and dashes, icons, skill bars, unusual fonts, ligatures. The one benchmark showed no breakage for tables or punctuation, and the rest are untested in what I found. Ligatures (fi/fl) and icon fonts are a plausible extraction risk: they can yield odd Unicode or Private Use Area glyphs. A tool can detect that directly from extracted text rather than assert it.
- The candidate tool should frame its findings as "structural parse risk" and **not** as "you will be rejected". No source ties a parse defect to an auto-rejection in a real employer system.

### Gaps
- No primary documentation or independent tests found for Daxtra, HireAbility, RChilli or Affinda. No market-share data on which parser sits behind which ATS (for example, which ATS vendors license Textkernel and which build in-house).
- No source found confirming Textkernel's acquisition of Sovren. The Tx SDK naming suggests a lineage, but this is not verified here.
- No controlled tests found for text boxes, skill bars, icons, ligatures, fonts, or DOCX headers and footers.
- The original HBS "Hidden Workers" report and the Preptel source were not retrieved.

---

## 2. How do parsers extract fields and compute years of experience? (gaps, overlaps, "Present", month-less dates)

### Takeaway
Textkernel documents that total experience is computed from position date ranges, with overlaps **not double-counted**. "Current" or "Present" is resolved against a **Document Last Modified Date**: if that date is missing, an old resume's latest job is treated as still current. Open-source parsers such as OpenResume use regex and keyword feature scoring over positionally grouped lines.

### Cited Findings
- `MonthsOfWorkExperience` is the total months derived from start and end dates across all positions, and overlapping date ranges are not double-counted [documented]. A release note records a fix for wrong values when a CV had overlapping job date ranges, so this was historically buggy. — [Textkernel SDK ExperienceSummary](https://textkernel.github.io/tx-dotnet/sdk/Textkernel.Tx.Models.Resume.Employment.ExperienceSummary.html); [Tx v9 release notes archive](https://developer.textkernel.com/tx-platform/v9/release-notes-archive/)
- The Document Last Modified Date "impacts the interpretation of terms such as 'current'". Without it, the latest experience on old resumes is interpreted as current. Textkernel recommends using today's date for candidate uploads [documented]. — [Textkernel Tx FAQ](https://developer.textkernel.com/tx-platform/v9/faq/); [Tx getting started](https://developer.textkernel.com/tx-platform/v9/resume-parser/overview/getting-started/)
- **The OpenResume parser algorithm** [documented]:
  1. pdf.js extracts text items with x/y position and bold flag.
  2. Items closer together than the average character width are merged, which repairs things like split phone numbers.
  3. Items are grouped into lines.
  4. A line is a section title if it is the only item on its line, bold, and all uppercase. Otherwise the parser falls back to matching section keywords.
  5. Each attribute is chosen by feature scoring. For example, a name candidate loses points for containing "@" or digits. Regexes cover email, phone, "City, ST" location and x.xx GPA; keyword lists cover school, degree and job title.
  6. A new job or education subsection starts when the vertical gap is more than about 1.4 times the typical line gap, with a bold-text fallback.
  - The page states the parser is designed "to parse single column resume in English language".
  — [OpenResume resume parser page](https://www.open-resume.com/resume-parser)

### Inferences
- **For the candidate tool:**
  - Flag month-less dates such as "2019–2021". Total-months arithmetic needs month granularity, so parsers must guess, and the tool should show the candidate the ambiguity range.
  - Flag "Present" or "Current" on a role that has actually ended.
  - Flag overlapping roles. These are legitimate, but the tool should show that total experience will not sum them.
  - Flag gaps over 6 months, given the Hidden Workers gap-filter finding (secondary evidence). Advise honest framing, such as a one-line explanation entry, rather than hiding the gap.
- Section detection in heuristic parsers depends on standard heading words ("Experience", "Education", "Skills"). Creative headings ("Where I've Been") are a documented risk, both in OpenResume's keyword fallback and in the benchmark's "missing standard headings" warning.
- Contact info is pattern-matched. Non-standard phone formats, emails split across text items, or contact details rendered as icons or images can be missed.

### Gaps
- No documentation found on how commercial parsers handle year-only dates (for example, whether "2019" is assumed to be January or mid-year), on how "relevant years" for a specific skill are computed, or on how gaps are surfaced to recruiters as structured fields.
- No vendor documentation found for Daxtra, RChilli or Affinda field extraction.

---

## 3. How can a tool simulate parsing to show the candidate what the ATS "sees"?

### Takeaway
Use a text-layer extractor (pdf.js, PyMuPDF, pdfplumber, pdftotext) and show the **raw linear reading order** next to a heuristic field extraction, OpenResume-style. Present this as an approximation. Even the commercial "ATS checkers" are not emulations of specific vendors' parsers.

### Cited Findings
- OpenResume's parser is open source, browser-based (pdf.js) and documented step by step. Its stated goal: at minimum the name and email should parse, and more parsed fields indicate a more readable resume [documented]. — [OpenResume parser](https://www.open-resume.com/resume-parser)
- Commercial testers (Jobscan, JobShinobi) are described as approximations, not emulations of specific ATS vendors' parsers [anecdotal]. — [JobShinobi on the Jobscan scanner](https://jobshinobi.com/blog/jobscan-resume-scanner-for-pdf-parsing-issues); [JobShinobi PDF parsing test](https://jobshinobi.com/tools/ats-pdf-parsing-test-for-resume-tool)
- **PyMuPDF.** `get_text(sort=True)` orders blocks by bounding box, top to bottom then left to right. A second column that starts slightly higher can therefore still be emitted out of order. A manual workaround is to clip the page into column regions [anecdotal or docs blog]. Unsorted output follows the PDF's internal content-stream order rather than visual order [anecdotal]. — [StackOverflow mirror](https://kiwix.lema.org/stackoverflow.com_en_all_2023-11/questions/74857980/extract-text-in-natural-reading-order-using-pymupdf-fitz); [Artifex blog](https://artifex.com/blog/text-extraction-with-pymupdf); [theneuralbase](https://theneuralbase.com/pdf-processing/learn/beginner/pymupdf-the-recommended-path/)
- **pdfplumber.** `extract_text(layout=True)` preserves spatial layout [anecdotal]. — [theneuralbase](https://theneuralbase.com/pdf-processing/learn/beginner/pymupdf-the-recommended-path/)
- **Hidden-text detection approach (from the prompt-injection paper; reusable for the "what the ATS sees" view)** [tested]:
  - Rule-based visual checks: font size under 4pt, low text-to-background colour distance, low pixel variance, low ink density.
  - Comparing the rendered page image with the extracted text using a vision-language model.
  — [arXiv 2605.28999](https://arxiv.org/html/2605.28999v1)

### Inferences
- **Recommended simulation design:**
  1. Extract in **raw content-stream order**, which approximates a naive parser and shows the worst case.
  2. Extract in **sorted or layout order** as well, which approximates a smarter parser and shows the best case.
  3. Diff the two. A large divergence signals a multi-column or text-box risk.
  4. Run OpenResume-style field heuristics: name, email, phone, location, section headings, job blocks and dates.
  5. Report the fields that could not be found.
  6. Check for no text layer (image-only PDF), for contact info found only inside header or footer regions, and for Private Use Area or odd Unicode from icon fonts and ligatures.
  7. Run the same visual-vs-text discrepancy check used for injection detection, so the candidate's *legitimate* file does not accidentally contain invisible text, such as white text left over from a template.
- Use DOCX as a second path. Converting DOCX to text with python-docx or similar exposes text boxes and headers or footers, which some parsers skip.
- Always caveat the output: "approximates generic parsers; real ATS parsers differ by vendor and configuration".

### Gaps
- No benchmark found comparing pdftotext, pdfplumber, PyMuPDF and pdf.js on resume reading order. The tool builder should build a small corpus of their own (single-column, two-column, sidebar, table, text-box layouts) and test it.
- Not researched or verified: pyresparser's current maintenance state (it is reportedly old and spaCy-2-based), the Affinda free tier, and other GitHub parsers.

---

## 4. LLM-based screening: bias research and implications

### Takeaway
Controlled studies consistently find that LLM screeners show name-based race and gender bias, **self-preference for LLM-written resumes**, and order or position effects. These are mostly simulations or preprints, not audits of live hiring. Commercial ATSs (Greenhouse, Workday HiredScore) are adding AI match scoring but publicly frame it as advisory to recruiters.

### Cited Findings
- **UW, Wilson & Caliskan (AIES 2024; arXiv 2407.20371).** Researchers swapped names associated with white or Black and male or female identity across more than 550 real resumes, using a zero-shot retrieval setup with massive text embedding models [tested].
  - White-associated names were favored 85% of the time; female-associated names only 11%.
  - Black male names were **never** preferred over white male names.
  - Black women's names were preferred 67% of the time versus 15% for Black men's names.
  - Funded by NIST. The authors caution that the setup may not mirror real deployments.
  - Some coverage reports the figures as 85.1% and 51.9% male, so exact numbers vary slightly between write-ups.
  — [UW News, 2024-10-31](https://www.washington.edu/news/2024/10/31/ai-bias-resume-screening-race-gender/); [arXiv 2407.20371](https://www.arxiv.org/pdf/2407.20371); [UW iSchool](https://ischool.uw.edu/news/2024/11/ai-tools-show-biases-ranking-job-applicants-names-according-perceived-race-and-gender)
- **Bloomberg (March 2024).** GPT-3.5 ranked 1,000 equally qualified resumes differing only by name, drawn from 800 demographically distinct names, against real Fortune 500 job listings for four roles: financial analyst, HR business partner, senior software engineer, retail manager [tested, journalism].
  - The result "would fail benchmarks used to assess job discrimination against protected groups", and preferences varied by role.
  - OpenAI responded that businesses can strip names and often fine-tune responses to mitigate bias.
  - **Disputed:** interviewing.io re-analysed the numbers and said Bloomberg did no significance testing. It found bias for HR and financial-analyst roles but not for software engineer or retail manager.
  - Code and data: BloombergGraphics on GitHub.
  — [Bloomberg GitHub repo](https://github.com/BloombergGraphics/2024-openai-gpt-hiring-racial-discrimination); [FlowingData summary](https://flowingdata.com/2024/03/13/racial-bias-in-openai-gpt-resume-rankings); [interviewing.io rebuttal](https://interviewing.io/blog/refuting-bloombergs-analysis-chatgpt-isnt-racist)
- **AI self-preference, Xu, Li & Jiang (arXiv 2509.00462; non-archival at EAAMO 2025 and AIES 2025; v4 dated 2026-06-06).** A controlled resume-correspondence experiment with content quality held constant [tested, preprint]:
  - LLM evaluators preferred their own generated resumes over human-written ones, with self-preference of **67–82%** across models according to the current abstract. An earlier secondary summary reported 68–88%, so the figures vary by version.
  - In simulated pipelines across 24 occupations, candidates using the same LLM as the evaluator were **23–60% more likely to be shortlisted** than equally qualified candidates with human-written resumes.
  - The disadvantage was largest in business fields (sales, accounting).
  - Simple interventions targeting self-recognition cut the bias by more than 50%.
  - LLM-vs-LLM preferences are less consistent: GPT-4o and LLaMA-3.3-70B showed no consistent preference for other models' outputs.
  — [arXiv 2509.00462](https://arxiv.org/abs/2509.00462); [webpronews summary](https://www.webpronews.com/llms-show-strong-self-bias-in-resume-screening-giving-ai-written-applications-a-big-edge-over-human-ones/); [Marginal Revolution](https://marginalrevolution.com/marginalrevolution/2025/10/do-llms-favor-outputs-created-by-themselves.html)
- **FAIRE benchmark (arXiv 2504.01420, 2025).** Racial and gender bias persists in AI-driven resume evaluations across tested models [tested, preprint; details not extracted]. — [arXiv 2504.01420](https://arxiv.org/pdf/2504.01420)
- **Order or position bias, MIT Computational Law Report, "First Come, First Hired?" (Feb 2025).** AI hiring tools may favor the first resume presented [tested per secondary coverage; the page returned 403 and could not be read]. — [MIT law.mit.edu](https://law.mit.edu/pub/firstcomefirsthired)
- **Human-AI interaction, "No Thoughts Just AI" (Wilson et al., 2025; N=528).** People working with a simulated, racially biased AI tended to follow its preferences. Completing an IAT beforehand increased selection of stereotype-incongruent candidates by 13% [tested]. — [UW news tag, Kyra Wilson](https://www.washington.edu/news/tag/kyra-wilson); [arXiv 2509.04404](https://arxiv.org/pdf/2509.04404v1)
- **ATS deployment.**
  - Greenhouse states its AI never advances or rejects anyone on its own. Its talent matching shows recruiters match scores against criteria the recruiters defined and weighted, with explanations [anecdotal or secondary].
  - Workday acquired HiredScore in 2024, which adds automated grading and prioritization.
  - Workday's "Candidate Skills Match" compares application skills with requisition skills and gives recruiters a sortable score [secondary].
  — [Jobscan on Greenhouse](https://jobscan.co/blog/greenhouse-ats-what-job-seekers-need-to-know/); [aiapply.co, Greenhouse vs Lever vs Workday](https://aiapply.co/blog/greenhouse-vs-lever-vs-workday); [G2 HiredScore features](https://www.g2.com/products/workday-hiredscore-ai-for-recruiting/features)

### Inferences
- **Implications for a candidate-side tool:**
  - The candidate cannot control name-based bias. The tool should not suggest changing names; that is an ethical and identity issue, beyond the scope of formatting advice. It *can* note that some employers anonymize, and focus on what is controllable: clarity, evidence and relevance.
  - **Self-preference is a real but double-edged finding.** The evidence suggests LLM-polished phrasing may score better with LLM screeners. But the effect is strongest when generator and evaluator are the same model, which the candidate cannot know, and it is a preprint-level simulation. The tool could reasonably offer LLM-assisted *editing for clarity* while keeping claims truthful and specific. It should not promise ranking gains.
  - **Order effects** are outside the candidate's control. Applying early is weakly supported advice at best.
  - The tool could run an LLM-as-screener simulation: score the CV against the job description with 2–3 different models and permute the order of comparison resumes. That shows variance, and that is the honest message: LLM scores are noisy and model-dependent.

### Gaps
- The full text of the MIT order-bias study, and its effect sizes, were not retrieved.
- No public audit found of bias in a *deployed* commercial ATS AI (HiredScore, Greenhouse matching, Eightfold, and others). Mobley v. Workday litigation was not researched in this pass.
- No confirmation found on whether HiredScore or Greenhouse matching uses generative LLMs versus classic ML or embeddings.
- The models used in arXiv 2509.00462 were not named in the abstract page.

---

## 5. Manipulation: hidden white text and prompt injection. Prevalence, detection, risks.

### Takeaway
About 1% of real resumes contain hidden text or prompt injections, measured in roughly 197k resumes and corroborated by Greenhouse's reported figure. Most are hidden *keyword or skills stuffing* (about 90–96%), not "ignore previous instructions". The text becomes visible once parsing strips formatting, ATS vendors flag it, and cheap detectors exist. Recruiters report disqualifying applicants for it. The agent must not recommend it.

### Cited Findings
- **"Measuring Real-World Prompt Injection Attacks in LLM-based Resume Screening" (Zhang, Jia, Tan, Jiang, Gong, Chen, Song; arXiv 2605.28999, 2026-05-27).** About 196,682 de-identified resumes from hireEZ: 83,277 Applicant Match resumes (2024-07 to 2025-11) and 113,405 resumes from enterprise ATSs (2019-07 to 2025-12) [tested]. Findings:
  - **Prevalence:** 1.19% in Applicant Match and 0.91% in ATS, described as a conservative lower bound.
  - **ATS trend:** 0.6–0.8% in 2019–2023, a spike to about 1.2% in 2024, then down to 0.67% by 2025-H2.
  - **Hiding methods:** white-on-white colour, 1pt size, off-page or behind-element positioning, and layering.
  - **Data injection** made up 90.5% and 95.7% of cases. In order of frequency: hidden skills lists, fabricated experience, copied job requirements, education credentials.
  - **Instruction injection** was only about 5–10%: mostly "combined" attacks (~60%) and naive attacks (~28%).
  - No optimization or adversarial-token attacks were found.
  - **Effectiveness on screening outcomes was NOT measured**, since the datasets had no decision labels.
  - **Detectors:**
    - Hybrid Cascade Detector (rules, then GPT-5 classification): about $0.0001 per resume, 1.35s, 86.1% estimated precision.
    - Visual Discrepancy Analyzer (VLM render-vs-text comparison): about $0.0134 per resume, 24.8s, 92.7% precision.
    - Generic prompt-injection guards did poorly on resumes. PromptArmor: precision 0.583, recall 0.070. PromptGuard: precision 0.455, recall 0.050.
  - **Note:** one co-author (Steven Jiang) is affiliated with hireEZ, the data provider.
  — [arXiv 2605.28999](https://arxiv.org/html/2605.28999v1)
- **Greenhouse figure.** About 1% of roughly 300M resumes processed in H1 2025 contained white-text messages, and Greenhouse alerts recruiters to suspicious formatting [secondary, via NYT coverage]. ManpowerGroup reportedly detects hidden text in about 10% of resumes it scans [secondary]. — [Built In](https://builtin.com/articles/hidden-ai-prompts-in-resume); [Hiration](https://www.hiration.com/blog/white-text-resume-hack/); [The Star (Oct 2025, syndicated NYT)](https://www.thestar.com.my/tech/tech-news/2025/10/09/recruiters-use-ai-to-scan-resumes-applicants-are-trying-to-trick-it)
- **Why it fails.** Parsers strip formatting, so "invisible" text shows up as plain text in the recruiter view, and recruiters often disqualify applicants who try it [anecdotal or press]. It may still slip past older systems [anecdotal]. — [Built In](https://builtin.com/articles/hidden-ai-prompts-in-resume); [Robert Half](https://www.roberthalf.com/us/en/insights/hiring-help/the-risks-of-ai-generated-resumes-what-finance-leaders-should-know); [Entrepreneur](https://www.entrepreneur.com/business-news/job-seekers-try-to-pass-ai-screening-with-white-text-prompts/498109)
- **Unverified claims to avoid citing.** Some low-quality sites cite a "Duke, 2026" study with a 94% detection rate, or claim "41% of job seekers" hide text. Neither has a verifiable primary source. — [The Interview Guys (41% claim)](https://blog.theinterviewguys.com/?p=8508)

### Inferences
- **Why the agent must not recommend these tactics:**
  1. **Detectable.** Vendors flag it, and detectors are cheap enough to run on every resume.
  2. **Self-defeating.** Text hidden with formatting is exposed in the parsed text a recruiter reads.
  3. **Integrity.** About 90%+ of real cases are hidden *claims*: skills, experience, credentials. Hiding claims is misrepresentation, and fabricated credentials can be grounds for rescinded offers or termination.
  4. **Unproven benefit.** No study measured a positive effect on outcomes.
  5. **Instruction injection** against an employer's AI system is an attempt to subvert their automated decision process.
- **Defensive features the agent should have:**
  - Run the hidden-text checks (tiny font, low contrast, off-page text, render-vs-text diff) on the user's own CV and warn. Templates sometimes carry leftover white text.
  - Refuse and explain if asked to add hidden keywords or injections.
  - Include visible, truthful keywords instead.

### Gaps
- No primary Greenhouse publication found; the figures come via NYT-derived coverage. No data on how many flagged applicants are rejected.
- No study found measuring whether hidden injections actually change LLM screener outcomes in production.

---

## 6. Keyword matching specifics: exact, stemmed, synonym, acronyms, hard vs soft skills, density

### Takeaway
Modern parsers normalize skills to taxonomies with language-specific synonyms; Textkernel documents full and partial matches with confidence scores. Recruiter Boolean searches in ATSs like Greenhouse still favor exact titles, tools and credentials. The safe strategy is to include both the acronym and the spelled-out form once, mirror the job description's exact terms where they are truthful, and not repeat for "density". I found no evidence that density matters.

### Cited Findings
- **Textkernel skills taxonomy** [documented]:
  - Three layers: categories, language-independent skill concepts, and language-specific synonyms (surface forms). Each skill links to one or more synonyms per supported language.
  - The Normalize endpoint returns a full match with confidence 1.0, or a partial match scored between 0 and 1 (longest partial match only). Unknown skills come back "unclassified".
  - Skills are deliberately coarse. For example, running, training and tuning ML models collapse into a single "Machine Learning" skill.
  - Synonym-level patches ship between quarterly updates.
  — [Textkernel Skills API overview](https://developer.textkernel.com/tx-platform/v10/skills-intelligence/skills-api/overview/); [Skills normalize](https://developer.textkernel.com/SkillsIntelligence/master/skills/normalize/); [Professions API](https://developer.textkernel.com/tx-platform/v10/skills-intelligence/professions-api/overview/)
- **Greenhouse recruiter search.** Recruiters search by title, skill and keyword, and search favors exact titles, tools, credentials and domain nouns. Recruiters may combine related terms because candidates use different labels (for example, "AE" and "account executive") [anecdotal]. — [Jobscan on Greenhouse](https://jobscan.co/blog/greenhouse-ats-what-job-seekers-need-to-know/); [Enhancv on Greenhouse](https://enhancv.com/blog/how-does-greenhouse-work/); [hireflow on Greenhouse](https://hireflow.net/blog/greenhouse-ats-how-recruiters-screen-your-resume)
- **Workday Candidate Skills Match** compares application skills with requisition skills to produce a sortable score [secondary]. — [aiapply.co](https://aiapply.co/blog/greenhouse-vs-lever-vs-workday)

### Inferences
- **Keyword checklist for the tool:**
  - (a) Extract hard skills, tools, certifications and titles from the job description and check each for an exact or near match in the CV.
  - (b) For acronyms, recommend writing both forms once, for example "Search Engine Optimization (SEO)". Taxonomy parsers may map one to the other, but recruiter Boolean searches may not.
  - (c) Match the job-description title wording where it truthfully applies, for example in a summary line.
  - (d) Treat soft skills as low value for matching. Taxonomies and recruiter searches centre on hard skills and nouns; this is an inference from the sources above, not a direct finding.
  - (e) Do not advise repetition for density. I found no source showing density helps, and repetition reads as stuffing to both human and LLM reviewers.
  - (f) Show each skill in context, in experience bullets as well as the skills list. Context matters for LLM screeners and for "years with skill" computations; the last point is an inference.
- Stemming behaviour (for example "managed" vs "management") varies by system and is undocumented here. The tool can show both an exact-match score and a lemmatized-match score so the candidate sees the difference.

### Gaps
- No vendor documentation found on whether Greenhouse, Workday, iCIMS or Lever keyword search uses stemming or synonym expansion.
- No documentation found on how Textkernel maps "SEO" specifically. Testing the Normalize endpoint would answer it.
- No empirical study found on keyword density effects for either keyword or LLM screening.
