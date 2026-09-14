# Federation, hosted UI, and identity pools

Source: AWS's auth agent skill + docs.aws.amazon.com. Fetched 2026-09.

## Hosted UI / managed login and OAuth flows

Cognito's hosted UI (managed login) handles the sign-in page and OAuth token exchange for you.

- **Use the authorization code grant with PKCE** (`response_type=code` + `code_challenge`) for SPAs and mobile — public clients, no secret. **Never the implicit grant** for new apps (see `SKILL.md`).
- **Machine-to-machine** (service calling service, no user) uses the **client credentials grant** against a **resource server** with **custom scopes** — a different flow from user sign-in entirely, with a confidential client (secret required, since there's no browser to protect).
- **Custom domain** for the hosted UI needs an ACM certificate in **`us-east-1`**, regardless of which region the user pool itself lives in — the same cross-region certificate quirk as CloudFront.
- Callback/logout URLs must be registered exactly (scheme, host, path, trailing slash) — see the `redirect_mismatch` troubleshooting entry in `SKILL.md`.

## Social and SAML federation

Register the external IdP on the user pool, map its claims to Cognito attributes, then add the provider to both the app client and the hosted UI.

**Critical: the token type each provider hands to an *identity pool* is provider-specific** (this table matters when you're also using an identity pool, not just the user pool):

| Provider | Artifact passed to the identity pool |
|---|---|
| Cognito user pool | ID token |
| Generic OIDC IdP | ID token |
| Google | ID token (`id_token`) |
| Apple | ID token (`id_token`) |
| Facebook | **Access token** |
| Login with Amazon | **Access token** |
| SAML 2.0 IdP | SAML assertion |

Google and Apple are OIDC providers — wire them with their `id_token`. Only Facebook and Login with Amazon hand over an access token. Getting this backwards (e.g. configuring Google with an access token) fails identity resolution at configuration time, not silently at runtime.

Social login gotcha: the **same email across two different providers creates two separate Cognito users by default** — enable attribute mapping and account linking if you want "sign in with Google" and "sign in with email" to resolve to one account for the same person.

## Identity pools (federated identities)

An identity pool exchanges a proof of authentication for **temporary AWS credentials** via STS. Only add one if the client needs to call AWS services directly (see `SKILL.md`'s decision table).

```bash
aws cognito-identity create-identity-pool \
  --identity-pool-name my_app_identities \
  --no-allow-unauthenticated-identities \
  --cognito-identity-providers ProviderName=cognito-idp.<region>.amazonaws.com/<pool-id>,ClientId=<app-client-id>

aws cognito-identity set-identity-pool-roles \
  --identity-pool-id <identity-pool-id> \
  --roles authenticated=<auth-role-arn>
```

**`set-identity-pool-roles` is a full replace of the roles + `RoleMappings` structure.** To add or change one mapping on a pool that already has others configured: `get-identity-pool-roles` first, then re-send every existing role and mapping plus your addition in one call. Sending only the new mapping silently drops the existing default role and every other mapping — invisible until an affected user's credentials stop resolving correctly.

**The authenticated role's trust policy must scope to this specific identity pool**, or another identity pool could assume it (confused deputy):
```json
"Condition": {
  "StringEquals": { "cognito-identity.amazonaws.com:aud": "<identity-pool-id>" },
  "ForAnyValue:StringLike": { "cognito-identity.amazonaws.com:amr": "authenticated" }
}
```
The `:aud` condition binds trust to your specific pool; `:amr: authenticated` ensures the guest role can never assume the authenticated role (mirror with `:amr: unauthenticated` on the guest role itself).

**Default to `--no-allow-unauthenticated-identities`.** Only enable guest access when genuinely required, with its own tightly-scoped role.

### Credential flows

- **Enhanced (simplified) flow** — recommended default. `GetCredentialsForIdentity` returns credentials in one call; the pool decides the role.
- **Basic (classic) flow** — the app calls `GetOpenIdToken` then `sts:AssumeRoleWithWebIdentity` itself, for full control over which role gets assumed.

### Role selection

- **Default role** — applies to all authenticated users absent other rules.
- **Rules-based** — pick a role from token claims (e.g. a specific claim value).
- **Role from token** (`cognito:preferred_role`) — driven by the user pool group's associated role; when a user is in multiple groups, **the group with the lowest `Precedence` wins** (see `user-pools-and-tokens.md`).
- **Attributes for access control** — map user claims to STS **principal tags**, then gate access in resource policies with `aws:PrincipalTag/...` — app-level ABAC layered on top of Cognito.

Scope the authenticated role to least privilege — the actual IAM policy authoring is general IAM practice, not Cognito-specific, but the trust-policy condition above is.

## Common identity pool errors

| Error | Cause | Fix |
|---|---|---|
| `NotAuthorizedException` / "Token is not from a supported provider" | Provider not registered on the pool, or wrong `ClientId` | Match `ProviderName` = `cognito-idp.<region>.amazonaws.com/<pool-id>` and the correct app client ID |
| Access denied after getting credentials | Role permissions too narrow, or trust policy misconfigured | Fix the role's permissions; confirm it trusts `cognito-identity.amazonaws.com` with the pool-id condition |
| Guests unexpectedly allowed | Unauthenticated identities enabled somewhere along the way | Disable guest access; remove the unauthenticated role |

## Pitfalls

- Wiring Google/Apple with an access token instead of an ID token (or Facebook/LWA the reverse).
- Calling `set-identity-pool-roles` with only the new mapping, wiping existing ones.
- An authenticated-role trust policy with no `:aud` condition — any identity pool can assume it.
- Treating same-email social sign-ins as automatically linked — they aren't, by default.
