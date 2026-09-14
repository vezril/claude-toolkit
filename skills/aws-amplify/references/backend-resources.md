# Backend resources: auth and functions

Source: docs.amplify.aws (build-a-backend/auth, build-a-backend/functions) + AWS's Amplify agent skill. Fetched 2026-09.

## `defineAuth` (Cognito)

```ts
// amplify/auth/resource.ts
import { defineAuth } from '@aws-amplify/backend';

export const auth = defineAuth({
  loginWith: { email: true },              // or phone: true
  userAttributes: { preferredUsername: { required: false } },
});
```

Import into `amplify/backend.ts`: `defineBackend({ auth, ... })` — nothing deploys until it's here.

**MFA:**

```ts
multifactor: { mode: 'REQUIRED' /* or 'OPTIONAL' */, totp: true, sms: true, email: true }
```
`sms`/`email` MFA each require the matching user attribute (`phone_number`/`email`) to exist on the pool.

**Passwordless** (composable with password auth and with each other):

```ts
loginWith: {
  email: { otpLogin: true },
  phone: { otpLogin: true },
  webAuthn: { relyingPartyId: 'example.com' },   // passkeys — still needs an initial email/phone signup
}
```

**Social login** — credentials always via `secret()`:

```ts
import { defineAuth, secret } from '@aws-amplify/backend';

export const auth = defineAuth({
  loginWith: {
    email: true,
    externalProviders: {
      google: {
        clientId: secret('GOOGLE_CLIENT_ID'),
        clientSecret: secret('GOOGLE_CLIENT_SECRET'),
        scopes: ['email', 'profile', 'openid'],       // omit and attributes won't populate
        attributeMapping: { email: 'email', fullname: 'name' },  // Google's `name` claim → Cognito `fullname`; values are plain strings, not objects
      },
      facebook: { clientId: secret('FB_CLIENT_ID'), clientSecret: secret('FB_CLIENT_SECRET') },
      signInWithApple: { clientId: secret('APPLE_CLIENT_ID'), teamId: secret('APPLE_TEAM_ID'), keyId: secret('APPLE_KEY_ID'), privateKey: secret('APPLE_PRIVATE_KEY') },
      loginWithAmazon: { clientId: secret('AMAZON_CLIENT_ID'), clientSecret: secret('AMAZON_CLIENT_SECRET') },
      callbackUrls: ['http://localhost:3000/', 'https://myapp.com/'],
      logoutUrls: ['http://localhost:3000/', 'https://myapp.com/'],
    },
  },
});
```
Set the secret values: `echo "<value>" | npx ampx sandbox secret set GOOGLE_CLIENT_ID` (sandbox) or `npx ampx secret set GOOGLE_CLIENT_ID --branch main --app-id $APP_ID` (hosted).

**OIDC** is supported directly (`externalProviders.oidc: [{ name, clientId, clientSecret, issuerUrl, attributeMapping }]`). **SAML is not** exposed by `defineAuth` — the high-level type has no `saml` property. Reach it via the CDK escape hatch: `backend.auth.resources.cfnResources.cfnUserPool` and a `CfnUserPoolIdentityProvider` (see `advanced-and-ops.md`).

**Cognito Lambda triggers:**

```ts
import { preSignUp } from './pre-sign-up/resource';

export const auth = defineAuth({
  loginWith: { email: true },
  triggers: { preSignUp, postConfirmation /*, preAuthentication, postAuthentication, createAuthChallenge,
    defineAuthChallenge, verifyAuthChallengeResponse, preTokenGeneration, customMessage, userMigration */ },
});
// amplify/auth/pre-sign-up/resource.ts
export const preSignUp = defineFunction({ name: 'pre-sign-up' });
```
Defining the function is not enough — it **must also appear in `triggers: {}`**, or it deploys and silently never fires.

**Guest (unauthenticated) access** is **on by default** in Gen 2 (`allowUnauthenticatedIdentities: true` on the Identity Pool). To use it in data authorization, `defineData`'s `defaultAuthorizationMode` must be `'iam'`. To disable it entirely:

