# Scaffolding, hosting, and CI/CD

Source: docs.amplify.aws (deploy-and-host/*, start/*) + AWS's Amplify agent skill. Fetched 2026-09.

## Scaffolding

**Use official starter templates for greenfield web projects** — don't hand-build the directory structure; a nonstandard layout can break Amplify Hosting's build detection.

```bash
git clone https://github.com/aws-samples/amplify-vite-react-template.git my-app   # React
git clone https://github.com/aws-samples/amplify-next-template.git my-app        # Next.js App Router
git clone https://github.com/aws-samples/amplify-next-pages-template.git my-app  # Next.js Pages Router
git clone https://github.com/aws-samples/amplify-vue-template.git my-app         # Vue
git clone https://github.com/aws-samples/amplify-angular-template.git my-app     # Angular
cd my-app && rm -rf .git && git init && npm install
```

**Adding Gen 2 to an existing (brownfield) project:**
```bash
npm create amplify@latest -y      # scaffolds amplify/, installs backend deps; -y for non-interactive runs
npm install aws-amplify           # the frontend client library
```
For monorepos/custom pipelines where the create command conflicts, install manually (`@aws-amplify/backend`, `@aws-amplify/backend-cli`, `typescript` as devDependencies) and hand-write a minimal `amplify/backend.ts` with `defineBackend({})`.

**React Native / mobile:** scaffold the platform project first (`create-expo-app`, RN CLI `init`, `flutter create`, or an existing Xcode/Android Studio project), then run `npm create amplify@latest -y` inside it, then add the platform-specific Amplify packages. Never generate the Xcode or Android Studio project itself from the CLI — assume it already exists.

**After scaffolding, generate outputs before running the app:**
```bash
npx ampx sandbox --once   # generates amplify_outputs.json
npm run dev                # only works after the line above
```
The single most common setup mistake is running the dev server before the first sandbox deploy.

## Sandbox (personal dev environment)

```bash
AWS_REGION=us-east-1 npx ampx sandbox --once
```
`--once` deploys, writes `amplify_outputs.json`, and exits — required in any agent/CI/non-interactive context, since bare `npx ampx sandbox` starts a file watcher that never returns. First run in a fresh account/region may need CDK bootstrapping; follow the prompt, then rerun `--once`.

## CI/CD (Amplify Hosting)

```bash
# 1. Create the app — MUST be github.com/user/repo, not a https:// URL
APP_ID=$(aws amplify create-app --name my-app \
  --repository "github.com/<user>/<repo>" --access-token "$(gh auth token)" \
  --query 'app.appId' --output text)

# 2. A dedicated IAM role for backend deploys — skipping this = AccessDeniedException on every deploy
ROLE_NAME="AmplifyBackendRole-${APP_ID}"
aws iam create-role --role-name "$ROLE_NAME" --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [{"Effect": "Allow", "Principal": {"Service": "amplify.amazonaws.com"}, "Action": "sts:AssumeRole"}]
}'
aws iam attach-role-policy --role-name "$ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmplifyBackendDeployFullAccess
ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
aws amplify update-app --app-id "$APP_ID" --iam-service-role-arn "$ROLE_ARN"

# 3. A branch, and a build
aws amplify create-branch --app-id "$APP_ID" --branch-name main
aws amplify start-job --app-id "$APP_ID" --branch-name main --job-type RELEASE
```

**`amplify.yml`:**
```yaml
version: 1
backend:
  phases:
    build:
      commands:
        - npm ci --cache .npm --prefer-offline
        - npx ampx pipeline-deploy --branch $AWS_BRANCH --app-id $AWS_APP_ID
frontend:
  phases:
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist     # see table below — wrong value silently ships a blank page
    files: ['**/*']
  cache:
    paths: ['.npm/**/*', 'node_modules/**/*']
```

| Framework | `baseDirectory` |
|---|---|
| Vite (React/Vue) | `dist` |
| Create React App | `build` |
| Next.js, static export | `out` |
| Next.js, SSR | `.next` |
| Angular | `dist/<project-name>/browser` |

For SSR Next.js, Amplify Hosting deploys the necessary edge/CloudFront wiring automatically — no manual CloudFront setup needed. Production URL shape: `https://<branch>.<app-id>.amplifyapp.com`, or a custom domain (below).

### Monorepos

```yaml
appRoot: packages/web   # NO leading slash — "/packages/web" breaks path resolution
```
Only **one** app in the monorepo runs `npx ampx pipeline-deploy`; every other app pulls its outputs with `npx ampx generate outputs --app-id <backend-app-id>`. Run `npm ci` at the repo root, not inside `appRoot`.

## Secrets

- **Sandbox:** `npx ampx sandbox secret set MY_API_KEY` (prompts interactively — don't pass the value as a CLI arg or via `echo`, both land in shell history). To pipe from a secure source: `aws ssm get-parameter --name /path --with-decryption --query Parameter.Value --output text | npx ampx sandbox secret set MY_SECRET --from-stdin`.
- **Hosted branches:** `npx ampx secret set MY_API_KEY --branch main --app-id $APP_ID`, or the Hosting console's Environment variables page. **Sandbox secrets do not carry over to Hosting** — they're set again per-branch.
- `aws amplify update-app --environment-variables KEY=value` stores **plain text** — fine for non-sensitive config, wrong for anything sensitive (use the `secret()`-backed path instead, which is SSM `SecureString` under the hood).

## Multi-environment (branch-per-environment)

```bash
git checkout -b staging && git push origin staging
aws amplify create-branch --app-id "$APP_ID" --branch-name staging
aws amplify start-job --app-id "$APP_ID" --branch-name staging --job-type RELEASE
```
Each branch gets fully isolated backend resources (its own Cognito pool, AppSync API, DynamoDB tables) and its own secrets.

## Custom domains

```bash
aws amplify create-domain-association --app-id "$APP_ID" --domain-name example.com \
  --sub-domain-settings '[{"prefix":"","branchName":"main"},{"prefix":"staging","branchName":"staging"}]'
aws amplify get-domain-association --app-id "$APP_ID" --domain-name example.com   # check verification status
```
Amplify provisions the TLS certificate; you add the returned CNAME records to your DNS.

## Rollback

```bash
git revert HEAD --no-edit && git push origin main    # Amplify auto-triggers a rebuild from the push
# or, to redeploy the current HEAD without a new commit:
aws amplify start-job --app-id "$APP_ID" --branch-name main --job-type RELEASE
```

## Pitfalls

- Bare `npx ampx sandbox` (no `--once`) in CI/agent contexts → hangs forever.
- Repository passed as `https://github.com/...` instead of `github.com/user/repo` → `create-app` fails.
- Skipped IAM service role → `AccessDeniedException` on every backend deploy.
- Wrong `baseDirectory` → blank page in production, no build error.
- `appRoot` with a leading slash in a monorepo.
- Expecting `amplify_outputs.json` to be committed — it's gitignored and regenerated by `sandbox`/`pipeline-deploy` every time.
