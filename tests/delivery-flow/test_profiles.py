#!/usr/bin/env python3
"""Tests for profiles: a named slice of the routing table, and how a slice ends.

Run: python3 tests/delivery-flow/test_profiles.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
FLOW = SCRIPTS / "flow-status.py"
OUTCOME = SCRIPTS / "write-outcome.py"
BRIEF = SCRIPTS / "render-brief.py"
EDGE = ROOT / "hooks" / "check-edge.py"
SENTINEL = SCRIPTS / "write-sentinel.py"

sys.path.insert(0, str(SCRIPTS))
from common import load_profiles, select_profile  # noqa: E402

TRIAGE = {"item": "PRO-1", "type": "feature", "path": "standard", "domains": ["backend"],
          "summary": "Add bounded backoff so a slow downstream is not retried into collapse.",
          "rationale": "Immediate retries amplify load.", "handoff": False,
          "handoff_reason": None, "architecture_change": False, "breaking_change": False}
ITEM = {"key": "PRO-1", "title": "Retries hammer the consumer", "body": "No backoff.",
        "status": "Open", "url": "https://example.invalid/PRO-1", "source": "jira",
        "labels": ["dlq"], "links": []}
BREAKDOWN = {"item": "PRO-1", "epics": [{"id": "E1", "title": "Backoff", "stories": [
    {"id": "S1", "statement": "Retry with capped exponential backoff", "domains": ["backend"],
     "acceptance_criteria": [{"id": "AC1", "given": "a timeout", "when": "it retries",
                              "then": "delays grow to a 30s cap"}]}]}]}
CHALLENGE = {"item": "PRO-1", "target": "breakdown.json", "verdict": "WEAKENED",
             "attacks": [{"attack": "idempotency?", "method": "read criteria", "result": "landed"},
                         {"attack": "cap?", "method": "read the ticket", "result": "failed"},
                         {"attack": "metrics?", "method": "read criteria", "result": "failed"}],
             "findings": [{"finding": "No story covers idempotent redelivery.",
                           "evidence": "AC1 describes timing only."}]}


class Repo:
    def __init__(self, profile="triage", vault=False, item="PRO-1"):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / ".git").mkdir()
        # In-repo artifacts, declared as such: the preflight refuses an unexplained in-repo
        # root, because that is where a client's ticket text gets committed by accident.
        cfg = ("tracker:\n  kind: jira\n  external: true\nforge:\n  kind: github-pr\n"
               "artifacts:\n  in_repo_ack: test fixture, no real ticket text\n")
        if profile is not None:
            cfg += f"profile: {profile}\n"
        cfg += "vault:\n  binding: olympus\n" if vault else "vault:\n  binding: null\n"
        (self.dir / ".delivery-flow.yaml").write_text(cfg)
        self.item = item
        self.item_dir = self.dir / "delivery" / item
        self.item_dir.mkdir(parents=True)

    def artifact(self, name, doc):
        (self.item_dir / name).write_text(json.dumps(doc, indent=2))

    def through_the_hook(self, name):
        """Write the sentinel and fire the edge hook, as a real run does.

        Terminal prose gets no sentinel: a sentinel is a node's claim about its own output,
        and the brief's producer is a script with nothing to claim.
        """
        if name.endswith(".json"):
            subprocess.run([sys.executable, str(SENTINEL), str(self.item_dir / name),
                            "--step", name.removesuffix(".json")], capture_output=True, check=True)
        payload = json.dumps({"tool_name": "Write",
                              "tool_input": {"file_path": str(self.item_dir / name)},
                              "cwd": str(self.dir)})
        return subprocess.run([sys.executable, str(EDGE)], input=payload.encode(),
                              capture_output=True)

    def chain(self):
        """Everything up to the brief, written the way the flow writes it."""
        for name, doc in (("item.json", ITEM), ("triage.json", TRIAGE),
                          ("breakdown.json", BREAKDOWN), ("challenge-breakdown.json", CHALLENGE)):
            self.artifact(name, doc)
            out = self.through_the_hook(name)
            assert out.returncode == 0, f"{name}: {out.stderr.decode()}"
        self.run(BRIEF)
        assert self.through_the_hook("summary.md").returncode == 0

    def run(self, script, *args):
        return subprocess.run([sys.executable, str(script), self.item, "--repo", str(self.dir),
                               *args], capture_output=True, text=True)


class TestProfileRouting(unittest.TestCase):
    def test_triage_profile_routes_within_its_own_steps(self):
        r = Repo(profile="triage")
        r.artifact("item.json", ITEM)
        r.artifact("triage.json", TRIAGE)
        out = r.run(FLOW)
        self.assertIn("Next: breakdown", out.stdout)
        self.assertIn("profile triage", out.stdout)
        # Steps outside the profile are not in the table at all.
        self.assertNotIn("proposal.json", out.stdout)
        self.assertNotIn("pr-opened.json", out.stdout)

    def test_absent_profile_key_is_the_full_table(self):
        r = Repo(profile=None)
        out = r.run(FLOW)
        self.assertIn("profile full", out.stdout)
        self.assertIn("proposal.json", out.stdout)
        self.assertIn("vault-updated.json", out.stdout)

    def test_unknown_profile_is_refused(self):
        r = Repo(profile="nope")
        out = r.run(FLOW)
        self.assertEqual(out.returncode, 2)
        self.assertIn("unknown profile", out.stderr)
        self.assertIn("full", out.stderr)
        self.assertIn("triage", out.stderr)

    def test_the_brief_is_in_both_profiles(self):
        """It is the triage profile's terminus and the full profile's approval surface."""
        self.assertIn("summary.md", Repo(profile="triage").run(FLOW).stdout)
        self.assertIn("summary.md", Repo(profile="full").run(FLOW).stdout)

    def test_propose_is_in_the_full_profile_only(self):
        self.assertIn("proposal.json", Repo(profile="full").run(FLOW).stdout)
        self.assertNotIn("proposal.json", Repo(profile="triage").run(FLOW).stdout)

    def test_the_full_profile_briefs_after_proposing_and_before_implementing(self):
        """Explanation before decision: the proposal's triggers fire on leaving the brief."""
        out = Repo(profile="full").run(FLOW).stdout
        self.assertLess(out.index("proposal.json"), out.index("summary.md"))
        self.assertLess(out.index("summary.md"), out.index("implementation.json"))

    def test_the_triage_profile_is_unchanged_by_the_proposal_step(self):
        """The certified chain's routing must not move when the full profile grows."""
        st = json.loads(Repo(profile="triage").run(FLOW, "--json").stdout)
        self.assertEqual([r["step"] for r in st["table"]],
                         ["intake", "triage", "project-memory", "breakdown",
                          "challenge-breakdown", "brief", "report"])
        self.assertEqual([r["artifact"] for r in st["table"]],
                         ["item.json", "triage.json", "project-context.json", "breakdown.json",
                          "challenge-breakdown.json", "summary.md", "outcome.json"])


