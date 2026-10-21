#!/usr/bin/env python3
"""SubagentStop / Stop hook: record what a step cost.

Stage 4 asks which step produced which output, on which model, for how many tokens and at
what cost. That has to come from the system's own records, not from an agent reporting on
itself, so this hook reads Claude Code's transcripts and appends one record per step per
model to `delivery/<ITEM-KEY>/trace.jsonl`.

  - SubagentStop: the subagent's whole transcript, attributed to the step named in
    `.current-step`.
  - Stop: the main session's usage since this hook last recorded it, attributed to
    `orchestrator` — the conductor's own turns are part of the cost.

Two facts about transcripts drive the implementation, both verified against Claude Code
2.1.209: usage repeats on every content block of one API message, so it is counted once per
`message.id`; and transcripts are written asynchronously, so a record may undercount a final
message, which `delivery-report.py` reconciles by re-reading.

Inert outside a delivery-flow repo. Never fails a tool call: a hook that breaks a session
to record a number is worse than a missing number.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HELPERS = Path(__file__).resolve().parents[1] / "scripts" / "delivery-flow"


def _common():
    sys.path.insert(0, str(HELPERS))
    import common
    return common


def _registry(common, repo):
    """step -> {tier, certified}: what the registry says this step should have run on."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_certification", HELPERS / "check-certification.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    reg = common.PLUGIN_ROOT / "skills" / "delivery-flow" / "steps.yaml"
    if not reg.exists():
        return {}
    out = {}
    for entry in mod.parse_registry(reg.read_text()).get("steps", []):
        prompt = common.PLUGIN_ROOT / str(entry.get("prompt", ""))
        sha_ok = prompt.exists() and common.sha256(prompt) == entry.get("prompt_sha256")
        out[entry.get("step")] = {"tier": entry.get("tier"), "certified": bool(sha_ok)}
    return out


TIER_ORDER = {"haiku": 1, "sonnet": 2, "opus": 3, "fable": 4}


def tier_of(model: str) -> str:
    for name in ("haiku", "sonnet", "opus", "fable"):
        if name in (model or ""):
            return name
    return "unknown"


def current_step(repo: Path, common):
    """The step the orchestrator said it was running, and for which item."""
    for path in sorted((repo / "delivery").glob("*/.current-step")) if (repo / "delivery").exists() else []:
        doc, err = common.load_json(path)
        if not err and doc.get("step"):
            return doc.get("item") or path.parent.name, doc["step"]
    return None, None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    common = _common()
    repo = common.repo_root(Path(payload.get("cwd") or "."))
    if not common.is_delivery_repo(repo):
        return 0

    item, step = current_step(repo, common)
    if not item:
        return 0  # nothing is being delivered right now

    event = payload.get("hook_event_name")
    if event == "SubagentStop":
        transcript = Path(payload.get("agent_transcript_path") or "")
        step_name, agent = step, payload.get("agent_type")
        state_key = f"subagent:{payload.get('agent_id')}"
    else:
        transcript = Path(payload.get("transcript_path") or "")
        step_name, agent = "orchestrator", "main"
        state_key = f"session:{payload.get('session_id')}"

    if not transcript or not transcript.exists():
        common.append_trace(repo, item, {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "item": item, "step": step_name, "agent": agent,
            "session_id": payload.get("session_id"), "agent_id": payload.get("agent_id"),
            "trace_error": f"transcript not found: {transcript or '(no path in payload)'}",
        })
        return 0

    # The main session's transcript grows across steps, so only count what is new.
    state_path = repo / "delivery" / item / ".trace-state.json"
    state, _ = common.load_json(state_path)
    state = state or {}
    already = set(state.get(state_key) or [])

    per_model, seen = {}, set()
    for line in transcript.read_text().splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        mid, usage, model = msg.get("id"), msg.get("usage"), msg.get("model")
        if not (mid and usage) or mid in seen or mid in already:
            continue
        seen.add(mid)
        creation = usage.get("cache_creation") or {}
        b = per_model.setdefault(model, {"input_tokens": 0, "output_tokens": 0,
                                         "cache_creation_5m": 0, "cache_creation_1h": 0,
                                         "cache_read": 0, "messages": 0})
        b["input_tokens"] += usage.get("input_tokens") or 0
        b["output_tokens"] += usage.get("output_tokens") or 0
        b["cache_creation_5m"] += creation.get("ephemeral_5m_input_tokens") or 0
        b["cache_creation_1h"] += creation.get("ephemeral_1h_input_tokens") or 0
        b["cache_read"] += usage.get("cache_read_input_tokens") or 0
        b["messages"] += 1

    if not per_model:
        return 0

    pricing = common.load_pricing()
    registry = _registry(common, repo)
    declared = registry.get(step_name, {})
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for model, usage in per_model.items():
        row = common.price_for(model, pricing)
        cost = common.cost_usd(usage, row)
        declared_tier = declared.get("tier")
        record = {
            "ts": now, "item": item, "step": step_name, "agent": agent,
            "session_id": payload.get("session_id"), "agent_id": payload.get("agent_id"),
            "model": model, "messages": usage["messages"],
            "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"],
            "cache_creation_tokens": usage["cache_creation_5m"] + usage["cache_creation_1h"],
            "cache_read_tokens": usage["cache_read"],
            "api_equivalent_cost_usd": cost,
            "pricing_as_of": pricing.get("meta", {}).get("as_of"),
            "certified": declared.get("certified"),
        }
        if cost is None:
            record["pricing_missing"] = True
        if declared_tier:
            record["declared_tier"] = declared_tier
            record["model_conformant"] = TIER_ORDER.get(tier_of(model), 99) <= TIER_ORDER.get(declared_tier, 99)
        common.append_trace(repo, item, record)

    state[state_key] = sorted(already | seen)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # a telemetry hook must never break the session it measures
        print(f"trace-step: {e}", file=sys.stderr)
        sys.exit(0)
