# Module Quality Report

## Largest Source Or Tool Files

- .aide/scripts/aide_lite.py: 1393380 bytes (AIDE Lite)
- surfaces/web/server/workbench_server.py: 95222 bytes (unknown)
- runtime/engine/evals/archive_resolution_runner.py: 92731 bytes (unknown)
- scripts/audit_dev_production_reality.py: 75474 bytes (unknown)
- scripts/validate_publication_inventory.py: 68043 bytes (unknown)
- control/prototypes/legacy_runtime/connectors/h7_library_research/live_probe_common.py: 62606 bytes (unknown)
- scripts/generate_public_data_summaries.py: 58917 bytes (unknown)
- surfaces/web/server/api_routes.py: 58749 bytes (unknown)
- runtime/engine/evals/search_usefulness_runner.py: 57877 bytes (unknown)
- control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/live_probe_common.py: 56845 bytes (unknown)
- scripts/validate_pack_task_review_page_view_models.py: 56528 bytes (unknown)
- runtime/engine/interfaces/normalize/steps.py: 55301 bytes (unknown)
- control/prototypes/legacy_runtime/connectors/h4_code_source_release/live_probe_common.py: 53594 bytes (unknown)
- control/prototypes/legacy_runtime/connectors/h5_vendor_update_driver/live_probe_common.py: 52922 bytes (unknown)
- runtime/gateway/public_api/public_search.py: 52380 bytes (unknown)
- scripts/validate_download_evidence_absence_compare_view_models.py: 52054 bytes (unknown)
- surfaces/web/workbench/render_resolution_workspace.py: 51935 bytes (unknown)
- surfaces/native/cli/main.py: 51914 bytes (unknown)
- control/prototypes/legacy_runtime/connectors/h10_games_emulation/live_probe_common.py: 51604 bytes (unknown)
- scripts/resolve_contract_taxonomy_blockers.py: 51163 bytes (unknown)

## High Dependency Count Candidates

- .aide/scripts/aide_lite.py: large_module_candidate, missing_doc_candidate, mixed_purpose_candidate, orphan_candidate, public_surface_missing_doc_candidate, reuse_candidate
- runtime/engine/evals/archive_resolution_runner.py: mixed_purpose_candidate, orphan_candidate, reuse_candidate, unknown_owner
- runtime/gateway/public_api/__init__.py: missing_doc_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, unknown_owner
- runtime/gateway/public_api/demo_support.py: missing_doc_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, reuse_candidate, unknown_owner

## Mixed Purpose Candidates

- .aide/scripts/aide_lite.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- runtime/engine/evals/archive_resolution_runner.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- runtime/gateway/public_api/__init__.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- runtime/gateway/public_api/demo_support.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.

## Owner Summary

- AIDE Git workflow: 13
- AIDE Lite: 17
- AIDE changelog preview: 4
- AIDE context compiler: 12
- AIDE control plane: 113
- AIDE evals: 69
- AIDE governance: 27
- AIDE harness: 1
- AIDE self-hosting queue: 275
- compatibility baseline: 2
- documentation reference: 555
- unknown: 15201

## Caveats

- module findings are first-pass candidates
- Q38 does not refactor or extract helpers
