---
name: gitbucket
description: GitBucket — the self-hosted, single-WAR Git platform written in Scala (gitbucket.github.io) with a deliberately GitHub-compatible REST API at /api/v3. Covers running it (java -jar gitbucket.war, the official Docker image, a NAS/reverse-proxy deployment, GITBUCKET_HOME), every CLI flag and its env-var and system-property equivalents plus the config precedence order, the API in detail — all four authentication methods and the inconsistent unauthenticated-request behaviour (401 vs 404 vs empty 200) plus unauthenticated user enumeration, the verified route table, the endpoints GitHub has that GitBucket does not (notably no PATCH /issues/:id, so an issue cannot be closed or edited via the API), hard-coded 25-item pagination with no Link headers, GitBucket's own issue-filter vocabulary (author/assigned, not creator/assignee), 404-for-unimplemented error semantics and the disabled rate_limit endpoint — plus webhooks and their event types, SSH access on port 29418, clone and raw/archive URL formats, external MySQL/PostgreSQL setup, backup, and plugins. Use when installing, configuring, upgrading or debugging GitBucket, writing API or webhook automation against it, porting GitHub tooling or a delivery-flow adapter to it, or deciding how far its GitHub compatibility actually goes. Complements git, docker, nginx, scala and secure-coding.
---

# GitBucket

A **GitHub-like Git platform in a single WAR file**: Scala on Scalatra + JGit, H2 embedded by default, an embedded Jetty when run standalone. Its two stated priorities are *easy installation* and *API compatibility with GitHub*. The second is the reason it appears in automation at all — and the exact shape of that compatibility is where every real problem lives, so most of this skill is about the edges rather than the happy path.

Verified against **v4.48.0** and the `gitbucket/gitbucket` source route table, not only the wiki (which is incomplete and in places out of date).