class TestProfileCoverage(unittest.TestCase):
    """profiles.yaml and the routing table must describe the same pipeline."""

    def setUp(self):
        self.profiles = load_profiles()
        import importlib.util
        spec = importlib.util.spec_from_file_location("flow_status", FLOW)
        self.flow = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.flow)

    def test_every_profile_step_exists_in_the_routing_table(self):
        known = {step for _a, step, _k, _o in self.flow.STEPS}
        for p in self.profiles:
            unknown = set(p["steps"]) - known
            self.assertFalse(unknown, f"profile {p['profile']} names unknown steps: {unknown}")

    def test_the_union_of_profiles_covers_the_routing_table(self):
        covered = {s for p in self.profiles for s in p["steps"]}
        orphans = {step for _a, step, _k, _o in self.flow.STEPS} - covered
        self.assertFalse(orphans, f"steps in the table but in no profile: {orphans}")

    def test_terminus_is_the_last_step(self):
        for p in self.profiles:
            self.assertEqual(p["terminus"], p["steps"][-1], f"profile {p['profile']}")

    def test_next_names_a_real_profile_or_nothing(self):
        names = {p["profile"] for p in self.profiles}
        for p in self.profiles:
            if p["next"] is not None:
                self.assertIn(p["next"], names, f"profile {p['profile']} points at {p['next']}")

    def test_a_wrapped_steps_list_is_an_error_not_a_short_list(self):
        """A continuation line would silently truncate a profile, so the parser refuses it."""
        bad = Path(tempfile.mkdtemp()) / "profiles.yaml"
        bad.write_text("profiles:\n  - profile: x\n    terminus: report\n    next: null\n"
                       "    steps: [intake, triage,\n            report]\n")
        with self.assertRaises(ValueError) as cm:
            load_profiles(bad)
        self.assertIn("does not close", str(cm.exception))

    def test_a_profile_step_absent_from_the_table_is_reported(self):
        p, _ = select_profile({"profile": "triage"}, self.profiles)
        rows, err = self.flow.profile_steps({**p, "steps": ["intake", "invented-step"]})
        self.assertIsNone(rows)
        self.assertIn("invented-step", err)


