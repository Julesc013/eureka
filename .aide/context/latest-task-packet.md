# Latest Task Packet

## TASK

IA-05 - IA Candidate Index Integration.

## PHASE

IA-05 completed as `PASS`.

## GOAL

Convert Internet Archive metadata evidence-ledger candidates into provisional
candidate-index records while preserving the review boundary.

## WHY

IA-04 proved IA source-cache records can become review-required evidence
candidates. IA-05 adds the next local-only handoff: evidence candidates become
searchable provisional candidates, but not reviewed records or accepted truth.

## CONTEXT_REFS

- IA-05 queue item
- IA-05 result inventory
- IA-05 audit pack
- IA candidate adapter and validator
- .aide/context/repo-map.json
- .aide/context/test-map.json
- .aide/context/context-index.json
- .aide/context/latest-context-packet.md

## ALLOWED_PATHS

- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/local_foundry/**`
- `runtime/evidence_ledger/**`
- `runtime/source_cache/**`
- `runtime/source_observation/internet_archive_candidate_index.py`
- `runtime/source_observation/internet_archive_evidence.py`
- `runtime/source_observation/internet_archive_source_cache.py`
- `runtime/source_observation/internet_archive_metadata.py`
- `runtime/source_observation/internet_archive_normalization.py`
- `runtime/source_observation/internet_archive_validation.py`
- `scripts/eureka_ia_candidate_index_write.py`
- `scripts/eureka_ia_evidence_ledger_write.py`
- `scripts/eureka_ia_source_cache_write.py`
- `scripts/eureka_ia_fixture_replay.py`
- `scripts/eureka_ia_live_metadata_probe.py`
- `scripts/validate_ia_candidate_index_integration.py`
- `scripts/validate_ia_evidence_ledger_integration.py`
- `scripts/validate_ia_source_cache_write.py`
- `scripts/validate_ia_fixture_replay.py`
- `scripts/validate_ia_live_metadata_probe.py`
- `scripts/validate_ia_metadata_policy.py`
- `tests/runtime/test_ia_candidate_index_integration.py`
- `tests/runtime/test_ia_candidate_records.py`
- `tests/runtime/test_ia_candidate_boundaries.py`
- `tests/operations/test_ia_candidate_index_scripts.py`
- `examples/candidate_index/internet_archive_metadata/**`
- `examples/evidence_ledger/internet_archive_metadata/**`
- `examples/source_cache/internet_archive_metadata/**`
- `examples/internet_archive_metadata/**`
- `control/policies/ia_candidate_index_policy.json`
- `control/policies/ia_evidence_ledger_policy.json`
- `control/policies/ia_source_cache_policy.json`
- `control/policies/ia_metadata_connector_policy.json`
- `control/policies/ia_source_access_policy.json`
- `control/policies/ia_non_claim_policy.json`
- `control/inventory/ia_05_input_state.json`
- `control/inventory/ia_candidate_policy_matrix.json`
- `control/inventory/ia_candidate_record_schema.json`
- `control/inventory/ia_candidate_write_plan.json`
- `control/inventory/ia_candidate_fixture_write_result.json`
- `control/inventory/ia_candidate_live_preview_write_result.json`
- `control/inventory/ia_candidate_boundary_report.json`
- `control/inventory/ia_05_result.json`
- `control/inventory/ia_05_next_task_decision.json`
- `control/audits/ia-05-candidate-index-integration-v0/**`
- `docs/operations/IA_CANDIDATE_INDEX_RUNBOOK.md`
- `docs/operations/IA_METADATA_PILOT_RUNBOOK.md`
- `docs/reference/IA_CANDIDATE_RECORD.md`
- `docs/reference/IA_EVIDENCE_RECORD.md`
- `docs/reference/IA_SOURCE_CACHE_RECORD.md`
- `docs/reference/IA_METADATA_FIELD_MAPPING.md`
- `.aide/queue/IA-05/task.yaml`
- `.aide/queue/IA-06/**`
- `.aide/queue/IA-06/task.yaml`
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

IA-05 adds:

- `control/policies/ia_candidate_index_policy.json`
- IA candidate record schema and write-plan inventories
- `runtime/candidate_index/store.py`
- `runtime/source_observation/internet_archive_candidate_index.py`
- `scripts/eureka_ia_candidate_index_write.py`
- `scripts/validate_ia_candidate_index_integration.py`
- focused runtime and operations tests
- candidate examples, docs, inventories, and audit evidence

The IA adapter consumes IA evidence candidates from fixture replay and the
redacted IA-02 live-preview path. It builds provisional IA item, media metadata,
file-list, collection-member, source-locator, near-miss, and missing-item
candidates where the evidence supports them.

Candidate records remain review-required. They do not create accepted truth,
reviewed records, reviewed-index mutations, master-index mutations, raw response
commits, downloads, uploads, extraction, model/provider calls, or deployment.

## NON_GOALS

- no new live IA probe
- no downloads or uploads
- no extraction
- no model/provider calls
- no operator instance mutation
- no reviewed record creation
- no reviewed or master index mutation
- no production/public launch claim

## EVIDENCE

- `control/inventory/ia_05_result.json`
- `control/inventory/ia_candidate_boundary_report.json`
- `control/audits/ia-05-candidate-index-integration-v0/`
- `examples/candidate_index/internet_archive_metadata/expected_candidates.json`

## VALIDATION

- `python scripts/validate_ia_metadata_policy.py`
- `python scripts/validate_ia_fixture_replay.py`
- `python scripts/validate_ia_live_metadata_probe.py`
- `python scripts/validate_ia_source_cache_write.py`
- `python scripts/validate_ia_evidence_ledger_integration.py`
- `python scripts/validate_ia_candidate_index_integration.py`
- IA candidate focused tests

## ACCEPTANCE

- IA candidate policy exists.
- IA candidate record schema inventory exists.
- Candidate adapter, CLI, validator, examples, docs, tests, inventories, and audit pack exist.
- Dry-run passes without mutation.
- Temp-instance apply proof writes fixture and live-preview candidates.
- All candidates require review.
- No accepted truth, reviewed-index mutation, master-index mutation, raw response commit, downloads, uploads, extraction, model/provider calls, or deployment occur.

## OUTPUT_SCHEMA

Final result is recorded in `control/inventory/ia_05_result.json` using
`ia_05_result.v0`.

## TOKEN_ESTIMATE

- packet_chars: under 5000
- approximate_tokens: under 1250

## NEXT

Recommended next task: IA-06 - IA Review/Promotion Dry-Run.

Alternative: SYN-00 - Synthetic Query Foundry planning over Local/HUNT/PLAY/IA.
