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
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "workflow"))
from common import load_json, parse_mapping, repo_root  # noqa: E402
import descriptor as workflow_descriptor  # noqa: E402
import layout as workflow_layout  # noqa: E402


# Kinds whose step runs a model with a prompt, and so the only kinds a certification claim can
# be made about. `script`, `adapter` and `build` steps are deterministic producers with no
# prompt to certify. A `segment` is a container of nodes rather than a prompt of its own, but
# its certification is exactly its nodes' — so it answers the same way.
CERTIFIABLE_KINDS = {"node", "sdlc", "segment"}


def _step_roles() -> dict:
    """name -> `"node"` or `"deterministic"`, across *every* workflow the plugin declares.

    Read from the descriptors rather than from `flow-status.py`, which only ever knew
    delivery-flow's sixteen steps. With one workflow those are the same set; with two they are
    not, and the difference is not cosmetic — see `certification_role`, where an unrecognised
    step used to be waved through the certification claim.

    Two kinds of name go in, because a trace does not record what the routing table is keyed
    by. The sdlc table is keyed by *segment* (`readiness`), while `trace-step.py` records the
    *node* that ran (`readiness-review`); keying on the table alone left all eleven sdlc nodes
    unrecognised. Each segment's declared `nodes` are therefore mapped too.

    A name two workflows disagree about is dropped rather than arbitrated, so it falls to the
    unknown branch and refuses the claim. Guessing which workflow's table applies would be a
    coin flip inside the Stage 4 number. Note this is about disagreement on the *role*, not on
    the kind: delivery-flow calls its `implementation` step `sdlc` and the sdlc workflow calls
    its own `segment`, and since both are certifiable there is nothing to arbitrate.
    """
    roles, conflicting = {}, set()

    def put(name, role):
        if name in roles and roles[name] != role:
            conflicting.add(name)
        roles[name] = role

    for d in workflow_descriptor.active():
        for step in d.get("steps") or []:
            name, kind = step.get("step"), step.get("kind")
            if not name:
                continue
            put(name, "node" if kind in CERTIFIABLE_KINDS else "deterministic")
            # A segment's nodes are what the trace will actually name.
            for node in step.get("nodes") or []:
                put(node, "node")
    for name in conflicting:
        roles.pop(name, None)
    return roles


STEP_ROLES = _step_roles()


