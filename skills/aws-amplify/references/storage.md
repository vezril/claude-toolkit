# Storage (`defineStorage` — S3)

Source: docs.amplify.aws (build-a-backend/storage) + AWS's Amplify agent skill. Fetched 2026-09.

## Backend

```ts
// amplify/storage/resource.ts
import { defineStorage } from '@aws-amplify/backend';

export const storage = defineStorage({
  name: 'myFiles',
  access: (allow) => ({
    'public/*': [
      allow.guest.to(['read']),                                    // PROPERTY — no parens, unlike data rules
      allow.authenticated.to(['read', 'write', 'delete']),
    ],
    'protected/{entity_id}/*': [
      allow.authenticated.to(['read']),
      allow.entity('identity').to(['read', 'write', 'delete']),    // {entity_id} only works paired with this
    ],
    'private/{entity_id}/*': [
      allow.entity('identity').to(['read', 'write', 'delete']),
    ],
  }),
});
```
Import into `backend.ts` alongside `auth` (needed for `allow.entity('identity')` to resolve).

**Rule anatomy:**
- Subjects: `allow.guest`, `allow.authenticated`, `allow.groups(['Admins'])`, `allow.entity('identity')` — all **properties**, no `()`. (Contrast `defineData`'s `allow.guest()`, which *is* a method call — the asymmetry is a common source of TypeScript errors.)
- Actions: `'read'`, `'write'`, `'delete'`, or the granular `'get'`/`'list'` in place of `'read'`.
- Every rule **must end in `.to([...])`** — omit it and the rule grants nothing, silently.
- Paths **must end in `/*`** to match objects under that prefix, and **must not start with `/`**.
- `{entity_id}` resolves to the caller's Cognito identity ID at runtime, giving each user an isolated subtree — but only takes effect where `allow.entity('identity')` is also present for that path.

## Multiple buckets

```ts
export const primaryStorage = defineStorage({ name: 'primaryFiles', isDefault: true, access: (allow) => ({ /* ... */ }) });
export const secondaryStorage = defineStorage({ name: 'secondaryFiles', access: (allow) => ({ /* ... */ }) });
```
Exactly one bucket needs `isDefault: true`; every bucket needs a unique `name` (clients reference non-default buckets by that name).

## Event triggers

```ts
const onUploadHandler = defineFunction({ entry: './on-upload-handler.ts' });
export const storage = defineStorage({
  name: 'myFiles',
  triggers: { onUpload: onUploadHandler, onDelete: onUploadHandler },
  access: (allow) => ({ 'public/*': [allow.authenticated.to(['read', 'write'])] }),
});
```
```ts
import type { S3Handler } from 'aws-lambda';
export const handler: S3Handler = async (event) => {
  const keys = event.Records.map(r => r.s3.object.key);
};
```
Import the trigger function into `backend.ts` like any other function.

## Client (`aws-amplify/storage`)

| Operation | Call |
|---|---|
| Upload | `uploadData({ path: 'public/file.txt', data })` — returns a task with `.pause()/.resume()/.cancel()` and `.result` (a Promise); progress via `options.onProgress` |
| Download | `(await downloadData({ path }).result).body.blob()` |
| Presigned URL | `await getUrl({ path })` — default 15-minute expiry |
| List | `await list({ path: 'public/' })` → `{ items }` |
| Remove | `await remove({ path })` |
| Copy | `await copy({ source: { path }, destination: { path } })` |

`options: { bucket: 'nameFromDefineStorage' }` or `{ bucket: { bucketName, region } }` targets a non-default bucket — a raw ARN does not work.

**React UI components** (`@aws-amplify/ui-react-storage`): `<StorageBrowser />`, `<StorageImage />`, `<FileUploader />`. Import **both** `@aws-amplify/ui-react/styles.css` and `@aws-amplify/ui-react-storage/styles.css`, or components render unstyled — the second import is easy to miss.

## Security notes

- SSE-S3 server-side encryption is on by default; for sensitive data consider SSE-KMS with a customer-managed key via a CDK override.
- HTTPS-only access is enforced by default; if you customize the bucket via CDK, add an explicit `Deny` statement on `"aws:SecureTransport": "false"` to preserve that.

## Pitfalls

- Path without trailing `/*` → matches nothing.
- Rule without `.to([...])` → grants nothing, no error.
- `'private/*'` instead of `'private/{entity_id}/*'` → exposes every user's private files to all authenticated users.
- Leading `/` on a path → doesn't match.
- Multiple buckets, none marked `isDefault: true` → client operations fail to resolve a bucket.
- `grantReadWrite(lambda)` operates on the **whole bucket** — there's no per-path grant API for functions.
