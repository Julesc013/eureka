# Validation Report

Task: `SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-08`

External evidence ingested:

```text
run_id: source_snapshot_full_discovery_rerun_08
status: fail
tests_run: 5676
failures: 23
errors: 0
current_to_head: true
```

Ingest validation:

- PASS: `python scripts/check_full_discovery.py --run-id source_snapshot_full_discovery_rerun_08 --json`
- PASS: external summary parsed from `../eureka-test-runs/source_snapshot_full_discovery_rerun_08/full_unittest_summary.json`
- PASS: summary HEAD matches current `dev` HEAD.
- PASS: compact failure evidence classified without copying raw full logs into the repo.
- PASS: `python -m json.tool docs\reference\validation\source_snapshot_full_discovery_ingest_08\FULL_DISCOVERY_SUMMARY_INDEX.json`
- PASS: `python -m json.tool docs\reference\validation\source_snapshot_full_discovery_ingest_08\FAILURE_FAMILY_INDEX.json`
- PASS: `git diff --check`
- PASS: `py -3 .aide/scripts/aide_lite.py doctor`
- PASS: `py -3 .aide/scripts/aide_lite.py validate`
- PASS: `python scripts/check_architecture_boundaries.py`
- PASS: `python scripts/check_generated_artifact_cleanliness.py --check --json`
- PASS: `py -3 scripts/eureka_test_select.py --changed --failed-first --json`
- NOT RUN: `python -m unittest discover -s tests -t .` inside the AI session.

The changed-path selector requested only the static preflight lane for this
docs-only ingest package.
