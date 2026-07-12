---
name: gcp-buildpacks
description: "Google Cloud Buildpacks — Google's Cloud Native Buildpacks (CNB) distribution that turns source code into production container images with no Dockerfile; the engine behind gcloud run deploy --source, Cloud Run functions, and App Engine builds. Covers builder/run images (gcr.io/buildpacks/builder:google-24|google-22|v1), runtime pinning (GOOGLE_RUNTIME_VERSION, GOOGLE_PYTHON_VERSION, GOOGLE_NODEJS_VERSION, .python-version, package.json engines), entrypoints (Procfile, GOOGLE_ENTRYPOINT), functions (GOOGLE_FUNCTION_TARGET), pack CLI vs gcloud builds submit --pack, and extending build/run images. Use when containerizing without a Dockerfile, debugging a source-deploy build, pinning a runtime version, or customizing builder/run images."
license: MIT
---

# Google Cloud Buildpacks

Google's distribution of Cloud Native Buildpacks (CNB): open-source buildpacks that take
application source and produce a production-ready OCI image — no Dockerfile. This is the
build engine behind `gcloud run deploy --source`, Cloud Run functions, and App Engine's
managed builds; you can also run it yourself with the `pack` CLI or Cloud Build.

## The mental model

- **Detect → build.** Each buildpack owns one concern (Python, `pip`, a web server). A
  **builder** groups buildpacks: it inspects your source, picks the matching group, makes a
  build plan, and produces the image. You never write container config; you steer with files
  in your repo and `GOOGLE_*` build-time env vars.
- **Two base images.** The **build image** hosts the build environment where the buildpacks
  lifecycle runs; the **run image** is the base of the final container. Generic builders:
  - `gcr.io/buildpacks/builder:latest` → alias of `google-24` (Ubuntu 24)
  - `gcr.io/buildpacks/builder:google-24` / `google-22` (Ubuntu 22) / `v1` (Ubuntu 18)
  - App Engine uses per-language builders under `us-central1-docker.pkg.dev/serverless-runtimes/`.
- **Runtime support tracks the builder.** `google-24`: Python 3.13–3.14, Node 22/24,
  Go 1.x, Java 17/21/25, Ruby 3.2–4.0, PHP 8.2–8.5, .NET 8/10, plus an OS-only path.
  `google-22` reaches further back (Python 3.10+, Node 12+, Java 8+, .NET 6+); `v1` is legacy.
- **Version pinning is per language, env var wins over file:**
  - Generic: `GOOGLE_RUNTIME` (force a runtime), `GOOGLE_RUNTIME_VERSION` (pin its version).
  - Python: `GOOGLE_PYTHON_VERSION` > `.python-version` file > latest LTS. Deps from
    `requirements.txt` (or `pyproject.toml` if absent); `GOOGLE_PYTHON_PACKAGE_MANAGER`
    flips pip/uv (uv is the default from Python 3.14).
  - Node: `GOOGLE_NODEJS_VERSION` > `package.json` `engines.node` (semver). Package manager
    from the lockfile (yarn.lock → pnpm-lock.yaml → bun.lock → package-lock.json) or
    `GOOGLE_PACKAGE_MANAGER`. Custom build steps: `gcp-build` script or
    `GOOGLE_NODE_RUN_SCRIPTS=lint,build` (env var wins). No `.nvmrc` support.
- **Entrypoint precedence:** `Procfile` in the repo root (`web: gunicorn --bind :$PORT ...`)
  > `GOOGLE_ENTRYPOINT` env var > framework default (Node runs `scripts.start` / `npm start`;
  Python 3.13+ infers from the framework in requirements.txt, else `gunicorn -b :8080 main:app`).
  The container must listen on `$PORT` (8080 by convention).
