---
name: dsm-5
description: "DSM-5-TR (Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition, Text Revision; APA, 2022) — the meta/router skill for the diagnostic classification system. Covers how the manual is built and how it is meant to be used: the definition of a mental disorder, the role of distress and functional impairment, criteria as necessary-but-not-sufficient, specifiers/subtypes/severity and course modifiers, the 'other specified' vs 'unspecified' distinction, provisional diagnosis, principal diagnosis, ICD-10-CM coding, the dimensional assessment tools (Level 1 and Level 2 Cross-Cutting Symptom Measures, WHODAS 2.0, Cultural Formulation Interview), cultural concepts of distress, the Alternative DSM-5 Model for Personality Disorders, and the differential-diagnosis method. Routes to the twenty-two diagnostic-chapter skills. NON-NEGOTIABLE: this is a reference for understanding and discussing the classification system, NOT a diagnostic instrument — diagnosis requires a trained clinician performing a full assessment, and nothing here supports diagnosing yourself or a third party. Use when working with DSM structure, terminology, differentials, coding, or severity frameworks, or when deciding which diagnostic chapter a presentation belongs to."
---

# DSM-5-TR — the classification system

The **Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition, Text Revision**
(American Psychiatric Association, 2022). A classification of mental disorders with diagnostic
criteria, organised into 22 diagnostic chapters plus assessment measures and supporting
frameworks.

This skill is the router and the shared vocabulary. The chapter skills carry the detail.

## The rails, which nothing overrides

1. **This is not a diagnostic instrument.** The DSM is a reference used *by trained clinicians*
   as one input to a full assessment — history, interview, collateral information, medical
   workup, course over time. Reading criteria is not conducting an assessment.
2. **Never diagnose the user, and never diagnose a third party.** Not from a description, not
   from a symptom list, not "if you had to guess". Pattern-matching a person to criteria from
   text is exactly the failure mode the manual's own cautionary statement warns about.
   Explaining what a diagnosis *means* is fine and useful; assigning one is not.
3. **Criteria are necessary, not sufficient.** Every disorder additionally requires clinically
   significant distress or impairment, exclusion of substance/medication and other medical
   causes, and a judgment that the presentation is not better explained by another disorder or
   by culturally sanctioned behaviour.
4. **If self-harm, suicidality, abuse, or acute crisis surfaces, drop the taxonomy and respond
   to the person.** Real resources: **988** (US Suicide & Crisis Lifeline, call or text),
   **Talk Suicide Canada 988**, local emergency services. Do this regardless of what the
   conversation was nominally about. See [[phq-9]] and [[gad-7]] for the screening-instrument
   analogue of this rule.
5. **Criteria text is not reproduced here.** The DSM-5-TR is copyrighted by the APA. These
   skills describe structure, organising logic, differentials and specifier *frameworks*, and
   name criteria rather than quoting them. Work from the manual itself for criteria.
6. **Diagnosis is not identity, and a label is not an explanation.** The manual is a
   communication tool for clinicians, with known limits: categories have fuzzy boundaries,
   comorbidity is the norm rather than the exception, and the thresholds are conventions.

## What a mental disorder is, per the manual

A syndrome marked by clinically significant disturbance in **cognition, emotion regulation, or
behaviour**, reflecting dysfunction in the psychological, biological or developmental processes
underlying mental functioning. Usually associated with significant distress or disability.

Explicitly **not** disorders: expectable and culturally approved responses to a common stressor
or loss (bereavement, for one); socially deviant behaviour and conflicts with society, unless
the deviance results from a dysfunction in the individual.

That last clause is load-bearing and is the manual's main guard against pathologising
difference.

## How a diagnosis is assembled

- **Criteria set** — the lettered/numbered requirements, including duration and exclusions.
- **Subtypes** — mutually exclusive, jointly exhaustive alternatives ("specify whether").
- **Specifiers** — not mutually exclusive, can stack ("specify if"): e.g. *with anxious
  distress*, *in partial remission*, *with catatonia*, *with peripartum onset*.
