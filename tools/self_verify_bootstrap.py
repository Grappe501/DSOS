from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TRACKING = [
    "tracking/current_state.json",
    "tracking/progress.json",
    "tracking/NEXT_THREAD_PROMPT.md",
    "tracking/HANDOFF_MIGRATION_MESSAGE.md",
    "tracking/handoff_state_snapshot.json",
    "tracking/malone/MALONE_V1_MASTER_PLAN.md",
    "tracking/malone/malone_manifest_v1.json",
]

REQUIRED_TOOLS = [
    "tools/project_map_audit.py",
]

REQUIRED_RUNTIME = [
    "app/main.py",
    "app/api/routes.py",
    "app/api/auth_routes.py",
    "app/api/malone_routes.py",
    "src/App.jsx",
    "src/lib/api.js",
    "src/lib/maloneApi.js",
    "src/pages/SchedulesPage.jsx",
    "src/pages/MalonePage.jsx",
]

def exists_report(paths: list[str]) -> dict[str, bool]:
    return {path: (PROJECT_ROOT / path).exists() for path in paths}

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def main() -> None:
    tracking_report = exists_report(REQUIRED_TRACKING)
    tools_report = exists_report(REQUIRED_TOOLS)
    runtime_report = exists_report(REQUIRED_RUNTIME)

    current_state_path = PROJECT_ROOT / "tracking" / "current_state.json"
    progress_path = PROJECT_ROOT / "tracking" / "progress.json"

    current_state = load_json(current_state_path) if current_state_path.exists() else None
    progress = load_json(progress_path) if progress_path.exists() else None

    summary = {
        "project_root": str(PROJECT_ROOT),
        "tracking_ok": all(tracking_report.values()),
        "tools_ok": all(tools_report.values()),
        "runtime_ok": all(runtime_report.values()),
        "tracking_presence": tracking_report,
        "tool_presence": tools_report,
        "runtime_presence": runtime_report,
        "current_state": current_state,
        "progress": progress,
    }

    output_path = PROJECT_ROOT / "tracking" / "bootstrap_verification_report.json"
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== DSOS BOOTSTRAP VERIFICATION ===")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Tracking OK: {summary['tracking_ok']}")
    print(f"Tools OK: {summary['tools_ok']}")
    print(f"Runtime OK: {summary['runtime_ok']}")
    print(f"Wrote: {output_path}")

    if not summary["tracking_ok"] or not summary["tools_ok"] or not summary["runtime_ok"]:
        print("WARNING: Required continuity files are missing.")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
