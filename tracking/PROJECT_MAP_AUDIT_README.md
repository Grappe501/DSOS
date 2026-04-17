# Project Map Audit Script

This script is for thread handoff and architecture continuity.

## Purpose
Generate a lightweight audit of:
- project tree
- tracking files present
- Malone files present
- root tools present
- key backend/frontend entrypoints present

## Companion audit
Run `python tools/scaffold_size_audit.py` immediately after the project map audit.

The size audit adds:
- folder and file size mapping
- active vs passive root review
- expected vs present path comparison from tracking artifacts
- exclusion of `.git`, `.venv`, and `node_modules` noise

## Usage
Run from project root:

```powershell
python tools\project_map_audit.py
python tools\scaffold_size_audit.py
```

Optional output paths:

```powershell
python tools\project_map_audit.py --output tracking\project_audit_report.json
python tools\scaffold_size_audit.py --output tracking\scaffold_size_audit_report.json
```

These scripts should be run at the start of a new thread before coding.
