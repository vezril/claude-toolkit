# Story 11.1: Never lose track of a created dataset

Status: Draft

## Story
As an operator, I want every dataset we create recorded against its run, so that nothing we
provision is left unreferenced and billing.

## Acceptance Criteria
- AC-1 (P0): Given a dataset is created, when the run still owns its row, then the row
  records the dataset id.
- AC-2 (P0): Given a dataset is created, when the run no longer owns its row, then the
  dataset is not left unreferenced.

## Tasks / Subtasks
- [ ] record the dataset, or clean it up if the row moved on (AC: 1, 2)
