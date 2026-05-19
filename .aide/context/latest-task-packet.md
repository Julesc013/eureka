# Latest Task Packet

## TASK

IA-07 - IA Reviewed Local Index Rebuild.

## PHASE

IA-07 completed as `PASS`.

## GOAL

Rebuild a reviewed local index from Internet Archive promotion previews in a
temporary explicit instance, then prove local search, object, and absence reads
can consume the rebuilt reviewed index.

## WHY

IA-06 proved IA provisional candidates can enter a review queue and produce
promotion previews without reviewed/master index writes. IA-07 completes the
local pilot loop by projecting approved promotion previews into reviewed local
records inside a temp instance only.

## CONTEXT_REFS

- IA-07 queue item
- IA-07 result inventory
- IA-07 audit pack
- IA reviewed-index adapter and CLI
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`

## ALLOWED_PATHS

- `runtime/public_index/**`
- `runtime/review_queue/**`
- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/evidence_ledger/**`
- `runtime/source_cache/**`
- `runtime/source_observation/internet_archive_review.py`
- `runtime/source_observation/internet_archive_promotion.py`
- `runtime/source_observation/internet_archive_reviewed_index.py`
- `runtime/source_observation/internet_archive_candidate_index.py`
- `runtime/source_observation/internet_archive_evidence.py`
- `runtime/source_observation/internet_archive_source_cache.py`
- `scripts/eureka_ia_reviewed_index_rebuild.py`
- `scripts/eureka_ia_promotion_dry_run.py`
- `scripts/validate_ia_reviewed_index_rebuild.py`
- IA source-cache/evidence/candidate/review prerequisite scripts
- `tests/runtime/test_ia_reviewed_*.py`
- `tests/operations/test_ia_reviewed_index_scripts.py`
- `examples/reviewed_index/**`
- `examples/reviewed_index/internet_archive_metadata/**`
- `control/policies/ia_reviewed_index_policy.json`
- `control/inventory/ia_07_*.json`
- `control/inventory/ia_reviewed_*.json`
- `control/audits/ia-07-reviewed-local-index-rebuild-v0/**`
- `docs/operations/IA_REVIEWED_INDEX_REBUILD_RUNBOOK.md`
- `docs/operations/IA_METADATA_PILOT_RUNBOOK.md`
- `docs/reference/IA_REVIEWED_LOCAL_RECORD.md`
- `docs/reference/IA_PROMOTION_PREVIEW.md`
- `.aide/queue/IA-07/task.yaml`
- `.aide/queue/IA-PILOT-CLOSEOUT-01/task.yaml`
- `.aide/queue/IA-PILOT-CLOSEOUT-01/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- private local files, credentials, raw prompts, raw responses, and raw live IA
  response bodies
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

IA-07 added:

- `control/policies/ia_reviewed_index_policy.json`
- reviewed local record schema inventory and policy matrix
- `runtime/source_observation/internet_archive_reviewed_index.py`
- `scripts/eureka_ia_reviewed_index_rebuild.py`
- `scripts/validate_ia_reviewed_index_rebuild.py`
- reviewed-index examples, docs, inventories, and audit evidence
- focused runtime and operations tests

Promotion preview detail is now preserved through review and promotion records so
reviewed local records retain source locator, evidence IDs, provenance,
uncertainty, limitations, rights/risk flags, and source metadata summaries.

The temp-instance proof wrote reviewed local records only to a temporary
explicit instance. It then proved search, object packet, and absence packet
behavior over that temp reviewed local index.

## NON_GOALS

- no new live IA probe
- no downloads or uploads
- no extraction
- no model/provider calls
- no operator instance mutation
- no committed `data/public_index` mutation
- no master index mutation
- no public hosted index mutation
- no production/public launch claim

## EVIDENCE

- `control/inventory/ia_07_result.json`
- `control/inventory/ia_reviewed_index_boundary_report.json`
- `control/inventory/ia_reviewed_search_result_matrix.json`
- `control/inventory/ia_reviewed_object_packet_matrix.json`
- `control/inventory/ia_reviewed_absence_packet_matrix.json`
- `control/audits/ia-07-reviewed-local-index-rebuild-v0/`
- `examples/reviewed_index/internet_archive_metadata/expected_reviewed_records.json`

## VALIDATION

- `python scripts/validate_ia_metadata_policy.py`
- `python scripts/validate_ia_fixture_replay.py`
- `python scripts/validate_ia_live_metadata_probe.py`
- `python scripts/validate_ia_source_cache_write.py`
- `python scripts/validate_ia_evidence_ledger_integration.py`
- `python scripts/validate_ia_candidate_index_integration.py`
- `python scripts/validate_ia_review_promotion_dry_run.py`
- `python scripts/validate_ia_reviewed_index_rebuild.py`
- IA reviewed-index focused tests

## ACCEPTANCE

- IA reviewed-index policy, schema, adapter, CLI, validator, examples, docs,
  inventories, and audit pack exist.
- Dry-run passes without mutation.
- Temp-instance proof writes fixture and live-preview reviewed local records.
- Search result, object packet, and absence packet proofs pass.
- Operator instance, committed public index, hosted public index, and master
  index remain untouched.
- No raw response commit, download, upload, extraction, model/provider call,
  deployment, production readiness claim, or public launch readiness claim
  occurs.

## OUTPUT_SCHEMA

Final result is recorded in `control/inventory/ia_07_result.json` using
`ia_07_result.v0`.

## TOKEN_ESTIMATE

- packet_chars: under 8000
- approximate_tokens: under 2000

## NEXT

Recommended next task: IA-PILOT-CLOSEOUT-01 - Internet Archive Metadata Pilot
Closeout.

Alternative: SYN-00 - Synthetic Query Foundry planning over
Local/HUNT/PLAY/IA.
