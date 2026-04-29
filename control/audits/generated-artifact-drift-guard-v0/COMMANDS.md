# Commands

Primary drift guard commands:

```bash
python scripts/check_generated_artifact_drift.py
python scripts/check_generated_artifact_drift.py --json
python scripts/check_generated_artifact_drift.py --list
```

Artifact-scoped example:

```bash
python scripts/check_generated_artifact_drift.py --artifact public_data_summaries
```

The guard delegates to existing owner checks:

- `python scripts/generate_public_data_summaries.py --check`
- `python scripts/generate_compatibility_surfaces.py --check`
- `python scripts/generate_static_resolver_demos.py --check`
- `python scripts/generate_static_snapshot.py --check`
- `python scripts/validate_static_snapshot.py`
- `python site/build.py --check`
- `python site/validate.py`
- `python scripts/generate_python_oracle_golden.py --check`
- `python scripts/generate_public_alpha_rehearsal_evidence.py --check`
- `python scripts/validate_publication_inventory.py`
- `python -m unittest tests.operations.test_test_eval_operating_layer`
- `python -m unittest tests.hardening.test_aide_test_registry_consistency`

