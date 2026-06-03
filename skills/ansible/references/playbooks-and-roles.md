# Ansible: playbooks, roles, variables, vault, testing

*Ansible for DevOps* (Geerling). Practical detail behind the SKILL.

## Project layout (idiomatic)

```
inventories/
  production/  hosts.yml  group_vars/  host_vars/
  staging/     hosts.yml  group_vars/  host_vars/
roles/
  common/  webserver/  database/      # each a standard role
playbooks/
  site.yml        # master: include roles per host group
  webservers.yml
requirements.yml   # Galaxy roles/collections to install
ansible.cfg
```
Run: `ansible-playbook -i inventories/production playbooks/site.yml`.

## Play & task mechanics

- A **play** maps a host pattern → an ordered task list, with play-level keys: `become`, `vars`, `vars_files`, `roles`, `pre_tasks`/`post_tasks`, `serial` (rolling batch size), `strategy` (linear/free), `gather_facts`.
- **Task control**: `name` (always), `when:` (conditional), `loop:`/`with_items` (iteration), `register:` (capture result), `changed_when:`/`failed_when:` (override change/failure detection), `notify:` (trigger handlers), `tags:` (selective runs), `delegate_to:` (run on another host), `run_once:`, `ignore_errors:`, `no_log: true` (hide secrets), `block:`/`rescue:`/`always:` (grouping + try/except).
- **Modules**: prefer fully-qualified collection names (`ansible.builtin.apt`). Use the right module (`package`, `service`/`systemd`, `copy`/`template`, `file`, `user`/`group`, `git`, `unarchive`, `lineinfile`/`blockinfile`, cloud modules) over `command`/`shell`. When shelling out, add `creates:`/`removes:`/`changed_when:` so it stays idempotent.

## Variables & precedence

Sources (low → high, roughly): role `defaults/` → inventory group_vars/host_vars → play `vars`/`vars_files` → task `vars` → `set_fact`/registered → **extra-vars (`-e`)** (always wins). Keep it predictable: put tunables in `defaults/main.yml`, environment differences in inventory `group_vars`, and avoid surprising overrides. **Facts** (`ansible_facts.*`, gathered at play start) describe the host; `ansible.builtin.setup` gathers them, `gather_facts: false` skips for speed.

## Templates (Jinja2)

`template:` renders `.j2` files with variables, facts, filters (`| default(...)`, `| to_json`, `| b64encode`), conditionals (`{% if %}`), and loops (`{% for %}`). The standard way to produce env-specific config files; pair with handlers to restart the service only when the rendered file changes.

## Roles & dependencies

A role's `tasks/main.yml` is the entry; `defaults/main.yml` (overridable defaults) vs `vars/main.yml` (higher-precedence, "internal"); `handlers/`, `templates/`, `files/`, `meta/main.yml` (role `dependencies`, supported platforms, Galaxy metadata). Include via a play's `roles:` list or `include_role`/`import_role` (dynamic vs static). Compose larger systems by layering roles (`common` → `webserver` → app).

## Galaxy & collections

`ansible-galaxy install -r requirements.yml` pulls community **roles** and **collections** (namespaced module/plugin bundles, e.g. `community.docker`, `amazon.aws`). Pin versions in `requirements.yml`; vendor or mirror for reproducible CI.

## Secrets — ansible-vault

- `ansible-vault create/edit/encrypt/decrypt/view secret.yml`; encrypt a whole file or single vars (`encrypt_string`).
- Reference encrypted vars normally; provide the password via `--ask-vault-pass`, `--vault-password-file`, or `--vault-id` (CI uses a file/secret store).
- Keep encrypted secrets in VCS (fine — they're ciphertext), plaintext keys out of VCS; combine with `no_log: true` on tasks that handle them.

## Testing & CI

- **`--syntax-check`**, **`--check`** (dry run, reports would-be changes), **`--diff`** (show file diffs).
- **`ansible-lint`** for best-practice/idempotency linting.
- **Molecule** — the standard role test framework: spins up a container/VM, runs the role (`converge`), asserts (`verify`), and crucially tests **idempotence** (a second run reports zero changes). Wire Molecule + ansible-lint into CI so roles are verified before they touch prod.
- Idempotence is the headline test: a converged system should report **no changes** on re-run.

## Operational notes

- `serial:` + health checks give **rolling deploys** (update a few hosts at a time) — the Ansible-level analog of [[akka-management]] rolling updates.
- Use `--limit` to scope a run; tags to run a slice; `--start-at-task` to resume.
- Treat playbooks/roles as code: review them, keep them clean and modular ([[clean-code]]/[[software-design]]), and never make undocumented manual changes to managed hosts ([[devops]] IaC discipline).
