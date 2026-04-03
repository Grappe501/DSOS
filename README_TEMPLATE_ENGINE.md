# Template-Aware Scaffold Engine Bundle

This bundle upgrades `tools/scaffold_next_phase.py` from placeholder creation to starter-code generation.

## Included
- `tools/scaffold_next_phase.py` — upgraded engine
- `tools/templates/...` — starter templates
- `tracking/scaffold_targets_v0.7.0.json` — template-driven target map

## Safe usage
```powershell
python tools\scaffold_next_phase.py --dry-run
python tools\scaffold_next_phase.py
```

## Force rewrite of scaffold-generated or existing files
```powershell
python tools\scaffold_next_phase.py --force --only backend_scaffold
```

The engine will skip non-empty files unless `--force` is used.
