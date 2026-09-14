# Authorizers

Source: AWS's serverless and aws-auth agent skills + docs.aws.amazon.com. Fetched 2026-09. Full Cognito setup depth lives in [[aws-cognito]] — this file covers the API Gateway side.

## Lambda authorizers (custom logic, REST or HTTP API)

| | TOKEN | REQUEST |
|---|---|---|
| Identity source | A single header (bearer token) | Headers, query strings, stage variables, `$context` — any combination |
| Cache key | The token header value | All specified identity sources, combined |
| Available on | REST API only | REST API + HTTP API |
| Recommendation | Legacy | **Preferred for new work** |

- Default cache TTL **300 seconds** (0–3600 configurable). **A cached authorization decision applies to every method/resource covered by that cache key** — not just the one that triggered the Lambda call. Don't assume a cache hit is scoped narrowly.
- **If any configured identity source is missing, null, or empty, API Gateway returns 401 without ever invoking the authorizer Lambda.** This is the first thing to check when an authorizer "isn't being called" — it may simply never be reached.
- Required Lambda authorizer response shape:
```json
{
  "principalId": "user123",
  "policyDocument": {
    "Version": "2012-10-17",
    "Statement": [{ "Action": "execute-api:Invoke", "Effect": "Allow", "Resource": "<methodArn>" }]
  },
  "context": { "...": "passed through to the integration" }
}
```
HTTP API's **native JWT authorizer needs no Lambda at all** — configure `issuer` + `audience` directly on the route.

## HTTP API — native JWT authorizer

```bash
aws apigatewayv2 create-authorizer --api-id <api-id> \
  --authorizer-type JWT --name my-jwt-authorizer \
  --identity-source '$request.header.Authorization' \
  --jwt-configuration Audience=<client-id>,Issuer=https://cognito-idp.<region>.amazonaws.com/<pool-id>
```

- Validates **signature, `iss`, `aud`/`client_id`, `exp`/`nbf`/`iat`**, and — if `authorizationScopes` is set on the route — the token's `scope`/`scp` claim.
- **Does not enforce arbitrary custom claims** — `custom:tenant_id`, `cognito:groups`, or anything added by a pre-token-generation Lambda trigger. Those must be checked in your integration/backend, not assumed to be gated at the authorizer.
- Claims are forwarded into `event.requestContext.authorizer.jwt.claims` for a Lambda integration — read and enforce custom claims there:
```js
const tenantId = event.requestContext.authorizer.jwt.claims["custom:tenant_id"];
if (tenantId !== requestedTenant) return { statusCode: 403, body: "wrong tenant" };
```
- Works with any OIDC-compliant issuer, not only Cognito.

## REST API — Cognito user pools authorizer

```bash
aws apigateway create-authorizer --rest-api-id <api-id> \
  --name cognito-authorizer --type COGNITO_USER_POOLS \
  --provider-arns arn:aws:cognito-idp:<region>:<account>:userpool/<pool-id> \
  --identity-source method.request.header.Authorization
```
Set the method's `authorizationType` to `COGNITO_USER_POOLS` and reference the authorizer. Validates the **ID token** by default — send that token type, not the access token, unless you've specifically configured otherwise.

## IAM authorization

`AWS_IAM` authorization type requires callers to sign requests with SigV4 and have `execute-api:Invoke` on the specific method ARN. Good for service-to-service calls within your own AWS account/org where the caller already has AWS credentials; poor fit for end-user-facing APIs.

## Verifying tokens yourself (no API Gateway authorizer)

If your backend sits behind something other than API Gateway (an ALB, a container directly), validate every request manually:
1. Fetch the pool's JWKS: `https://cognito-idp.<region>.amazonaws.com/<pool-id>/.well-known/jwks.json`.
2. Verify the RS256 signature against the matching `kid`.
3. Check `iss`, `exp`, `token_use` (`id` vs `access`), and `aud`/`client_id`.

Use a maintained library (e.g. `aws-jwt-verify`) — never hand-roll JWT verification.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| 401 with a token that looks valid | Issuer/audience mismatch, or the wrong token type sent | Match issuer/audience exactly; send ID token for REST/Cognito authorizer, ID or access token per your HTTP API JWT config |
| 401 "Unauthorized" even though the token is attached | Identity source header missing or wrong casing | Send exactly the header the authorizer's identity source names |
| Works locally, fails in prod with CORS-looking errors | OPTIONS preflight is being sent through the authorizer | Allow unauthenticated `OPTIONS` |

## Pitfalls

- Assuming an authorizer's cache scopes to one route — it scopes to the cache key, which can cover many routes.
- Debugging "authorizer never runs" without first checking whether the identity source is actually present on the request (the 401-before-invoke case).
- Relying on the HTTP API JWT authorizer to enforce a custom claim it was never configured to check.
- Sending an access token where the authorizer expects (and validates) an ID token, or vice versa.
