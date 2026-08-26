---
name: new-constellation-service
description: End-to-end playbook to stand up a new Codex-constellation service ("a god") from idea to buildable repo — exploration + design capture, naming + god mark, seeding the <god>-service/<god>-ui pair, git + branch protection, CI/CD + Docker Hub secrets, and ownership registration + a dedicated-session handoff. Orchestrates the constellation-logo-prompt/-key/-drop, new-github-project, github-branch-protection, dockerhub-setup, and github-actions CI skills, and pauses at the human seams (the discussion, you providing the mark image, approvals). Use when starting a new constellation service / divinity.
user-invocable: true
argument-hint: "<god-name> [what it does]"
license: MIT
---

# New Constellation Service (playbook)

Stand up a new constellation service end to end. This **orchestrates** existing skills and enforces
the constellation's disciplines; it is a sequence with **human-in-the-loop seams** — never rush past
them, and never auto-perform an outward-facing action (GitHub repo creation, publishing, deploys)
without Calvin's word.

**Constellation facts this assumes** (source of truth = the `codex` repo): Greek names = software,
Norse = physical devices; per-god accent (dark-only) echoing the UI `--primary`; design notes live
in `codex/docs/<god>.md`; deploy source of truth is `codex/apps/<god>/<god>.yaml` (a HelmRelease
pin) and **deploys are the Codex session's, on Calvin's word** — separate from creation. Docker Hub
namespace `calvinference`, GitHub owner `vezril`.

**Not every step applies to every service.** Stateless services skip persistence; a laptop/Docker-
Compose service (e.g. Ares) skips k8s/Helm and the `apps/` pin; a backend-only service skips `-ui`.
Note the exceptions rather than forcing the full list.

---

## Phase 0 — Exploration & design capture  ⟨human seam: this is a conversation⟩

1. **Discuss the idea with Calvin.** What problem, what real gap it fills — *need-first, not
   mark-first* (a god is built because the need is real, not because a name is free).
2. **Check `codex/docs/pantheon-roadmap.md`** — is this domain already assigned, speculative, or
   new? Resolve collisions before building.
3. **Name it** — Greek (software) per the convention; sanity-check it isn't claimed.
4. **⟨GATE⟩ Capture the design note** at `codex/docs/<god>.md` — the DECIDED design (what it does,
   architecture, the load-bearing constraint if any, phases, open questions). Add a roadmap row.
   *Exploration isn't done until this doc exists.* Every constellation service has one.

## Phase 1 — God mark  ⟨human seam: Calvin provides the image⟩

1. **Pick the accent** — fits the domain, **distinct from existing marks** (check the accent table
   in `codex/docs/ux-standards.md`), glows on `#06060F`. It must equal the UI `--primary` (the echo).
2. **If no mark art exists → [SKILL: constellation-logo-prompt]** to produce a paste-ready image
   prompt (4 samples, facing right, transparent, text-free).
3. **⟨PAUSE⟩** Calvin generates in Gemini and provides the chosen image.
4. **[SKILL: constellation-logo-key]** — key the raw art to a transparent mark; preview on the dark
   background for approval.
5. **⟨GATE⟩** Calvin approves the mark (brand quality is his call).
6. **[SKILL: constellation-logo-drop]** — verify → place at `codex/docs/brand/<god>.png` → register
   the accent in `ux-standards.md` (committed services only).

*The mark does not block seeding — Phase 2 can proceed in parallel and the mark lands when ready.*

## Phase 2 — Seed the project pair  (`<god>-service` [+ `<god>-ui`])

Create the folders to the standing pattern:

- **`<god>-service/`**: `README.md` (brief), a `DESIGN-*.md` pointer to `codex/docs/<god>.md`,
  `AGENTS.md` (the dedicated-session kickoff — lead with the load-bearing rule if the service has
  one), `.gitignore`.
- **`<god>-ui/`** (if it has a console): `README.md`, copied `UX-STANDARDS.md` + `UI-PLAYBOOK.md`,
  `.gitignore`. Next.js; dark-only; the god mark; surfaces the service's `/docs`.

Bake these constellation conventions into the seed (as design intent for the builder session):

- **Contract in the Lexicon.** The `.proto`/schema is the single source of truth (`the-lexicon`
  owns it) — coordinate with the Lexicon session; REST/gRPC generate *from* it.
- **APIs = what the consumers need + Hermes.** **Hermes events are the async default** (provide the
  HermesMQ client); **gRPC** for typed/streaming internal service-to-service; **REST** for
  browser/BFF/external. *Don't build both protocols if only one is used* — the contract's in the
  Lexicon, so adding the second later is cheap. Rule: blocked-and-waiting → REST/gRPC; reaction /
  pipeline / fan-out → Hermes.
- **Self-hosted `/docs`.** The service serves its own Swagger/OpenAPI on-classpath, no CDN/egress
  (the Apollo v0.13.0 precedent); the UI can surface it too.
- **Health + metrics** — `/health` + `/metrics` with Hera scrape annotations on the pod.
- **Persistence** (if stateful) — Postgres via the `pg-service` chart + pg-dump→S3 backups.
- **Runtime secrets** — SOPS+age → k8s Secret (the Harpocrates story), distinct from CI secrets.
- **Helm chart + `codex/apps/<god>/<god>.yaml` pin** — the chart *and* its HelmRelease mirror (the
  deploy source of truth). Author these in the `codex` repo (Codex session's tree). Skip for a
  Docker-Compose/laptop service; note the exception.

## Phase 3 — Git structure  ⟨approval: creating a public repo is outward-facing⟩

1. **⟨GATE⟩** confirm with Calvin before creating GitHub repos.
2. For each of `<god>-service` and `<god>-ui`, either run the **`new-github-project` workflow**
   (it bundles the three skills below) or the skills directly:
   - **[SKILL: github-new-repo] `<name> public`** — create the empty GitHub repo + seed main.
   - **[SKILL: repo-starter-docs]** — starter docs (README/LICENSE) shipped via PR.
   - **[SKILL: github-branch-protection] `<name>`** — protect `main` (PR-only).

## Phase 4 — CI/CD + Docker Hub  (after Phase 3 — dockerhub-setup needs the repo to exist)

1. **[SKILL: github-actions-scala-ci]** (or `github-actions-python-ci`) — the full CI surface:
   test / lint / build / coverage + gitleaks secret-scan, dev + release image workflows.
2. **[SKILL: dockerhub-setup] `<service>`** — creates the Hub repo, mints a CI token, sets
   `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` GitHub secrets (needs the admin PAT in env; it stops
   cleanly if absent). This is the "never hand-create the secrets" step.

## Phase 5 — Coordination & handoff

1. **Register the repos** in `codex/docs/session-coordination.md` (ownership map).
2. **Confirm `AGENTS.md` is complete** (written in Phase 2) — it's the seam between "scaffolded" and
   "built."
3. **Hand off** to a dedicated builder session: Calvin runs `cd <god>-service && claude`; it reads
   `AGENTS.md` and starts. This playbook creates the service; the dedicated session builds it, and
   the **Codex session deploys it** (pin-first, on Calvin's word) — do not deploy from here.

---

## Human seams & gates (never auto-cross)

The discussion (Phase 0), **Calvin provides the mark image** (Phase 1), **mark approval** (Phase 1),
**GitHub repo creation** (Phase 3), and **any deploy** (out of scope here — Codex session, Calvin's
word). Pause at each; surface, don't assume.

## Track it

Keep a running checklist of the phases as you go and report what's done vs pending — a service
half-created is worse than one clearly parked at a known step.
