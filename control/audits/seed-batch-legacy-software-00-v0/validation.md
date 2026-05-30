# Validation

The intended validation lane is:

```text
git diff --check
python scripts/validate_seed_batch_legacy_software.py
focused legacy seed batch tests
cross-stack validators
AIDE Lite checks
```

Full discovery remains a manual or CI gate.
