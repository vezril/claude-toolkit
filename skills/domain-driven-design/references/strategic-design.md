# Strategic design

DDD Part IV: keeping models coherent across large systems, multiple teams, and integrations — the part of DDD that has aged best. Definitions faithful to Evans (2003); Scala/FP and modern (microservices) notes added.

## Contents

1. Bounded Context
2. Continuous Integration (within a context)
3. Context Map
4. The context-relationship patterns
5. Distillation and the Core Domain
6. Large-Scale Structure

---

## 1. Bounded Context

**Explicitly define the context within which a model applies** — the boundary (a subsystem, a team's work, a service) inside which a particular model is **unified and internally consistent**, with terms having one precise meaning. A single enterprise-wide model is a mirage; instead, accept multiple models and make their boundaries explicit.

The key insight: the *same word* means different things in different contexts. "Customer" in Sales (a prospect, a pipeline stage) is not "Customer" in Support (an account with tickets). Forcing one shared `Customer` class onto both couples them and corrupts both models. A Bounded Context lets each model stay clean within its boundary.

**Scala/FP & modern.** A Bounded Context maps naturally onto a **module or microservice** with its own model and its own persistence. The biggest modern misuse of "microservices" is splitting by technical layer while sharing a database/model — that violates the boundary and recreates coupling. One context = one model = one team's autonomy.

## 2. Continuous Integration (within a context)

Within a single Bounded Context, the model can fragment if people work without merging and reconciling frequently. **Continuously integrate** — merge code and model often, with automated tests and team practices that catch divergence early — so the context stays unified. (This is model integration, not just the CI-server sense, though they reinforce each other.)

## 3. Context Map

**Identify each Bounded Context and the relationships between them, and document them in a Context Map** — a shared, honest picture of the territory: which models exist, where they touch, and how they translate. Without it, contexts collide invisibly at their seams. The map describes *reality* (including messy relationships), not an idealized plan, and names the contexts in the Ubiquitous Language so the whole team can talk about boundaries.

## 4. The context-relationship patterns

Ways two Bounded Contexts can relate, from most to least cooperative — choose deliberately per relationship:

- **Shared Kernel** — two teams share a small, explicitly agreed subset of the model (and its code), changed only by consultation. Reduces duplication but tightly couples the teams on that kernel.
- **Customer/Supplier** — upstream context (supplier) and downstream context (customer) have a clear directional dependency; the downstream team's needs are negotiated into the upstream team's plan. Works when both teams are cooperative and priorities can be balanced.
- **Conformist** — the downstream team simply **adopts the upstream model as-is**, with no translation, when the upstream is too big/uncooperative to negotiate with and good enough to follow. Cheap, but you inherit the upstream's model.
- **Anticorruption Layer (ACL)** — the downstream builds an **isolating translation layer** that converts the upstream model into its own, so a foreign or legacy model can't leak in and corrupt yours. Costlier, but protects model integrity; essential when integrating a messy legacy or third-party system.
- **Separate Ways** — when integration costs more than it's worth, **don't integrate**; let the contexts go fully independent.
- **Open Host Service** — a context used by many others publishes a well-defined **service/protocol** as its integration point, instead of bespoke translation per consumer.
- **Published Language** — pair with Open Host Service: define a shared, documented interchange language (e.g. a well-specified schema/format) for communication between contexts.

**Scala/FP & modern.** The **Anticorruption Layer is an Adapter** (see [[design-patterns]]) at the service boundary — translate the external model into your domain types right at the edge, keeping the core pure and uncontaminated. Open Host Service + Published Language is exactly a versioned public API / well-specified event schema between microservices.

## 5. Distillation and the Core Domain

In a large model, not all parts matter equally. **Distillation** is the work of finding and elevating what does:

- **Core Domain** — the part that is the *reason the software exists*, your competitive edge. Identify it explicitly and **put your best people and most design effort there**; don't let it drown among supporting code. The most important strategic decision in the book.
- **Generic Subdomains** — necessary but non-differentiating parts (e.g. a generic money/ledger or notification model). Don't lavish your best modeling here; use off-the-shelf solutions, outsource, or implement plainly so attention stays on the Core.
- **Domain Vision Statement** — a short description of the Core Domain and its value, to keep the team aligned on what matters.
- **Highlighted Core / Cohesive Mechanisms / Segregated Core / Abstract Core** — techniques to make the Core stand out and stay clean: flag the core elements, factor out reusable computational "mechanisms," and physically separate the core from supporting subdomains.

**Modern note.** Distillation is the most reused strategic idea: **focus effort on the differentiating Core, buy/borrow the generic.** It directly informs build-vs-buy and where to spend senior engineering time.

## 6. Large-Scale Structure

Patterns for giving a big system a comprehensible shape so people can navigate it without grasping every detail:

- **Evolving Order** — let the large-scale structure **evolve** with understanding rather than being imposed up front and frozen; an over-rigid structure imposed early constrains the model badly. Favor a structure that can change.
- **System Metaphor** — a shared, evocative analogy for the whole system (from XP) that guides design when it genuinely fits (don't force one).
- **Responsibility Layers** — assign each part of the model to a layer of responsibility (e.g. potential / operations / decision-support) so dependencies flow in one direction and the system's narrative is legible.
- **Knowledge Level** — a group of objects that describes and constrains how another group may behave (a meta-model / "things that configure other things"), letting users adjust behavior without code changes.
- **Pluggable Component Framework** — for very mature domains: distill an abstract core into an interface that diverse components plug into.

**Modern note.** Most teams need far less of this than Parts II–III; reach for large-scale structure only when a system is big enough that people genuinely get lost in it, and keep it evolving.
