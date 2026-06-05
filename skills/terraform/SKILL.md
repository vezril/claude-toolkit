---
name: terraform
description: Infrastructure as Code with Terraform (HashiCorp) — declaratively provisioning and versioning cloud and on-prem infrastructure. Covers the core model (providers, resources, data sources, the state file as source of truth, modules, input variables & outputs), HCL declarative configuration describing end-state, the write → plan → apply workflow (plus init/destroy/fmt/validate/import), state management (remote backends, locking, workspaces, HCP Terraform), the resource dependency graph, and the safety/validation toolchain (terraform validate/plan/fmt, policy-as-code via Sentinel/OPA, security scanning via tfsec/Checkov/Terrascan). Use when writing or reviewing Terraform/HCL, provisioning multi-cloud infrastructure as code, structuring reusable modules, managing remote state, or setting up an execution-grounded IaC pipeline (plan in CI, policy gates). Complements ansible (config management), devops, site-reliability-engineering, and github-actions; an alternative/peer to the IaC discussed there.
---

# Terraform

Provision and version infrastructure **declaratively, as code**. *"Terraform is an infrastructure as code tool that lets you build, change, and version cloud and on-prem resources safely and efficiently."* You describe the **desired end-state** in HCL; Terraform diffs it against recorded **state** and computes the minimal set of create/update/destroy operations to converge.

Sits in the deployment/operations layer with [[devops]] and [[ansible]]. Key distinction: **Terraform provisions infrastructure (immutable, declarative end-state); [[ansible]] configures it (procedural-ish, idempotent tasks).** They're complementary — Terraform stands up the servers/network, Ansible (or cloud-init/containers) configures what runs on them. Cross-links [[site-reliability-engineering]] (reliability/observability of what you provision), [[github-actions]] (running IaC in CI), [[secure-coding]] (secrets, least-privilege, scanning), [[sdlc-orchestration]] (the enterprise track's IaC step).

## The model

- **Providers** — plugins that talk to a platform's API (AWS, Azure, GCP, Kubernetes, GitHub, Datadog, …). Thousands on the Terraform Registry; you can write your own. A provider defines what resources/data sources exist.
- **Resources** — the infrastructure objects you declare (a VM, bucket, DNS record, k8s deployment, SaaS setting). The verbs of your config.
- **Data sources** — read-only lookups of existing/external data to feed config (e.g. fetch the latest AMI, an existing VPC).
- **State** — *"Terraform keeps track of your real infrastructure in a state file, which acts as a source of truth."* Terraform compares config ↔ state to decide changes. Losing/corrupting state is the cardinal operational risk.
- **Modules** — *"reusable configuration components"*: a folder of `.tf` files you call with inputs. Root module + child modules; publishable to the Registry. The unit of reuse and composition.
- **Input variables / outputs** — `variable` parameterizes a config/module; `output` exposes computed values (and passes data between modules).
- **HCL** — HashiCorp Configuration Language: declarative `.tf` files describing end-state (a JSON variant exists; CDKTF lets you use TS/Python). You declare *what*, not *how* — Terraform builds a **dependency graph** and provisions independent resources in parallel.

## The core workflow

**Write → Plan → Apply** (the canonical three stages):

```bash
terraform init      # download providers/modules, set up the backend
terraform fmt       # canonical formatting
terraform validate  # syntax / internal consistency
terraform plan      # PREVIEW: what will be created/updated/destroyed — the safety gate
terraform apply     # execute, in dependency order, after approval
terraform destroy   # tear down managed infrastructure
```

- **`plan` is the safety gate** — always read it before `apply`; it shows the exact diff and prompts for approval. In automation, save the plan and apply *that* artifact.
- Other commands worth knowing: `state` (advanced state surgery), `import` (bring existing infra under management), `output`, `graph`, `taint`/`-replace`, `workspace`, `force-unlock`, `show`, `providers`. `-chdir=DIR` runs from another directory.

## State management

