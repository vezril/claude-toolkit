"""Shared helpers for delivery-flow scripts and hooks. Standard library only.

Everything here answers one of four questions: where is the repo, is this a
delivery-flow repo at all, which artifact is this path, and what does its schema say.
"""

import hashlib
import json
import os
import re
from pathlib import Path

CONFIG_NAME = ".delivery-flow.yaml"
SENTINEL_SUFFIX = ".sentinel.json"
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parents[2]))
SCHEMA_DIR = PLUGIN_ROOT / "schemas"

# delivery/<ITEM-KEY>/<artifact>, the only place artifacts live.
ARTIFACT_RE = re.compile(r"(?:^|/)delivery/([A-Za-z0-9][A-Za-z0-9._-]*)/([A-Za-z0-9][A-Za-z0-9._-]*)$")


def repo_root(start: Path) -> Path:
    start = start.resolve()
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    return start


def is_delivery_repo(path: Path) -> bool:
    """A delivery-flow repo has the config at its root. Everything is inert otherwise."""
    return (repo_root(path) / CONFIG_NAME).exists()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_artifact_path(path):
    """Return (item_key, filename) for a path inside delivery/<ITEM>/, else (None, None)."""
    m = ARTIFACT_RE.search(str(path).replace(os.sep, "/"))
    return (m.group(1), m.group(2)) if m else (None, None)


def load_schemas(schema_dir: Path = None) -> dict:
    """Map artifact file name -> schema. The sentinel schema is keyed by its suffix."""
    schema_dir = schema_dir or SCHEMA_DIR
    out = {}
    for p in sorted(schema_dir.glob("*.schema.json")):
        schema = json.loads(p.read_text())
        schema["_path"] = str(p)
        out[schema["artifact"]] = schema
    return out


def schema_for(filename: str, schemas: dict):
    if filename.endswith(SENTINEL_SUFFIX):
        return schemas.get("*.sentinel.json")
    return schemas.get(filename)


def count_expr(doc, expr: str) -> int:
    """Evaluate a count expression: 'epics[]' or 'epics[].stories[]'.

    Each '<key>[]' segment descends into a list; the result is the number of items at
    the deepest level, summed across the branches above it.
    """
    parts = [p for p in expr.split(".") if p]
    nodes = [doc]
    total = 0
    for i, part in enumerate(parts):
        if not part.endswith("[]"):
            raise ValueError(f"count expression segment must end with []: {part!r}")
        key = part[:-2]
        nxt = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            value = node.get(key)
            if isinstance(value, list):
                if i == len(parts) - 1:
                    total += len(value)
                else:
                    nxt.extend(value)
        nodes = nxt
    return total


def expected_counts(doc, schema: dict) -> dict:
    return {name: count_expr(doc, expr) for name, expr in (schema.get("counts") or {}).items()}


def load_json(path: Path):
    """Return (doc, error). Never raises on bad input: the caller reports it as a failure."""
    try:
        return json.loads(path.read_text()), None
    except FileNotFoundError:
        return None, f"{path} does not exist"
    except json.JSONDecodeError as e:
        return None, f"{path} is not valid JSON: {e}"
    except OSError as e:  # unreadable, a directory, a broken link
        return None, f"{path} could not be read: {e}"


def load_config(repo: Path) -> dict:
    """Parse `.delivery-flow.yaml`. Supported subset: nested mappings by indentation,
    scalars, inline lists `[a, b]` and block sequences of scalars. Standard library only,
    so a hook can read the binding on a machine with no PyYAML."""
    return parse_mapping((repo / CONFIG_NAME).read_text())


def load_roster(path: Path = None) -> dict:
    """Parse `templates/delivery-flow/roster.yaml`: kinds of work -> specialists.

    Same subset as the config, because it is the same shape — a mapping of mappings with
    inline lists. Paired with `skills/delivery-flow/references/roster.md`: the vocabulary of
    kinds and the keys under each live in both, and they have to agree.
    """
    path = path or (PLUGIN_ROOT / "templates" / "delivery-flow" / "roster.yaml")
    return parse_mapping(Path(path).read_text())


