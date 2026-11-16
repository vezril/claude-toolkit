#!/usr/bin/env python3
"""Tests for punch-outs: when they fire, how they are decided, and what they block.

Signing uses a throwaway ed25519 key, so the machinery is tested without a hardware key.
In production the configured key requires a human's presence on every use, which is the
property an agent cannot satisfy.

Run: python3 tests/delivery-flow/test_punch_outs.py
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
CHECK = SCRIPTS / "check-punch-out.py"
DECIDE = SCRIPTS / "decide.py"
HOOK = ROOT / "hooks" / "enforce-punch-outs.py"
sys.path.insert(0, str(SCRIPTS))

import common  # noqa: E402

TRIAGE = {"item": "DEM-12", "type": "feature", "path": "standard", "domains": ["backend"],
          "summary": "s", "rationale": "r", "handoff": False, "handoff_reason": None,
          "architecture_change": False, "breaking_change": False}


class Repo:
    def __init__(self, item="DEM-12", external=False, budget=None, deploy=True):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / ".git").mkdir()
        self.item = item
        self.item_dir = self.dir / "delivery" / item
        self.item_dir.mkdir(parents=True)
        self.key = self.dir / "signing_key"
        subprocess.run(["ssh-keygen", "-t", "ed25519", "-N", "", "-C", "t", "-f", str(self.key)],
                       capture_output=True, check=True)
        self.signers = self.dir / "allowed_signers"
        self.signers.write_text(f"calvin {self.key.with_suffix('.pub').read_text().strip()}\n")
        cfg = ["tracker:", "  kind: local-markdown", f"  external: {str(external).lower()}",
               "decisions:", f"  allowed_signers: {self.signers}", "  signer: calvin"]
        if budget is not None:
            cfg += ["punch_out:", f"  cost_budget_usd: {budget}", "  retry_limit: 3"]
        if deploy:
            cfg += ["deploy:", "  auto_roll:", "    routine_bumps: true"]
        (self.dir / ".delivery-flow.yaml").write_text("\n".join(cfg) + "\n")

    def triage(self, **kw):
        (self.item_dir / "triage.json").write_text(json.dumps({**TRIAGE, "item": self.item, **kw}))

    def current_step(self, step="triage"):
        (self.item_dir / ".current-step").write_text(json.dumps({"step": step, "item": self.item}))

    def trace(self, **rec):
        with (self.item_dir / "trace.jsonl").open("a") as f:
            f.write(json.dumps({"ts": "2026-10-21T00:00:00+00:00", "item": self.item, **rec}) + "\n")

    def check(self, step="triage"):
        r = subprocess.run([sys.executable, str(CHECK), self.item, "--step", step,
                            "--repo", str(self.dir), "--json"], capture_output=True, text=True)
        return r.returncode, json.loads(r.stdout)

    def decide(self, subject, choice="proceed"):
        return subprocess.run(
            [sys.executable, str(DECIDE), self.item, subject, "--choose", choice, "--yes",
             "--repo", str(self.dir), "--key", str(self.key), "--decider", "calvin"],
            capture_output=True, text=True)

    def hook(self, tool, tool_input):
        r = subprocess.run([sys.executable, str(HOOK)], capture_output=True, text=True,
                           input=json.dumps({"hook_event_name": "PreToolUse", "tool_name": tool,
                                             "cwd": str(self.dir), "tool_input": tool_input}))
        out = {}
        if r.stdout.strip():
            try:
                out = json.loads(r.stdout)["hookSpecificOutput"]
            except (json.JSONDecodeError, KeyError):
                out = {}
        return out.get("permissionDecision"), out.get("permissionDecisionReason", "")

    def bash(self, cmd):
        return self.hook("Bash", {"command": cmd})


class TestTriggers(unittest.TestCase):
    def test_no_triggers_no_punch_out(self):
        r = Repo(); r.triage()
        code, out = r.check()
        self.assertEqual(code, 0)
        self.assertEqual(out["written"], [])

    def test_handoff_fires_scope(self):
        r = Repo(); r.triage(handoff=True, handoff_reason="a whole new service")
        code, out = r.check()
        self.assertEqual(code, 1)
        self.assertEqual(out["triggered"][0]["trigger"], "scope")
        text = (r.item_dir / "punch-out-1.md").read_text()
        self.assertIn("a whole new service", text)
        self.assertIn("decide.py", text)

    def test_architecture_and_breaking_fire_separately(self):
        r = Repo(); r.triage(architecture_change=True, breaking_change=True)
        _, out = r.check()
        self.assertEqual({t["trigger"] for t in out["triggered"]}, {"architecture", "breaking"})
        self.assertEqual(len(out["written"]), 2)

    def test_budget_fires_on_recorded_cost(self):
        r = Repo(budget=0.05); r.triage()
        r.trace(step="breakdown", api_equivalent_cost_usd=0.04)
        self.assertEqual(r.check()[0], 0)
        r.trace(step="implementation", api_equivalent_cost_usd=0.03)
        code, out = r.check()
        self.assertEqual(code, 1)
        self.assertEqual(out["triggered"][0]["trigger"], "budget")

    def test_retry_limit_fires(self):
        r = Repo(budget=99); r.triage()
        for _ in range(3):
            r.trace(artifact="breakdown.json", edge={"name": "schema", "exit": 1, "summary": "bad"})
        _, out = r.check()
        self.assertIn("retry-limit", {t["trigger"] for t in out["triggered"]})

    def test_refuted_twice_fires(self):
        r = Repo(); r.triage()
        (r.item_dir / "challenge-breakdown.json").write_text(json.dumps(
            {"item": "DEM-12", "target": "breakdown", "verdict": "REFUTED", "attacks": [], "findings": []}))
        r.trace(step="breakdown", verdict="REFUTED")   # first challenge run
        r.trace(step="breakdown", verdict="REFUTED")   # and the rerun, refuted again
        _, out = r.check()
        self.assertIn("refuted-twice", {t["trigger"] for t in out["triggered"]})

    def test_external_post_fires_only_at_the_post_step(self):
        r = Repo(external=True); r.triage()
        self.assertEqual(r.check("breakdown")[0], 0)
        self.assertEqual(r.check("post-back")[0], 1)

    def test_same_trigger_does_not_stack(self):
        r = Repo(); r.triage(handoff=True)
        r.check(); code, out = r.check()
        self.assertEqual(out["written"], [])
        self.assertEqual(len(list(r.item_dir.glob("punch-out-*.md"))), 1)


class TestDeciding(unittest.TestCase):
    def test_decision_is_signed_and_verifies(self):
        r = Repo(); r.triage(handoff=True); r.check()
        res = r.decide("punch-out-1")
        self.assertEqual(res.returncode, 0, res.stderr)
        d = json.loads((r.item_dir / "decisions" / "punch-out-1.json").read_text())
        self.assertTrue(d["signature"].startswith("-----BEGIN SSH SIGNATURE-----"))
        self.assertEqual(d["choice"], "proceed")

    def test_decide_refuses_without_the_punch_out(self):
        r = Repo()
        res = r.decide("punch-out-7")
        self.assertEqual(res.returncode, 1)
        self.assertIn("no such punch-out", res.stderr)

    def test_signature_does_not_verify_with_a_key_outside_allowed_signers(self):
        r = Repo(); r.triage(handoff=True); r.check()
        other = r.dir / "other_key"
        subprocess.run(["ssh-keygen", "-t", "ed25519", "-N", "", "-C", "x", "-f", str(other)],
                       capture_output=True, check=True)
        res = subprocess.run([sys.executable, str(DECIDE), r.item, "punch-out-1", "--choose", "proceed",
                              "--yes", "--repo", str(r.dir), "--key", str(other), "--decider", "calvin"],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("does not verify", res.stderr)
        self.assertFalse((r.item_dir / "decisions").exists())


class TestSigningEnv(unittest.TestCase):
    """The key path and the agent socket are read, not remembered.

    `decide.py` defaulted `--key` to `~/.ssh/id_ed25519_sk`, a path that has never existed on
    this machine, while the real settings sat in `~/.config/delivery-flow/signing.env` that
    nothing read. So signing worked only in a shell where that file had been sourced by hand,
    and failed everywhere else with "No such file or directory" naming a key the user does not
    own — pointing at the wrong problem every time it came up, which was twice.
    """

    def env_file(self, **kw):
        d = Path(tempfile.mkdtemp())
        p = d / "signing.env"
        p.write_text("# a comment\n\n" + "".join(f"{k}={v}\n" for k, v in kw.items()))
        return p

    def test_the_file_is_read(self):
        p = self.env_file(DELIVERY_FLOW_SIGNING_KEY="/k.pub", DELIVERY_FLOW_SIGNER="calvin")
        got = common.load_signing_env(p)
        self.assertEqual("/k.pub", got["DELIVERY_FLOW_SIGNING_KEY"])
        self.assertEqual("calvin", got["DELIVERY_FLOW_SIGNER"])

    def test_comments_and_blank_lines_are_ignored(self):
        p = self.env_file(DELIVERY_FLOW_SIGNER="calvin")
        self.assertEqual({"DELIVERY_FLOW_SIGNER": "calvin"}, common.load_signing_env(p))

    def test_an_absent_file_is_not_an_error(self):
        self.assertEqual({}, common.load_signing_env(Path("/nonexistent/signing.env")))

    def test_an_explicit_delivery_flow_var_wins(self):
        """Nothing but a person sets these, so an explicit one is a deliberate override."""
        p = self.env_file(DELIVERY_FLOW_SIGNING_KEY="/from-file.pub")
        old = os.environ.get("DELIVERY_FLOW_SIGNING_KEY")
        os.environ["DELIVERY_FLOW_SIGNING_KEY"] = "/from-env.pub"
        try:
            self.assertNotIn("DELIVERY_FLOW_SIGNING_KEY", common.load_signing_env(p))
        finally:
            os.environ.pop("DELIVERY_FLOW_SIGNING_KEY", None)
            if old is not None:
                os.environ["DELIVERY_FLOW_SIGNING_KEY"] = old

    def test_ssh_auth_sock_from_the_file_overrides_the_environment(self):
        """The asymmetry, and the one that makes this work at all.

        macOS always has `SSH_AUTH_SOCK` pointing at its own launchd agent, so a plain
        "already set wins" rule means the file's value never applies and signing quietly
        reaches an agent that does not hold the key. Naming it in the file is the deliberate
        choice; the ambient value is just the default.
        """
        p = self.env_file(SSH_AUTH_SOCK="/secretive/socket.ssh")
        old = os.environ.get("SSH_AUTH_SOCK")
        os.environ["SSH_AUTH_SOCK"] = "/var/run/launchd/Listeners"
        try:
            self.assertEqual("/secretive/socket.ssh",
                             common.load_signing_env(p)["SSH_AUTH_SOCK"])
        finally:
            os.environ.pop("SSH_AUTH_SOCK", None)
            if old is not None:
                os.environ["SSH_AUTH_SOCK"] = old

    def test_decide_refuses_with_no_key_configured_and_says_what_to_set(self):
        """Not "no such file": a path the user never owned is the wrong thing to name."""
        r = Repo(); r.triage(handoff=True); r.check()
        env = {k: v for k, v in os.environ.items() if k != "DELIVERY_FLOW_SIGNING_KEY"}
        env["DELIVERY_FLOW_SIGNING_ENV"] = "/nonexistent/signing.env"
        res = subprocess.run([sys.executable, str(DECIDE), r.item, "punch-out-1",
                              "--choose", "proceed", "--yes", "--repo", str(r.dir)],
                             capture_output=True, text=True, env=env)
        self.assertEqual(1, res.returncode)
        self.assertIn("no signing key configured", res.stderr)
        self.assertIn("DELIVERY_FLOW_SIGNING_KEY", res.stderr)
        self.assertNotIn("id_ed25519_sk", res.stderr)
        self.assertFalse((r.item_dir / "decisions").exists())

    def test_the_env_file_supplies_the_key(self):
        """End to end: no --key, no exported vars, and the decision still signs."""
        r = Repo(); r.triage(handoff=True); r.check()
        p = self.env_file(DELIVERY_FLOW_SIGNING_KEY=str(r.key),
                          DELIVERY_FLOW_SIGNER="calvin")
        env = {k: v for k, v in os.environ.items()
               if k not in ("DELIVERY_FLOW_SIGNING_KEY", "DELIVERY_FLOW_SIGNER")}
        env["DELIVERY_FLOW_SIGNING_ENV"] = str(p)
        res = subprocess.run([sys.executable, str(DECIDE), r.item, "punch-out-1",
                              "--choose", "proceed", "--yes", "--repo", str(r.dir)],
                             capture_output=True, text=True, env=env)
        self.assertEqual(0, res.returncode, res.stderr)
        d = json.loads((r.item_dir / "decisions" / "punch-out-1.json").read_text())
        self.assertTrue(d["signature"].startswith("-----BEGIN SSH SIGNATURE-----"))


class TestHookBlocks(unittest.TestCase):
    def test_agent_cannot_write_a_decision(self):
        r = Repo()
        d, why = r.hook("Write", {"file_path": str(r.item_dir / "decisions" / "punch-out-1.json")})
        self.assertEqual(d, "deny")
        self.assertIn("human", why)

    def test_agent_cannot_shell_a_decision(self):
        r = Repo()
        self.assertEqual(r.bash(f"echo '{{}}' > {r.item_dir}/decisions/punch-out-1.json")[0], "deny")
        self.assertEqual(r.bash(f"python3 decide.py {r.item} punch-out-1 --choose proceed")[0], "deny")
        self.assertEqual(r.bash(f"rm {r.item_dir}/punch-out-1.md")[0], "deny")

    def test_agent_cannot_edit_a_punch_out(self):
        r = Repo()
        self.assertEqual(r.hook("Edit", {"file_path": str(r.item_dir / "punch-out-1.md")})[0], "deny")

    def test_merge_is_always_denied(self):
        r = Repo(); r.triage(); r.current_step()
        self.assertEqual(r.bash("gh pr merge 42 --merge")[0], "deny")
        self.assertEqual(r.bash("git push origin main")[0], "deny")

    def test_open_punch_out_blocks_pr_and_delegation(self):
        r = Repo(); r.triage(handoff=True); r.check(); r.current_step()
        d, why = r.bash("gh pr create --fill")
        self.assertEqual(d, "deny")
        self.assertIn("waiting on a human", why)
        self.assertEqual(r.hook("Task", {"subagent_type": "implementer"})[0], "deny")

    def test_proceed_decision_releases_the_flow(self):
        r = Repo(); r.triage(handoff=True); r.check(); r.current_step()
        self.assertEqual(r.decide("punch-out-1").returncode, 0)
        self.assertIsNone(r.bash("gh pr create --fill")[0])

    def test_editing_a_punch_out_after_deciding_blocks_again(self):
        r = Repo(); r.triage(handoff=True); r.check(); r.current_step()
        r.decide("punch-out-1")
        (r.item_dir / "punch-out-1.md").write_text("# Punch-out 1: scope\n\nsomething else\n")
        d, why = r.bash("gh pr create --fill")
        self.assertEqual(d, "deny")
        self.assertIn("edited", why)

    def test_deploy_needs_a_decision(self):
        r = Repo(); r.triage(architecture_change=True); r.current_step()
        d, why = r.bash("helm upgrade apollo ./charts/apollo")
        self.assertEqual(d, "deny")
        self.assertIn("deploy", why)

    def test_routine_bump_auto_rolls_and_is_traced(self):
        r = Repo(); r.triage(); r.current_step()
        self.assertIsNone(r.bash("helm upgrade apollo ./charts/apollo")[0])
        recs = [json.loads(l) for l in (r.item_dir / "trace.jsonl").read_text().splitlines()]
        self.assertTrue(any(x.get("policy") == "auto_roll" for x in recs))

    def test_inert_outside_a_delivery_repo(self):
        d = Path(tempfile.mkdtemp()); (d / ".git").mkdir()
        res = subprocess.run([sys.executable, str(HOOK)], capture_output=True, text=True,
                             input=json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                               "cwd": str(d), "tool_input": {"command": "gh pr merge 1"}}))
        self.assertEqual(res.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
