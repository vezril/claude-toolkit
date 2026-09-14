# Data modeling (`defineData` — AppSync + DynamoDB)

Source: docs.amplify.aws (build-a-backend/data) + AWS's Amplify agent skill. Fetched 2026-09.

## Schema and client typing

```ts
// amplify/data/resource.ts
import { type ClientSchema, a, defineData } from '@aws-amplify/backend';

const schema = a.schema({
  Todo: a.model({
    content: a.string().required(),
    priority: a.enum(['low', 'medium', 'high']),
    done: a.boolean().default(false),
    dueDate: a.date(),
  }).authorization(allow => [allow.owner()]),
});

export type Schema = ClientSchema<typeof schema>;   // MUST export this — without it the frontend client is untyped
export const data = defineData({
  schema,
  authorizationModes: { defaultAuthorizationMode: 'userPool' },
});
```
Import `data` into `backend.ts`, or none of it deploys.

**Field types:** `a.string()`, `a.integer()`, `a.float()`, `a.boolean()`, `a.date()`, `a.datetime()`, `a.timestamp()`, `a.time()`, `a.email()`, `a.url()`, `a.phone()`, `a.ipAddress()`, `a.json()`, `a.id()`, `a.enum([...])`. Chain `.required()` / `.array()` on any field. `.default(value)` works on scalars only — **it silently does nothing on `a.enum()` fields**.

## Authorization — six strategies

```ts
a.model({ /* fields */ }).authorization(allow => [
  allow.publicApiKey().to(['read']),   // open, unauthenticated, via API key
  allow.guest().to(['read']),          // unauthenticated via IAM — needs defaultAuthorizationMode: 'iam'
  allow.owner(),                       // record creator gets full CRUD
  allow.authenticated().to(['read']),  // any signed-in user
  allow.group('Admins'),               // named Cognito group
  allow.custom(),                      // Lambda authorizer
])
```
`allow.publicApiKey()` and `allow.guest()` both mean *unauthenticated can access this* — reserve them for genuinely public, non-sensitive data; default to `allow.authenticated()` or `allow.owner()` otherwise.

**Field-level rules override the model-level rule** for that field:
```ts
Post: a.model({
  title: a.string(),
  secret: a.string().authorization(allow => [allow.owner()]),
}).authorization(allow => [allow.authenticated().to(['read'])])
```

**Multi-owner / dynamic groups:** `allow.ownersDefinedIn('editors')` with an `editors: a.string().array()` field grants ownership to a list of users; `allow.groupsDefinedIn('teamGroups')` does the same for group names stored per-record.

**`defaultAuthorizationMode` must match a strategy actually used** in the schema: `userPool` ↔ `owner()`/`authenticated()`/`group()`; `apiKey` ↔ `publicApiKey()` (needs `apiKeyAuthorizationMode: { expiresInDays }` set too); `iam` ↔ `guest()`. A mismatch (e.g. `publicApiKey()` in a rule but `userPool` as default with no `apiKeyAuthorizationMode`) rejects the corresponding requests.

## Relationships

```ts
const schema = a.schema({
  Team: a.model({
    name: a.string().required(),
    members: a.hasMany('Member', 'teamId'),          // parent side
  }).authorization(allow => [allow.owner()]),

  Member: a.model({
    name: a.string().required(),
    teamId: a.id().required(),                        // FK — MUST be a.id(), not a.string()
    team: a.belongsTo('Team', 'teamId'),               // child side — REQUIRED, not implied by hasMany
    profile: a.hasOne('Profile', 'memberId'),
  }).authorization(allow => [allow.owner()]),

  Profile: a.model({
    bio: a.string(),
    memberId: a.id().required(),
    member: a.belongsTo('Member', 'memberId'),
  }).authorization(allow => [allow.owner()]),
});
```
The second argument to `hasMany`/`belongsTo`/`hasOne` is the foreign-key field name, and that field must be declared explicitly on the child. **Both sides are required** — omit `belongsTo` on the child (or `hasMany` on the parent) and lazy-loading the relation returns `undefined` with no error. Using `a.string()` instead of `a.id()` for the FK causes the same kind of silent resolution failure.

Subscriptions on models with mismatched authorization between parent and child redact relational fields to null/empty rather than leaking data across permission boundaries — expected behavior, not a bug, when it happens.

## Secondary indexes

```ts
Todo: a.model({ content: a.string(), status: a.string(), createdAt: a.datetime() })
  .secondaryIndexes(index => [ index('status').sortKeys(['createdAt']).queryField('listByStatus') ])
```
Enables `client.models.Todo.listByStatus({ status: 'active' })`. Name `queryField` descriptively — it becomes the generated client method name.

## Enums and custom types

```ts
const schema = a.schema({
  Priority: a.enum(['low', 'medium', 'high']),          // top-level, reusable
  Location: a.customType({ lat: a.float(), lng: a.float() }),

  Task: a.model({
    title: a.string().required(),
    priority: a.ref('Priority'),        // reference a top-level enum
    location: a.ref('Location'),        // reference a custom type
  }).authorization(allow => [allow.owner()]),
});
```
Enums can also be declared inline on a field (`priority: a.enum(['low','medium','high'])`) without a top-level definition.

## Custom queries and mutations

```ts
const schema = a.schema({
  // ...models...
  placeOrder: a.mutation()
    .arguments({ productId: a.id().required(), qty: a.integer() })
    .returns(a.json())
    .handler(a.handler.function('orderHandler'))
    .authorization(allow => [allow.authenticated()]),
});
```
The handler name must match a `defineFunction` imported into `backend.ts`. Call from the client as `client.mutations.placeOrder({ productId, qty })` — same shape as a model operation.

## Pitfalls

- Missing `export type Schema = ClientSchema<typeof schema>` → `generateClient<Schema>()` has nothing to type against.
- FK field typed `a.string()` instead of `a.id()` → relationship queries return `null`/`undefined`, no error.
- One-sided relationship declarations → same silent failure.
- `.default()` on an `a.enum()` field → silently ignored at deploy time.
- `defaultAuthorizationMode` that doesn't match any rule actually used in the schema → requests using the unmatched strategy are rejected.
- Forgetting to import `data` into `backend.ts` → the schema never deploys, no local error.
