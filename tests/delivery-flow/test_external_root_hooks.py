#!/usr/bin/env python3
"""The hooks under a configured `artifacts.root` outside the repo.

Every other fixture in this suite uses the default in-repo `delivery/`, which is why the
`artifacts.root` branch shipped broken: `check-edge` globbed the configured root correctly and
then parsed the result without it, so every artifact under an external root returned
`(None, None)` and was skipped. Edges silently stopped running. `enforce-punch-outs` went inert
for a related reason — it gated on the payload containing the string `delivery/`, which never
appears once the root moves.

The paths here contain a space on purpose. The real root is `~/Amazon RAG/Atlas/RAG/_runs`, and
a quoting bug would be invisible against a tmpdir with no spaces in it.

Run: python3 tests/delivery-flow/test_external_root_hooks.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
EDGE = ROOT / "hooks" / "check-edge.py"
ENFORCE = ROOT / "hooks" / "enforce-punch-outs.py"
sys.path.insert(0, str(SCRIPTS))

import common  # noqa: E402

TRIAGE = {"item": "AN-1", "type": "feature", "path": "standard", "domains": ["backend"],
          "summary": "s", "rationale": "r", "handoff": False, "handoff_reason": None,
          "architecture_change": False, "breaking_change": False}


# Valid enough for `openspec validate --strict`, which runs as an extra layer wherever the
# CLI is installed: an ADDED requirement needs requirement text and at least one scenario.
# A fixture that fails it would make the proposal edge look broken for the wrong reason.
VALID_DELTA_SPEC = """## ADDED Requirements

### Requirement: Callers can request a date range

The endpoint SHALL accept a start and end date and SHALL return only the records that fall
within them.

#### Scenario: A caller requests a range

