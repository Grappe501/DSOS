# Thread Continuity Additions

This bundle adds two continuity controls:

1. `tracking/THREAD_MEMORY_COMPRESSION.md`
   - compact architecture + current-state continuity layer
   - meant for fast reloading by future AI threads

2. `tools/self_verify_bootstrap.py`
   - verifies required tracking, tooling, and runtime files exist
   - writes `tracking/bootstrap_verification_report.json`

## Usage

Run from project root:

```powershell
python tools\self_verify_bootstrap.py
```

If the script exits cleanly, the thread takeover baseline is intact.
If it exits with code 1, required continuity files are missing and should be restored before further coding.
