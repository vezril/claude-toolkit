#!/usr/bin/env python3
"""Tests for delivery recall over a synthetic mini-vault.

Asserts **exact scores** and exact membership, not a pass rate: that strictness is the whole
argument for implementing recall as a script rather than certifying it as a prompt.

Run: python3 tests/delivery-flow/test_vault_recall.py
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
RECALL = SCRIPTS / "vault-recall.py"

sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("vault_recall", RECALL)
vr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vr)

ITEM = {"key": "DEM-12", "title": "Retry cap for the ledger consumer",
        "body": "b", "status": "Open", "url": "u", "source": "jira", "labels": [], "links": []}
TRIAGE = {"item": "DEM-12", "type": "feature", "path": "standard",
          "domains": ["backend", "infra"], "summary": "Add a bounded retry cap to the consumer.",
          "rationale": "r", "handoff": False, "handoff_reason": None,
          "architecture_change": False, "breaking_change": False,
          "services": ["[[orders-api]]"]}


def note(path: Path, **fm):
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        else:
            lines.append(f"{k}: {v}")
    lines += ["---", "", "## Body", "", "Narrative that must never reach the output.", ""]
    path.write_text("\n".join(lines))


class Vault:
    """One project, two services, accepted and superseded decisions, deliveries, lessons,
    patterns, and a cross-project decoy — the fixture the parent change specified."""

    def __init__(self, project="olympus", empty=False):
        self.base = Path(tempfile.mkdtemp())
        self.root = self.base / "vault" / "Atlas" / "RAG"
        for f in ("decisions", "deliveries", "lessons", "patterns", "entities"):
            (self.root / f).mkdir(parents=True, exist_ok=True)
        if empty:
            return

        # same project + 1 keyword = 3 + 1 = 4 -> kept
        note(self.root / "decisions" / "grpc-bff.md", type="decision", project=project,
             status="accepted", date="2026-05-01",
             decision="Use a gRPC BFF for the retry path", context="c", consequences="x")
        # another project, 1 keyword, no shared service = 1 -> dropped
        note(self.root / "decisions" / "rest-bff.md", type="decision", project="hermes",
             status="accepted", date="2026-06-01",
             decision="Use REST for the retry path", context="c", consequences="x")
        # same project but superseded -> coverage only
        note(self.root / "decisions" / "old-retry.md", type="decision", project=project,
             status="superseded", date="2026-01-01", superseded_by=["[[grpc-bff]]"],
             decision="Unbounded retry was fine", context="c", consequences="x")
        # cross-project but shares a service + 1 keyword = 3 + 1 = 4 -> kept
        note(self.root / "deliveries" / "HER-3.md", type="delivery", project="hermes",
             status="shipped", date="2026-07-01", services=["[[orders-api]]"],
             goal="Cap the retry storm", approach="a", outcome="o")
        note(self.root / "deliveries" / "DEM-4.md", type="delivery", project=project,
             status="shipped", date="2026-08-01", goal="Ledger reads", approach="a", outcome="o")
        # one shared domain only: 2 in solutioning (dropped), 3 in implementation (kept)
        note(self.root / "lessons" / "budget-your-retries.md", type="lesson",
             domains=["backend"], date="2026-04-01",
             lesson="Budget retries", practice="p", why="w")
        note(self.root / "patterns" / "silent-await.md", type="pattern", project=project,
             date="2026-03-01", shape="s", detection="d", mitigation="m")

    def cfg(self, binding="olympus", backend="filesystem"):
        return {"vault": {"binding": binding, "path": str(self.base / "vault"),
                          "graph_root": "Atlas/RAG", "backend": backend}}


class Repo:
    def __init__(self, vault: Vault, binding="olympus", graph_root="Atlas/RAG", backend="filesystem"):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / ".git").mkdir()
        (self.dir / ".delivery-flow.yaml").write_text(
            "tracker:\n  kind: jira\nprofile: full\n"
            f"vault:\n  binding: {binding}\n  path: {vault.base / 'vault'}\n"
            f"  graph_root: {graph_root}\n  backend: {backend}\n")
        self.item_dir = self.dir / "delivery" / "DEM-12"
        self.item_dir.mkdir(parents=True)
        (self.item_dir / "item.json").write_text(json.dumps(ITEM))
        (self.item_dir / "triage.json").write_text(json.dumps(TRIAGE))

    def run(self, *args):
        return subprocess.run([sys.executable, str(RECALL), "DEM-12", "--repo", str(self.dir),
                               *args], capture_output=True, text=True)


def do(vault, mode="solutioning", story=None, cfg=None):
    return vr.recall(ITEM, TRIAGE, cfg or vault.cfg(), mode, story)


def git(repo: Path, *args, **env):
    e = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x.invalid",
         "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x.invalid",
         "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(repo)}
    e.update({k: str(v) for k, v in env.items()})
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, env=e)


class TestVaultSyncState(unittest.TestCase):
    """The local clone is always reachable, so freshness replaces reachability as the signal.

    A clone weeks behind the NAS looks identical to a current one unless the run says so, and a
    silent wrong answer is worse than a loud missing one — which is the whole reason D3 exists.
    """

    def clone(self, commits=True, remote=True, dirty=False):
        v = Vault()
        repo = v.base / "vault"
        git(repo, "init", "-q", "-b", "main")
        if commits:
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "scaffold")
        if remote:
            bare = v.base / "nas" / "amazon-rag.git"
            bare.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "init", "-q", "--bare", str(bare)], capture_output=True)
            git(repo, "remote", "add", "origin", str(bare))
            if commits:
                git(repo, "push", "-q", "-u", "origin", "main")
        if dirty:
            (repo / "Atlas" / "RAG" / "decisions" / "wip.md").write_text("---\ntype: decision\n---\n")
        return v

    def test_a_git_backed_vault_reports_its_head_and_cleanliness(self):
        v = self.clone()
        doc = do(v)
        s = doc["vault"]
        self.assertTrue(s["tracked"])
        self.assertIsNotNone(s["head"])
        self.assertFalse(s["dirty"])
        self.assertEqual(s["upstream"], "origin/main")

    def test_a_non_git_vault_says_so_rather_than_claiming_freshness(self):
        """A plain directory has no sync story, and must not be reported as a synced one."""
        doc = do(Vault())
        s = doc["vault"]
        self.assertFalse(s["tracked"])
        self.assertFalse(s["stale"])
        self.assertTrue(any("not a git work tree" in n for n in s["notes"]))

    def test_uncommitted_notes_are_reported_as_not_durable(self):
        doc = do(self.clone(dirty=True))
        self.assertTrue(doc["vault"]["dirty"])
        self.assertTrue(any("uncommitted" in n for n in doc["vault"]["notes"]))

    def test_unpushed_commits_are_counted_and_called_out(self):
        v = self.clone()
        repo = v.base / "vault"
        (repo / "Atlas" / "RAG" / "decisions" / "new.md").write_text("---\ntype: decision\n---\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "a local decision")
        s = do(v)["vault"]
        self.assertEqual(s["ahead"], 1)
        self.assertEqual(s["behind"], 0)
        self.assertTrue(any("not reached the NAS" in n for n in s["notes"]))

    def test_a_clone_past_the_ceiling_is_marked_stale(self):
        v = self.clone()
        cfg = v.cfg()
        cfg["punch_out"] = {"vault_staleness_days": 0}   # anything synced before today is stale
        import os
        fetch_head = v.base / "vault" / ".git" / "FETCH_HEAD"
        fetch_head.write_text("")
        old = datetime.now(timezone.utc).timestamp() - 40 * 86400
        os.utime(fetch_head, (old, old))
        s = vr.recall(ITEM, TRIAGE, cfg, "solutioning")["vault"]
        self.assertTrue(s["stale"])
        self.assertGreaterEqual(s["days_since_sync"], 39)
        self.assertTrue(any("newer decisions" in n for n in s["notes"]))

    def test_a_fresh_clone_is_not_stale(self):
        s = do(self.clone())["vault"]
        self.assertFalse(s["stale"])

    def test_a_null_ceiling_disables_the_staleness_check(self):
        v = self.clone()
        cfg = v.cfg()
        cfg["punch_out"] = {"vault_staleness_days": None}
        import os
        fetch_head = v.base / "vault" / ".git" / "FETCH_HEAD"
        fetch_head.write_text("")
        old = datetime.now(timezone.utc).timestamp() - 400 * 86400
        os.utime(fetch_head, (old, old))
        s = vr.recall(ITEM, TRIAGE, cfg, "solutioning")["vault"]
        self.assertFalse(s["stale"])
        self.assertIsNone(s["staleness_ceiling_days"])

    def test_a_nonsense_ceiling_is_a_usage_error_not_a_silent_default(self):
        v = self.clone()
        cfg = v.cfg()
        cfg["punch_out"] = {"vault_staleness_days": "soon"}
        with self.assertRaises(vr.Usage):
            vr.recall(ITEM, TRIAGE, cfg, "solutioning")

    def test_a_config_remote_disagreeing_with_origin_is_reported(self):
        v = self.clone()
        cfg = v.cfg()
        cfg["vault"]["remote"] = "ssh://elsewhere/amazon-rag.git"
        s = vr.recall(ITEM, TRIAGE, cfg, "solutioning")["vault"]
        self.assertTrue(any("one of them is wrong" in n for n in s["notes"]))

    def test_no_upstream_is_unknown_rather_than_zero(self):
        """Reporting ahead=0 with no upstream would claim agreement we cannot observe."""
        s = do(self.clone(remote=False))["vault"]
        self.assertIsNone(s["ahead"])
        self.assertTrue(any("tracks no upstream" in n for n in s["notes"]))

    def test_the_artifact_still_satisfies_its_schema(self):
        from common import load_schemas
        vspec = importlib.util.spec_from_file_location(
            "validate_artifact", SCRIPTS / "validate-artifact.py")
        validator = importlib.util.module_from_spec(vspec)
        vspec.loader.exec_module(validator)
        problems = []
        validator.validate(do(self.clone()), load_schemas()["project-context.json"], "", problems)
        self.assertEqual(problems, [])

    def test_recall_makes_no_network_call(self):
        """A step that hung on an unreachable NAS would reinstate the dependency we removed."""
        src = RECALL.read_text()
        for forbidden in ("ls-remote", "git fetch", '"fetch"', '"pull"', '"push"'):
            self.assertNotIn(forbidden, src, f"recall must not reach the network: {forbidden}")

    def test_the_markdown_leads_with_a_stale_warning(self):
        v = self.clone()
        cfg = v.cfg()
        cfg["punch_out"] = {"vault_staleness_days": 0}
        import os
        fetch_head = v.base / "vault" / ".git" / "FETCH_HEAD"
        fetch_head.write_text("")
        old = datetime.now(timezone.utc).timestamp() - 40 * 86400
        os.utime(fetch_head, (old, old))
        md = vr.render_md(vr.recall(ITEM, TRIAGE, cfg, "solutioning"))
        self.assertIn("Stale memory", md.split("\n\n")[1])
        self.assertIn("## Vault sync", md)


class TestScoring(unittest.TestCase):
    def test_same_project_decision_outranks_a_cross_project_one(self):
        doc = do(Vault())
        names = [d["note"] for d in doc["decisions"]]
        self.assertIn("grpc-bff", names)
        self.assertNotIn("rest-bff", names)
        self.assertEqual([d["score"] for d in doc["decisions"] if d["note"] == "grpc-bff"], [4])

    def test_a_cross_project_hit_through_a_shared_service_scores_four(self):
        doc = do(Vault())
        her = [d for d in doc["deliveries"] if d["note"] == "HER-3"]
        self.assertEqual(len(her), 1)
        self.assertEqual(her[0]["score"], 4)

    def test_domains_weigh_more_during_implementation(self):
        v = Vault()
        self.assertEqual([l["note"] for l in do(v)["lessons"]], [])
        impl = do(v, mode="implementation", story="S1")
        self.assertEqual([l["note"] for l in impl["lessons"]], ["budget-your-retries"])
        self.assertEqual(impl["lessons"][0]["score"], 3)

    def test_the_threshold_drops_low_scorers(self):
        doc = do(Vault())
        self.assertGreater(doc["coverage"]["dropped"], 0)
        for bucket in ("decisions", "deliveries", "lessons", "patterns"):
            for m in doc[bucket]:
                self.assertGreaterEqual(m["score"], vr.THRESHOLD)

    def test_caps_are_applied_after_sorting(self):
        v = Vault()
        for i in range(8):
            note(v.root / "decisions" / f"extra-{i}.md", type="decision", project="olympus",
                 status="accepted", date=f"2026-09-0{i + 1}",
                 decision=f"Retry policy variant {i}", context="c", consequences="x")
        doc = do(v)
        self.assertEqual(len(doc["decisions"]), vr.CAPS["decisions"])
        self.assertGreater(doc["coverage"]["capped"], 0)
        scores = [d["score"] for d in doc["decisions"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_ties_break_by_date_newest_first(self):
        v = Vault();
        for name, date in (("tie-old", "2026-02-01"), ("tie-new", "2026-09-01")):
            note(v.root / "deliveries" / f"{name}.md", type="delivery", project="olympus",
                 status="shipped", date=date, goal="Retry cap work", approach="a", outcome="o")
        doc = do(v)
        order = [d["note"] for d in doc["deliveries"] if d["note"].startswith("tie-")]
        self.assertEqual(order, ["tie-new", "tie-old"])


class TestDecisionStatus(unittest.TestCase):
    def test_only_accepted_decisions_are_in_force(self):
        doc = do(Vault())
        self.assertNotIn("old-retry", [d["note"] for d in doc["decisions"]])

    def test_a_superseded_decision_appears_in_coverage_with_its_replacement(self):
        doc = do(Vault())
        skipped = " ".join(doc["coverage"]["superseded_skipped"])
        self.assertIn("old-retry", skipped)
        self.assertIn("grpc-bff", skipped)


class TestOutput(unittest.TestCase):
    def test_body_text_never_reaches_the_output(self):
        doc = do(Vault())
        self.assertNotIn("Narrative", json.dumps(doc))

    def test_payload_lines_only(self):
        doc = do(Vault())
        for d in doc["decisions"]:
            self.assertTrue(set(d["payload"]) <= set(vr.PAYLOAD["decision"]))

    def test_the_keyword_set_is_reported_and_filtered(self):
        doc = do(Vault())
        kws = doc["coverage"]["keywords"]
        self.assertIn("retry", kws)
        self.assertIn("consumer", kws)
        self.assertNotIn("the", kws)
        self.assertNotIn("add", kws)
        self.assertTrue(all(len(k) >= vr.MIN_KEYWORD_LEN for k in kws))

    def test_the_artifact_conforms_to_its_schema(self):
        from common import load_schemas
        s = importlib.util.spec_from_file_location("va", SCRIPTS / "validate-artifact.py")
        va = importlib.util.module_from_spec(s); s.loader.exec_module(va)
        problems = []
        va.validate(do(Vault()), load_schemas()["project-context.json"], "", problems)
        self.assertEqual(problems, [])

    def test_the_markdown_stays_within_the_line_cap(self):
        v = Vault()
        for i in range(30):
            note(v.root / "deliveries" / f"bulk-{i}.md", type="delivery", project="olympus",
                 status="shipped", date="2026-09-01", goal=f"Retry consumer work {i}",
                 approach="a", outcome="o")
        md = vr.render_md(do(v))
        self.assertLessEqual(len(md.splitlines()), vr.MD_LINE_CAP)

    def test_reruns_are_byte_identical(self):
        r = Repo(Vault())
        self.assertEqual(r.run().returncode, 0)
        first = (r.item_dir / "project-context.json").read_text()
        self.assertEqual(r.run().returncode, 0)
        self.assertEqual((r.item_dir / "project-context.json").read_text(), first)

    def test_implementation_mode_does_not_overwrite_the_solutioning_output(self):
        r = Repo(Vault())
        r.run()
        before = (r.item_dir / "project-context.json").read_text()
        out = r.run("--mode", "implementation", "--story", "S1")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertTrue((r.item_dir / "project-context-S1.json").exists())
        self.assertEqual((r.item_dir / "project-context.json").read_text(), before)


class TestReachability(unittest.TestCase):
    """Unreachable is not empty — the decision this whole script hangs on."""

    def test_an_absent_graph_root_exits_3_and_writes_nothing(self):
        v = Vault()
        r = Repo(v, graph_root="Atlas/NotMounted")
        out = r.run()
        self.assertEqual(out.returncode, 3)
        self.assertIn("not there", out.stderr)
        self.assertFalse((r.item_dir / "project-context.json").exists())

    def test_a_file_where_the_graph_root_should_be_exits_3(self):
        v = Vault()
        (v.base / "vault" / "NotADir").write_text("x")
        r = Repo(v, graph_root="NotADir")
        out = r.run()
        self.assertEqual(out.returncode, 3)
        self.assertIn("not a directory", out.stderr)

    def test_a_reachable_but_empty_vault_exits_0_with_an_artifact(self):
        r = Repo(Vault(empty=True))
        out = r.run()
        self.assertEqual(out.returncode, 0, out.stderr)
        doc = json.loads((r.item_dir / "project-context.json").read_text())
        self.assertFalse(doc["matched"])
        self.assertEqual(doc["coverage"]["scanned"],
                         {"decisions": 0, "deliveries": 0, "lessons": 0, "patterns": 0})

    def test_the_empty_markdown_says_so_rather_than_inventing(self):
        r = Repo(Vault(empty=True))
        r.run()
        md = (r.item_dir / "project-context.md").read_text()
        self.assertIn("Nothing in the vault matched", md)
        self.assertIn("## Search coverage", md)

    def test_an_unimplemented_backend_is_a_usage_error(self):
        out = Repo(Vault(), backend="iris").run()
        self.assertEqual(out.returncode, 2)
        self.assertIn("not implemented", out.stderr)

    def test_no_binding_is_a_usage_error(self):
        out = Repo(Vault(), binding="null").run()
        self.assertEqual(out.returncode, 2)
        self.assertIn("no project", out.stderr)

    def test_a_graph_root_escaping_the_vault_is_refused(self):
        with self.assertRaises(vr.Usage):
            vr.graph_root({"vault": {"path": "/tmp/x", "graph_root": "../elsewhere"}})


class TestFrontmatterParsing(unittest.TestCase):
    def test_wikilinks_and_bare_names_compare_equal(self):
        self.assertEqual(vr.link_names(["[[orders-api]]", "ledger"]), {"orders-api", "ledger"})

    def test_a_note_without_frontmatter_is_ignored_not_fatal(self):
        v = Vault()
        (v.root / "decisions" / "plain.md").write_text("# just a note\n")
        doc = do(v)
        self.assertNotIn("plain", [d["note"] for d in doc["decisions"]])

    def test_inline_and_block_lists_both_parse(self):
        v = Vault()
        (v.root / "deliveries" / "block.md").write_text(
            "---\ntype: delivery\nproject: olympus\nstatus: shipped\ndate: 2026-09-09\n"
            "services:\n  - '[[orders-api]]'\ngoal: Retry work\napproach: a\noutcome: o\n---\n")
        doc = do(v)
        self.assertIn("block", [d["note"] for d in doc["deliveries"]])


class TestScaffold(unittest.TestCase):
    """The vault is somebody's own notes: additive only, and confined to the vault."""

    SCAFFOLD = SCRIPTS / "scaffold-vault.py"

    # NB: this helper is deliberately *not* called `run`. `TestCase.run` is the method
    # unittest calls to execute a test, and shadowing it makes every test in the class
    # silently report nothing — no failures, no successes, just a missing test count.

    def vault(self):
        base = Path(tempfile.mkdtemp()) / "vault"
        base.mkdir(parents=True)
        (base / "Welcome.md").write_text("# my own notes\n")
        return base

    def scaffold(self, vault, *args):
        return subprocess.run([sys.executable, str(self.SCAFFOLD), "--vault", str(vault),
                               "--graph-root", "Atlas/RAG", "--binding", "amazon", *args],
                              capture_output=True, text=True)

    def test_it_creates_the_graph_and_leaves_existing_notes_alone(self):
        v = self.vault()
        before = (v / "Welcome.md").read_text()
        out = self.scaffold(v, "--json")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertTrue((v / "Atlas" / "RAG" / "decisions").is_dir())
        self.assertTrue((v / "Atlas" / "RAG" / "entities" / "amazon.md").is_file())
        self.assertEqual((v / "Welcome.md").read_text(), before)

    def test_running_it_twice_changes_nothing(self):
        v = self.vault()
        self.scaffold(v)
        payload = json.loads(self.scaffold(v, "--json").stdout)
        self.assertEqual(payload["created"], [])
        self.assertTrue(payload["skipped"])

    def test_an_existing_note_in_the_graph_is_never_overwritten(self):
        v = self.vault()
        self.scaffold(v)
        mine = v / "Atlas" / "RAG" / "entities" / "amazon.md"
        mine.write_text("--- \ntype: entity\n---\n\nmy own edits\n")
        self.scaffold(v)
        self.assertIn("my own edits", mine.read_text())

    def test_a_graph_root_escaping_the_vault_is_refused(self):
        v = self.vault()
        out = subprocess.run([sys.executable, str(self.SCAFFOLD), "--vault", str(v),
                              "--graph-root", "../escape", "--binding", "amazon"],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 2)
        self.assertFalse((v.parent / "escape").exists())

    def test_an_unreachable_vault_exits_3_and_creates_nothing(self):
        missing = Path(tempfile.mkdtemp()) / "not-mounted"
        out = self.scaffold(missing)
        self.assertEqual(out.returncode, 3)
        self.assertIn("not reachable", out.stderr)
        self.assertFalse(missing.exists())

    def test_dry_run_writes_nothing(self):
        v = self.vault()
        out = self.scaffold(v, "--dry-run", "--json")
        self.assertEqual(out.returncode, 0)
        self.assertTrue(json.loads(out.stdout)["created"])
        self.assertFalse((v / "Atlas").exists())

    def test_a_scaffolded_vault_is_reachable_and_recalls_empty(self):
        """The round trip: scaffold, then recall reports a cold start rather than failing."""
        v = self.vault()
        self.scaffold(v)
        cfg = {"vault": {"binding": "amazon", "path": str(v),
                         "graph_root": "Atlas/RAG", "backend": "filesystem"}}
        doc = vr.recall(ITEM, TRIAGE, cfg, "solutioning")
        self.assertFalse(doc["matched"])
        self.assertEqual(doc["project"], "amazon")
        self.assertEqual(sum(doc["coverage"]["scanned"].values()), 0)


