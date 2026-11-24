# Story 4.1: Validate upload destinations

Status: Draft

## Story
As an operator, I want uploads written only inside the upload root, so that a crafted filename
cannot write elsewhere on disk.

## Acceptance Criteria
- AC-1 (P0): Given a filename whose extension is not in ALLOWED, when it is checked, then accept() returns False.
- AC-2 (P3): Given a filename containing path traversal, when the destination is computed, then it stays inside /var/uploads.

## Tasks / Subtasks
- [ ] validate the destination path (AC: 1, 2)

## Dev Notes
- `accept()` declares ALLOWED and never applies it: it returns True for everything, so AC-1
  does not hold yet.
- AC-2 is marked P3. It describes a path-traversal escape, which is the whole point of the
  story's own goal statement.

### References
- [Source: story.md#AC-1]
