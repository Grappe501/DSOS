from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "tracking" / "scaffold_size_audit_report.json"

EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    "Thumbs.db",
}

EXPECTED_ACTIVE_ROOTS = {
    "backend": "app",
    "frontend": "src",
}

PASSIVE_ROOT_CANDIDATES = {
    "backend": ["backend/app"],
    "frontend": ["frontend/src"],
}

TRACKING_EXPECTATION_FILES = [
    "tracking/file_map_v0.7.0.json",
    "tracking/build_map.json",
    "tracking/scaffold_targets_v0.7.0.json",
]


def is_excluded_dir(path: Path) -> bool:
    return path.name in EXCLUDED_DIR_NAMES


def is_excluded_file(path: Path) -> bool:
    return path.name in EXCLUDED_FILE_NAMES


def iter_project_files(root: Path):
    for path in root.rglob("*"):
        if not path.exists():
            continue
        if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
            continue
        if path.is_dir():
            continue
        if is_excluded_file(path):
            continue
        yield path


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{size} B"


def safe_rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def collect_directory_sizes() -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}

    def ensure_dir(path: Path) -> dict[str, Any]:
        rel = "." if path == PROJECT_ROOT else safe_rel(path)
        entry = stats.setdefault(
            rel,
            {
                "path": rel,
                "file_count": 0,
                "total_bytes": 0,
            },
        )
        return entry

    ensure_dir(PROJECT_ROOT)

    for file_path in iter_project_files(PROJECT_ROOT):
        size = file_path.stat().st_size
        parent = file_path.parent
        while True:
            entry = ensure_dir(parent)
            entry["file_count"] += 1
            entry["total_bytes"] += size
            if parent == PROJECT_ROOT:
                break
            parent = parent.parent

    for entry in stats.values():
        entry["total_size_human"] = format_bytes(entry["total_bytes"])

    return stats


def collect_largest_files(limit: int = 50) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in iter_project_files(PROJECT_ROOT):
        size = path.stat().st_size
        rows.append(
            {
                "path": safe_rel(path),
                "bytes": size,
                "size_human": format_bytes(size),
            }
        )
    rows.sort(key=lambda item: item["bytes"], reverse=True)
    return rows[:limit]


