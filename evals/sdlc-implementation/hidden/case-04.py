"""File uploads."""
import os

ALLOWED = {".png", ".jpg", ".pdf"}
ROOT = "/var/uploads"


def accept(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in ALLOWED


def destination(filename: str) -> str:
    path = os.path.normpath(os.path.join(ROOT, filename))
    if not path.startswith(ROOT + os.sep):
        raise ValueError(f"destination escapes the upload root: {filename}")
    return path
