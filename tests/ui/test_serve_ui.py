"""The workflow UI server: read-only, localhost, and no client content on the wire.

This opens a listening socket, so the properties worth enforcing are the security ones. They
are claims the module docstring makes, and a claim nobody tests is a comment.

The functional half guards against the UI being confidently wrong. Its first version read the
registry's `certified:` field and reported delivery-flow as having **nothing** certified —
because delivery-flow's certified steps do not carry that field at all; their certification is
the evidence clearing the gate. A dashboard that states the opposite of the truth is worse than
no dashboard.
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVE = ROOT / "scripts" / "ui" / "serve-ui.py"
PAGE = ROOT / "scripts" / "ui" / "assets" / "index.html"


def _load():
    spec = importlib.util.spec_from_file_location("serve_ui", SERVE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["serve_ui"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheSecurityPosture(unittest.TestCase):
    """Each of these is a sentence in the docstring. Tested so it stays true."""

    def setUp(self):
        self.m = _load()
        self.src = SERVE.read_text()

    def test_it_binds_to_localhost_only(self):
        self.assertEqual("127.0.0.1", self.m.BIND)

    def test_the_bind_address_is_not_configurable(self):
        """The only reason to make it configurable would be to expose it."""
        self.assertNotIn("--bind", self.src)
        self.assertNotIn("--host", self.src)
        self.assertNotIn("0.0.0.0", self.src.replace("never `0.0.0.0`", ""))

    def test_there_is_no_write_handler(self):
        for verb in ("do_POST", "do_PUT", "do_DELETE", "do_PATCH"):
            with self.subTest(verb=verb):
                self.assertNotIn(verb, self.src)

    def test_no_request_path_reaches_the_filesystem(self):
        """`self.path` is read to pick a route and nothing else — there is no static route, so
        a request cannot name a file and there is no traversal surface.

        Asserted by the constructions that would create one. The earlier version of this test
        asserted `self.path` never appeared at all, which is both false and not the property
        that matters: reading the route is fine, turning it into a path is not.
        """
        handler = self.src.split("class Handler")[1].split("def main")[0]
        for dangerous in ("Path(self.path", "Path(route", "open(self.path", "open(route",
                          "/ self.path", "/ route", "+ self.path", "+ route",
                          "join(self.path", "join(route"):
            with self.subTest(construction=dangerous):
                self.assertNotIn(dangerous, handler)

    def test_the_only_file_it_serves_is_resolved_at_import(self):
        """PAGE is a module constant, so the served file cannot depend on a request."""
        self.assertIn("PAGE = HERE", self.src)
        self.assertIn("PAGE.read_bytes()", self.src)


class TestItServesNoClientContent(unittest.TestCase):
    """The delivery repos point at a client's tracker (`tracker.external: true`), and this
    plugin's rule is that client content stays out of the public repo. So the UI shows
    structure and statistics, and ticket prose never reaches the socket at all."""

    PROSE_FIELDS = ("body", "summary", "rationale", "description", "post", "pr_body")

    def setUp(self):
        self.m = _load()

    def test_the_structure_payload_carries_no_prose_fields(self):
        payload = json.dumps(self.m.structure())
        for field in self.PROSE_FIELDS:
            with self.subTest(field=field):
                self.assertNotIn(f'"{field}"', payload)

    def test_the_structure_payload_does_not_read_item_json(self):
        """Structure comes from descriptors and registries only."""
        self.assertNotIn("item.json", SERVE.read_text().split("def structure")[1][:2000])

    def test_runs_without_a_repo_reports_a_reason_not_zero(self):
        """"No data" and "I could not read the data" are different answers — this project has
        already shipped one number that conflated them."""
        out = self.m.runs([])
        self.assertFalse(out["available"])
        self.assertIn("reason", out)


class TestTheGateIsTheSourceOfTruth(unittest.TestCase):
    """Not the registry's `certified:` flag, which delivery-flow's certified steps omit."""

    @classmethod
    def setUpClass(cls):
        cls.m = _load()
        cls.struct = cls.m.structure()

    def test_both_workflows_are_present(self):
        self.assertEqual({"delivery-flow", "sdlc"}, set(self.struct))

    def test_delivery_flows_certified_steps_are_reported_certified(self):
        """The regression that made the first version useless."""
        states = {s["step"]: s["gate"] for s in self.struct["delivery-flow"]["steps"]}
        for step in ("triage", "breakdown", "challenge-breakdown", "pr-description"):
            with self.subTest(step=step):
                self.assertEqual("certified", states.get(step))

    def test_review_reports_uncertified(self):
        states = {s["step"]: s["gate"] for s in self.struct["delivery-flow"]["steps"]}
        self.assertEqual("uncertified", states.get("review"))

    def test_sdlc_reports_only_readiness_certified(self):
        states = {s["step"]: s["gate"] for s in self.struct["sdlc"]["steps"]}
        self.assertEqual("certified", states.get("readiness"))
        for seg in ("analysis", "planning", "solutioning", "implementation", "verification"):
            with self.subTest(segment=seg):
                self.assertEqual("uncertified", states.get(seg))

    def test_scripts_and_adapters_are_not_registered_rather_than_uncertified(self):
        """Collapsing those two would report every deterministic step as a failure."""
        states = {s["step"]: s["gate"] for s in self.struct["delivery-flow"]["steps"]}
        for step in ("intake", "brief", "report", "open-pr"):
            with self.subTest(step=step):
                self.assertEqual("not-registered", states.get(step))

    def test_it_agrees_with_check_certification_itself(self):
        """The whole claim: the UI and the gate cannot disagree about who is certified."""
        import subprocess
        gate = ROOT / "scripts" / "delivery-flow" / "check-certification.py"
        for wf in self.struct.values():
            reg = None
            for s in wf["steps"]:
                if s["gate"] == "not-registered":
                    continue
                reg = ("skills/delivery-flow/steps.yaml" if wf["workflow"] == "delivery-flow"
                       else "skills/sdlc-orchestration/steps.yaml")
                out = subprocess.run([sys.executable, "-I", str(gate), s["step"],
                                      "--registry", reg], cwd=str(ROOT),
                                     capture_output=True, text=True)
                with self.subTest(step=s["step"]):
                    expected = "certified" if out.returncode == 0 else "uncertified"
                    self.assertEqual(expected, s["gate"])
            self.assertIsNotNone(reg, "no registered steps found at all")

    def test_every_profile_step_exists_in_the_routing_table(self):
        """Otherwise the diagram draws a node the table does not have, which the UI renders
        as an explicit inconsistency rather than hiding."""
        for wf in self.struct.values():
            table = {s["step"] for s in wf["steps"]}
            for p in wf["profiles"]:
                for step in p["steps"]:
                    with self.subTest(workflow=wf["workflow"], profile=p["profile"], step=step):
                        self.assertIn(step, table)

    def test_profiles_are_loaded(self):
        """`load_profiles` takes a path; passing text returned [] and every workflow showed
        as having no profiles."""
        for wf in self.struct.values():
            with self.subTest(workflow=wf["workflow"]):
                self.assertTrue(wf["profiles"])


class TestThePage(unittest.TestCase):
    def test_the_page_asset_exists(self):
        self.assertTrue(PAGE.exists())

    def test_status_is_never_colour_alone(self):
        """Each badge pairs a glyph and a word, per the accessibility rule."""
        text = PAGE.read_text()
        self.assertIn("glyph", text)
        for word in ("certified", "uncertified", "no prompt"):
            with self.subTest(word=word):
                self.assertIn(word, text)

    def test_the_one_chart_has_a_table_view(self):
        """A contrast WARN on the palette obliges visible labels or a table; it ships both."""
        text = PAGE.read_text()
        self.assertIn("The same numbers as a table", text)
        self.assertIn("bar-fill", text)

    def test_dark_mode_is_declared_under_both_scopes(self):
        text = PAGE.read_text()
        self.assertIn("prefers-color-scheme: dark", text)
        self.assertIn('[data-theme="dark"]', text)


if __name__ == "__main__":
    unittest.main()


class TestItRunsAsAScript(unittest.TestCase):
    """The gap that let a broken import ship.

    Every other test here loads the module with importlib, in a process where
    `scripts/workflow` is already on `sys.path` — so they all passed while
    `python3 serve-ui.py` died on `ModuleNotFoundError: descriptor`. A script that cannot run
    as a script is only caught by running it.
    """

    def test_help_exits_cleanly(self):
        import subprocess
        out = subprocess.run([sys.executable, str(SERVE), "--help"],
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertIn("127.0.0.1", out.stdout)

    def test_a_missing_repo_is_refused_before_binding(self):
        """Exit 2 on bad input, rather than opening a socket and then failing."""
        import subprocess
        out = subprocess.run([sys.executable, str(SERVE), "--repo", "/nonexistent/repo",
                              "--no-browser"], capture_output=True, text=True, timeout=60)
        self.assertEqual(2, out.returncode)
        self.assertIn("no such repo", out.stdout + out.stderr)

    def test_it_actually_serves_the_page_and_the_api(self):
        """End to end against a real socket, then shut down."""
        import socket, subprocess, time, urllib.request
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        proc = subprocess.Popen([sys.executable, str(SERVE), "--port", str(port),
                                 "--no-browser"], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        try:
            body = None
            for _ in range(40):
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                        body = r.read().decode()
                    break
                except Exception:
                    time.sleep(0.25)
            self.assertIsNotNone(body, "the server never answered")
            self.assertIn("<title>Workflow", body)
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/structure",
                                        timeout=10) as r:
                doc = json.loads(r.read().decode())
            self.assertEqual({"delivery-flow", "sdlc"}, set(doc))
            # An unknown route is a flat 404 with no filesystem lookup.
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/nope", timeout=5)
                self.fail("an unknown route should 404")
            except urllib.error.HTTPError as e:
                self.assertEqual(404, e.code)
        finally:
            proc.terminate()
            proc.wait(timeout=10)
