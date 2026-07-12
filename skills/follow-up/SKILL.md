---
name: follow-up
description: Write follow-up emails that re-engage a non-responder without nagging — bump, value-add, or breakup patterns matched to the follow-up number. Each one shorter than the last, always with a new angle. Use when a sent email got no reply and it's time to follow up.
user-invocable: true
argument-hint: "[original email context] [days since sent] [follow-up number 1-3]"
---

# Write a Follow-Up Email

Draft a follow-up that adds a reason to reply instead of just asking again.

## Input

Parse $ARGUMENTS for:
- **Original email** or a summary of the first outreach
- **Days since sent**
- **Follow-up number** (1, 2, or 3)
- **New context** (optional) — news, trigger event, fresh value to offer

If the original context is missing, ask for the key points before drafting. If this would be follow-up #4+, advise stopping — persistence past a breakup email reads as spam.

## Pattern by Follow-Up Number

| # | Timing | Pattern | Shape |
|---|--------|---------|-------|
| 1 | 3-5 days | **The Bump** — assume busy, not uninterested | Friendly nudge + one new detail or angle. Shortest possible. |
| 2 | 7-10 days | **The Value-Add** — earn the reply | Share something genuinely useful (insight, resource, relevant example) tied to their problem. Reframe the value prop. |
| 3 | 14+ days | **The Breakup** — permission-based close | Give an easy out ("if the timing's wrong, no worries — I'll close this out"). Real close, not a guilt lever. |

## Hard Rules

1. **30-75 words**, and shorter than the previous email.
2. **New angle every time** — never resend or paraphrase the original.
3. **Brief callback** to the first email so they have context.
4. **One CTA**, same or smaller than the original ask.
5. **No guilt, no neediness:** cut "I haven't heard back", "I'm sure you're busy but...", "just checking in".
6. **The breakup is honest.** If the email says you'll stop reaching out, the user should actually stop. Don't draft a fake-breakup designed to be followed by more emails.

## What NOT to Write

- "I wanted to follow up on my last email" (dead opener)
- Passive-aggressive readings of their silence
- Multiple CTAs or a new, bigger ask
- Manufactured urgency or fake deadlines

## Output Format

```
Subject: Re: [original subject]  — or a new 3-5 word subject

[Email body]

[First name]
```

**Pattern:** [bump / value-add / breakup]
**What's new vs. the original:** [one line]
**Word count:** [N]
