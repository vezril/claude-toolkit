"""Session expiry. The reference adds the seam the test-writer must ASK for, never add."""
import time

SESSION_TTL = 1800


def is_expired(started_at: float, now=None) -> bool:
    current = time.time() if now is None else now
    return current - started_at > SESSION_TTL
