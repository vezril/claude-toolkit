# 2009 Toyota Matrix (XR 2.4L) — recalls & known issues

The recall text below is quoted from the US **NHTSA** recalls API (`api.nhtsa.gov`,
public-domain, retrieved **2026-09**). **For a Canadian car, NHTSA is the *supplementary*
source — your primary authority is Transport Canada**, whose campaign numbers differ. Always
confirm status **by VIN**, because a listed model can already be remedied on your unit.

## ⚠️ Check your VIN first — two databases, because you're in Canada

- **Transport Canada (primary for a Canadian car):** <https://recalls-rappels.canada.ca> → Motor Vehicle → enter make/model or VIN. This is the authoritative list for a Quebec-registered Matrix.
- **NHTSA (US, supplementary):** <https://www.nhtsa.gov/recalls> by VIN — useful, but some US campaigns are **region-limited** and won't map cleanly to a Canadian car (see the Takata note below).
- **Toyota Canada:** recall lookup on toyota.ca, or a Toyota dealer with your VIN.
- Recall remedies are **free**, regardless of age or ownership history.

## Recall 1 — Takata passenger airbag inflator ⚠️ (the serious one — but read the zone caveat)

| | |
|---|---|
| **NHTSA campaign** | **16V340000** (began 2016-12-06) |
| **Component** | Air bags: frontal: passenger side: inflator module |

**Consequence (verbatim):** *"An inflator rupture may result in metal fragments striking the vehicle occupants resulting in serious injury or death."* The cause: propellant degrades after *"long-term exposure to absolute humidity and temperature cycling"* — the inflator can explode instead of inflating.

**Remedy (verbatim):** *"dealers will replace the passenger frontal air bag inflator or the air bag assembly, free of charge."*

> ### The zone caveat — do NOT assume you're clear
> The **US** recall is **geographically zoned**: it lists 2009-2011 Corolla Matrix (and the sibling **Pontiac Vibe**) only for cars *"originally sold, or ever registered in"* hot-humid states/territories (**Zone A**: AL, CA, FL, GA, HI, LA, MS, SC, TX, PR, etc.). **Quebec is not in any US zone**, so the NHTSA VIN lookup may show "not affected" — that reflects the *US* campaign, not whether Takata affects your car.
>
> **Takata inflators were also recalled in Canada** (Transport Canada, Canada-wide). A humid-summer / cold-winter climate like Quebec's is exactly the temperature-cycling condition that degrades these inflators. **Check Transport Canada by VIN** — this is the one recall where the US "clear" result is misleading, and it's a rupture-shrapnel hazard, so it's worth being certain.

## Recall 2 — Accelerator pedal can stick (floor-mat entrapment) ⚠️

| | |
|---|---|
| **NHTSA campaign** | **10V023000** (began 2010-03-30) |
| **Component** | Vehicle speed control: accelerator pedal |

**Summary (verbatim):** *"Toyota is recalling certain model year 2008-2010 Highlander, model year 2009-2010 Corolla, Venza and Matrix passenger vehicles. The accelerator pedal can get stuck in the wide open position due to its being trapped by an unsecured or incompatible driver's floor mat."*

**Consequence (verbatim):** *"A stuck open accelerator pedal may result in very high vehicle speeds and make it difficult to stop the vehicle, which could cause a crash, serious injury or death."*

**Remedy (verbatim):** dealers **reshape or replace the accelerator pedal**, modify the floor surface where appropriate, and **replace any Toyota all-weather floor mat with a newly designed mat, free of charge.**

> This was part of the era's massive unintended-acceleration campaigns (and was Canada-wide). Even if the recall is closed on your VIN: **never stack floor mats, and make sure the driver's mat is the correct one, secured to its retention hooks, and not riding up against the pedal.** That habit is the free half of the fix.

## Recall 3 — Gulf States tire/rim label — **almost certainly N/A to you**

| | |
|---|---|
| **NHTSA campaign** | **10V035000** |
| **Component** | Equipment: labels (FMVSS 110 tire/rim label) |

Issued by **Gulf States Toyota**, a **regional US distributor** (Texas-area), for cars *sold* through that distributor missing a load-capacity label. **A Canadian car did not come through Gulf States**, so this doesn't apply. Noted only so it's not a mystery when it shows in the US list.

## Owner-complaint themes (NHTSA — 192 on file for the 2009 Matrix)

Complaints are owner-reported and uninvestigated, but the *distribution* is informative. Top components:

| Complaints | Component | What it usually reflects |
|---|---|---|
| **72** | Air bags | Takata + airbag warning-light / occupant-sensing complaints |
| **33** | Vehicle speed control | The unintended-acceleration saga (pedal/floor-mat) |
| **17** | **Steering** | See the EPS known-issue below |
| **8 + 7** | Engine / engine & cooling | Oil consumption + overheating themes (see below) |
| several | Brakes, powertrain, electrical | Scattered |

## Known 2.4L (2AZ-FE) / platform issues — community & TSB level, NOT authoritative-fetched

These are **widely documented** for the 2AZ-FE engine and E140 Matrix, but they come from owner communities, TSBs, and past warranty programs — **not** from the recall database. Treat them as *things to check and ask a dealer about*, and verify any warranty-program eligibility by VIN with Toyota:

- **★ Excessive oil consumption (the big one for your 2.4L).** The **2AZ-FE** (≈2007-2009, shared with Camry/Corolla XRS/RAV4/tC/Scion) is notorious for burning oil via a piston-ring/oil-ring design flaw. Toyota issued a **Customer Support Program / warranty enhancement** and there was a class-action settlement. **Practical upshot: check your oil level often** (this engine can run low between changes and low oil accelerates wear/overheating). If it consumes heavily, ask a dealer whether any support program still applies to your VIN. This interacts with the overheating item below.
- **Stripped cylinder-head bolt threads.** The 2AZ-FE aluminum block can **strip its head-bolt threads**, causing coolant loss, head-gasket symptoms, and overheating. A known failure mode; the fix is thread inserts (or worse). If you see unexplained coolant loss or overheating, mention this specifically.
- **Electric power steering (EPS).** 2009-2010 Corolla/Matrix drew many **steering** complaints (wander, looseness, a notchy or heavy feel); there were TSBs and, for some Corolla/Matrix, a **warranty extension** on the EPS. If steering feels wrong, it's worth asking whether any EPS program covers your VIN — and steering is safety-critical, so don't ignore it.
- **Sibling parts = Pontiac Vibe (2009-2010).** The Matrix and Vibe are the same NUMMI-built car; many parts and TSBs cross-reference. Handy when sourcing parts or searching problems.

Where a symptom overlaps a **recall** (sudden acceleration → the pedal recall; airbag light → the Takata/airbag items), the recall/dealer path takes priority over DIY.
