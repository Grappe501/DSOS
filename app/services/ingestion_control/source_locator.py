"""Resolve and validate filesystem paths for ingest inputs."""

from __future__ import annotations

import os
from pathlib import Path


def resolve_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def path_exists(path: str) -> bool:
    return Path(path).is_file()
