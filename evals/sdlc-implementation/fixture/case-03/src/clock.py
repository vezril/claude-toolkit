"""Session expiry."""
import time

SESSION_TTL = 1800


def is_expired(started_at: float) -> bool:
    # Reads the wall clock directly: there is no seam to inject a time source.
    return time.time() - started_at > SESSION_TTL
