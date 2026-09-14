---
name: aws-amplify
description: "Building and deploying full-stack apps with AWS Amplify Gen 2 — the TypeScript code-first successor to the Amplify CLI/Studio (Gen 1), distilled from docs.amplify.aws and AWS's own Amplify agent skill (fetched 2026-09). Covers the architecture (amplify/backend.ts + defineBackend composing defineAuth/defineData/defineStorage/defineFunction, generated amplify_outputs.json consumed by Amplify.configure()), auth (Cognito: email/social/SAML login, MFA, passwordless/WebAuthn, Lambda triggers, guest access), data (AppSync + DynamoDB: schema with a.model()/a.enum()/a.customType(), six authorization strategies, hasMany/belongsTo/hasOne relationships, secondary indexes, custom Lambda-backed queries/mutations), storage (S3 path-based access rules, event triggers), functions (Lambda: env vars/secrets, schedules, resource grants, REST/HTTP APIs via CDK), client integration per framework (React/Next.js/Vue/Angular/React Native/Flutter/Swift/Android: generateClient, CRUD + observeQuery/subscriptions, the Authenticator component and manual signIn/signInStep state machine, Next.js SSR via generateServerClientUsingCookies), hosting and CI/CD (sandbox vs pipeline-deploy, amplify.yml per-framework baseDirectory, IAM service role, branch-per-environment, monorepos, secrets via SSM, custom domains), CDK escape hatches (createStack, backend overrides for CFN properties Amplify doesn't expose), and a security checklist. Use when scaffolding an Amplify Gen 2 project, writing defineAuth/defineData/defineStorage/defineFunction, wiring a frontend to amplify_outputs.json, setting up Amplify Hosting CI/CD or custom domains, debugging a silent Amplify failure (blank page, undefined API calls, stalled auth flow), or distinguishing Gen 2 from legacy Gen 1 (amplify/.config/, Amplify Studio)."
license: MIT
---

# AWS Amplify (Gen 2)

