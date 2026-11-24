# Story 2.1: Make slugs unique

Status: Draft

## Story
As an author, I want a unique slug per post, so that two posts with the same title both resolve.

## Acceptance Criteria
- AC-1 (P0): Given a title whose slug is already taken, when a slug is generated, then it gets a numeric suffix that is not taken.
- AC-2 (P1): Given a title whose slug is free, when a slug is generated, then it is returned unchanged.

## Tasks / Subtasks
- [ ] suffix colliding slugs in unique_slug() (AC: 1, 2)

## Dev Notes
- AC-2 already holds for the current code. A test for it alone will pass immediately, which is
  not a red hand-off; AC-1 is the behaviour that does not exist.

### References
- [Source: story.md#AC-1]