- **GIVEN** a ledger holding records across several dates
- **WHEN** a caller requests a date range
- **THEN** only the records inside that range are returned
"""


def breakdown(stories=2):
    return {"item": "AN-1", "epics": [{"id": "E1", "title": "T", "stories": [
        {"id": f"S{i}", "statement": f"story {i}", "domains": ["backend"],
         "acceptance_criteria": [{"id": f"AC{i}", "given": "g", "when": "w", "then": "t"}]}
        for i in range(1, stories + 1)]}]}


class ExternalRoot:
    """A delivery repo whose artifacts live outside it, in a path containing a space."""

    def __init__(self):
        base = Path(tempfile.mkdtemp())
        self.runs = base / "Amazon RAG" / "Atlas" / "RAG" / "_runs"
        self.runs.mkdir(parents=True)
        self.repo = base / "repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        (self.repo / ".delivery-flow.yaml").write_text(
            "tracker:\n  kind: jira\nprofile: full\n"
            f"artifacts:\n  root: {self.runs}\n  commit: false\n"
            "decisions:\n  allowed_signers: /nonexistent/allowed_signers\n")
        self.item = "AN-1"
        self.item_dir = self.runs / self.item
        self.item_dir.mkdir()

    def write(self, name, doc):
        (self.item_dir / name).write_text(json.dumps(doc, indent=2))

    def sentinel(self, name, step, counts=None):
        argv = [sys.executable, str(SCRIPTS / "write-sentinel.py"),
                str(self.item_dir / name), "--step", step]
        for key, value in (counts or {}).items():
            argv += ["--count", f"{key}={value}"]
        return subprocess.run(argv, capture_output=True, text=True)

    def edge(self, name, tool="Write"):
        payload = {"hook_event_name": "PostToolUse", "tool_name": tool,
                   "cwd": str(self.repo),
                   "tool_input": {"file_path": str(self.item_dir / name)} if tool == "Write"
                   else {"command": f'cat x > "{self.item_dir / name}"'}}
        return subprocess.run([sys.executable, str(EDGE)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def enforce(self, tool, tool_input):
        payload = {"hook_event_name": "PreToolUse", "tool_name": tool,
                   "cwd": str(self.repo), "tool_input": tool_input}
        return subprocess.run([sys.executable, str(ENFORCE)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def trace(self):
        path = self.item_dir / "trace.jsonl"
        if not path.exists():
            return []
        return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]

    def open_punch_out(self):
        (self.item_dir / "punch-out-1.md").write_text("# Punch-out 1: architecture\n\nbody\n")
        (self.item_dir / ".current-step").write_text(
            json.dumps({"step": "breakdown", "item": self.item}))


class TestEdgeUnderExternalRoot(unittest.TestCase):
    def test_a_good_artifact_is_checked_and_traced(self):
        """The defect: the glob found it, the parse threw it away, nothing was recorded."""
        r = ExternalRoot()
        r.write("breakdown.json", breakdown())
        self.assertEqual(r.sentinel("breakdown.json", "breakdown").returncode, 0)
        out = r.edge("breakdown.json")
        self.assertEqual(out.returncode, 0, out.stderr)
        records = [x for x in r.trace() if x.get("artifact") == "breakdown.json"]
        self.assertTrue(records, "the edge produced no trace record under an external root")
        self.assertEqual(records[-1]["edge"]["exit"], 0)

    def test_a_bad_artifact_is_rejected(self):
        r = ExternalRoot()
        r.write("triage.json", {**TRIAGE, "type": "enhancement", "handoff": "yes"})
        r.sentinel("triage.json", "triage")
        out = r.edge("triage.json")
        self.assertEqual(out.returncode, 2, "a schema violation must still block")
        self.assertIn("enhancement", out.stderr)

    def test_a_sentinel_count_lie_is_caught(self):
        r = ExternalRoot()
        r.write("breakdown.json", breakdown(stories=2))
        r.sentinel("breakdown.json", "breakdown", counts={"stories": 99})
        out = r.edge("breakdown.json")
        self.assertEqual(out.returncode, 2)
        self.assertIn("99", out.stderr)

    def test_content_detection_catches_a_write_the_command_text_hides(self):
        """The handoff asked for this to be confirmed, not assumed.

        A Bash redirect through a shell variable under an external root leaves no
        `delivery/`-shaped fragment in the command, so only content comparison can find it.
        """
        r = ExternalRoot()
        r.write("breakdown.json", breakdown())
        r.sentinel("breakdown.json", "breakdown", counts={"stories": 99})
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Bash",
                   "cwd": str(r.repo),
                   "tool_input": {"command": f'R="{r.item_dir}"; cat x > "$R/breakdown.json"'}}
        out = subprocess.run([sys.executable, str(EDGE)], input=json.dumps(payload),
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 2, f"content detection missed it: {out.stderr}")
        self.assertIn("99", out.stderr)

    def test_a_space_in_the_root_does_not_break_it(self):
        r = ExternalRoot()
        self.assertIn(" ", str(r.runs))
        r.write("breakdown.json", breakdown())
        r.sentinel("breakdown.json", "breakdown")
        self.assertEqual(r.edge("breakdown.json").returncode, 0)
        self.assertTrue(r.trace())

    def test_it_stays_inert_in_a_repo_with_no_config(self):
        plain = Path(tempfile.mkdtemp())
        (plain / ".git").mkdir()
        (plain / "delivery" / "AN-1").mkdir(parents=True)
        (plain / "delivery" / "AN-1" / "notes.txt").write_text("scratch")
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Write", "cwd": str(plain),
                   "tool_input": {"file_path": str(plain / "delivery" / "AN-1" / "notes.txt")}}
        out = subprocess.run([sys.executable, str(EDGE)], input=json.dumps(payload),
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0)


class TestTheSentinelLandsAfterTheArtifact(unittest.TestCase):
    """The node contract, reproduced exactly: Write the artifact, then Bash the sentinel.

    `SKILL.md` specifies that ordering, so the hook fires on the artifact's write while the
    sentinel does not yet exist. That first verdict is a legitimate failure *for the instant
    it was taken* — and before this fix it was permanent. The sentinel landed a moment later
    and nothing re-checked: `written_paths` found nothing in the Bash call (its regex needs a
    literal `delivery/`, which a configured root need not have, and its character class
    excludes the space in `Amazon RAG`), and `changed_artifacts` skipped the artifact because
    its bytes had not changed since the failing record.

    So a correct artifact with a correct sentinel blocked AN-3702 forever, and rerunning the
    step reproduced the same deadlock because the rerun repeats the same ordering.
    """

    def sentinel_via_bash(self, r, name, step):
        """The sentinel written the way a node writes it: a separate Bash call."""
        command = (f'python3 "{SCRIPTS / "write-sentinel.py"}" '
                   f'"{r.item_dir / name}" --step {step}')
        subprocess.run(command, shell=True, capture_output=True, text=True)
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Bash",
                   "cwd": str(r.repo), "tool_input": {"command": command}}
        return subprocess.run([sys.executable, str(EDGE)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def test_the_failure_is_cleared_when_the_sentinel_arrives(self):
        r = ExternalRoot()
        r.write("triage.json", TRIAGE)

        first = r.edge("triage.json")
        self.assertEqual(2, first.returncode, "a missing sentinel must fail at the time")
        self.assertIn("sentinel", first.stderr)
        records = [x for x in r.trace() if x.get("artifact") == "triage.json"]
        self.assertEqual(1, len(records))
        self.assertEqual(1, records[-1]["edge"]["exit"])

        out = self.sentinel_via_bash(r, "triage.json", "triage")
        self.assertEqual(0, out.returncode, out.stderr)
        records = [x for x in r.trace() if x.get("artifact") == "triage.json"]
        self.assertEqual(2, len(records), f"the edge did not run again: {r.trace()}")
        self.assertEqual(0, records[-1]["edge"]["exit"],
                         f"the stale failure was never cleared: {records[-1]['edge']}")

    def test_flow_status_is_no_longer_blocked(self):
        """The symptom the run actually presented with."""
        r = ExternalRoot()
        r.write("item.json", {"key": r.item, "title": "t", "body": "acceptance: b",
                              "status": "Open", "url": "https://example.invalid/1",
                              "source": "jira", "labels": [], "links": []})
        r.sentinel("item.json", "intake")
        r.edge("item.json")
        r.write("triage.json", TRIAGE)
        r.edge("triage.json")
        self.sentinel_via_bash(r, "triage.json", "triage")
        out = subprocess.run([sys.executable, str(SCRIPTS / "flow-status.py"),
                              r.item, "--repo", str(r.repo)], capture_output=True, text=True)
        self.assertNotIn("BLOCKED", out.stdout, out.stdout)

    def test_a_still_broken_artifact_stays_failed(self):
        """Re-evaluation must not amount to forgiveness. The retry re-runs the check; an
        artifact that is genuinely wrong fails it again."""
        r = ExternalRoot()
        r.write("triage.json", {**TRIAGE, "type": "enhancement"})
        self.assertEqual(2, r.edge("triage.json").returncode)
        out = self.sentinel_via_bash(r, "triage.json", "triage")
        self.assertEqual(2, out.returncode, "a schema violation must survive the retry")
        records = [x for x in r.trace() if x.get("artifact") == "triage.json"]
        self.assertEqual(1, records[-1]["edge"]["exit"])

    def test_a_persistent_failure_does_not_record_forever(self):
        """The regression the first fix shipped, and the test that was missing.

        `or failed` re-checked on every hook invocation while the last verdict was a failure.
        For a failure whose cause is neither the artifact nor its sentinel, nothing ever
        changes, so it appended a record each time: 44 identical failures on one artifact in
        the live AN-3702, and AN-3631 from 8 failed edges to 65. The earlier suite asked only
        whether a *passing* record suppresses re-checking.
        """
        r = ExternalRoot()
        # Fails on something that is neither the artifact nor the sentinel: a proposal whose
        # change directory does not exist. Both inputs are valid and stay valid.
        r.write("proposal.json", {
            "item": r.item, "change_id": "nope", "change_path": "openspec/changes/nope",
            "specs_touched": [], "tasks": [{"id": "T1", "description": "d", "files": ["a.py"]}],
            "dependencies_added": [], "scope": False, "architecture": False, "breaking": False})
        self.assertEqual(0, r.sentinel("proposal.json", "propose").returncode)
        self.assertEqual(2, r.edge("proposal.json").returncode)
        after_first = len([x for x in r.trace() if x.get("artifact") == "proposal.json"])
        self.assertEqual(1, after_first)

        payload = {"hook_event_name": "PostToolUse", "tool_name": "Bash",
                   "cwd": str(r.repo), "tool_input": {"command": "ls -la"}}
        for _ in range(5):
            subprocess.run([sys.executable, str(EDGE)], input=json.dumps(payload),
                           capture_output=True, text=True)
        after = len([x for x in r.trace() if x.get("artifact") == "proposal.json"])
        self.assertEqual(after_first, after,
                         f"the failure re-recorded {after - after_first} extra times")

    def test_the_record_carries_the_sentinel_sha(self):
        """What lets the gate tell a sentinel landing from nothing happening."""
        r = ExternalRoot()
        r.write("breakdown.json", breakdown())
        r.sentinel("breakdown.json", "breakdown")
        r.edge("breakdown.json")
        rec = [x for x in r.trace() if x.get("artifact") == "breakdown.json"][-1]
        expected = common.sha256(r.item_dir / "breakdown.json.sentinel.json")
        self.assertEqual(expected, rec["sentinel_sha256"])

    def test_a_rewritten_sentinel_is_rechecked(self):
        """A sentinel that starts lying after a pass must not be suppressed by the gate."""
        r = ExternalRoot()
        r.write("breakdown.json", breakdown(stories=2))
        r.sentinel("breakdown.json", "breakdown")
        self.assertEqual(0, r.edge("breakdown.json").returncode)
        r.sentinel("breakdown.json", "breakdown", counts={"stories": 99})
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Bash",
                   "cwd": str(r.repo), "tool_input": {"command": "ls -la"}}
        out = subprocess.run([sys.executable, str(EDGE)], input=json.dumps(payload),
                             capture_output=True, text=True)
        self.assertEqual(2, out.returncode, "a sentinel rewritten to lie was not re-checked")
        self.assertIn("99", out.stderr)

    def test_a_passing_record_still_suppresses_rechecking(self):
        """The sha gate's real job. Only a failure is retried, or the trace triples."""
        r = ExternalRoot()
        r.write("breakdown.json", breakdown())
        r.sentinel("breakdown.json", "breakdown")
        self.assertEqual(0, r.edge("breakdown.json").returncode)
        before = len([x for x in r.trace() if x.get("artifact") == "breakdown.json"])
        self.assertEqual(1, before)
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Bash",
                   "cwd": str(r.repo), "tool_input": {"command": "ls -la"}}
        for _ in range(3):
            subprocess.run([sys.executable, str(EDGE)], input=json.dumps(payload),
                           capture_output=True, text=True)
        after = len([x for x in r.trace() if x.get("artifact") == "breakdown.json"])
        self.assertEqual(before, after, "a passing edge was re-recorded")