How to build and ship a full-stack app on **AWS Amplify Gen 2** — the current, TypeScript-first version of Amplify (distinct from the retired Gen 1 CLI/Studio experience). Distilled from [docs.amplify.aws](https://docs.amplify.aws/) and AWS's own Amplify agent skill, fetched 2026-09. Cross-links: [[react]] / [[nextjs]] / [[vue]] / [[typescript]] for the frontend half, [[nodejs]] for Lambda handlers ([[aws-lambda]] for their execution model), [[aws-cognito]] for what `defineAuth` provisions underneath, [[aws-s3]] for what `defineStorage` provisions underneath, [[secure-coding]] for the auth/IAM hardening checklist below, [[cqrs-event-sourcing]] for how AppSync subscriptions relate to event-driven patterns.

> **Freshness.** Amplify Gen 2 ships continuously; exact package/CLI behavior here is a dated snapshot (2026-09). When in doubt, re-check `docs.amplify.aws` or AWS's own Amplify skill (`aws agent-toolkit`) for the installed version's exact API.

## The mental model

**Code-first, not console-first.** Gen 1 provisioned infrastructure through the Amplify CLI wizard or Amplify Studio. Gen 2 is the opposite: you write plain TypeScript describing *what* you need, and Amplify translates it into CloudFormation/CDK and deploys it.

```
amplify/
├── backend.ts              defineBackend({ auth, data, storage, myFunc })  — the composition root
├── auth/resource.ts        defineAuth({...})      → Cognito User Pool + Identity Pool
├── data/resource.ts        defineData({...})      → AppSync GraphQL API + DynamoDB tables
├── storage/resource.ts     defineStorage({...})   → S3 bucket + access policies
└── functions/<name>/
    ├── resource.ts         defineFunction({...})  → Lambda function
    └── handler.ts          the actual Lambda code
src/                        your frontend, a sibling of amplify/
amplify_outputs.json        GENERATED, gitignored — Amplify.configure(outputs) reads this
```

Every `define*` call declares a resource; `defineBackend` wires them together and is the **only** place that determines what actually deploys — a `defineFunction` never imported into `backend.ts` never ships. Deploying (`npx ampx sandbox` locally, `npx ampx pipeline-deploy` in CI) generates `amplify_outputs.json`, and the frontend reads that file at startup via `Amplify.configure(outputs)`. Nothing in `amplify/` is committed as infrastructure state — the TypeScript *is* the source of truth, same spirit as CDK.

**Gen 1 vs Gen 2 — check before touching a project.** If `amplify/.config/` exists (no `backend.ts`), the project is legacy Gen 1 (CLI-driven, `amplify push`, Amplify Studio) — this skill does not apply; that's a separate migration effort. Gen 2 signals: `amplify/backend.ts` exists and `@aws-amplify/backend` is a devDependency. Never mix the two.

## Choosing defaults (ask, don't assume)

| Unspecified input | What to do |
|---|---|
| Web framework | Default to **React (Vite)**, say so |
| Mobile platform | **Ask** — Flutter/Swift/Android/React Native have no shared default |
| "Build an app," web vs mobile unclear | **Ask** before scaffolding anything |
| Package manager | Default **npm** unless told otherwise |
| Next.js router | Default **App Router** |
| React Native | **Ask** Expo vs bare CLI — setup differs |
| Login method | **Ask** — never silently pick email/password vs social vs SAML |
| Data authorization | Starter default is `publicApiKey` (open); once auth exists, switch to **owner-based** (`allow.owner()` + `defaultAuthorizationMode: 'userPool'`) |

## Non-negotiables (the failures are almost all *silent*)

Amplify's failure mode is rarely a loud error — it's a blank page, an `undefined` response, or a stalled UI. Check these first:

1. **`amplify/` and `src/` are siblings** at the project root. A different layout breaks sandbox detection.
2. **Run `npx ampx sandbox --once` before `npm run dev`, every fresh checkout.** `amplify_outputs.json` doesn't exist until you deploy once; without it the build fails on the missing import. In any non-interactive/CI/agent context, always pass `--once` — bare `npx ampx sandbox` starts a file watcher that never exits.
3. **`Amplify.configure(outputs)` must run in the framework's real entry point** (`src/main.tsx`, `app/layout.tsx` with `{ ssr: true }` for Next.js App Router only, `src/main.js`/`.ts` for Vue/Angular). Wrong file → every Amplify call silently no-ops.
4. **`generateClient<Schema>()` is called once, at module scope** — never inside a component/render. Missing the `<Schema>` generic silently strips all typing.
5. **Every relationship needs both sides declared** (`hasMany` on the parent *and* `belongsTo` on the child) and the foreign key must be `a.id()`, not `a.string()`. One-sided or wrong-typed FKs resolve to `undefined`/`null` with no error.
6. **Storage rules need `.to([...])` and end in `/*`.** A rule missing `.to()` grants nothing; a path without a trailing `/*` matches nothing; `{entity_id}` only works paired with `allow.entity('identity')`.
7. **`allow.guest()` (data) vs `allow.guest` (storage)** — method vs property. Mixing them is a TypeScript error, not a runtime one, so it's usually caught — but the asymmetry trips people constantly.
8. **Secrets always go through `secret()`**, never string literals or plain `environment` values — and sandbox secrets (`npx ampx sandbox secret set`) are invisible to Hosting; production secrets need `npx ampx secret set --branch <branch> --app-id <id>`.
9. **`amplify.yml`'s `baseDirectory` must match the framework** (Vite → `dist`, CRA → `build`, Next.js SSR → `.next`, Next static export → `out`, Angular → `dist/<project>/browser`). Wrong value = blank page in production, no error.
10. **Guest (unauthenticated) access is ON by default** in Gen 2 — the Identity Pool ships with `allowUnauthenticatedIdentities: true`. Evaluate deliberately; don't assume it's opt-in.

## Quick reference

| Package | Purpose |
|---|---|
| `@aws-amplify/backend` | `defineAuth`, `defineData`, `defineStorage`, `defineFunction`, `defineBackend` |
| `aws-amplify` | Frontend: `Amplify.configure()`, `generateClient()`, auth/data/storage client APIs |
| `@aws-amplify/ui-react` (+ `-vue`, `-angular`, `-react-native`) | `<Authenticator>` |
| `@aws-amplify/adapter-nextjs` | `generateServerClientUsingCookies`, `createServerRunner` for SSR |

| Command | Does |
|---|---|
| `npm create amplify@latest -y` | Scaffold `amplify/` into an existing frontend project |
| `npx ampx sandbox --once` | Deploy a personal dev backend, generate `amplify_outputs.json`, exit |
| `npx ampx sandbox` | Same, but watches files and redeploys on change (interactive dev only) |
| `npx ampx sandbox secret set <NAME>` | Set a secret for **sandbox only** |
| `npx ampx secret set <NAME> --branch <b> --app-id <id>` | Set a secret for a **hosted branch** |
| `npx ampx pipeline-deploy --branch $AWS_BRANCH --app-id $AWS_APP_ID` | CI/CD backend deploy (used inside `amplify.yml`) |
| `npx ampx generate outputs --app-id <id>` | Pull `amplify_outputs.json` for a frontend-only app in a monorepo |

## References

- `references/backend-resources.md` — `defineAuth` (login methods, MFA, passwordless, social/SAML, triggers, guest access) and `defineFunction` (Lambda, schedules, env/secrets, resource grants, REST/HTTP APIs).
- `references/data-modeling.md` — `defineData` schema, field types, the six authorization strategies, relationships, secondary indexes, enums/custom types, custom Lambda-backed queries and mutations.
- `references/storage.md` — `defineStorage`, path-based access rules, multiple buckets, event triggers, the client file API.
- `references/client-integration.md` — per-framework `Amplify.configure()`, `generateClient` CRUD/subscriptions, the Authenticator component and manual `signIn`/`signInStep` flow, Next.js SSR patterns, React Native specifics.
- `references/hosting-and-cicd.md` — scaffolding, sandbox workflow, Amplify Hosting CI/CD setup (IAM role, `amplify.yml`, monorepos), branch-per-environment, secrets, custom domains, rollback.
- `references/advanced-and-ops.md` — CDK escape hatches (custom stacks, resource overrides), Geo/PubSub/Face Liveness, the security checklist, Gen 1 detection, and a troubleshooting index of the silent failures above.
