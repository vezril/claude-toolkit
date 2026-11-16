# The C4 model & diagrams-as-code

The full C4 model (Simon Brown, c4model.com) plus the text-to-diagram tooling (Mermaid, PlantUML) for keeping architecture diagrams in the repo. C4 is **notation-independent and tooling-independent** — "maps of your code at different zoom levels."

## C4 abstractions (the hierarchy)

> "A **software system** is made up of one or more **containers** (applications and data stores), each of which contains one or more **components**, which in turn are implemented by one or more **code** elements. And **people** use the software systems we build."

`Person → Software System → Container → Component → Code`

- **Person** — actors/roles/personas who use the system.
- **Software System** — the highest level; *"something that delivers value to its users."* Rule of thumb: what a single team builds, owns, and sees inside. Includes the system in scope **and** external systems it depends on. (Not: bounded contexts, capabilities, teams.)
- **Container** — *"an application or a data store… something that needs to be running for the system to work"* — a **separately runnable/deployable unit**. **Explicitly NOT a Docker container.** Examples: a server-side web app, an SPA, a mobile/desktop app, a serverless function, a database/schema, a blob store, a file system. A significant SPA + its server-side API = **two** containers. A JAR/DLL/module is **not** a container (code organization, not runtime). Cloud data services (S3, RDS) you own = treat as containers.
- **Component** — *"a grouping of related functionality encapsulated behind a well-defined interface."* **Not** separately deployable — components live in the same process as their container. A package/namespace/folder is not necessarily a component.
- **Code** — classes, interfaces, functions, DB tables. Rarely drawn by hand; generate if needed.

**Microservices:** if one team owns them, model each as a **group of containers** (API + DB-schema) inside the system boundary; if separate teams own them (Conway), "promote" each to its own **software system**. **Queues/topics:** model each queue/topic as its own **container** (it's "essentially a data store"), or put it on the relationship as a "via" label — don't model the bus as a hub.

## C4 diagram types

**Core (the "C4"):**
1. **System Context** — the system as one box + its users + external systems. Audience: **everyone**. The starting point. Focus on people/systems, not tech.
2. **Container** — zoom inside the system boundary: the apps/data stores, major **technology choices**, and how they communicate. Audience: **technical**. (Says little about deployment.)
3. **Component** — zoom inside one container: its components and responsibilities. *Draw only if it adds value; automate for long-lived docs.*
4. **Code** — UML class / ERD inside a component. *Rarely worth hand-drawing.*

**Supplementary:**
- **System Landscape** — multiple systems across an org (context diagram with no single focus). A bridge to enterprise architecture.
- **Dynamic** — runtime collaboration for a story/use case, with **numbered interactions** (communication- or sequence-style). Use sparingly.
- **Deployment** — how container instances map to infrastructure **per environment** (one per prod/staging/dev). **Deployment nodes** (physical/VM/**Docker container**/execution env, nestable) + **infrastructure nodes** (DNS, load balancers, firewalls). (Note: a Docker container is a *deployment node* here — distinct from a C4 "container".)

Recommended for all teams: **System Context, Container, Deployment** (and System Landscape in larger orgs). Component/Code only where they earn it.

## Notation (make a diagram stand alone)

The test: *can each diagram be understood without a narrative?* So:
- **Title** stating diagram type + scope ("System Context diagram for X").
- **Key/legend** explaining shapes, colors, line/border/arrow styles, acronyms.
- **Elements:** specify the **type** (Person/System/Container/Component), a short **description**, and (for containers/components) the **technology**.
- **Relationships:** every line is **unidirectional** and **labelled** with intent (avoid bare "Uses"); inter-process lines name the **protocol/technology**.
- **Colors** are your choice but **consistent**; mind color-blindness/B&W printing.
- Diagrams are *not* just wiring diagrams — the descriptive text is what makes them C4.

## Diagram review checklist (C4's own)
Title present? Type understood? Scope understood? Key present? — Every element: name, type, what it does, technology (where applicable), acronyms, colors/shapes/icons all explained? — Every relationship: labelled, label matches direction, protocol where applicable, line/arrow styles explained?

## Diagramming vs modelling (why it scales)
Don't cram 600 components on one canvas. Split into many focused diagrams — per functional area / bounded context / use case — each at **one consistent level of abstraction**. This is trivial with a **modelling** tool (one model → many auto-generated views, e.g. Structurizr DSL) and painful with a pure drawing tool. C4 deliberately covers **static structure only** (not business processes, workflows, state, or data models — supplement with BPMN/state diagrams/ERDs). It's inspired by UML and the 4+1 model; use UML/ArchiMate instead if those already work for you.

## Diagrams-as-code tooling

Keep diagrams as **text in the repo** so they version and diff with the code (fights doc-rot):

- **Mermaid** — *"create diagrams and visualizations using text and code."* Markdown-inspired; renders to SVG. Supports flowchart, sequence, class, state, ER, deployment-ish, and **C4** diagrams (`C4Context`/`C4Container`/… — *experimental, limited layout control*). **Renders natively in GitHub, GitLab, Obsidian, Notion**, many SSGs — zero-friction default. Editable at mermaid.live.
- **PlantUML** — *"generate diagrams from textual description."* Java-based; full UML + many non-UML types; has a mature **C4-PlantUML** extension (`!include` C4_Context/Container/Component/Deployment) — the best text-to-C4 notation alongside Structurizr DSL. Renders via JAR/online/self-hosted server.
- **Structurizr DSL** — the dedicated C4 *modelling* tool (one model → many diagrams); doesn't render inline in Markdown but is the richest C4 route.

**In Obsidian** (Calvin's notes): **Mermaid works natively** (` ```mermaid ` fenced block — the *Mermaid Tools* plugin only adds snippet buttons). **PlantUML needs the community `obsidian-plantuml` plugin** (renders via online/local/self-hosted server; ` ```plantuml ` / `plantuml-svg` / `plantuml-ascii`). Practical upshot: the **same C4 diagram text** drops into an Obsidian note, a GitHub README, or the repo — version-controlled alongside prose and ADRs.

**Default recommendation:** Mermaid for quick C4/sequence/flow diagrams that must render everywhere (GitHub + Obsidian); PlantUML (C4-PlantUML) when you want richer, more faithful C4 notation; Structurizr DSL if you outgrow drawing and want a real model. Whichever — keep it as code, beside the architecture it describes.
