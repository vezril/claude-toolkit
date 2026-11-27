# Story 13.1: Only the owning run may complete a row

Status: Draft

## Story
As an operator, I want a run that lost its row to be unable to mark it complete, so that a
stale worker cannot close out work it no longer owns.

## Acceptance Criteria
- AC-1 (P0): Given a row re-claimed by another worker, when the stale run finishes, then the
  row is not marked complete.

## Tasks / Subtasks
- [ ] guard the completion write by ownership (AC: 1)
- [ ] test that a re-claimed row refuses the write (AC: 1)
