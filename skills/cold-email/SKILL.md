---
name: cold-email
description: Write short cold emails that earn replies using AIDA, PAS, or BAB frameworks — 50-125 words, personalized first line, one specific ask, honest subject lines. Use when drafting outreach to someone with no prior relationship (sales, partnerships, recruiting, intros).
user-invocable: true
argument-hint: "[target] [goal] [context/personalization]"
---

# Write a Cold Email

Draft a cold email that respects the reader's time and earns a reply.

## Input

Parse $ARGUMENTS for:
- **Target** — who they're emailing (role, company, industry)
- **Goal** — the one thing they want (meeting, intro, feedback, sale)
- **Context** — real personalization hooks (mutual connection, their recent work, a specific pain point)

If any piece is missing, ask for it before drafting. If the user has no genuine personalization hook, say so and help find one — don't invent it.

## Pick One Framework

- **AIDA** (Attention → Interest → Desire → Action): relevance hook, value, proof, one CTA. Default choice.
- **PAS** (Problem → Agitate → Solution): name their problem, make the cost concrete, position the fix. Best when the pain is sharp and provable.
- **BAB** (Before → After → Bridge): current state, better state, how to get there. Best for aspirational/outcome pitches.

## Hard Rules

1. **50-125 words.** Shorter wins. Enforce it structurally: 2-3 short paragraphs of at most 2 sentences each, plus the CTA line — respect that shape and the cap takes care of itself. Count the body words before finalizing; over 125, cut.
2. **Subject: 3-5 words**, lowercase, plainly related to the body — never bait-and-switch.
3. **First line is about them**, referencing something specific and true. No "I hope this finds you well", no "My name is...".
4. **One CTA**, concrete and small ("worth a 15-min call Thursday?" — not "let me know your thoughts").
5. **Under 30 seconds to read.** Short paragraphs, mobile-friendly.
6. **Honest by construction:**
   - No fabricated familiarity ("loved your talk" only if they actually gave one the user can name).
   - No fake urgency or invented scarcity.
   - Sender identity stays real — never impersonate or imply a relationship that doesn't exist.
   - If this is bulk/commercial outreach, remind the user that spam laws (CAN-SPAM, CASL, GDPR) require a real sender address and a working opt-out.

## What Makes It Land

A specific reason for emailing *this* person, evidence of two minutes of real research, a clear "what's in it for them", and zero hype words.

## Output Format

Reply in exactly this order — the first line of your reply is the Subject line, and the Framework/Personalization/Word count notes come after the email, never before:

```
Subject: [subject line]

[Email body]

[First name only]
```

**Framework:** [which and why]
**Personalization angle:** [what was used]
**Word count:** [N]
