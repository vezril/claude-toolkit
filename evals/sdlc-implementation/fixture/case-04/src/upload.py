"""File uploads."""
import os

ALLOWED = {".png", ".jpg", ".pdf"}


def accept(filename: str) -> bool:
    # The allow-list is declared but never applied: everything is accepted.
    return True


def destination(filename: str) -> str:
    # Joins the user-supplied name straight onto the upload root.
    return os.path.join("/var/uploads", filename)