```ts
const { cfnIdentityPool } = backend.auth.resources.cfnResources;
cfnIdentityPool.allowUnauthenticatedIdentities = false;
```
Default to `allow.authenticated()` for anything sensitive; if guest access is genuinely needed, scope it to read-only, non-sensitive models.

## `defineFunction` (Lambda)

```ts
// amplify/functions/my-func/resource.ts
import { defineFunction } from '@aws-amplify/backend';

export const myFunc = defineFunction({
  name: 'my-func',
  entry: './handler.ts',
  timeoutSeconds: 30,   // default 3, max 900
  memoryMB: 512,        // default 512
  runtime: 22,           // an integer (18 | 20 | 22 | 24) — NOT the string "nodejs22.x"
  environment: { TABLE_NAME: 'my-table' },
});
```

```ts
// amplify/functions/my-func/handler.ts
import type { Handler } from 'aws-lambda';
import { env } from '$amplify/env/my-func';   // typed access to `environment`, preferred over process.env

export const handler: Handler = async (event) => ({ statusCode: 200, body: JSON.stringify({ table: env.TABLE_NAME }) });
```

Sensitive values use `secret()` instead of a literal in `environment`.

**Scheduled functions:**

```ts
export const cronJob = defineFunction({
  name: 'cron-job',
  entry: './handler.ts',
  schedule: 'every 1h',        // shorthand: 'every 5m' | '1h' | '6h' | '1d', or a raw cron expression
});
```
Handler type: `EventBridgeHandler<'Scheduled Event', void, void>`.

**Granting a function access to other resources** (nothing is granted automatically):

```ts
const backend = defineBackend({ auth, data, storage, myFunc });
backend.myFunc.resources.lambda.addEnvironment('USER_POOL_ID', backend.auth.resources.userPool.userPoolId);
backend.data.resources.tables['Todo'].grantReadData(backend.myFunc.resources.lambda);
backend.storage.resources.bucket.grantReadWrite(backend.myFunc.resources.lambda);   // whole-bucket only — no per-path grant API
```
For a data model, `allow.resource(myFunc)` in its `.authorization()` array grants that function direct access through the schema.

## Exposing custom server logic

**Prefer AppSync-native custom queries/mutations** — type-safe, no separate URL:

```ts
// amplify/data/resource.ts
const schema = a.schema({
  summarize: a.query()
    .arguments({ text: a.string().required() })
    .returns(a.string())
    .handler(a.handler.function(summarizeHandler))
    .authorization(allow => [allow.authenticated()]),
});
```
Call from the client: `await client.queries.summarize({ text: '...' })`.

**Reach for API Gateway only when you need a REST/HTTP URL** (webhooks, third-party callbacks):

```ts
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
const apiStack = backend.createStack('RestApiStack');    // stack names must be unique across the backend
const api = new apigateway.RestApi(apiStack, 'MyRestApi', { restApiName: 'my-rest-api', deployOptions: { stageName: 'prod' } });
api.root.addResource('items').addMethod('GET', new apigateway.LambdaIntegration(backend.myFunc.resources.lambda));
backend.addOutput({ custom: { restApiUrl: api.url } });   // read this from amplify_outputs.json client-side
```
REST API (v1) handlers use `APIGatewayProxyHandler` (`event.httpMethod`); the lighter HTTP API (v2, via `aws-cdk-lib/aws-apigatewayv2` + `HttpLambdaIntegration`) uses `APIGatewayProxyHandlerV2` (`event.requestContext.http.method`). Mixing the two handler types produces malformed responses with no clear error.

## Pitfalls

- Trigger defined but not registered in `triggers: {}` → silent no-op.
- Hardcoded OAuth/API credentials instead of `secret()`.
- `runtime` as a string (`"nodejs22.x"`) instead of an integer → build error.
- A function with no explicit grant cannot touch auth/data/storage — grants are opt-in, always.
- Duplicate `backend.createStack()` names anywhere in the backend → deployment failure.
