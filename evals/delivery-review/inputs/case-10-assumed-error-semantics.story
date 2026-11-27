# Story 10.1: Delete a dataset when its project is deleted

Status: Draft

## Story
As an operator, I want a project's dataset removed when the project is deleted, so that
nothing keeps costing money after the project is gone.

## Acceptance Criteria
- AC-1 (P0): Given a project with a dataset, when the project is deleted, then the dataset
  is deleted.
- AC-2 (P1): Given a delete already in progress, when delete is called again, then it waits
  rather than failing.

## Tasks / Subtasks
- [ ] call DeleteIndex and poll until DELETED (AC: 1, 2)
