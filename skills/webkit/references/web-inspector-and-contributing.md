# Web Inspector, the code style, and the project

Sources: webkit.org/web-inspector/, /code-style-guidelines/, /project/ + linked pages (fetched 2026-07).

## Web Inspector

Panels (each documented at `webkit.org/web-inspector/<feature>/`): **Elements** (DOM + styles), **Console** (+ command-line API, console snippets), **Sources** (debugger: JS breakpoints, DOM breakpoints, event breakpoints, **local overrides** — substitute your own response for a live resource), **Network**, **Timelines** (profiling), **Layers** (compositing/memory), **Audit** (a11y/quality), device settings simulation, plus Storage and Graphics.

Enabling:
- macOS Safari: Settings → Advanced → "Show features for web developers" → Develop menu; ⌥⌘I / Inspect Element.
- iOS device: Settings → Safari → Advanced → Web Inspector; connect by cable (or wireless), pick the page under the device in the Mac's Develop menu. Simulators are always inspectable.
- **Your own app:** `webView.isInspectable = true` (also on `JSContext`; ObjC `inspectable`) — macOS 13.3/iOS 16.4+, per-instance, **works in App Store builds** (pre-API, only Xcode-built developer-provisioned apps were inspectable — now even debug builds need the flag). Name your JSContexts to tell them apart in the Develop menu. Ship it behind a "developer mode" toggle.
- GTK/WPE ports expose the same inspector via port settings APIs.

## WebKit C++ code style (for anything destined upstream)

Only governs WebKit-tree code — your app can do what it likes. Enforced by `Tools/Scripts/check-webkit-style` and EWS.

- **Layout**: 4 spaces never tabs; namespace contents not indented; `case` aligns with `switch`; operators lead continuation lines; space after control keywords (`if (x)`), none after function names; function-definition brace on its own line, all other opening braces end-of-line; one-line clauses drop braces; empty body = `{ }`.
- **Null/bool/zero**: `nullptr` (C++), `NULL` (C), `nil` (ObjC); test truthiness directly (no `== null`/`== false`); no gratuitous `.0`/`.f`.
- **Naming**: CamelCase; types capitalized, functions/variables lowercase-first; full words; members `m_`, statics `s_`, ObjC ivars `_`; bools read as assertions (`is`/`did`/`should`); setters `setFoo`, getters bare `foo()` (no `get` prefix except out-arg getters; `IfExists` suffix for non-creating variants); enum members InterCaps capitalized; `#define` ALL_CAPS but prefer constexpr/inline; `#pragma once`; `protectedThis` for Ref/RefPtr guarding `this`.
- **Pointers**: C++ `Type* ptr` / `Type& ref` (asterisk hugs the type); C/ObjC space before `*`. Out-args by reference, pointer only when optional.
- **Includes**: `config.h` first in .cpp, primary header second, then sorted; system headers last; headers never include config.h; no global-scope `using` in headers; never `using namespace std`.
- **Types/patterns**: `unsigned` not `unsigned int`; single-arg constructors `explicit`; singletons via static `singleton()`; overrides use exactly one of `override`/`final`; spell out smart-pointer types (no `auto`) when adopting.
- **Comments**: sentence-style with periods; `FIXME:` without attribution.
- Python in-tree: PEP8.

## The project

- **Goals**: open source engine (BSD + LGPL) — compatibility, standards compliance, stability, performance, battery, security, **"privacy is a human right"**, portability, hackability.
- **Roles**: contributor → **committer** (~10–20 good patches; nominated on the reviewers list, 3 reviewers incl. nominator, 5 business days) → **reviewer** (~80 patches, 4 reviewers). One year inactive = downgrade; revocation = 2/3 reviewer vote.
- **Ports**: **Cocoa** (macOS/iOS — Safari/WKWebView), **WebKitGTK** (Linux desktop), **WPE** (embedded/kiosk/IoT), **Windows**. Nightlies from WebKit Build Archives; `build-webkit` builds from source; **MiniBrowser** is the test shell.
- **Contribution loop**: monorepo **github.com/WebKit/WebKit**; **bugs.webkit.org stays the central communication point**; `Tools/Scripts/git-webkit setup` → commit → `git-webkit pull-request` → **EWS** auto-checks (style, builds) → reviewer approval → **Merge-Queue** label lands it. All layout tests must pass (`run-webkit-tests`); **every fix needs a regression test that fails without the patch** (JSC changes also `run-javascriptcore-tests`); watch build.webkit.org afterwards.
- **Licensing**: LGPL v2 + 2-clause BSD. LGPL §6 governs embedding: ship a modified WebKit and you must allow users to see/modify/swap the LGPL parts, give notice, include the license, provide source. **Keeping patches upstreamable is usually cheaper than carrying a fork** — which is why the style guide matters to an embedder at all.
