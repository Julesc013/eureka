# SOURCE-WAVE-00 Task Packet

## PHASE

SOURCE-WAVE-00 - Metadata-only source family wave using SourceActionKernel.

## GOAL

Register the first metadata-only source family wave through the existing SourceActionKernel. The wave proves that Internet Archive metadata v2, Wayback/CDX metadata, GitHub Releases metadata, Software Heritage metadata, package registry metadata, Open Library metadata, Wikidata metadata, and manual source packs can all run deterministic fixture actions and emit mapping plans, lane projections, review handoff plans, scorecards, and boundary reports.

## WHY

Future source families must use one governed source-action seam rather than one-off scripts. This keeps source outputs as policy-gated candidate inputs, not accepted truth or store mutation.

## CONTEXT_REFS

- `control/inventory/source_action_kernel_result.json`
- `runtime/source/action/source_wave.py`
- `tools/validators/validate_source_wave.py`
- `control/inventory/source_wave_result.json`
- `control/audits/source-wave-00-v0/`

## ALLOWED_PATHS

- `contracts/source/action/**`
- `contracts/source/families/**`
- `contracts/source/policy/**`
- `contracts/source/coverage/**`
- `contracts/source/scorecard/**`
- `contracts/sources/**`
- `contracts/source_cache/**`
- `contracts/evidence/**`
- `contracts/candidates/**`
- `contracts/review/**`
- `contracts/resolution_run/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `contracts/projections/**`
- `runtime/source/action/**`
- `runtime/source/observation/**`
- `runtime/source/cache/**`
- `runtime/source/registry/**`
- `runtime/review/queue/**`
- `runtime/resolution_run/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/local_eval/**`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`
- `runtime/connectors/internet_archive_metadata/**`
- `runtime/connectors/wayback_cdx/**`
- `runtime/connectors/github_releases/**`
- `runtime/connectors/software_heritage/**`
- `runtime/connectors/package_registries/**`
- `runtime/connectors/open_library/**`
- `runtime/connectors/wikidata/**`
- `runtime/connectors/manual_source_pack/**`
- `runtime/connectors/fixture_source_action/**`
- `surfaces/web/workbench/**`
- `surfaces/api/**`
- `surfaces/web/**`
- `tools/validators/validate_source_wave.py`
- `tools/generators/source_wave_fixture_builder.py`
- `tools/auditors/source_wave_boundary_auditor.py`
- `scripts/validate_source_wave.py`
- `scripts/validate_source_action_kernel.py`
- `scripts/eureka_source_wave.py`
- `scripts/eureka_source_action.py`
- `scripts/eureka_source_action_manifest.py`
- `scripts/eureka_source_action_scorecard.py`
- `scripts/eureka_source_wave_smoke.py`
- `scripts/eureka_test_select.py`
- `tests/runtime/test_source_wave*.py`
- `tests/operations/test_source_wave*.py`
- `tests/scripts/test_validate_source_wave.py`
- `examples/source_actions/**`
- `examples/sources/internet_archive_metadata/**`
- `examples/sources/wayback_cdx/**`
- `examples/sources/github_releases/**`
- `examples/sources/software_heritage/**`
- `examples/sources/package_registries/**`
- `examples/sources/open_library/**`
- `examples/sources/wikidata/**`
- `examples/sources/manual_source_pack/**`
- `examples/connectors/internet_archive_metadata/**`
- `examples/connectors/wayback_cdx/**`
- `examples/connectors/github_releases/**`
- `examples/connectors/software_heritage/**`
- `examples/connectors/package_registries/**`
- `examples/connectors/open_library/**`
- `examples/connectors/wikidata/**`
- `examples/connectors/manual_source_pack/**`
- `evals/source_wave/**`
- `evals/sources/**`
- `control/policies/source_wave*.json`
- `control/inventory/source_wave*.json`
- `docs/architecture/SOURCE_WAVE*.md`
- `docs/architecture/SOURCE_FAMILY_ADAPTERS.md`
- `docs/operations/*SOURCE_WAVE*.md`
- `docs/reference/SOURCE_FAMILY_MANIFEST.md`
- `docs/reference/SOURCE_WAVE*.md`
- `.aide/queue/AIDE-BATCH-SOURCE-WAVE-00/**`
- `.aide/queue/SOURCE-WAVE-00/task.yaml`
- `.aide/queue/SNAPSHOT-RELAY-00/task.yaml`
- `.aide/queue/PUBLIC-ALPHA-READONLY-00/task.yaml`
- `.aide/queue/PUBLIC-DEMAND-SIGNAL-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/source-wave-00-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- `private local files`
- `committed operator tokens`
- `committed provider credentials`
- `raw prompts`
- `raw responses`
- `raw live source response bodies`
- `raw live IA response bodies`
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Add source-wave policies, family descriptors, capability/fixture/transport/normalizer/mapping/lane/review/scorecard matrices, examples, docs, audit evidence, and queue/report updates.
- Add fixture/mock adapter registrations for eight required metadata source families.
- Add `runtime/source/action/source_wave.py` as the SourceActionKernel-based family registry and fixture runner.
- Add `scripts/eureka_source_wave.py`, `scripts/eureka_source_wave_smoke.py`, and `scripts/validate_source_wave.py`.
- Add focused source-wave tests.

## VALIDATION

- `python scripts/validate_source_wave.py`
- `python scripts/validate_source_action_kernel.py`
- Source-wave focused unittest modules.
- Existing subsystem validators.
- `git diff --check`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check when practical.

## EVIDENCE

- `control/inventory/source_wave_result.json`
- `control/inventory/source_wave_validation_matrix.json`
- `control/inventory/source_wave_smoke_result.json`
- `control/inventory/source_wave_boundary_report.json`
- `control/audits/source-wave-00-v0/`

## NON_GOALS

- No broad source expansion beyond metadata fixture/mock foundations.
- No live source calls, source probes, public source fanout, crawling, scraping, downloads, uploads, extraction, execution, emulation, model/provider calls, deployment, operator-instance mutation, committed instance state, master/public index mutation, fake evidence, fake verified records, production readiness claim, public launch claim, or marketplace/app-store readiness claim.

## ACCEPTANCE

- Eight required families are registered and runnable in fixture mode.
- Each required family emits mapping plans, lane projection plans, review handoff plans, scorecards, and boundary reports.
- All unsafe boundary flags remain false.
- Source-wave validator and focused tests pass.
- Recommended next task is `SNAPSHOT-RELAY-00`.

## OUTPUT_SCHEMA

`source_wave_result.v0`.

## TOKEN_ESTIMATE

Medium batch packet; use repo files and audit evidence for detail instead of embedding full prompt history.