class TestTheOutcomeIsWrittenOnce(unittest.TestCase):
    """A terminal outcome is a record, and a record a later run can replace is not one.

    AN-3702 was reported `completed` on the `triage` profile at 16:08 — the first certified
    data point criterion 4 had ever had. A second report at 16:16 overwrote it. The clean
    completion became unrecoverable, and the file that replaced it still claimed
    `profile: triage` while the item had since run `propose` and `implementation`.
    """

    def test_a_second_report_is_refused(self):
        r = Repo(profile="triage")
        r.chain()
        self.assertEqual(0, r.run(OUTCOME).returncode)
        first = (r.item_dir / "outcome.json").read_text()
        out = r.run(OUTCOME)
        self.assertEqual(1, out.returncode)
        self.assertIn("already reported", out.stderr)
        self.assertEqual(first, (r.item_dir / "outcome.json").read_text(),
                         "the first outcome was overwritten")

    def test_the_refusal_says_how_to_proceed_deliberately(self):
        r = Repo(profile="triage")
        r.chain()
        r.run(OUTCOME)
        err = r.run(OUTCOME).stderr
        self.assertIn("--force", err)
        self.assertIn("DISCARDED-", err)

    def test_force_replaces_it(self):
        r = Repo(profile="triage")
        r.chain()
        r.run(OUTCOME)
        self.assertEqual(0, r.run(OUTCOME, "--force").returncode)

    def test_a_dry_run_never_refuses(self):
        """It writes nothing, so there is nothing to protect."""
        r = Repo(profile="triage")
        r.chain()
        r.run(OUTCOME)
        self.assertEqual(0, r.run(OUTCOME, "--dry-run").returncode)


