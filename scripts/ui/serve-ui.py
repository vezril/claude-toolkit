#!/usr/bin/env python3
"""A local, read-only web UI for the workflows: the pipeline as a diagram, clickable per node.

Usage:
    serve-ui.py [--repo <delivery repo> ...] [--port 8787] [--no-browser]

Serves one page and two JSON endpoints on **127.0.0.1 only**. Structure comes from each
workflow's `workflow.yaml`, `steps.yaml` and profiles; statistics come from
`delivery-report.py --json` over the repos named with `--repo`.

## Security posture, stated rather than assumed

This opens a listening socket, so the choices are deliberate:

- **Bound to 127.0.0.1**, never `0.0.0.0`. Nothing on the network can reach it. The bind
  address is not configurable, because the only reason to make it configurable would be to
  expose it.
- **Read-only.** There is no endpoint that writes, and no path that reaches a script which
  does. Everything it serves is derived from files on disk by the same readers the flow uses.
- **No file serving.** The page is one fixed path resolved at import; nothing in a request
  reaches the filesystem, so there is no traversal surface.
- **No ticket prose.** `item.json` bodies, briefs, triage rationale and PR text are
  deliberately NOT exposed. The delivery repos here point at a client's tracker
  (`tracker.external: true`), and this plugin's own rule is that client content stays out of
  the public repo. The UI shows structure, certification and statistics — which is what the
  question "how is this pipeline doing" actually needs — so client text never reaches a
  socket at all.
- **No secrets.** Nothing reads the environment, and the config values surfaced are the
  structural ones (profile, artifact root, ceilings), never credentials.

If any of that needs to change, it is a security decision and belongs to a human, not to a
flag on this script.
"""

import argparse
import json
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parent.parent
PAGE = HERE / "assets" / "index.html"

# NOT in `scripts/workflow/`. That directory is the substrate and
# `tests/workflow/test_substrate_shims.py` enforces that nothing in it mentions a specific
# workflow — correctly, since a substrate module that knows about delivery-flow is how a second
# workflow ends up priced off the first one's rates. This UI reads BOTH workflows and calls
# `check-certification.py` and `delivery-report.py`, which still live under
# `scripts/delivery-flow/`. So it is neither substrate nor one workflow's own, and it lives
# here rather than being contorted to hide a dependency it really has.
# Explicit, not relative to HERE. These pointed at `HERE` while this file lived in
# `scripts/workflow/`; moving it out of the substrate silently broke the import, and the tests
# did not catch it because they load the module with those paths already present. A script that
# cannot run as a script is only caught by running it, which `test_it_starts_as_a_script` now
# does.
sys.path.insert(0, str(PLUGIN_ROOT / "scripts" / "workflow"))
sys.path.insert(0, str(PLUGIN_ROOT / "scripts" / "delivery-flow"))

import descriptor as workflow_descriptor  # noqa: E402

# The bind address is a constant on purpose. See the module docstring.
BIND = "127.0.0.1"

WORKFLOWS = [
    ("delivery-flow", PLUGIN_ROOT / "skills" / "delivery-flow" / "workflow.yaml"),
    ("sdlc", PLUGIN_ROOT / "skills" / "sdlc-orchestration" / "workflow.yaml"),
]


def _registry(path: Path) -> dict:
    """step -> registry entry, via check-certification's own parser.

    Reusing that parser rather than a second one: a UI that disagreed with the gate about
    which steps are certified would be worse than no UI.
    """
    import importlib.util
    gate = PLUGIN_ROOT / "scripts" / "delivery-flow" / "check-certification.py"
    spec = importlib.util.spec_from_file_location("check_certification", gate)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not path.exists():
        return {}
    return {e["step"]: e for e in mod.parse_registry(path.read_text()).get("steps", [])}


