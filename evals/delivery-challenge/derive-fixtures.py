#!/usr/bin/env python3
"""Build the challenge fixtures from real certified breakdowns, with one planted defect each.

The ground truth for an adversarial node is "the hole that is actually there", so every
fixture's provenance has to be auditable rather than asserted. This script is that audit:
each case names the certified breakdown run it starts from and the single edit that plants
its defect. Run it and the committed `inputs/` are reproduced byte for byte.

    python3 derive-fixtures.py            # write inputs/
    python3 derive-fixtures.py --check     # fail if the committed inputs/ differ

The base artifacts are the six outputs of `evals/delivery-breakdown` run v6 / Sonnet / run 1,
every one of which passed all four breakdown criteria. Nothing here is hand-authored prose:
a defect is a deletion, a substitution, or an insertion made of the item's own words.

Epic and story ids are then renumbered contiguously (`renumber`), because otherwise the edit
is visible in the numbering and the defect can be found without reading the item. See that
function for why that invalidated a run.

Defect classes, which are also what the prompt's verdict rule is written against:
  A1 a deliverable the item requires is in no story and no criterion   -> REFUTED
  A2 a story plans the opposite of what the item says                  -> REFUTED
  A3 a whole epic of work the item never asked for                     -> REFUTED
  B1 a story's criteria do not test the story's own statement          -> WEAKENED
  B2 a criterion's `then` asserts nothing observable                   -> WEAKENED
  B3 two stories are the same work                                     -> WEAKENED
  B4 a story's domains would send it to the wrong specialist           -> WEAKENED

Class B defects are all invisible to `breakdown.schema.json`: an empty criteria array is
not, so "a story with no criteria" is deliberately absent — the edge hook already fails it,
and a node taught to hunt for what code guarantees is a node learning the wrong job.
"""

import argparse
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BREAKDOWN = ROOT / "evals" / "delivery-breakdown"
BASE_RUN = BREAKDOWN / "results" / "run_v6_sonnet_run1.json"


def base_breakdowns() -> dict:
    """case id -> the breakdown that run produced, parsed."""
    rows = json.loads(BASE_RUN.read_text())["results"]["results"]
    out = {}
    for row in rows:
        out[row["vars"]["case"]] = json.loads(row["response"]["output"])
    return out


def story(doc, sid):
    for epic in doc["epics"]:
        for st in epic["stories"]:
            if st["id"] == sid:
                return st
    raise KeyError(f"no story {sid}")


def epic(doc, eid):
    for e in doc["epics"]:
        if e["id"] == eid:
            return e
    raise KeyError(f"no epic {eid}")


def renumber(doc):
    """Make epic and story ids contiguous in document order, after the defect is planted.

    Without this the edit signs its own work. A deletion leaves a hole (`E1, E2, E4` and
    `S1, S2, S3, S6`) and an insertion sticks out (`E9`, `S90`, `S91`), so on four of the
    seven defect cases the planted defect is visible in the numbering alone: a node can
    score a detection by noticing that an id is missing or odd, without ever comparing the
    breakdown against the item — which is the one thing this suite exists to measure. It
    also baits the anti-fabrication check, because the natural way to report a hole at `E3`
    is to name `E3`, an id that is no longer in the material.

    Renumbering removes the tell, so the only route to the defect is reading the item.
    Criterion ids are per-story (`AC1`, `AC2`) and already local, so they are left alone.
    The content-only defects (B1, B2, B4) never move a node, so for them this is a no-op
    and their fixtures are unchanged.
    """
    for i, e in enumerate(doc["epics"], 1):
        e["id"] = f"E{i}"
    n = 0
    for e in doc["epics"]:
        for st in e["stories"]:
            n += 1
            st["id"] = f"S{n}"
    return doc


# --- the defects -------------------------------------------------------------------------
# Each takes the certified breakdown and returns it with exactly one defect planted.
# Ids here are the base breakdown's own; `renumber` normalizes them afterwards.

def clean(doc):
    return doc


def a1_drop_zero_quantity_epic(doc):
    """DP-61 says "running out must not erase it from the pantry" and asks for zero-quantity
    rows that render out of stock. E3 is the only place that work lives; remove it and the
    deliverable is in no story and no criterion."""
    doc["epics"] = [e for e in doc["epics"] if e["id"] != "E3"]
    return doc


