# Story 4.1: Reject out-of-range ports

Status: Draft

## Story
As an operator, I want bad ports rejected, so that a typo fails fast.

## Acceptance Criteria
- AC-1 (P0): Given a port above 65535, when parsed, then a ValueError is raised.

## Tasks / Subtasks
- [ ] range-check the port (AC: 1)
