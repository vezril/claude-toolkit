#!/usr/bin/env python3
"""PostToolUse hook: check the edge after an artifact is written.

Stage 4's rule is that the check between two nodes is deterministic code that runs
*after* the write, not something the model chooses to call. This hook fires on writes
under `delivery/<ITEM-KEY>/` and checks, for the artifact just written:

  1. it parses;
  2. its sha256 matches its sentinel;
  3. it conforms to its schema;
  4. the sentinel's claimed counts match the real counts (the sentinel is a claim);
  5. it satisfies the input contract of every step that consumes it.

Terminal prose (`summary.md`) has no schema; it is checked for coverage of the structured
artifacts it was rendered from, and its readability is measured into the trace, not gated.

Every outcome is appended to `delivery/<ITEM-KEY>/trace.jsonl`, pass or fail, so the
trace shows which checks ran. On failure the hook exits 2, which returns the report to
the model as feedback. It cannot un-write the file; the orchestrator refuses to advance
on a failed edge, and the report counts items whose edges failed.

Inert outside a delivery-flow repo: no `.delivery-flow.yaml` at the git root, exit 0.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HELPERS = Path(__file__).resolve().parents[1] / "scripts" / "delivery-flow"

# Any path under delivery/<ITEM-KEY>/, in a tool input or a shell command. Checked against
# the raw payload first: a session that writes nothing there costs one regex and exits.
# No text-match hint here on purpose. An early exit that depends on the command spelling
# `delivery/` is an early exit an artifact can be written behind, which is how the first
# version of this hook let three real writes through. `main` gates on a filesystem fact
# instead: is anything in reach a delivery-flow repo.


def _helpers():
    """Import the validator and shared helpers only once a delivery path is in play."""
    import importlib.util
    sys.path.insert(0, str(HELPERS))
    import common
    import brief
    import triggers as trigger_rules

    def _load(name, filename):
        spec = importlib.util.spec_from_file_location(name, HELPERS / filename)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    return (common, _load("validate_artifact", "validate-artifact.py"), brief, trigger_rules,
            _load("validate_proposal", "validate-proposal.py"))


# Paths inside a Bash command line; quotes and redirects are stripped by the split.
BASH_PATH_RE = re.compile(r"[A-Za-z0-9._/-]*delivery/[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]+")


# `cd <dir>` anywhere in the command. The payload's `cwd` is the *session's* directory, not the
# subshell's, so a command that cds elsewhere and then writes a relative path would otherwise
# resolve to a path that does not exist — and a non-existent path is skipped as "a command that
# mentioned the path without writing it". The edge then silently does not run.
# Found on a real run 2026-10-28: `cd ~/repo && … > delivery/K/item.json` wrote the artifact
# with no check and no trace record. The bypass suite missed it because its fixture always runs
# from the repo root, where the payload cwd happens to be correct.
BASH_CD_RE = re.compile(r"(?:^|[;&|])\s*cd\s+(?:-{1,2}\S+\s+)*(\"[^\"]+\"|'[^']+'|[^\s;&|]+)")


def _cd_targets(command: str) -> list:
    """Directories the command changes into, so a relative write resolves against them too."""
    out = []
    for raw in BASH_CD_RE.findall(command or ""):
        token = raw.strip().strip("'\"")
        if token and not token.startswith("-"):
            out.append(Path(token).expanduser())
    return out


def _registered_bases() -> list:
    """Opted-in repos, as bases a relative artifact fragment may belong to."""
    try:
        common, _, _, _, _ = _helpers()
        return list(common.known_repos())
    except Exception:
        return []


def written_paths(payload: dict) -> list:
    """Every path this tool call may have written, as absolute paths.

    A relative path is resolved against the payload's cwd *and* every `cd` target in the
    command, returning all candidates: `main` discards the ones that do not exist, so offering
    several costs nothing while missing the real one costs the entire check.
    """
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or ".")
    # Registered repos are extra *bases*, not extra things to scan. The regex always recovers
    # the `delivery/<ITEM>/<file>` fragment even from `"$R/delivery/K/f.json"` — what it cannot
    # recover is the base `$R` expands to. Supplying the opted-in repos as candidate bases
    # closes that without making the hook fire on calls that touch no delivery repo at all,
    # which scanning the whole registry did (and which broke inertness).
    out, bases = [], [cwd] + _registered_bases()
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        for key in ("file_path", "notebook_path"):
            if ti.get(key):
                out.append(Path(ti[key]))
    elif tool == "Bash":
        command = ti.get("command", "")
        bases += _cd_targets(command)
        for token in BASH_PATH_RE.findall(command):
            out.append(Path(token))
            # The leading character class swallows whatever precedes `delivery/` — in
            # `"$R/delivery/K/f.json"` it captures `R/delivery/K/f.json`, because `$` stops it
            # but `R` and `/` do not. Joining that to a base yields `<base>/R/delivery/...`,
            # which never exists. So also consider the fragment from `delivery/` onward.
            cut = token.find("delivery/")
            if cut > 0:
                out.append(Path(token[cut:]))

    resolved = []
    for p in out:
        if p.is_absolute():
            resolved.append(p)
        else:
            resolved.extend(base / p for base in bases)
    seen, unique = set(), []
    for p in resolved:                      # de-duplicate, keep order
        if str(p) not in seen:
            seen.add(str(p))
            unique.append(p)
    return unique


def check_brief(path: Path, common, brief) -> tuple:
    """Return (ok, problems, checks_run, metrics) for `summary.md`.

    Terminal prose has no schema to conform to, which is not the same as having no contract.
    What the renderer is answerable for is coverage: everything structured that mattered
    reached the page, and nothing reached the page that was not in its inputs. Readability is
    measured into the trace but never gated — the prose is inherited from the breakdown node,
    so failing the brief for it would stall the chain on something it cannot fix.
    """
    item_dir = path.parent
    triage, _ = common.load_json(item_dir / "triage.json")
    breakdown, _ = common.load_json(item_dir / "breakdown.json")
    challenge, _ = common.load_json(item_dir / "challenge-breakdown.json")
    proposal, _ = common.load_json(item_dir / "proposal.json")
    text = path.read_text()
    problems = brief.coverage_problems(text, triage, breakdown, challenge, proposal)
    metrics = brief.readability(text, common.PLUGIN_ROOT)
    return not problems, problems, ["coverage", "readability"], metrics


# Terminal prose: an artifact a human reads and no step consumes. It has no schema, so it gets
# a checker of its own rather than being waved through. `pr.md` and `post.md` belong here too
# once their contracts are written.
TERMINAL_PROSE = {"summary.md": check_brief}


def check_artifact(path: Path, schemas: dict, common, validator, trigger_rules, proposal_rules,
                   repo: Path = None) -> tuple:
    """Return (ok, problems, checks_run) for one artifact."""
    problems, ran = [], []
    schema = common.schema_for(path.name, schemas)
    if schema is None:
        return True, [], []  # not an artifact we govern

    ran.append("parse")
    doc, err = common.load_json(path)
    if err:
        return False, [err], ran

    ran.append("schema")
    validator.validate(doc, schema, "", problems)

    if not path.name.endswith(common.SENTINEL_SUFFIX):
        ran.append("sentinel")
        sentinel_path = path.with_name(path.name + common.SENTINEL_SUFFIX)
        sentinel, s_err = common.load_json(sentinel_path)
        if s_err:
            problems.append(f"no readable sentinel beside the artifact: {s_err}")
        else:
            actual_sha = common.sha256(path)
            sha_matches = sentinel.get("sha256") == actual_sha
            if not sha_matches:
                problems.append(
                    f"sentinel sha256 {str(sentinel.get('sha256'))[:12]}… does not match the file "
                    f"({actual_sha[:12]}…): the artifact changed after its sentinel was written")
            else:
                # Counts are only meaningful against the file the sentinel was written for.
                ran.append("counts")
                claimed = sentinel.get("counts") or {}
                for name, value in sorted(common.expected_counts(doc, schema).items()):
                    if name not in claimed:
                        problems.append(f"sentinel does not claim a count for {name!r}")
                    elif claimed[name] != value:
                        problems.append(
                            f"sentinel claims {name}={claimed[name]} but the file holds {value}")

        ran.append("input-contract")
        for consumer in schema.get("consumed_by", []):
            if consumer in (schema.get("consumers") or {}):
                problems += validator.consumer_problems(doc, schema, consumer)

        # The proposal carries a second artifact — the OpenSpec change directory — and the
        # interesting failure is the two disagreeing. Schema conformance cannot see that.
        if path.name == "proposal.json":
            ran.append("change-dir")
            # The *delivery repo*, not the artifact path's git root. With `artifacts.root`
            # pointing into the vault, `repo_root(path.parent)` climbs to the vault — itself a
            # git repo — and looks for openspec/changes/<id> there, where no change directory
            # will ever be. The result was "no change directory at openspec/changes/<id>"
            # against a change that exists in the delivery repo, blocking the flow at propose
            # on a checker bug rather than a bad artifact. `policy_disagreements` below already
            # takes `repo` for exactly this reason; this call site was missed.
            found, info = proposal_rules.problems(path, repo or common.repo_root(path.parent))
            problems += found
            if info.get("openspec_validate"):
                ran.append("openspec-validate")

        # Named in the trace even when it finds nothing: a check nobody can see ran is not
        # evidence that it ran.
        if path.name in ("triage.json", "breakdown.json", "proposal.json"):
            ran.append("policy-claim")

    return not problems, problems, ran


def policy_disagreements(path: Path, common, trigger_rules, repo: Path = None) -> list:
    """Where triage.json's gating flags and the artifacts part company.

    Recorded on the edge, never failed on: the derivations available before any code exists
    are textual, and the claim and the derivation are not always the same proposition. The
    protection is that a trigger fires on either signal; this is the audit trail for how often
    the node and the evidence disagree. Run on both artifacts because at triage time only the
    text derivations are determinable — the counts arrive with the breakdown.
    """
    if path.name not in ("triage.json", "breakdown.json", "proposal.json"):
        return []
    item_dir = path.parent
    # The repo is passed in, not re-derived from the artifact path. Under a configured
    # `artifacts.root` the artifact lives outside the repo entirely, so walking up from it
    # finds no `.delivery-flow.yaml` and `load_config` raised — taking the whole hook down
    # with it, on a valid artifact.
    try:
        cfg = common.load_config(repo if repo is not None else common.repo_root(item_dir))
    except OSError:
        return []
    if path.name == "proposal.json":
        return trigger_rules.proposal_disagreements(common.load_json(path)[0], cfg)
    return trigger_rules.disagreements(
        common.load_json(item_dir / "item.json")[0],
        common.load_json(item_dir / "triage.json")[0],
        common.load_json(item_dir / "breakdown.json")[0],
        cfg)


def last_traced_sha(repo: Path, item: str, filename: str, common):
    """The sha this artifact had when an edge last ran over it, or None."""
    found = None
    try:
        lines = common.trace_path(repo, item).read_text().splitlines()
    except OSError:
        return None
    for line in lines:                      # the newest matching record wins
        try:
            rec = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if rec.get("artifact") == filename and rec.get("sha256"):
            found = rec["sha256"]
    return found


def changed_artifacts(payload: dict, common, schemas: dict) -> list:
    """Artifacts that are new or whose bytes changed since an edge last saw them.

    Content, not command text. Detecting writes by regexing a Bash command line loses to
    shell variables, subshells, `python -c`, heredocs and computed paths — three separate
    real runs on 2026-10-28 wrote an artifact that the edge never checked, each defeating the
    pattern a different way. The trace already records every artifact's sha, so "what
    actually changed" is answerable without parsing anything, and no write syntax can hide
    from it.
    """
    bases = [Path(payload.get("cwd") or ".")]
    if payload.get("tool_name") == "Bash":
        bases += _cd_targets((payload.get("tool_input") or {}).get("command", ""))
    repos, out = [], []
    for base in bases:
        try:
            repo = common.repo_root(base)
        except OSError:
            continue
        if repo not in repos and common.is_delivery_repo(repo):
            repos.append(repo)

    for repo in repos:
        root = common.artifact_root(repo)
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*/*")):
            if not path.is_file():
                continue
            # Parsed against *this* root. Without it the match falls through to the default
            # `delivery/<ITEM>/<file>` pattern, returns (None, None) for a configured root,
            # and every artifact under it is skipped — the glob above was already correct and
            # the result was thrown away one line later.
            item, filename = common.parse_artifact_path(path, root)
            if not item:
                continue
            # Artifacts only. A sentinel is checked as part of its artifact's edge, so
            # scanning it separately would triple the trace and blur "one record per step".
            if filename.endswith(common.SENTINEL_SUFFIX):
                continue
            # `schema_for`, not `filename in schemas`: the glob-keyed artifacts (rendered
            # stories) never match an exact key, so an exact lookup skipped them here even
            # though `check_artifact` below would have governed them.
            if common.schema_for(filename, schemas) is None and filename not in TERMINAL_PROSE:
                continue
            try:
                current = common.sha256(path)
            except OSError:
                continue
            if current != last_traced_sha(repo, item, filename, common):
                out.append(path)
    return out


def identify(path: Path, common, payload: dict):
    """(item, filename, repo) for an artifact path, under either layout.

    The default `delivery/<ITEM>/<file>` is tried first so nothing about the in-repo layout
    changes. A configured `artifacts.root` can sit anywhere — outside the repo entirely — so
    where the default does not match, each candidate repo's own root is tried.
    """
    fallback = common.repo_root(path.parent if path.parent.exists()
                                else Path(payload.get("cwd") or "."))
    item, filename = common.parse_artifact_path(path)
    if item:
        return item, filename, fallback
    for candidate in common.candidate_repos(payload, [path.parent]):
        item, filename = common.parse_artifact_path(path, common.artifact_root(candidate))
        if item:
            return item, filename, candidate
    return None, None, fallback


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return 0  # not our business to fail a tool call over a malformed payload

    common, validator, brief, trigger_rules, proposal_rules = _helpers()
    schemas = common.load_schemas()
    paths = written_paths(payload)

    # Bail only when nothing in reach is a delivery-flow repo — a filesystem fact, not a text
    # match on the command. "In reach" must include the directories the paths themselves
    # imply: a command can write an absolute path held in a shell variable, from a cwd that is
    # not a delivery repo and with no `cd` anywhere, which is how the fourth variant of this
    # bug got through in one afternoon. So the list is built from the paths under
    # consideration rather than guessed at — every hand-written enumeration of "places to
    # look" has missed one.
    gate = [Path(payload.get("cwd") or ".")] + [p.parent for p in paths]
    if payload.get("tool_name") == "Bash":
        gate += _cd_targets((payload.get("tool_input") or {}).get("command", ""))
    if not any(common.is_delivery_repo(c) for c in gate if str(c)):
        return 0

    # Union with what actually changed on disk, so a write the command text hid still gets
    # checked. De-duplicate on the *resolved* path: on macOS a tempdir reaches the hook as
    # /tmp from one route and /private/tmp from the other, and the same file would be
    # checked twice.
    def _key(path):
        try:
            return str(path.resolve())
        except OSError:
            return str(path)

    seen = {_key(p) for p in paths}
    for p in changed_artifacts(payload, common, schemas):
        if _key(p) not in seen:
            seen.add(_key(p))
            paths.append(p)
    if not paths:
        return 0

    schemas = common.load_schemas()
    failures = []
    for path in paths:
        item, filename, repo = identify(path, common, payload)
        if not item:
            continue
        if not common.is_delivery_repo(repo):
            continue
        if not path.exists():
            continue  # a command that mentioned the path without writing it

        metrics = {}
        if filename in TERMINAL_PROSE:
            ok, problems, ran, metrics = TERMINAL_PROSE[filename](path, common, brief)
        else:
            ok, problems, ran = check_artifact(path, schemas, common, validator, trigger_rules,
                                               proposal_rules, repo)
        if not ran:
            continue
        step = None
        current = common.artifact_root(repo) / item / ".current-step"
        if current.exists():
            try:
                step = json.loads(current.read_text()).get("step")
            except (json.JSONDecodeError, ValueError, OSError):
                step = None
        summary = "ok" if ok else "; ".join(problems)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "item": item,
            "step": step,
            "artifact": filename,
            "hook": "check-edge",
            "session_id": payload.get("session_id"),
            "agent_id": payload.get("agent_id"),
            # The sha of the bytes this edge actually ran over. The sentinel carries one too,
            # but it sits beside the artifact and is as editable as the artifact is; the trace
            # is append-only, which is what makes a later hand-edit detectable at all.
            "sha256": common.sha256(path),
            "edge": {"name": "+".join(ran), "exit": 0 if ok else 1, "summary": summary[:500]},
        }
        if metrics:
            record["metrics"] = metrics
        disagreement = policy_disagreements(path, common, trigger_rules, repo)
        if disagreement:
            record["policy_disagreement"] = disagreement
        common.append_trace(repo, item, record)
        if not ok:
            failures.append((path, problems))

    if failures:
        lines = ["Edge check failed. The artifact is on disk but the flow cannot advance past it."]
        for path, problems in failures:
            lines.append(f"\n{path}:")
            lines += [f"  - {p}" for p in problems]
        lines.append("\nFix the artifact (and its sentinel) and write it again.")
        print("\n".join(lines), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
