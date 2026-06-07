---
name: nodejs
description: Node.js — JavaScript on the server — distilled from *Node.js in Action* and *Node.js, MongoDB & AngularJS Web Development*. Covers the runtime model (V8, the single-threaded event loop, libuv, non-blocking I/O, the call stack vs the event/microtask queues, worker threads & the cluster module for CPU/scaling), modules (ESM vs CommonJS, npm/package.json, semver), core APIs (fs, path, http, events/EventEmitter, streams & backpressure, buffers, process/env), async patterns (callbacks → promises → async/await, error-first callbacks), building HTTP servers and REST APIs with Express (routing, middleware, error handling), working with databases (MongoDB/Mongoose, SQL), environment/config & secrets, and production concerns (logging, process managers, security). Use when building or reviewing a Node.js backend/CLI/tool, designing an Express API, working with streams or the event loop, choosing async patterns, structuring modules/packages, or connecting to a database. Builds on javascript/typescript; pairs with nginx (reverse proxy), docker, and nextjs (its runtime).
---

# Node.js

**JavaScript on the server** — from ***Node.js in Action*** and ***Node.js, MongoDB & AngularJS Web Development***. Node runs [[javascript]] outside the browser on Google's **V8** engine with non-blocking I/O, making JS a full backend/CLI/tooling language. The same event-loop model as the browser, applied to servers.

Cross-links: [[javascript]] (the language — same event loop), [[typescript]] (TS-first backends), [[nginx]] (reverse proxy in front of Node), [[docker]] (containerized deploy), [[nextjs]] (runs on Node), [[secure-coding]] (web/server security), [[cqrs-event-sourcing]] / [[akka]] (alternative server architectures).

> Note: the MEAN-stack book covers **AngularJS** (Angular 1.x), which is **end-of-life** — use it for the Node/MongoDB material, not as a frontend recommendation (use [[react]]/[[vue]] today).

## The runtime model (why Node is the way it is)

- **Single-threaded event loop + non-blocking I/O.** Node runs your JS on one thread; I/O (disk, network, DB) is delegated to the OS / a thread pool (**libuv**) and results come back as callbacks. So one process handles **thousands of concurrent connections** efficiently — *as long as you never block the loop*.
- **The loop phases** (libuv): timers → pending callbacks → poll (I/O) → check (`setImmediate`) → close; **microtasks** (Promise callbacks, `process.nextTick`) run between phases (and `nextTick` before other microtasks). Same mental model as [[javascript]]'s event loop.
- **Don't block the loop** — heavy synchronous work (big loops, sync crypto, JSON of huge objects) freezes *all* requests. Offload CPU work to **worker threads** (`worker_threads`), child processes, or a queue; scale across cores with the **`cluster`** module / a process manager.
- Node is great for **I/O-bound** workloads (APIs, proxies, real-time), less so for CPU-bound (use workers or a different runtime).

## Modules & packages

- **ESM** (`import`/`export`, `"type":"module"`) is the standard; **CommonJS** (`require`/`module.exports`) is the legacy default — know both (lots of code is CJS). Use ESM for new projects.
- **npm** + **`package.json`**: dependencies, scripts, `engines`; lockfile for reproducibility; **semver** (`^`/`~`). Audit deps ([[secure-coding]] — supply chain). Built-in modules use the `node:` prefix (`import fs from 'node:fs/promises'`).

## Core APIs

