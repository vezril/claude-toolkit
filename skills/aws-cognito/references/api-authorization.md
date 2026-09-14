# Protecting APIs and load balancers with Cognito

Source: AWS's auth agent skill + docs.aws.amazon.com. Fetched 2026-09. Full API Gateway authorizer mechanics live in [[aws-api-gateway]]'s `authorizers.md` — this file is the Cognito-specific half.

## Choose the mechanism by front door

| Front door | Mechanism | Token used |
|---|---|---|
| **HTTP API** (API Gateway v2) | Built-in **JWT authorizer** | ID or access token |
| **REST API** (API Gateway v1) | **Cognito user pools authorizer** (`COGNITO_USER_POOLS`) | ID token by default |
| **Application Load Balancer** | Built-in `authenticate-cognito` action | ALB performs the OIDC login itself |

## HTTP API — JWT authorizer

```bash
aws apigatewayv2 create-authorizer --api-id <api-id> \
  --authorizer-type JWT --name cognito-jwt \
  --identity-source '$request.header.Authorization' \
  --jwt-configuration Audience=<app-client-id>,Issuer=https://cognito-idp.<region>.amazonaws.com/<pool-id>
```
- **Issuer** must be exactly `https://cognito-idp.<region>.amazonaws.com/<userPoolId>`.
- **Audience** must be the **app client ID**.
- The ID token carries `aud` = client ID; the access token carries `client_id` and `scope` instead. Configure and send the token type consistently — if you want scope-based route authorization, send the access token and set `authorizationScopes` on the route.

**What it does *not* enforce**: signature/`iss`/`aud`/expiry/scope only. Custom claims (`custom:tenant_id`, `cognito:groups`, anything from a `PreTokenGeneration` trigger) are **not** checked by the authorizer — validate those in your integration:
```js
const tenantId = event.requestContext.authorizer.jwt.claims["custom:tenant_id"];
const groups = event.requestContext.authorizer.jwt.claims["cognito:groups"];
if (tenantId !== requestedTenant) return { statusCode: 403, body: "wrong tenant" };
```
For heavier claim-based policy than a few `if` checks, consider a Lambda authorizer (arbitrary logic) or Amazon Verified Permissions (Cedar policies over token claims) instead of hand-rolling more conditionals.

## REST API — Cognito user pools authorizer

```bash
aws apigateway create-authorizer --rest-api-id <api-id> \
  --name cognito-authorizer --type COGNITO_USER_POOLS \
  --provider-arns arn:aws:cognito-idp:<region>:<account>:userpool/<pool-id> \
  --identity-source method.request.header.Authorization
```
Set the method's `authorizationType` to `COGNITO_USER_POOLS`, referencing the authorizer. Validates the **ID token by default** — this is a REST API detail that differs from HTTP API's more flexible token-type handling.

## Verifying tokens outside API Gateway

For a backend not sitting behind an API Gateway authorizer at all (a container, an ALB target beyond what `authenticate-cognito` already checked):
1. Fetch the pool JWKS: `https://cognito-idp.<region>.amazonaws.com/<pool-id>/.well-known/jwks.json`.
2. Verify the RS256 signature against the matching `kid`.
3. Check `iss`, `exp`, `token_use` (`id` vs `access`), `aud`/`client_id`.

Use a maintained library (`aws-jwt-verify` or equivalent) — this is exactly the kind of security-critical parsing not worth hand-rolling.

## Defense in depth (the authorizer is not the whole story)

- Attach **AWS WAF** to the API Gateway stage (managed rule groups + rate-based rules) — an authorizer authenticates callers, it doesn't blunt volumetric or token-stuffing attacks.
- Configure **throttling** on the API Gateway stage/method to cap brute-force attempts against the authorizer itself.
- Still validate and sanitize request inputs beyond the token — authorization and input validation are separate concerns.

## Common errors

| Error | Cause | Fix |
|---|---|---|
| 401 with a token that looks valid | Issuer or audience mismatch, or the wrong token type sent for this authorizer type | Match issuer/audience exactly; send the token type the authorizer expects |
| 401 despite the token being attached | Identity-source header missing, or wrong casing | Send `Authorization: <token>` exactly as configured |
| Works locally, 403 in prod | CORS preflight (OPTIONS) is being routed through the authorizer | Allow unauthenticated `OPTIONS`; configure CORS on the API (see [[aws-api-gateway]]) |

## Pitfalls

- Assuming the JWT/Cognito authorizer enforces a custom claim it was never configured to check.
- REST API sending an access token when the Cognito authorizer expects (and validates) the ID token.
- Treating authorizer + WAF + throttling as redundant layers instead of complementary ones — each catches a different failure class.
