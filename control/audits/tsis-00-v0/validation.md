# Validation

Focused validation for TSIS-00:

```text
python scripts/validate_temporal_semantic_interface_system.py --json
python -m unittest tests.contracts.test_temporal_semantic_interface_contracts tests.scripts.test_validate_temporal_semantic_interface_system
```

Full unittest discovery is not run by policy.
