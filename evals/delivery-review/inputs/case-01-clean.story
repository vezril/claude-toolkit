# Story 1.1: Cap the retry backoff

Status: Draft

## Story
As an operator, I want retry delays capped, so that a long outage does not stall the queue.

## Acceptance Criteria
- AC-1 (P0): Given many failed attempts, when backoff is computed, then it never exceeds MAX_DELAY.
- AC-2 (P2): Given a successful call, when logged, then the attempt count appears in the log line.

## Tasks / Subtasks
- [ ] cap the delay (AC: 1, 2)
