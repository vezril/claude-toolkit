# unattended-trigger-workflow Specification

## Purpose
Defines the reference GitHub Actions workflow that turns a labeled issue into an unattended SDLC run: trigger guards, phase-per-job execution with artifact handoff, the independent review as a required status check, and the PR + issue-comment audit trail. Created by archiving change add-unattended-mode.

## Requirements
### Requirement: Label-triggered GitHub Actions workflow with guards
The plugin SHALL ship a reference GitHub Actions workflow template that starts an unattended run when an issue receives the opt-in label, and the workflow SHALL enforce trigger guards before any pipeline work: the labeling actor is on the author allowlist, a per-repository concurrency group serializes runs, and per-run budget caps (wall-clock, iteration bounds) are stamped into the run.

#### Scenario: Allowlisted author triggers a run
- **WHEN** an allowlisted user applies the opt-in label to an issue
- **THEN** the workflow starts a run for that issue under the repository concurrency group

#### Scenario: Non-allowlisted actor is refused
- **WHEN** a user not on the allowlist applies the opt-in label
- **THEN** the workflow exits without starting the pipeline and leaves an explanatory comment

### Requirement: Phase-per-job execution with artifact handoff
The workflow SHALL run each pipeline phase as a separate job invoking headless Claude Code in a fresh context, on a dedicated work branch (`claude-auto/<issue>-<slug>`), committing that phase's artifacts to the branch so each subsequent job resumes from disk; the deterministic validators (`lint-story.py`, `openspec validate`) SHALL run as ordinary CI steps whose non-zero exit fails the job.

#### Scenario: Phase job resumes from prior artifacts
- **WHEN** the solutioning job starts after the spec job has committed its artifacts
- **THEN** it operates solely from the branch's artifacts (no shared conversation state) and commits its own outputs before the build job starts

#### Scenario: Validator failure fails the job
- **WHEN** lint-story.py or openspec validate exits non-zero inside a phase job
- **THEN** that job fails and the workflow proceeds only to the escalation path

### Requirement: Independent review as a required status check
The workflow SHALL run the reviewer as its own job, on a different model from the builder, prompted to refute the change, and SHALL surface its verdict as a commit status/check suitable for branch-protection required-checks, so that even the human merge is gated on it.

#### Scenario: Reviewer refutes the change
- **WHEN** the review job's verdict is FAIL or CONCERNS
- **THEN** the check is reported as failed, no PR auto-opens (escalation path instead), and the branch cannot be merged while the check is red

### Requirement: PR creation and issue-comment audit trail
On a fully green run the workflow SHALL open a pull request from the work branch whose description contains symptom/intent, root cause or spec summary, the fix, test evidence, and the review verdict, and SHALL post a comment on the triggering issue with the PR link on the first line followed by the run summary; on escalation it SHALL post the findings comment and apply `needs-human` instead.

#### Scenario: Green run produces PR and comment
- **WHEN** all phase jobs and the review check pass
- **THEN** a PR exists with the evidence-bearing description and the issue carries a comment linking it on the first line

#### Scenario: Escalated run leaves an audit trail
- **WHEN** the run ends in escalation at any phase
- **THEN** the issue carries a findings comment identifying the failing gate and the `needs-human` label, and no PR is opened
