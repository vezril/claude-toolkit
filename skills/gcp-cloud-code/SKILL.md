---
name: gcp-cloud-code
description: "Google Cloud Code — IDE extensions (VS Code, JetBrains/IntelliJ, preinstalled in Cloud Shell Editor) that wrap skaffold/minikube/kubectl into in-IDE inner dev loops for Kubernetes and Cloud Run, plus GCP surface browsers (APIs, Secret Manager, Compute Engine, Cloud SQL, Apigee). Covers the Run on Kubernetes and Cloud Run emulator loops, watch mode, launch.json/skaffold.yaml wiring, image-registry rules for remote clusters, buildpacks-instead-of-Dockerfile builds, and current status: bundles Gemini Code Assist Standard/Enterprise (the individuals/AI-Pro/Ultra tiers stopped serving June 2026 in favor of Antigravity)."
license: MIT
---

# Google Cloud Code

IDE tooling for developing on Google Cloud without leaving the editor. Three flavors:
**Cloud Code for VS Code**, **Cloud Code for IntelliJ** (and other JetBrains IDEs; limited
Android Studio support), and the copy **preinstalled in Cloud Shell Editor**. Language
support targets Go, Java, Node.js, Python, and .NET Core.

## The mental model

Cloud Code is two things glued together:

1. **A UI wrapper around Google's CLI container tools** — skaffold, minikube, kubectl.
   The "Run on Kubernetes" and "Run on Cloud Run Emulator" commands are skaffold dev
   loops with IDE affordances (status panes, log streaming, debugger attach, port
   forwarding). If you understand skaffold, you understand what Cloud Code is doing;
   the IDE config (`.vscode/launch.json`, run configurations in JetBrains) mostly maps
   onto `skaffold.yaml` and skaffold flags.
2. **A set of GCP explorers inside the IDE** — browse Cloud APIs and install client
   libraries, manage Secret Manager secrets, browse/SSH Compute Engine VMs, connect
   Cloud SQL (IntelliJ), develop Apigee API proxies locally, view GKE clusters and
   Cloud Run services, integrate Cloud Build. These are conveniences over the same
   APIs `gcloud` uses — nothing exclusive.

It also bundles **Gemini Code Assist** (the AI completion/chat extension) — Cloud Code
is the distribution vehicle for it in VS Code (`GoogleCloudTools.cloudcode`).

## The Kubernetes inner loop

- `Cloud Code: Run on Kubernetes` runs skaffold's dev mode: build → push → deploy →
  stream logs, repeating on file changes.
- **Watch mode is the default**: skaffold rebuilds/redeploys on save. Turn it off and
  you trigger rebuilds manually (Restart in the debug toolbar, `Ctrl/Cmd+Shift+F5`).
- **Targets**: local clusters (minikube, Docker Desktop) need no image registry —
  images load straight into the cluster. Remote clusters (GKE or any other provider)
  require you to specify a registry: Artifact Registry
  (`REGION-docker.pkg.dev/PROJECT_ID/REPO`), Docker Hub, ECR, or ACR. Cloud Code
  concatenates that registry prefix with the image name in your manifests to form the
  final repo name.
- The kubecontext is confirmed before deploy and remembered in `launch.json`.
- Debugging attaches the IDE debugger to the container via skaffold's debug support;
  YAML authoring gets schema-aware completion/linting for Kubernetes resources.
- Skaffold **modules** let you run/debug one part of a multi-service app independently.

## The Cloud Run inner loop

- `Run on Cloud Run Emulator` builds the service (choose **Docker** or **Buildpacks**
  as the builder) and runs it locally with Cloud Run-shaped env (`PORT=8080`,
  `K_SERVICE`, `K_REVISION`, `K_CONFIGURATION`), optional Cloud SQL connection, and
  optional exposure to the local network.
- Same skaffold-driven watch mode: save → rebuild → rerun, service URL surfaced for
  browser testing; debugger attach and source mapping via `launch.json`.
- When the loop looks good, deploy to real Cloud Run from the IDE (or hand off to CI).
- **Buildpacks option matters**: you get a production-grade image with no Dockerfile,
  consistent with what `gcloud run deploy --source` does server-side.

## Gotchas and current status (as of 2026-07)

- **Gemini Code Assist for individuals is gone**: since **June 18, 2026**, the IDE
  extensions and Gemini CLI stopped serving the individuals, Google AI Pro, and AI
  Ultra tiers — those users are pointed at **Antigravity** (Google's agentic IDE
  platform). Cloud Code's bundled AI assist now means **Gemini Code Assist Standard
  or Enterprise** (paid, org-provisioned) only; it needs explicit enablement and IAM
  setup. Cloud Code itself — the k8s/Cloud Run tooling — is not deprecated.
- **Private GKE Autopilot clusters** often can't pull from Docker Hub; host dev images
  in Artifact Registry or give the cluster outbound internet access.
- The docs' own advice: run the dev loop against a **non-production cluster**.
- The emulator is local-first fidelity, not perfection — it fakes the Cloud Run env
  vars and port contract, not IAM, service-to-service auth, or scaling behavior.
- App Engine support is disabled by default in the IntelliJ plugin (Java 8 App Engine
  support ended January 2024).
- Cloud Shell Editor gives you the same Cloud Code features with zero install, at the
  cost of Cloud Shell's ephemeral VM limits — good for demos and quick fixes, cramped
  for a real dev loop.
- Debugging deployed workloads uses Google Cloud Observability snapshots, not the
  old standalone Cloud Debugger (shut down 2023).

## When to reach for it

Use Cloud Code when a human is iterating on a k8s/Cloud Run service and wants
save-to-redeploy latency with a debugger attached. Don't contort CI or scripted
workflows through it — the underlying skaffold, `gcloud run deploy`, and kubectl
commands are the automatable surface, and everything Cloud Code does can be done with
them directly.

## Related

- [[gcp-cloud-run]] — the deploy target the emulator imitates
- [[gcp-gke]] — the remote-cluster target of Run on Kubernetes
- [[gcp-buildpacks]] — the no-Dockerfile builder option
- [[gcp-artifact-registry]] — where remote-cluster dev images should live
- [[gcp-cloud-build]] — the CI counterpart to the IDE inner loop
- [[gcp-cloud-sdk]] — gcloud/kubectl/skaffold, the tools Cloud Code wraps
- [[gcp-secret-manager]] — managed in-IDE via the Secret Manager explorer
- [[gcp-compute-engine]] — VM browsing/SSH from the IDE
- [[gcp-apigee]] — local API proxy development support
- [[gcp-cloud-functions]] — Cloud Run functions deployable from the IDE
- [[docker]] — the alternative builder and local runtime

Sources: https://docs.cloud.google.com/code/docs, https://docs.cloud.google.com/code/docs/vscode/overview, https://docs.cloud.google.com/code/docs/intellij/overview, https://docs.cloud.google.com/code/docs/vscode/running-an-application, https://docs.cloud.google.com/code/docs/vscode/developing-a-cloud-run-service, https://docs.cloud.google.com/code/docs/shell/overview, https://docs.cloud.google.com/gemini/docs/codeassist/overview (fetched 2026-07).
