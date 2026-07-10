#!/usr/bin/env python3
"""PreToolUse hook: enforce the test-writer / implementer file boundary.

The SDLC dev pair is separated by file territory: the test-writer may edit
test code only, the implementer everything except test code. Their agent
charters state the rule; this hook makes it mechanical. For any other agent
(or the main session) it is a no-op.

Classification is by file path, not intent — same definition as in
agents/test-writer.md and agents/implementer.md. Keep the three in sync.
"""
import json
import re
import sys

TEST_DIR_SEGMENTS = {
    "test", "tests", "__tests__", "spec", "specs",
    "__mocks__", "__snapshots__", "__fixtures__", "testdata",
    "test-resources", "it",
}

# Filename conventions: foo.test.ts, foo.spec.js, foo_test.go, test_foo.py,
# foo_spec.rb, FooTest.scala, FooSpec.scala, FooTests.cs, conftest.py.
TEST_FILE_RE = re.compile(
    r"(\.test\.|\.spec\.|_test\.|_spec\.)"
    r"|^test_"
    r"|^conftest\.py$"
)
TEST_BASENAME_SUFFIXES = ("Test", "Tests", "Spec", "Specs")


def is_test_path(path: str) -> bool:
    segments = [s for s in path.replace("\\", "/").split("/") if s]
    if not segments:
        return False
    filename = segments[-1]
    if any(d.lower() in TEST_DIR_SEGMENTS for d in segments[:-1]):
        return True
    if TEST_FILE_RE.search(filename):
        return True
    base = filename.rsplit(".", 1)[0]
    return base.endswith(TEST_BASENAME_SUFFIXES)


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    agent = data.get("agent_type") or ""
    if agent not in ("test-writer", "implementer"):
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not path:
        sys.exit(0)

    test_file = is_test_path(path)
    if agent == "test-writer" and not test_file:
        deny(
            f"Boundary: test-writer may modify test code only, and {path} is not "
            "a test file. Do not retry or work around this — hand back a request "
            "naming this file and the change you need from the implementer/human."
        )
    if agent == "implementer" and test_file:
        deny(
            f"Boundary: implementer may not modify test code, and {path} is a "
            "test file. Do not retry or work around this — if the test is wrong, "
            "report it back to the test-writer/human with your evidence instead."
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
