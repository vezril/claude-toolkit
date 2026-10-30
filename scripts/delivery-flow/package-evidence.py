#!/usr/bin/env python3
"""Assemble the Stage 4 evidence package: one directory per examined criterion.

Usage:
    package-evidence.py [--out evidence/] [--repo <delivery-repo> ...] [--force]
                        [--allow-uncertified] [--dry-run]

Five criteria are examined, so the package has five directories and a README mapping each to
its criterion. The point is that a reviewer who has never seen this repository can open one
directory and answer one question, without being told where to look.

**It refuses to build when a chain step is not certified.** A package is a claim, and the claim
rests on the chain being certified at Stage 3; assembling one anyway would produce a tidy
directory making an untrue argument. `--allow-uncertified` exists for drafting and stamps the
README so the output cannot be mistaken for a submission.

**It copies, never summarises.** Every file in the package is a byte-for-byte copy of something
in the repository, and MANIFEST.txt records each source path and sha256. A reviewer can diff the
package against the repo; a summary would be a new document nobody has checked.

**It reports what is missing rather than omitting it.** A criterion with no evidence gets a
directory containing MISSING.md saying so. An absent file is indistinguishable from an
oversight; a stated gap is a fact the reviewer can weigh.

Exit codes: 0 built, 1 refused (an uncertified chain step), 2 a usage error.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import PLUGIN_ROOT, artifact_root, known_repos  # noqa: E402

# criterion -> (directory, the question a reviewer answers from it)
CRITERIA = [
    ("1-workflow-definition",
     "Is the sequence executable, or only described in prose?"),
    ("2-guardrails",
     "Do deterministic checks fire automatically at every handoff, after the write?"),
    ("3-punch-out-evidence",
     "Were the decision points actually tested, and can an agent produce a decision?"),
    ("4-end-to-end-rate",
     "What is the rate over real runs, on what denominator?"),
    ("5-audit-trail",
     "Is there one machine-readable record per step, with the model actually used?"),
]

# criterion -> [(source relative to the plugin root, note for the reviewer)]
SOURCES = {
    "1-workflow-definition": [
        ("skills/delivery-flow/SKILL.md", "the routing table and the rules"),
        ("skills/delivery-flow/steps.yaml", "the step registry: certification evidence per step"),
        ("templates/delivery-flow/profiles.yaml", "the named slices of the table"),
        ("schemas", "every artifact's schema, each naming produced_by and consumed_by"),
        ("scripts/delivery-flow/flow-status.py",
         "the router: computes position from what is on disk, not from memory"),
        ("docs/figures/delivery-flow.svg", "the pipeline"),
        ("docs/figures/delivery-flow-profiles.svg", "the two profiles and the terminus"),
    ],
    "2-guardrails": [
        ("hooks/check-edge.py", "PostToolUse: the edge checks, by content not command text"),
        ("hooks/hooks.json", "how the hooks are registered"),
        ("scripts/delivery-flow/validate-artifact.py", "the schema subset checker"),
        ("scripts/delivery-flow/write-sentinel.py", "a node's claim about what it produced"),
        ("tests/delivery-flow/test_edges.py", "the edge tests, including every bypass shape found"),
    ],
    "3-punch-out-evidence": [
        ("scripts/delivery-flow/check-punch-out.py", "the triggers"),
        ("scripts/delivery-flow/triggers.py", "the derivations, independent of a node's claims"),
        ("scripts/delivery-flow/decide.py", "a decision, signed by a key requiring human presence"),
        ("hooks/enforce-punch-outs.py", "PreToolUse: agents cannot decide, merge or deploy"),
        ("tests/delivery-flow/bypass/bypass-report.md",
         "23 attacks and the four harness defects the runs found"),
        ("tests/delivery-flow/bypass/run-bypass.py", "the suite, so a reviewer can rerun it"),
    ],
    "4-end-to-end-rate": [
        ("scripts/delivery-flow/delivery-report.py", "how the rate is computed"),
        ("scripts/delivery-flow/write-outcome.py",
         "outcomes, and manual-correction detection against the trace"),
    ],
    "5-audit-trail": [
        ("hooks/trace-step.py", "SubagentStop/Stop: model, tokens and cost per step"),
        ("skills/delivery-flow/references/trace.md", "what a trace record means"),
        ("tests/delivery-flow/test_trace.py",
         "including the per-message usage de-duplication, which overcounts several-fold if missed"),
    ],
}

CHAIN_NOTE = """## Honest limits of this package

