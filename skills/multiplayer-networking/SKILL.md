---
name: multiplayer-networking
description: Networked multiplayer game programming, distilled from Glazer & Madhav's *Multiplayer Game Programming* and Glenn Fiedler's Gaffer On Games. Covers why games use UDP over TCP (head-of-line blocking/latency), building reliability/sequencing/congestion over UDP, the three networking models (deterministic lockstep, snapshot interpolation, state synchronization) and when to use each, the authoritative-server model with client-side prediction and server reconciliation, entity interpolation and lag compensation, snapshot/delta compression and bit-packing, the fixed-timestep simulation ("Fix Your Timestep!") and float determinism, replication/RPCs, topologies (client-server vs peer-to-peer), and security/cheating concerns (never trust the client). Use when designing or implementing multiplayer, choosing a netcode model, handling latency/prediction/reconciliation, replicating state, debugging desync/lag, or reasoning about authority and anti-cheat. Builds on tcp-ip/network-engineering and pairs with godot (high-level multiplayer API), game-physics (deterministic sim), and akka (server-side actors).
---

# Multiplayer Game Programming

Building **networked multiplayer** — the hardest distributed-systems problem in games — from **Glazer & Madhav's *Multiplayer Game Programming*** and **Glenn Fiedler's Gaffer On Games** (gafferongames.com, the canonical netcode resource). The core challenge: hide **latency** and keep clients **consistent** over an unreliable, ~tens-to-hundreds-of-ms network.

Cross-links: [[tcp-ip]] / [[network-engineering]] (UDP/IP, the wire), [[godot]] (high-level multiplayer API: `@rpc`, `MultiplayerSpawner`/`Synchronizer`), [[game-physics]] (fixed-step deterministic sim), [[akka]] (actor model for authoritative game servers), [[network-security]] (DDoS/anti-cheat), [[cqrs-event-sourcing]] (inputs-as-events parallels lockstep).

## UDP over TCP (why)

