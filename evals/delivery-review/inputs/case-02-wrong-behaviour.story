# Story 2.1: Reject expired tokens

Status: Draft

## Story
As a user, I want expired tokens rejected, so that a stolen token stops working.

## Acceptance Criteria
- AC-1 (P0): Given a token whose exp is in the past, when verified, then verification fails.

## Tasks / Subtasks
- [ ] compare exp against now (AC: 1)
