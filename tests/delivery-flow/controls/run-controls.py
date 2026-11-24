#!/usr/bin/env python3
"""Prove the three controls added by `add-review-step-and-size-limits` actually fire.

Usage:
    run-controls.py [--out <report.md>] [--only <probe>] [--keep]

Group 5 of that change asks for the controls to be confirmed in a real run rather than from
unit tests. This harness closes the part that does not need a model: it builds a fixture
delivery repo and drives the **real scripts** — `check-punch-out.py`, `check-test-scope.py`,
`flow-status.py` — over artifacts on disk, checking that each control fires and, just as
importantly, that it stays quiet when it should.

What this does **not** cover, and task 5.1/5.2 still own: a model-driven `full` run whose trace
shows `review` executed and its findings reached `pr-description`. That needs a session whose
cwd is the delivery repo, because `hooks/trace-step.py` records only then — a run orchestrated
from the toolkit produces no step records at all, which is why the existing runs on nx-neptune
are uncountable.

Both polarities, or a probe proves nothing: every control here has a fires case and a
stays-quiet case. A run where either set is empty is reported inconclusive.

Exit codes: 0 every probe as expected, 1 at least one unexpected, 2 a harness error.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
ITEM = "CTRL-1"

CONFIG = """profile: full
tracker:
  kind: local-markdown
  project: CTRL
forge:
  kind: github-pr
  base: main
artifacts:
  root: {root}
  commit: false
punch_out:
  max_diff_files: 3
  max_diff_lines: 50
  contract_paths: []
  protected_paths: []
allow_uncertified: [propose, review, vault-update, implementation, challenge-implementation]
"""

STORY = """# Story 1.1: A thing

Status: Draft

## Story
As a user, I want a thing, so that I benefit.

## Acceptance Criteria
- AC-1 (P0): Given a context, when an action, then an outcome.
- AC-2 (P1): Given another, when another, then another.
- AC-3 (P3): Given a nicety, when asked, then polished.

## Tasks / Subtasks
- [ ] do it (AC: 1, 2, 3)

## Dev Notes
- none

