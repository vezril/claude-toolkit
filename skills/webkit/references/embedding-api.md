# The WKWebView embedding API, by browser-building task

Swift naming; all WebKit types are `@MainActor`. Source: developer.apple.com/documentation/webkit (2026-07).

## Load and navigate

- `WKWebView.init(frame:configuration:)` — the configuration is **copied at init**; you cannot swap most of it afterwards. Live-mutable exceptions: userContentController contents (scripts apply next navigation, message handlers immediately), `customUserAgent`, `isInspectable`, `pageZoom`.
- Loading: `load(URLRequest)`, `loadHTMLString(_:baseURL:)`, `loadFileURL(_:allowingReadAccessTo:)` (second URL grants sandbox read scope — pass a directory to allow subresources), `load(data:mimeType:characterEncodingName:baseURL:)`, `loadSimulatedRequest(_:response:responseData:)` / `(_:responseHTML:)` (fake a response — offline pages, tests).
- Back-forward: `canGoBack`/`canGoForward` (KVO), `goBack()`/`goForward()`/`go(to: WKBackForwardListItem)`; `backForwardList` (`backList`/`forwardList`/`currentItem`) feeds a history menu. `allowsBackForwardNavigationGestures` (opt-in swipe).
- `reload()` vs `reloadFromOrigin()` (revalidates, bypasses cache); `stopLoading()`. macOS has IBAction variants wired straight to toolbar buttons.
- Chrome state, all KVO-observable: `title`, `url`, `isLoading`, `estimatedProgress` (0–1), `hasOnlySecureContent`, `serverTrust: SecTrust?` (lock icon / cert panel), `themeColor`, `underPageBackgroundColor`.
- `customUserAgent` per view; prefer `configuration.applicationNameForUserAgent` (appends a token) over full UA spoofing.
- macOS zoom: `pageZoom` (CSS zoom) and `allowsMagnification`/`magnification`/`setMagnification(_:centeredAt:)`.
- Capture: `takeSnapshot(with:)`, `createPDF(configuration:)`, `createWebArchiveData`, `printOperation(with: NSPrintInfo)` (macOS).
- Find: `find(_:configuration: WKFindConfiguration)` → `WKFindResult`; iOS also `isFindInteractionEnabled` + `findInteraction` (system panel). macOS: build your own find bar around `find`.
- `fullscreenState` (KVO; entering/in/exiting/not) — the HTML Fullscreen API only exists if `WKPreferences.isElementFullscreenEnabled = true`.
- `interactionState: Any?` — serialize/restore a tab's session (scroll, forms, back-forward) across launches.

## Intercept navigation (WKNavigationDelegate)

- `decidePolicyFor navigationAction` → `.allow`/`.cancel`/`.download`. `WKNavigationAction`: `request`, `navigationType` (linkActivated, formSubmitted, backForward, reload, other), `sourceFrame`/`targetFrame` (**nil targetFrame = new-window intent**), `shouldPerformDownload` (HTML `download` attribute), macOS `modifierFlags`/`buttonNumber` (cmd-click → new tab).
- Preferences variant hands you a mutable `WKWebpagePreferences` per navigation: `allowsContentJavaScript`, `preferredContentMode` (desktop/mobile), `isLockdownModeEnabled` (iOS 16.1/macOS 13.1), `preferredHTTPSNavigationPolicy` (iOS 17/macOS 14). This is where per-site JS toggles and desktop-mode live.
- `decidePolicyFor navigationResponse` → `.allow`/`.cancel`/`.download`; `canShowMIMEType == false` is the classic "download it" branch.
- Lifecycle: `didStartProvisionalNavigation` → (`didReceiveServerRedirect…`)* → `didCommit` (update URL bar here) → `didFinish`; failures split `didFailProvisionalNavigation` (pre-commit; **filter NSURLErrorCancelled -999 and code 102** — normal policy-cancel noise) vs `didFail` (post-commit).
- Auth: `didReceive challenge:` — `NSURLAuthenticationMethodServerTrust` (`.useCredential` with `URLCredential(trust:)` / `.performDefaultHandling`), client certificates, HTTP Basic/Digest (present your own sheet). `shouldAllowDeprecatedTLS` for TLS < 1.2.
- `webViewWebContentProcessDidTerminate` — renderer died (crash or OS jettison, routine on iOS memory pressure): reload or show crashed-tab UI, else the user sees a white rectangle.

