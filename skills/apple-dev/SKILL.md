---
name: apple-dev
description: Meta/overview skill for Apple platform development (Swift, SwiftUI, iOS, macOS) — the entry point and router for the toolkit's contributed Apple skills. Explains the cluster and points to the right one: building/refactoring/styling/auditing SwiftUI (swiftui-ui-patterns, swiftui-view-refactor, swiftui-liquid-glass, swiftui-performance-audit), Swift 6.2+ concurrency (swift-concurrency-expert), profiling and on-simulator debugging (native-app-profiling, ios-debugger-agent), and release packaging/notes (release-macos-spm-packaging, release-app-store-changelog), plus the github-issue-fix-flow workflow. Use as the starting point for any Swift/SwiftUI/iOS/macOS task, when unsure which Apple skill fits, or when a task spans several of them. From any Apple task, defer to the specific skill for detail.
---

# Apple platform development (overview / meta)

The map for this toolkit's **Apple/Swift** skills (Swift, SwiftUI, iOS, macOS). These were contributed and live alongside the JVM/Scala skills; this meta skill is the router — for real work, **read the specific skill** linked below. These complement the toolkit's language-agnostic engineering skills ([[clean-code]], [[software-design]], [[tdd]], [[functional-programming]], [[design-patterns]], [[secure-coding]]), which apply to Swift as much as anywhere.

## Which skill to reach for

**Building & shaping SwiftUI**
- **[[swiftui-ui-patterns]]** — best practices/patterns for SwiftUI views & components (MV over MVVM, tab/screen architecture, sheets, environment, state management). *Start here when creating or composing UI.*
- **[[swiftui-view-refactor]]** — refactor a view file for consistent structure, dependency injection, and Observation usage. *Use when cleaning up an existing view.*
- **[[swiftui-liquid-glass]]** — adopt/review the iOS 26+ Liquid Glass API. *Use for the modern glass styling.*
- **[[swiftui-performance-audit]]** — diagnose slow rendering, janky scrolling, excessive view updates, layout thrash. *Use when SwiftUI feels slow.*

**Language & runtime**
- **[[swift-concurrency-expert]]** — Swift 6.2+ concurrency review/remediation (data-race safety, actors, `async/await`, fixing concurrency compiler errors). *Use for concurrency work or migration.*

**Profiling & debugging**
- **[[native-app-profiling]]** — CPU/Time-Profiler profiling of macOS/iOS apps via `xctrace` (no Instruments GUI). *Use to find hotspots from the CLI.*
- **[[ios-debugger-agent]]** — build, run, and debug an iOS app on the simulator; drive the UI; capture logs; diagnose runtime behavior. *Use to actually run/observe the app.*

**Release & delivery**
- **[[release-macos-spm-packaging]]** — scaffold/build/package SwiftPM-based macOS apps without an Xcode project (bundle assembly, signing, notarization). *Use for from-scratch SPM macOS apps.*
- **[[release-app-store-changelog]]** — generate App Store "What's New" / release notes from git history. *Use at release time.*

**Workflow**
- **[[github-issue-fix-flow]]** — end-to-end GitHub issue → implement fix → build/test → commit & push (via `gh`). *Use to take an issue number to a pushed fix.* (Domain-neutral; useful beyond Apple.)

## How they fit together (a typical flow)

Build UI with **[[swiftui-ui-patterns]]** and tidy it via **[[swiftui-view-refactor]]**; style with **[[swiftui-liquid-glass]]**; keep state/concurrency correct with **[[swift-concurrency-expert]]**; run and inspect it with **[[ios-debugger-agent]]**; when it's slow, audit with **[[swiftui-performance-audit]]** and profile hotspots via **[[native-app-profiling]]**; ship with **[[release-macos-spm-packaging]]** + **[[release-app-store-changelog]]**; and route bug fixes through **[[github-issue-fix-flow]]**. The general disciplines ([[clean-code]], [[software-design]], [[tdd]]) apply throughout.

## Companion subagents

These skills back several subagents (in `agents/`): **swiftui-reviewer** (read-only SwiftUI/Swift review), **ios-app-debugger** (build/run/debug on simulator), **apple-release-manager** (package + release notes), and the domain-neutral **issue-fixer**.

## Always-apply notes

- This is a **router** — defer to the specific skill for APIs, commands, and code; don't try to recall everything here.
- Swift is value-oriented and increasingly functional — the [[functional-programming]] instincts (immutability, value types, total functions) and [[clean-code]]/[[software-design]] principles carry over directly.
- For release signing/notarization, the [[secure-coding]] skill's secrets/supply-chain notes apply.

## Related

- The 10 Apple skills above.
- [[clean-code]], [[software-design]], [[tdd]], [[functional-programming]], [[design-patterns]], [[secure-coding]] — language-agnostic disciplines that apply to Swift too.
- (These Apple skills were contributed by a third party and integrated into the toolkit; this meta skill was added to route among them.)
