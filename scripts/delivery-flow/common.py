"""Shared helpers for delivery-flow scripts and hooks. Standard library only.

Everything here answers one of four questions: where is the repo, is this a
delivery-flow repo at all, which artifact is this path, and what does its schema say.
"""

import fnmatch
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow"))
import pricing as _pricing  # noqa: E402
import registry as _registry  # noqa: E402
import layout as _layout  # noqa: E402
import schema as _schema  # noqa: E402
import trace as _trace  # noqa: E402

CONFIG_NAME = ".delivery-flow.yaml"
SENTINEL_SUFFIX = ".sentinel.json"
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parents[2]))
SCHEMA_DIR = PLUGIN_ROOT / "schemas"

# <root>/<ITEM-KEY>/<artifact>. The root is `delivery/` inside the repo by default, and
# `artifacts.root` can point it anywhere — typically the Obsidian vault, which is itself a git
# repo synced between machines, so the trail is still versioned and still aggregates. The
# pattern is built per call because the root is per repo.
ARTIFACT_DIR = "delivery"

# Repo detection and artifact layout live in the substrate (`scripts/workflow/layout.py`).
# What stays here is delivery-flow's two answers: the opt-in file name and the artifact
# directory. Re-exports below, so no existing call site changes (task 1.3).
repo_root = _layout.repo_root


def is_delivery_repo(path: Path) -> bool:
    """A delivery-flow repo has the config at its root. Everything is inert otherwise."""
    return _layout.opted_in(path, CONFIG_NAME)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_artifact_path(path, root: Path = None):
    """(item_key, filename) for a path inside the artifact root, else (None, None)."""
    return _layout.parse_artifact_path(path, ARTIFACT_DIR, root)


def artifact_root(repo: Path, cfg: dict = None) -> Path:
    """Where this repo's run artifacts live. See `scripts/workflow/layout.py`.

    Loads the config when the caller has none — the substrate cannot, because which file to
    read and how to parse it are this workflow's business.
    """
    if cfg is None:
        try:
            cfg = load_config(repo)
        except OSError:
            cfg = {}
    return _layout.artifact_root(repo, ARTIFACT_DIR, cfg)


def item_dir(repo: Path, item: str, cfg: dict = None) -> Path:
    return artifact_root(repo, cfg) / item


# Schema loading and resolution live in the substrate (`scripts/workflow/schema.py`).
# Re-exports, so no existing call site changes (task 1.3). `SCHEMA_DIR` above is the one
# workflow-specific part — which contracts apply — and the substrate's `load` requires it
# rather than defaulting, so a second workflow cannot be validated against these.
for_name = _schema.for_name
count_expr = _schema.count_expr
expected_counts = _schema.expected_counts


def load_schemas(schema_dir: Path = None) -> dict:
    """delivery-flow's artifact schemas. Parser: `scripts/workflow/schema.py`."""
    return _schema.load(schema_dir or SCHEMA_DIR)


def schema_for(filename: str, schemas: dict):
    """The schema for an artifact file name, by exact name then by glob."""
    return _schema.for_name(filename, schemas)


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


# Pricing and usage live in the substrate now (`scripts/workflow/pricing.py`); nothing about
# multiplying tokens by rates is specific to delivery. These are thin re-exports so that every
# existing `from common import ...` and `common.price_for(...)` call site keeps working —
# certify-sdlc-pipeline task 1.3 requires no import in the submitted tree to change.
#
# `PRICING_PATH` is the one delivery-specific part: which table applies. The substrate's
# `load` requires a path precisely so a second workflow cannot be priced off this one by
# accident.
PRICING_PATH = PLUGIN_ROOT / "templates" / "delivery-flow" / "pricing.yaml"

price_for = _pricing.price_for
cost_usd = _pricing.cost_usd
usage_from_transcript = _pricing.usage_from_transcript


def load_pricing(path: Path = None) -> dict:
    """delivery-flow's pricing table. See `scripts/workflow/pricing.py` for the parser."""
    return _pricing.load(path or PRICING_PATH)


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

    cfg_for_root = None
    try:
        cfg_for_root = load_config(repo)
    except OSError:
        pass
    item_dir = artifact_root(repo, cfg_for_root) / item
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


# The opted-in repo registry lives in the substrate (`scripts/workflow/registry.py`). What
# stays here is the two workflow-specific answers it needs: which file to read, and what
# counts as opted in. Everything below is a thin re-export so no existing call site changes
# (task 1.3).
#
# The generic rule for the registry path reproduces delivery-flow's existing locations
# exactly — `~/.config/delivery-flow/repos` and `DELIVERY_FLOW_REPOS` — so this is a move
# rather than a migration, and no test fixture or shell export changes.
WORKFLOW_NAME = "delivery-flow"


def repo_registry() -> Path:
    """Where the opted-in repos are listed. Resolved per call, not at import.

    An override has to reach a subprocess started after this module was first imported; tests
    set one, and reading it once at import meant they wrote to the real registry instead.
    """
    return _registry.path_for(WORKFLOW_NAME)


def known_repos(registry: Path = None) -> list:
    """Every repo that has opted into delivery-flow, newest last. Missing ones are dropped."""
    return _registry.known(registry or repo_registry(), is_delivery_repo)


def register_repo(repo: Path, registry: Path = None) -> bool:
    """Record a repo in the registry. True if it was added, False if already there."""
    return _registry.register(repo, registry or repo_registry())


def candidate_repos(payload: dict, extra=None) -> list:
    """Every delivery repo a hook should consider for this tool call, cwd-derived ones FIRST."""
    return _registry.candidates(payload, is_delivery_repo, repo_registry(), repo_root, extra)


def trace_path(repo: Path, item: str, cfg: dict = None) -> Path:
    return artifact_root(repo, cfg) / item / "trace.jsonl"


def append_trace(repo: Path, item: str, record: dict) -> None:
    """Append to this item's trace. Format and damage policy: `scripts/workflow/trace.py`."""
    _trace.append(trace_path(repo, item), record)


def read_trace(repo: Path, item: str) -> list:
    """This item's trace records, oldest first. Unreadable reads as empty."""
    return _trace.read(trace_path(repo, item))