Real-time games use **UDP**, not TCP. TCP's in-order reliability causes **head-of-line blocking**: one lost packet stalls *all* later data until it's retransmitted — fatal for a 60 Hz update stream where stale data is worthless. So games send **UDP** datagrams and build *only the reliability they need* on top:
- a **virtual connection** (handshake, keep-alive, timeout) over connectionless UDP;
- **sequence numbers + acks** for the packets that must arrive;
- **congestion avoidance** (don't flood the link);
- packet **fragmentation/reassembly** for >MTU data, and **reliable-ordered messages** only where required.
(Fiedler's "networking fundamentals" + "game networking protocol" series; [[tcp-ip]] for UDP/MTU.)

## The three networking models (pick one)

Fiedler's "What Every Programmer Needs To Know About Game Networking":
- **Deterministic lockstep** — send only **inputs**; every peer runs the *same deterministic* simulation in step. Tiny bandwidth, scales to huge unit counts (RTS — StarCraft/AoE). Requires **perfect determinism** (float determinism!) and waits on the slowest peer; one desync diverges everything. (Inputs-as-events ≈ [[cqrs-event-sourcing]].)
- **Snapshot interpolation** — the **authoritative server** sends world **snapshots**; clients **interpolate between** them, rendering slightly **in the past** for smoothness. Simple, robust, handles loss gracefully; **bandwidth-heavy** and adds interpolation delay. Great for shooters with modest entity counts.
- **State synchronization** — hybrid: stream **state updates** with **client-side prediction** + smoothing/correction; balances bandwidth and responsiveness; suits **physics-heavy** games. The most common modern AAA approach.

## Authoritative server + client-side prediction + reconciliation

The standard model for action games (the anti-cheat-friendly one):
- **The server is authoritative** — it owns the true game state; clients send **inputs**, the server simulates and broadcasts results. **Never trust the client.**
- **Client-side prediction** — to hide RTT, the client *immediately* applies its own input locally (predicts) instead of waiting for the server.
- **Server reconciliation** — when the authoritative state arrives, the client **replays** its unacknowledged inputs from that corrected state, snapping/smoothing any mismatch. Keeps the local player responsive *and* consistent.
- **Entity interpolation** — *remote* entities are rendered interpolated in the past (buffered snapshots) for smooth motion despite packet jitter.
- **Lag compensation** — for hit detection, the server rewinds to the shooter's view-time so "I aimed at them" registers fairly (Valve's model).

## Compression & bandwidth

Bandwidth is the budget: **snapshot/delta compression** (send only what changed vs a baseline), **bit-packing** and **quantization** (don't send a full float for a position — pack to the needed bits), relevancy/interest management (only send what a client can see), and prioritization. (Fiedler "Snapshot Compression".)

## The fixed timestep & determinism

**"Fix Your Timestep!"** (Fiedler) — run the simulation at a **fixed delta** via an accumulator and **interpolate the render** between sim states. Essential for stable physics ([[game-physics]]) and *mandatory* for **lockstep** (every peer must step identically). **Floating-point determinism** across machines/compilers is hard (different rounding) — use fixed-point or carefully controlled float math when you truly need cross-platform determinism.

## Replication, topology & the engine

- **Replication / RPCs** — sync object state and call remote functions; mark what replicates and who has authority. In [[godot]]: the **high-level multiplayer API** — `@rpc` annotations, `MultiplayerSpawner` (spawn replicated nodes), `MultiplayerSynchronizer` (sync properties), over ENet/WebSocket/WebRTC.
- **Topology:** **client-server** (authoritative, the default — easier security, one source of truth) vs **peer-to-peer** (lower latency between peers, but trust/cheating and NAT-traversal problems). Dedicated server vs listen server.
- **Server-side** scaling/concurrency pairs with [[akka]] (an actor per player/room is a natural fit).

## Security & cheating

**Never trust the client** — validate all input server-side; the client only *requests*. Guard against speed/teleport/aimbot by server authority + sanity checks; encrypt/authenticate sessions; rate-limit and protect against **DDoS** ([[network-security]]). Anti-cheat is fundamentally "the server decides."

## Anti-patterns

- Using **TCP** for real-time state (head-of-line blocking, latency spikes) — use UDP + your own reliability.
- **Trusting the client** (client-authoritative movement/damage) → trivially cheatable; make the server authoritative.
- No **client-side prediction** (laggy local controls) or no **reconciliation** (rubber-banding/desync).
- **Variable timestep** in the simulation → nondeterminism, exploding physics, broken lockstep.
- Assuming **float determinism** across platforms for lockstep without testing/controlling it.
- Sending **full state** every tick with no delta/quantization/interest management (bandwidth blowout).
- Hand-rolling transport when [[godot]]'s high-level multiplayer API fits; ignoring NAT traversal for P2P.

## Always-apply

1. **UDP + only the reliability you need**; never use TCP for the real-time stream.
2. Choose the model deliberately: **lockstep** (RTS, deterministic, tiny bandwidth) / **snapshot interpolation** (simple, robust) / **state sync** (responsive, physics) — know the trade.
3. **Authoritative server + client prediction + reconciliation + entity interpolation (+ lag compensation)**; never trust the client.
4. **Fixed timestep**; mind **float determinism**; **delta-compress/quantize** and use interest management.
5. Use [[godot]]'s high-level multiplayer API where it fits; scale servers with [[akka]]; defend with [[network-security]].

## Related

- [[tcp-ip]] / [[network-engineering]] — UDP/IP, MTU, NAT, the wire underneath.
- [[godot]] — high-level multiplayer API (`@rpc`, Spawner/Synchronizer).
- [[game-physics]] — fixed-step deterministic simulation; [[cqrs-event-sourcing]] — inputs-as-events ≈ lockstep.
- [[akka]] — actor-per-player/room authoritative servers; [[network-security]] — DDoS/anti-cheat.
- Sources: *Multiplayer Game Programming: Architecting Networked Games* (Glazer & Madhav); Gaffer On Games (Glenn Fiedler, gafferongames.com).
