#!/usr/bin/env python3
"""The dispatch boundary: does the edge hook hand each artifact to a checker *at all*?

Every other edge test asks whether a checker is correct. None of them asks whether the
checker is ever called. That gap is where today's defects lived:

- A glob-keyed artifact whose declared `artifact` did not match the name its producer wrote:
  `schema_for` returned None, `check_artifact` reported "not mine", and `main`'s
  `if not ran: continue` dropped it. The schema and both validators were correct and covered
  by tests; nothing ever handed them the file. (That producer has since been retired, but the
  shape is why this file exists.)
- The punch-out breaking trigger matched a correct contract-path list against the whole
  branch diff instead of the item's own (defect 12).
- The architecture trigger was fed the guarded node's own `rationale` (defect 8).

The shape is the same every time, and it is silent in the safe-looking direction: an inert
gate reports success, so it is indistinguishable from a passing one in the trace, the outcome
and the report. "We fixed N defects" misframes it — the other defects were visible once you
looked, and this class is not visible even then.

So these tests assert only that a record EXISTS for each artifact the routing table names.
Not that it passed. A gate that ran and failed is working; a gate that never ran is the bug.

Run: python3 tests/delivery-flow/test_edge_dispatch.py
Standard library only, like the code under test.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
HOOK = ROOT / "hooks" / "check-edge.py"
sys.path.insert(0, str(SCRIPTS))
import common  # noqa: E402


def _flow_status():
    """`flow-status.py` is not importable by name (the hyphen), so load it by path."""
    spec = importlib.util.spec_from_file_location("flow_status", SCRIPTS / "flow-status.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


STEPS = _flow_status().STEPS
SCHEMAS = common.load_schemas()

# The axis is the UNION of the routing table and `schemas/`, because each alone has a blind
# spot and they are different blind spots:
#
#   - `schemas/` alone cannot see an artifact with no schema. There is nothing to iterate.
#     That hides the six routed-but-ungoverned artifacts below.
#   - `STEPS` alone cannot see a schema'd artifact that is not a routed step. An artifact can
#     be produced and consumed off the step table entirely, and iterating STEPS would miss it
#     — which is exactly how the bug that prompted this file escaped.
#
# Hence both. `(artifact, origin)` pairs; the origin only sharpens failure messages.
ARTIFACTS = sorted(
    {(row[0], f"step {row[1]}") for row in STEPS}
    | {(s["artifact"], f"schema {Path(s['_path']).name}") for s in SCHEMAS.values()
       if s["artifact"] != "*.sentinel.json"}  # a sentinel is checked with its artifact
)

# Artifacts the hook governs: a schema resolves, or a prose checker is registered for it.
# Read from the hook's own table rather than restated, so registering a checker there is
# enough to move an artifact out of the "ungoverned" list without editing this file.
TERMINAL_PROSE = set(
    json.loads(
        subprocess.run(
            [sys.executable, "-c",
             "import json,sys;sys.path.insert(0,%r);"
             "import importlib.util as u;"
             "s=u.spec_from_file_location('ce',%r);m=u.module_from_spec(s);s.loader.exec_module(m);"
             "print(json.dumps(sorted(m.TERMINAL_PROSE)))" % (str(SCRIPTS), str(HOOK))],
            capture_output=True, text=True, check=True).stdout
    )
)


def governed(artifact: str) -> bool:
    return (common.schema_for(artifact.replace("*", "X"), SCHEMAS) is not None
            or artifact in TERMINAL_PROSE)


class Fixture:
    """A throwaway delivery-flow repo with one item."""

    def __init__(self, item="DEM-12"):
        self.dir = Path(tempfile.mkdtemp())
        self.item = item
        (self.dir / ".git").mkdir()
        (self.dir / ".delivery-flow.yaml").write_text("binding: test\n")
        self.item_dir = self.dir / "delivery" / item
        self.item_dir.mkdir(parents=True)

    def write(self, name, text):
        p = self.item_dir / name
        p.write_text(text)
        return p

    def hook(self, name):
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Write", "cwd": str(self.dir),
                   "session_id": "s1", "tool_input": {"file_path": str(self.item_dir / name)}}
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def trace(self):
        p = self.item_dir / "trace.jsonl"
        return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


class TestEveryRoutedArtifactReachesAChecker(unittest.TestCase):
    """Write each routed artifact under its real name; a record must appear for it.

    Deliberately written as garbage content. A well-formed artifact could pass for the wrong
    reason — an inert edge and a satisfied edge both say nothing. Garbage can only produce a
    record if something actually looked at it.
    """

    def test_a_governed_artifact_is_always_recorded(self):
        checked = 0
        for artifact, origin in ARTIFACTS:
            if not governed(artifact):
                continue
            with self.subTest(artifact=artifact, origin=origin):
                f = Fixture()
                name = artifact.replace("*", "E1-S1")
                f.write(name, "{ this is not valid json" if name.endswith(".json") else "x")
                f.hook(name)
                recorded = [r for r in f.trace() if r.get("artifact") == name]
                self.assertTrue(
                    recorded,
                    f"{name} ({origin}) resolves to a checker but produced no trace record "
                    f"— the dispatcher never handed it over")
            checked += 1
        # Guards the guard: a bug that emptied ARTIFACTS or `governed()` would make every
        # subTest vacuous and this test pass while covering nothing — the same inert-check
        # failure it exists to catch.
        self.assertGreater(checked, 5, "the parametrisation covered almost nothing")


class TestDeclaredNamesMatchProducedNames(unittest.TestCase):
    """A schema's declared `artifact` must match the name its producer actually writes.

    This is the blind spot that let the original bug through, and it is a subtle one: the
    parametrised test above iterates *declared* names, so it is satisfied by whatever the
    schema claims. A schema declaring a fixed `artifact` while its producer writes a varying
    name keeps that test green — it dutifully writes a file by the declared name, which
    resolves — while every file the producer actually wrote goes unchecked. **A test keyed to
    the declaration cannot detect a declaration that is wrong.**

    So for any artifact whose name is not a literal, the authority has to be the producer, and
    the assertion has to use the producer's own name-building code rather than the registry's.
    The sentinel is the only such artifact left; add a case here for the next one.
    """

    def test_a_sentinel_filename_resolves_to_the_sentinel_schema(self):
        """Built the way `write-sentinel.py` builds it, not the way the schema declares it."""
        name = "breakdown.json" + common.SENTINEL_SUFFIX
        schema = common.schema_for(name, SCHEMAS)
        self.assertIsNotNone(schema, f"nothing claims {name}")
        self.assertEqual(schema["artifact"], "*.sentinel.json")


class TestTheUngovernedArtifactsAreKnown(unittest.TestCase):
    """The artifacts no checker covers, pinned so the set cannot grow unnoticed.

    `changed_artifacts` drops these with a bare `continue` — no record, no "skipped", nothing.
    The flow's rule "never advance past a failed edge" is then satisfied trivially, because an
    absent edge cannot fail, and `flow-status.py` and `references/trace.md` surface the gap
    nowhere. Six of the eight are `full`-profile-only and past `propose`, so this is plausibly
    a profile whose edges were never built rather than six broken ones.

    Either reading makes the *current* state the bad one: an undeclared absence looks exactly
    like a working edge. The precedent for the fix is already here — certification does not
    silently skip an uncertified step, it records `certified: false` and excludes the run from
    the certified-only rate. The edge has no equivalent, and a recorded
    `edge: {name: "none", reason: "no schema"}` would make the gap countable instead of
    invisible. That is a smaller change than writing eight schemas.

    This test does not assert the gap is acceptable. It asserts it is *known*, so that adding
    a step without an edge is a deliberate act with a failing test attached.
    """

    EXPECTED_UNGOVERNED = {
        "implementation.json",            # step implementation (sdlc)
        "verify.json",                    # step verify (build)
        "challenge-implementation.json",  # step challenge-implementation (node)
        "pr-opened.json",                 # step open-pr (adapter)
        "posted.json",                    # step post-back (adapter)
        "vault-updated.json",             # step vault-update (node)
        "pr.md",                          # step pr-description — prose, no checker registered
        "post.md",                        # step post-summary — prose, no checker registered
    }

    def test_the_ungoverned_set_has_not_grown(self):
        actual = {a for a, _ in ARTIFACTS if not governed(a)}
        new = actual - self.EXPECTED_UNGOVERNED
        self.assertFalse(new, f"new routed artifacts with no edge checker: {sorted(new)}. "
                              f"Give each a schema, register a prose checker, or declare the "
                              f"absence here on purpose.")

    def test_nothing_claims_an_edge_it_does_not_have(self):
        """The inverse: anything listed as ungoverned must really be ungoverned.

        Without this, the pin above rots the moment someone writes one of the eight schemas —
        the artifact becomes governed, the set shrinks, and the stale entry hides the next
        real gap.
        """
        fixed = {a for a in self.EXPECTED_UNGOVERNED if governed(a)}
        self.assertFalse(fixed, f"these now have a checker and must be removed from "
                                f"EXPECTED_UNGOVERNED: {sorted(fixed)}")

    def test_an_ungoverned_artifact_is_silently_skipped(self):
        """Characterising the current behaviour, so a future fix has something to change.

        If a recorded skip is implemented, this test fails and should be rewritten to assert
        the record instead. That is the intended outcome, not a regression.
        """
        f = Fixture()
        f.write("verify.json", "{ not valid json either")
        r = f.hook("verify.json")
        self.assertEqual(r.returncode, 0, "an ungoverned artifact must not block the flow")
        self.assertEqual([t for t in f.trace() if t.get("artifact") == "verify.json"], [],
                         "verify.json now produces a record — good; update this test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
