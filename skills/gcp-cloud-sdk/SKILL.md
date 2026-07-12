---
name: gcp-cloud-sdk
description: "Google Cloud SDK / gcloud CLI practitioner knowledge: the three separate credential stores (gcloud auth login vs application-default login/ADC vs service-account activation and workload identity federation), named configurations and property precedence (flags > CLOUDSDK_* env vars > active config), scripting discipline (--format json/value, --filter, --quiet, --impersonate-service-account, exit codes, never parse stderr), component management and the package-manager caveat, and the gsutil-to-gcloud-storage migration. Use when installing or configuring gcloud, debugging 'works in gcloud but not in my code' auth mismatches, quota-project errors, writing shell scripts or CI pipelines that call gcloud/bq/gcloud storage, or juggling multiple projects/accounts."
license: MIT
---

# Google Cloud SDK / gcloud CLI

The Google Cloud SDK is the toolkit for driving Google Cloud from a terminal or script:
the `gcloud` CLI (the primary tool), `bq` (BigQuery), the legacy `gsutil`, plus optional
components like `kubectl` and local emulators. Requires Python 3.10–3.14 (bundled by the
macOS/Windows installers). Post-install, `gcloud init` authorizes an account and creates
the default configuration.

## The mental model

**Everything gcloud does is (active credentials) x (active configuration's properties).**
Most confusion is a mismatch in one of those two dimensions.

### Configurations and properties

- A *configuration* is a named set of properties (`project`, `account`, `compute/zone`, ...).
  gcloud creates one named `default`; add more with `gcloud config configurations create NAME`
  and switch with `gcloud config configurations activate NAME`. Exactly one is active.
- Set properties with `gcloud config set project MY_PROJECT`,
  `gcloud config set compute/zone ZONE`; inspect with `gcloud config list` and
  `gcloud config configurations list`.
- **Precedence: command-line flags > `CLOUDSDK_*` environment variables > active configuration.**
  Every property has an env-var form: `CLOUDSDK_CORE_PROJECT`, `CLOUDSDK_COMPUTE_ZONE`,
  `CLOUDSDK_ACTIVE_CONFIG_NAME` (pick a config for one shell), and `--configuration=NAME`
  (pick one for a single command). CI tip: env vars beat the config file, so a stray
  `CLOUDSDK_CORE_PROJECT` explains "gcloud ignores my `config set`".
- Everything lives under the config dir: `~/.config/gcloud` (Linux/macOS), `%APPDATA%\gcloud`
  (Windows); relocate with `CLOUDSDK_CONFIG`. Find it:
  `gcloud info --format='value(config.paths.global_config_dir)'`.

### The auth distinction that trips everyone

There are **three separate credential stores**; setting one does nothing for the others:

1. **`gcloud auth login`** — credentials for the *gcloud CLI itself*. Browser flow; stored
   under the config dir; the account becomes the active principal (`gcloud auth list`,
   switch with `gcloud config set account`). Headless variants: `--no-browser` (needs a
   second machine with gcloud >= 372.0.0) or `--no-launch-browser`.
2. **`gcloud auth application-default login`** — credentials for *your code* via Application
   Default Credentials (ADC). Writes `~/.config/gcloud/application_default_credentials.json`
   (`%APPDATA%\gcloud\...` on Windows). Client libraries resolve ADC in this order:
   `GOOGLE_APPLICATION_CREDENTIALS` env var -> that local ADC file -> the attached service
   account via the metadata server (the production path on GCE/GKE/Cloud Run/etc.).
   "gcloud works but my app gets 401/403" almost always means ADC was never set up — the
   two stores are distinct by design.
3. **Service-account / federated credentials for gcloud** —
   `gcloud auth activate-service-account --key-file=KEY.json` (required for legacy P12 keys),
   or better, keyless options: `gcloud auth login --cred-file=/path/credential-config.json`
   with a workload identity federation config (short-lived tokens, no exportable key), or
   pure impersonation (below). Google recommends federation over downloaded keys — keys
   never expire and leak easily.

**Impersonation** works at both layers without any key file (needs
`roles/iam.serviceAccountTokenCreator` on the target SA and the Service Account Credentials
API enabled): per command `--impersonate-service-account=SA_EMAIL`, session-wide
`gcloud config set auth/impersonate_service_account SA_EMAIL` or
`CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT`, and for code
`gcloud auth application-default login --impersonate-service-account SA_EMAIL`.

**Quota project (ADC only).** User-credential ADC needs a quota project for billing/quota
attribution; errors mentioning "no quota project" or `serviceusage.services.use` mean it is
missing or you lack that permission — fix with
`gcloud auth application-default set-quota-project PROJECT`. Clean up dev machines with
`gcloud auth application-default revoke` (and `gcloud auth revoke` for CLI creds).

## Scripting essentials

- `--format` makes output a contract: `json`, `yaml`, `csv`, `text`, `value`, `list`, `table(...)`.
  For shell variables use projections: `gcloud info --format='value(config.account)'`;
  `--flatten='quotas[]'` explodes repeated fields for csv/table.
- `--filter` is server/client-side selection: `--filter="zone:us-central1-a"`,
  `--filter="labels.env=test AND labels.version=alpha"`. Prefer `--filter` + `--format`
  over piping to grep/awk.
- `--quiet` (`-q`) disables all interactive prompts, taking each prompt's default —
  mandatory in CI; also settable as the `disable_prompts` property.
- **Exit codes are the API: non-zero means the command failed and output may be incomplete.**
  Do not parse stderr — human-readable messages change between releases; status and
  diagnostics go to stderr, structured data to stdout.
- Script auth: on a workstation, user creds are fine; in CI use workload identity federation
  or `gcloud auth activate-service-account --key-file`, or per-command
  `--impersonate-service-account`. `gcloud auth print-access-token` mints a bearer token for
  raw `curl` calls (user tokens live ~1 hour); `CLOUDSDK_AUTH_ACCESS_TOKEN` injects one.

## Components

- `gcloud components list` / `install ID` / `update` / `remove ID`. Defaults: `gcloud`, `bq`,
  `gsutil`, `core`. Extras: `kubectl`, `alpha`, `beta`, App Engine language extensions,
  emulators (Bigtable/Datastore/Firestore/Pub/Sub), `cloud-sql-proxy`.
- **Package-manager caveat:** installed via apt/yum, the component manager is *disabled* —
  `gcloud components install` fails. Install extras as OS packages instead
  (`apt-get install google-cloud-cli-app-engine-go`, `kubectl`, etc.), and updates come from
  `apt-get upgrade`, not `gcloud components update`.
- Tool relationships: `bq` ships by default for BigQuery. `gsutil` is **legacy and minimally
  maintained** — use `gcloud storage` (faster defaults, supports newer features like soft
  delete and managed folders; a shim exists for migration). `kubectl` is distributed as a
  component/package; `gcloud container clusters get-credentials` wires it to GKE.

## Gotchas

- The three credential stores are independent: `gcloud auth login` does **not** give your
  code credentials, and `GOOGLE_APPLICATION_CREDENTIALS` does **not** change what `gcloud`
  runs as. Check both `gcloud auth list` and the ADC resolution order when debugging.
- Credential precedence inside gcloud itself: `CLOUDSDK_AUTH_ACCESS_TOKEN` > access-token
  file > credential file override (`auth/credential_file_override`) > the active logged-in
  principal — a forgotten env var silently changes identity.
- Stored credentials are plaintext-usable by anyone with filesystem access; avoid
  `gcloud auth login` on shared/persistent remote machines, and revoke when done.
- Only one configuration is active per invocation; long-lived shells with
  `CLOUDSDK_ACTIVE_CONFIG_NAME` set will ignore `gcloud config configurations activate`.
- `--format`/`--filter` output is stable; raw default output and stderr wording are not —
  never scrape them in scripts.

## Related

[[gcp-iam]], [[gcp-cloud-storage]], [[gcp-bigquery]], [[gcp-gke]], [[gcp-compute-engine]],
[[gcp-cloud-run]], [[gcp-cloud-build]], [[gcp-cloud-sql]], [[gcp-secret-manager]],
[[gcp-cloud-code]], [[terraform]], [[devops]]

Sources: https://docs.cloud.google.com/sdk/docs, https://docs.cloud.google.com/sdk/docs/install, https://docs.cloud.google.com/sdk/docs/authorizing, https://docs.cloud.google.com/sdk/docs/configurations, https://docs.cloud.google.com/sdk/docs/components, https://docs.cloud.google.com/sdk/docs/scripting-gcloud, https://docs.cloud.google.com/docs/authentication/application-default-credentials, https://docs.cloud.google.com/docs/authentication/set-up-adc-local-dev-environment, https://docs.cloud.google.com/storage/docs/gsutil (fetched 2026-07).