def parse_mapping(text: str) -> dict:
    """The YAML subset both `.delivery-flow.yaml` and `roster.yaml` are written in."""
    root = {}
    stack = [(-1, root)]  # (indent, mapping) — the innermost mapping is last
    pending = None

    for raw in text.splitlines():
        line = "" if raw.lstrip().startswith("#") else raw.split(" #")[0].rstrip()
        if not line.strip():
            continue

        m = re.match(r"^(\s*)-\s+(.+)$", line)
        if m and pending is not None:
            pending.append(_config_scalar(m.group(2)))
            continue

        m = re.match(r"^(\s*)([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            continue
        indent, key, value = len(m.group(1)), m.group(2), m.group(3)

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        target = stack[-1][1]

        if value == "":
            child = {}
            target[key] = child
            stack.append((indent, child))
            pending = _Pending(target, key)
        else:
            target[key] = _config_scalar(value)
            pending = None
    return root


def _config_scalar(v: str):
    v = v.strip()
    if v in ("", "null", "~"):
        return None
    if v in ("true", "True"):
        return True
    if v in ("false", "False"):
        return False
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
    if v[0] == v[-1] and v[0] in "'\"" and len(v) >= 2:
        return v[1:-1]
    return v


class _Pending(list):
    """A key whose value is still unknown: a block sequence appends here, and if nothing
    appends, it stays the empty mapping the parser first assumed."""

    def __init__(self, owner, key):
        super().__init__()
        self.owner, self.key = owner, key

    def append(self, item):
        super().append(item)
        self.owner[self.key] = list(self)


DEFAULT_PROFILE = "full"


def load_profiles(path: Path = None) -> list:
    """Parse `templates/delivery-flow/profiles.yaml` without PyYAML.

    Shape: `profiles:` as a block sequence of flat mappings, each with `profile`, `terminus`,
    `next` and an inline `steps` list. A `steps:` value whose bracket never closes is an
    error rather than a short list, because silently truncating a profile would drop steps
    from the flow and still look like a successful run.
    """
    path = path or (PLUGIN_ROOT / "templates" / "delivery-flow" / "profiles.yaml")
    profiles, cur = [], None
    for lineno, raw in enumerate(path.read_text().splitlines(), 1):
        line = "" if raw.lstrip().startswith("#") else raw.split(" #")[0].rstrip()
        if not line.strip():
            continue
        m = re.match(r"^\s*-\s+([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            cur = {}
            profiles.append(cur)
            key, value = m.group(1), m.group(2)
        else:
            m = re.match(r"^(\s+)([A-Za-z0-9_-]+):\s*(.*)$", line)
            if not m or cur is None:
                continue
            key, value = m.group(2), m.group(3)
        if value.lstrip().startswith("[") and not value.rstrip().endswith("]"):
            raise ValueError(
                f"{path}:{lineno}: `{key}:` opens an inline list that does not close on the "
                "same line; keep each list on one line so none is silently truncated")
        cur[key] = _config_scalar(value)
    return profiles


def select_profile(cfg: dict, profiles: list):
    """(profile, error) for the config's `profile:` key, defaulting to `full`."""
    name = cfg.get("profile") or DEFAULT_PROFILE
    for p in profiles:
        if p.get("profile") == name:
            return p, None
    available = ", ".join(sorted(p.get("profile") or "?" for p in profiles)) or "none"
    return None, f"unknown profile {name!r}; profiles.yaml defines: {available}"


def load_pricing(path: Path = None) -> dict:
    """Parse `templates/delivery-flow/pricing.yaml` without PyYAML.

    Shape: top-level scalars, then `models:` as a block sequence of flat mappings whose
    `match` is an inline list of model-id prefixes.
    """
    path = path or (PLUGIN_ROOT / "templates" / "delivery-flow" / "pricing.yaml")
    meta, models, cur = {}, [], None
    for raw in path.read_text().splitlines():
        line = "" if raw.lstrip().startswith("#") else raw.split(" #")[0].rstrip()
        if not line.strip():
            continue
        m = re.match(r"^\s*-\s+(\w+):\s*(.*)$", line)
        if m:
            cur = {}
            models.append(cur)
            cur[m.group(1)] = _price_scalar(m.group(2))
            continue
        m = re.match(r"^(\s*)(\w+):\s*(.*)$", line)
        if not m:
            continue
        indent, key, value = len(m.group(1)), m.group(2), m.group(3)
        if indent == 0:
            cur = None
            if value:
                meta[key] = _price_scalar(value)
        elif cur is not None:
            cur[key] = _price_scalar(value)
    return {"meta": meta, "models": models}


def _price_scalar(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
    if v and v[0] == v[-1] and v[0] in "'\"":
        v = v[1:-1]
    try:
        return float(v) if "." in v else int(v)
    except ValueError:
        return v


def price_for(model: str, pricing: dict):
    """The pricing row whose `match` prefixes the model id, or None."""
    for row in pricing.get("models", []):
        for prefix in row.get("match") or []:
            if model and model.startswith(prefix):
                return row
    return None


def cost_usd(usage: dict, row: dict):
    """USD at published list rates for one usage bundle. None when the model is unpriced."""
    if not row:
        return None
    per_m = lambda tokens, rate: (tokens or 0) * (rate or 0) / 1_000_000
    return round(
        per_m(usage.get("input_tokens"), row.get("input"))
        + per_m(usage.get("cache_creation_5m"), row.get("cache_write_5m"))
        + per_m(usage.get("cache_creation_1h"), row.get("cache_write_1h"))
        + per_m(usage.get("cache_read"), row.get("cache_read"))
        + per_m(usage.get("output_tokens"), row.get("output")), 6)


def usage_from_transcript(path: Path) -> dict:
    """Sum a transcript's usage per model, counting each API message once.

    Claude Code repeats the same `usage` object on every content block of one message, so
    summing lines overcounts several-fold; de-duplicating by `message.id` is the fix.
    """
    per_model, seen = {}, set()
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return {}
    for line in lines:
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        usage, mid, model = msg.get("usage"), msg.get("id"), msg.get("model")
        if not usage or not mid or mid in seen:
            continue
        seen.add(mid)
        bucket = per_model.setdefault(model, {"input_tokens": 0, "output_tokens": 0,
                                              "cache_creation_5m": 0, "cache_creation_1h": 0,
                                              "cache_read": 0, "messages": 0})
        creation = usage.get("cache_creation") or {}
        bucket["input_tokens"] += usage.get("input_tokens") or 0
        bucket["output_tokens"] += usage.get("output_tokens") or 0
        bucket["cache_creation_5m"] += creation.get("ephemeral_5m_input_tokens") or 0
        bucket["cache_creation_1h"] += creation.get("ephemeral_1h_input_tokens") or 0
        bucket["cache_read"] += usage.get("cache_read_input_tokens") or 0
        bucket["messages"] += 1
    return per_model


SIGN_NAMESPACE = "delivery-flow-decision"


def _payload_for_signing(decision: dict) -> bytes:
    """The bytes a decision's signature covers: every field except the signature itself."""
    body = {k: v for k, v in decision.items() if k != "signature"}
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode()


def verify_decision(decision: dict, allowed_signers: Path):
    """(ok, reason) for a decision's signature.

    A decision is the one thing in this pipeline an agent must not be able to produce, so
    it is signed by a key whose every use needs a human present (a hardware key's touch, or
    Touch ID). Verification is `ssh-keygen -Y verify` against an allowed-signers file; an
    unsigned decision, a bad signature, or a signer outside that file is treated as absent.
    """
    import subprocess
    import tempfile

    sig = decision.get("signature")
    if not sig or sig == "(test)":
        return False, "decision is not signed"
    if not allowed_signers or not Path(allowed_signers).expanduser().exists():
        return False, f"no allowed_signers file at {allowed_signers}"
    signer = decision.get("decider")
    if not signer:
        return False, "decision names no decider"
    with tempfile.TemporaryDirectory() as tmp:
        sig_path = Path(tmp) / "decision.sig"
        sig_path.write_text(sig if sig.endswith("\n") else sig + "\n")
        try:
            out = subprocess.run(
                ["ssh-keygen", "-Y", "verify", "-f", str(Path(allowed_signers).expanduser()),
                 "-I", signer, "-n", SIGN_NAMESPACE, "-s", str(sig_path)],
                input=_payload_for_signing(decision), capture_output=True, timeout=20)
        except (OSError, subprocess.SubprocessError) as e:
            return False, f"could not run ssh-keygen: {e}"
    if out.returncode != 0:
        return False, (out.stderr or b"").decode().strip() or "signature did not verify"
    return True, "signature verified"


def punch_out_trigger(path: Path) -> str:
    """The trigger named in a punch-out's H1. The one-line idiom `check-punch-out.py` uses to
    decide whether a trigger is already open, kept here so every reader agrees."""
    try:
        return path.read_text().split("\n", 1)[0].split(": ", 1)[-1].strip()
    except OSError:
        return path.stem


def open_punch_outs(item_dir: Path) -> list:
    """Punch-outs with no decision file, or whose decision no longer matches the file.

    Signature verification is the enforcement hook's job; this reports what is unresolved.
    """
    out = []
    for p in sorted(item_dir.glob("punch-out-*.md")):
        decision = item_dir / "decisions" / (p.stem + ".json")
        doc, err = load_json(decision)
        entry = {"punch_out": p.name, "trigger": punch_out_trigger(p)}
        if err:
            out.append({**entry, "state": "undecided"})
            continue
        if doc.get("sha256") != sha256(p):
            out.append({**entry, "state": "decision is stale: the punch-out changed after it was decided"})
            continue
        if doc.get("choice") != "proceed":
            out.append({**entry, "state": f"decided: {doc.get('choice')}", "stops_flow": True})
    return out


class Usage(Exception):
    """A failure that belongs to the caller: bad arguments, missing config, or a refusal.

    Exit 2. Every adapter raises this same class, because the exit codes *are* the adapter
    contract and three adapters with three private exception hierarchies would eventually
    disagree about which code a refusal gets.
    """


class Remote(Exception):
    """A failure that belongs to the other end: auth, network, or an unexpected status.

    Exit 3, with the remediation on stderr.
    """


def dispatch(handlers: dict, cmd: str, args) -> int:
    """Run an adapter subcommand and map its failures onto the contract's exit codes."""
    import sys
    try:
        return handlers[cmd](args)
    except Usage as e:
        print(str(e), file=sys.stderr)
        return 2
    except Remote as e:
        print(str(e), file=sys.stderr)
        return 3


def emit(doc) -> int:
    """Every subcommand's stdout: sorted, indented JSON, so reruns are byte-identical."""
    import sys
    print(json.dumps(doc, indent=2, sort_keys=True))
    sys.stdout.flush()
    return 0


def outward_refusal(item: str, action: str, start: Path = None):
    """None if an outward action may proceed for this item, else the reason it must not.

    Every adapter's `comment`, `transition` and `open-pr` asks this before it touches the
    remote, so the three cannot drift into three different ideas of "blocked". Two things
    block: an unresolved punch-out on the item, and a post to a tracker configured
    `external: true` without a decision carrying a signature that verifies. A decision file
    on its own is not enough — an agent can write a file.

    The PreToolUse hook blocks these too. Checking here as well is deliberate: one layer can
    be wrong, and the far end is someone else's system.
    """
    repo = repo_root(start or Path("."))
    if not is_delivery_repo(repo):
        return f"{repo} is not a delivery-flow repo, so {action} has no policy to check"

    item_dir = repo / "delivery" / item
    blocking = open_punch_outs(item_dir) if item_dir.is_dir() else []
    if blocking:
        names = ", ".join(f"{p['punch_out']} ({p['trigger']}) is {p['state']}" for p in blocking)
        return f"refusing to {action}: an unresolved punch-out is open — {names}"

    cfg = load_config(repo)
    if not (cfg.get("tracker") or {}).get("external"):
        return None

    signers = (cfg.get("decisions") or {}).get("allowed_signers")
    if not signers:
        return (f"refusing to {action}: tracker.external is true but no "
                "decisions.allowed_signers is configured, so no decision can be verified")
    decisions = (sorted((item_dir / "decisions").glob("*.json"))
                 if (item_dir / "decisions").is_dir() else [])
    if not decisions:
        return (f"refusing to {action}: tracker.external is true, so writing to this tracker "
                "needs a signed decision. Raise one with check-punch-out.py and sign it with "
                "decide.py.")

    reasons = []
    for path in decisions:
        doc, err = load_json(path)
        if err:
            reasons.append(f"{path.name}: {err}")
            continue
        if doc.get("choice") != "proceed":
            reasons.append(f"{path.name}: choice is {doc.get('choice')!r}, not 'proceed'")
            continue
        ok, why = verify_decision(doc, Path(signers).expanduser())
        if ok:
            return None
        reasons.append(f"{path.name}: {why}")
    return (f"refusing to {action}: no decision for this item carries a verifiable human "
            "signature — " + "; ".join(reasons))


def repo_registry() -> Path:
    """Where the opted-in repos are listed. Read at call time, not import time, so an
    override reaches a subprocess started after this module was first imported — tests set
    it, and reading it once at import meant they wrote to the real registry instead."""
    return Path(os.environ.get("DELIVERY_FLOW_REPOS",
                               "~/.config/delivery-flow/repos")).expanduser()


def known_repos(registry: Path = None) -> list:
    """Every repo that has opted into delivery-flow, newest last. Missing ones are dropped.

    A hook is handed the *session's* `cwd`, never the directory a command actually wrote to, so
    it cannot learn the target repo from its payload: a shell command can `cd`, hold the path in
    a variable, or use an absolute path from an unrelated cwd. Three separate hooks were each
    guessing, and each missed. This is the registry they consult instead — written by
    `init-delivery-flow.py` when a repo opts in, so there is nothing to infer.
    """
    registry = registry or repo_registry()
    out = []
    try:
        lines = registry.read_text().splitlines()
    except OSError:
        return out
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        path = Path(line).expanduser()
        if path not in out and is_delivery_repo(path):
            out.append(path)
    return out


def register_repo(repo: Path, registry: Path = None) -> bool:
    """Record a repo in the registry. True if it was added, False if already there."""
    registry = registry or repo_registry()
    repo = Path(repo).expanduser().resolve()
    existing = []
    try:
        existing = [l.split("#", 1)[0].strip() for l in registry.read_text().splitlines()]
    except OSError:
        pass
    if str(repo) in existing:
        return False
    registry.parent.mkdir(parents=True, exist_ok=True)
    with registry.open("a") as f:
        f.write(f"{repo}\n")
    return True


def candidate_repos(payload: dict, extra=None) -> list:
    """Every delivery repo a hook should consider for this tool call, cwd-derived ones FIRST.

    Order matters and this order is deliberate. A caller that wants one repo should pick the
    one that actually holds the thing it is looking for — the item's `.current-step`, its open
    punch-out — not simply the head of this list. But where a caller must choose blind, the
    session's own repo is the better guess than an arbitrary registry entry, so it leads.
    """
    out = []
    for base in [Path(payload.get("cwd") or ".")] + list(extra or []):
        try:
            repo = repo_root(Path(base))
        except OSError:
            continue
        if repo not in out and is_delivery_repo(repo):
            out.append(repo)
    for repo in known_repos():
        if repo not in out:
            out.append(repo)
    return out


def trace_path(repo: Path, item: str) -> Path:
    return repo / "delivery" / item / "trace.jsonl"


def append_trace(repo: Path, item: str, record: dict) -> None:
    p = trace_path(repo, item)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")
