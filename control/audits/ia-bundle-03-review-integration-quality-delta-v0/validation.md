# Validation

Planned validation:

```text
git status --short
git diff --check
python -m json.tool control/inventory/connectors/internet_archive_review_integration_policy.json
python -m json.tool control/inventory/connectors/internet_archive_quality_delta_policy.json
python -m json.tool control/inventory/connectors/internet_archive_postmortem_policy.json
python -m json.tool control/inventory/connectors/internet_archive_review_output_policy.json
python -m json.tool control/inventory/connectors/internet_archive_review_path_policy.json
python -m json.tool control/inventory/connectors/internet_archive_review_truth_policy.json
python -m json.tool control/audits/ia-bundle-03-review-integration-quality-delta-v0/ia_bundle_03_report.json
python scripts/validate_ia_review_integration.py
python -m unittest tests.connectors.test_internet_archive_review_integration
python -m unittest tests.operations.test_ia_review_integration_scripts
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

Final command results are reported in the task response.

Observed results:

- `git diff --check`: PASS with line-ending advisories only.
- Required JSON syntax checks: PASS.
- `python scripts/validate_ia_metadata_connector_foundation.py`: PASS.
- `python scripts/validate_ia_metadata_live_probe.py`: PASS.
- `python scripts/validate_ia_review_integration.py`: PASS.
- `python -m unittest tests.connectors.test_internet_archive_review_integration`: PASS, 14 tests.
- `python -m unittest tests.operations.test_ia_review_integration_scripts`: PASS, 7 tests.
- `python -m unittest discover -s tests -t .`: PASS, 2584 tests.
- `python scripts/check_architecture_boundaries.py`: PASS.
- Core Track B validators: PASS.
- AIDE Lite doctor/validate/test/selftest/eval/review-pack/adapter validate: PASS.
- AIDE Lite verify: WARN with 0 errors; warnings are optional/future references.
