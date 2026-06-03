---
name: ansible
description: Ansible — agentless configuration management, provisioning, and orchestration / infrastructure as code, distilled from Geerling's *Ansible for DevOps*. Covers the model (agentless over SSH, push-based, declarative + idempotent), inventory (static/dynamic, groups, host/group vars), playbooks (plays, tasks, modules, handlers/notify), variables/facts and Jinja2 templates, roles and their directory structure, Ansible Galaxy & collections, ansible-vault for secrets, loops/conditionals/tags/blocks, check mode, and testing (Molecule) + CI. Use when automating server configuration or app deployment, writing or reviewing playbooks/roles, managing infrastructure as code, handling secrets with vault, or making provisioning idempotent and repeatable. The infrastructure-as-code skill in the DevOps set; see devops for principles and site-reliability-engineering for operations.
---

# Ansible

**Agentless** configuration management, provisioning, and orchestration — define the desired state of your infrastructure/apps as code and let Ansible converge machines to it, **idempotently** and repeatably. The infrastructure-as-code arm of [[devops]]. Source: Jeff Geerling's *Ansible for DevOps*.

Cross-links: [[devops]] (the IaC/automation pillar), [[secure-coding]] (vault/secrets), [[site-reliability-engineering]] (release/provisioning ops), [[akka-management]]/[[os-virtualization]] (deploying clustered/containerized apps).

## The model

- **Agentless** — Ansible connects over **SSH** (WinRM for Windows) and runs modules on the target; no daemon to install/maintain on managed nodes. You run from a **control node**; targets just need Python + SSH.
- **Push-based & declarative-ish** — you push changes from the control node; tasks declare desired state via **modules** that are **idempotent** (running twice = same result, no spurious changes). This is the central discipline: tasks should converge state, not blindly execute commands.
- **YAML** for everything; **Jinja2** for templating; secrets via **ansible-vault**.

## Inventory

The list of hosts Ansible manages, organized into **groups**:
- **Static** (`inventory.ini`/YAML) or **dynamic** (a script/plugin querying AWS/GCP/etc.).
- **Group vars / host vars** (`group_vars/`, `host_vars/`) hold per-group/per-host variables — the natural place to vary config by environment (separate inventories for dev/staging/prod).

## Playbooks, tasks, modules, handlers

A **playbook** is an ordered list of **plays**; each play targets a group of hosts and runs a list of **tasks**; each task invokes a **module** (`apt`, `copy`, `template`, `service`, `user`, `file`, `git`, `command`/`shell`, hundreds more) idempotently.

```yaml
- hosts: webservers
  become: true                      # privilege escalation (sudo)
  vars:
    http_port: 80
  tasks:
    - name: Install nginx
      ansible.builtin.apt: { name: nginx, state: present }
    - name: Deploy config
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Restart nginx          # fire a handler only if this task changed something
  handlers:
    - name: Restart nginx
      ansible.builtin.service: { name: nginx, state: restarted }
```

- **Handlers** run **once at the end** of a play, and only if **notified** by a changed task — the idiomatic way to restart a service only when its config actually changed.
- **`become`** for privilege escalation; **`register`** to capture a task's result; **`when`** for conditionals; **`loop`** for iteration; **`tags`** to run subsets; **`block`/`rescue`/`always`** for grouping + error handling.
- **Ad-hoc commands** (`ansible web -m ping`, `-a "uptime"`) for one-off actions.

## Variables, facts, templates

- **Variables** come from many places with a precedence order (defaults → inventory/group/host vars → play vars → extra-vars `-e`). Keep it predictable.
- **Facts** — host data Ansible gathers (`ansible_facts`: OS, IP, memory…); use them in conditionals/templates. `gather_facts` can be tuned for speed.
- **Jinja2 templates** (`template` module) render config files with variables/facts/loops — the heart of environment-specific config.

## Roles — the unit of reuse

Package related tasks/handlers/templates/files/vars/defaults into a **role** with a standard layout:

```
roles/webserver/
  tasks/main.yml      handlers/main.yml    templates/   files/
  vars/main.yml       defaults/main.yml    meta/main.yml (deps)
```

Playbooks then just *include roles*. Share/consume roles and collections via **Ansible Galaxy** (`ansible-galaxy install`, `requirements.yml`). Roles are how you keep large automations organized and reusable (the [[clean-code]]/[[software-design]] discipline applied to ops code).

## Secrets — ansible-vault

Encrypt sensitive vars/files at rest with **`ansible-vault`** (`encrypt`/`edit`/`view`); reference them like any var; supply the password via prompt, file, or a vault-id in CI. **Never commit plaintext secrets** ([[secure-coding]]).

## Always-apply defaults

1. **Idempotency first** — use the proper module for the job, not `command`/`shell` (which aren't idempotent); when you must shell out, guard it with `creates:`/`removed:`/`changed_when:`/`when:` so reruns are safe.
2. **Organize with roles**; keep playbooks thin (mostly role includes); one inventory per environment with `group_vars`/`host_vars`.
3. **Secrets in vault**, never plaintext; keep everything in version control ([[devops]] IaC).
4. **Use handlers** for service restarts (only on change); prefer declarative state (`state: present`) over imperative steps.
5. **Test**: run `--check` (dry run) and `--diff`; lint with `ansible-lint`; test roles with **Molecule** in CI before applying to prod.
6. **Readable plays** — clear `name:` on every task, sensible defaults in `defaults/main.yml`, document role variables.

## Anti-patterns (flag in review)

- `command`/`shell` where a module exists (non-idempotent, reports `changed` every run); missing `changed_when`/`creates` guards.
- Plaintext secrets in vars/playbooks/VCS; secrets echoed in logs (use `no_log: true`).
- One giant monolithic playbook instead of roles; copy-pasted tasks instead of a reusable role.
- Mutating prod by hand instead of through version-controlled playbooks; no `--check`/lint/Molecule testing.
- Relying on implicit variable precedence; over-using `set_fact` where a defined var would do.

## How to use this skill

- **`references/playbooks-and-roles.md`** — fuller detail on play/task structure, the module ecosystem, variable precedence, role layout & dependencies, Galaxy/collections, vault workflows, and testing with Molecule + CI.

## Related

- [[devops]] — the principles and the IaC/automation pillar Ansible implements.
- [[site-reliability-engineering]] — provisioning/release as part of reliable operations.
- [[secure-coding]] — vault/secrets hygiene; [[akka-management]] / [[os-virtualization]] — deploying clustered/containerized services Ansible provisions.
- [[clean-code]] / [[software-design]] — keep ops code (roles/playbooks) clean and modular.
- Source: *Ansible for DevOps*, Jeff Geerling.
