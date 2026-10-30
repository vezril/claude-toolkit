#!/usr/bin/env python3
"""Derive the two `.local.*` promptfoo configs for a suite from its canonical one.

The canonical `promptfooconfig.yaml` is the CI arm and the single source of truth
for tests and asserts. This writes two derived files beside it:

  promptfooconfig.local.yaml           with-skill arm, exec: providers
  promptfooconfig.local.baseline.yaml  naive baseline, exec: providers, no skill

Why derive instead of hand-maintaining three configs: the arms must share tests
and asserts byte for byte or the naive-vs-skill delta measures nothing. Hand-copying
is exactly how they drift. Edit the canonical config, re-run this, commit all three.

Why the exec: providers at all: the canonical configs use anthropic:claude-agent-sdk,
which spawns the claude-code binary and so inherits no AWS credentials on a
Bedrock-backed install -- every case errors with "Could not load AWS credentials".
See evals/_provider/claude.sh.

Usage:  python3 evals/_provider/make-local-configs.py evals/phq-9 [...]
"""

import re
import sys
from pathlib import Path

HEADER = """# DERIVED FILE -- do not hand-edit.
# Regenerate with: python3 evals/_provider/make-local-configs.py evals/{suite}
#
# {what} Tests and asserts come verbatim from promptfooconfig.yaml (the CI arm);
# only the providers differ, swapped to the shared exec: scripts in
# evals/_provider/ for machines where anthropic:claude-agent-sdk cannot
# authenticate. Deliberately not named promptfooconfig.yaml, so CI's
# auto-discovery ignores it.
"""

# The generation provider: a `- id: anthropic:...` list item plus its config block.
GEN_RE = re.compile(
    r"^(?P<indent> *)- +id: +anthropic:[^\n]*\n(?:\1 {2}[^\n]*\n|\1 {4}[^\n]*\n)*",
    re.MULTILINE,
)
# The grader: an `id: anthropic:...` under options.provider, plus its config block.
GRADER_RE = re.compile(
    r"^(?P<indent> *)id: +anthropic:[^\n]*\n(?:(?P=indent)[^\n]*\n)*?"
    r"(?=^ {0,%d}\S|\Z)" % 10,
    re.MULTILINE,
)


def swap_providers(src: str) -> str:
    """Point generation at claude.sh and grading at claude-grader.sh."""
    def gen_sub(m):
        ind = m.group("indent")
        label = re.search(r"label: *(\S+)", m.group(0))
        out = f"{ind}- id: exec:../_provider/claude.sh\n"
        if label:
            out += f"{ind}  label: {label.group(1)}\n"
        return out

    out, n_gen = GEN_RE.subn(gen_sub, src)
    if n_gen == 0:
        raise SystemExit("no anthropic generation provider found -- check the config shape")

    # Grader block sits under `options:\n  provider:\n    id: anthropic:...`
    out, n_grade = re.subn(
        r"(provider:\n)(\s+)id: +anthropic:[^\n]*\n(?:\2\s+[^\n]*\n)*",
        lambda m: f"{m.group(1)}{m.group(2)}id: exec:../_provider/claude-grader.sh\n",
        out,
    )
    return out


def strip_context_var(src: str) -> tuple[str, str]:
    """Remove the skill/agent injection so the baseline runs with no guidance.

    Returns the edited text and the var name removed, so the caller can fail loudly
    if a suite injects its context some other way.
    """
    m = re.search(r"^(\s*)(skill|agent): +file://[^\n]*\n", src, re.MULTILINE)
    if not m:
        raise SystemExit("no `skill:`/`agent:` var found -- baseline arm would be identical")
    out = src[: m.start()] + src[m.end() :]
    # If that was the only entry, drop the now-empty `vars:` key as well: a bare
    # `vars:` parses as None and promptfoo treats it as a malformed test block.
    out = re.sub(r"^ *vars: *\n(?= *(options|assert|tests|providers|prompts|defaultTest):)", "", out, flags=re.MULTILINE)
    return out, m.group(2)


def main(dirs: list[str]) -> None:
    for d in dirs:
        suite = Path(d)
        canonical = (suite / "promptfooconfig.yaml").read_text()
        name = suite.name

        local = HEADER.format(suite=name, what="WITH-SKILL arm.") + swap_providers(canonical)
        (suite / "promptfooconfig.local.yaml").write_text(local)

        base, var = strip_context_var(swap_providers(canonical))
        base = base.replace("file://prompt.txt", "file://prompt-baseline.txt")
        base = re.sub(
            r'^description: *"?(.*?)"?$',
            lambda m: f'description: "{m.group(1)} -- NAIVE BASELINE (no {var} in context)"',
            base,
            count=1,
            flags=re.MULTILINE,
        )
        (suite / "promptfooconfig.local.baseline.yaml").write_text(
            HEADER.format(suite=name, what=f"NAIVE-BASELINE arm: the `{var}` var is removed.") + base
        )

        if not (suite / "prompt-baseline.txt").exists():
            print(f"  !! {name}: write prompt-baseline.txt by hand (task without the {var})")
        print(f"  wrote {name}/promptfooconfig.local.yaml and .local.baseline.yaml  [{var}]")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1:])
