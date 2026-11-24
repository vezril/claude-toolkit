# Story 1.1: Apply tax to the cart total

Status: Draft

## Story
As a shopper, I want tax included in the total, so that the price I see is the price I pay.

## Acceptance Criteria
- AC-1 (P0): Given a cart with a subtotal, when the total is computed, then it equals subtotal * (1 + TAX_RATE).
- AC-2 (P1): Given an empty cart, when the total is computed, then it is 0.
- AC-3 (P3): Given a total, when displayed, then it is rounded to two decimal places for presentation.

## Tasks / Subtasks
- [ ] apply the tax rate in total() (AC: 1, 2, 3)

## Dev Notes
- `TAX_RATE` already exists in `src/cart.py` and is currently 0.0.

### References
- [Source: story.md#AC-1]
