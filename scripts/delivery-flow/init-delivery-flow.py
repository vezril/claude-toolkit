#!/usr/bin/env python3
"""Make a repository a delivery-flow repo: generate its `.delivery-flow.yaml`.

Usage:
    init-delivery-flow.py [<repo>] [--profile triage|full] [--jira-project ABC]
                          [--external | --internal] [--signers <path>]
                          [--contract-paths a,b] [--dry-run] [--force]

Nothing about delivery-flow is per-project except this file, and most of what goes in it is
sitting in the repository already — the forge, the default branch, the test command, which
protected directories exist. So detect those and ask only for what detection cannot know.

Three things are never guessed, because guessing them wrong is worse than leaving them blank:

  - the Jira project key, which the flow cannot infer from a git remote;
  - `tracker.external`, which decides whether a post needs a signed human decision;
  - `contract_paths`, because only a person knows which paths other teams depend on.

Credentials are never written here. The Jira adapter reads them from the environment, and a
token in a committed file is a token in the git history forever.

Exit codes: 0 written, 2 a usage error, not a git repository, or a config already present.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONFIG_NAME, load_profiles  # noqa: E402

# (marker, test command) — first match wins, most specific first.
TEST_COMMANDS = [
    ("build.sbt", "sbt test"),
    ("pom.xml", "mvn -q test"),
    ("build.gradle.kts", "./gradlew test"),
    ("build.gradle", "./gradlew test"),
    ("Cargo.toml", "cargo test"),
    ("go.mod", "go test ./..."),
    ("pyproject.toml", "pytest"),
    ("pytest.ini", "pytest"),
    ("tox.ini", "tox"),
]
# Directories worth protecting *if they exist*. Inventing one would fire a punch-out on a path
# the repo does not have, which trains people to ignore punch-outs.
CANDIDATE_PROTECTED = [".github", ".circleci", "charts", "helm", "terraform", "infra",
                       "deploy", "hooks", ".buildkite"]


def git(repo: Path, *args):
    try:
        out = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def detect_forge(repo: Path) -> dict:
    remote = git(repo, "remote", "get-url", "origin") or ""
    base = None
    head = git(repo, "symbolic-ref", "refs/remotes/origin/HEAD")
    if head:
        base = head.rsplit("/", 1)[-1]
    if not base:
        base = git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "main"
    if "github" in remote:
        return {"kind": "github-pr", "base": base, "remote": remote}
    return {"kind": "github-pr", "base": base, "remote": remote, "uncertain": True}


def detect_test_command(repo: Path):
    # A `test:` target is the project declaring its own entry point, which beats inferring one
    # from the language: it usually wraps lint, coverage and the flags that matter here.
    if (repo / "Makefile").is_file():
        try:
            if re.search(r"^test:", (repo / "Makefile").read_text(), re.M):
                return "make test"
        except OSError:
            pass
    if (repo / "package.json").is_file():
        try:
            pkg = json.loads((repo / "package.json").read_text())
            if (pkg.get("scripts") or {}).get("test"):
                return "npm test"
        except (json.JSONDecodeError, OSError):
            pass
    for marker, cmd in TEST_COMMANDS:
        if (repo / marker).is_file():
            return cmd
    return None


def detect_protected(repo: Path) -> list:
    return [p for p in CANDIDATE_PROTECTED if (repo / p).exists()]


def detect_visibility(repo: Path):
    """"public" | "private" | "internal" | None. Needs `gh`; None means we could not tell."""
    try:
        out = subprocess.run(["gh", "repo", "view", "--json", "visibility", "-q", ".visibility"],
                             cwd=repo, capture_output=True, text=True, timeout=25)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    v = out.stdout.strip().lower()
    return v if v in ("public", "private", "internal") else None


def commit_artifacts_default(visibility, external: bool) -> tuple:
    """(value, why) for `artifacts.commit`.

    `delivery/<KEY>/` holds the ticket body, the triage rationale, the breakdown and the brief.
    Committing it sends all of that wherever the branch goes — which is the point on a private
    repo, and a disclosure on a public one. Someone else's ticket text is not ours to publish,
    so where visibility is unknown and the tracker belongs to someone else, we do not commit.
    """
    if visibility == "public":
        return False, "this repo is PUBLIC, so committing the trail would publish ticket content"
    if visibility is None and external:
        return False, ("repo visibility could not be determined and the tracker is external, "
                       "so the cautious reading applies")
    return True, "the trail travels with the PR, which is how two machines' runs aggregate"


def render(repo: Path, args, forge: dict, test_cmd, protected: list, visibility=None) -> str:
    jira = bool(args.jira_project)
    external = True if args.external or (jira and not args.internal) else False
    assumed_external = jira and not args.external and not args.internal
    signers = args.signers or "~/.config/delivery-flow/allowed_signers"
    contracts = [c.strip() for c in (args.contract_paths or "").split(",") if c.strip()]

    L = [f"# Generated by init-delivery-flow.py for {repo.name}.",
         "# Its presence is what makes this a delivery-flow repo: every hook and script in the",
         "# plugin is inert without it. Edit freely — the generator never runs again unless you",
         "# ask it to.", "",
         f"profile: {args.profile}", ""]

    if jira:
        L += ["tracker:", "  kind: jira",
              f"  project: {args.jira_project}",
              f"  external: {str(external).lower()}"]
        if assumed_external:
            L += ["  # ASSUMED true: a Jira you did not declare internal is treated as someone",
                  "  # else's, so every post-back needs a signed decision. Confirm or pass",
                  "  # --internal and regenerate."]
        L += ["  # Credentials come from the environment, never from this file:",
              "  #   JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN", ""]
    else:
        L += ["tracker:", "  kind: github-issues", "  external: false", ""]

    L += ["forge:", f"  kind: {forge['kind']}", f"  base: {forge['base']}"]
    if forge.get("uncertain"):
        L += [f"  # The remote ({forge['remote'] or 'none'}) is not GitHub — check this adapter."]
    L += [""]

    if test_cmd:
        L += [f'test_command: "{test_cmd}"   # detected; what `verify` runs', ""]
    else:
        L += ['test_command: ""   # NOT DETECTED — set this or `verify` has nothing to run', ""]

    commit, why = commit_artifacts_default(visibility, external)
    if args.commit_artifacts:
        commit, why = True, "forced with --commit-artifacts"
    elif args.no_commit_artifacts:
        commit, why = False, "forced with --no-commit-artifacts"

    L += ["vault:",
          "  binding: null   # a project name enables the recall and update steps",
          "  path: null", "  graph_root: null", "  backend: filesystem", "",
          "artifacts:",
          f"  # {why}.",
          f"  commit: {str(commit).lower()}",
          "  # delivery/<KEY>/ holds the ticket body, the triage rationale, the breakdown and",
          "  # the brief. Only commit it where all of that may go.", "",
          "punch_out:", "  cost_budget_usd: 5.00", "  retry_limit: 3",
          "  # Only a human knows which paths other teams depend on, so this starts empty.",
          "  # A planned or realized edit under one of these fires a breaking-change punch-out.",
          f"  contract_paths: [{', '.join(contracts)}]",
          f"  protected_paths: [{', '.join(protected)}]" + (
              "   # detected" if protected else "   # none of the usual ones exist here"),
          "  epic_ceiling: 4", "  story_ceiling: 12", "  domain_ceiling: 2",
          "  require_acceptance_signal: true",
          "  proposal_task_ceiling: 8", "  proposal_file_ceiling: 15", "",
          "deploy:",
          '  patterns: ["helm upgrade", "helm install", "flux reconcile", "docker push"]',
          "  auto_roll:", "    routine_bumps: true",
          "    never: [api, schema, breaking, first-deploy, exposure]", "",
          "decisions:", f"  allowed_signers: {signers}", ""]

    if args.profile == "full":
        L += ["# `propose` and `vault-update` have no prompt-edd package yet, so their runs are",
              "# traced certified: false and excluded from the certified-only rate.",
              "allow_uncertified: [propose, vault-update]", ""]
    else:
        L += ["allow_uncertified: []", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--profile", default="triage")
    ap.add_argument("--jira-project", default=None, metavar="KEY")
    ap.add_argument("--external", action="store_true", help="the tracker belongs to someone else")
    ap.add_argument("--internal", action="store_true", help="the tracker is yours")
    ap.add_argument("--signers", default=None)
    ap.add_argument("--contract-paths", default=None, metavar="a,b")
    ap.add_argument("--commit-artifacts", action="store_true",
                    help="commit delivery/<KEY>/ even where the default declines to")
    ap.add_argument("--no-commit-artifacts", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    if args.external and args.internal:
        print("--external and --internal are contradictory", file=sys.stderr)
        return 2

    repo = Path(args.repo).expanduser().resolve()
    if not (repo / ".git").exists():
        print(f"{repo} is not a git repository root; delivery-flow config lives at the root",
              file=sys.stderr)
        return 2

    try:
        names = [p.get("profile") for p in load_profiles()]
    except (OSError, ValueError) as e:
        print(f"could not read profiles.yaml: {e}", file=sys.stderr)
        return 2
    if args.profile not in names:
        print(f"unknown profile {args.profile!r}; available: {', '.join(sorted(names))}",
              file=sys.stderr)
        return 2

    target = repo / CONFIG_NAME
    if target.exists() and not args.force:
        print(f"{target} already exists; pass --force to replace it", file=sys.stderr)
        return 2

    forge = detect_forge(repo)
    test_cmd = detect_test_command(repo)
    protected = detect_protected(repo)
    visibility = detect_visibility(repo)
    text = render(repo, args, forge, test_cmd, protected, visibility)

    if args.dry_run:
        print(text, end="")
        return 0

    target.write_text(text)
    print(f"wrote {target}\n")
    print(f"  profile:        {args.profile}")
    print(f"  tracker:        {'jira (' + args.jira_project + ')' if args.jira_project else 'github-issues'}")
    print(f"  forge:          {forge['kind']} onto {forge['base']}")
    print(f"  test command:   {test_cmd or 'NOT DETECTED — set test_command'}")
    print(f"  protected:      {', '.join(protected) or 'none detected'}")
    print(f"  visibility:     {visibility or 'could not determine (gh unavailable?)'}")
    commit, why = commit_artifacts_default(visibility, bool(args.jira_project) and not args.internal)
    if args.commit_artifacts:
        commit, why = True, "forced"
    elif args.no_commit_artifacts:
        commit, why = False, "forced"
    print(f"  commit trail:   {str(commit).lower()} — {why}")
    print("\nStill yours to decide:")
    print("  - punch_out.contract_paths: which paths other teams depend on")
    if args.jira_project and not (args.external or args.internal):
        print("  - tracker.external: assumed true (a client's Jira). Confirm or set --internal")
    if args.jira_project:
        print("\nThe adapter reads credentials from the environment:")
        print("  export JIRA_BASE_URL=https://<site>.atlassian.net")
        print("  export JIRA_EMAIL=<your account email>")
        print("  export JIRA_API_TOKEN=<id.atlassian.com/manage-profile/security/api-tokens>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
