"""Model pricing and token usage — workflow-agnostic.

Moved out of `scripts/delivery-flow/common.py` unchanged (certify-sdlc-pipeline task 1.1).
Nothing here knows what a delivery item is: it parses a pricing table, matches a model id to
a row, multiplies tokens by rates, and sums usage out of a Claude Code transcript. A second
workflow needs all of that and none of it needs to be duplicated.

The one workflow-specific thing — *which* pricing file — stays with the caller. `load` takes a
path; `common.load_pricing` supplies delivery-flow's default and delegates here, so every
existing import keeps working and the behaviour is identical.

Stdlib only: this is reached from `hooks/trace-step.py`, which runs in whatever interpreter the
session has.
"""

import json
import re
from pathlib import Path


def load(path: Path) -> dict:
    """Parse a pricing table without PyYAML.

    Shape: top-level scalars, then `models:` as a block sequence of flat mappings whose
    `match` is an inline list of model-id prefixes.

    The path is required rather than defaulted. Which pricing file applies is a property of
    the workflow, not of this module, and a default here would silently price a second
    workflow's runs off delivery-flow's table.
    """
    path = Path(path)
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
