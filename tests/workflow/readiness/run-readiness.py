#!/usr/bin/env python3
"""Drive the certification gate for the sdlc `readiness` segment at runtime.

Task 5.6 left two claims unconfirmed. The gate agrees *statically* that both
`readiness` nodes are certified, but nothing had ever asked it the two questions
that matter while a run is happening:

  1. is delegation to a certified node actually permitted now?
  2. does editing a live node prompt re-block it?

`check-certification.py` is the gate, and until this harness existed **nothing
invoked it** — every reference to it in the tree was a doc or a unit test. A gate
with no caller is the same failure class section 6 and 7 kept finding: present,
successful, and checking nothing.

So this harness is the caller. It runs the real gate, unmodified, against a
fixture copy of the registry and the evidence it points at, and records what the
gate said.

**Why a fixture copy rather than the live tree.** Probes 2-4 edit a prompt in
order to prove the edit re-blocks the step. Editing the live
`skills/sdlc-orchestration/references/readiness.md` would un-certify the real
step, and a crash between the edit and the restore would leave the repository
that way — the harness that proves the gate works would have broken it. Nothing
here writes outside its temp directory.

**Both polarities, or the result is worthless.** A suite of "the gate said yes"
probes proves only that something returned zero. `uncertified-sibling-refused`
is the control: the same gate, same invocation, on a node with no evidence, which
must be refused. Probes 2-4 are the other direction — the gate must say no when
the prompt moves. A run where every probe reports the same polarity is reported
as inconclusive rather than as a pass.

Usage:
    run-readiness.py [--out <report.md>] [--keep] [--only <probe>]

Exit codes: 0 every probe as expected, 1 at least one unexpected, 2 harness error
(a missing gate script, an unparseable registry — never a skip).
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "scripts" / "delivery-flow" / "check-certification.py"
REGISTRY_REL = Path("skills") / "sdlc-orchestration" / "steps.yaml"

# The segment under test and the node the pipeline would delegate to first.
SEGMENT = "readiness"
NODES = ("readiness", "readiness-review")

# A node in another segment with no eval suite. The control: if this one is not
# refused, the gate is a yes-machine and every PASS above it means nothing.
UNCERTIFIED_CONTROL = "analysis"


def load_registry() -> dict:
    """Parse the registry with the gate's own parser, not a second copy of it.

    A harness that re-implements the parse can disagree with the gate about what
    the registry says, and then reports on a registry nobody runs.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_certification", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    text = (ROOT / REGISTRY_REL).read_text()
    return {e["step"]: e for e in mod.parse_registry(text).get("steps", [])}


def build_fixture(base: Path, reg: dict) -> Path:
    """Copy the registry and every path it points at into an isolated tree.

    `check-certification.py` resolves evidence relative to `repo_root(registry)`,
    which walks up looking for `.git`. The fixture gets an empty `.git` so that
    walk terminates inside the fixture instead of escaping to the real checkout —
    the whole isolation rests on that one directory existing.
    """
    fx = base / "fixture"
    (fx / ".git").mkdir(parents=True)

    shutil.copytree(ROOT / REGISTRY_REL.parent, fx / REGISTRY_REL.parent)

    # Only the certified nodes carry evidence paths; the uncertified ones bail on
    # missing registry fields before touching the filesystem, which is why the
    # control probe needs nothing copied for it.
    wanted = set()
    for node in NODES:
        e = reg[node]
        wanted.add(Path(e["prompt"]).parent)
        for key in ("certified_version", "results", "load_bearing", "iteration_log"):
            wanted.add(Path(e[key]).parent)
        for rp in e.get("consecutive_runs") or []:
            wanted.add(Path(rp).parent)

    for rel in sorted(wanted):
        src, dst = ROOT / rel, fx / rel
        if not src.exists() or dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst)
    return fx


