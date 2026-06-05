---
name: game-production
description: The production and business of shipping games — scoping, milestones, avoiding crunch/scope-creep, validating ideas cheaply, and indie launch/marketing — distilled from Schreier's *Blood, Sweat, and Pixels* and *Press Reset*, Hill-Whittall's *The Indie Game Developer Handbook*, Ries' *The Lean Startup*, and Eyal's *Hooked* (with an ethics critique). Covers project realities (every game's development is a struggle; scope creep and crunch are the chronic failures), scoping & milestones (vertical slice, MVP, cut to ship, "find the fun then stop adding"), the build-measure-learn / MVP loop adapted to games, the indie business (funding, budgeting, platforms/storefronts, pricing, marketing on a budget, wishlists/community, launch and post-launch), team/career sustainability (anti-crunch, the industry's volatility, layoffs/closures), and engagement/monetization ethics (the Hooked model and where habit-forming design becomes a dark pattern). Use when scoping a game, planning milestones, deciding what to cut, validating an idea, planning a launch/marketing, pricing, or weighing monetization ethics. Pairs with game-development (the lifecycle), game-design, and ux-design (dark-patterns ethics).
---

# Game Production

The **production discipline and business** of actually **shipping** a game — the part that kills more games than bad code. From **Jason Schreier's *Blood, Sweat, and Pixels* & *Press Reset*** (how games really get made and unmade), **Richard Hill-Whittall's *The Indie Game Developer Handbook***, **Eric Ries' *The Lean Startup***, and **Nir Eyal's *Hooked*** (covered with an ethics critique). It's the "scope it and ship it" layer of the [[game-development]] lifecycle.

Cross-links: [[game-development]] (the lifecycle this operates within), [[game-design]] (what to build/cut), [[ux-design]] (shared dark-patterns ethics), [[devops]] / [[site-reliability-engineering]] (live-game ops).

## The brutal truth (Blood, Sweat, and Pixels)

Schreier's reporting on dozens of shipped games yields one lesson: **every game's development is improbable and a struggle.** Common threads — constant **scope creep**, **crunch**, late pivots, technical disasters, and the near-miracle of shipping at all. Practical takeaways: assume things will slip, **scope smaller than you think**, prototype to de-risk early, and treat crunch as a **failure of planning, not a strategy**. *Press Reset* adds the industry's volatility (studio closures, layoffs) — build career and financial resilience; don't bet everything on one unscoped dream project.

## Scoping & milestones (the core skill)

The #1 cause of unfinished games is **over-scoping**. Discipline:
- **Vertical slice first** — one polished slice proves quality & feel before you commit to volume ([[game-development]]).
- **MVP / find-the-fun-then-stop-adding** — define the smallest game that's actually fun and ship *that*; feature creep is the enemy.
- **Cut to ship** — maintain a ruthless priority list (must/should/could); when time runs out, cut features, not quality of what remains. "A shipped B+ beats an unshipped A+."
- **Milestones** — concept → prototype → vertical slice → alpha (feature-complete) → beta (content-complete) → gold/release; gate each on a playtest. Buffer for the "last 10%" that always takes 50% of the time.
- **Realistic estimates** — solo/indie scope to weeks-months per feature; pad heavily; track velocity.

## Lean / build-measure-learn for games

Ries' loop, adapted: **build** the cheapest experiment (prototype/demo) → **measure** with real players (playtests, wishlist conversion, demo retention) → **learn** and pivot or persevere. Validate that the game is fun *and* that people want it **before** full production. The game-dev analog: the prototype *is* the MVP; the playtest *is* the measurement ([[game-development]]'s find-the-fun gate). Fail cheap, fail early.

## The indie business

- **Funding/budget** — self-funded, savings/runway, publishers (advance vs control/cut), grants, crowdfunding, early access. Know your runway; budget art/audio/marketing, not just dev time.
- **Platforms & storefronts** — Steam (the wishlist economy), itch.io, consoles (cert process), mobile (F2P dynamics). Each has fees (~30%), rules, and audiences.
- **Pricing** — premium vs free-to-play vs DLC; regional pricing; discounts/sales cadence.
- **Marketing on a budget** — start **early** (a Steam page + wishlists from day one), a trailer, a demo (Next Fest), devlogs/social, press/streamer outreach, community (Discord). Visibility, not the game alone, decides indie outcomes. Wishlists drive the launch algorithm.
- **Launch & post-launch** — launch is a beginning: day-one patch, reviews, updates, community management, possibly live-ops ([[devops]]/[[site-reliability-engineering]] for online games).

## Team & career sustainability

- **Anti-crunch** — sustainable pace ships better games and keeps people; crunch is a planning/scope failure. (Echoes [[devops]]/[[site-reliability-engineering]] on toil & burnout.)
- **Roles** even for small teams (design/code/art/audio/production) — the [[game-development]] disciplines; solo devs wear all hats (lean on the studio agents).
- **Resilience** (*Press Reset*) — the industry churns; keep skills broad, finances buffered, scope humane.

## Engagement & monetization ethics (Hooked — with a critique)

*Hooked* describes the **Hook Model** — Trigger → Action → Variable Reward → Investment — for building habit-forming products. **Capture it with the ethics caveat:** in games this shades directly into **dark patterns** — compulsion loops, manipulative variable-reward (loot boxes/gacha), fake scarcity/FOMO, pay-to-win, predatory whale-targeting monetization. The stance (shared with [[ux-design]] and [[game-design]]): design for the player's **genuine enjoyment and respect**, not compulsion or extraction. Use engagement understanding to make games *better and fairer*, not to exploit. Be especially careful with minors and gambling-like mechanics (loot boxes are regulated/banned in some jurisdictions).

## Anti-patterns

- **Over-scoping** / feature creep — the chronic game-killer; not cutting to ship.
- **Crunch as a plan** instead of fixing scope/schedule; ignoring the "last 10%" tax.
- Building the whole game before a **vertical slice / playtest** proves it's fun and wanted (skipping validation).
- **Marketing late** (no Steam page/wishlists until launch) — visibility is built over months.
- Betting everything on one giant unscoped dream project (no runway/resilience — *Press Reset*).
- **Predatory monetization** / dark patterns (loot boxes, manipulative FOMO, pay-to-win), especially targeting minors.
- Treating launch as the finish line (no post-launch plan).

## Always-apply

1. **Scope ruthlessly**; build a **vertical slice**, define an **MVP**, and **cut to ship** (B+ shipped beats A+ unshipped).
2. **Validate cheaply** (prototype + playtest + wishlists) before full production — build-measure-learn.
3. **Plan against crunch**; buffer the last 10%; gate milestones on playtests.
4. **Market early** (page/wishlists/demo/community); treat launch as a start, plan post-launch.
5. Monetize **ethically** — design for enjoyment, not compulsion; avoid dark patterns (esp. with minors). ([[ux-design]])

## Related

- [[game-development]] — the lifecycle/milestones this manages; [[game-design]] — what to build and cut.
- [[ux-design]] — shared dark-patterns ethics; [[devops]] / [[site-reliability-engineering]] — live-game ops & anti-toil/burnout.
- Sources: *Blood, Sweat, and Pixels* & *Press Reset* (Jason Schreier); *The Indie Game Developer Handbook* (Richard Hill-Whittall); *The Lean Startup* (Eric Ries); *Hooked* (Nir Eyal — used with an ethics critique).
