# Facilitating an EventStorming workshop

How to actually run a session, from *Introducing EventStorming*. A big chunk of the book is facilitation, because the technique lives or dies on group dynamics. Faithful to Brandolini.

## Contents

1. Preparation
2. The Big Picture workshop phases
3. Aftermath: when to stop, capturing output
4. Facilitation patterns
5. Anti-patterns
6. Remote EventStorming

---

## 1. Preparation

- **Invite the right people.** The single biggest determinant of value. You need the people who *know* different parts of the domain and the people with *questions* — a diverse mix across silos (business + dev + ops + whoever holds the messy edge cases). Homogeneous rooms learn nothing new.
- **Provide an unlimited modeling surface.** A long roll of paper along a wall, not a whiteboard. The cramped-whiteboard reflex silently caps the model; remove the space constraint so the timeline can sprawl.
- **Room setup.** Clear the chairs away from the wall — people must *stand* and move. A big table in the center is an anti-pattern (see below). Plenty of stickies in the legend colors and one marker per person.
- **Manage invitations** deliberately, especially in corporate settings: get the right sponsors, set expectations, and make attendance meaningful rather than mandatory-and-checked-out.

## 2. The Big Picture workshop phases

1. **Kick-off.** State the scope and the one rule that gets things moving: write **domain events** (past tense) on orange stickies and put them on the wall, roughly left-to-right in time. Don't over-explain — *do first, explain later*.
2. **Chaotic Exploration.** Everyone writes events at once, in parallel, no coordination. Embrace the mess; the point is to externalize knowledge fast. Expect duplicates, gaps, disagreement.
3. **Enforcing the Timeline.** Now bring order: sequence the events, merge duplicates, resolve contradictions, and use a sorting strategy (pivotal events, swimlanes — see notation reference). Disagreements here are gold; mark them as **hot spots**.
4. **People & Systems.** Enrich the timeline: add **actors** who trigger key moments, **external systems** that emit/consume events, and the **read models** people rely on to decide.
5. **Problems & Opportunities.** Sweep for pain: add **hot spots** (problems, risks, open questions) and opportunities. This is often where the real payoff surfaces.
6. **Pick your problem.** Decide collectively where the energy is — which hot spot or area justifies going deeper (e.g. into a Design-Level session).

## 3. Aftermath

- **When to stop?** When the group's energy drops, when the remaining detail isn't worth the room's time, or when you've achieved the shared understanding you came for. Don't grind a workshop into the ground.
- **How do we know we did a good job?** New shared understanding, surfaced hot spots, and emerging structure (boundaries) — not a pretty artifact.
- **Capture the output** before tearing down: photograph the whole wall (and sections) systematically; the photos plus a transcription of events/hot spots are the durable record. Note the **emerging structure** (clusters that hint at bounded contexts) and the chosen hot spot for follow-up.

## 4. Facilitation patterns

A selection from the book's catalog — moves that keep a session productive:

- **Unlimited Modeling Surface / Add More Space** — never let the wall fill up; extend it.
- **Visible Legend** — keep the color key posted so notation stays shared.
- **Do First, Explain Later** — start people writing events before a long theory lecture.
- **Keep Your Mouth Shut** — the facilitator's hardest discipline: let the group think and argue; don't supply answers.
- **Guess First / The Right To Be Wrong** — encourage guesses; make being wrong safe and normal (nobody likes to look stupid, especially in front of "the big guys").
- **One Person One Marker / Make Some Noise** — keep everyone active and engaged, not spectating.
- **Mark Hot Spots** — capture every disagreement/question loudly instead of resolving or burying it.
- **Start from the Center / from the Extremes / Reverse Narrative** — ways to seed a stuck timeline (begin at a pivotal middle event, at the ends, or walk it backwards).
- **Manage Energy** — read the room; break before it flags. **Go Personal**, defuse the **Alpha-male** dominating the room, and watch body language.
- **Conquer First, Divide Later** — get a whole rough picture before partitioning into detail.

## 5. Anti-patterns

Things that quietly kill a workshop:

- **Ask Questions First** — opening with analysis/Q&A instead of having people put events up; stalls momentum.
- **Big Table at the Center of the Room** — anchors people in chairs and kills the standing, moving dynamic.
- **Committee / Follow the Leader / The Godfather / Single Alpha-male** — letting a hierarchy or one loud voice drive, so quieter domain knowledge never surfaces.
- **Dungeon Master** — the facilitator steering the *content* (what the model "should" say) rather than the *process*.
- **Human Bottleneck / Karaoke Singer** — one person (often a scribe) funneling all stickies, instead of parallel contribution.
- **The Spoiler / Start from the Beginning** — forcing a strict chronological start can stall; the Spoiler reveals conclusions too early and shuts down exploration.

## 6. Remote EventStorming

It's possible but **downgrade expectations**: you lose the spatial bandwidth, the standing-and-moving energy, and the easy parallelism. Use a large virtual canvas (e.g. an online whiteboard), keep groups smaller, be more explicit about turn-taking and the legend, and budget more time. The co-located, physical version remains the gold standard.
