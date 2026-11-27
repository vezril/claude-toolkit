# Story 12.1: Clean up a dataset whose row disappeared

Status: Draft

## Story
As an operator, I want a dataset deleted when its row was purged mid-provision, so that we do
not pay for something nothing references.

## Acceptance Criteria
- AC-1 (P0): Given a row purged during provisioning, when the dataset finishes creating,
  then the dataset is deleted.
- AC-2 (P1): Given cleanup is running, when another request arrives, then that request is
  served normally.

## Tasks / Subtasks
- [ ] wait for the dataset to leave CREATING, then delete it (AC: 1)
- [ ] keep the service responsive while waiting (AC: 2)
