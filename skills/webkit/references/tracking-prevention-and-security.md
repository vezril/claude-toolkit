# Tracking prevention (ITP) & the WebKit security process

Sources: webkit.org/tracking-prevention/, /tracking-prevention-policy/, /security-policy/ (fetched 2026-07). Scope note: the technical page covers Apple OSes without per-mechanism Safari-vs-WKWebView scoping — engine-level protections travel with WebKit; verify ITP specifics on your own data store rather than assuming Safari parity.

## ITP mechanics (the numbers that matter)

**Classification** — on-device ML, no browsing history leaves the machine. Signals: subresource/iframe prevalence across unique first parties + cross-site redirects; bounce tracking (top-frame redirect counts, incl. delayed bounces); tracker collusion (walking the redirect graph backward recursively classifies colluders).

**Effects on classified domains**
- Full website-data deletion when the domain has no first-party interaction or Storage Access grant in the last **30 days of browser use**.
- Bounce-tracker cookie jail: classified domains with interaction that still bounce-track get cookies rewritten **SameSite=strict** (unreadable cross-site).

**Cookies**
- **All third-party cookies blocked, no exceptions.** Re-entry only via the Storage Access API (or the temporary popup compatibility flow). Cookie-blocking latch: once a request is cookie-blocked, all its redirects are too.

**Expiry caps on script-writable storage**
- **7 days without first-party interaction**: `document.cookie` cookies AND all script-writable storage (LocalStorage, SessionStorage, IndexedDB, Service Worker registrations + caches, media keys) are deleted.
- **24 hours**: JS cookies on a landing page reached from a classified domain **with link decoration** (click IDs etc.).
- **7 days**: cookies set in HTTP responses behind third-party **CNAME cloaking** or IP-address cloaking (closes the "set it as first-party HTTP cookie" loophole).
- Exemption: home-screen web apps' first-party domain (data also isolated from Safari).

**Partitioning & related defenses**
- Third-party LocalStorage/IndexedDB: partitioned per first party AND ephemeral (session-only); third-party Service Workers partitioned likewise.
- HTTP cache partitioned per first party; **Verified Partitioned Cache** for classified domains (flagged entries re-fetch after 7 days; mismatch triggers re-verification — kills cache-based identifiers).
- Referrer downgrade: all third-party referrers reduced to origin (`Referer` header and `document.referrer`).
- HSTS writable only by the first party and only for host/registrable domain (no HSTS super-cookies).

**Anti-fingerprinting** — web + OS-bundled fonts only; frozen UA string; DNT removed (was itself an fingerprint bit); refused APIs: Web Bluetooth, Web MIDI, Magnetometer, Web NFC, Device Memory, Network Information, Battery Status, Ambient Light, Proximity, WebHID, Serial, Web USB, background Geolocation Sensor.

**Private browsing** (Safari's model, worth mirroring): ephemeral session **per tab**, nothing on disk.

## The policy (what WebKit promises and demands)

Tracking taxonomy: **cross-site tracking** (incl. app↔web, and retention/sharing of data derived from cross-site activity), **stateful** (cookies/DOM storage/IndexedDB/cache/SW), **covert stateful** (HSTS, TLS — channels not meant for storage), **navigational** (link decoration, headers), **fingerprinting/stateless**, **covert tracking** (the umbrella).

Commitments: prevent **all covert tracking and all cross-site tracking**; where impossible without undue harm → limit the capability or gate on informed consent. Purpose-built replacements (Storage Access API, Private Click Measurement), never allowlists.

The two lines an embedder must never cross:
- **Circumvention = security vulnerability.** Anything that re-enables cross-site identity (sharing cookies across stores, injecting identifiers, un-truncating referrers, proxying around partitioning) gets patched with security urgency, possibly without notice.
- **No exceptions to specific parties** — don't build per-site tracker allowlists into a product; route breakage (federated login, embedded media, analytics) to the Storage Access API path instead, and accept that "breakage is not a reason to stop" is the project's stated posture.

## Security process

- Report: bugs.webkit.org, **Security product** (access-controlled: Security Group + reporter). Email **security@webkit.org** with the bug link for fast acknowledgment (≤ a week).
- Embargo: negotiated per bug, **default minimum 60 days**; can lift early when all affected vendors have shipped and the reporter agrees.
- **WebKit Security Group**: fixers, trusted researchers, and **vendor contacts shipping WebKit-based products** — the membership track relevant to a custom-browser shipper (nomination via security@webkit.org; 3 members' support within 5 business days; confidentiality until disclosure). Join it and track advisories: anti-tracking circumvention fixes ship with security urgency, so keep your embedded WebKit current.

## Checklist for a privacy-respecting custom browser

1. Verify (don't assume) ITP behavior on your `WKWebsiteDataStore`; test the 7-day/24-hour caps against your deployment target.
2. Design every feature (sync, telemetry, extensions) against the taxonomy: would it enable stateful/covert/navigational/fingerprint tracking?
3. Surface Storage Access API prompts in your UI — WKWebView hands the decision to you.
4. Mirror the private-browsing model: ephemeral store per window (or per tab if you go full Safari), nothing persisted.
5. Keep referrer downgrades, partitioning, and the fingerprinting refusals intact — no "compatibility modes" that weaken them.
6. Ship engine updates promptly; join the Security Group as a vendor.
