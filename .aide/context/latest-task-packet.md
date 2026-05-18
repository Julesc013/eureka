# Latest Task Packet

## TASK

IA-06 - IA Review/Promotion Dry-Run.

## PHASE

IA-06 completed as `PASS`.

## GOAL

Load Internet Archive metadata candidate-index records into a local review queue,
record local review decisions, and build promotion previews without mutating the
reviewed index or master index.

## WHY

IA-05 proved IA evidence candidates can become provisional candidate-index
records. IA-06 adds the next gate: candidates can be queued for local review and
can produce promotion previews, while reviewed/master indexes remain unchanged.

## CONTEXT_REFS

- IA-06 queue item
- IA-06 result inventory
- IA-06 audit pack
- IA review and promotion adapters
- .aide/context/latest-context-packet.md
- .aide/context/repo-map.json
- .aide/context/test-map.json
- .aide/context/context-index.json

## ALLOWED_PATHS

- `runtime/review_queue/**`
- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/evidence_ledger/**`
- `runtime/source_cache/**`
- `runtime/source_observation/internet_archive_review.py`
- `runtime/source_observation/internet_archive_promotion.py`
- `runtime/source_observation/internet_archive_candidate_index.py`
- `runtime/source_observation/internet_archive_evidence.py`
- `runtime/source_observation/internet_archive_source_cache.py`
- `scripts/eureka_ia_review_queue.py`
- `scripts/eureka_ia_promotion_dry_run.py`
- `scripts/validate_ia_review_promotion_dry_run.py`
- `tests/runtime/test_ia_review_queue_integration.py`
- `tests/runtime/test_ia_review_decisions.py`
- `tests/runtime/test_ia_promotion_dry_run.py`
- `tests/runtime/test_ia_promotion_boundaries.py`
- `tests/operations/test_ia_review_promotion_scripts.py`
- `examples/review_queue/**`
- `control/policies/ia_review_policy.json`
- `control/policies/ia_promotion_dry_run_policy.json`
- `control/inventory/ia_06_*.json`
- `control/inventory/ia_review_*.json`
- `control/inventory/ia_promotion_*.json`
- `control/audits/ia-06-review-promotion-dry-run-v0/**`
- `docs/operations/IA_REVIEW_PROMOTION_DRY_RUN.md`
- `docs/operations/IA_METADATA_PILOT_RUNBOOK.md`
- `docs/reference/IA_REVIEW_ITEM.md`
- `docs/reference/IA_REVIEW_DECISION.md`
- `docs/reference/IA_PROMOTION_PREVIEW.md`
- `docs/reference/IA_CANDIDATE_RECORD.md`
- `docs/reference/IA_EVIDENCE_RECORD.md`
- `docs/reference/IA_SOURCE_CACHE_RECORD.md`
- `.aide/queue/IA-06/task.yaml`
- `.aide/queue/IA-07/task.yaml`
- `.aide/queue/IA-07/**`
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

IA-06 added:

- `control/policies/ia_review_policy.json`
- `control/policies/ia_promotion_dry_run_policy.json`
- review item, review decision, and promotion preview schema inventories
- `runtime/source_observation/internet_archive_review.py`
- `runtime/source_observation/internet_archive_promotion.py`
- `scripts/eureka_ia_review_queue.py`
- `scripts/eureka_ia_promotion_dry_run.py`
- `scripts/validate_ia_review_promotion_dry_run.py`
- focused runtime and operations tests
- review/promotion examples, docs, inventories, and audit evidence

The temp-instance proof wrote IA review queue records and review decisions to a
temporary explicit instance only. Promotion produced preview-only records and did
not write reviewed or master indexes.

## NON_GOALS

- no new live IA probe
- no downloads or uploads
- no extraction
- no model/provider calls
- no operator instance mutation
- no accepted truth
- no final reviewed record creation
- no reviewed or master index mutation
- no production/public launch claim

## EVIDENCE

- `control/inventory/ia_06_result.json`
- `control/inventory/ia_review_promotion_boundary_report.json`
- `control/audits/ia-06-review-promotion-dry-run-v0/`
- `examples/review_queue/internet_archive_metadata/expected_promotion_preview.json`

## VALIDATION

- `python scripts/validate_ia_metadata_policy.py`
- `python scripts/validate_ia_fixture_replay.py`
- `python scripts/validate_ia_live_metadata_probe.py`
- `python scripts/validate_ia_source_cache_write.py`
- `python scripts/validate_ia_evidence_ledger_integration.py`
- `python scripts/validate_ia_candidate_index_integration.py`
- `python scripts/validate_ia_review_promotion_dry_run.py`
- IA review/promotion focused tests

## ACCEPTANCE

- IA review and promotion policies exist.
- Review and promotion adapters, CLIs, validator, examples, docs, tests,
  inventories, and audit pack exist.
- Dry-run passes without mutation.
- Temp-instance proof writes fixture and live-preview review items.
- Promotion previews are created and preview-only.
- No accepted truth, reviewed-index mutation, master-index mutation, raw
  response commit, downloads, uploads, extraction, model/provider calls, or
  deployment occur.

## OUTPUT_SCHEMA

Final result is recorded in `control/inventory/ia_06_result.json` using
`ia_06_result.v0`.

## TOKEN_ESTIMATE

- packet_chars: under 8000
- approximate_tokens: under 2000

## NEXT

Recommended next task: IA-07 - IA Reviewed Local Index Rebuild.

Alternative: SYN-00 - Synthetic Query Foundry planning over Local/HUNT/PLAY/IA.
