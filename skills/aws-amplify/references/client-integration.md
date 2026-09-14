# Client integration

Source: docs.amplify.aws (frontend build docs, how-amplify-works/concepts) + AWS's Amplify agent skill. Fetched 2026-09.

## Configure Amplify at the real entry point

Wrong location = every Amplify call silently no-ops (not an error — just empty/undefined results).

| Framework | File | Call |
|---|---|---|
| React (Vite) | `src/main.tsx` | `Amplify.configure(outputs)` |
| Next.js (App Router) | `app/layout.tsx` | `Amplify.configure(outputs, { ssr: true })` — `{ ssr: true }` is App-Router-only |
| Vue | `src/main.js` | `Amplify.configure(outputs)` |
| Angular | `src/main.ts` | `Amplify.configure(outputs)` |
| React Native | entry file, before anything else Amplify-related | see below — extra import-order rules apply |

```ts
import { Amplify } from 'aws-amplify';
import outputs from '../amplify_outputs.json';
Amplify.configure(outputs);
```

`amplify_outputs.json` must exist before the app can compile — run `npx ampx sandbox --once` first (see `hosting-and-cicd.md`).

### React Native specifics

Uses the same `aws-amplify` JS package as web (not a separate native SDK); all web client APIs apply.

```ts
import 'react-native-get-random-values';   // MUST be the first import
import '@aws-amplify/react-native';        // MUST come before aws-amplify
import { Amplify } from 'aws-amplify';
import outputs from './amplify_outputs.json';
Amplify.configure(outputs);
```
Reversing that import order breaks crypto at runtime. `@react-native-async-storage/async-storage` is required for token persistence — without it, users re-authenticate on every app restart.

## Data client

```ts
// module scope — NOT inside a component
import { generateClient } from 'aws-amplify/data';
import type { Schema } from '../amplify/data/resource';
const client = generateClient<Schema>();
```
Calling `generateClient` inside a component creates a new client per render and breaks subscriptions/caching. Omitting `<Schema>` produces an untyped client.

**CRUD** — every call returns `{ data, errors }`; check `errors` before trusting `data`:
```ts
const { data, errors } = await client.models.Todo.create({ content: 'Ship feature', priority: 'high' });
```
Same shape for `.list({ filter: { done: { eq: false } } })`, `.get({ id })`, `.update({ id, done: true })`, `.delete({ id })`. Wrap in `try/catch` too — that layer catches network failures; `errors` catches GraphQL-level ones.

**Real-time:**
```tsx
useEffect(() => {
  const sub = client.models.Todo.observeQuery().subscribe({ next: ({ items }) => setTodos(items) });
  return () => sub.unsubscribe();   // required — otherwise subscriptions accumulate across re-renders
}, []);
```
`observeQuery()` is the recommended default (auto-updating list snapshots); `onCreate()`/`onUpdate()`/`onDelete()` give per-event subscriptions. Subscriptions need a WebSocket-compatible auth mode (`userPool` or `iam`) — API-key auth on a subscription fails silently.

**Next.js Server Components** — `generateClient()` has no browser session and fails silently server-side; use the cookie-based client instead:
```ts
import { generateServerClientUsingCookies } from '@aws-amplify/adapter-nextjs/data';
import { cookies } from 'next/headers';
const cookieClient = generateServerClientUsingCookies<Schema>({ config: outputs, cookies });
```
For Server Actions/middleware, `createServerRunner` from `@aws-amplify/adapter-nextjs` gives `runWithAmplifyServerContext`.

## Auth: the `<Authenticator>` component

| Framework | Package | Tag | CSS |
|---|---|---|---|
| React / Next.js | `@aws-amplify/ui-react` | `<Authenticator>` | `@aws-amplify/ui-react/styles.css` |
| Vue | `@aws-amplify/ui-vue` | `<Authenticator>` (PascalCase — not `<authenticator>`) | `@aws-amplify/ui-vue/styles.css` |
| Angular | `@aws-amplify/ui-angular` | `<amplify-authenticator>` + `AmplifyAuthenticatorModule` | `@aws-amplify/ui-angular/theme.css` |

Missing the CSS import renders unstyled HTML. Props: `loginMechanisms={['email']}`, `socialProviders={['google']}`; render-prop slot `{({ signOut, user }) => ...}` (`user?.signInDetails?.loginId`). Next.js SSR: wrap the layout in `<Authenticator.Provider>` and read state with `useAuthenticator`.

## Auth: manual flow

Imports from `aws-amplify/auth`: `signIn`, `signUp`, `confirmSignUp`, `confirmSignIn`, `signOut`, `resetPassword`, `signInWithRedirect({ provider: 'Google' })`.

After `signIn()`, switch on `result.nextStep.signInStep` — **every** value must be handled or the flow stalls with no visible error:

| `signInStep` | Do |
|---|---|
| `DONE` | Authenticated |
| `CONFIRM_SIGN_UP` | `confirmSignUp()` |
| `CONFIRM_SIGN_IN_WITH_TOTP_CODE` / `_SMS_CODE` / `_EMAIL_CODE` | Prompt code → `confirmSignIn({ challengeResponse })` |
| `CONTINUE_SIGN_IN_WITH_TOTP_SETUP` | Show QR URI → `confirmSignIn()` |
| `CONTINUE_SIGN_IN_WITH_MFA_SELECTION` / `_MFA_SETUP_SELECTION` | `confirmSignIn({ challengeResponse: 'TOTP' \| 'SMS' \| 'EMAIL' })` |
| `RESET_PASSWORD` | `resetPassword()` |
| `CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED` | `confirmSignIn({ challengeResponse: newPassword })` |
| `CONFIRM_SIGN_IN_WITH_CUSTOM_CHALLENGE` / `_WITH_PASSWORD` | `confirmSignIn({ challengeResponse })` |
| `CONTINUE_SIGN_IN_WITH_EMAIL_SETUP` | Prompt email → `confirmSignIn()` |
| `CONTINUE_SIGN_IN_WITH_FIRST_FACTOR_SELECTION` | `confirmSignIn({ challengeResponse: selectedFactor })` |

**Session:** `getCurrentUser()` → `{ userId, username, signInDetails? }`; `fetchAuthSession()` → `{ tokens?, credentials?, identityId? }` (tokens refresh automatically — don't hand-roll refresh); `fetchUserAttributes()` → `{ email, phone_number, ... }`.

Multi-page OAuth redirects need `Hub.listen('auth', ...)` to capture the callback on reload. Don't call `updateMFAPreference()` before `signInStep === 'DONE'` — it fails silently pre-auth.

## Pitfalls

- Forgetting the `amplify_outputs.json` import in the entry point → app loads, every Amplify call is silently empty.
- `generateClient` inside a component instead of module scope.
- Missing subscription cleanup (`sub.unsubscribe()`) in `useEffect`.
- Using `generateClient()` (not the cookie variant) inside a Next.js Server Component.
- Not handling every `signInStep` value.
- React Native: wrong import order, or missing `@react-native-async-storage/async-storage`.
