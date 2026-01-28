import os
import hashlib
from urllib.parse import urlparse
from typing import Optional


MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def guess_ext(url: str, mime: Optional[str]) -> str:
    if mime in MIME_TO_EXT:
        return MIME_TO_EXT[mime]
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext if ext else ".img"


def ensure_dirs(*paths: str) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)
