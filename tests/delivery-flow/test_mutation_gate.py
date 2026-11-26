"""The mutation gate: break the diff's own production lines, see if its tests notice.

The gate exists because of a review comment on a client PR — *"making it unconditional still
passes"* — so the load-bearing test here is the end-to-end pair: the same production change,
once with a test that cannot reach the branch and once with a test that can. The first must
report survivors and the second must report none. A gate that only ever says "survived" would
be as useless as one that only ever says "killed", and only running both directions tells them
apart.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "delivery-flow" / "mutation-gate.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


mg = load(SCRIPT, "mutation_gate")

PRODUCTION = '''\
class Rows:
    """A docstring with a == b in it, which must never be mutated."""

    def __init__(self):
        self.rows = {}
        self.owner = {}

    def record_graph(self, run_id, graph_id):
        if run_id not in self.rows:
            raise KeyError("re-claimed")
        self.rows[run_id] = graph_id
        return graph_id
'''

COMPLETE = '''
    def complete(self, run_id, owner):
        if self.owner.get(run_id) == owner:
            self.rows[run_id] = "complete"
            return True
        return False
'''

TEST_HEAD = '''\
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.pipeline import Rows  # noqa: E402


def test_record_graph_on_a_live_row():
    r = Rows()
    r.rows["a"] = None
    assert r.record_graph("a", "g1") == "g1"
'''

# The defect: the row is re-claimed BEFORE the run, so `record_graph` raises and the
# conditional write is never reached. The test passes, and it passes just as well when the
# condition is deleted.
INERT_TEST = '''

def test_complete_is_refused_for_a_reclaimed_row():
    r = Rows()
    r.rows["a"] = None
    r.owner["a"] = "me"
    try:
        r.record_graph("zz", "g1")
    except KeyError:
        pass
'''

REAL_TEST = '''

def test_complete_writes_for_the_owner_and_is_refused_otherwise():
    r = Rows()
    r.rows["a"] = None
    r.owner["a"] = "me"
    assert r.complete("a", "me") is True
    assert r.rows["a"] == "complete"
    r.owner["a"] = "someone-else"
    assert r.complete("a", "me") is False
'''


def git(repo: Path, *args):
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert out.returncode == 0, f"git {args}: {out.stderr}"
    return out.stdout


def build_repo(tmp: Path, extra_test: str) -> Path:
    """A two-commit repo: `main`, then a branch adding a conditional write and a test."""
    repo = tmp / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / ".gitignore").write_text("__pycache__/\n")
    (repo / ".delivery-flow.yaml").write_text(textwrap.dedent(f"""\
        tracker:
          kind: local-markdown
        forge:
          kind: github-pr
          base: main
        test_command: {sys.executable} -m pytest -q
        artifacts:
          root: {tmp / 'runs'}
        """))
    (tmp / "runs").mkdir()
    (repo / "src" / "pipeline.py").write_text(PRODUCTION)
    (repo / "tests" / "test_recovery.py").write_text(TEST_HEAD)
    git(repo, "init", "-q", "-b", "main", ".")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")
    git(repo, "checkout", "-q", "-b", "feat/complete")
    (repo / "src" / "pipeline.py").write_text(PRODUCTION + COMPLETE)
    (repo / "tests" / "test_recovery.py").write_text(TEST_HEAD + extra_test)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "the conditional complete write, with a test")
    return repo


def run_gate(repo: Path, *extra):
    out = subprocess.run([sys.executable, "-I", str(SCRIPT), "--repo", str(repo),
                          "--base", "main", "--json", *extra],
                         capture_output=True, text=True,
                         env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return out, json.loads(out.stdout)


class TestItTellsAnInertTestFromARealOne(unittest.TestCase):
    """The whole point. Same production change, two tests, opposite verdicts."""

    def test_an_unreachable_branch_leaves_survivors(self):
        with tempfile.TemporaryDirectory() as t:
            repo = build_repo(Path(t), INERT_TEST)
            out, doc = run_gate(repo)
            self.assertTrue(doc["ran"], doc)
            self.assertEqual(1, out.returncode, "survivors must exit 1")
            self.assertTrue(doc["survived"], "the test cannot reach the branch")
            ops = {s["operator"] for s in doc["survived"]}
            self.assertIn("condition-always-true", ops,
                          "the mutant the review comment named must be among them")

    def test_a_test_that_reaches_the_branch_kills_them(self):
        with tempfile.TemporaryDirectory() as t:
            repo = build_repo(Path(t), REAL_TEST)
            out, doc = run_gate(repo)
            self.assertTrue(doc["ran"], doc)
            self.assertEqual([], doc["survived"], doc)
            self.assertEqual(0, out.returncode)
            self.assertEqual(doc["mutants"], doc["killed"])

    def test_it_never_writes_inside_the_repo_it_was_given(self):
        """It mutates source on purpose, and the repo may hold uncommitted work."""
        with tempfile.TemporaryDirectory() as t:
            repo = build_repo(Path(t), INERT_TEST)
            before = git(repo, "status", "--porcelain")
            digest = (repo / "src" / "pipeline.py").read_text()
            run_gate(repo)
            self.assertEqual(before, git(repo, "status", "--porcelain"))
            self.assertEqual(digest, (repo / "src" / "pipeline.py").read_text())


class TestItRefusesRatherThanGuessing(unittest.TestCase):
    def test_a_red_baseline_does_not_run(self):
        """A mutant killed by an already-failing suite is killed by the failure."""
        with tempfile.TemporaryDirectory() as t:
            repo = build_repo(Path(t), INERT_TEST)
            (repo / "tests" / "test_broken.py").write_text("def test_x():\n    assert False\n")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "a failing test")
            out, doc = run_gate(repo)
            self.assertFalse(doc["ran"])
            self.assertIn("baseline", doc["reason"])
            self.assertEqual(3, out.returncode)

    def test_no_test_command_does_not_run(self):
        with tempfile.TemporaryDirectory() as t:
            repo = build_repo(Path(t), INERT_TEST)
            cfg = repo / ".delivery-flow.yaml"
            cfg.write_text("\n".join(l for l in cfg.read_text().splitlines()
                                     if not l.startswith("test_command:")) + "\n")
            out, doc = run_gate(repo)
            self.assertFalse(doc["ran"])
            self.assertEqual(3, out.returncode)

    def test_a_diff_with_no_production_python_mutates_nothing(self):
        with tempfile.TemporaryDirectory() as t:
            repo = build_repo(Path(t), REAL_TEST)
            git(repo, "checkout", "-q", "-b", "docs-only", "main")
            (repo / "README.md").write_text("docs\n")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "docs")
            out, doc = run_gate(repo)
            self.assertTrue(doc["ran"])
            self.assertEqual(0, doc["mutants"])
            self.assertEqual(0, out.returncode)


class TestItMutatesOnlyTheDiffsProductionLines(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = build_repo(Path(self.tmp.name), INERT_TEST)

    def tearDown(self):
        self.tmp.cleanup()

    def test_changed_lines_skips_test_files(self):
        got = mg.changed_lines(self.repo, "main", "HEAD")
        self.assertIn("src/pipeline.py", got)
        self.assertNotIn("tests/test_recovery.py", got,
                         "mutating a test and watching it fail proves nothing")

    def test_changed_lines_covers_only_the_added_lines(self):
        """Mutating untouched code measures the suite's history, not this branch."""
        got = mg.changed_lines(self.repo, "main", "HEAD")["src/pipeline.py"]
        lines = (self.repo / "src" / "pipeline.py").read_text().splitlines()
        added = {i for i in range(len(PRODUCTION.splitlines()) + 1, len(lines) + 1)}
        self.assertEqual(added, got, "only the `complete` method is new on this branch")

    def test_strings_and_comments_are_not_candidates(self):
        """The class docstring contains `a == b`; tokenising is what keeps it out."""
        targets = set(range(1, 40))
        got = mg.mutants_for_file(self.repo / "src" / "pipeline.py", "src/pipeline.py", targets)
        self.assertTrue(got)
        for m in got:
            self.assertNotIn("docstring", m["before"],
                             f"mutated inside a string: {m}")

    def test_a_one_line_if_body_is_left_alone(self):
        self.assertIsNone(mg._unconditional("    if x: return y"))
        self.assertEqual("    if True:", mg._unconditional("    if x == 1:"))
        self.assertEqual("    elif True:", mg._unconditional("    elif x == 1:"))

    def test_an_already_unconditional_if_is_not_remutated(self):
        self.assertIsNone(mg._unconditional("    if True:"))

    def test_a_mutant_that_cannot_compile_is_dropped(self):
        """`ast.parse` is the filter; a mutant that will not run tests nothing."""
        p = Path(self.tmp.name) / "broken.py"
        p.write_text("x = 1\nif not x:\n    pass\n")
        got = mg.mutants_for_file(p, "broken.py", {2})
        for m in got:
            __import__("ast").parse(m["source"])


