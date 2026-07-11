# merge-train Specification

## Purpose
TBD - created by archiving change add-merge-skill. Update Purpose after archive.
## Requirements
### Requirement: The train runs merge, tag, archive in order

The skill SHALL, on invocation: (1) resolve the target PR (argument, else the current branch's single open PR, else ask), merge it, verify `MERGED`, and sync local `main`; (2) tag the merge commit on `main` with `vX.Y.Z` and push the tag; (3) archive the corresponding completed OpenSpec change and land the bookkeeping. Steps 2 and 3 SHALL be individually skippable by explicit instruction (`--no-tag`/`--no-archive` or conversational equivalent) and SHALL auto-skip with a note when inapplicable (no tag convention requested, no completed change).

#### Scenario: Full train

- **GIVEN** a green gated PR, a `v1.2.3` latest tag, and one fully-completed OpenSpec change
- **WHEN** `/merge` runs and the human picks the proposed `v1.2.4`
- **THEN** the PR is merged, `v1.2.4` sits on the merge commit on `main`, the change is archived with its bookkeeping landed, and the report lists merge SHA, tag, release run, and archive path

### Requirement: One invocation is the authorization — with absolute stop conditions

Invoking the skill SHALL constitute the human authorization for every merge the train performs (target PR + archive bookkeeping), and the report SHALL enumerate each merge performed. The skill SHALL stop and ask instead of proceeding when: any required check is failing (never overridden), the version is not determinable from argument or confirmed proposal, multiple candidate PRs or changes exist, or the candidate change has incomplete tasks (hand off to the interactive /opsx:archive flow).

#### Scenario: Red checks

- **GIVEN** the target PR has a failing required check
- **WHEN** `/merge` runs
- **THEN** nothing is merged and the failing check is named

#### Scenario: No version given

- **WHEN** `/merge` runs without a version argument
- **THEN** the skill proposes the next patch bump over the latest `v*` tag (or `v0.1.0` when none) and waits for the human's choice before tagging

### Requirement: Tags land only on merged main

The tag SHALL be created on the merge commit on `main` after syncing — never on a feature branch — so repos with release workflows pass their tag-on-main ancestry gates.

#### Scenario: Release fires

- **GIVEN** a repo scaffolded with release.yml
- **WHEN** the train pushes `vX.Y.Z`
- **THEN** the release run triggers and its link appears in the report

