# DSOS Template Registry Scaffold Engine

This bundle upgrades the scaffold engine from:
- static target-to-template file creation

to:
- template registry + manifest-rule expansion
- feature-slice scaffolding
- machine-readable automation growth

## New files
- `tools/scaffold_next_phase.py`
- `tools/template_registry.json`
- `tracking/manifest_rules_v0.7.0.json`
- updated `tracking/phase_manifest_v0.7.0.json`
- updated `tracking/scaffold_targets_v0.7.0.json`

## How it works
1. `tracking/scaffold_targets_v0.7.0.json` defines runnable targets.
2. `tracking/manifest_rules_v0.7.0.json` defines feature slices.
3. `tools/template_registry.json` maps template ids to template files and output paths.
4. `tools/scaffold_next_phase.py` expands slices into file actions and renders starter code.

## Commands

Run full phase dry-run:

```powershell
python tools\scaffold_next_phase.py --dry-run
```

Run one target only:

```powershell
python tools\scaffold_next_phase.py --target phase_core --dry-run
```

Run one slice only:

```powershell
python tools\scaffold_next_phase.py --slice approval_workflow --dry-run
```

Force write starter code into placeholder-like files:

```powershell
python tools\scaffold_next_phase.py --force --slice audit_v2
```
