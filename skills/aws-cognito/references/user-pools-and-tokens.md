# User pools and tokens

Source: AWS's auth agent skill + docs.aws.amazon.com (cognito/latest/developerguide). Fetched 2026-09.

## User pool basics

A user pool is a managed user directory and OIDC identity provider: sign-up, sign-in, password reset, MFA, and JWT issuance. Configure:
- **Login attributes** — email and/or phone and/or username.
- **Password policy** — length, character requirements, temporary-password expiry.
- **App clients** — one per application/platform, each with its own auth flows and secret policy (see `SKILL.md` non-negotiable #3).

## MFA

- **TOTP** (authenticator app) and **SMS** are the two classic factors; **email OTP** is also available.
- Set the pool's MFA mode to **required** (every user must enroll) or **optional** (users opt in).
- SMS MFA needs a verified phone number attribute on the user; email MFA needs a verified email attribute — enabling the MFA method without the matching attribute configured is a common setup gap.

## Passwordless and WebAuthn/passkeys

Passwordless methods (email OTP, SMS OTP) and WebAuthn (passkeys) can be enabled **alongside** password-based auth — not an either/or choice. Passkey enrollment uses the `USER_AUTH` flow with `AllowedFirstAuthFactors`; a user still needs an initial email/phone-based signup before enrolling a passkey, since the passkey is associated with an existing account rather than being a standalone signup method.

## User pool groups

Groups let you bucket users for coarse-grained authorization (`cognito:groups` claim on the token).
```bash
aws cognito-idp create-group --user-pool-id <pool-id> --group-name Admins --precedence 1
aws cognito-idp admin-add-user-to-group --user-pool-id <pool-id> --username <user> --group-name Admins
```
**`Precedence`** matters when a user belongs to multiple groups and you're using identity-pool role-from-token mapping: **the group with the lowest `Precedence` value wins** for `cognito:preferred_role` (see `federation-and-identity-pools.md`).

## Tokens

Three token types, all JWTs, issued together on successful sign-in:

| Token | Carries | Typical use |
|---|---|---|
| **ID token** | User identity claims (`sub`, `email`, custom attributes, `cognito:groups`) | Prove who the user is; default token for REST API Cognito authorizers |
| **Access token** | `client_id`, `scope` | Authorize API calls by scope; carries fewer identity claims than the ID token |
| **Refresh token** | Opaque, used to mint new ID/access tokens | Kept longer-lived; the thing you actually need to protect carefully |

- **Rotation**: enable refresh token rotation so each use issues a new refresh token and invalidates the old one — limits the blast radius of a leaked refresh token.
- **Revocation**: enable token revocation on the app client so a compromised or logged-out session's tokens can actually be invalidated, not just left to expire naturally.
- **Session termination** has three distinct operations that are easy to conflate: **global sign-out** (invalidate all of a user's tokens across devices), **revoke** (invalidate one specific refresh token), and **disable** (prevent the user from signing in at all, existing tokens unaffected until they expire or are separately revoked). Pick the one that actually matches the intended effect.
- **Storage**: the Amplify client library defaults to `localStorage`, which is XSS-readable. For anything high-value, switch to `cookieStorage`, keep refresh-token lifetime short, and lean on rotation + revocation rather than trusting storage alone.

## Cognito Lambda triggers

Triggers let you run custom logic at specific points in the auth lifecycle:

| Trigger | Fires |
|---|---|
| `PreSignUp` | Before account creation — validate/allowlist, auto-confirm |
| `PostConfirmation` | After signup confirmation — provision downstream resources |
| `PreAuthentication` / `PostAuthentication` | Around each sign-in |
| `PreTokenGeneration` | Before tokens are issued — customize claims (ID token on entry plan; access token needs a paid plan, see `SKILL.md`) |
| `CustomMessage` | Customize verification/invite emails and SMS |
| `CreateAuthChallenge` / `DefineAuthChallenge` / `VerifyAuthChallengeResponse` | Build a fully custom authentication flow (e.g. a non-standard MFA factor) |
| `UserMigration` | Lazily migrate users from a legacy auth system on first sign-in |

## Pitfalls

- Enabling SMS or email MFA without the corresponding verified attribute present on user accounts.
- Assuming `PreTokenGeneration` can customize the access token on the entry-level feature plan — it can't; only the ID token, without the paid tier.
- Confusing global sign-out, revoke, and disable — they have materially different effects and none is a superset of another.
- Leaving refresh tokens in `localStorage` on an app that handles anything sensitive.
- Setting group precedence without realizing it drives `cognito:preferred_role` resolution when identity pools are involved.