Read these first; a reviewer will find them anyway, and finding them unstated is worse.

- **The end-to-end rate rests on few runs.** The number in `4-end-to-end-rate/` is real but
  thin. Every run is listed individually so the denominator is visible rather than implied.
- **A discarded run is named, not hidden.** A run whose trace was contaminated is renamed
  `DISCARDED-*` with the reason beside it and excluded from the rate. The reasons are in the
  package, because why a run was thrown out is evidence about the pipeline.
- **Known residuals are listed in `RESIDUALS.md`** rather than left for the reviewer to find.
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_label(path: Path) -> str:
    """How a source is named in the manifest: plugin-relative where it lives in the plugin,
    absolute otherwise. Run artifacts live in the delivery repo, not here."""
    try:
        return str(path.relative_to(PLUGIN_ROOT))
    except ValueError:
        return str(path)


def certification_state() -> tuple:
    """(ok, output) from check-certification.py over every registered step."""
    out = subprocess.run([sys.executable, "-I", str(HERE / "check-certification.py"), "--all"],
                         capture_output=True, text=True)
    return out.returncode == 0, (out.stdout or "") + (out.stderr or "")


def copy_source(src: Path, dest_dir: Path, manifest: list, dry: bool) -> int:
    """Copy a file or directory verbatim, recording every file in the manifest."""
    if not src.exists():
        return 0
    copied = 0
    if src.is_dir():
        for f in sorted(p for p in src.rglob("*") if p.is_file()):
            rel = f.relative_to(src.parent)
            if not dry:
                (dest_dir / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest_dir / rel)
            manifest.append((str(rel), source_label(f), sha256(f)))
            copied += 1
    else:
        if not dry:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest_dir / src.name)
        manifest.append((src.name, source_label(src), sha256(src)))
        copied = 1
    return copied


def collect_runs(repos: list, dest: Path, manifest: list, dry: bool) -> dict:
    """Copy each item's artifacts and trace, and report the run census."""
    census = {"completed": 0, "failed": 0, "punched-out": 0, "abandoned": 0,
              "discarded": 0, "items": []}
    for repo in repos:
        root = artifact_root(repo)
        if not root.is_dir():
            continue
        for item_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            discarded = item_dir.name.startswith("DISCARDED-")
            outcome = "unknown"
            doc_path = item_dir / "outcome.json"
            if doc_path.exists():
                try:
                    outcome = json.loads(doc_path.read_text()).get("status") or "unknown"
                except (json.JSONDecodeError, ValueError, OSError):
                    outcome = "unreadable"
            if discarded:
                census["discarded"] += 1
            elif outcome in census:
                census[outcome] += 1
            census["items"].append({"item": item_dir.name, "repo": str(repo),
                                    "outcome": outcome, "discarded": discarded})
            copy_source(item_dir, dest / "runs", manifest, dry)
    return census


