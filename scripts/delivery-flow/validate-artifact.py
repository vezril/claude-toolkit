#!/usr/bin/env python3
"""Validate a delivery-flow artifact against its schema.

Usage:
    validate-artifact.py <path> [--schema <artifact-name>] [--consumer <step>] [--json]

Checks, in order:
  1. the file parses as JSON;
  2. it conforms to its schema (a JSON Schema subset: type, required, properties,
     items, enum, const, pattern, minLength, minItems, additionalProperties);
  3. with --consumer, that it carries the fields that consuming step requires.

Exit codes: 0 valid, 1 invalid (report on stdout), 2 usage error.
Standard library only, so it runs anywhere a hook does.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, load_schemas, schema_for  # noqa: E402

TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "number": (int, float), "integer": int, "null": type(None),
}


def type_ok(value, expected) -> bool:
    names = expected if isinstance(expected, list) else [expected]
    for name in names:
        py = TYPES.get(name)
        if py is None:
            continue
        if name in ("number", "integer") and isinstance(value, bool):
            continue  # bool is an int in Python; JSON disagrees
        if isinstance(value, py):
            return True
    return False


def validate(value, schema: dict, path: str, problems: list) -> None:
    where = path or "(root)"

    if "type" in schema and not type_ok(value, schema["type"]):
        problems.append(f"{where}: expected {schema['type']}, got {type(value).__name__}")
        return
    if "enum" in schema and value not in schema["enum"]:
        problems.append(f"{where}: {value!r} is not one of {schema['enum']}")
    if "const" in schema and value != schema["const"]:
        problems.append(f"{where}: expected {schema['const']!r}")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            problems.append(f"{where}: shorter than {schema['minLength']} characters")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            problems.append(f"{where}: {value!r} does not match {schema['pattern']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            problems.append(f"{where}: {len(value)} items, needs at least {schema['minItems']}")
        if "items" in schema:
            for i, item in enumerate(value):
                validate(item, schema["items"], f"{where}[{i}]", problems)

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                problems.append(f"{where}: missing required field {key!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    problems.append(f"{where}: unexpected field {key!r}")
        for key, sub in props.items():
            if key in value:
                validate(value[key], sub, f"{where}.{key}" if path else key, problems)


def consumer_problems(doc, schema: dict, consumer: str) -> list:
    spec = (schema.get("consumers") or {}).get(consumer)
    if spec is None:
        return [f"schema {schema['artifact']} declares no input contract for consumer {consumer!r}"]
    out = []
    for field in spec.get("requires", []):
        if not isinstance(doc, dict) or field not in doc:
            out.append(f"{consumer} requires field {field!r}, which is absent")
        elif doc[field] in ("", [], {}, None):
            out.append(f"{consumer} requires field {field!r}, which is empty")
    # Fields that must exist but may legitimately hold nothing. `project-context.decisions` is
    # the case that forced this: an empty list is the honest answer from a vault with no
    # decisions recorded, and demanding content made a cold start block the flow — directly
    # against the design's own rule that a cold start is not a failure.
    for field in spec.get("requires_present", []):
        if not isinstance(doc, dict) or field not in doc:
            out.append(f"{consumer} requires field {field!r} to be present, and it is absent")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--schema", help="artifact name to validate against (default: the file's own name)")
    ap.add_argument("--consumer", help="also check this consuming step's input contract")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args(argv)

    path = Path(args.path)
    schemas = load_schemas()
    name = args.schema or path.name
    schema = schema_for(name, schemas)
    if schema is None:
        print(f"no schema for {name} (schemas: {', '.join(sorted(schemas))})", file=sys.stderr)
        return 2

    doc, err = load_json(path)
    problems = [err] if err else []
    if not problems:
        validate(doc, schema, "", problems)
        if args.consumer:
            problems += consumer_problems(doc, schema, args.consumer)

    if args.json:
        print(json.dumps({"path": str(path), "schema": schema["artifact"],
                          "ok": not problems, "problems": problems}, indent=2))
    elif problems:
        print(f"INVALID {path} against {schema['artifact']}")
        for p in problems:
            print(f"  - {p}")
    else:
        print(f"valid: {path} against {schema['artifact']}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
