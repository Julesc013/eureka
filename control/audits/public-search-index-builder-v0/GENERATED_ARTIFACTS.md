# Generated Artifacts

`data/public_index` is generated, committed, and drift-checked.

Generator:

```powershell
python scripts/build_public_search_index.py --rebuild
```

Checks:

```powershell
python scripts/build_public_search_index.py --check
python scripts/validate_public_search_index.py
python scripts/check_generated_artifact_drift.py --artifact public_search_index
```

Manual edits are not allowed. Change source inputs or generator code, rebuild,
and review the diff.