Cross-links: [[git]] (the underlying operations), [[docker]] / [[finch]] (how it usually runs), [[nginx]] (reverse proxy), [[scala]] (it's a Scala app; plugins are Scala), [[secure-coding]] (tokens, default credentials), [[delivery-flow]] (adapter contract — see the mapping below).

## Running it

```bash
java -jar gitbucket.war                          # standalone, embedded Jetty, :8080
java -jar gitbucket.war --port=8080 --prefix=/git --gitbucket.home=/srv/gitbucket
docker run -d -p 8080:8080 -p 29418:29418 \
  -v /volume1/docker/gitbucket:/gitbucket gitbucket/gitbucket
```

- **Java 17.** Default login is `root` / `root` — change it immediately ([[secure-coding]]).
- Data lives in **`GITBUCKET_HOME`** (`~/.gitbucket`, or `/gitbucket` in the container):
  `repositories/`, `data/` (avatars), `gist/`, `plugins/`, `gitbucket.conf`, `database.conf`.
- Upgrading is "stop, swap the WAR, start" — but back up `GITBUCKET_HOME` first, because some
  releases run large schema migrations (4.47.0 and 4.48.0 both altered `REPOSITORY`/`ACCOUNT`).
- It also deploys into a Servlet 3.0 container (Jetty/Tomcat/JBoss). **Jakarta EE is not
  supported**, so Tomcat 10+ will not work — this catches people out.

### On a NAS

The Docker image is the sane route. Two things that are easy to miss:

- **Map 29418 as well as 8080** if you want SSH clones, *and* enable SSH in the UI. The quick-start
  command in the docs maps only 8080, so SSH silently isn't available.
- **Set the base URL** (Administration → System Settings). Nothing that generates an absolute
  link — SSH clone URLs, webhook payloads, notification emails — is correct without it, and
  behind a reverse proxy GitBucket cannot infer it.

## Configuration

| Flag | Default | Env var |
|---|---|---|
| `--gitbucket.home=DIR` | `~/.gitbucket` | `GITBUCKET_HOME` |
| `--port=N` / `--secure_port=N` | `8080` / `8443` | `GITBUCKET_PORT` / `GITBUCKET_SECUREPORT` |
| `--host=HOST` | — | `GITBUCKET_HOST` |
| `--prefix=/path` | `/` | `GITBUCKET_PREFIX` |
| `--connectors=HTTP,HTTPS` | `http` | `GITBUCKET_CONNECTORS` |
| `--key_store_path` / `--key_store_password` / `--key_manager_password` | — | `GITBUCKET_KEYSTOREPATH`, … |
| `--redirect_https=BOOL` | `false` | `GITBUCKET_REDIRECTHTTPS` |
| `--temp_dir=DIR` | `tmp` under home | `GITBUCKET_TEMPDIR` |
| `--plugin_dir=DIR` | — | `GITBUCKET_PLUGINDIR` |
| `--jetty_idle_timeout=MS` | `300000` | `GITBUCKET_JETTYIDLETIMEOUT` |
| `--disable_cache`, `--disable_news_feed`, `--save_sessions` | off | `GITBUCKET_DISABLECACHE` |

**Precedence: system property → environment variable → config file.** So `gitbucket.base_url`
or `GITBUCKET_BASE_URL` silently overrides what the admin UI wrote into `gitbucket.conf`, which
is the usual reason a setting "won't stick". Same pattern for `gitbucket.db.url` / `GITBUCKET_DB_URL`.

## The API

Base path **`/api/v3`** — the GitHub Enterprise shape, deliberately.

### Authentication — four ways, and one trap

```bash
curl -H "Authorization: token $GB_TOKEN"  "$GB/api/v3/user"   # personal access token
curl -H "Authorization: Bearer $GB_TOKEN" "$GB/api/v3/user"   # also accepted
curl -u user:password                      "$GB/api/v3/user"  # basic auth
curl "$GB/api/v3/user?access_token=$GB_TOKEN"                 # query param
```

Tokens are minted per user under **Account Settings → Applications**. `Bearer` works even
though the wiki documents only `token`. OAuth2 key/secret flows are **not** supported.

**The trap: an unauthenticated request does not fail consistently.** The auth filter rejects
only a token that is *present and invalid*; a missing header falls through to the route's own
authenticator, and those disagree about what to return. Measured on a live 4.x instance:

| Request | Result |
|---|---|
| `GET /user`, no header | `401 {"message":"Requires authentication"}` |
| `GET /user`, bad token | `401 {"message":"Bad credentials"}` |
| `GET /user/repos`, no header | **`404 {"message":"Not Found"}`** |
| `GET /repositories`, no header | `200 []` — public subset, no error |
| `GET /users`, no header | `200` with the **full account list** |

So no single status proves an auth problem: the same missing header yields 401 on one endpoint,
404 on another, and a plausible-looking empty success on a third. **Smoke-test with
`GET /api/v3/user`** — it is the one endpoint that distinguishes all three states, and the two
401 messages tell you *which* failure you have: `Requires authentication` means your header
never arrived, `Bad credentials` means the token itself is rejected.

**`GET /api/v3/users` needs no authentication and returns every account including email
addresses.** Anyone who can reach the port can enumerate your users. Treat network exposure as
the only control here and put the instance behind a VPN or an authenticating proxy
([[secure-coding]]).

### What exists

Verified from the source route table (~97 routes). Grouped, with GitHub's paths:

- **Users/orgs:** `GET /user`, `PATCH /user`, `GET /user/:id`, `GET /users`, `/users/:u`,
  `/users/:u/repos`, `/users/:u/orgs`, `GET /user/repos`, `/user/orgs`, `GET /organizations`,
  `/orgs/:org`, `/orgs/:org/repos`. Admin: `POST /admin/users`, `POST /admin/organizations`,
  `PUT|DELETE /users/:u/suspended`.
- **Repos:** `GET /repositories`, `/repositories/:id`, `GET /repos/:o/:r`, `POST /user/repos`,
  `POST /orgs/:org/repos`, `GET|POST /repos/:o/:r/forks`, `GET …/tags`, `…/branches`,
  `…/collaborators` (+ check/add/remove/`/permission`).
- **Commits/contents/refs:** `GET …/commits`, `…/commits/:sha`, `…/contents/*`,
  `PUT …/contents/*` (create or update a file), `…/readme`, `GET|POST|PATCH|DELETE …/git/refs/*`.
- **Issues:** `GET …/issues`, `GET …/issues/:id`, `POST …/issues`; comments
  (`GET|POST|PATCH|DELETE`); labels and milestones (full CRUD); issue-label add/remove/replace.
- **Pull requests:** `GET …/pulls`, `POST …/pulls`, `GET …/pulls/:id`, **`PATCH …/pulls/:id`**,
  `GET …/pulls/:id/commits`, `GET …/pulls/:id/merge` (is-merged), `PUT …/pulls/:id/merge`.
- **Statuses & protection:** `POST …/statuses/:sha`, `GET …/statuses/:ref`,
  `GET …/commits/:ref/status`, branch protection `GET|DELETE`, `PATCH …/branches/*`.
- **Releases:** full CRUD plus assets — `GET|POST …/releases`, `…/releases/latest`,
  `…/releases/tags/:tag`, `PATCH|DELETE …/releases/:tag`, `POST …/releases/:tag/assets`.
  (Undocumented on the wiki's endpoint list; it's in the source.)
- **Webhooks:** `GET|POST …/hooks`, `GET|PATCH|DELETE …/hooks/:id`.
- **GitBucket-only:** `GET …/raw/*`, `GET …/commits/:sha/branches-where-head`,
  `GET /api/v3/gitbucket/plugins`.

### What's missing — the ones that break workflows

- **No `PATCH /repos/:o/:r/issues/:id`.** You cannot close, reopen, retitle, or reassign an
  issue through the API. Only create, read, and comment. Pull requests *do* have `PATCH`, which
  makes the asymmetry easy to miss. Workarounds: a **commit-message keyword** on a pushed
  commit (`close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved #N`, repeatable in one
  message), or the web UI. Changing labels is possible, so label-as-state is a viable model.
- **No repo deletion, no issue deletion, no reviews/review-comments API, no teams, no search,
  no Actions/Checks** (status API only), **no git blobs/trees/commits write API**.
- **`GET /api/v3/rate_limit` returns `404 {"message":"Rate limiting is not enabled."}`** —
  copying GitHub Enterprise. Tooling that preflights rate limits will read that as a hard failure.
- **Unimplemented routes return `404`, not `501`.** A catch-all maps every unmatched
  `/api/v3/*` verb to `NotFound`, so *"this endpoint doesn't exist"* and *"this resource doesn't
  exist"* are indistinguishable by status code. When a port of GitHub tooling 404s, check the
  route table above before assuming your IDs are wrong.

### Pagination — inconsistent, and there are no Link headers

Three different behaviours, so never write one generic pager:

| Endpoints | Paging |
|---|---|
| Issues, pull requests | `page` only. Page size is **hard-coded at 25**; `per_page` is ignored. |
| Commits, repository lists | `page` + `per_page` (default 30, capped 100). |
| Labels, milestones, hooks, collaborators, tags, branches, releases | **None** — the full list, always. |

**GitBucket emits no `Link` header anywhere.** There is no `rel="next"` to follow, so the only
termination condition is a short page: loop `page=1,2,3…` until you get fewer than the page
size. Code that trusts `Link` will silently process page 1 and stop.

### Issue filters use GitBucket's vocabulary, not GitHub's

`GET …/issues` accepts `labels` (comma-separated), `milestone`, `priority`, **`author`**,
**`assigned`**, `mentioned`, `state` (`open`|`closed`|`all`, default **`open`**), `sort`
(`created`|`comments`|`updated`|`priority`), `direction` (`asc`|`desc`), `visibility`, `groups`,
and `custom.<field>=<op>:<value>`.

GitHub's `creator=` and `assignee=` **are not recognised and are silently ignored** — you get an
unfiltered list that looks plausible. Note also that `state` defaults to `open`, so a sync job
that forgets `state=all` will never see closed work.

## Webhooks

Per-repo, managed in the UI or via the `…/hooks` API. Supported events: **CreateEvent,
IssuesEvent, IssueCommentEvent, PullRequestEvent, PullRequestReviewCommentEvent, PushEvent,
GollumEvent** (wiki edits). Payloads imitate GitHub's but implement only a subset of fields —
validate against a real delivery rather than against GitHub's documented schema, and set the
base URL or the payload links will be wrong.

## Git access and URL formats

```
http(s)://<host>[:8080]/git/<owner>/<repo>.git     # HTTP(S) clone — note the /git/ segment
ssh://git@<host>:29418/<owner>/<repo>.git          # SSH clone, once SSH is enabled
```

- **SSH defaults to port 29418** and is **off** until you set the SSH bind host/port in System
  Settings; set the public host/port too when behind a proxy. Users add their key under Account
  Settings. Git LFS is supported.
- Web/raw/archive paths: `/{owner}/{repo}/blob|raw|edit/{branch}/{path}`,
  `/{owner}/{repo}/archive/{branch}.zip` (and `.tar.gz`), `/{owner}/{repo}/wiki/{Page}`,
  `/{user}/_avatar`, `/activities.atom`.

## Database

H2 by default. External options are **MySQL 5.7+** or **PostgreSQL 14+** via
`GITBUCKET_HOME/database.conf`:

```
db {
  url = "jdbc:postgresql://localhost/gitbucket"
  user = "gitbucket_user"
  password = "..."
}
```

Migration gotchas: H2 1.x→2.x needs `;MVCC=true` dropped from the URL (upgrading past 4.42);
after a PostgreSQL import you must `setval` every sequence or inserts collide; PostgreSQL 15+
also needs `GRANT ALL ON SCHEMA public`; MySQL needs a case-sensitive collation
(`utf8mb4_ja_0900_as_cs`) or names differing only in case throw duplicate-key errors.

**Backup:** simplest is stop GitBucket and copy `GITBUCKET_HOME`. For a live backup, mirror-clone
`repositories/`, copy `gitbucket.conf`, `data/`, `gist/`, and export the database — the wiki's
example script POSTs to `/api/v3/plugins/database/backup` for that, which is plugin-provided and
not in the core route table, so confirm it exists on your instance before relying on it.

## Plugins

Scala, dropped into `GITBUCKET_HOME/plugins/` (or installed from the admin UI). Official ones:
gist, emoji, pages, notifications. `GET /api/v3/gitbucket/plugins` lists what's loaded. Plugins
own database tables and can block upgrades — uninstall before a major version jump, reinstall after.

## Using it from the delivery-flow adapter contract

If the workflow is a GitBucket [[delivery-flow]] adapter, the contract maps cleanly except in
one place:

| Contract command | GitBucket |
|---|---|
| `fetch <key>` | `GET /repos/:o/:r/issues/:id` ✅ |
| `comment <key>` | `POST /repos/:o/:r/issues/:id/comments` ✅ |
| `related <key>` | no link API — parse `#N` references out of body/comments |
| **`transition <key> <state>`** | **no API.** No `PATCH /issues/:id`. Use labels as state, or a `close #N` commit |
| `open-pr` | `POST /repos/:o/:r/pulls` ✅ |
| `ci-status <ref>` | `GET /repos/:o/:r/commits/:ref/status` ✅ |

`transition` is the whole problem: model state as **labels** (full CRUD exists) rather than
open/closed, or accept that closing is a side effect of a push. Decide that before writing the
adapter, because it changes the item schema.

## Anti-patterns

- Assuming full GitHub API parity, then reading the resulting `404` as a bad ID rather than a
  missing endpoint.
- Writing `PATCH /issues/:id` to close an issue; expecting reviews, teams, search, or Actions.
- Sending `creator=`/`assignee=` filters and trusting the result, or forgetting `state=all`.
- Writing a `Link`-header pager, or passing `per_page` to the issues/pulls endpoints.
- Leaving `root`/`root`, or putting a token in a URL (`?access_token=`) that lands in logs.
- Running GitBucket on Tomcat 10+ (Jakarta), or forgetting to map 29418 and enable SSH.
- Not setting the base URL behind a reverse proxy, then debugging "broken" webhook links.
- Swapping the WAR across a migration release without backing up `GITBUCKET_HOME`.

## Always-apply

1. **`/api/v3` is GitHub-*shaped*, not GitHub-complete.** Check the route table before porting
   tooling; unimplemented endpoints answer `404`.
2. **Smoke-test auth with `GET /api/v3/user`** — unauthenticated requests return 401, 404 or a
   plausible empty 200 depending on the endpoint, so only that one tells you the real state.
   `GET /api/v3/users` is unauthenticated and leaks every account's email.
3. **Page by "short page", never by `Link`.** Issues and pulls are fixed at 25 and ignore `per_page`.
4. **Issues are create/read/comment only.** No close or edit via API — labels or commit keywords.
5. **Set the base URL**, and enable SSH explicitly on 29418 if you want it.
6. **Back up `GITBUCKET_HOME`** before any upgrade; config precedence is property → env → file.

## Related

- [[git]] — the operations underneath; [[merge]], [[pr-description]] for the review flow.
- [[docker]] / [[finch]] — how it's usually deployed; [[nginx]] — reverse proxy and `--prefix`.
- [[scala]] — the implementation language and the plugin API.
- [[secure-coding]] — default credentials, token handling, exposing a forge on a LAN.
- [[delivery-flow]] — the adapter contract above; [[github-issue-fix-flow]] for the GitHub equivalent.
- Source: [gitbucket/gitbucket](https://github.com/gitbucket/gitbucket) (route table read from
  `src/main/scala/gitbucket/core/controller/api/`) and the project wiki, at v4.48.0.