def _profiles(path: Path) -> list:
    """`load_profiles` takes a **path**, not text — passing text returned an empty list and
    the UI showed every workflow as having no profiles."""
    if not path.exists():
        return []
    import importlib.util
    common_path = PLUGIN_ROOT / "scripts" / "delivery-flow" / "common.py"
    spec = importlib.util.spec_from_file_location("df_common", common_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        return mod.load_profiles(path)
    except Exception:
        return []


def _gate(step: str, registry_rel: str) -> dict:
    """What `check-certification.py` says about one step. The single source of truth.

    **Not the registry's `certified:` field.** delivery-flow's certified steps do not carry
    that field at all — certification there is the evidence (`prompt_sha256`, `results`,
    `load_bearing`, …) clearing the gate, and only `review` declares `certified: false`
    explicitly. Reading the flag showed delivery-flow as having nothing certified, which is
    the opposite of true and exactly the kind of confidently-wrong display worth avoiding.
    """
    gate = PLUGIN_ROOT / "scripts" / "delivery-flow" / "check-certification.py"
    out = subprocess.run([sys.executable, "-I", str(gate), step, "--registry", registry_rel],
                         cwd=str(PLUGIN_ROOT), capture_output=True, text=True)
    said = ((out.stdout or "") + (out.stderr or "")).strip()
    if "not in the registry" in said:
        return {"state": "not-registered", "detail": said[:300]}
    return {"state": "certified" if out.returncode == 0 else "uncertified",
            "detail": said[:400]}


def structure() -> dict:
    """Both workflows: their routing table, registry evidence and profiles."""
    out = {}
    for name, wf_path in WORKFLOWS:
        if not wf_path.exists():
            continue
        desc = workflow_descriptor.load(wf_path)
        reg = _registry(PLUGIN_ROOT / (desc.get("registry") or ""))
        profiles = _profiles(PLUGIN_ROOT / (desc.get("profiles") or ""))
        registry_rel = desc.get("registry") or ""
        steps = []
        for artifact, step, kind, optional_when in workflow_descriptor.step_table(desc):
            e = reg.get(step) or {}
            gate = _gate(step, registry_rel) if e else {"state": "not-registered",
                                                        "detail": "no registry entry: a "
                                                                  "script or adapter, which "
                                                                  "has no prompt to certify"}
            steps.append({
                "step": step, "artifact": artifact, "kind": kind,
                "optional_when": optional_when,
                # From the gate, not from a flag. Three states that must stay distinct:
                # certified, uncertified, and not-registered (a script or adapter with no
                # prompt to certify) — collapsing the last two would report every
                # deterministic step as a certification failure.
                "gate": gate["state"],
                "gate_detail": gate["detail"],
                "declared_uncertified": e.get("certified") is False,
                "in_registry": bool(e),
                "chain": bool(e.get("chain")),
                "tier": e.get("tier"),
                "agent": e.get("agent"),
                "prompt": e.get("prompt"),
                "eval": e.get("eval"),
                "criteria": e.get("criteria") or [],
                "consecutive_runs": len(e.get("consecutive_runs") or []),
                "known_residual": e.get("known_residual"),
                "nodes": e.get("nodes") or [],
            })
        out[name] = {
            "workflow": name,
            "config_name": desc.get("config_name"),
            "artifact_dir": desc.get("artifact_dir"),
            "edge_checks": desc.get("edge_checks") or {},
            "verdict_policy": desc.get("verdict_policy") or {},
            "punch_out": desc.get("punch_out") or {},
            "steps": steps,
            "profiles": [{"profile": p.get("profile"), "terminus": p.get("terminus"),
                          "next": p.get("next"), "steps": p.get("steps") or []}
                         for p in profiles],
        }
    return out


def runs(repos: list) -> dict:
    """`delivery-report.py --json` over the given repos, or an explicit empty answer.

    A report that cannot be produced is reported as an error, not as zero runs: "no data" and
    "I could not read the data" are different answers, and this project has already shipped
    one number that conflated them.
    """
    if not repos:
        return {"available": False,
                "reason": "no --repo given, so no run statistics were requested"}
    script = PLUGIN_ROOT / "scripts" / "delivery-flow" / "delivery-report.py"
    out = subprocess.run([sys.executable, "-I", str(script), "--json"],
                         cwd=str(repos[0]), capture_output=True, text=True)
    if not (out.stdout or "").strip():
        return {"available": False,
                "reason": ((out.stderr or "").strip() or "the report produced no output")[:400]}
    try:
        return {"available": True, "report": json.loads(out.stdout)}
    except json.JSONDecodeError as e:
        return {"available": False, "reason": f"the report did not return JSON: {e}"}


class Handler(BaseHTTPRequestHandler):
    repos: list = []

    def _send(self, code, body, ctype):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        # Nothing here is meant to be embedded or framed elsewhere.
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self' 'unsafe-inline'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        route = self.path.split("?", 1)[0].rstrip("/") or "/"
        if route == "/":
            if not PAGE.exists():
                return self._send(500, f"missing page asset: {PAGE}", "text/plain")
            return self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if route == "/api/structure":
            return self._send(200, json.dumps(structure()), "application/json")
        if route == "/api/runs":
            return self._send(200, json.dumps(runs(self.repos)), "application/json")
        # Everything else is a 404 with no filesystem lookup: there is no static route, so a
        # request cannot name a path.
        return self._send(404, "not found", "text/plain")

    def log_message(self, fmt, *args):
        sys.stderr.write(f"  {self.address_string()} {fmt % args}\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", action="append", default=[],
                    help="a delivery repo to read run statistics from; repeatable")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args(argv)

    repos = []
    for r in args.repo:
        p = Path(r).expanduser().resolve()
        if not p.exists():
            print(f"no such repo: {p}", file=sys.stderr)
            return 2
        repos.append(p)
    Handler.repos = repos

    if not PAGE.exists():
        print(f"page asset missing: {PAGE}", file=sys.stderr)
        return 2

    srv = ThreadingHTTPServer((BIND, args.port), Handler)
    url = f"http://{BIND}:{args.port}/"
    print(f"workflow UI on {url}  (bound to {BIND} only; read-only; no ticket prose)")
    print(f"  structure: both workflows from their descriptors")
    print(f"  statistics: {', '.join(str(r) for r in repos) if repos else '(none — pass --repo)'}")
    print("  Ctrl-C to stop")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