## Popups, dialogs, permissions (WKUIDelegate)

- `createWebViewWith configuration:for:windowFeatures:` — `window.open` / `target="_blank"`. **Must** create the returned WKWebView with the passed configuration (else NSInternalInconsistencyException); present it as a tab/window yourself; return nil to block. Not implementing it dead-ends every _blank link. Pair with `webViewDidClose` for JS `window.close()`.
- JS dialogs render nothing until you implement `runJavaScriptAlertPanelWithMessage` / `…ConfirmPanel…` / `…TextInputPanel…` — call each completion handler **exactly once** or the page hangs.
- File upload (macOS): `runOpenPanelWith parameters:` → NSOpenPanel (`allowsMultipleSelection`, `allowsDirectories`).
- Media capture: `requestMediaCapturePermissionFor origin:…type:decisionHandler:` (`.grant`/`.deny`/`.prompt`; iOS 15/macOS 12); KVO `cameraCaptureState`/`microphoneCaptureState` (.none/.active/.muted) for a recording indicator; `setCameraCaptureState`/`setMicrophoneCaptureState` to mute natively. Also `pauseAllMediaPlayback`, `setAllMediaPlaybackSuspended`, `closeAllMediaPresentations`.
- `requestDeviceOrientationAndMotionPermissionFor` (iOS). Geolocation has **no WKUIDelegate hook** — CoreLocation + your app's NSLocationWhenInUseUsageDescription.
- Context menus: iOS `contextMenuConfigurationForElement` family; macOS is NOT WKUIDelegate — subclass WKWebView and override `willOpenMenu(_:with:)` to add "Open Link in New Tab".

## Inject scripts & talk JS ↔ native

