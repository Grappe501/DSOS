#!/usr/bin/env python3
"""
Scaffold the next DSOS phase from machine-readable tracking files.
v0: creates directories, placeholder files, and planning artifacts.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

def touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

def resolve_backend_root() -> str:
    for option in ("backend/app", "app"):
        if (ROOT / option).exists():
            return option
    return "backend/app"

def resolve_frontend_root() -> str:
    for option in ("frontend/src", "src"):
        if (ROOT / option).exists():
            return option
    return "frontend/src"

def run_action(action: dict[str, Any], artifacts: dict[str, Any], backend_root: str, frontend_root: str) -> str:
    action_type = action["type"]
    raw_path = action.get("path", "")
    path_str = raw_path.format(backend_root=backend_root, frontend_root=frontend_root)
    path = ROOT / path_str if path_str else None

    if action_type == "mkdir":
        assert path is not None
        path.mkdir(parents=True, exist_ok=True)
        return f"mkdir {path_str}"

    if action_type == "touch":
        assert path is not None
        touch(path)
        return f"touch {path_str}"

    if action_type == "write_json":
        assert path is not None
        source = action["source"]
        _, key = source.split(".", 1)
        write_json(path, artifacts[key])
        return f"write_json {path_str}"

    raise ValueError(f"Unsupported action type: {action_type}")

def load_artifacts() -> dict[str, Any]:
    tracking = ROOT / "tracking"
    return {
        "phase_manifest": read_json(tracking / "phase_manifest_v0.7.0.json"),
        "file_map": read_json(tracking / "file_map_v0.7.0.json"),
        "scaffold_targets": read_json(tracking / "scaffold_targets_v0.7.0.json"),
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", default="v0.7.0")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.phase != "v0.7.0":
        raise SystemExit("This initial scaffold script is pinned to v0.7.0.")

    artifacts = load_artifacts()
    backend_root = resolve_backend_root()
    frontend_root = resolve_frontend_root()
    targets = artifacts["scaffold_targets"]["targets"]

    summary: list[str] = []
    for target in targets:
        for action in target["actions"]:
            msg = run_action(action, artifacts, backend_root, frontend_root) if not args.dry_run else f"dry-run {action['type']} {action.get('path','')}"
            summary.append(msg)

    print("Scaffold complete.")
    print(f"Backend root: {backend_root}")
    print(f"Frontend root: {frontend_root}")
    print("Actions:")
    for item in summary:
        print(f"- {item}")

if __name__ == "__main__":
    main()
