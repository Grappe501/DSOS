# Project Map Audit Script

This script is for thread handoff and architecture continuity.

## Purpose
Generate a lightweight audit of:
- project tree
- tracking files present
- Malone files present
- root tools present
- key backend/frontend entrypoints present

## Usage
Run from project root:

```powershell
python tools\project_map_audit.py
```

Optional output path:

```powershell
python tools\project_map_audit.py --output tracking\project_audit_report.json
```

The script should be run at the start of a new thread takeover so the incoming thread can compare the actual codebase against tracking.
