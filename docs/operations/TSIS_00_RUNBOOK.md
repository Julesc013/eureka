# TSIS-00 Runbook

Run the TSIS foundation checks with:

```bash
python scripts/validate_temporal_semantic_interface_system.py
python scripts/validate_representation_contracts.py
python scripts/validate_semantic_renderer_parity.py
python scripts/validate_renderer_parity_harness.py
python -m unittest tests.contracts.test_temporal_semantic_interface_contracts
python -m unittest tests.scripts.test_validate_temporal_semantic_interface_system
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
```

Do not run full unittest discovery in the AI session for this task.

## Non-Goals

TSIS-00 does not implement the Surface Kernel runtime, deploy, write `site/dist`,
enable live source calls, create top-level renderer/app/service roots, mutate
public/master indexes, perform downloads, OCR, extraction, or model calls, or
claim public launch readiness.