def gate(fx: Path, step: str) -> tuple:
    """Run the real gate against the fixture. Returns (exit_code, output).

    A gate that is missing or that raises is a harness error, never a skip. Task
    4.5 made the same ruling for the edge checks and for the same reason: the
    code that runs the gates is the one place an inert gate must not return.
    """
    if not GATE.exists():
        raise SystemExit(f"harness error: gate not found at {GATE}")
    proc = subprocess.run(
        [sys.executable, str(GATE), step, "--registry", str(fx / REGISTRY_REL)],
        capture_output=True, text=True, cwd=str(fx),
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def edit(path: Path) -> None:
    """Append a line to a prompt — the smallest edit that moves its sha256.

    Appending rather than rewriting is deliberate: it proves the gate keys on the
    hash and not on some structural property of the text that a careful edit
    could preserve.
    """
    path.write_text(path.read_text() + "\nAn edit the suite never scored.\n")


# Each probe returns (ok, detail). `expect` is what the gate must say, and it is
# recorded in the report next to the result so a reader can see the probe had a
# way to fail.
def probe_delegation_permitted(fx: Path, reg: dict) -> tuple:
    """Both certified nodes clear the gate on an untouched tree."""
    out = {}
    for node in NODES:
        code, text = gate(fx, node)
        out[node] = {"exit": code, "said": text}
    ok = all(v["exit"] == 0 and v["said"].startswith("PASS") for v in out.values())
    return ok, out


def probe_live_prompt_edit_reblocks(fx: Path, reg: dict) -> tuple:
    """Editing `readiness`'s live prompt re-blocks it, naming the sha mismatch."""
    target = fx / reg["readiness"]["prompt"]
    original = target.read_text()
    try:
        edit(target)
        code, text = gate(fx, "readiness")
    finally:
        target.write_text(original)
    ok = code == 1 and "prompt changed since certification" in text
    restored, _ = gate(fx, "readiness")
    return (ok and restored == 0), {
        "exit": code, "said": text, "restored_exit": restored,
    }


def probe_review_prompt_edit_reblocks(fx: Path, reg: dict) -> tuple:
    """The same, for `readiness-review`, so probe 2 is not a single-node fluke."""
    target = fx / reg["readiness-review"]["prompt"]
    original = target.read_text()
    try:
        edit(target)
        code, text = gate(fx, "readiness-review")
    finally:
        target.write_text(original)
    ok = code == 1 and "prompt changed since certification" in text
    restored, _ = gate(fx, "readiness-review")
    return (ok and restored == 0), {
        "exit": code, "said": text, "restored_exit": restored,
    }


def probe_certified_version_edit_reblocks(fx: Path, reg: dict) -> tuple:
    """Editing the *frozen* copy re-blocks too, by a different rule.

    The live prompt's sha still matches `prompt_sha256` here, so the sha-mismatch
    rule stays silent and the `certified_version` comparison is what fires. Both
    rules exist because either file moving alone is a drift the other cannot see.
    """
    target = fx / reg["readiness"]["certified_version"]
    original = target.read_text()
    try:
        edit(target)
        code, text = gate(fx, "readiness")
    finally:
        target.write_text(original)
    ok = code == 1 and "differs from the certified version" in text
    return ok, {"exit": code, "said": text}


def probe_uncertified_sibling_refused(fx: Path, reg: dict) -> tuple:
    """The control. A node with no evidence must be refused by the same gate."""
    code, text = gate(fx, UNCERTIFIED_CONTROL)
    ok = code == 1 and "FAIL" in text
    return ok, {"exit": code, "said": text}


def probe_segment_claim(fx: Path, reg: dict) -> tuple:
    """`readiness` is certified end to end; no other segment is.

    Read from the registry's `certified:` flags rather than asserted here, so the
    probe tracks the file instead of a hand-copied answer that can go stale.
    """
    by_segment = {}
    for entry in reg.values():
        by_segment.setdefault(entry.get("segment"), []).append(bool(entry.get("certified")))
    certified = {s for s, flags in by_segment.items() if flags and all(flags)}
    ok = certified == {SEGMENT}
    return ok, {"certified_segments": sorted(certified),
                "all_segments": sorted(by_segment),
                "per_segment": {s: f"{sum(f)}/{len(f)} nodes" for s, f in sorted(by_segment.items())}}


PROBES = [
    ("delegation-permitted", probe_delegation_permitted,
     "both certified nodes exit 0 with PASS"),
    ("live-prompt-edit-reblocks", probe_live_prompt_edit_reblocks,
     "exit 1 naming the sha mismatch, and exit 0 again once restored"),
    ("review-prompt-edit-reblocks", probe_review_prompt_edit_reblocks,
     "exit 1 naming the sha mismatch, and exit 0 again once restored"),
    ("certified-version-edit-reblocks", probe_certified_version_edit_reblocks,
     "exit 1 naming the certified-version difference"),
    ("uncertified-sibling-refused", probe_uncertified_sibling_refused,
     "exit 1 with FAIL — the control"),
    ("segment-claim", probe_segment_claim,
     "readiness is the only fully certified segment"),
]

# Which probes assert the gate *permits* and which assert it *refuses*. A run
# where one of these sets is empty proves nothing about the other.
PERMITS = {"delegation-permitted"}
REFUSES = {"live-prompt-edit-reblocks", "review-prompt-edit-reblocks",
           "certified-version-edit-reblocks", "uncertified-sibling-refused"}


def report(results: list, inconclusive: str = "") -> str:
    ok = sum(1 for r in results if r["ok"])
    lines = [
        "# Readiness segment — runtime certification gate report",
        "",
        f"Generated by `tests/workflow/readiness/run-readiness.py` on "
        f"{time.strftime('%Y-%m-%d')}. Evidence for task 5.6 of "
        "`openspec/changes/certify-sdlc-pipeline/`.",
        "",
        f"**{ok} of {len(results)} probes as expected.**",
        "",
        "This answers the two questions task 5.6 left open: delegation to the "
        "certified `readiness` nodes is permitted at runtime, and editing either "
        "live prompt re-blocks its node. The gate is "
        "`scripts/delivery-flow/check-certification.py`, run unmodified against a "
        "fixture copy so no probe touches the live tree.",
        "",
    ]
    if inconclusive:
        lines += [f"**Inconclusive: {inconclusive}**", ""]
    lines += ["| Probe | Expected | Result |", "|---|---|---|"]
    for r in results:
        lines.append(f"| `{r['probe']}` | {r['expect']} | "
                     f"{'as expected' if r['ok'] else '**UNEXPECTED**'} |")
    lines += ["", "## What each probe saw", ""]
    for r in results:
        lines += [f"### `{r['probe']}`", "",
                  f"Expected: {r['expect']}", "",
                  "```json", json.dumps(r["detail"], indent=2), "```", ""]
    lines += [
        "## What this does not show",
        "",
        "The gate is a *delegation* check, not a run. These probes prove the "
        "`readiness` segment is unblocked and that prompt drift re-blocks it; they "
        "do not produce the readiness success rate, which task 7.5 owns and which "
        "only accumulates from real runs on real items. No end-to-end rate is "
        "claimed for the pipeline, and five of its six segments remain "
        "uncertified.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(Path(__file__).parent / "readiness-gate-report.md"))
    ap.add_argument("--only", default="", help="run one probe by name")
    ap.add_argument("--keep", action="store_true", help="keep the fixture for inspection")
    args = ap.parse_args(argv)

    reg = load_registry()
    for node in (*NODES, UNCERTIFIED_CONTROL):
        if node not in reg:
            print(f"harness error: {node} is not in {REGISTRY_REL}", file=sys.stderr)
            return 2

    base = Path(tempfile.mkdtemp(prefix="readiness-gate-"))
    try:
        fx = build_fixture(base, reg)
        selected = [p for p in PROBES if not args.only or p[0] == args.only]
        if not selected:
            print(f"no such probe: {args.only}", file=sys.stderr)
            return 2

        results = []
        for name, fn, expect in selected:
            ok, detail = fn(fx, reg)
            results.append({"probe": name, "ok": ok, "expect": expect, "detail": detail})
            print(f"{'ok  ' if ok else 'FAIL'} {name}")

        ran = {r["probe"] for r in results}
        inconclusive = ""
        if ran & PERMITS and not ran & REFUSES:
            inconclusive = ("only permit-probes ran, so nothing shows the gate can "
                            "refuse")
        elif ran & REFUSES and not ran & PERMITS:
            inconclusive = ("only refuse-probes ran, so nothing shows the gate can "
                            "permit")

        out = Path(args.out)
        out.write_text(report(results, inconclusive))
        Path(str(out).replace(".md", ".results.json")).write_text(
            json.dumps({"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "probes": results, "inconclusive": inconclusive}, indent=2) + "\n")
        print(f"\nreport: {out}")
        return 1 if any(not r["ok"] for r in results) else 0
    finally:
        if args.keep:
            print(f"fixture kept at {base}")
        else:
            shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