def _parse_registry(text: str) -> dict:
    """The registry format, parsed by `check-certification.py`'s own parser.

    Imported rather than reimplemented: two parsers for one file is how the gate and the report
    come to disagree about which steps are certified.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_certification_for_report",
        Path(__file__).resolve().parent / "check-certification.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_registry(text)


def segment_certification() -> dict:
    """`workflow -> {segment: {"nodes": [...], "certified": bool, "uncertified": [...]}}`.

    A segment is certified when *every* node in it is, because a chain is only as certified as
    its weakest link and a half-certified segment makes no claim at all.

    This is what keeps the report from promising a rate it has no evidence for. The sdlc
    pipeline is six segments and eleven nodes, of which section 5 certified two (`readiness` and
    `readiness-review`); the remaining nine are `certified: false` in the registry on purpose.
    An "end-to-end rate" over that pipeline would be a number about a chain whose links were
    never measured, so the report states the rate per *certified* segment and says plainly which
    segments are outside the claim.
    """
    out = {}
    for d in workflow_descriptor.active():
        registry_rel = d.get("registry")
        segments = {s.get("step"): list(s.get("nodes") or [])
                    for s in (d.get("steps") or []) if s.get("kind") == "segment"}
        if not registry_rel or not segments:
            continue
        path = workflow_descriptor.PLUGIN_ROOT / registry_rel
        try:
            entries = _parse_registry(path.read_text()).get("steps") or []
        except (OSError, ValueError, AttributeError):
            # Unreadable means unknown, and unknown is reported as such. Defaulting to
            # "certified" would manufacture the claim; defaulting to "uncertified" would
            # silently erase a real one.
            out[d["workflow"]] = {seg: {"nodes": nodes, "certified": None, "uncertified": []}
                                  for seg, nodes in segments.items()}
            continue
        flags = {e.get("step"): bool(e.get("certified")) for e in entries}
        out[d["workflow"]] = {}
        for seg, nodes in segments.items():
            uncertified = [n for n in nodes if not flags.get(n)]
            out[d["workflow"]][seg] = {"nodes": nodes, "certified": not uncertified,
                                       "uncertified": uncertified}
    return out

# Steps that legitimately have no routing-table entry and never will. Named one by one, because
# the whole point of the `unknown` branch below is that *not* being in the table is normally a
# reason to refuse the certification claim, not to grant it.
#
# `orchestrator` is the only member: `trace-step.py` records the conductor's own turns under
# that step — deliberately, because its cost is real — and they carry `certified: false`, since
# there is no registry entry for a conductor. It produces no artifact; `flow-status.py` computes
# the routing, so the conductor executes a decision rather than making one.
NOT_CERTIFIABLE_BY_DESIGN = {"orchestrator"}


def certification_role(step) -> str:
    """`"node"`, `"deterministic"` or `"unknown"` — what a `certified: false` here means.

    Three answers rather than two, because the two-answer version was wrong in the direction
    that inflates the number. It asked `ROUTING_KINDS.get(step) in CERTIFIABLE_KINDS`, and a
    step absent from the table answered `False` — identical to a deterministic producer — so an
    uncertified step the report had simply never heard of was *excluded* from the claim and the
    run still counted as certified. That was invisible while delivery-flow was the only
    workflow and its sixteen steps were the whole table. The moment a second workflow existed,
    every one of its nodes was an unknown step, and a `certified: false` on any of them would
    have been silently set aside — the certified-only rate asserting a certification nobody
    had made.

    So:

    - `node` — a model with a prompt (or a segment of them). `certified: false` disqualifies
      the run.
    - `deterministic` — a `script`, `adapter` or `build` step, or a member of
      `NOT_CERTIFIABLE_BY_DESIGN`. Nothing to certify; set aside, and named in the report as
      `excluded_from_certification`.
    - `unknown` — in no routing table, not a declared node of any segment, and not named as an
      exception. The report cannot say whether this needed certifying, so it does not claim the
      run was certified. Named separately as `unknown_steps`, because "set aside deliberately"
      and "not recognised" are different facts and reporting them in one bucket is how the
      first version hid this.

    **The deterministic exclusion is a claim a reviewer may reject**, so the report states it
    rather than applying it silently: the certified-only rate asserts every *node* in the chain
    was Stage 3 certified. If a reviewer wants the orchestrator inside the claim, the fix is to
    certify it, not to widen the denominator.
    """
    role = STEP_ROLES.get(step)
    if role:
        return role
    return "deterministic" if step in NOT_CERTIFIABLE_BY_DESIGN else "unknown"


def certifiable(step) -> bool:
    """Whether a `certified: false` on this step disqualifies the run. See `certification_role`.

    An unknown step disqualifies: the report will not grant a certification it cannot check.
    """
    return certification_role(step) != "deterministic"

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

    A root may be a repo opted into any workflow (whose `artifacts.root` says where its runs
    are, possibly outside itself) or an artifact root given directly. Both are accepted,
    because a report that only understood `<repo>/delivery/` stopped finding anything the
    moment the artifacts moved to the vault — and criterion 4's number comes from here.

    Every workflow, not just delivery-flow: this gated on `is_delivery_repo` and globbed a
    hard-coded `delivery/`, so pointed at an sdlc repo it found nothing. That failure is at
    least loud — `main` exits non-zero on no items rather than printing a 0% rate — but "no
    runs exist" and "this report cannot see the runs that exist" are different facts, and only
    one of them is true here.
    """
    root = Path(root)
    found = []
    for d in workflow_descriptor.for_repo(root):
        cfg = {}
        try:
            # `parse_mapping`, not `descriptor.parse`: this is a *repo* config, and only the
            # former reads the nested `artifacts: root:` the next line depends on. The
            # descriptor parser returned a flat mapping, so every absolute artifact root
            # silently fell back to `<repo>/<artifact_dir>` — which exists for no one who
            # configured a root outside the repo.
            cfg = parse_mapping((root / d["config_name"]).read_text())
        except (OSError, ValueError):
            pass
        base = workflow_layout.artifact_root(root, d["artifact_dir"], cfg)
        found += sorted(Path(base).glob("*/trace.jsonl"))
    # The in-repo default layout of each declared workflow, and the root given as an artifact
    # root directly. Kept as a fallback so a trace tree detached from its repo still reports.
    for artifact_dir in workflow_descriptor.artifact_dirs():
        found += sorted(root.glob(f"{artifact_dir}/*/trace.jsonl"))
    found += sorted(root.glob("*/trace.jsonl"))
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
        uncertified_nodes, excluded, unknown_steps = set(), set(), set()
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
                # Only a node's certification is a claim about the chain, and only a
                # *recognised* deterministic step may be set aside. See `certification_role`.
                role = certification_role(rec.get("step"))
                name = rec.get("step") or "?"
                if role == "deterministic":
                    excluded.add(name)
                else:
                    certified_all = False
                    (uncertified_nodes if role == "node" else unknown_steps).add(name)
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
                     # Self-test #7: "can you state the number of manually-corrected runs?"
                     # `outcome.json` has carried the evidence all along — artifact, traced
                     # sha, actual sha — and nothing read it, so the honest answer to a
                     # reviewer asking was "no". Counted per run and totalled below.
                     "manual_corrections": len(outcome.get("manual_corrections") or []),
                     "corrected_artifacts": sorted(
                         c.get("artifact", "?") for c in (outcome.get("manual_corrections") or [])),
                     "cost_usd": round(cost, 4), "priced": priced,
                     "certified": certified_all, "failed_edges": failed_edges,
                     "unchecked_edges": unchecked_edges,
                     # All three named, so the certification claim is auditable rather than
                     # asserted: which nodes broke it, what was set aside as having no prompt
                     # to certify, and what the report did not recognise at all. The third is
                     # separate because folding it into the second is how an unrecognised
                     # uncertified step came to look deliberately excluded.
                     "uncertified_nodes": sorted(uncertified_nodes),
                     "excluded_from_certification": sorted(excluded),
                     "unknown_steps": sorted(unknown_steps),
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
    # Self-test #7's answer as one number, over terminal runs only: an in-flight run has not
    # finished being corrected yet, so counting it would understate the rate.
    terminal = [r for r in rows if r["status"] in ("completed", "failed", "punched-out",
                                                   "abandoned")]
    corrected = [r for r in terminal if r["manual_corrections"]]
    corrections = {
        "terminal_runs": len(terminal),
        "runs_corrected": len(corrected),
        "artifacts_corrected": sum(r["manual_corrections"] for r in terminal),
        "rate": round(len(corrected) / len(terminal) * 100, 1) if terminal else None,
        "items": [{"item": r["item"], "artifacts": r["corrected_artifacts"]} for r in corrected],
    }

    return {"items": rows, "per_step": {k: dict(v) for k, v in per_step.items()},
            "per_model": {k: dict(v) for k, v in per_model.items()},
            "weekly": weeks, "per_profile": profiles, "non_conformant": nonconformant,
            "manual_corrections": corrections,
            # Which segments the rates above may be claimed for. Without this the per-profile
            # table reads as an end-to-end number for a pipeline whose segments are mostly
            # uncertified.
            "segment_certification": segment_certification(),
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

    mc = s["manual_corrections"]
    L += ["", "## Manually-corrected runs", "",
          "The certification's own wording: *hand-editing a validated artifact to get a step to "
          "pass is not a repair, it is a failed run.* Detected by comparing each artifact "
          "against the sha the trace recorded, so this is a measurement and not an attestation.",
          ""]
    if mc["terminal_runs"]:
        L.append(f"**{mc['runs_corrected']} of {mc['terminal_runs']} terminal runs** were "
                 f"corrected by hand ({mc['rate']}%), touching "
                 f"{mc['artifacts_corrected']} artifact(s).")
        for row in mc["items"]:
            L.append(f"- `{row['item']}` — {', '.join(row['artifacts'])}")
    else:
        L.append("No terminal runs yet, so there is no rate — which is not the same as zero.")

    uncert = sorted({n for r in s["items"] for n in r["uncertified_nodes"]})
    excl = sorted({e for r in s["items"] for e in r["excluded_from_certification"]})
    unknown = sorted({u for r in s["items"] for u in r["unknown_steps"]})
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
    if unknown:
        # Reported here and not folded into the line above, because the reader's question is
        # different: an unknown step is a hole in the report's own knowledge, and the fix is to
        # declare the step, not to argue about whether it needed certifying.
        L += [f"- **Uncertified steps this report does not recognise**, which also disqualify "
              f"their run: `{'`, `'.join(unknown)}`. Not in any workflow's routing table and "
              f"not a declared node of any segment, so the report cannot say whether they "
              f"needed certifying — and will not claim they did not."]
    if not excl and not uncert and not unknown:
        L += ["", "- Nothing was set aside, and no node was uncertified."]

    segs = s.get("segment_certification") or {}
    if segs:
        L += ["", "### Which segments these rates may be claimed for", "",
              "A segment is certified only when **every** node in it is: a chain is as "
              "certified as its weakest link. The rates below belong to the certified "
              "segments. **No end-to-end rate is asserted for a pipeline containing an "
              "uncertified segment** — that would be a number about links nobody measured."]
        for workflow, by_segment in sorted(segs.items()):
            done = sorted(k for k, v in by_segment.items() if v["certified"] is True)
            todo = sorted(k for k, v in by_segment.items() if v["certified"] is False)
            unknown_seg = sorted(k for k, v in by_segment.items() if v["certified"] is None)
            L += ["", f"**{workflow}**", ""]
            L += [f"- Certified segments: `{'`, `'.join(done)}`" if done
                  else "- Certified segments: none yet."]
            if todo:
                L += [f"- Not certified, and so outside any rate claimed here: "
                      f"`{'`, `'.join(todo)}`"]
            if unknown_seg:
                L += [f"- Certification **unknown** (its registry could not be read): "
                      f"`{'`, `'.join(unknown_seg)}`"]
            if done and todo:
                L += [f"- Therefore: a rate for `{'`, `'.join(done)}` is evidence; an "
                      f"end-to-end rate for {workflow} is not."]

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
