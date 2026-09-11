# 2022 Super Chief — troubleshooting & warning lights

Diagnosis and triage, not torque-critical repair. This helps you **narrow a symptom, decide
if it's safe to ride, and know owner-check vs. dealer** — it does not replace the service
manual or a certified tech, and it never gives a from-memory procedure for a safety-critical
system. Exact specs (pressures, tensions, torques, codes) → the specs reference and your manual.

## 🛑 Stop-riding-now symptoms — do NOT "ride it to the shop"

If any of these appear, park it and get it inspected/towed. These are the ones where continuing risks a crash:

- **Any change in braking** — longer stopping distance, spongy/long lever or pedal travel, brake drag, grinding, or the *"shushing"* + delayed bite an owner reported. Brakes are pass/fail, not wait-and-see.
- **ABS warning light stays on while riding** *and* braking feels off — the ABS may not be modulating; treat wheel lockup as possible.
- **Fuel smell, visible fuel leak, or fuel sputtering/stalling** — overlaps the **fuel-pump recall (I-22-06)**; stalling in traffic is the exact hazard that recall addresses.
- **Wobble, weave, or headshake** at speed — steering-head, wheel-bearing, tire, or loaded-touring geometry issue.
- **Belt damage** — visible cracks, missing teeth, frayed edges, or a stone lodged in it. A belt that lets go strands you and can lock the rear.
- **Warning light + power loss / limp behavior** — the EFI may be protecting the engine; forcing it can compound damage.
- **Steering-head or fork play**, front-end clunk on braking, or a leaking fork.

When in doubt about a safety system, the correct move is a flatbed, not a gamble.

## Owner-checkable first (safe, no special tools)

Before booking a dealer, these are legitimately DIY and resolve a lot of "won't start / acting weird":

- **Kill switch & kickstand interlock** — run/stop switch set to run; **kickstand fully up** (the bike won't run in gear with it down — and note the kickstand **recall I-23-01**). Check neutral.
- **Keyless fob** — if no-start or intermittent recognition, the **fob battery** (a coin cell — verify type in the manual) is the usual culprit; there's a documented **backup start procedure** holding the fob to the console. Keep the fob near the bike.
- **Main battery** — cranks slow / clicks / dead dash after sitting → check/charge the 12V battery; a **battery tender** prevents the parasitic drain these keyless CAN-bus bikes are prone to. Confirm terminals are tight and clean.
- **Fuses** — a dead circuit (lights, accessory, no-crank) can be a blown fuse; locate the fuse box and check per the manual's ratings (don't up-rate a fuse).
- **Fuel** — enough in the tank; if you struggle to fill, that's the **filler-neck anti-siphon bar** (fuel slowly at a shallow angle), not a fault.
- **Tire pressure (cold)** — low pressure explains vague handling and uneven wear; set to the **placard** value.
- **Oil level** — check via the **sight glass** per the manual's exact procedure (upright, specified temp).
- **Loose/dirty connections** and a clogged **air filter** for rough running.

## Symptom → likely area → action

| Symptom | Likely areas (narrow it) | Action |
|---|---|---|
| **No crank / dead dash** | Battery low/terminals; kill switch; kickstand or clutch interlock; fuse; fob not recognized | Owner-check battery, switches, fob, fuses → else dealer (starter/relay/security) |
| **Cranks, won't start** | Fuel delivery (**recall I-22-06**), fob/immobilizer, flooded, sensor | Confirm fuel + fob; **check the fuel-pump recall** → dealer for EFI/security |
| **Stalls / sputters under load or when hot** | **Fuel pump (recall I-22-06)**, fuel filter, EFI sensor | **Prioritize the recall check**; then dealer diagnosis |
| **Hard hot-start** | Fuel pressure (pump), heat soak | Recall check → dealer |
| **Check-engine (MIL) on** | EFI fault stored — could be trivial (loose gas cap / sensor) or real | Don't ride hard; get the **stored code read** by a dealer — code meaning is service-manual territory, don't guess from the number |
| **ABS light on** | Wheel-speed sensor, ABS module, low battery voltage, sensor gap/debris | If braking is normal it may be a sensor; **if braking is abnormal → stop-ride**. Dealer for ABS faults |
| **Battery keeps dying** | Parasitic drain (sitting), charging system, aging battery | Tender + load-test; charging-system diagnosis → dealer |
| **Overheating feel / temp warning** | Traffic heat is normal for air-cooled; warning light is not | If a **temperature telltale** shows, stop and let it cool; recurring → dealer |
| **Vague / heavy steering, uneven tire wear** | Tire pressure, tire wear, bearings | Set cold pressure; inspect tires; play/wobble → dealer |
| **Belt noise / vibration** | Tension out of spec, debris, wear | Visual + deflection check **per manual spec**; damage → dealer, don't ride |
| **Clunky shifting / clutch slip** | Clutch adjustment/wear, oil level/grade, linkage | Check oil; persistent → dealer |
| **Cluster telltale you don't recognize** | See the light table below | Match the light; unknown + drivability change → dealer |

## Warning lights / telltales (standard cluster)

The standard (non-Ride Command) cluster uses telltale lamps plus the digital inset. Meanings are largely standard, but **your owner's manual has the exact icon legend for your build** — confirm there, especially for anything amber/red.

| Light | Means | If it's on |
|---|---|---|
| **Check-engine / MIL** (engine outline) | EFI stored a fault | Rideable-gentle if running normally; get the code read. Power loss → stop |
| **ABS** | ABS self-check (normal at key-on, should extinguish) or a fault if it stays lit | Stays on: sensor/module — pair with how the brakes feel |
| **Low oil pressure** (oil can) | Oil pressure below threshold — **serious** | **Stop the engine now**; check oil; do not run it |
| **Engine temperature** | Overtemp | Stop, idle-cool or shut down; recurring → dealer |
| **Battery / charging** | Charging fault | Ride minimally; diagnose charging → dealer |
| **Security / immobilizer** | Fob not recognized / system armed | Fob battery, backup start procedure |
| **Low fuel** | Reserve | Fuel up (mind the filler-neck bar) |
| **Neutral, high-beam, turn signals, cruise** | Status indicators | Informational |

*(At key-on, several lights illuminate briefly as a bulb/self-check and then go out — that's normal. A light that **stays on or comes on while riding** is the signal.)*

## What to never DIY on this bike

- **Brake and ABS hydraulics/internals** — bleeding, caliper, ABS module, sensors. Get it right or don't touch it.
- **Fuel system** — pump, lines, pressure (and this is a live recall area).
- **EFI/ABS fault-code interpretation and clearing** — dealer diagnostic tooling.
- **Safety-critical fasteners** (axle, steering, caliper mounts) without the **torque spec** and a torque wrench.
- **Recall work** — it's free at the dealer; don't improvise a fuel-pump or kickstand fix.

## How to escalate well

When you take it in, hand the dealer specifics: the **symptom + when it happens** (cold/hot, load, speed), any **telltale** and whether it self-cleared, and — critically — **your VIN and the recall numbers** (I-22-06 fuel pump, I-23-01 kickstand) so open campaigns get done in the same visit. Indian customer service: **1-877-204-3697**.
