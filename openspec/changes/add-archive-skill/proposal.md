# Proposal: add-archive-skill

## Why

Retiring a toolkit component (skill, workflow, script) currently means deleting it — losing the reference value of battle-tested prompts, scripts, and the reasoning behind them. The immediate consumer is the decompose-scala-scaffold change, which retires the monolithic `new-scala-service` skill and needs somewhere to put it.

## What Changes

- New top-level `archive/` folder in claude-toolkit for retired components, excluded from the plugin's active surface (nothing under `archive/` is installed or invocable).
- New reusable skill `toolkit-archive` that performs the retirement: moves the component's files into `archive/<name>/`, writes a `RETIRED.md` documenting what it was, why it was retired, what replaced it, and when, and removes the component from the active indexes (README, and `~/.claude` installs if present).
- README gains an Archive note in the Layout section.

## Capabilities

### New Capabilities
- `toolkit-archive`: archiving a retired toolkit component into `archive/` with its documentation, preserving files verbatim and recording the retirement rationale.

### Modified Capabilities
<!-- none — no existing specs in openspec/specs/ -->

## Impact

- Repo layout: new `archive/` directory.
- `README.md`: Layout section update; archived components leave the skill index.
- No runtime/plugin impact: `archive/` is inert by convention.
