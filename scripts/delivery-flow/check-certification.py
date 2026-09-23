#!/usr/bin/env python3
"""Check that a delivery-flow step clears the Stage 3 bar.

Usage:
    check-certification.py <step> [--registry skills/delivery-flow/steps.yaml]
    check-certification.py --all

Each step in the registry must have:
  - at least 3 distinct criteria, each present as a metric in the certified results;
  - a certified results file (promptfoo -o output) scoring >= 95% of asserts for the
    step's declared tier, with no unscored provider errors;
  - a declared tier of haiku or sonnet, or escalation evidence (a results file showing
    the same suite below 95% on sonnet) for anything heavier;
  - a prompt whose current sha256 equals the recorded prompt_sha256, and equals the
    certified version file;
  - results actually produced with that certified prompt (every scored row's rendered
    prompt contains it), so an older run's scores can't certify an edited prompt;
  - a load-bearing map mapping at least 90% of the prompt's instructions to a criterion;
  - an iteration log with at least 2 iterations, each stating baseline, hypothesis,
    change, result and reasoning.

Exit codes: 0 all checked steps certified, 1 at least one unmet condition, 2 usage error.
Paths in the registry are relative to the repository root.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # used when available
except ImportError:  # the registry format is simple enough to parse without it
    yaml = None

BAR = 0.95
LOAD_BEARING_BAR = 0.90
ALLOWED_TIERS = {"haiku", "sonnet"}
LOG_LABELS = ("baseline", "hypothesis", "change", "result", "reasoning")


def _scalar(v: str):
    v = v.strip()
    if v in ("", "null", "~"):
        return None
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
    if (v[0] == v[-1]) and v[0] in "'\"" and len(v) >= 2:
        return v[1:-1]
    return v


def parse_registry(text: str) -> dict:
    """Parse the registry without PyYAML. Supported subset (the only one steps.yaml uses):
    a top-level `steps:` list of flat mappings whose values are scalars, quoted strings,
    null, or inline lists like [a, b]. Comments and blank lines are ignored."""
    if yaml is not None:
        return yaml.safe_load(text) or {}
    steps, cur = [], None
    for raw in text.splitlines():
        line = raw.split(" #")[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip() or line.strip() == "steps:":
            continue
        m = re.match(r"^\s*-\s+(\w+):\s*(.*)$", line)
        if m:
            cur = {m.group(1): _scalar(m.group(2))}
            steps.append(cur)
            continue
        m = re.match(r"^\s+(\w+):\s*(.*)$", line)
        if m and cur is not None:
            cur[m.group(1)] = _scalar(m.group(2))
            continue
        raise ValueError(f"unsupported registry line: {raw!r}")
    return {"steps": steps}


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    return start


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prompt_mismatches(results_path: Path, tier: str, certified_text: str) -> int:
    """Rows for `tier` whose rendered prompt does not contain the certified prompt text.
    This binds a results file to the exact prompt that produced it, so an older run's
    scores can't certify an edited prompt."""
    data = json.loads(results_path.read_text())
    bad = 0
    for row in data.get("results", {}).get("results", []):
        label = (row.get("provider") or {}).get("label") or (row.get("provider") or {}).get("id")
        if label != tier:
            continue
        raw = (row.get("prompt") or {}).get("raw", "") if isinstance(row.get("prompt"), dict) else str(row.get("prompt", ""))
        if certified_text not in raw:
            bad += 1
    return bad


def score(results_path: Path, tier: str):
    """Return (passed, total, metrics_seen, unscored_errors) for provider label == tier."""
    data = json.loads(results_path.read_text())
    rows = data.get("results", {}).get("results", [])
    passed = total = errors = 0
    metrics = set()
    for row in rows:
        label = (row.get("provider") or {}).get("label") or (row.get("provider") or {}).get("id")
        if label != tier:
            continue
        grading = row.get("gradingResult")
        if not grading:
            errors += 1
            continue
        for comp in grading.get("componentResults") or []:
            metric = (comp.get("assertion") or {}).get("metric")
            if metric:
                metrics.add(metric)
            total += 1
            passed += 1 if comp.get("pass") else 0
    return passed, total, metrics, errors