- `WKUserScript(source:injectionTime:forMainFrameOnly:in:)` — `.atDocumentStart` (shims/blocking) vs `.atDocumentEnd` (content scripts); `forMainFrameOnly: false` reaches iframes; optional world.
- JS→native: `userContentController.add(handler, name:)` → `window.webkit.messageHandlers.<name>.postMessage(obj)` → `WKScriptMessage` (`body`, `frameInfo`, `world`). Async replies: `addScriptMessageHandler(_: WKScriptMessageHandlerWithReply, contentWorld:name:)` — the JS Promise resolves with your reply. **The controller retains handlers strongly** (VC→webView→config→controller→handler→VC cycle): use a weak proxy or remove handlers in teardown.
- Native→JS: `evaluateJavaScript(_:)` (main frame, **page world** — pages can interfere; errors on non-serializable or undefined results) or `evaluateJavaScript(_:in frame:in world:)`; `callAsyncJavaScript(_:arguments:in:in:)` wraps the string as an async function body (named arguments, `return`, top-level `await`, Promise-aware) — prefer it for anything non-trivial.
- `WKContentWorld`: `.page`, `.defaultClient` (your app's private world), `.world(name:)`. Worlds isolate JS state but share the DOM — run browser features in `.defaultClient`.

## Block content (the only http(s) interception)

- `WKContentRuleListStore.default()` / `init(url:)`; `compileContentRuleList(forIdentifier:encodedContentRuleList:)` compiles JSON → persisted bytecode (compile once — EasyList-scale takes seconds); `lookUpContentRuleList(forIdentifier:)` on later launches; `getAvailableContentRuleListIdentifiers`, `removeContentRuleList`.
- Rule JSON: `[{"trigger": …, "action": …}]`. Triggers: `url-filter` (restricted regex), `url-filter-is-case-sensitive`, `if-domain`/`unless-domain` (mutually exclusive), `resource-type` (document, image, style-sheet, script, font, media, raw, svg-document, popup), `load-type` (first-party/third-party), `if-top-url`. Actions: `block`, `block-cookies`, `css-display-none` (+`selector`), `ignore-previous-rules` (allowlisting), `make-https`. Order matters; later rules win via ignore-previous-rules.
- Attach per config: `userContentController.add(ruleList)` / `remove` / `removeAllContentRuleLists()`. Enforcement is declarative in the network/content process — there is **no per-request callback API**; `WKURLSchemeHandler` only serves custom schemes (`handlesURLScheme` check; http/https/file/about/blob/data are off-limits).

## Data, privacy, profiles

- `WKWebsiteDataStore.default()` (persistent, shared); `.nonPersistent()` (**private browsing**: memory-only, dies with the object, not enumerable later — keep one instance alive for all private tabs that should share cookies); `WKWebsiteDataStore(forIdentifier: UUID)` (iOS 17/macOS 14) for **profiles** (+ `fetchAllDataStoreIdentifiers`, `remove(forIdentifier:)`).
- Settings UI: `fetchDataRecords(ofTypes:)` → per-site records; `removeData(ofTypes:for:)`, `removeData(ofTypes:modifiedSince:)` ("clear last hour"). Types via `allWebsiteDataTypes()` or constants (cookies, disk/memory cache, local/session storage, IndexedDB, service workers, fetch cache…).
- Cookies: `httpCookieStore` (`getAllCookies`/`setCookie`/`delete` + `WKHTTPCookieStoreObserver`). **Distinct from `HTTPCookieStorage.shared`** — URLSession cookies and WKWebView cookies do not sync; copy explicitly.
- `proxyConfigurations` (Network framework; iOS 17/macOS 14) — per-store SOCKS/HTTP-CONNECT.

## Downloads

- Entry points: `.download` policy from either decidePolicy callback → `navigationAction/navigationResponse didBecome download:` (**set `download.delegate` synchronously** or callbacks are lost); `webView.startDownload(using:)`; `webView.resumeDownload(fromResumeData:)`.
- `WKDownloadDelegate`: required `decideDestinationUsing response:suggestedFilename:` — return a full file URL, nil cancels, and an **existing file at the path fails the download** ("file (2).ext" logic is yours). Optional: `downloadDidFinish`, `didFailWithError:resumeData:` (offer resume), redirect and challenge hooks. `WKDownload` conforms to `ProgressReporting` → observe `download.progress`.

## Process model & app-bound domains

- Content/network/GPU are separate processes; `WKProcessPool` is deprecated (iOS 15/macOS 12) and multiple instances are a no-op — share a data store, not a pool. Popup configurations preserve the `window.opener` relationship.
- `limitsNavigationsToAppBoundDomains` + `WKAppBoundDomains` Info.plist (≤ ~10 domains): outside app-bound domains, script injection/message handlers/cookie APIs are blocked. Real browsers don't use it (iOS browsers take the `com.apple.developer.web-browser` entitlement; macOS just leaves it off) — but adding the plist key by accident silently breaks injection.

## Choosing the API

- UIWebView (iOS) and legacy WebView (macOS) are deprecated — WKWebView since iOS 8/macOS 10.10 is the only path. SFSafariViewController = stock in-app Safari (iOS only, zero chrome control); ASWebAuthenticationSession = OAuth. A custom browser is always WKWebView; on macOS it's the only option anyway.
- JavaScriptCore (JSContext/JSValue/JSExport) is the engine **without** a web view — scripting/plugins/headless JS; no DOM, and you cannot reach a WKWebView page's JSContext (other process). Page work goes through evaluateJavaScript/user scripts.
- SwiftUI-native WebKit (`WebView`/`WebPage`) exists as of the 2025 SDKs (iOS 26/macOS 26); for a full-featured custom browser the WKWebView/AppKit surface remains the complete API.

## Version pins

| API | Since |
|---|---|
| WKWebView, configuration, preferences, user scripts | iOS 8 / macOS 10.10 |
| WKWebsiteDataStore (httpCookieStore) | iOS 9/10.11 (11/10.13) |
| WKURLSchemeHandler, WKContentRuleList | iOS 11 / macOS 10.13 |
| WKWebpagePreferences (+ per-navigation policy variant) | iOS 13 / macOS 10.15 |
| allowsContentJavaScript, content worlds, callAsyncJavaScript, createPDF, find, pageZoom, reply handlers | iOS 14 / macOS 11 |
| WKDownload + `.download` policies | iOS 14.5 / macOS 11.3 |
| Media-capture permission + capture state, themeColor | iOS 15 / macOS 12 |
| isElementFullscreenEnabled | iOS 15.4 / macOS 12.3 |
| fullscreenState | iOS 16 / macOS 13 |
| isLockdownModeEnabled | iOS 16.1 / macOS 13.1 |
| **isInspectable (default false)** | **iOS 16.4 / macOS 13.3** |
| Data-store identifiers (profiles), proxyConfigurations, preferredHTTPSNavigationPolicy | iOS 17 / macOS 14 |
| WKProcessPool deprecated | iOS 15 / macOS 12 |