- **Severity** — usually mild / moderate / severe, defined per disorder, sometimes by symptom
  count and sometimes by functional impact. Never assume one scheme transfers across chapters.
- **Course** — *in partial remission*, *in full remission*, *recurrent*, *single episode*.
- **Principal diagnosis** — when more than one applies, the one chiefly responsible for the
  visit or admission. Listed first.
- **Provisional** — used when criteria are expected to be met once more information arrives, or
  when duration criteria aren't yet satisfiable.

### "Other specified" vs "unspecified"

Both are for presentations that cause significant distress or impairment but don't meet a full
criteria set. The difference is **why**:

- **Other specified** — the clinician *states the reason* ("other specified depressive disorder,
  depressive episode with insufficient symptoms").
- **Unspecified** — the clinician *doesn't specify*, typically because information is
  insufficient (an emergency presentation, say).

They are not a dustbin; they are how the system handles real presentations that don't fit, and
choosing between them is a deliberate act.

## Differential diagnosis, as a method

The manual's own sequence, worth following in order:

1. **Is it malingering or a factitious disorder?** Consider intentional production first, not
   last.
2. **Substance or medication?** Including intoxication, withdrawal, and medication side effects.
   This is the most commonly missed step.
3. **Another medical condition?** Thyroid, neurological, autoimmune, sleep apnea, and many more
   produce psychiatric presentations.
4. **Which disorder best accounts for the whole picture**, including course and age at onset.
5. **Is it a boundary case with no mental disorder** — an expectable reaction, a culturally
   sanctioned practice, a personality trait within range?

**Comorbidity is normal.** Two diagnoses is usually a better description than forcing one.

## Dimensional and cross-cutting assessment

The DSM-5 moved partway from purely categorical toward dimensional measurement:

- **Level 1 Cross-Cutting Symptom Measure** — a brief screen across 13 symptom domains
  (depression, anger, mania, anxiety, somatic symptoms, suicidal ideation, psychosis, sleep,
  memory, repetitive thoughts and behaviours, dissociation, personality functioning, substance
  use). Positive domains trigger **Level 2** measures for depth.
- **WHODAS 2.0** — disability across six domains (understanding/communicating, getting around,
  self-care, getting along, life activities, participation). Functioning is measured separately
  from symptoms, which is the point.
- **Severity measures** per disorder, where available.

## Culture, and why it is structural rather than decorative

- **Cultural Formulation Interview (CFI)** — 16 questions covering cultural definition of the
  problem, perceptions of cause and context, support-seeking, and the clinician-patient
  relationship, plus an informant version and supplementary modules.
- **Cultural concepts of distress** — three kinds: *syndromes* (recognisable clusters, e.g.
  ataque de nervios), *idioms of distress* (shared ways of talking about suffering, e.g.
  "nerves"), *causal explanations* (e.g. maladi dyab).
- **DSM-5-TR strengthened this throughout**, revising text on racism and discrimination as
  contributors to risk and presentation, and replacing "race" framing with more precise terms.

A criteria set applied without cultural context produces both false positives and false
negatives, and the manual says so.

## The 22 diagnostic chapters

Ordered as the manual orders them, which is roughly **developmental** — conditions typically
appearing early in life first, later-life conditions last. That ordering is itself information.

| Chapter | Skill |
|---|---|
| Neurodevelopmental Disorders | [[dsm-neurodevelopmental]] |
| Schizophrenia Spectrum and Other Psychotic Disorders | [[dsm-schizophrenia-spectrum]] |
| Bipolar and Related Disorders | [[dsm-bipolar]] |
| Depressive Disorders | [[dsm-depressive]] |
| Anxiety Disorders | [[dsm-anxiety]] |
| Obsessive-Compulsive and Related Disorders | [[dsm-ocd-related]] |
| Trauma- and Stressor-Related Disorders | [[dsm-trauma-stressor]] |
| Dissociative Disorders | [[dsm-dissociative]] |
| Somatic Symptom and Related Disorders | [[dsm-somatic-symptom]] |
| Feeding and Eating Disorders | [[dsm-feeding-eating]] |
| Elimination Disorders | [[dsm-elimination]] |
| Sleep-Wake Disorders | [[dsm-sleep-wake]] |
| Sexual Dysfunctions | [[dsm-sexual-dysfunctions]] |
| Gender Dysphoria | [[dsm-gender-dysphoria]] |
| Disruptive, Impulse-Control, and Conduct Disorders | [[dsm-disruptive-impulse-conduct]] |
| Substance-Related and Addictive Disorders | [[dsm-substance-related]] |
| Neurocognitive Disorders | [[dsm-neurocognitive]] |
| Personality Disorders | [[dsm-personality]] |
| Paraphilic Disorders | [[dsm-paraphilic]] |
| Other Mental Disorders and Additional Codes | [[dsm-other-mental]] |
| Medication-Induced Movement Disorders and Other Adverse Effects | [[dsm-medication-induced]] |
| Other Conditions That May Be a Focus of Clinical Attention | [[dsm-other-conditions]] |

**Adjacent chapters are adjacent for a reason.** The spectrum ordering means a disorder's
nearest differentials usually sit in the same or neighbouring chapter — bipolar between
psychotic and depressive disorders, OCD-related next to anxiety, trauma next to that.

## Coding

Diagnoses carry **ICD-10-CM** codes, because the DSM is the clinical reference and ICD is the
billing and statistical standard. Notes worth knowing:

- Many codes depend on the specifier chosen (ADHD's `F90.0` / `F90.1` / `F90.2` by presentation).
- Substance-related codes encode use-disorder severity *and* the induced condition together.
- Some conditions need an **additional code** (catatonia, the medical condition underlying a
  "due to another medical condition" diagnosis).
- Z-codes cover most of [[dsm-other-conditions]] — psychosocial and environmental problems.

## DSM-5-TR: what changed from DSM-5 (2013)

- **Prolonged grief disorder** added ([[dsm-trauma-stressor]]).
- **Unspecified mood disorder** restored, for presentations not yet separable into bipolar or
  depressive.
- **Symptom codes for suicidal behaviour and nonsuicidal self-injury**, codable independent of
  any disorder — a significant change for documentation.
- Text revised throughout by over 200 contributors; substantial revisions to prevalence, risk,
  culture, and sex/gender sections.
- Terminology: *intellectual developmental disorder*, and "desired gender" language revised in
  [[dsm-gender-dysphoria]].

## The Alternative Model for Personality Disorders

Section III carries a **dimensional** alternative: level of personality functioning (identity,
self-direction, empathy, intimacy) plus five pathological trait domains (negative affectivity,
detachment, antagonism, disinhibition, psychoticism). It coexists with the categorical ten in
Section II rather than replacing them. Detail in [[dsm-personality]].

## Anti-patterns

- Applying criteria to a person from a text description — the single thing this skill exists to
  prevent.
- Treating a criteria count as the diagnosis, skipping distress/impairment and the rule-outs.
- Skipping the substance/medication and medical-condition steps of the differential.
- Assuming a severity or specifier scheme carries across chapters.
- Using "unspecified" as a shrug when "other specified" with a stated reason is available.
- Reading a category as a natural kind with sharp edges.
- Ignoring culture, then reading a culturally normative practice as pathology.
- Quoting criteria verbatim from a copyrighted manual.

## Always-apply

1. **Not a diagnostic tool. Never diagnose a person** — explain the system instead.
2. **Criteria + distress/impairment + rule-outs**, in that order, always.
3. **Substance, medication, and medical causes get excluded before anything else.**
4. **Crisis content outranks the taxonomy.** 988, every time, immediately.
5. **Culture is part of the assessment**, not an afterthought.
6. **Comorbidity is the norm** — don't force one label.
7. **Name criteria, don't reproduce them.**

## Related

- [[phq-9]] / [[gad-7]] — screening instruments with the same screen-is-not-diagnosis rail.
- Source: *Diagnostic and Statistical Manual of Mental Disorders*, Fifth Edition, Text Revision
  (DSM-5-TR), American Psychiatric Association, 2022. Criteria not reproduced; consult the
  manual.