class TestProposalResolvesAgainstTheCodeRepo(unittest.TestCase):
    """The change directory lives in the code repo, never beside the artifact.

    `check_artifact` inferred the repo with `repo_root(path.parent)`. Under an external
    `artifacts.root` the artifact's parent is the vault, so the change-directory check looked
    for `openspec/changes/<id>` in the vault, did not find it, and reported "no change
    directory" — blaming the node for a directory it had correctly created in the repo. The
    hook's `identify()` already knows the right repo; it now hands it in.
    """

    PROPOSAL = {
        "item": "AN-1", "change_id": "add-range", "change_path": "openspec/changes/add-range",
        "specs_touched": ["openspec/changes/add-range/specs/range/spec.md"],
        "tasks": [{"id": "T1", "description": "Add the range endpoint",
                   "files": ["src/Range.scala"]}],
        "dependencies_added": [], "scope": False, "architecture": False, "breaking": False,
    }

    def change_dir(self, r):
        """The OpenSpec change directory, in the code repo where the node puts it."""
        d = r.repo / "openspec" / "changes" / "add-range"
        (d / "specs" / "range").mkdir(parents=True)
        for name in ("proposal.md", "design.md"):
            (d / name).write_text(f"# {name}\n")
        (d / "specs" / "range" / "spec.md").write_text(VALID_DELTA_SPEC)
        (d / "tasks.md").write_text("## 1. Work\n\n- [ ] T1 Add the range endpoint\n")
        return d

    def test_the_change_directory_is_found_in_the_code_repo(self):
        r = ExternalRoot()
        self.change_dir(r)
        r.write("proposal.json", self.PROPOSAL)
        self.assertEqual(r.sentinel("proposal.json", "propose").returncode, 0)
        out = r.edge("proposal.json")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertNotIn("no change directory", out.stderr)
        records = [x for x in r.trace() if x.get("artifact") == "proposal.json"]
        self.assertTrue(records)
        self.assertEqual(0, records[-1]["edge"]["exit"])
        self.assertIn("change-dir", records[-1]["edge"]["name"])

    def test_a_genuinely_missing_change_directory_still_fails(self):
        """Handing the repo in must not make the check toothless."""
        r = ExternalRoot()
        r.write("proposal.json", self.PROPOSAL)
        r.sentinel("proposal.json", "propose")
        out = r.edge("proposal.json")
        self.assertEqual(2, out.returncode)
        self.assertIn("no change directory", out.stderr)

    def test_the_failure_names_the_absolute_path_it_looked_in(self):
        """So a wrong repo is visible instead of reading as a missing directory."""
        r = ExternalRoot()
        r.write("proposal.json", self.PROPOSAL)
        r.sentinel("proposal.json", "propose")
        out = r.edge("proposal.json")
        self.assertIn(str(r.repo / "openspec" / "changes" / "add-range"), out.stderr)

    def test_the_vault_is_not_where_it_looks(self):
        """The precise regression, and the one that needs the vault to be a git repo.

        The real vault is itself a git repo — that is how the run trail is versioned — so
        `repo_root` walking up from an artifact inside it *succeeds*, and returns the vault.
        Without the `.git` below this test passes either way, because the walk falls off the
        top and the decoy is never reached: it would assert the right thing and prove nothing.
        """
        r = ExternalRoot()
        vault = r.runs.parent.parent.parent          # the vault's own root: `~/Amazon RAG`
        (vault / ".git").mkdir(exist_ok=True)
        # Planted where the broken inference looks — `repo_root(artifact.parent)` resolves to
        # the vault root, so that is the only place a decoy could ever have satisfied it.
        decoy = vault / "openspec" / "changes" / "add-range"
        (decoy / "specs" / "range").mkdir(parents=True)
        for name in ("proposal.md", "design.md"):
            (decoy / name).write_text(f"# {name}\n")
        (decoy / "specs" / "range" / "spec.md").write_text(VALID_DELTA_SPEC)
        (decoy / "tasks.md").write_text("## 1. Work\n\n- [ ] T1 Add the range endpoint\n")
        r.write("proposal.json", self.PROPOSAL)
        r.sentinel("proposal.json", "propose")
        out = r.edge("proposal.json")
        self.assertEqual(2, out.returncode, "a decoy in the vault satisfied the check")
        self.assertIn("no change directory", out.stderr)


