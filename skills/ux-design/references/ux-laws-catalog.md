# The Laws of UX — catalog

From Jon Yablonski's *Laws of UX* (lawsofux.com). Each law: what it says, the psychology, how to apply it, and caveats. Group by theme.

## Heuristics (interaction & decision)

**Jakob's Law** — *Users spend most of their time on other sites/apps, so they prefer yours to work the same way.* Honor established conventions (nav placement, icons, gestures); reduce the learning cost. Innovate only where it clearly helps, and ease transitions when you must change. Caveat: convention ≠ stagnation, but novelty has a usability tax.

**Fitts's Law** — *Time to acquire a target is a function of the distance to and size of the target.* Make important/frequent controls **large** and **near** the user's likely pointer/thumb position; group related actions; exploit edges and corners (effectively infinite size). Touch: respect minimum tap-target sizes. Caveat: don't make destructive actions huge and adjacent to common ones.

**Hick's Law** — *Decision time increases with the number and complexity of choices.* Minimize options; break complex tasks into steps (progressive disclosure/wizards); categorize; recommend a default path; avoid overwhelming onboarding. Caveat: don't oversimplify to the point of hiding needed options; abstraction must not become obscurity.

**Miller's Law** — *The average person can hold about 7 (±2) items in working memory.* **Chunk** information (group digits, limit menu items per group); don't use "7" as a hard rule — the real lesson is chunking and not overloading memory. Let the interface hold state so users don't have to.

**Tesler's Law (Conservation of Complexity)** — *Every application has an inherent, irreducible amount of complexity; the only question is who deals with it.* Absorb complexity into the **system/design** rather than dumping it on the user (smart defaults, inference, automation). Mirrors [[software-design]]'s "pull complexity downward." Caveat: don't hide complexity the user legitimately needs to control.

**Postel's Law (Robustness Principle)** — *Be liberal in what you accept, conservative in what you send.* Accept varied/imperfect input gracefully (flexible formats, forgiving parsing, sensible error recovery); produce predictable, well-formed output. Builds resilient, humane interfaces (accept phone numbers with or without dashes, etc.).

## Performance & memory

**Doherty Threshold** — *Productivity soars when system and user interact at a pace (<400 ms) where neither waits on the other.* Keep responses under ~400 ms; when you can't, use **perceived-performance** techniques: skeleton screens, optimistic UI, progress/feedback, preloading. Ties to [[swiftui-performance-audit]].

**Peak-End Rule** — *People judge an experience largely on its peak (most intense point) and its end, not the sum/average.* Design deliberate **delight peaks** and a strong **ending**; pay special attention to failure/empty states and the end of flows (checkout confirmation, task completion). A rough patch is forgiven if the peak and end are good.

**Zeigarnik Effect** — *People remember uncompleted or interrupted tasks better than completed ones.* Use **progress indicators**, checklists, and visible "incompleteness" to motivate completion (profile completion meters, onboarding checklists).

**Goal-Gradient Effect** — *Motivation increases as one approaches a goal.* Show progress toward the goal and reduce perceived remaining effort; **artificial advancement** helps (the loyalty card pre-stamped with 2 of 10 outperforms a fresh 8-of-8). Use to encourage completion, not to trap.

**Serial Position Effect** — *Items at the beginning (primacy) and end (recency) of a series are most memorable; the middle is weakest.* Put the **most important** nav/list items **first and last**; don't bury key actions in the middle.

**Von Restorff Effect (Isolation Effect)** — *When multiple similar items are present, the one that differs is most likely to be remembered.* Make the **primary action / key info** visually distinct (color, size, weight) — but only one focal point per view, and don't rely on color alone (accessibility).

## Gestalt grouping principles (visual perception)

The brain organizes visual elements into groups; use these to convey structure with the *least* visual noise (prefer spacing/grouping over borders/lines):
- **Proximity** — elements close together are perceived as a group; spacing communicates relationships.
- **Common Region** — elements within a shared boundary/container are perceived as grouped (cards).
- **Similarity** — elements that look alike (color/shape/size) are seen as related; consistent styling implies same function.
- **Continuity** — the eye follows lines/curves; align elements to imply flow/order.
- **Closure** — the mind completes incomplete shapes (logos, icons); you can imply form without drawing it fully.
- **Prägnanz (Law of Simplicity / Good Figure)** — people interpret ambiguous images in the simplest form; keep visuals simple.
- **Uniform Connectedness** — elements visually connected (by lines, enclosure, or shared background) are perceived as more related than those merely near each other.
- **Figure/Ground** — the eye separates a focal "figure" from the "ground"; use contrast/layering (modals, blur) to direct attention.

## Meta-principles & ethics

- **Cognitive load** — minimize intrinsic + extraneous load; offload memory to the interface; one primary action per screen.
- **Power of defaults** — most users keep defaults; choose them to benefit the user (opt-in for things that cost the user, not opt-out).
- **Responsible design** — these laws can be weaponized into **dark patterns** (manipulative goal-gradient, fake scarcity, confusing defaults). Yablonski's stance: apply them to *serve* users' goals and respect their autonomy. Design ethically.

## Applying the catalog

Don't run the whole list every time — for a given decision, identify the one or two laws that actually bite (a long form → Hick + Miller + progressive disclosure; a slow action → Doherty + perceived performance; a primary CTA → Fitts + Von Restorff; a layout → Gestalt). Pair with the build skills ([[swiftui-ui-patterns]], [[apple-dev]]) to implement, and remember Tesler/complexity ties back to [[software-design]].
