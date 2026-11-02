#!/usr/bin/env python3
"""`common.py`'s re-exports must stay re-exports, not forks.

Task 1.3 of certify-sdlc-pipeline requires that moving code into `scripts/workflow/` change
no import in the submitted tree. The mechanism is thin shims in
`scripts/delivery-flow/common.py`, and the risk is that someone later edits a shim — fixing a
bug in the delivery-flow copy while the substrate copy, and any second workflow built on it,
keeps the bug.

So these tests assert **identity**, not equality: `common.price_for` must *be*
`pricing.price_for`, the same function object. Equality of results would pass against two
diverging implementations that happen to agree on the cases tested, which is exactly the
failure this is meant to prevent.

Grows with each slice of the extraction. One class per moved module.

Run: python3 tests/workflow/test_substrate_shims.py
"""

import ast
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))
sys.path.insert(0, str(ROOT / "scripts" / "delivery-flow"))
import common  # noqa: E402
import pricing  # noqa: E402
import registry  # noqa: E402
import layout  # noqa: E402
import schema  # noqa: E402


class TestPricing(unittest.TestCase):
    """`scripts/workflow/pricing.py`, moved in task 1.1."""

    def test_the_shims_are_the_substrate_functions(self):
        for name in ("price_for", "cost_usd", "usage_from_transcript"):
            with self.subTest(name=name):
                self.assertIs(getattr(common, name), getattr(pricing, name),
                              f"common.{name} has been forked from pricing.{name}")

    def test_load_pricing_delegates_to_the_substrate(self):
        """Not an identity check: this one wraps, because it supplies the default path."""
        self.assertEqual(common.load_pricing(), pricing.load(common.PRICING_PATH))

    def test_the_default_pricing_table_exists(self):
        self.assertTrue(common.PRICING_PATH.is_file(), common.PRICING_PATH)

    def test_the_substrate_refuses_to_guess_a_pricing_table(self):
        """`load` takes no default, so a second workflow cannot be priced off this one."""
        with self.assertRaises(TypeError):
            pricing.load()

    def test_pricing_still_parses_and_prices(self):
        """A behavioural anchor, so the move is not merely structurally intact."""
        table = common.load_pricing()
        self.assertTrue(table.get("meta", {}).get("as_of"), "pricing table has no as_of date")
        row = common.price_for("claude-sonnet-4-5", table)
        self.assertIsNotNone(row, "the default table prices no sonnet model")
        cost = common.cost_usd({"input_tokens": 1000, "output_tokens": 500}, row)
        self.assertGreater(cost, 0)

    def test_an_unknown_model_is_unpriced_rather_than_free(self):
        """A model the table does not list must not silently cost zero."""
        self.assertIsNone(common.price_for("some-model-nobody-listed", common.load_pricing()))


class TestSchema(unittest.TestCase):
    """`scripts/workflow/schema.py`, moved in task 1.1."""

    def test_the_shims_are_the_substrate_functions(self):
        for name in ("count_expr", "expected_counts"):
            with self.subTest(name=name):
                self.assertIs(getattr(common, name), getattr(schema, name))

    def test_schema_for_delegates(self):
        loaded = common.load_schemas()
        self.assertIs(common.schema_for("breakdown.json", loaded),
                      schema.for_name("breakdown.json", loaded))

    def test_load_schemas_delegates_to_the_substrate(self):
        self.assertEqual(sorted(common.load_schemas()), sorted(schema.load(common.SCHEMA_DIR)))

    def test_the_substrate_refuses_to_guess_a_schema_directory(self):
        with self.assertRaises(TypeError):
            schema.load()

    def test_a_sentinel_resolves_to_the_sentinel_schema_not_its_artifact(self):
        """Longest-glob-first, which is load-bearing: both names are `<x>.json`-shaped."""
        loaded = common.load_schemas()
        self.assertEqual(
            common.schema_for("breakdown.json.sentinel.json", loaded)["artifact"],
            "*.sentinel.json")

    def test_count_expr_sums_across_branches(self):
        doc = {"epics": [{"stories": [1, 2]}, {"stories": [3]}]}
        self.assertEqual(common.count_expr(doc, "epics[].stories[]"), 3)

    def test_count_expr_rejects_a_segment_without_brackets(self):
        with self.assertRaises(ValueError):
            common.count_expr({}, "epics")