class TestBashPathsResolveAgainstTheRoot(unittest.TestCase):
    """Seam 1: find the artifact from the real roots, not from the command's spelling."""

    def test_the_root_spelled_out_in_the_command_is_found(self):
        r = ExternalRoot()
        r.write("triage.json", TRIAGE)
        command = f'python3 write-sentinel.py "{r.item_dir / "triage.json"}" --step triage'
        found = [str(p) for p in _edge_module().rooted_paths(command, [r.runs])]
        self.assertIn(str(r.item_dir / "triage.json"), found)

    def test_a_root_held_in_a_variable_is_found_by_its_tail(self):
        r = ExternalRoot()
        r.write("triage.json", TRIAGE)
        command = f'R="{r.runs}"; python3 write-sentinel.py "$R/{r.item}/triage.json"'
        found = [str(p) for p in _edge_module().rooted_paths(command, [r.runs])]
        self.assertIn(str(r.item_dir / "triage.json"), found)

    def test_a_space_in_the_root_is_not_what_breaks_it(self):
        r = ExternalRoot()
        self.assertIn(" ", str(r.runs), "the fixture must keep its space")
        r.write("triage.json", TRIAGE)
        command = f'cat x > "{r.item_dir / "triage.json"}"'
        found = [str(p) for p in _edge_module().rooted_paths(command, [r.runs])]
        self.assertIn(str(r.item_dir / "triage.json"), found)

    def test_an_unmentioned_item_is_not_invented(self):
        r = ExternalRoot()
        found = _edge_module().rooted_paths("echo hello", [r.runs])
        self.assertEqual([], found)

    def test_no_registered_roots_means_no_paths(self):
        self.assertEqual([], _edge_module().rooted_paths("cat x > /a/AN-1/triage.json", []))


