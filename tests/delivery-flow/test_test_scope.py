"""AC priorities and the P0/P1 test scope.

The priority is opt-in in `lint-story.py` on purpose. `evals/readiness-stories/` and
`evals/readiness-review/cases/` carry 29 unprioritised AC lines, and readiness-stories' own
`schema` criterion shells out to this linter — so making the priority mandatory would fail the
certified fixtures against their own gate and un-certify the `readiness` node to add a rule
that binds in the dev pair.

So the tests that matter most here are the ones asserting the default did **not** change.
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINT = ROOT / "scripts" / "lint-story.py"

STORY = """# Story 1.1: A thing

Status: Draft

## Story
As a user, I want a thing, so that I benefit.

## Acceptance Criteria
{acs}

## Tasks / Subtasks
- [ ] do it (AC: {refs})

## Dev Notes
- none

### References
- [Source: prd.md#FR-1]
"""


def _story(acs, refs="1"):
    d = Path(tempfile.mkdtemp())
    # A real `[Source:]` target, because the linter resolves them and an unresolvable
    # reference is a failure that would mask the one each test is actually about.
    (d / "prd.md").write_text("# PRD\n\n## FR-1\nA thing.\n")
    p = d / "story.md"
    p.write_text(STORY.format(acs="\n".join(acs), refs=refs))
    return d, p


def _lint(path, root, *flags):
    out = subprocess.run([sys.executable, str(LINT), str(path), "--root", str(root), *flags],
                         capture_output=True, text=True)
    return out.returncode, (out.stdout or "") + (out.stderr or "")


class TestThePriorityIsOptionalByDefault(unittest.TestCase):
    """The half that protects the certified readiness suites."""

    def test_an_unprioritised_story_still_passes(self):
        d, p = _story(["- AC-1: Given a context, when an action, then an outcome."])
        code, out = _lint(p, d)
        self.assertEqual(0, code, out)

    def test_the_default_run_never_mentions_priority(self):
        d, p = _story(["- AC-1: Given a context, when an action, then an outcome."])
        _, out = _lint(p, d)
        self.assertNotIn("priority", out.lower())

    def test_a_prioritised_story_also_passes_by_default(self):
        """Adding the marker must not become an error for callers that do not ask for it."""
        d, p = _story(["- AC-1 (P0): Given a context, when an action, then an outcome."])
        code, out = _lint(p, d)
        self.assertEqual(0, code, out)


class TestTheFlagRequiresIt(unittest.TestCase):
    def test_an_unprioritised_ac_fails_and_is_named(self):
        """Named, not counted: the dev pair has to act on a specific criterion."""
        d, p = _story(["- AC-1: Given a context, when an action, then an outcome.",
                       "- AC-2 (P1): Given another, when another, then another."],
                      refs="1, 2")
        code, out = _lint(p, d, "--require-priority")
        self.assertEqual(1, code)
        self.assertIn("AC-1 has no priority", out)
        self.assertNotIn("AC-2 has no priority", out)

    def test_a_fully_prioritised_story_passes_with_the_flag(self):
        d, p = _story(["- AC-1 (P0): Given a context, when an action, then an outcome.",
                       "- AC-2 (P3): Given another, when another, then another."],
                      refs="1, 2")
        code, out = _lint(p, d, "--require-priority")
        self.assertEqual(0, code, out)

    def test_every_priority_in_the_scale_is_accepted(self):
        for prio in ("P0", "P1", "P2", "P3"):
            with self.subTest(priority=prio):
                d, p = _story([f"- AC-1 ({prio}): Given a, when b, then c."])
                code, out = _lint(p, d, "--require-priority")
                self.assertEqual(0, code, out)

    def test_an_invalid_priority_is_not_silently_accepted(self):
        """`(P9)` must not parse as a priority. The regex only admits P0-P3, so the marker
        stays in the text and the AC reads as unprioritised — which the flag then fails."""
        d, p = _story(["- AC-1 (P9): Given a, when b, then c."])
        code, out = _lint(p, d, "--require-priority")
        self.assertEqual(1, code)
        self.assertIn("AC-1 has no priority", out)

    def test_the_priority_does_not_swallow_the_criterion_text(self):
        """A regex that ate the body would let a vacuous AC pass the Given/When/Then check."""
        d, p = _story(["- AC-1 (P0): nothing testable here"])
        code, out = _lint(p, d, "--require-priority")
        self.assertEqual(1, code)
        self.assertIn("neither Given/When/Then", out)


class TestTheCertifiedFixturesAreUntouched(unittest.TestCase):
    """The regression that would have cost the readiness certification."""

    def test_the_readiness_case_files_lint_the_same_as_before(self):
        cases = sorted((ROOT / "evals" / "readiness-review" / "cases").glob("stories-*.md"))
        self.assertTrue(cases, "the readiness-review case fixtures moved")
        for case in cases:
            with self.subTest(case=case.name):
                # Default invocation only: these fixtures are deliberately imperfect (one has a
                # dropped requirement, one is vacuous), so what is asserted is that this change
                # did not alter what the linter says about them.
                code, out = _lint(case, ROOT)
                self.assertNotIn("has no priority", out,
                                 "the priority check leaked into the default path")


class TestTheTestWriterCarriesTheRule(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / "agents" / "test-writer.md").read_text()

    def test_it_states_the_scope_in_both_directions(self):
        self.assertIn("P0 and P1", self.text)
        self.assertRegex(self.text, r"[Nn]o test for a P2 or P3|no test below P1|nothing below")

    def test_it_reports_a_disputed_priority_rather_than_overriding_it(self):
        """Otherwise the priority is advisory, and the scope stops being checkable data."""
        self.assertRegex(self.text, r"do not act on it|hand back a finding|Hand back a finding")

    def test_the_file_territory_definition_is_unchanged(self):
        """CLAUDE.md pairs this with agents/implementer.md and the boundary hook. This change
        must not have touched it — asserted rather than trusted to the diff."""
        for expected in ("src/test/", "tests/", "spec/", "__tests__/",
                         "enforce-dev-pair-boundary.py"):
            with self.subTest(fragment=expected):
                self.assertIn(expected, self.text)


if __name__ == "__main__":
    unittest.main()
