"""The audit trail: append one JSON line, read them back tolerantly.

Workflow-agnostic (certify-sdlc-pipeline task 1.1). A trace record is whatever the caller
decides; this module owns only the file format and, more importantly, **what happens when the
file is damaged**.

That second part is why this exists rather than staying three local helpers. Before the move
there were three readers:

- `common.append_trace` wrote the lines;
- `check-punch-out.read_trace` returned `[]` for a missing file, skipped blank lines, and
  caught `JSONDecodeError`;
- `check-edge.last_traced_sha` caught `OSError`, caught `(JSONDecodeError, ValueError)`, and
  relied on `json.loads("")` raising to skip blanks.

Three behaviours for "the trace is unreadable", in a system where the trace *is* one of the
five things the certification examines. A record silently dropped by one reader and kept by
another is an audit trail that disagrees with itself depending on who asks.

The policy here, stated once: a trace that cannot be read is empty, not an error, and a line
that cannot be parsed is skipped rather than fatal. A hook must not crash because an earlier
write was interrupted — losing one record is recoverable, taking down every subsequent edge
check is not. `read` is lossy on purpose. Nothing currently measures how lossy, which is a known gap
rather than a hidden one: a report saying "32 steps" means something different if three
records were unreadable.

Stdlib only: reached from all three hooks.
"""

import json
from pathlib import Path


def append(path: Path, record: dict) -> None:
    """Append one record. Creates the directory if the item is new.

    Opened in append mode per call rather than held open: several hooks write to the same
    trace in the same session, and a long-lived handle would interleave partial lines.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def read(path: Path) -> list:
    """Every parseable record, oldest first. Missing or unreadable file reads as empty.

    Blank and malformed lines are skipped. See the module docstring for why that is a policy
    rather than an oversight.
    """
    try:
        text = Path(path).read_text()
    except OSError:
        return []
    out = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except (json.JSONDecodeError, ValueError):
            continue
    return out