def _edge_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_edge_mod", EDGE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestEnforceUnderExternalRoot(unittest.TestCase):
    def test_a_decision_write_is_denied(self):
        """The hook that matters most: nobody but a human writes a decision."""
        r = ExternalRoot()
        r.open_punch_out()
        out = r.enforce("Write", {"file_path": str(r.item_dir / "decisions" / "punch-out-1.json"),
                                  "content": '{"choice":"proceed"}'})
        self.assertIn("deny", out.stdout.lower() + out.stderr.lower(),
                      f"a decision write was permitted under an external root: {out.stdout}")

    def test_invoking_decide_py_is_denied(self):
        r = ExternalRoot()
        r.open_punch_out()
        out = r.enforce("Bash", {"command": f"python3 {SCRIPTS}/decide.py AN-1 punch-out-1 "
                                            "--choose proceed"})
        self.assertIn("deny", out.stdout.lower() + out.stderr.lower())

    def test_a_merge_is_denied(self):
        r = ExternalRoot()
        r.open_punch_out()
        out = r.enforce("Bash", {"command": "gh pr merge 12 --squash"})
        self.assertIn("deny", out.stdout.lower() + out.stderr.lower())

    def test_it_stays_inert_outside_a_delivery_repo(self):
        plain = Path(tempfile.mkdtemp())
        (plain / ".git").mkdir()
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": str(plain),
                   "tool_input": {"command": "gh pr merge 12 --squash"}}
        out = subprocess.run([sys.executable, str(ENFORCE)], input=json.dumps(payload),
                             capture_output=True, text=True)
        self.assertNotIn("deny", out.stdout.lower(),
                         "the hook must be inert where no delivery-flow config exists")


