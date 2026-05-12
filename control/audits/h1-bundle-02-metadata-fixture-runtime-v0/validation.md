# Validation

H1-BUNDLE-02 validation was run offline against committed fixtures and local
repo artifacts only. No live source calls, provider calls, browser automation,
downloads, scraping, source sync, or public/master index mutations were used.

## H1 Fixture Runtime

- `python -m json.tool control/schemas/fixtures/h1/connectors/metadata_fixture.v0.json`: PASS
- `python -m json.tool control/schemas/previews/h1/connectors/metadata_normalized_record.v0.json`: PASS
- `python -m json.tool control/schemas/fixtures/h1/connectors/metadata_fixture_replay_result.v0.json`: PASS
- `python -m json.tool control/inventory/connectors/h1_metadata_fixture_runtime_policy.json`: PASS
- `python -m json.tool control/inventory/connectors/h1_metadata_normalization_policy.json`: PASS
- `python -m json.tool control/inventory/connectors/h1_metadata_fixture_output_policy.json`: PASS
- `python -m json.tool control/inventory/connectors/h1_metadata_fixture_path_policy.json`: PASS
- `python -m json.tool control/inventory/connectors/h1_metadata_fixture_truth_policy.json`: PASS
- `python -m json.tool control/inventory/connectors/h1_metadata_source_cache_mapping_policy.json`: PASS
- `python -m json.tool control/inventory/connectors/h1_metadata_evidence_mapping_policy.json`: PASS
- `python -m json.tool control/audits/h1-bundle-02-metadata-fixture-runtime-v0/h1_bundle_02_report.json`: PASS
- `python scripts/validate_h1_metadata_fixture_runtime.py`: PASS
- `python scripts/normalize_h1_metadata_fixture.py --source-id pypi --input examples/connectors/h1_metadata_wave/fixtures/pypi/typical_record.json --check`: PASS
- `python scripts/replay_h1_metadata_fixtures.py --check`: PASS
- `python -m unittest tests.connectors.test_h1_metadata_fixture_runtime`: PASS
- `python -m unittest tests.operations.test_h1_metadata_fixture_scripts`: PASS

## Repo Validation

- `git diff --check`: PASS
- `python -m unittest discover -s tests -t .`: PASS after rerun with a longer timeout; the first 120-second attempt timed out.
- `python scripts/check_architecture_boundaries.py`: PASS

## Existing H0/H1/IA/Core Validators

- `python scripts/validate_h1_metadata_wave_policy_packs.py`: PASS
- `python scripts/validate_source_os_foundation.py`: PASS
- `python scripts/validate_connector_interface_foundation.py`: PASS
- `python scripts/validate_source_os_coverage_scorecards.py`: PASS
- `python scripts/audit_h0_integration.py --check`: PASS
- `python scripts/validate_ia_readiness_polish.py`: PASS
- `python scripts/validate_ia_metadata_connector_foundation.py`: PASS
- `python scripts/validate_ia_metadata_live_probe.py`: PASS
- `python scripts/validate_ia_review_integration.py`: PASS
- `python scripts/validate_local_source_cache_runtime.py`: PASS
- `python scripts/validate_local_evidence_ledger_runtime.py`: PASS
- `python scripts/validate_source_cache_to_evidence_bridge.py`: PASS
- `python scripts/validate_local_review_queue_runtime.py`: PASS
- `python scripts/validate_candidate_promotion_dry_run.py`: PASS
- `python scripts/validate_pack_builder_runtime.py`: PASS
- `python scripts/validate_pack_export_runtime.py`: PASS

## AIDE Lite

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with warnings for optional review-packet refs.
- `py -3 .aide/scripts/aide_lite.py test`: PASS
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS with verifier WARN
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 3 warnings, 0 errors. Warnings are missing optional status refs in `.aide/context/latest-review-packet.md`: `.aide/controller/latest-recommendations.md`, `.aide/gateway/latest-gateway-status.json`, and `.aide/providers/latest-provider-status.json`.
