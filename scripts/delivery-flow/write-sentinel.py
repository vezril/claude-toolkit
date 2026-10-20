#!/usr/bin/env python3
"""Write the sentinel beside an artifact: the node's own claim about what it produced.

Usage:
    write-sentinel.py <artifact-path> --step <step> [--status complete|partial]
                      [--count name=N ...]

A node calls this as its last action. By default the counts are read from the file it
just wrote, which covers the honest case. `--count` records what the node *believes* it
produced instead, which is the point of the sentinel: the edge check compares the claim
against the file, and a node that thinks it wrote 8 stories over a file holding 5 fails.

Exit codes: 0 written, 1 the artifact is unreadable, 2 usage error.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SENTINEL_SUFFIX, expected_counts, load_json, load_schemas, schema_for, sha256  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("artifact")
    ap.add_argument("--step", required=True)
    ap.add_argument("--status", default="complete", choices=["complete", "partial"])
    ap.add_argument("--count", action="append", default=[], metavar="name=N",
                    help="claimed count; repeatable. Omit to read counts from the artifact")
    args = ap.parse_args(argv)

    path = Path(args.artifact)
    schemas = load_schemas()
    schema = schema_for(path.name, schemas)
    if schema is None:
        print(f"no schema for {path.name}", file=sys.stderr)
        return 2

    doc, err = load_json(path)
    if err:
        print(err, file=sys.stderr)
        return 1

    counts = expected_counts(doc, schema)
    for claim in args.count:
        if "=" not in claim:
            print(f"--count wants name=N, got {claim!r}", file=sys.stderr)
            return 2
        name, _, value = claim.partition("=")
        try:
            counts[name.strip()] = int(value)
        except ValueError:
            print(f"--count value must be an integer, got {value!r}", file=sys.stderr)
            return 2

    sentinel = {
        "artifact": path.name,
        "sha256": sha256(path),
        "counts": counts,
        "status": args.status,
        "step": args.step,
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    out = path.with_name(path.name + SENTINEL_SUFFIX)
    out.write_text(json.dumps(sentinel, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out} ({', '.join(f'{k}={v}' for k, v in sorted(counts.items())) or 'no counts'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