def load_bearing_ratio(path: Path):
    rows = [l for l in path.read_text().splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
    if not rows:
        return 0, 0
    mapped = 0
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        serves = cells[2].lower() if len(cells) > 2 else ""
        if serves and serves not in {"none", "-", "—", "n/a"}:
            mapped += 1
    return mapped, len(rows)


def complete_iterations(path: Path) -> int:
    sections = re.split(r"(?m)^## ", path.read_text())
    count = 0
    for sec in sections:
        low = sec.lower()
        if all(re.search(r"\*\*" + lab + r":\*\*", low) for lab in LOG_LABELS):
            count += 1
    return count


def check_step(entry: dict, root: Path) -> list:
    problems = []
    name = entry.get("step", "?")
    req = ["prompt", "tier", "results", "prompt_sha256", "criteria", "iteration_log", "load_bearing", "certified_version"]
    missing = [k for k in req if not entry.get(k)]
    if missing:
        return [f"missing registry fields: {', '.join(missing)}"]

    criteria = entry["criteria"]
    if len(set(criteria)) < 3:
        problems.append(f"{len(set(criteria))} distinct criteria (need >= 3)")

    tier = entry["tier"]
    if tier not in ALLOWED_TIERS:
        ev = entry.get("escalation_evidence")
        if not ev or not (root / ev).exists():
            problems.append(f"tier {tier} is above sonnet and has no escalation_evidence results file")
        else:
            p, t, _, _ = score(root / ev, "sonnet")
            if t and p / t >= BAR:
                problems.append(f"escalation evidence shows sonnet at {p}/{t} ({100 * p / t:.1f}%), which already clears the bar")

    prompt = root / entry["prompt"]
    version = root / entry["certified_version"]
    for label, path in (("prompt", prompt), ("certified_version", version)):
        if not path.exists():
            problems.append(f"{label} file not found: {path.relative_to(root)}")
    if prompt.exists():
        current = sha256(prompt)
        if current != entry["prompt_sha256"]:
            problems.append(f"prompt changed since certification: sha256 {current[:12]}… != recorded {str(entry['prompt_sha256'])[:12]}… (re-run the suite)")
        if version.exists() and current != sha256(version):
            problems.append(f"prompt differs from the certified version {entry['certified_version']}")

    results = root / entry["results"]
    if not results.exists():
        problems.append(f"results file not found: {entry['results']}")
    else:
        p, t, metrics, errors = score(results, tier)
        if t == 0:
            problems.append(f"no scored asserts for tier {tier} in {entry['results']}")
        else:
            pct = p / t
            if pct < BAR:
                problems.append(f"{p}/{t} asserts ({100 * pct:.1f}%) against the {int(BAR * 100)}% bar")
        if errors:
            problems.append(f"{errors} unscored provider error(s) for tier {tier}")
        if version.exists():
            bad = prompt_mismatches(results, tier, version.read_text().strip())
            if bad:
                problems.append(f"{bad} result row(s) were not produced with the certified prompt {entry['certified_version']}")
        absent = [c for c in criteria if c not in metrics]
        if absent:
            problems.append(f"criteria not found as metrics in results: {', '.join(absent)}")

    lb = root / entry["load_bearing"]
    if not lb.exists():
        problems.append(f"load-bearing map not found: {entry['load_bearing']}")
    else:
        m, n = load_bearing_ratio(lb)
        if n == 0 or m / n < LOAD_BEARING_BAR:
            problems.append(f"load-bearing {m}/{n} instructions (need >= {int(LOAD_BEARING_BAR * 100)}%)")

    log = root / entry["iteration_log"]
    if not log.exists():
        problems.append(f"iteration log not found: {entry['iteration_log']}")
    else:
        k = complete_iterations(log)
        if k < 2:
            problems.append(f"iteration log has {k} complete iteration(s) (need >= 2 with baseline, hypothesis, change, result, reasoning)")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--registry", default="skills/delivery-flow/steps.yaml")
    args = ap.parse_args(argv)
    if not args.step and not args.all:
        ap.print_usage(sys.stderr)
        return 2

    root = repo_root(Path.cwd())
    reg_path = root / args.registry
    if not reg_path.exists():
        print(f"registry not found: {args.registry}", file=sys.stderr)
        return 2
    entries = parse_registry(reg_path.read_text()).get("steps", [])
    if args.step:
        entries = [e for e in entries if e.get("step") == args.step]
        if not entries:
            print(f"{args.step}: not in the registry ({args.registry})")
            return 1

    failed = 0
    for entry in entries:
        problems = check_step(entry, root)
        if problems:
            failed += 1
            print(f"FAIL {entry.get('step')}")
            for p in problems:
                print(f"  - {p}")
        else:
            p, t, _, _ = score(root / entry["results"], entry["tier"])
            m, n = load_bearing_ratio(root / entry["load_bearing"])
            k = complete_iterations(root / entry["iteration_log"])
            print(f"PASS {entry['step']}: {entry['tier']} {p}/{t} ({100 * p / t:.1f}%), "
                  f"{len(set(entry['criteria']))} criteria, load-bearing {m}/{n}, {k} iterations")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