class TestRegistryShims(unittest.TestCase):
    """`scripts/workflow/registry.py`, moved in task 1.1."""

    def test_the_workflow_name_drives_the_registry_location(self):
        self.assertEqual(common.WORKFLOW_NAME, "delivery-flow")
        self.assertEqual(registry.env_var(common.WORKFLOW_NAME), "DELIVERY_FLOW_REPOS")


class TestLayout(unittest.TestCase):
    """`scripts/workflow/layout.py`, moved in task 1.1. What section 2 is blocked on."""

    def test_repo_root_is_the_substrate_function(self):
        self.assertIs(common.repo_root, layout.repo_root)

    def test_is_delivery_repo_delegates_with_this_workflows_config_name(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / ".git").mkdir()
            self.assertFalse(common.is_delivery_repo(repo))
            (repo / common.CONFIG_NAME).write_text("\n")
            self.assertTrue(common.is_delivery_repo(repo))
            self.assertEqual(common.is_delivery_repo(repo),
                             layout.opted_in(repo, common.CONFIG_NAME))

    def test_a_second_workflows_config_does_not_opt_a_repo_in(self):
        """The isolation property, at the layout level."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / ".git").mkdir()
            (repo / ".other-workflow.yaml").write_text("\n")
            self.assertFalse(layout.opted_in(repo, common.CONFIG_NAME))
            self.assertTrue(layout.opted_in(repo, ".other-workflow.yaml"))

    def test_parse_artifact_path_matches_the_default_layout(self):
        self.assertEqual(common.parse_artifact_path("x/delivery/AN-1/triage.json"),
                         ("AN-1", "triage.json"))

    def test_parse_artifact_path_with_a_root_matches_that_root(self):
        self.assertEqual(
            common.parse_artifact_path("/vault/_runs/AN-1/triage.json", Path("/vault/_runs")),
            ("AN-1", "triage.json"))

    def test_a_directory_merely_named_like_the_root_does_not_match(self):
        """Why passing `root` matters: the fallback would claim this."""
        self.assertEqual(
            common.parse_artifact_path("/elsewhere/delivery/AN-1/t.json", Path("/vault/_runs")),
            (None, None))

    def test_the_artifact_dir_is_escaped_in_the_pattern(self):
        """A workflow whose artifact dir contains regex metacharacters must still match."""
        self.assertEqual(layout.parse_artifact_path("a/my.dir/AN-1/t.json", "my.dir"),
                         ("AN-1", "t.json"))
        self.assertEqual(layout.parse_artifact_path("a/myXdir/AN-1/t.json", "my.dir"),
                         (None, None))

    def test_artifact_root_defaults_inside_the_repo(self):
        self.assertEqual(common.artifact_root(Path("/r"), {}), Path("/r/delivery"))

    def test_an_absolute_configured_root_leaves_the_repo(self):
        cfg = {"artifacts": {"root": "/vault/_runs"}}
        self.assertEqual(common.artifact_root(Path("/r"), cfg), Path("/vault/_runs"))

    def test_a_relative_configured_root_stays_inside(self):
        cfg = {"artifacts": {"root": "runs"}}
        self.assertEqual(common.artifact_root(Path("/r"), cfg), Path("/r/runs"))


class TestTheSubstrateStaysWorkflowAgnostic(unittest.TestCase):
    """Nothing under `scripts/workflow/` may name delivery-flow."""

    def test_no_substrate_module_mentions_delivery(self):
        """Checked against the AST, not the text.

        Prose may name delivery-flow — the modules explain where they were moved from, and
        that provenance is worth keeping. Only *code* is in scope, so docstrings and comments
        are stripped by parsing rather than guessed at with a line scan. The first version of
        this test used a line scan and failed on its own docstring.
        """
        offenders = []
        for p in sorted((ROOT / "scripts" / "workflow").glob("*.py")):
            tree = ast.parse(p.read_text(), filename=str(p))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                     ast.AsyncFunctionDef)) and ast.get_docstring(node):
                    node.body = node.body[1:]
            code = ast.unparse(tree)
            for lineno, line in enumerate(code.splitlines(), 1):
                if "delivery" in line:
                    offenders.append(f"{p.name}: {line.strip()}")
        self.assertEqual(offenders, [],
                         "substrate code references delivery-flow; it must be workflow-agnostic")


if __name__ == "__main__":
    unittest.main(verbosity=2)
