# Story 3.1: Expire sessions after the TTL

Status: Draft

## Story
As a security reviewer, I want sessions to expire, so that an abandoned session cannot be reused.

## Acceptance Criteria
- AC-1 (P0): Given a session started more than SESSION_TTL ago, when checked, then it is expired.
- AC-2 (P0): Given a session started within SESSION_TTL, when checked, then it is not expired.

## Tasks / Subtasks
- [ ] expire sessions past the TTL (AC: 1, 2)

## Dev Notes
- `is_expired` calls `time.time()` directly. Testing it deterministically needs an injectable
  time source, which is a change to production code.

### References
- [Source: story.md#AC-1]
