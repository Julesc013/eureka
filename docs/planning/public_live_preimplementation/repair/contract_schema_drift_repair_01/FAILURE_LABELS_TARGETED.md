# Failure Labels Targeted

| Family | Test label | Test module/file | Original failure text | Current focused reproduction | Current status | Confidence |
|---|---|---|---|---|---|---|
| `contract_schema_drift` / `unittest-af0abc3ea9a15727` | `test_cli_json_passes`; `test_validator_passes` | `tests/scripts/test_validate_temporal_semantic_interface_system.py` | TSIS validator reported `TSIS-00 must not add runtime phase file` for `runtime/surface/cache_key.py`, `runtime/surface/fallback.py`, `runtime/surface/kernel.py`, and `runtime/surface/output_policy.py`. | `python -m unittest tests.scripts.test_validate_temporal_semantic_interface_system`; `python scripts/validate_temporal_semantic_interface_system.py --json` | PASS after repair | High |

## External Evidence

The ingest inventory mapped `contract_schema_drift` to:

```text
tests.scripts.test_validate_temporal_semantic_interface_system
```

The queue-handoff repair reclassified the remaining TSIS failure as
contract/schema drift because the validator still assumed an earlier phase.

## Current Focused Evidence

Before repair, the current focused validator failed with:

```text
TSIS-00 must not add runtime phase file: runtime/surface/cache_key.py
TSIS-00 must not add runtime phase file: runtime/surface/fallback.py
TSIS-00 must not add runtime phase file: runtime/surface/kernel.py
TSIS-00 must not add runtime phase file: runtime/surface/output_policy.py
```

After repair, both focused commands pass.

