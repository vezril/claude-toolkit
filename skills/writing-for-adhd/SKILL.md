---
name: writing-for-adhd
description: "How to write text a reader with ADHD will actually read and act on — grounded in the working-memory literature (Martinussen et al. 2005 meta-analysis; Cowan's ~4-chunk capacity), cognitive load theory (Sweller; split-attention, expertise reversal), and measured reading-behaviour research (Nielsen Norman Group: concise text +58%, scannable +47%, objective language +27%, combined +124% usability; the F-shaped scanning pattern). Covers the one mechanism that explains every rule (working memory is impaired, comprehension is not), the hard limits on list length and open questions, front-loading and why position determines what gets read at all, externalising to files instead of chat, one-decision-per-message, delay discounting and why a concrete next action beats a complete plan, emotional dysregulation and how to open with the win rather than the caveat, and the expertise-reversal trap of over-explaining to a domain expert. Use when writing anything to a reader who has told you they have ADHD, or who has said a reply was too long, didn't read it, or asked what to do next — and when reporting status, findings, or finished work to them."
---

# Writing for a reader with ADHD

## The one mechanism

**Working memory is impaired. Comprehension and intelligence are not.** Long-term memory is
largely intact in ADHD; recall failures trace back to working memory
(Martinussen et al., 2005, meta-analysis of 26 studies: verbal storage *d* = 0.47, verbal
central executive *d* = 0.43, spatial storage *d* = 0.85, spatial central executive *d* = 1.06).
Baseline capacity is already only about **four chunks** (Cowan, 2001 — not Miller's 7±2), and
ADHD reduces it further.

So the failure is never *"they couldn't follow it."* It is **"they couldn't hold it."** Every
rule below is a way of not asking the reader to hold something.

Spatial working memory is the *most* impaired component, which is why a reader loses the shape
of a long structured document faster than they lose the sentences in it. Nested sections are
harder than prose, not easier.

## Don't make them hold anything

- **Name the referent.** Never "as mentioned above", "the earlier issue", "that file". Say which.
  A back-reference is a demand to reload context that is no longer in memory.
- **Three items, four at the outside.** Past that, a list is a memory test. If there are nine
  things, give the one that matters and put the rest in a file.
- **One decision per message.** Each open question is a held item. Two questions usually gets
  one answered and one silently dropped — and you won't know which.
- **No forward references.** "More on this below" asks them to carry a placeholder.
- **Resolve, don't enumerate.** Don't list options you've already ruled out. Give the
  recommendation and the one-clause reason.

## Position decides what is read at all

79% of readers scan rather than read; 16% read word by word (Nielsen Norman Group). Unformatted
text triggers **F-pattern scanning** — a sweep across the top, a shorter sweep lower, then a
vertical run down the left edge. Readers then skip content *because of where it sits*, and
**they do not notice what they missed.**

The F-pattern fires when three things coincide: the text is a wall, the reader wants to be
efficient, and they're not gripped. That is exactly a status update.

So:

- **Front-load the answer.** First sentence = what happened or what to do. Not the approach, not
  the context, not the journey.
- **First two words of any heading carry it.** Assume the rest of the line is unread.
- **Bold the thing they must not miss** — one per message, or the emphasis is noise.
- **Cut, don't compress.** Measured against promotional prose: concise text was **58%** better,
  scannable layout **47%**, objective non-boastful language **27%**, all three together
  **124%**.

## Chat is a stream; files are addressable

Chat cannot be re-found and has no state. A decision, a list, or a plan written in chat is lost
by tomorrow — not through inattention, but because nothing points to it.

- **Detail goes in an artifact**: a file, a PR body, a tracker, an iteration log.
- **Chat gets one line pointing at it.** "In `TODO.md` §4" beats repeating §4.
- Writing it twice is worse than once: now there are two versions and one is stale.

This is Barkley's externalising principle in practice — if working memory can't hold it, it has
to exist outside the head, somewhere with an address.

## Make the next action concrete

ADHD involves **delay discounting**: immediate, specific rewards dominate distant ones. A
complete prioritised plan is a distant reward. One concrete next action is an immediate one.

- **"Next: X"** — one thing, startable now.
- A plan with six ranked items produces no action. Name the first; the plan lives in the file.
- Never end on an open-ended "what would you like to do?" after a wall of text. That's two
  demands: reconstruct everything, then decide.

## Tone, because it changes whether they keep reading

Emotional dysregulation and mood lability are common in ADHD, and roughly half of people with
ADHD experience social rejection versus 10–15% otherwise. Length and framing both read as
affect.

- **Open with what's done and working.** A reply that opens on problems reads as "this is bad
  news" before a word is parsed.
- **Don't bury a win under caveats.** State it, then one clause of caveat.
- **A wall of text reads as reproach** regardless of content. Brevity is kindness here, not
  terseness.
- Stay factual rather than reassuring. Objective language measured **27%** better than
  promotional language — hedging and cheerleading both cost comprehension.

## Don't over-scaffold an expert

The **expertise reversal effect** (Kalyuga, Ayres, Chandler & Sweller, 2003): support that helps
a novice actively *hurts* an expert, because reconciling an explanation against knowledge you
already have is extra load.

So with a domain expert — which is the usual case here — explaining what they already know is
not thoroughness, it's extraneous load. Skip the background. Give the delta.

Related: the **split-attention effect** (Chandler & Sweller, 1992) — making a reader integrate
two separated sources costs them. Put the number next to the claim it supports, not in a table
three paragraphs away.

## Anti-patterns

- A multi-section summary of work they can read in the PR body.
- Restating the task before answering it.
- Tables used for two rows of data.
- Three caveats before the result.
- "Let me know if you'd like me to…" × 4.
- A recap at the end of a message that was already short.
- Hedging a verified fact into vagueness — precision is not length.

## Always-apply

1. **Answer in the first sentence.** Everything else is optional and will probably go unread.
2. **≤3 items. One decision. One bolded thing.**
3. **Name every referent.** No "the above", no "that thing".
4. **Detail to a file; one line in chat pointing at it.**
5. **End with one concrete next action**, not a menu.
6. **Open with the win, caveat in a clause.**
7. **Skip what they already know.** Give the delta.

Target length for a status reply: **2–4 sentences.** If it needs more, that's a sign it needs a
file instead.

## Sources

- Martinussen, Hayden, Hogg-Johnson & Tannock (2005), *J Am Acad Child Adolesc Psychiatry*
  44(4) — working-memory meta-analysis, 26 studies.
- Cowan (2001), *Behav Brain Sci* 24(1) — capacity ≈ 4 chunks.
- Sweller, Chandler, Kalyuga & Ayres — cognitive load theory: extraneous load, split-attention,
  expertise reversal.
- Nielsen Norman Group — measured usability of concise/scannable/objective text; F-shaped
  scanning pattern.
- Kooij et al. (2019), European Consensus Statement — mind-wandering in adult ADHD.
