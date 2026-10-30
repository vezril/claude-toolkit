#!/usr/bin/env python3
"""Roll the traces up into the numbers Stage 4 asks for.

Usage:
    delivery-report.py [<root> ...] [--markdown out.md] [--csv out.csv] [--json]

Reads every `delivery/*/trace.jsonl` and `outcome.json` under the roots given (default: the
current repo) and reports:

  - per item: outcome, tokens, API-equivalent cost, where it ended;
  - per step and per model: token and cost distribution;
  - weekly end-to-end rate, both readings (see below);
  - steps that ran on a heavier model than their registry tier, with the extra cost;
  - the certified-only rate, which is the Stage 4 number.

Two readings of the rate, because which one the certification wants is still open:
  - *excluding punch-outs*: completed / (completed + failed), treating a human decision as a
    legitimate stop rather than a failure;
  - *counting punch-outs as unsuccessful*: completed / all terminal items.

Cost is `api_equivalent_cost_usd`: the step's tokens priced at published API list rates. Runs
under a subscription are not billed per token, so this is a comparison figure, not spend.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import artifact_root, is_delivery_repo, load_json, repo_root  # noqa: E402


def _routing_kinds() -> dict:
    """step -> its kind in the routing table, read from `flow-status.py` rather than repeated."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "flow_status_for_report", Path(__file__).resolve().parent / "flow-status.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {step: kind for _artifact, step, kind, _opt in mod.STEPS}


ROUTING_KINDS = _routing_kinds()

# Kinds whose step is a model with a prompt, and so the only kinds a certification claim can
# be made about. `script`, `adapter` and `build` steps are deterministic producers with no
# prompt to certify, and `orchestrator` is not in the routing table at all.
CERTIFIABLE_KINDS = {"node", "sdlc"}


def certifiable(step) -> bool:
    """Whether a `certified: false` on this step should disqualify the run.

    This is the fix for a number that could never exist. `trace-step.py` records the
    orchestrator's own turns as `step: "orchestrator"` — deliberately, because its cost is
    real — and those records carry `certified: false`, since there is no registry entry for a
    conductor and never will be. The run-level judgement was "every record certified", so
    every orchestrated run was disqualified, and the certified-only rate could only ever be
    0/0. DISCARDED-AN-3704 is the proof: a clean `triage`-profile run whose *only* uncertified
    step was the orchestrator.

    Deterministic steps fail it the same way. `report`, `verify`, `brief`, `intake` and the
    adapters have no prompt, which is exactly why `.delivery-flow.yaml` does not list them
    under `allow_uncertified` — and they were still recording `certified: false` and still
    disqualifying the run.

    **This is a claim a reviewer may reject**, so the report states it rather than applying it
    silently: the certified-only rate asserts that every *node* in the chain was Stage 3
    certified. A deterministic producer has no prompt to certify, and the orchestrator
    produces no artifact — `flow-status.py` computes the routing, so the conductor executes a
    decision rather than making one. If a reviewer wants the orchestrator inside the claim,
    the fix is to certify it, not to widen the denominator; `excluded_from_certification` in
    the report names exactly what was set aside.
    """
    return ROUTING_KINDS.get(step) in CERTIFIABLE_KINDS

TOKEN_FIELDS = ("input_tokens", "output_tokens", "cache_creation_tokens", "cache_read_tokens")


