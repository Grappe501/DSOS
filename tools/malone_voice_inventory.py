#!/usr/bin/env python3
"""
Deterministic scan of active-lane paths for voice / audio / streaming related terms.

Active lanes: app/, src/, tracking/, tests/ (repository root-relative).
Outputs: tracking/reports/malone_voice_inventory.json and .md
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

ACTIVE_LANES = ("app", "src", "tracking", "tests")

SKIP_DIR_NAMES = {
    "__pycache__",
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
}

TEXT_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".md",
    ".json",
    ".sql",
    ".yml",
    ".yaml",
    ".toml",
    ".txt",
}

# (group_id, human label, regex pattern with IGNORECASE)
TERM_GROUPS: list[tuple[str, str, re.Pattern[str]]] = [
    ("voice", "voice", re.compile(r"\bvoice\b", re.I)),
    ("speech", "speech", re.compile(r"\bspeech\b", re.I)),
    ("audio", "audio", re.compile(r"\baudio\b", re.I)),
    ("microphone", "microphone", re.compile(r"microphone|\bmic\b", re.I)),
    ("media_recorder", "media recorder / MediaRecorder", re.compile(r"mediarecorder|media\s+recorder", re.I)),
    ("websocket", "websocket", re.compile(r"websocket", re.I)),
    ("streaming", "streaming", re.compile(r"streaming", re.I)),
    ("playback", "playback", re.compile(r"playback", re.I)),
    ("abort", "abort", re.compile(r"\babort\b", re.I)),
    ("cancel", "cancel", re.compile(r"\bcancel\b", re.I)),
]


def _iter_files(root: Path) -> list[Path]:
    out: list[Path] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(REPO_ROOT)
        except ValueError:
            continue
        parts = set(rel.parts)
        if parts & SKIP_DIR_NAMES:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        out.append(path)
    return out


def _scan_file(path: Path) -> dict[str, list[int]]:
    """Return line numbers (1-based) per group id that matched."""
    hits: dict[str, list[int]] = {gid: [] for gid, _, _ in TERM_GROUPS}
    try:
        raw = path.read_bytes()
    except OSError:
        return hits
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    for lineno, line in enumerate(lines, start=1):
        for gid, _, pattern in TERM_GROUPS:
            if pattern.search(line):
                hits[gid].append(lineno)
    return hits


def _file_checksum(path: Path) -> str:
    h = hashlib.sha256()
    try:
        h.update(path.read_bytes())
    except OSError:
        return ""
    return h.hexdigest()[:16]


def main() -> int:
    scanned_files: list[str] = []
    file_hits: dict[str, dict[str, list[int]]] = {}

    for lane in ACTIVE_LANES:
        lane_root = REPO_ROOT / lane
        for fpath in _iter_files(lane_root):
            rel = fpath.as_posix().replace("\\", "/")
            if not rel.startswith(f"{lane}/"):
                rel = "/".join(fpath.relative_to(REPO_ROOT).parts)
            scanned_files.append(rel)
            per = _scan_file(fpath)
            if any(per.values()):
                file_hits[rel] = {k: v for k, v in per.items() if v}

    scanned_files.sort()

    summary: dict[str, dict[str, int]] = {}
    for gid, label, _ in TERM_GROUPS:
        file_count = sum(1 for fh in file_hits.values() if gid in fh)
        line_count = sum(len(fh.get(gid, [])) for fh in file_hits.values())
        summary[gid] = {"label": label, "files_with_matches": file_count, "match_lines_total": line_count}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "schema_version": "malone_voice_inventory_v1",
        "generated_at_utc": now,
        "repo_root": str(REPO_ROOT),
        "active_lanes": [f"{x}/" for x in ACTIVE_LANES],
        "scanned_text_files": len(scanned_files),
        "term_groups": {gid: {"label": label} for gid, label, _ in TERM_GROUPS},
        "summary_by_term": summary,
        "files_with_any_match": sorted(file_hits.keys()),
        "matches": file_hits,
    }

    out_json = REPO_ROOT / "tracking" / "reports" / "malone_voice_inventory.json"
    out_md = REPO_ROOT / "tracking" / "reports" / "malone_voice_inventory.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines_md: list[str] = [
        "# Malone voice term inventory (deterministic scan)",
        "",
        f"- Generated (UTC): `{now}`",
        f"- Text files scanned: **{len(scanned_files)}** under `{', '.join(ACTIVE_LANES)}/`",
        "",
        "## Summary by term",
        "",
        "| Term group | Files | Lines matched |",
        "|------------|------:|--------------:|",
    ]
    for gid, label, _ in TERM_GROUPS:
        s = summary[gid]
        lines_md.append(
            f"| {label} (`{gid}`) | {s['files_with_matches']} | {s['match_lines_total']} |"
        )
    lines_md.extend(
        [
            "",
            "## Files with any match (sorted)",
            "",
        ]
    )
    for rel in sorted(file_hits.keys()):
        ch = _file_checksum(REPO_ROOT / Path(rel))
        lines_md.append(f"- `{rel}` (sha256-16: `{ch}`)")
        fh = file_hits[rel]
        for gid, _, _ in TERM_GROUPS:
            if gid not in fh:
                continue
            nums = fh[gid]
            preview = ", ".join(str(n) for n in nums[:12])
            more = f" (+{len(nums) - 12} more)" if len(nums) > 12 else ""
            lines_md.append(f"  - **{gid}**: lines {preview}{more}")
    lines_md.append("")
    out_md.write_text("\n".join(lines_md), encoding="utf-8")

    print(f"Wrote {out_json.relative_to(REPO_ROOT)}")
    print(f"Wrote {out_md.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