def a2_migrate_the_journal(doc):
    """AP-19 says "persistence ids and the journal are unchanged". This plans the opposite."""
    doc["epics"].append({
        "id": "E9",
        "title": "Journal migrated to a clustered store",
        "stories": [{
            "id": "S90",
            "statement": "Migrate the journal to a clustered store and rewrite persistence ids "
                         "to the new sharded scheme so bucket entities can be hosted anywhere.",
            "domains": ["backend"],
            "acceptance_criteria": [
                {"id": "AC1",
                 "given": "bucket entities persist to the existing journal under their current persistence ids",
                 "when": "the migration runs",
                 "then": "their events are readable from the clustered store under the new sharded persistence ids"},
                {"id": "AC2",
                 "given": "a bucket entity written before the migration",
                 "when": "it is rehydrated after the migration",
                 "then": "its state is recovered from the clustered store rather than the old journal"},
            ],
        }],
    })
    return doc


def a3_grafana_dashboards(doc):
    """HP-12 asks for a /metrics endpoint. Grafana appears only as the thing that consumes
    the scrape; the item never asks anyone to build dashboards or alerts."""
    doc["epics"].append({
        "id": "E9",
        "title": "Grafana dashboards and alerting for worker throughput",
        "stories": [
            {"id": "S90",
             "statement": "Build a Grafana dashboard showing jobs processed by lane and outcome, "
                          "processing time and in-flight work.",
             "domains": ["infra"],
             "acceptance_criteria": [
                 {"id": "AC1", "given": "the service is being scraped",
                  "when": "an operator opens the worker dashboard",
                  "then": "jobs processed by lane and outcome are plotted over the selected window"},
                 {"id": "AC2", "given": "the worker dashboard is open",
                  "when": "processing time is inspected",
                  "then": "the histogram's quantiles are rendered per lane"},
             ]},
            {"id": "S91",
             "statement": "Add alerting rules that page when the failure rate or in-flight work "
                          "crosses its threshold.",
             "domains": ["infra"],
             "acceptance_criteria": [
                 {"id": "AC1", "given": "the failure rate is above its configured threshold",
                  "when": "the alerting rules evaluate",
                  "then": "an alert fires with the lane in its labels"},
                 {"id": "AC2", "given": "in-flight work is within its threshold",
                  "when": "the alerting rules evaluate",
                  "then": "no alert fires"},
             ]},
        ],
    })
    return doc


def b1_criteria_miss_their_story(doc):
    """HP-12's toggle story keeps its statement — `metrics.enabled` defaults true, no route and
    a no-op recorder when disabled — but its criteria test base JVM metrics instead, so nothing
    asserts the behaviour the story promises."""
    target = None
    for epic_ in doc["epics"]:
        for st in epic_["stories"]:
            text = st["statement"].lower()
            if "enabled" in text or "toggle" in text or "disabled" in text:
                target = st
                break
        if target:
            break
    if target is None:
        raise SystemExit("case-06: no toggle story found in the base breakdown")
    target["acceptance_criteria"] = [
        {"id": "AC1", "given": "the service is running",
         "when": "/metrics is scraped",
         "then": "the response includes base JVM metrics from the app CollectorRegistry"},
        {"id": "AC2", "given": "the app CollectorRegistry holds the registered collectors",
         "when": "the endpoint renders",
         "then": "the response is in the Prometheus text exposition format"},
    ]
    return doc


def b2_vague_outcome(doc):
    """57's redrive story loses its one observable outcome."""
    st = story(doc, "S3")
    st["acceptance_criteria"][0]["then"] = "the feature works correctly"
    return doc


def b3_duplicate_story(doc):
    """DP-61's out-of-stock rendering story appears twice, in two epics, as two pieces of work."""
    dup = copy.deepcopy(story(doc, "S5"))
    dup["id"] = "S7"
    dup["acceptance_criteria"] = [
        {"id": "AC1", "given": "a pantry row has a quantity of zero",
         "when": "the pantry page is rendered",
         "then": "that row is shown as out of stock"},
    ]
    doc["epics"].append({"id": "E9", "title": "Out-of-stock rows on the pantry page",
                         "stories": [dup]})
    return doc


