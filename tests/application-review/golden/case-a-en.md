# Application review

I can't see this employer's ATS settings, so nothing below is a prediction of what their system is configured to do. It's what this posting suggests they would filter on, with the evidence I could find in your CV quoted underneath.

## Verdict

| Part | Reading |
|---|---|
| Knockout exposure | **at risk** |
| Likely AI tier | **some gaps** |
| Parse health | **structural risk** |

### Why

- **R1** — '5+ years of Python' is a likely screening question and the CV does not meet it
- **R3** — 'Authorized to work in Canada' is required and the CV is silent on it
- contact_in_header: An email or phone number appears only in the page header.

I don't infer work authorization, location or clearance from an address, a name or a school. Where your CV is silent, the answer is a question for you.

## Requirement by requirement

| Id | Requirement | Strength | Status | Evidence from your CV |
|---|---|---|---|---|
| R1 | 5+ years of Python | required | partly met | "Built data pipelines in Python and Scala." |
| R2 | Experience with Kubernetes | required | met | "Operated production Kubernetes clusters across three regions." |
| R3 | Authorized to work in Canada | required | unknown, needs your answer | no quote found |
| R4 | AWS Certified Solutions Architect | preferred | not met | no quote found |

### Where I stopped trusting my own reading

- **R1**: met → partly met, the dates give 4.9 years against a 5-year requirement

## Ranking signals

- **R1** — the dates give 4.9 years against a 5-year requirement, which is close enough that a different rounding could go either way
- **R4** — the preferred 'AWS Certified Solutions Architect' is not evidenced

## Years of experience, as a parser would count them

Overlapping roles are counted once, "Present" is dated to 2026-11-03, and anything you state as a total is ignored.

- Total across all positions: 2022-01 to 2026-11 = 59 months (4.9)
- **R1**: 2022-01 to 2026-11 = 59 months (4.9) against a 5-year requirement

## How your file reads to a parser

- [risk] **contact_in_header** — An email or phone number appears only in the page header.
  - `marie.tremblay@example.com \| 514-555-0142`

## What you can do

### File and layout fixes

- Move your email and phone out of the page header into the first line of the body.

### Surface what's already there

- **R2** — Name Kubernetes on a skills line as well as in the bullet, so a keyword match finds it.
  - Evidence from your CV: "Operated production Kubernetes clusters across three regions."

### Questions only you can answer

- **R3** — If you are authorized to work in Canada, say so in one line under your contact details.

### Real gaps

- **R4** — You hold no AWS certification. It is preferred rather than required, so it costs you ranking, not the application.
