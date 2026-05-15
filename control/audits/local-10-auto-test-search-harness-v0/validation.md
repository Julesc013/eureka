# Validation

LOCAL-10 validation is performed with:

```bash
python scripts/validate_local_auto_test_harness.py
```

Focused tests cover suite definitions, runner behavior, reports, latency,
safety, and operation scripts. The known runtime leakage gate warning remains
recorded separately.

Observed validation summary:

- JSON policy/inventory/report parsing: pass.
- `python scripts/validate_local_auto_test_harness.py --json`: pass with warnings.
- Manual localhost auto-test and auto-search smoke: pass.
- Focused LOCAL-10 tests: pass.
- LOCAL-04 through LOCAL-06 validators: pass with warnings.
- LOCAL-07 through LOCAL-09 validators: fail only on superseded queue-pointer expectations.
- LOCAL-00 through LOCAL-02 validators: fail on phase-pinned latest-task/forbidden-path expectations.
- `python scripts/check_architecture_boundaries.py`: pass.
- Runtime leakage audit/validation: fail with pre-existing findings; LOCAL-10 did not increase leakage.
- Full unittest discovery: fail_other.