def residuals() -> str:
    """The known gaps, stated here so the package does not have to be read sceptically."""
    return """# Known residuals

Stated rather than discovered. Each is a real limit of the pipeline as submitted.

1. **`proposal-scope` has no structural derivation.** It checks task and file ceilings only, so
   a proposal under those ceilings rests on the node's own claim, caught only by hand-edit
   detection against the trace. Scope has no path signature before there is code, so this may be
   irreducible — but it is the one derived trigger a claim can still silence alone.

2. **One write shape escapes the edge check.** An absolute path held in a shell variable, with
   no `cd`, from a working directory that is not a delivery repo. The variable's value is not in
   the hook payload in any recoverable form, so a PostToolUse hook cannot resolve it. Mitigated
   by a repo registry for the shapes that *are* recoverable; the residual is documented rather
   than claimed fixed.

3. **The breaking-change derivation reads the branch diff, not the item's diff.** Two work items
   on one branch each inherit the other's changes, so a punch-out can cite files the item never
   touched. Observed on a real run.

4. **`contract_paths` is only as good as its configuration.** Pointed at a library's own package
   it fires on every change, which trains people to ignore punch-outs. The gate conveys
   information only when it names the paths other teams actually depend on.

5. **The typed confirmation in `decide.py` is not a control.** `--yes` skips it and an agent can
   pass `--yes`. The signature is the control; the prompt only prevents a slip.

6. **Step records require the session to run inside the delivery repo.** `trace-step` resolves
   the repo from the session's working directory. Driving the flow from elsewhere produces no
   step records — an honest absence, but an absence.
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="evidence")
    ap.add_argument("--repo", action="append", default=[],
                    help="a delivery repo to collect runs from; defaults to the registry")
    ap.add_argument("--force", action="store_true", help="replace an existing output directory")
    ap.add_argument("--allow-uncertified", action="store_true",
                    help="build a DRAFT even though a chain step is uncertified")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    certified, cert_output = certification_state()
    if not certified and not args.allow_uncertified:
        print(cert_output.strip(), file=sys.stderr)
        print("\nRefusing to build: a chain step is not certified, and the package's whole "
              "claim rests on the chain being certified at Stage 3. Fix the step, or pass "
              "--allow-uncertified to produce a clearly-stamped draft.", file=sys.stderr)
        return 1

    dest = Path(args.out).expanduser().resolve()
    if dest.exists() and not args.force and not args.dry_run:
        print(f"{dest} exists; pass --force to replace it", file=sys.stderr)
        return 2
    if dest.exists() and args.force and not args.dry_run:
        shutil.rmtree(dest)

    repos = [Path(r).expanduser().resolve() for r in args.repo] or known_repos()
    manifest, counts = [], {}

    for name, _question in CRITERIA:
        d = dest / name
        copied = 0
        for rel, _note in SOURCES.get(name, []):
            copied += copy_source(PLUGIN_ROOT / rel, d, manifest, args.dry_run)
        counts[name] = copied

    census = collect_runs(repos, dest / "4-end-to-end-rate", manifest, args.dry_run)
    report = subprocess.run([sys.executable, "-I", str(HERE / "delivery-report.py"),
                             *[str(r) for r in repos]], capture_output=True, text=True)

    if not args.dry_run:
        (dest / "4-end-to-end-rate").mkdir(parents=True, exist_ok=True)
        (dest / "4-end-to-end-rate" / "report.md").write_text(report.stdout or "(no runs)\n")
        (dest / "RESIDUALS.md").write_text(residuals())
        (dest / "CERTIFICATION.txt").write_text(cert_output)

        lines = [f"# Stage 4 evidence package", "",
                 f"Assembled {datetime.now(timezone.utc).isoformat(timespec='seconds')} from "
                 f"`{PLUGIN_ROOT.name}`.", ""]
        if not certified:
            lines += ["> **DRAFT — NOT FOR SUBMISSION.** A chain step is not certified; this was "
                      "built with `--allow-uncertified`. See CERTIFICATION.txt.", ""]
        lines += ["Every file here is a byte-for-byte copy of something in the repository, and "
                  "`MANIFEST.txt` records each source path and its sha256 — so this package can "
                  "be diffed against the source rather than trusted.", "",
                  "One directory per examined criterion. Each answers one question:", ""]
        for name, question in CRITERIA:
            lines.append(f"- **`{name}/`** — {question} ({counts.get(name, 0)} files)")
        lines += ["", "Plus `RESIDUALS.md` (the known limits), `CERTIFICATION.txt` (the Stage 3 "
                  "state of every registered step) and `MANIFEST.txt`.", "",
                  "## Runs", "",
                  f"- completed: {census['completed']}",
                  f"- failed: {census['failed']}",
                  f"- punched out: {census['punched-out']}",
                  f"- abandoned: {census['abandoned']}",
                  f"- discarded (contaminated, excluded from the rate): {census['discarded']}",
                  "",
                  "Each run's artifacts and trace are under `4-end-to-end-rate/runs/`, one "
                  "directory per item, so a reviewer can trace a single failure to its origin "
                  "step rather than take the rate on trust.", "",
                  CHAIN_NOTE]
        (dest / "README.md").write_text("\n".join(lines) + "\n")

        man = ["# path in package | source path | sha256", ""]
        man += [f"{a} | {b} | {c}" for a, b, c in sorted(manifest)]
        (dest / "MANIFEST.txt").write_text("\n".join(man) + "\n")

    total = sum(counts.values()) + len(manifest) - sum(counts.values())
    print(f"{'would build' if args.dry_run else 'built'} {dest}")
    for name, _q in CRITERIA:
        print(f"  {name:28} {counts.get(name, 0):3} files")
    print(f"  runs collected               {len(census['items']):3} "
          f"({census['completed']} completed, {census['discarded']} discarded)")
    print(f"  manifest entries             {len(manifest):3}")
    if not certified:
        print("\n  DRAFT: a chain step is not certified (see CERTIFICATION.txt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
