from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROGRESS_PATH = PROJECT_ROOT / "tracking" / "progress.json"
REPORT_PATH = PROJECT_ROOT / "tracking" / "update_progress_report.json"


def task_is_done(task: Any) -> bool:
    if isinstance(task, dict):
        if "done" in task:
            return bool(task["done"])
        status = str(task.get("status", "")).strip().lower()
        return status in {"done", "complete", "completed", "shipped"}
    if isinstance(task, str):
        return False
    return False


def normalize_phase_progress(phase_payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    tasks = phase_payload.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        existing = phase_payload.get("progress", 0)
        return int(existing), {
            "task_count": 0,
            "done_count": 0,
            "mode": "preserved_existing_progress",
        }

    if all(isinstance(task, str) for task in tasks):
        existing = phase_payload.get("progress", 0)
        return int(existing), {
            "task_count": len(tasks),
            "done_count": None,
            "mode": "string_tasks_preserved_existing_progress",
        }

    done_count = sum(1 for task in tasks if task_is_done(task))
    computed = int((done_count / len(tasks)) * 100)
    return computed, {
        "task_count": len(tasks),
        "done_count": done_count,
        "mode": "computed_from_structured_tasks",
    }


def update_progress() -> dict[str, Any]:
    data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    report: dict[str, Any] = {"phases": {}}

    for phase_name, payload in data.items():
        progress, meta = normalize_phase_progress(payload)
        payload["progress"] = progress
        report["phases"][phase_name] = {
            "progress": progress,
            **meta,
        }

    PROGRESS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = update_progress()
    print("Progress updated.")
    print(json.dumps(result, indent=2))