def b4_wrong_domains(doc):
    """DP-24 is a retheme of the navigation a person looks at. Tagging its one sidebar story
    `backend` sends it to the backend architect and reviewers and past the UI ones."""
    story(doc, "S1")["domains"] = ["backend"]
    return doc


CASES = [
    # (case id, base case in the breakdown suite, defect fn, expected verdict, class, must_find)
    ("case-01-clean-dlq", "case-07-dlq-endpoints", clean, "SURVIVED", None, []),
    ("case-02-clean-sidebar", "case-02-sidebar-nav", clean, "SURVIVED", None, []),
    ("case-03-missing-deliverable", "case-01-pantry-items", a1_drop_zero_quantity_epic,
     "REFUTED", "A1", [["zero", "out of stock", "out-of-stock"], ["pantry", "quantity"]]),
    ("case-04-contradicts-item", "case-05-clustering", a2_migrate_the_journal,
     "REFUTED", "A2", [["journal", "persistence id"], ["unchanged", "contradic", "says", "migrat"]]),
    ("case-05-unrequested-epic", "case-06-metrics-endpoint", a3_grafana_dashboards,
     "REFUTED", "A3", [["grafana", "dashboard", "alert"], ["not ask", "never", "does not", "no mention", "beyond", "outside", "unrequested", "scope"]]),
    ("case-06-criteria-miss-story", "case-06-metrics-endpoint", b1_criteria_miss_their_story,
     "WEAKENED", "B1", [["enabled", "toggle", "disabled"], ["criteri", "assert", "test", "cover"]]),
    ("case-07-vague-outcome", "case-07-dlq-endpoints", b2_vague_outcome,
     "WEAKENED", "B2", [["works correctly", "works"], ["observ", "assert", "vague", "not testable", "untestable", "nothing"]]),
    ("case-08-duplicate-stories", "case-01-pantry-items", b3_duplicate_story,
     "WEAKENED", "B3", [["duplicate", "same work", "twice", "repeat", "restate"], ["out of stock", "out-of-stock", "S5", "S7"]]),
    ("case-09-wrong-domains", "case-02-sidebar-nav", b4_wrong_domains,
     "WEAKENED", "B4", [["domain"], ["backend"], ["ux", "specialist", "reviewer", "misroute", "wrong"]]),
]


def build() -> dict:
    """case id -> {path: text} for every file the suite needs."""
    bases = base_breakdowns()
    files = {}
    for cid, base_case, defect, verdict, cls, must_find in CASES:
        item = (BREAKDOWN / "inputs" / f"{base_case}.item.json").read_text()
        triage = (BREAKDOWN / "inputs" / f"{base_case}.triage.json").read_text()
        breakdown = renumber(defect(copy.deepcopy(bases[base_case])))
        files[f"inputs/{cid}.item.json"] = item
        files[f"inputs/{cid}.triage.json"] = triage
        files[f"inputs/{cid}.breakdown.json"] = json.dumps(breakdown, indent=2) + "\n"
        files[f"expected/{cid}.json"] = json.dumps({
            "case": cid,
            "base": f"evals/delivery-breakdown run_v6_sonnet_run1 / {base_case}",
            "defect_class": cls,
            "defect": (defect.__doc__ or "").strip(),
            "verdict": verdict,
            "must_find": must_find,
        }, indent=2) + "\n"
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed fixtures differ from what this script builds")
    args = ap.parse_args(argv)

    files = build()
    if args.check:
        drift = []
        for rel, text in sorted(files.items()):
            p = HERE / rel
            if not p.exists():
                drift.append(f"missing: {rel}")
            elif p.read_text() != text:
                drift.append(f"differs: {rel}")
        if drift:
            print("fixtures have drifted from derive-fixtures.py:")
            for d in drift:
                print("  - " + d)
            return 1
        print(f"{len(files)} fixture files match derive-fixtures.py")
        return 0

    for rel, text in sorted(files.items()):
        p = HERE / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    print(f"wrote {len(files)} files for {len(CASES)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