class TestOffProfileArtifactsAreNamed(unittest.TestCase):
    """The outcome must not imply a profile the run did not follow.

    `profile:` is a live config file, so the setting at report time is not evidence of what
    ran. Both AN-3702 and AN-3631 carry `profile: triage` while their directories hold
    `proposal.json`, a `full`-only artifact. The certified-only rate is computed per profile,
    so a run credited to a profile it did not follow corrupts the one number Stage 4 asks for
    — and on AN-3702 it did so in the flattering direction.
    """

    def test_an_artifact_outside_the_profile_is_recorded(self):
        r = Repo(profile="triage")
        r.chain()
        # A `full`-only artifact in a `triage`-profile run: the shape both real runs have.
        r.artifact("proposal.json", {
            "item": r.item, "change_id": "add-thing",
            "change_path": "openspec/changes/add-thing", "specs_touched": [],
            "tasks": [{"id": "T1", "description": "d", "files": ["a.py"]}],
            "dependencies_added": [], "scope": False, "architecture": False,
            "breaking": False})
        self.assertEqual(0, r.run(OUTCOME).returncode)
        doc = json.loads((r.item_dir / "outcome.json").read_text())
        self.assertEqual(["proposal.json"], doc["off_profile_artifacts"])
        self.assertEqual("triage", doc["profile"])

    def test_a_clean_run_has_no_such_field(self):
        """Absent rather than empty: a run that stayed in its profile makes no claim."""
        r = Repo(profile="triage")
        r.chain()
        r.run(OUTCOME)
        doc = json.loads((r.item_dir / "outcome.json").read_text())
        self.assertNotIn("off_profile_artifacts", doc)

    def test_the_outcome_still_passes_its_own_edge(self):
        """`outcome.schema.json` is `additionalProperties: false`, so a new field fails the
        edge unless the schema admits it. Written because the first version of this change
        added the field and not the schema, and every test still passed — none of them put
        `outcome.json` through the hook that governs it."""
        r = Repo(profile="triage")
        r.chain()
        # `implementation.json` rather than `proposal.json`: it is equally off-profile for
        # `triage`, and it has no schema, so the hook records it as `no-schema` instead of
        # failing it. A bare proposal would fail its own edge first and this test would be
        # measuring that failure rather than the outcome's.
        r.artifact("implementation.json", {"item": r.item, "done": True})
        self.assertEqual(0, r.run(OUTCOME).returncode)
        doc = json.loads((r.item_dir / "outcome.json").read_text())
        self.assertEqual(["implementation.json"], doc["off_profile_artifacts"])
        # The hook directly: `write-outcome.py` already wrote the sentinel, with `--step
        # report`, and rewriting it here would claim a different step than the run made.
        payload = json.dumps({"tool_name": "Write",
                              "tool_input": {"file_path": str(r.item_dir / "outcome.json")},
                              "cwd": str(r.dir)})
        out = subprocess.run([sys.executable, str(EDGE)], input=payload.encode(),
                             capture_output=True)
        self.assertEqual(0, out.returncode, out.stderr.decode())


class TestTerminus(unittest.TestCase):
    def test_terminus_produces_a_terminal_artifact(self):
        r = Repo(profile="triage")
        r.chain()
        out = r.run(OUTCOME)
        self.assertEqual(out.returncode, 0, out.stderr)
        doc = json.loads((r.item_dir / "outcome.json").read_text())
        self.assertEqual(doc["status"], "completed")
        self.assertEqual(doc["profile"], "triage")
        self.assertEqual(doc["manual_corrections"], [])

    def test_a_completed_profile_names_the_next_one(self):
        r = Repo(profile="triage")
        r.chain()
        r.run(OUTCOME)
        out = r.run(FLOW)
        self.assertIn("Profile 'triage' complete", out.stdout)
        self.assertIn("next profile: full", out.stdout)
        self.assertIn("next step: propose", out.stdout)

    def test_a_later_profile_resumes_from_the_artifacts_alone(self):
        r = Repo(profile="triage")
        r.chain()
        r.run(OUTCOME)
        cfg = (r.dir / ".delivery-flow.yaml").read_text().replace("profile: triage", "profile: full")
        (r.dir / ".delivery-flow.yaml").write_text(cfg)
        out = r.run(FLOW)
        # Nothing records which profile wrote what: position is recomputed from disk.
        self.assertIn("Next: propose", out.stdout)

    def test_a_stalled_run_is_not_reported_complete(self):
        r = Repo(profile="triage")
        r.artifact("item.json", ITEM)
        out = r.run(OUTCOME)
        self.assertEqual(out.returncode, 2)
        self.assertIn("nothing to report yet", out.stderr)
        self.assertFalse((r.item_dir / "outcome.json").exists())

    def test_a_failing_edge_is_a_failed_outcome_not_a_completed_one(self):
        r = Repo(profile="triage")
        r.chain()
        # A breakdown with no epics violates its schema, so its edge fails.
        r.artifact("breakdown.json", {"item": "PRO-1", "epics": []})
        self.assertNotEqual(r.through_the_hook("breakdown.json").returncode, 0)
        out = r.run(OUTCOME)
        doc = json.loads((r.item_dir / "outcome.json").read_text())
        self.assertEqual(doc["status"], "failed", out.stdout)
        self.assertIn("edge", doc["reason"])

    def test_an_open_punch_out_is_punched_out_not_failed(self):
        r = Repo(profile="triage")
        r.chain()
        (r.item_dir / "punch-out-1.md").write_text("# Punch-out 1: architecture\n\nbody\n")
        r.run(OUTCOME)
        doc = json.loads((r.item_dir / "outcome.json").read_text())
        self.assertEqual(doc["status"], "punched-out")
        self.assertIn("architecture", doc["reason"])

    def test_only_abandoned_may_be_asserted(self):
        r = Repo(profile="triage")
        r.chain()
        out = r.run(OUTCOME, "--status", "completed")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("invalid choice", out.stderr)


