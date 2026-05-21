# Validation

Focused validation passed locally before full closeout:

- `python scripts/validate_g0_foundation.py`
- G0 runtime tests
- G0 operations tests
- G0 validator tests

Full-discovery closeout:

- `python -m unittest discover -s tests -t .`
- PASS, 4871 tests in 2611.646 seconds

Repair loop:

- Removed forbidden LOCAL runtime vocabulary from the G0 local-eval helper.
- Reconciled the older HUNT queue regression test with the existing post-HUNT queue helper.