def collect_top_level_summary(directory_sizes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for child in sorted(PROJECT_ROOT.iterdir(), key=lambda p: p.name.lower()):
        if child.name in EXCLUDED_DIR_NAMES:
            continue
        if child.is_dir():
            rel = safe_rel(child)
            entry = directory_sizes.get(rel, {"file_count": 0, "total_bytes": 0, "total_size_human": "0.00 B"})
            summary.append(
                {
                    "path": rel,
                    "kind": "directory",
                    "file_count": entry["file_count"],
                    "bytes": entry["total_bytes"],
                    "size_human": entry["total_size_human"],
                }
            )
        elif child.is_file() and not is_excluded_file(child):
            size = child.stat().st_size
            summary.append(
                {
                    "path": child.name,
                    "kind": "file",
                    "file_count": 1,
                    "bytes": size,
                    "size_human": format_bytes(size),
                }
            )
    summary.sort(key=lambda item: item["bytes"], reverse=True)
    return summary


def load_json_if_present(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": str(exc), "path": safe_rel(path)}


def collect_expected_paths() -> dict[str, Any]:
    expected_files: set[str] = set()
    notes: list[str] = []
    file_map = load_json_if_present(PROJECT_ROOT / "tracking" / "file_map_v0.7.0.json")
    build_map = load_json_if_present(PROJECT_ROOT / "tracking" / "build_map.json")
    scaffold_targets = load_json_if_present(PROJECT_ROOT / "tracking" / "scaffold_targets_v0.7.0.json")

    if isinstance(file_map, dict):
        for section in ("backend", "frontend"):
            block = file_map.get(section, {})
            if not isinstance(block, dict):
                continue
            for key in ("create", "update"):
                for item in block.get(key, []):
                    if isinstance(item, dict) and item.get("path"):
                        expected_files.add(str(item["path"]).replace("\\", "/"))

    if isinstance(scaffold_targets, dict):
        for target in scaffold_targets.get("targets", []):
            if not isinstance(target, dict):
                continue
            for action in target.get("actions", []):
                if not isinstance(action, dict):
                    continue
                path = action.get("path")
                if path:
                    expected_files.add(str(path).replace("\\", "/"))

    if isinstance(build_map, dict):
        structure = build_map.get("structure")
        if isinstance(structure, dict):
            notes.append("build_map.json includes raw structure output but is too broad for exact expectation matching")

    present = []
    missing = []
    for rel in sorted(expected_files):
        if (PROJECT_ROOT / rel).exists():
            present.append(rel)
        else:
            missing.append(rel)

    return {
        "tracking_sources": TRACKING_EXPECTATION_FILES,
        "expected_file_count": len(expected_files),
        "present_expected_files": present,
        "missing_expected_files": missing,
        "notes": notes,
    }


def collect_root_alignment(directory_sizes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    for area, active_root in EXPECTED_ACTIVE_ROOTS.items():
        active_path = PROJECT_ROOT / active_root
        active_exists = active_path.exists()
        active_entry = directory_sizes.get(active_root, {"total_bytes": 0, "file_count": 0, "total_size_human": "0.00 B"})
        passive_rows = []
        for candidate in PASSIVE_ROOT_CANDIDATES.get(area, []):
            candidate_path = PROJECT_ROOT / candidate
            if not candidate_path.exists():
                continue
            candidate_entry = directory_sizes.get(candidate, {"total_bytes": 0, "file_count": 0, "total_size_human": "0.00 B"})
            passive_rows.append(
                {
                    "path": candidate,
                    "exists": True,
                    "file_count": candidate_entry["file_count"],
                    "bytes": candidate_entry["total_bytes"],
                    "size_human": candidate_entry["total_size_human"],
                }
            )

        finding = {
            "area": area,
            "active_root": {
                "path": active_root,
                "exists": active_exists,
                "file_count": active_entry["file_count"],
                "bytes": active_entry["total_bytes"],
                "size_human": active_entry["total_size_human"],
            },
            "passive_root_candidates": passive_rows,
            "status": "ok",
            "notes": [],
        }

        if passive_rows:
            finding["status"] = "review"
            finding["notes"].append(
                "Multiple root candidates exist for this layer. Treat the active root as source of truth unless the runtime proves otherwise."
            )

        findings.append(finding)

    return {"root_alignment": findings}


def collect_flags(directory_sizes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []

    def add(level: str, code: str, message: str, path: str | None = None) -> None:
        flags.append(
            {
                "level": level,
                "code": code,
                "message": message,
                "path": path,
            }
        )

    for candidate in ("backend/app", "frontend/src", "dsos_replacements", "test.db", "runtime_v5.db"):
        candidate_path = PROJECT_ROOT / candidate
        if candidate_path.exists():
            add(
                "review",
                "parallel_or_generated_artifact",
                "Parallel roots or generated artifacts exist and should be explicitly classified as active, passive, or disposable.",
                candidate,
            )

    app_size = directory_sizes.get("app", {}).get("total_bytes", 0)
    backend_app_size = directory_sizes.get("backend/app", {}).get("total_bytes", 0)
    src_size = directory_sizes.get("src", {}).get("total_bytes", 0)
    frontend_src_size = directory_sizes.get("frontend/src", {}).get("total_bytes", 0)

    if app_size and backend_app_size:
        add(
            "review",
            "dual_backend_roots",
            "Both app/ and backend/app/ contain code. Current runtime imports app/, so backend/app/ should be treated as passive until reconciled.",
            "app | backend/app",
        )

    if src_size and frontend_src_size:
        add(
            "review",
            "dual_frontend_roots",
            "Both src/ and frontend/src/ contain code. Current runtime and tooling reference src/, so frontend/src/ should be treated as passive until reconciled.",
            "src | frontend/src",
        )

    return flags


def build_report(limit: int = 50) -> dict[str, Any]:
    directory_sizes = collect_directory_sizes()
    report = {
        "project_root": str(PROJECT_ROOT),
        "excluded_dir_names": sorted(EXCLUDED_DIR_NAMES),
        "excluded_file_names": sorted(EXCLUDED_FILE_NAMES),
        "root_summary": {
            "tracked_file_count": directory_sizes["."]["file_count"],
            "tracked_total_bytes": directory_sizes["."]["total_bytes"],
            "tracked_total_size_human": directory_sizes["."]["total_size_human"],
        },
        "top_level_summary": collect_top_level_summary(directory_sizes),
        "largest_files": collect_largest_files(limit=limit),
        "largest_directories": sorted(
            [entry for key, entry in directory_sizes.items() if key != "."],
            key=lambda item: item["total_bytes"],
            reverse=True,
        )[:limit],
        "expected_vs_present": collect_expected_paths(),
        "root_alignment": collect_root_alignment(directory_sizes)["root_alignment"],
        "flags": collect_flags(directory_sizes),
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a scaffold size and placement audit for DSOS.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    report = build_report(limit=max(10, args.limit))
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote scaffold size audit to {output_path}")


if __name__ == "__main__":
    main()
