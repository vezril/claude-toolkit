---
name: aws-cognito
description: "Adding user authentication and authorization with Amazon Cognito, distilled from AWS's own auth agent skill and docs.aws.amazon.com (fetched 2026-09). Covers the user-pool-vs-identity-pool decision (authentication/OIDC IdP vs temporary AWS credentials via STS — most apps need only the former), the full-replace danger on update-user-pool-client and set-identity-pool-roles (omitted fields silently reset to defaults — always read-modify-write), hosted UI / managed login with the authorization-code-grant-with-PKCE flow (never the legacy implicit grant), social/SAML federation and the per-provider token-type table (Google/Apple pass an id_token, only Facebook/Login with Amazon pass an access token), MFA and passwordless/WebAuthn, tokens (ID/access/refresh, rotation, revocation, cookieStorage vs localStorage), identity pools (enhanced vs basic credential flow, role selection including cognito:preferred_role precedence, the confused-deputy trust-policy condition), protecting an API Gateway or ALB with Cognito (HTTP API JWT authorizer vs REST API Cognito authorizer vs ALB authenticate-cognito, and what each does and doesn't enforce), Cognito Lambda triggers, and Cognito feature-plan gating (access-token claim customization needs a paid plan). Use when adding sign-up/sign-in to an app, choosing a user pool vs identity pool, wiring social or SAML login, gating an API Gateway or ALB route behind authentication, debugging a redirect/token/MFA/CORS/federation error, or letting a signed-in browser client call AWS services directly."
license: MIT
---

# Amazon Cognito

Application-level authentication (Cognito) is not IAM, and a user pool is not an identity pool — most of the mistakes this skill exists to prevent come from conflating those. Distilled from AWS's own auth agent skill and `docs.aws.amazon.com`, fetched 2026-09. Cross-links: [[aws-api-gateway]] for the authorizer side of protecting an API, [[aws-amplify]] for Amplify Gen 2's `defineAuth` (which wraps Cognito but is configured very differently — see the note below), [[secure-coding]] for the token-storage and XSS hardening throughout.

> **Not covered here:** Amplify Gen 2 backend definitions (`defineAuth`, `npx ampx`) — see [[aws-amplify]] instead. IAM policy/role/trust-policy authoring, STS, IAM Identity Center — see `aws-iam`-shaped guidance. API Gateway route/integration setup and Lambda implementation beyond the authorizer itself — see [[aws-api-gateway]].

## User pool vs identity pool — decide this first

Two different services, constantly confused:

| Need | Use | Why |
|---|---|---|
| Sign-up/sign-in, a user directory, issuing JWTs | **User pool** | It's an authentication service and an OIDC identity provider |
| A signed-in client calling S3/DynamoDB/etc. **directly** with AWS credentials | **Identity pool** | Exchanges a token for temporary AWS credentials via STS |
| Both — sign in, then call AWS resources from the browser/app | User pool → identity pool | The identity pool trusts the user pool as its IdP |

**If your app only ever calls your own backend/API, you don't need an identity pool at all** — just send the user pool token to your API and validate it there (or at the API Gateway authorizer). Reaching for an identity pool when you don't need one is the most common over-engineering here.

## Non-negotiables

1. **`update-user-pool-client` and `set-identity-pool-roles` are full-replace calls, not partial updates.** Omit a field and it silently resets to its default — a call meant to change one setting can wipe `ExplicitAuthFlows`, token validity, `EnableTokenRevocation`, refresh-token rotation, read/write attributes, or (for identity pools) the entire roles + `RoleMappings` structure. **Always read first** (`describe-user-pool-client` / `get-identity-pool-roles`), then re-send every existing field plus your change. The call succeeds either way — the wipe is invisible until a user hits the now-missing flow.
2. **Authorization code grant with PKCE, never the implicit grant**, for any new app. The implicit grant (`response_type=token`) returns tokens in the URL fragment — legacy and insecure for SPAs/mobile. PKCE needs no client secret and is the correct default for public clients.
3. **No client secret on a public client.** A browser or mobile app cannot protect a secret; setting one on a SPA/mobile app client breaks token calls (`SECRET_HASH` required, which the browser can't safely produce) or, worse, exposes the secret. Generate secrets only for confidential (server-side) clients.
4. **Don't store refresh tokens in `localStorage` for anything high-value.** It's readable by any injected script (XSS). Prefer `cookieStorage`, keep refresh-token lifetime short, and enable refresh token rotation + token revocation on the app client.
5. **Access-token claim customization needs a paid Cognito feature plan.** The pre-token-generation trigger customizes the **ID token** on the entry-level plan; customizing the **access token** requires a paid tier — verify against current plan documentation before assuming this works.
6. **Don't bulk `admin-confirm-sign-up` on stuck `UNCONFIRMED` users.** It flips status instantly **without verifying the email**, leaving the email-verified attribute permanently false — dangerous when email drives password reset or account linking. Prefer `resend-confirmation-code` so the user re-proves ownership; reserve `admin-confirm-sign-up` for trusted/migrated accounts.
7. **Identity pools: scope the authenticated role tightly and disable guest (unauthenticated) access by default.** Only enable it when genuinely required, and even then keep its role minimal.
8. **Every protected request validates the JWT properly**: signature against the pool's JWKS, `iss`, `aud`/`client_id`, `token_use`, `exp`. Use a maintained library (`aws-jwt-verify`) — never hand-roll this.

## Common workflows

- **"Add sign-up/login to my React app"** → user pool + a public app client (no secret) → hosted UI/managed login with authorization code + PKCE → Amplify (or another) client library. See `user-pools-and-tokens.md`.
- **"Add Google/social login"** → register the social IdP on the user pool, map attributes, add the provider to the app client and hosted UI. See `federation-and-identity-pools.md`.
- **"Only signed-in users should call my API"** → HTTP API → JWT authorizer; REST API → Cognito user pools authorizer. See `api-authorization.md`.
- **"Let the browser upload to S3 after login"** → user pool for sign-in, then an identity pool to vend scoped temporary credentials. See `federation-and-identity-pools.md`.

## Quick troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `redirect_mismatch` after login | Callback URL not registered, or scheme/trailing-slash/case differs | Register the exact callback URL on the app client |
| "Unable to verify secret hash" | A client secret exists on a public (SPA/mobile) client | Recreate the client with no secret |
| 401 from API Gateway with a valid-looking token | Wrong token type or audience/issuer mismatch | HTTP API JWT authorizer expects issuer `https://cognito-idp.<region>.amazonaws.com/<pool-id>`, audience = app client ID |
| CORS errors calling the hosted UI's token endpoint | Browser calling `/oauth2/token` cross-origin, or missing CORS on your own API | Do the PKCE code exchange server-side or per the library's flow; don't proxy the token endpoint from the browser |
| Social login "user already exists" | Same email across providers creates separate identities by default | Enable attribute mapping + account linking; treat email as non-unique across IdPs |

## References

- `references/user-pools-and-tokens.md` — user pool setup, MFA, passwordless/WebAuthn, groups and precedence, token types/rotation/revocation/storage.
- `references/federation-and-identity-pools.md` — hosted UI/managed login OAuth flows, social/SAML federation, identity pools (provider token types, credential flows, role selection, the confused-deputy trust condition), and the full-replace warning in detail.
- `references/api-authorization.md` — protecting API Gateway (HTTP API JWT authorizer, REST API Cognito authorizer) and an ALB, what each does and doesn't enforce, manual JWT verification.
