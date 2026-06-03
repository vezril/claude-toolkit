---
name: ux-design
description: UX design heuristics from psychology — designing intuitive, usable products and interfaces, distilled from Jon Yablonski's *Laws of UX*. Covers the catalog of UX "laws" (Jakob's, Fitts's, Hick's, Miller's, Postel's, Tesler's, Doherty Threshold, Peak-End Rule, Aesthetic-Usability Effect, Von Restorff, Serial Position, Zeigarnik, Goal-Gradient, and the Gestalt grouping principles), how to apply them to UI/interaction decisions, and the meta-themes (cognitive load, the power of defaults, designing with psychology responsibly). Use when designing or reviewing a UI/interaction, deciding layout/affordances/choice architecture, reducing cognitive load, improving usability or perceived performance, or making product-design trade-offs — pairs with the SwiftUI / apple-dev skills for building the UI. Design heuristics, not a development framework.
---

# UX Design (Laws of UX)

Heuristics grounded in cognitive psychology for designing **intuitive, usable** products and interfaces, from Jon Yablonski's *Laws of UX*. These are **mental models and rules of thumb** to inform UI/interaction decisions — they tell you *why* a design feels easy or hard and *what* to adjust. They pair directly with the building skills: design with these, implement with [[swiftui-ui-patterns]] / [[apple-dev]] (or any UI stack).

Cross-links: [[apple-dev]], [[swiftui-ui-patterns]], [[swiftui-view-refactor]] (building the UI); [[clean-code]] / [[software-design]] (Tesler's "conservation of complexity" mirrors deep-modules thinking); [[swiftui-performance-audit]] (the Doherty Threshold ↔ responsiveness).

## The meta-themes (read these first)

- **Reduce cognitive load.** Working memory is tiny and attention is scarce; every choice, field, and bit of jargon costs the user. Remove, defer, chunk, and default. This idea unifies most of the laws.
- **Leverage prior knowledge.** Users spend most of their time on *other* products; meet their existing mental models instead of inventing novel patterns (Jakob's Law).
- **The power of defaults.** Most users never change a default — so defaults are a profound design decision; choose them to serve the user, ethically.
- **Design with psychology responsibly.** These laws can manipulate as well as help; Yablonski stresses using them to *respect* users (avoid dark patterns) — design for the user's goals, not against them.

## The laws (apply these)

Full descriptions and examples are in **`references/ux-laws-catalog.md`**. The high-leverage ones:

- **Jakob's Law** — users expect your product to work like the others they already know; honor conventions, innovate sparingly and only where it adds value.
- **Fitts's Law** — time to acquire a target depends on its **size** and **distance**; make important/frequent targets **large and close** (and exploit screen edges/corners, which are "infinitely large").
- **Hick's Law** — decision time grows with the **number and complexity of choices**; reduce options, break complex flows into steps, use progressive disclosure, highlight the recommended path.
- **Miller's Law** — people hold only ~**7±2** chunks in working memory; **chunk** content (phone numbers, menus) rather than relying on a magic number.
- **Tesler's Law (Conservation of Complexity)** — every system has **irreducible complexity** that must live *somewhere*; don't push it onto the user — absorb it in the design/system (mirrors "pull complexity downward" in [[software-design]]).
- **Doherty Threshold** — keep system response under **~400 ms** to keep users engaged and productive; use perceived-performance tricks (skeletons, optimistic UI, progress) when you can't (ties to [[swiftui-performance-audit]]).
- **Aesthetic-Usability Effect** — users perceive attractive designs as **more usable** and are more forgiving of minor issues; visual quality is a usability lever (but not a substitute for real usability).
- **Peak-End Rule** — people judge an experience by its **peak** and its **end**, not the average; design memorable highs and strong endings (and rescue failure states gracefully).
- **Von Restorff (Isolation) Effect** — the item that **differs** is remembered; make the key action/element visually distinct (and don't make non-actions look like the distinct one).
- **Serial Position Effect** — first and last items are best remembered; place key items at the **start and end** of lists/navigation.
- **Zeigarnik Effect** — people remember **incomplete** tasks; use progress indicators and "completeness" cues to drive task completion.
- **Goal-Gradient Effect** — motivation **increases as the goal nears**; show progress and reduce perceived remaining effort (the pre-filled loyalty-stamp trick).
- **Gestalt principles** (Proximity, Common Region, Similarity, Continuity, Closure, Prägnanz, Uniform Connectedness, Figure/Ground) — the brain groups visual elements; use **spacing, containers, and similarity** to convey structure *before* reaching for borders/lines.
- **Postel's Law** — be **liberal in what you accept** (forgiving inputs, flexible formats) and **conservative in what you do/return**; build robust, accommodating interfaces.

## How to apply (decision lens)

When designing or reviewing a screen/flow, walk the questions: Does it match users' **existing mental models** (Jakob)? Are the **important targets big and reachable** (Fitts)? Have we **minimized choices** at each step (Hick) and **chunked** what's left (Miller)? Where is the **irreducible complexity** living — user or system (Tesler)? Is it **fast enough** or do we fake it (Doherty)? Are the **peak and end** good (Peak-End)? Is the **primary action distinct** (Von Restorff)? Does **grouping/spacing** communicate structure (Gestalt)? Are **defaults** serving the user? Pick the one or two laws that bite for *this* decision — they're heuristics, not a checklist to satisfy mechanically.

## Always-apply notes

- **Reduce, default, chunk, and follow convention** before adding anything; the strongest UX move is usually *removal*.
- Treat **perceived** performance and the **peak/end** of a flow as first-class — they shape satisfaction more than averages.
- Use these to **help, not manipulate** — no dark patterns; align with the user's goals.
- These are **design** heuristics; implement the resulting UI with [[swiftui-ui-patterns]] / [[apple-dev]] (or your stack) and verify responsiveness with [[swiftui-performance-audit]].

## How to use this skill

- **`references/ux-laws-catalog.md`** — the full catalog: each law's definition, the psychology behind it, concrete UI applications, and caveats.

## Related

- [[apple-dev]], [[swiftui-ui-patterns]], [[swiftui-view-refactor]] — building the interfaces these heuristics inform.
- [[swiftui-performance-audit]] — responsiveness (Doherty Threshold).
- [[software-design]] — Tesler's conservation of complexity ≈ "pull complexity downward" / deep modules; [[clean-code]].
- Source: *Laws of UX: Using Psychology to Design Better Products & Services*, Jon Yablonski (lawsofux.com).