### References
- [Source: prd.md#FR-1]
"""


def sh(*args, cwd=None):
    return subprocess.run([str(a) for a in args], cwd=str(cwd) if cwd else None,
                          capture_output=True, text=True)


def build(base: Path) -> dict:
    """A fixture delivery repo with its artifact root outside it, as the real one is."""
    repo = base / "repo"
    root = base / "runs"
    (repo / ".git").mkdir(parents=True)
    root.mkdir()
    item_dir = root / ITEM
    item_dir.mkdir()

    sh("git", "init", "-q", "-b", "main", cwd=repo)
    sh("git", "config", "user.email", "t@t", cwd=repo)
    sh("git", "config", "user.name", "t", cwd=repo)
    (repo / ".delivery-flow.yaml").write_text(CONFIG.format(root=root))
    (repo / "prd.md").write_text("# PRD\n\n## FR-1\nA thing.\n")
    (repo / "story.md").write_text(STORY)
    (repo / "base.txt").write_text("one\n")
    sh("git", "add", "-A", cwd=repo)
    sh("git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base", cwd=repo)
    sh("git", "checkout", "-q", "-b", f"delivery/{ITEM}", cwd=repo)
    return {"base": base, "repo": repo, "root": root, "item_dir": item_dir}


def write(fx, name, doc):
    p = fx["item_dir"] / name
    p.write_text(json.dumps(doc, indent=2))
    return p


def sentinel(fx, name, step):
    return sh(sys.executable, SCRIPTS / "write-sentinel.py",
              fx["item_dir"] / name, "--step", step, cwd=fx["repo"])


def grow_diff(fx, files: int, lines: int):
    """Make the branch diff exceed or stay inside the ceilings, from real commits."""
    for i in range(files):
        (fx["repo"] / f"f{i}.txt").write_text("\n".join(f"line {n}" for n in range(lines)) + "\n")
    sh("git", "add", "-A", cwd=fx["repo"])
    sh("git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "work", cwd=fx["repo"])


def reset_diff(fx):
    sh("git", "checkout", "-q", "main", cwd=fx["repo"])
    sh("git", "branch", "-qD", f"delivery/{ITEM}", cwd=fx["repo"])
    sh("git", "checkout", "-q", "-b", f"delivery/{ITEM}", cwd=fx["repo"])


def review_doc(verdict, findings=(), diff_sha=None):
    return {
        "item": ITEM, "target": "implementation.json",
        "diff_sha256": diff_sha or hashlib.sha256(b"d").hexdigest(),
        "verdict": verdict,
        "reviewers": [{"agent": "clean-code-reviewer", "verdict": verdict}],
        "findings": [{"finding": f, "evidence": "f0.txt:1", "reviewer": "clean-code-reviewer",
                      "severity": "blocking"} for f in findings],
    }


# ---------------------------------------------------------------- the probes

def probe_review_schema_rejects_a_malformed_artifact(fx):
    """The edge must check review.json at all — the schema has to be reachable."""
    out = sh(sys.executable, SCRIPTS / "validate-artifact.py",
             write(fx, "review.json", {"item": ITEM, "verdict": "MAYBE"}), cwd=fx["repo"])
    ok = out.returncode != 0 and "verdict" in (out.stdout + out.stderr)
    return ok, {"exit": out.returncode, "said": (out.stdout + out.stderr).strip()[:300]}


def probe_review_schema_accepts_a_valid_artifact(fx):
    out = sh(sys.executable, SCRIPTS / "validate-artifact.py",
             write(fx, "review.json", review_doc("SURVIVED")), cwd=fx["repo"])
    return out.returncode == 0, {"exit": out.returncode,
                                 "said": (out.stdout + out.stderr).strip()[:200]}


def probe_size_ceiling_fires(fx):
    """A diff over either ceiling raises the punch-out, measured from real commits."""
    reset_diff(fx)
    grow_diff(fx, files=6, lines=40)
    out = sh(sys.executable, SCRIPTS / "check-punch-out.py", ITEM,
             "--step", "verify", "--repo", fx["repo"], "--json", "--dry-run", cwd=fx["repo"])
    body = out.stdout or "{}"
    ok = "diff-size" in body and "ceiling" in body
    return ok, {"exit": out.returncode, "mentions_diff_size": "diff-size" in body,
                "said": body.strip()[:400]}


def probe_size_within_ceiling_stays_quiet(fx):
    reset_diff(fx)
    grow_diff(fx, files=1, lines=3)
    out = sh(sys.executable, SCRIPTS / "check-punch-out.py", ITEM,
             "--step", "verify", "--repo", fx["repo"], "--json", "--dry-run", cwd=fx["repo"])
    body = out.stdout or "{}"
    fired = '"trigger": "diff-size"' in body
    return not fired, {"exit": out.returncode, "fired": fired, "said": body.strip()[:300]}


def probe_test_scope_rejects_an_uncovered_p0(fx):
    p = write(fx, "verify.json", {"story": "story.md",
                                  "tests": [{"name": "t", "covers": ["AC-2"]}]})
    out = sh(sys.executable, SCRIPTS / "check-test-scope.py", p, "--repo", fx["repo"])
    said = out.stdout + out.stderr
    return out.returncode == 1 and "AC-1 is P0" in said, {"exit": out.returncode,
                                                          "said": said.strip()[:300]}


def probe_test_scope_rejects_an_out_of_scope_p3(fx):
    """Direction two — the one this change exists for."""
    p = write(fx, "verify.json", {"story": "story.md",
                                  "tests": [{"name": "t", "covers": ["AC-1", "AC-2"]},
                                            {"name": "extra", "covers": ["AC-3"]}]})
    out = sh(sys.executable, SCRIPTS / "check-test-scope.py", p, "--repo", fx["repo"])
    said = out.stdout + out.stderr
    return out.returncode == 1 and "AC-3 is P3" in said, {"exit": out.returncode,
                                                          "said": said.strip()[:300]}


def probe_test_scope_accepts_the_right_scope(fx):
    p = write(fx, "verify.json", {"story": "story.md",
                                  "tests": [{"name": "t", "covers": ["AC-1", "AC-2"]}]})
    out = sh(sys.executable, SCRIPTS / "check-test-scope.py", p, "--repo", fx["repo"])
    return out.returncode == 0, {"exit": out.returncode,
                                 "said": (out.stdout + out.stderr).strip()[:200]}


def probe_a_weakened_review_blocks(fx):
    """The per-step policy, end to end through the real flow-status.

    `review` is declared `require-addressed` while the workflow default is `advance`, so this
    is also the check that the per-step key resolved at all — a nested block silently parsed as
    a sibling once, and the rule quietly did nothing.
    """
    write(fx, "review.json", review_doc("WEAKENED", findings=["a real defect"]))
    sentinel(fx, "review.json", "review")
    out = sh(sys.executable, SCRIPTS / "flow-status.py", ITEM, "--repo", fx["repo"], "--json",
             cwd=fx["repo"])
    doc = json.loads(out.stdout or "{}")
    blocked = doc.get("blocked") or ""
    return ("review.json" in blocked and "nothing has been addressed" in blocked), {
        "blocked": blocked[:300], "carry_forward": len(doc.get("carry_forward") or [])}


def probe_a_weakened_breakdown_still_advances(fx):
    """The certified triage chain's documented behaviour, unchanged by the per-step rule."""
    (fx["item_dir"] / "review.json").unlink(missing_ok=True)
    (fx["item_dir"] / "review.json.sentinel.json").unlink(missing_ok=True)
    write(fx, "challenge-breakdown.json", {
        "item": ITEM, "target": "breakdown.json", "verdict": "WEAKENED",
        "attacks": [{"attack": f"a{i}", "method": "m", "result": "failed"} for i in range(3)],
        "findings": [{"finding": "a note", "evidence": "e"}]})
    out = sh(sys.executable, SCRIPTS / "flow-status.py", ITEM, "--repo", fx["repo"], "--json",
             cwd=fx["repo"])
    doc = json.loads(out.stdout or "{}")
    blocked = doc.get("blocked") or ""
    return ("nothing has been addressed" not in blocked), {
        "blocked": blocked[:200] or "(not blocked on the verdict)",
        "carry_forward": len(doc.get("carry_forward") or [])}


PROBES = [
    ("review-schema-rejects-malformed", probe_review_schema_rejects_a_malformed_artifact,
     "validate-artifact refuses a review.json with a bad verdict"),
    ("review-schema-accepts-valid", probe_review_schema_accepts_a_valid_artifact,
     "a well-formed review.json validates"),
    ("size-ceiling-fires", probe_size_ceiling_fires,
     "a diff over the ceiling raises the diff-size punch-out"),
    ("size-within-ceiling-quiet", probe_size_within_ceiling_stays_quiet,
     "a diff inside the ceilings raises nothing"),
    ("scope-rejects-uncovered-p0", probe_test_scope_rejects_an_uncovered_p0,
     "an uncovered P0 fails the verify edge"),
    ("scope-rejects-out-of-scope-p3", probe_test_scope_rejects_an_out_of_scope_p3,
     "a test for a P3 fails the verify edge"),
    ("scope-accepts-right-scope", probe_test_scope_accepts_the_right_scope,
     "covering exactly P0 and P1 passes"),
    ("weakened-review-blocks", probe_a_weakened_review_blocks,
     "a WEAKENED review with an unchanged target blocks the flow"),
    ("weakened-breakdown-advances", probe_a_weakened_breakdown_still_advances,
     "a WEAKENED breakdown challenge still advances (certified chain unchanged)"),
]

FIRES = {"review-schema-rejects-malformed", "size-ceiling-fires", "scope-rejects-uncovered-p0",
         "scope-rejects-out-of-scope-p3", "weakened-review-blocks"}
QUIET = {"review-schema-accepts-valid", "size-within-ceiling-quiet",
         "scope-accepts-right-scope", "weakened-breakdown-advances"}


def report(results, inconclusive=""):
    ok = sum(1 for r in results if r["ok"])
    L = [
        "# The three controls, proven against the real scripts",
        "",
        f"Generated by `tests/delivery-flow/controls/run-controls.py` on "
        f"{time.strftime('%Y-%m-%d')}. Evidence for group 5 of "
        "`openspec/changes/add-review-step-and-size-limits/`.",
        "",
        f"**{ok} of {len(results)} probes as expected.**",
        "",
        "Each control is driven through the script that runs it in production — "
        "`check-punch-out.py`, `check-test-scope.py`, `flow-status.py`, `validate-artifact.py` "
        "— over artifacts on disk in a fixture delivery repo, with the diff built from real "
        "commits. Every control has a fires case and a stays-quiet case, because a probe that "
        "only ever sees one answer proves nothing about the other.",
        "",
    ]
    if inconclusive:
        L += [f"**Inconclusive: {inconclusive}**", ""]
    L += ["| Probe | Expected | Result |", "|---|---|---|"]
    for r in results:
        L.append(f"| `{r['probe']}` | {r['expect']} | "
                 f"{'as expected' if r['ok'] else '**UNEXPECTED**'} |")
    L += ["", "## What each probe saw", ""]
    for r in results:
        L += [f"### `{r['probe']}`", "", f"Expected: {r['expect']}", "",
              "```json", json.dumps(r["detail"], indent=2), "```", ""]
    L += [
        "## What this does not prove",
        "",
        "Tasks 5.1 and 5.2 remain open. There is no model-driven `full` run here, so nothing "
        "shows a trace in which `review` executed as a node and its findings reached "
        "`pr-description`. That needs a session whose cwd is the delivery repo — "
        "`hooks/trace-step.py` records only then, and a run orchestrated from the toolkit "
        "produces no step records at all, which is why the existing runs on nx-neptune are "
        "uncountable.",
        "",
        "**`full` remains outside any certified-only rate** (task 5.5). It carries `propose`, "
        "`review`, `implementation`, `challenge-implementation` and `vault-update` as "
        "uncertified nodes, so runs of it are not Stage 4 evidence and must not be counted as "
        "such. The certified chain is the `triage` profile, which none of these controls "
        "touch.",
        "",
    ]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(Path(__file__).parent / "controls-report.md"))
    ap.add_argument("--only", default="")
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args(argv)

    base = Path(tempfile.mkdtemp(prefix="controls-"))
    try:
        fx = build(base)
        selected = [p for p in PROBES if not args.only or p[0] == args.only]
        if not selected:
            print(f"no such probe: {args.only}", file=sys.stderr)
            return 2

        results = []
        for name, fn, expect in selected:
            try:
                ok, detail = fn(fx)
            except Exception as e:  # a harness error is never a pass
                ok, detail = False, {"harness_error": f"{type(e).__name__}: {e}"}
            results.append({"probe": name, "ok": ok, "expect": expect, "detail": detail})
            print(f"{'ok  ' if ok else 'FAIL'} {name}")

        ran = {r["probe"] for r in results}
        inconclusive = ""
        if ran & FIRES and not ran & QUIET:
            inconclusive = "only fires-probes ran; nothing shows a control staying quiet"
        elif ran & QUIET and not ran & FIRES:
            inconclusive = "only quiet-probes ran; nothing shows a control firing"

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