class TestManualCorrection(unittest.TestCase):
    """A hand-edited artifact is a failed run, not a repair."""

    def test_an_artifact_edited_after_its_edge_fails_the_run(self):
        r = Repo(profile="triage")
        r.chain()
        doc = json.loads((r.item_dir / "breakdown.json").read_text())
        doc["epics"][0]["title"] = "Backoff (tidied by hand)"
        r.artifact("breakdown.json", doc)  # written directly: no hook, no new trace sha
        r.run(OUTCOME)
        out = json.loads((r.item_dir / "outcome.json").read_text())
        self.assertEqual(out["status"], "failed")
        self.assertIn("manual-correction", out["reason"])
        self.assertEqual([c["artifact"] for c in out["manual_corrections"]], ["breakdown.json"])

    def test_an_artifact_with_no_traced_sha_is_reported_unverifiable(self):
        r = Repo(profile="triage")
        for name, doc in (("item.json", ITEM), ("triage.json", TRIAGE),
                          ("breakdown.json", BREAKDOWN), ("challenge-breakdown.json", CHALLENGE)):
            r.artifact(name, doc)  # never through the hook
        r.run(BRIEF)
        out = r.run(OUTCOME, "--json")
        payload = json.loads(out.stdout)
        self.assertEqual(payload["status"], "completed")
        self.assertIn("breakdown.json", payload["unverifiable"])
        self.assertIn("summary.md", payload["unverifiable"])

    def test_a_rewrite_through_the_hook_is_not_a_correction(self):
        r = Repo(profile="triage")
        r.chain()
        doc = json.loads((r.item_dir / "breakdown.json").read_text())
        doc["epics"][0]["title"] = "Backoff, reworded by a rerun"
        r.artifact("breakdown.json", doc)
        self.assertEqual(r.through_the_hook("breakdown.json").returncode, 0)
        r.run(BRIEF)
        r.through_the_hook("summary.md")
        r.run(OUTCOME)
        out = json.loads((r.item_dir / "outcome.json").read_text())
        self.assertEqual(out["status"], "completed", out.get("reason"))


class TestPerProfileRate(unittest.TestCase):
    def test_a_profile_with_no_terminal_runs_has_no_rate(self):
        """An in-flight item is not a 0% profile: no outcome means no evidence either way."""
        r = Repo(profile="triage")
        r.chain()  # a full trace, but no outcome.json
        out = subprocess.run([sys.executable, str(SCRIPTS / "delivery-report.py"), str(r.dir),
                              "--json"], capture_output=True, text=True)
        payload = json.loads(out.stdout)
        self.assertEqual(payload["items"][0]["status"], "in-flight")
        self.assertEqual(payload["per_profile"], {})

    def test_the_rate_is_grouped_by_profile(self):
        r = Repo(profile="triage")
        r.chain()
        r.run(OUTCOME)
        out = subprocess.run([sys.executable, str(SCRIPTS / "delivery-report.py"), str(r.dir),
                              "--json"], capture_output=True, text=True)
        payload = json.loads(out.stdout)
        self.assertIn("triage", payload["per_profile"])
        self.assertEqual(payload["per_profile"]["triage"]["all"]["completed"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
