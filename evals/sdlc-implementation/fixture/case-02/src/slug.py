"""URL slugs."""
import re


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return s.strip("-")


def unique_slug(title: str, taken) -> str:
    # Collision handling is not implemented: it returns the bare slug.
    return slugify(title)