def iso_week(ts: str) -> str:
    try:
        d = datetime.fromisoformat(ts.replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        d = date.today()
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def trace_files(root: Path) -> list:
    """Every run's trace under this root, wherever its artifacts live.

    A root may be a delivery repo (whose `artifacts.root` says where its runs are, possibly
    outside itself) or an artifact root given directly. Both are accepted, because a report
    that only understood `<repo>/delivery/` stopped finding anything the moment the artifacts
    moved to the vault — and criterion 4's number comes from here.
    """
    root = Path(root)
    found = []
    if is_delivery_repo(root):
        found += sorted(artifact_root(root).glob("*/trace.jsonl"))
    found += sorted(root.glob("delivery/*/trace.jsonl"))   # the default layout
    found += sorted(root.glob("*/trace.jsonl"))            # an artifact root given directly
    seen, out = set(), []
    for f in found:
        key = str(f.resolve())
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def collect(roots) -> dict:
    items = {}
    for root in roots:
        for trace in trace_files(root):
            # The project's convention for a contaminated run is to rename its directory
            # `DISCARDED-*` and write down why. The report has to honour that, or a run
            # discarded for having false numbers keeps contributing those numbers — which is
            # exactly what it was discarded for.
            if trace.parent.name.startswith("DISCARDED-"):
                continue
            item_dir = trace.parent
            key = item_dir.name
            entry = items.setdefault(key, {"item": key, "repo": str(root), "records": [],
                                           "edges": [], "outcome": None})
            for line in trace.read_text().splitlines():
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                (entry["edges"] if rec.get("edge") else entry["records"]).append(rec)
            outcome, err = load_json(item_dir / "outcome.json")
            if not err:
                entry["outcome"] = outcome
    return items


def summarize(items: dict) -> dict:
    per_step, per_model, weekly = defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(int))
    # Per profile too: the Stage 4 number belongs to the certified chain, and mixing it with
    # runs of the whole pipeline reports neither honestly.
    per_profile = defaultdict(lambda: defaultdict(int))
    nonconformant, missing_pricing, rows = [], set(), []

    for key, entry in sorted(items.items()):
        tokens = {f: 0 for f in TOKEN_FIELDS}
        cost, priced, certified_all = 0.0, True, True
        uncertified_nodes, excluded = set(), set()
        for rec in entry["records"]:
            for f in TOKEN_FIELDS:
                tokens[f] += rec.get(f) or 0
            if rec.get("api_equivalent_cost_usd") is None:
                priced = False
                if rec.get("model"):
                    missing_pricing.add(rec["model"])
            else:
                cost += rec["api_equivalent_cost_usd"]
            if rec.get("certified") is False:
                # Only a node's certification is a claim about the chain. See `certifiable`.
                if certifiable(rec.get("step")):
                    certified_all = False
                    uncertified_nodes.add(rec.get("step") or "?")
                else:
                    excluded.add(rec.get("step") or "?")
            step = rec.get("step") or "?"
            per_step[step]["cost"] += rec.get("api_equivalent_cost_usd") or 0
            per_step[step]["input"] += rec.get("input_tokens") or 0
            per_step[step]["output"] += rec.get("output_tokens") or 0
            per_step[step]["runs"] += 1
            if rec.get("model"):
                per_model[rec["model"]]["cost"] += rec.get("api_equivalent_cost_usd") or 0
                per_model[rec["model"]]["runs"] += 1
            if rec.get("model_conformant") is False:
                nonconformant.append({"item": key, "step": step, "model": rec.get("model"),
                                      "declared": rec.get("declared_tier"),
                                      "cost": rec.get("api_equivalent_cost_usd") or 0})

        outcome = entry["outcome"] or {}
        status = outcome.get("status") or ("in-flight" if entry["records"] or entry["edges"] else "empty")
        failed_edges = sum(1 for e in entry["edges"] if (e.get("edge") or {}).get("exit"))
        # Artifacts that reached an edge with no schema to check them against. Counted
        # separately from failures because they are neither a pass nor a failure: nothing ran.
        # Rolling them into either number is how an unchecked artifact came to look checked.
        unchecked_edges = sum(1 for e in entry["edges"]
                              if (e.get("edge") or {}).get("name") == "no-schema")
        ts = (entry["records"] or entry["edges"] or [{}])[-1].get("ts", "")
        profile = outcome.get("profile") or "unknown"
        if status in ("completed", "failed", "punched-out", "abandoned"):
            weekly[iso_week(ts)][status] += 1
            per_profile[profile][status] += 1
            if certified_all:
                weekly[iso_week(ts)][f"certified:{status}"] += 1
                per_profile[profile][f"certified:{status}"] += 1

        rows.append({"item": key, "status": status, "profile": profile,
                     "step": outcome.get("step") or "",
                     "reason": outcome.get("reason") or "", **tokens,
                     "cost_usd": round(cost, 4), "priced": priced,
                     "certified": certified_all, "failed_edges": failed_edges,
                     "unchecked_edges": unchecked_edges,
                     # Both named, so the certification claim is auditable rather than
                     # asserted: which nodes broke it, and what was set aside as having no
                     # prompt to certify in the first place.
                     "uncertified_nodes": sorted(uncertified_nodes),
                     "excluded_from_certification": sorted(excluded),
                     "steps": len(entry["records"])})

    def rate(counts, prefix=""):
        done = counts.get(f"{prefix}completed", 0)
        failed = counts.get(f"{prefix}failed", 0)
        punched = counts.get(f"{prefix}punched-out", 0)
        excl = done / (done + failed) * 100 if (done + failed) else None
        incl = done / (done + failed + punched) * 100 if (done + failed + punched) else None
        return {"completed": done, "failed": failed, "punched_out": punched,
                "rate_excluding_punch_outs": excl, "rate_counting_punch_outs": incl}

    weeks = {w: {"all": rate(c), "certified_only": rate(c, "certified:")} for w, c in sorted(weekly.items())}
    # A profile with no terminal runs has no rate. Reporting it as 0% would read as "it never
    # works" when it means "nobody has run it", and those are opposite conclusions.
    profiles = {p: {"all": rate(c), "certified_only": rate(c, "certified:")}
                for p, c in sorted(per_profile.items())}
    return {"items": rows, "per_step": {k: dict(v) for k, v in per_step.items()},
            "per_model": {k: dict(v) for k, v in per_model.items()},
            "weekly": weeks, "per_profile": profiles, "non_conformant": nonconformant,
            "missing_pricing": sorted(missing_pricing)}


