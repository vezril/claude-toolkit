# Story 9.1: Exercise each trust form against the index API

Status: Draft

## Story
As an operator, I want each role-trust form exercised, so that I know which forms the
index service accepts.

## Acceptance Criteria
- AC-1 (P0): Given a list of trust forms, when the suite runs, then each form's outcome is
  recorded as ACCEPTED or REJECTED_BY_POLICY.

## Tasks / Subtasks
- [ ] call StartIndexJob once per form (AC: 1)
