# CDK escape hatches, extra services, security, and Gen 1

Source: docs.amplify.aws (build-a-backend/add-aws-services) + AWS's Amplify agent skill. Fetched 2026-09.

## When Amplify's high-level API isn't enough

Two escape hatches, same idea as CDK L1 constructs vs L2/L3: reach for these only when `define*` genuinely doesn't expose what you need.

**Custom CDK stacks** — for resources Amplify has no `define*` for at all (SNS topics, Geo, PubSub/IoT, arbitrary CDK constructs):
```ts
const backend = defineBackend({ auth, data });
const customStack = backend.createStack('AnalyticsStack');   // name must be unique across the whole backend
import * as sns from 'aws-cdk-lib/aws-sns';
const topic = new sns.Topic(customStack, 'NotificationTopic');
const userPool = backend.auth.resources.userPool;             // Amplify resources are reachable from custom stacks
```

**Resource overrides** — for properties on resources Amplify *does* manage, but doesn't expose a setter for:
```ts
// Cognito: a stronger password policy than defineAuth exposes
const cfnUserPool = backend.auth.resources.cfnResources.cfnUserPool;
cfnUserPool.policies = { passwordPolicy: { minimumLength: 12, requireLowercase: true, requireUppercase: true, requireNumbers: true, requireSymbols: true } };

// DynamoDB: point-in-time recovery, billing mode, TTL
const { cfnResources } = backend.data.resources;
cfnResources.amplifyDynamoDbTables['Todo'].pointInTimeRecoveryEnabled = true;
cfnResources.amplifyDynamoDbTables['Todo'].billingMode = 'PAY_PER_REQUEST';
cfnResources.amplifyDynamoDbTables['Todo'].timeToLiveAttribute = { attributeName: 'ttl', enabled: true };
```
For a new GSI, prefer the schema-native `.secondaryIndexes()` (see `data-modeling.md`) over a CDK override.

**Custom outputs** — surface any value (a topic ARN, a third-party endpoint) to the frontend through the same generated file the rest of the config comes from:
```ts
backend.addOutput({ custom: { analyticsTopicArn: topic.topicArn } });
// frontend reads it from amplify_outputs.json after Amplify.configure()
```

## Geo, PubSub, Face Liveness (brief)

These have no `define*` — they're CDK-only:

- **Geo** (maps, place search): `aws-cdk-lib/aws-location` (`CfnPlaceIndex`, `CfnMap`) in a custom stack, IAM granted explicitly to the authenticated role, `@aws-amplify/geo` client-side.
- **PubSub** (real-time via IoT Core): an IoT endpoint plus an IAM policy on `backend.auth.resources.authenticatedUserIamRole` for `iot:Connect/Publish/Subscribe/Receive`; client via `@aws-amplify/pubsub`'s `PubSub.subscribe()`/`.publish()` — always `.unsubscribe()` in cleanup (React: inside `useEffect`'s return).
- **Face Liveness** (Rekognition): IAM grants for `rekognition:CreateFaceLivenessSession` etc. on the authenticated role; `@aws-amplify/ui-react-liveness`'s `<FaceLivenessDetector sessionId region onAnalysisComplete>` (parallel Swift/Android UI packages exist). None of these services get IAM access automatically — it's always an explicit grant.

Full setup: `docs.amplify.aws/react/build-a-backend/add-aws-services/`.

## Security checklist

- `secret()` for every credential/API key — never a literal, never a plain `environment` value.
- Treat `allow.guest()`/`allow.guest`(default-on Identity Pool) as a deliberate choice, not a default to leave alone.
- Scope IAM policies to specific resource ARNs; avoid `resources: ['*']` in production overrides.
- Never log secrets or put them in error messages.
- CloudTrail + CloudWatch alarms on Amplify-managed resources; access logging on S3, AppSync, API Gateway.
- Security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options) via `customHeaders` in `amplify.yml`.
- WAF in front of public-facing AppSync/API Gateway endpoints; throttling/rate limiting enabled on both.
- CI/CD and Lambda execution roles use short-lived IAM roles, never long-lived access keys.
- KMS-encrypt CloudWatch Log groups that may carry PII/tokens/secrets, with a retention policy set.
- AppSync schema validation and API Gateway request validators on, to reject malformed input at the edge.
- ACM-managed TLS on custom domains (Amplify Hosting provisions this automatically — verify it's actually attached).

See also [[secure-coding]] for the general injection/secrets/TLS hardening this sits on top of.

## Gen 1 vs Gen 2 (recognize it, don't migrate it here)

| Signal | Gen 1 | Gen 2 |
|---|---|---|
| Directory | `amplify/.config/`, `amplify/backend/<category>/` | `amplify/backend.ts` |
| Provisioning | `amplify push` via CLI wizard, or Amplify Studio | `npx ampx sandbox` / `pipeline-deploy`, TypeScript-defined |
| package.json | no `@aws-amplify/backend` devDependency | `@aws-amplify/backend` devDependency present |

If a project shows Gen 1 signals, this skill doesn't apply — treat it as a separate migration project rather than mixing CLI-based and code-first provisioning in the same app.

## Troubleshooting index (the silent failures, in one place)

| Symptom | Likely cause |
|---|---|
| Blank page in production only | Wrong `amplify.yml` `baseDirectory` for the framework |
| Build fails on a missing module import | `amplify_outputs.json` doesn't exist yet — run `npx ampx sandbox --once` |
| Every Amplify API call returns empty/undefined | `Amplify.configure()` missing or in the wrong entry file |
| Relationship field is `null`/`undefined` | Missing `belongsTo`/`hasMany` on one side, or FK typed `a.string()` instead of `a.id()` |
| A data or storage rule "does nothing" | Missing `.to([...])`, or (storage) path missing trailing `/*` |
| Auth trigger never fires | Defined with `defineFunction` but not added to `triggers: {}` |
| Sign-in flow hangs with no error | An unhandled `signInStep` value |
| Subscriptions duplicate / memory grows | Missing `sub.unsubscribe()` in cleanup |
| CI backend deploy: `AccessDeniedException` | Missing the `AmplifyBackendRole` IAM service role on the app |
| Agent/CI run never exits | Ran `npx ampx sandbox` without `--once` |
| `create-app` fails silently | Repository passed as a `https://` URL instead of `github.com/user/repo` |