def markdown(s: dict, pricing_as_of: str) -> str:
    L = ["# Delivery flow report", "",
         f"Cost is **API-equivalent**: tokens priced at published API list rates"
         f"{f' (as of {pricing_as_of})' if pricing_as_of else ''}. Runs under a subscription are not "
         "billed per token, so this is a comparison figure, not spend.", "",
         "## Items", "",
         "| Item | Profile | Outcome | Steps | In | Out | Cost (API-equiv) | Certified | Failed edges | Unchecked |",
         "|------|---------|---------|-------|----|-----|------------------|-----------|--------------|-----------|"]
    for r in s["items"]:
        L.append(f"| {r['item']} | {r['profile']} | {r['status']}{(' — ' + r['reason']) if r['reason'] else ''} | {r['steps']} | "
                 f"{r['input_tokens']:,} | {r['output_tokens']:,} | "
                 f"{'$' + format(r['cost_usd'], '.4f') if r['priced'] else 'unpriced'} | "
                 f"{'yes' if r['certified'] else 'no'} | {r['failed_edges']} | {r['unchecked_edges']} |")

    uncert = sorted({n for r in s["items"] for n in r["uncertified_nodes"]})
    excl = sorted({e for r in s["items"] for e in r["excluded_from_certification"]})
    L += ["", "### What the certified-only rate claims", "",
          "It asserts that every **node** in the chain was Stage 3 certified. A deterministic "
          "producer has no prompt to certify, and the orchestrator produces no artifact — "
          "`flow-status.py` computes the routing, so the conductor executes a decision rather "
          "than making one. **This is a claim a reviewer may reject**, so what was set aside "
          "is named rather than assumed."]
    if excl:
        L += ["", f"- Set aside as having no prompt to certify: `{'`, `'.join(excl)}`"]
    if uncert:
        L += [f"- Uncertified **nodes**, which do disqualify their run: `{'`, `'.join(uncert)}`"]
    if not excl and not uncert:
        L += ["", "- Nothing was set aside, and no node was uncertified."]

    L += ["", "## Weekly end-to-end rate", "",
          "| Week | Completed | Failed | Punched out | Excluding punch-outs | Counting them | Certified-only (Stage 4) |",
          "|------|-----------|--------|-------------|----------------------|---------------|--------------------------|"]
    for week, v in s["weekly"].items():
        a, c = v["all"], v["certified_only"]
        pct = lambda x: "—" if x is None else f"{x:.1f}%"
        L.append(f"| {week} | {a['completed']} | {a['failed']} | {a['punched_out']} | "
                 f"{pct(a['rate_excluding_punch_outs'])} | {pct(a['rate_counting_punch_outs'])} | "
                 f"{pct(c['rate_excluding_punch_outs'])} |")

    L += ["", "## End-to-end rate by profile", "",
          "A profile with no terminal runs has no rate: that is not 0%, it is no evidence.", "",
          "| Profile | Completed | Failed | Punched out | Excluding punch-outs | Counting them | Certified-only (Stage 4) |",
          "|---------|-----------|--------|-------------|----------------------|---------------|--------------------------|"]
    pct = lambda x: "—" if x is None else f"{x:.1f}%"
    for profile, v in s["per_profile"].items():
        a, c = v["all"], v["certified_only"]
        L.append(f"| {profile} | {a['completed']} | {a['failed']} | {a['punched_out']} | "
                 f"{pct(a['rate_excluding_punch_outs'])} | {pct(a['rate_counting_punch_outs'])} | "
                 f"{pct(c['rate_excluding_punch_outs'])} |")
    if not s["per_profile"]:
        L.append("| — | 0 | 0 | 0 | — | — | — |")

    L += ["", "## Cost by step", "", "| Step | Runs | In | Out | Cost |", "|------|------|----|-----|------|"]
    for step, v in sorted(s["per_step"].items(), key=lambda kv: -kv[1]["cost"]):
        L.append(f"| {step} | {int(v['runs'])} | {int(v['input']):,} | {int(v['output']):,} | ${v['cost']:.4f} |")

    L += ["", "## Cost by model", "", "| Model | Runs | Cost |", "|-------|------|------|"]
    for model, v in sorted(s["per_model"].items(), key=lambda kv: -kv[1]["cost"]):
        L.append(f"| {model} | {int(v['runs'])} | ${v['cost']:.4f} |")

    if s["non_conformant"]:
        L += ["", "## Steps that ran above their tier", "",
              "| Item | Step | Ran on | Declared | Cost |", "|------|------|--------|----------|------|"]
        for n in s["non_conformant"]:
            L.append(f"| {n['item']} | {n['step']} | {n['model']} | {n['declared']} | ${n['cost']:.4f} |")
    if s["missing_pricing"]:
        L += ["", f"**Missing pricing** for: {', '.join(s['missing_pricing'])} — those steps are "
                  "counted in tokens but not in cost."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roots", nargs="*", default=["."])
    ap.add_argument("--markdown")
    ap.add_argument("--csv")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    # Climb to the repo root only when the path given is not already where the runs are.
    # Climbing unconditionally is what made this unable to read the real data: the artifact
    # root is `~/Amazon RAG/Atlas/RAG/_runs`, the vault is itself a git repo, so `repo_root`
    # resolved it to `~/Amazon RAG`, looked for `delivery/*/trace.jsonl` there, found none,
    # and reported "no delivery items found" over three runs sitting in the path it was
    # handed. `trace_files` already understood an artifact root given directly; it never saw
    # one, because this line rewrote the argument before it got there.
    roots = []
    for r in (args.roots or ["."]):
        given = Path(r)
        roots.append(given if trace_files(given) else repo_root(given))
    items = collect(roots)
    if not items:
        print("no delivery items found under: " + ", ".join(str(r) for r in roots), file=sys.stderr)
        return 1
    summary = summarize(items)

    from common import load_pricing
    as_of = load_pricing().get("meta", {}).get("as_of", "")

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        text = markdown(summary, as_of)
        print(text) if not args.markdown else Path(args.markdown).write_text(text)
        if args.markdown:
            print(f"wrote {args.markdown}")
    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(summary["items"][0].keys()))
            w.writeheader()
            w.writerows(summary["items"])
        print(f"wrote {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
