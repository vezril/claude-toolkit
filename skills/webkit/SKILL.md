---
name: webkit
description: "Building browsers and web-content apps on Apple WebKit — the embedding engine, not web page authoring. Covers the WKWebView embedding surface organized by browser-building task (load/navigate, intercept navigation, JS injection and native messaging via content worlds, content-rule-list ad/tracker blocking, website data stores and private browsing, downloads, media permissions, popups and JS dialogs), the multi-process model, Web Inspector enablement (isInspectable), Intelligent Tracking Prevention mechanics and WebKit's tracking-prevention/security policies, the project's ports (Cocoa/GTK/WPE/Windows), contribution workflow and C++ code style, LGPL embedding obligations, and how features ship (runtime flags, css-status, standards-positions). Distilled from developer.apple.com/documentation/webkit and the webkit.org policy/reference pages (fetched 2026-07). Use when building or debugging a custom WKWebView-based browser or in-app web view, choosing WebKit APIs, aligning a browser with WebKit's privacy posture, checking engine feature support, or preparing a patch for WebKit itself."
license: MIT
---

# WebKit (embedding & the project)

WebKit is Apple's open source **web content engine** — the thing that renders pages inside
Safari and inside your app. This skill is about **embedding it** (a custom browser, an
in-app web view) and **engaging with the project** (policies, feature status, patches) —
not about writing web pages ([[web-development]], [[html-css]], [[javascript]] cover that).

Load the reference for the layer you're working at:

- **[references/embedding-api.md](references/embedding-api.md)** — the full WKWebView API
  surface by task, the gotcha catalog, version pins. Load for any implementation work.
- **[references/tracking-prevention-and-security.md](references/tracking-prevention-and-security.md)**
  — ITP mechanics (the actual numbers), the tracking-prevention policy taxonomy, the
  security process. Load when designing privacy features or anything touching storage.
- **[references/web-inspector-and-contributing.md](references/web-inspector-and-contributing.md)**
  — Inspector panels + remote debugging, the WebKit C++ style rules, ports, the
  contribution loop, licensing. Load when debugging pages or patching the engine.
- **[references/feature-status-and-standards.md](references/feature-status-and-standards.md)**
  — runtime-flag lifecycle, css-status, standards-positions. Load when asking "does the
  engine support X / will it ever".

## The mental model

- **An engine, not a browser.** WebKit gives you rendering, networking, JS (JavaScriptCore),
  storage, and a delegate-driven embedding API; *you* build chrome, tabs, history UI,
  downloads UI, error pages, dialogs — WKWebView shows nothing for `alert()` or popups
  unless you implement the delegates.
- **Out-of-process by construction.** Web content, networking, and GPU run in separate
  processes; a renderer crash blanks the view instead of killing your app — handle
  `webContentProcessDidTerminate` (reload or show a crashed-tab UI). `WKProcessPool` is
  deprecated and a no-op; share a `WKWebsiteDataStore` to share sessions.
- **Configuration is destiny.** `WKWebViewConfiguration` is *copied* at web view init —
  decide data store, user content controller, and preferences before creation. A private
  window is just `websiteDataStore = .nonPersistent()`; a profile is
  `WKWebsiteDataStore(forIdentifier:)`.
- **Ports.** Cocoa (WKWebView — Apple platforms), WebKitGTK (Linux desktop), WPE
  (embedded), Windows. The embedding API and community channels differ per port; this
  skill's API layer is the Cocoa port.

## The browser-builder's spine (the ten decisions)

1. **Chrome state is KVO.** Drive URL bar, progress, lock icon from observing `url`,
   `title`, `estimatedProgress`, `hasOnlySecureContent`, `serverTrust`.
2. **Navigation policy is your interception point.** `decidePolicyFor navigationAction /
   navigationResponse` (allow / cancel / **download**); `targetFrame == nil` = wants a new
   window; `canShowMIMEType == false` = download it. There is **no webRequest-style API**:
   http(s) blocking goes through compiled `WKContentRuleList`s, full stop.
3. **Popups need you.** Implement `createWebViewWith` and build the returned WKWebView
   **from the configuration WebKit hands you** (anything else throws); return nil to block.
   Implement the three JS dialog callbacks and always call their completion handlers.
4. **JS ↔ native = user scripts + message handlers, in your own `WKContentWorld`**
   (`.defaultClient`) so pages can't tamper. `callAsyncJavaScript` for calls with
   arguments/Promises. Message handlers are retained strongly — break the cycle.
5. **Content blocking is declarative.** JSON rules (triggers: url-filter/if-domain/
   resource-type/load-type; actions: block, block-cookies, css-display-none, make-https,
   ignore-previous-rules) compiled once per identifier by `WKContentRuleListStore`
   (EasyList-scale takes seconds — never on the hot path).
6. **Data management powers your settings UI.** `fetchDataRecords` / `removeData(ofTypes:)`
   for "manage website data" and "clear last hour"; `WKHTTPCookieStore` is **not**
   `HTTPCookieStorage` — they don't sync.
7. **Downloads are three-entry.** Policy `.download`, `startDownload`, `resumeDownload`;
   set `download.delegate` synchronously; destination collisions FAIL — unique names are
   your job; observe `download.progress`.
8. **Permissions route to you.** Camera/mic via `requestMediaCapturePermissionFor` (+
   capture-state KVO for a "tab is recording" indicator); geolocation via CoreLocation and
   your app's own permission; element fullscreen needs `isElementFullscreenEnabled`.
9. **Debugging = `isInspectable = true`** (macOS 13.3/iOS 16.4+, default false, works in
   release builds) → the full Safari Web Inspector attaches from the Develop menu.
10. **Privacy is inherited AND owed.** Engine-level protections (partitioned third-party
    storage, cache partitioning, referrer downgrades, fingerprinting-surface refusals) come
    with WebKit; verify ITP behavior on your data store rather than assuming Safari parity —
    and never build anything the tracking-prevention policy would classify as circumvention:
    WebKit patches those with security-bug urgency, and there are **no exceptions** for
    anyone.

## Always-apply

1. Deprecated-API tripwires: `UIWebView`/legacy `WebView` are dead; `WKPreferences.javaScriptEnabled`
   → `WKWebpagePreferences.allowsContentJavaScript` (which spares your own injected JS);
   `WKProcessPool` is a no-op.
2. Filter the noise errors: `NSURLErrorCancelled` (-999) and frame-load-interrupted (102)
   in `didFailProvisionalNavigation` are normal — don't show error pages for them.
3. Check availability against the version pins in the embedding reference — the good APIs
   (downloads, content worlds, profiles, proxies, inspectable) span iOS 14–17/macOS 11–14.
4. For "does WebKit support X": CSS → css-status (trunk truth); JS/web APIs → MDN/Can I Use
   (WebKit retired its general status page); future intent → standards-positions.
5. Patches destined upstream follow the WebKit C++ style (`check-webkit-style`) and need a
   regression test — no test, no landing.

## Related

- [[apple-dev]] — the Apple/Swift cluster this sits in (app lifecycle, SwiftUI chrome).
- [[web-development]] · [[html-css]] · [[javascript]] — the content side of the glass.
- [[webassembly]] — the other language JavaScriptCore runs; a WKWebView browser inherits
  Wasm support for free (this skill is the vessel, that one is the language).
- [[secure-coding]] · [[network-security]] — TLS handling, sandboxing your browser.
- Sources: developer.apple.com/documentation/webkit; webkit.org — web-inspector,
  tracking-prevention (+policy), security-policy, code-style-guidelines, feature-policy,
  project, css-status, standards-positions (fetched 2026-07).