class TestDocsMatchTheImplementation(unittest.TestCase):
    """The reference says the script is normative, so the reference must not contradict it.

    Caught a real drift when written: the doc spelled the keyword floor "four characters" while
    the code read 4, which no test would otherwise have noticed.
    """

    DOC = ROOT / "skills" / "vault-graphrag" / "references" / "delivery-recall.md"
    SCHEMA = ROOT / "skills" / "vault-graphrag" / "references" / "schema.md"

    def setUp(self):
        self.doc = self.DOC.read_text()
        self.schema = self.SCHEMA.read_text()

    def test_the_payload_fields_match_per_type(self):
        import re
        for kind, fields in vr.PAYLOAD.items():
            rows = [l for l in self.doc.splitlines() if l.startswith(f"| {kind} |")]
            self.assertTrue(rows, f"no payload row documented for {kind}")
            documented = set(re.findall(r"`([a-z_]+)`", rows[0]))
            self.assertEqual(documented, set(fields), kind)

    def test_the_weights_and_threshold_are_documented_as_implemented(self):
        self.assertIn(f"**+{vr.SCORE_SAME_PROJECT}**", self.doc)
        self.assertIn(f"**+{vr.SCORE_SHARED_SERVICE}**", self.doc)
        self.assertIn(f"**+{vr.SCORE_SHARED_DOMAIN_SOLUTIONING}**", self.doc)
        self.assertIn(f"**+{vr.SCORE_SHARED_DOMAIN_IMPLEMENTATION}**", self.doc)
        self.assertIn(f"**+{vr.SCORE_KEYWORD}**", self.doc)
        self.assertIn(f"drop below {vr.THRESHOLD}", self.doc)

    def test_the_caps_are_documented_as_implemented(self):
        c = vr.CAPS
        self.assertIn(f"**{c['decisions']} decisions, {c['deliveries']} deliveries, "
                      f"{c['lessons']} lessons, {c['patterns']} patterns**", self.doc)

    def test_the_keyword_floor_is_documented_as_a_numeral(self):
        self.assertIn(f"**{vr.MIN_KEYWORD_LEN} characters**", self.doc)

    def test_the_markdown_cap_is_documented(self):
        self.assertIn(str(vr.MD_LINE_CAP), self.doc)

    def test_every_scanned_folder_appears_in_the_layout_block(self):
        for folder in vr.FOLDERS.values():
            self.assertIn(f"{folder}/", self.schema, folder)

    def test_the_exit_codes_are_documented(self):
        for code in ("**3**", "**0**", "**2**"):
            self.assertIn(code, self.doc)


if __name__ == "__main__":
    unittest.main(verbosity=2)
