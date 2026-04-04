from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

KEY_PATHS = {
    "tracking": [
        "tracking/current_state.json",
        "tracking/progress.json",
        "tracking/NEXT_PHASE_MASTER_BUILD_PLAN_v0.7.0.md",
        "tracking/malone/MALONE_V1_MASTER_PLAN.md",
        "tracking/malone/malone_manifest_v1.json",
        "tracking/malone/malone_build_map.json",
    ],
    "backend": [
        "app/main.py",
        "app/api/routes.py",
        "app/api/auth_routes.py",
        "app/api/malone_routes.py",
        "app/services/schedule_service.py",
        "app/services/malone_service.py",
        "app/services/intent_service.py",
        "app/services/proposal_service.py",
    ],
    "frontend": [
        "src/App.jsx",
        "src/lib/api.js",
        "src/lib/maloneApi.js",
        "src/pages/SchedulesPage.jsx",
        "src/pages/MalonePage.jsx",
        "src/components/malone/ChatPanel.jsx",
    ],
    "tooling": [
        "tools/scaffold_next_phase.py",
        "tools/scaffold_malone_phase.py",
        "tools/template_registry.json",
        "tools/malone_template_registry.json",
    ],
}

def exists_map(paths: list[str]) -> dict[str, bool]:
    return {p: (PROJECT_ROOT / p).exists() for p in paths}

def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob("*") if p.is_file())

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate DSOS project map audit.")
    parser.add_argument("--output", default="tracking/project_audit_report.json")
    args = parser.parse_args()

    report = {
        "project_root": str(PROJECT_ROOT),
        "counts": {
            "tracking_files": count_files(PROJECT_ROOT / "tracking"),
            "tool_files": count_files(PROJECT_ROOT / "tools"),
            "app_files": count_files(PROJECT_ROOT / "app"),
            "src_files": count_files(PROJECT_ROOT / "src"),
        },
        "presence": {section: exists_map(paths) for section, paths in KEY_PATHS.items()},
    }

    output_path = PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote audit report to {output_path}")

if __name__ == "__main__":
    main()