class TestTheBudgetThinsEveryFile(unittest.TestCase):
    def test_a_cap_round_robins_rather_than_dropping_a_file_whole(self):
        mutants = ([{"file": "a.py", "line": i} for i in range(5)]
                   + [{"file": "b.py", "line": i} for i in range(5)])
        picked, capped = mg.budget(mutants, 4)
        self.assertTrue(capped)
        self.assertEqual(4, len(picked))
        self.assertEqual({"a.py", "b.py"}, {m["file"] for m in picked},
                         "a cap that silences a whole file hides that file's findings")

    def test_under_the_cap_nothing_is_dropped(self):
        mutants = [{"file": "a.py", "line": 1}]
        picked, capped = mg.budget(mutants, 10)
        self.assertFalse(capped)
        self.assertEqual(mutants, picked)


class TestTheTestSubsetIsRunnable(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = build_repo(Path(self.tmp.name), INERT_TEST)

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_deleted_test_file_is_not_handed_to_the_runner(self):
        git(self.repo, "rm", "-q", "tests/test_recovery.py")
        git(self.repo, "commit", "-qm", "drop the test")
        self.assertEqual([], mg.changed_test_files(self.repo, "main", "HEAD"))

    def test_a_committed_pycache_under_tests_is_not_handed_to_the_runner(self):
        """It is test territory by path and a collection error by content. This happened."""
        d = self.repo / "tests" / "__pycache__"
        d.mkdir(exist_ok=True)
        (d / "test_recovery.cpython-312.pyc").write_bytes(b"\x00\x01")
        git(self.repo, "add", "-Af", "tests/__pycache__")
        git(self.repo, "commit", "-qm", "oops")
        got = mg.changed_test_files(self.repo, "main", "HEAD")
        self.assertEqual(["tests/test_recovery.py"], got)


class TestVerifyRecordsItEvenWhenItDoesNotRun(unittest.TestCase):
    """A missing field reads as clean, which is the flattering direction."""

    def setUp(self):
        self.rv = load(ROOT / "scripts" / "delivery-flow" / "run-verify.py", "run_verify")

    def test_disabled_is_recorded_with_a_reason(self):
        got = self.rv.run_mutation(ROOT, {}, None, None)
        self.assertFalse(got["ran"])
        self.assertTrue(got["reason"])

    def test_the_flag_overrides_a_config_that_enables_it(self):
        got = self.rv.run_mutation(ROOT, {"mutation": {"enabled": True}}, False, None)
        self.assertFalse(got["ran"])
        self.assertIn("not enabled", got["reason"])

    def test_the_verify_schema_requires_a_ran_field(self):
        schema = json.loads((ROOT / "schemas" / "verify.schema.json").read_text())
        mutation = schema["properties"]["mutation"]
        self.assertEqual(["ran"], mutation["required"])


if __name__ == "__main__":
    unittest.main()