- State can be **local** (`terraform.tfstate`) or **remote** (backends: S3, GCS, Azure Blob, HCP Terraform, …). Teams use **remote state** so everyone shares one source of truth.
- **Locking** prevents concurrent runs from corrupting state; `force-unlock` releases a stuck lock.
- **Workspaces** isolate multiple state instances (e.g. dev/staging/prod) from one config.
- **HCP Terraform / Terraform Enterprise** add shared remote state, locking, a consistent run environment, RBAC/governance, a private module registry, and VCS-driven runs.
- Never commit state to git (it contains secrets); never hand-edit it.

## Safety, validation & policy-as-code (the execution-grounded gate)

Per [[sdlc-orchestration]]'s "execute, don't opine" rule, an IaC change is validated by **running the tooling**, not by eyeballing HCL:

- **`terraform validate`** — config is syntactically valid and internally consistent.
- **`terraform plan`** — the real diff against state; the primary preview gate. Review it; fail CI on unexpected destroys.
- **`terraform fmt -check`** — style consistency.
- **`terraform test`** — the built-in testing framework for modules.
- **Policy-as-code** — **Sentinel** (HashiCorp, HCP/Enterprise) or **OPA / Conftest** to enforce guardrails on a plan (e.g. "no public S3 buckets," "only approved instance types," "tags required").
- **Security scanners** — **tfsec**, **Checkov**, **Terrascan**, **Trivy** lint HCL for misconfigurations/security issues.
- Wire these into CI ([[github-actions]]): `fmt -check` → `validate` → `plan` → policy/scan → (gated) `apply`.

## Good practice

- **Small, composable modules** with clear inputs/outputs; don't repeat yourself; pin module and provider **versions**.
- **Remote state + locking** from day one for teams; one workspace/state per environment.
- **Least privilege** for the provider credentials; **secrets** out of HCL and state where possible (use a secrets manager / provider-side; mark sensitive). ([[secure-coding]])
- **Plan in CI, apply on approval** (human-in-the-loop for prod, per [[sdlc-orchestration]]); save and apply the reviewed plan artifact.
- Keep config **DRY** with variables/locals/modules; use data sources instead of hard-coded IDs.
- Prefer **immutable** changes (replace) over in-place mutation where it reduces drift.

## Anti-patterns

- Editing infrastructure by hand (ClickOps) → **drift** between reality and state; or hand-editing `terraform.tfstate`.
- Committing state or secrets to version control.
- `apply` without reading `plan`; auto-approve in production with no human gate.
- One giant root module / no modules; copy-paste instead of reuse; unpinned provider versions (surprise breakage).
- No remote state/locking on a team → concurrent corruption.
- No policy-as-code or security scan → public buckets, open security groups slip through.
- Treating Terraform as config management (long provisioners doing app setup) — that's [[ansible]]'s/containers' job.

## Always-apply

1. Declare **end-state in HCL**; let the dependency graph and **plan** drive changes.
2. **init → fmt → validate → plan → apply**; never apply an unreviewed plan; HITL for prod.
3. **Remote state + locking**; one state per environment; never commit state/secrets.
4. **Small, versioned, reusable modules**; least-privilege credentials.
5. **Gate on execution** in CI: `validate` + `plan` + policy-as-code (Sentinel/OPA) + scan (tfsec/Checkov).

## Related

- [[ansible]] — configuration management; Terraform provisions, Ansible configures (complementary).
- [[devops]] — IaC as a core practice; the Three Ways / DORA.
- [[site-reliability-engineering]] — reliability/observability of provisioned systems.
- [[github-actions]] — running the IaC pipeline (plan/policy/apply) in CI.
- [[secure-coding]] — secrets, least privilege, misconfiguration scanning.
- [[sdlc-orchestration]] — the enterprise-track IaC step, execution-grounded.
- [[docker]] — what often runs *on* the infrastructure Terraform provisions.
- Source: HashiCorp Terraform documentation (developer.hashicorp.com/terraform).
