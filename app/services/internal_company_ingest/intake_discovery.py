"""Scan deterministic intake tree for ingestible files."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DiscoveredFile:
    absolute_path: str
    relative_path: str  # posix, relative to intake root
    folder_segment: str  # first directory under root
    filename: str


def _sha8(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()[:8]


def discover_intake_files(intake_root: str) -> list[DiscoveredFile]:
    """Walk intake_root; include files in subfolders (default model)."""
    root = os.path.abspath(intake_root)
    if not os.path.isdir(root):
        return []
    out: list[DiscoveredFile] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.startswith("."):
                continue
            if name.lower() == "readme.md":
                continue
            abs_p = os.path.join(dirpath, name)
            rel = os.path.relpath(abs_p, root).replace(os.sep, "/")
            parts = rel.split("/", 1)
            folder = parts[0] if len(parts) > 1 else ""
            out.append(
                DiscoveredFile(
                    absolute_path=abs_p,
                    relative_path=rel,
                    folder_segment=folder,
                    filename=name,
                )
            )
    out.sort(key=lambda x: x.relative_path)
    return out


def path_checksum_token(absolute_path: str) -> str:
    return _sha8(os.path.normpath(absolute_path))