- **Other build knobs:** `GOOGLE_BUILDABLE` (path to the unit to build — Go/Java/Dart/.NET),
  `GOOGLE_BUILD_ARGS` / `GOOGLE_MAVEN_BUILD_ARGS` / `GOOGLE_GRADLE_BUILD_ARGS`,
  `GOOGLE_CLEAR_SOURCE` (drop source from the final image), `GOOGLE_DEVMODE` (live-rebuild
  for local dev). Functions: `GOOGLE_FUNCTION_TARGET` (exported function name — required),
  `GOOGLE_FUNCTION_SIGNATURE_TYPE` (http | event | cloudevent), `GOOGLE_FUNCTION_SOURCE`.

## Local shape (pack CLI)

Requires Docker CE, pack, git:

```bash
pack build my-app --builder gcr.io/buildpacks/builder:latest \
  --env GOOGLE_ENTRYPOINT="gunicorn -p :8080 main:app"
docker run -it -e PORT=8080 -p 8080:8080 my-app
```

Or check env vars into the repo in `project.toml` so every build path picks them up:

```toml
[[build.env]]
name  = "GOOGLE_FUNCTION_TARGET"
value = "handler"
```

Functions builds = same builder + Functions Framework dependency + `GOOGLE_FUNCTION_TARGET`.

## The gcloud paths

```bash
# Cloud Build runs the buildpack, pushes to Artifact Registry:
gcloud builds submit --pack image=REGION-docker.pkg.dev/PROJECT/REPO/IMAGE

# Source deploys — buildpacks run implicitly, no flags needed:
gcloud run deploy SERVICE --source .
```

In a `cloudbuild.yaml`, the step is the `gcr.io/k8s-skaffold/pack` image running
`pack build ... --builder gcr.io/buildpacks/builder:latest --network cloudbuild --publish`.

## Extending build/run images

Need an apt package (imagemagick, subversion)? Derive images with a stock Dockerfile:
`FROM gcr.io/buildpacks/builder` → `USER root` → `apt-get install` → `USER cnb` (build side),
and `FROM` the matching run image → install → `USER 33:33` (run side); then
`pack build app --builder CUSTOM_BUILDER --run-image CUSTOM_RUN`. Builder tag and run-image
generation must match (`google-24` with `google-24`) — mixing, e.g. `v1` + `google-22`, is unsupported.

## Gotchas

- Runtime version availability differs per builder generation; a `.python-version` that
  `google-24` can't satisfy fails the build. Check the builders page before pinning.
- Language-specific env vars (`GOOGLE_PYTHON_VERSION`, `GOOGLE_NODEJS_VERSION`) override the
  in-repo files — a CI-set env var can silently diverge from what the repo declares.
- Some languages need an explicit process: Python without a recognized framework needs a
  `Procfile` or `GOOGLE_ENTRYPOINT`; Node needs `scripts.start` or a Procfile.
- `GOOGLE_CLEAR_SOURCE` breaks apps that read files from source at runtime (Go templates,
  static assets).
- Images bundle source + deps + OS; if you need tight size control, distroless bases, exotic
  system deps, or multi-stage tricks, you've outgrown buildpacks — write a Dockerfile
  (Cloud Run/Functions accept prebuilt images everywhere buildpacks are the default).
- These are build-time env vars: set via `pack --env` or `project.toml`, not the service's
  runtime env config.

## Related

[[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-app-engine]], [[gcp-cloud-build]],
[[gcp-artifact-registry]], [[gcp-artifact-analysis]], [[gcp-cloud-code]], [[docker]]

Sources: https://docs.cloud.google.com/docs/buildpacks, https://docs.cloud.google.com/docs/buildpacks/overview, https://docs.cloud.google.com/docs/buildpacks/builders, https://docs.cloud.google.com/docs/buildpacks/build-application, https://docs.cloud.google.com/docs/buildpacks/build-function, https://docs.cloud.google.com/docs/buildpacks/service-specific-configs, https://docs.cloud.google.com/docs/buildpacks/build-run-image, https://docs.cloud.google.com/docs/buildpacks/set-environment-variables, https://docs.cloud.google.com/docs/buildpacks/python, https://docs.cloud.google.com/docs/buildpacks/nodejs (fetched 2026-07).