- **`fs`** (prefer the promise API `fs/promises`), **`path`** (cross-platform paths), **`os`**, **`process`** (`process.env`, `argv`, `exit`, signals), **`crypto`**.
- **`events` / `EventEmitter`** — Node's pub/sub backbone (`on`/`emit`); streams and many core objects are emitters.
- **Streams** — process data **incrementally** (Readable/Writable/Duplex/Transform); pipe with `pipeline()`; mind **backpressure** (don't outpace the consumer). Essential for large files, HTTP bodies, and memory efficiency — a Node superpower.
- **`http`/`https`** — the low-level server (`createServer`); most apps use a framework on top.
- **Buffers** for binary data; **`AbortController`** for cancellation.

## Async patterns

- Evolution: **error-first callbacks** (`(err, data) => …`) → **Promises** → **async/await** (use this). Promisify old callback APIs (`util.promisify`) or use the `fs/promises`-style APIs.
- Always handle rejections (an unhandled rejection crashes the process); use `try/catch` around `await`, `Promise.all` for concurrency, and propagate errors as `Error` objects. ([[javascript]] async reference.)

## HTTP servers & APIs (Express)

The common stack is **Express** (or Fastify/Koa/Nest):
- **Routing** — `app.get('/users/:id', handler)`, route params, query, `req`/`res`.
- **Middleware** — `app.use(fn)` functions that run in order `(req, res, next)`; for parsing (`express.json()`), auth, logging, CORS, etc. The pipeline is the core Express idea.
- **Error handling** — a 4-arg middleware `(err, req, res, next)`; centralize it; never leak stack traces in prod.
- **REST** — resource routes, proper status codes, JSON bodies; validate input at the boundary ([[typescript]]/zod, [[secure-coding]]). For real-time, **WebSocket** (`ws`/Socket.IO).
- Modern alternative: **NestJS** (structured, DI, TS-first) for larger apps.

## Databases

- **MongoDB** (document store) via the driver or **Mongoose** (schemas/models/validation) — the book's stack. Good for flexible/JSON-shaped data.
- **SQL** (Postgres/MySQL) via `pg`/Prisma/Drizzle for relational data + transactions. ([[cqrs-event-sourcing]] for advanced data patterns.)
- Use a **connection pool**; parameterize queries (never string-concat SQL → injection, [[secure-coding]]); keep DB credentials in env/secrets.

## Config & production

- **Config via environment** (`process.env`, `.env` with dotenv); **never commit secrets**; separate config per environment ([[secure-coding]]).
- **Logging** (pino/winston) — structured logs, not `console.log` in prod; **process manager** (pm2/systemd) or a container ([[docker]]) for restarts; health checks.
- **Behind a reverse proxy** ([[nginx]]) for TLS, static files, compression, load balancing — don't expose Node directly. Scale with `cluster`/multiple instances. ([[site-reliability-engineering]] for ops.)
- **Graceful shutdown** (handle SIGTERM, drain connections); set timeouts; handle uncaught exceptions/rejections.

## Anti-patterns

- **Blocking the event loop** (sync FS/crypto, heavy CPU in the request path) — freezes the whole server; offload to workers.
- Unhandled promise rejections / swallowed errors; mixing callbacks and promises messily (promisify instead).
- **String-concatenated SQL / unsanitized input** (injection); committing secrets; leaking stack traces.
- Reading entire large files/bodies into memory instead of **streaming** (OOM); ignoring **backpressure**.
- Exposing Node directly to the internet without a reverse proxy/TLS; no process manager / graceful shutdown.
- Treating Node as CPU-compute (use worker threads or another tool); recommending **AngularJS** from the dated book (use [[react]]/[[vue]]).

## Always-apply

1. **Never block the event loop**; offload CPU to **worker threads**; scale with `cluster`/multiple instances behind [[nginx]].
2. **async/await** (+ `Promise.all`); always handle rejections; promisify legacy callback APIs.
3. **Stream** large data with backpressure; use `EventEmitter` for pub/sub.
4. Express: **middleware pipeline** + centralized **error handler**; validate input at the boundary; parameterize DB queries.
5. **Config/secrets via env**; structured logging; process manager/container; reverse proxy + TLS; graceful shutdown. Use **ESM** + [[typescript]].

## Related

- [[javascript]] — the language and event loop; [[typescript]] — TS-first backends.
- [[nginx]] — reverse proxy/TLS in front of Node; [[docker]] — containerized deploy; [[nextjs]] — runs on Node.
- [[secure-coding]] — injection, secrets, supply chain; [[site-reliability-engineering]] / [[devops]] — running it in prod.
- [[cqrs-event-sourcing]] / [[akka]] — alternative backend data/architecture patterns.
- Sources: *Node.js in Action* (Cantelon et al.); *Node.js, MongoDB & AngularJS Web Development* (Brad Dayley) — for the Node/MongoDB parts.
