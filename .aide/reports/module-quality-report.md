# Module Quality Report

## Largest Source Or Tool Files

- .aide/tools/latest-tool-classification.json: 5571541 bytes (AIDE tool absorption framework)
- .aide/tools/latest-tool-inventory.json: 2916899 bytes (AIDE tool absorption framework)
- .aide/tools/latest-tool-wrap-plan.json: 2031131 bytes (AIDE tool absorption framework)
- .aide/scripts/aide_lite.py: 1393380 bytes (AIDE Lite)
- .aide/tools/latest-tool-adapter-map.json: 786522 bytes (AIDE tool absorption framework)
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

## High Dependency Count Candidates

- .aide/scripts/aide_lite.py: large_module_candidate, missing_doc_candidate, mixed_purpose_candidate, orphan_candidate, public_surface_missing_doc_candidate, reuse_candidate
- .aide/tools/latest-tool-adapter-map.json: large_module_candidate, missing_doc_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, public_surface_missing_doc_candidate, reuse_candidate
- .aide/tools/latest-tool-classification.json: large_module_candidate, missing_doc_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, public_surface_missing_doc_candidate, reuse_candidate
- .aide/tools/latest-tool-inventory.json: large_module_candidate, missing_doc_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, public_surface_missing_doc_candidate, reuse_candidate
- .aide/tools/latest-tool-wrap-plan.json: large_module_candidate, missing_doc_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, public_surface_missing_doc_candidate, reuse_candidate
- runtime/engine/evals/archive_resolution_runner.py: mixed_purpose_candidate, orphan_candidate, reuse_candidate, unknown_owner
- runtime/gateway/public_api/__init__.py: missing_doc_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, unknown_owner
- runtime/gateway/public_api/demo_support.py: missing_doc_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, reuse_candidate, unknown_owner

## Mixed Purpose Candidates

- .aide/scripts/aide_lite.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- .aide/tools/latest-tool-adapter-map.json: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- .aide/tools/latest-tool-classification.json: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- .aide/tools/latest-tool-inventory.json: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- .aide/tools/latest-tool-wrap-plan.json: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- runtime/engine/evals/archive_resolution_runner.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- runtime/gateway/public_api/__init__.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- runtime/gateway/public_api/demo_support.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.

## Owner Summary

- AIDE Git workflow: 13
- AIDE GitHub advisory: 8
- AIDE Lite: 32
- AIDE changelog preview: 10
- AIDE context compiler: 12
- AIDE control plane: 254
- AIDE evals: 279
- AIDE governance: 77
- AIDE harness: 1
- AIDE intent compiler: 11
- AIDE refactor control plane: 35
- AIDE repo intelligence: 21
- AIDE root recycling framework: 14
- AIDE self-hosting queue: 294
- AIDE tool absorption framework: 24
- compatibility baseline: 2
- documentation reference: 555
- unknown: 15201

## Caveats

- module findings are first-pass candidates
- Q38 does not refactor or extract helpers