class TestTheChangeDirectoryResolvesAgainstTheRepo(unittest.TestCase):
    """`proposal.json`'s change directory lives in the delivery repo, not under the root.

    This blocked a real run at `propose`. `check_artifact` called
    `proposal_rules.problems(path, common.repo_root(path.parent))`, and `path.parent` is the
    item directory under `artifacts.root`. The real root is inside the Obsidian vault, which
    is itself a git repo, so `repo_root` climbed to the vault and looked for
    `openspec/changes/<id>` there — somewhere a change directory will never be. The edge
    reported "no change directory at openspec/changes/<id>" against a change that existed, and
    the flow correctly refused to advance past a failed edge. A checker bug presenting as a bad
    artifact.

    It also hid a second check: `openspec-validate` only runs once the directory is found, so
    it had never executed under an external root at all.

    `policy_disagreements` already took `repo` for this exact reason; this one call site was
    missed. The lesson is the one the rest of this file records — a default argument that
    resolves from the artifact's own path is wrong the moment the artifacts move.
    """

    CHANGE_ID = "add-thing"

    def _fixture(self):
        x = ExternalRoot()
        change = x.repo / "openspec" / "changes" / self.CHANGE_ID
        (change / "specs" / "thing").mkdir(parents=True)
        (change / "specs" / "thing" / "spec.md").write_text("## ADDED Requirement: a\n")
        for name in ("proposal.md", "design.md", "tasks.md"):
            (change / name).write_text("- [ ] T1 do it\n")
        x.write("proposal.json", {
            "item": "AN-1", "change_id": self.CHANGE_ID,
            "change_path": f"openspec/changes/{self.CHANGE_ID}",
            "specs_touched": [], "tasks": [
                {"id": "T1", "description": "do it", "files": ["src/a.py"]}]})
        return x, change

    def _problems(self, path, repo):
        """`check_artifact`'s change-dir problems, with and without the repo threaded in."""
        import importlib.util

        import common

        def load(name, p):
            spec = importlib.util.spec_from_file_location(name, p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod

        ce = load("ce", EDGE)
        va = load("va", SCRIPTS / "validate-artifact.py")
        tg = load("tg", SCRIPTS / "triggers.py")
        pr = load("pr", SCRIPTS / "validate-proposal.py")
        _ok, problems, ran = ce.check_artifact(path, common.load_schemas(), common, va, tg, pr,
                                               repo)
        return problems, ran

    def test_the_change_directory_is_found_in_the_repo(self):
        x, _ = self._fixture()
        problems, ran = self._problems(x.item_dir / "proposal.json", x.repo)
        self.assertIn("change-dir", ran)
        missing = [p for p in problems if "no change directory" in p]
        self.assertEqual(missing, [], f"the change dir exists in {x.repo} and was not found")

    def test_without_the_repo_it_looks_in_the_wrong_place(self):
        """Pins the old behaviour, so the fix cannot be quietly reverted.

        Asserted through the default-argument path rather than by editing the source: calling
        with `repo=None` is exactly what the buggy call site did.
        """
        x, _ = self._fixture()
        problems, _ = self._problems(x.item_dir / "proposal.json", None)
        self.assertTrue([p for p in problems if "no change directory" in p],
                        "resolving from the artifact path should miss the change dir")

    def test_openspec_validate_becomes_reachable(self):
        """The check the bug was hiding. It cannot run until the directory is found.

        `openspec` may not be installed, in which case the checker records the attempt
        differently — so this asserts the gating problem is gone rather than that the
        validator ran, which would make the test depend on the host.
        """
        x, _ = self._fixture()
        problems, ran = self._problems(x.item_dir / "proposal.json", x.repo)
        self.assertIn("change-dir", ran)
        self.assertNotIn("no change directory at openspec/changes/" + self.CHANGE_ID, problems)


if __name__ == "__main__":
    unittest.main(verbosity=2)
