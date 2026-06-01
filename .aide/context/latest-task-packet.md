# AIDE Latest Task Packet

## PHASE

LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00 - apply eligible live metadata review previews through local apply gate

## GOAL

Apply eligible live metadata review previews through a temp-only local apply
gate so they become limited reviewed metadata/source-lead records in proof,
without mutating operator, public, or master indexes.

## WHY

`PUBLIC-ALPHA-REASSESS-02` found the public alpha still deferred because
reviewed records remain too low and reviewed previews do not count as reviewed
records until a local apply gate runs. This task proves eligible previews can be
converted into limited local reviewed metadata/source-lead records while
preserving all artifact, safety, rights, and public launch boundaries.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/public_alpha_reassess_02_result.json`
- `control/inventory/snapshot_refresh_02_result.json`
- `control/inventory/live_metadata_review_result.json`
- `examples/review/live_metadata/`
- `examples/snapshots/refresh/live_metadata_review/`

## CURRENT_STATE

- reviewed metadata record previews: 1
- reviewed source lead previews: 2
- useful leads: 1
- needs more evidence: 2
- rejected or duplicate: 2
- reviewed previews applied before task: false
- public launch recommended: false
- local apply needed: true

## ALLOWED_PATHS

- `.aide/queue/LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-03/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `contracts/local_apply/**`
- `contracts/review/**`
- `runtime/local_apply/**`
- `runtime/review/live_metadata/**`
- `scripts/eureka_local_apply_live_metadata_previews.py`
- `scripts/eureka_local_apply_live_metadata_report.py`
- `scripts/eureka_local_apply_preview_validate.py`
- `scripts/validate_local_apply_live_metadata_previews.py`
- `tests/runtime/test_local_apply_live_metadata_previews.py`
- `tests/runtime/test_live_metadata_apply_plan.py`
- `tests/runtime/test_live_metadata_apply_validation.py`
- `tests/runtime/test_live_metadata_apply_temp_instance.py`
- `tests/runtime/test_live_metadata_reviewed_record_projection.py`
- `tests/runtime/test_live_metadata_apply_boundaries.py`
- `tests/operations/test_local_apply_live_metadata_scripts.py`
- `tests/scripts/test_validate_local_apply_live_metadata_previews.py`
- `examples/local_apply/live_metadata/**`
- `examples/review/live_metadata/**`
- `examples/snapshots/refresh/live_metadata_review/**`
- `examples/public_alpha/reassess/live_metadata_review/**`
- `control/policies/local_apply_live_metadata_previews_policy.json`
- `control/policies/live_metadata_apply_validation_policy.json`
- `control/policies/live_metadata_reviewed_record_policy.json`
- `control/policies/live_metadata_source_lead_policy.json`
- `control/policies/live_metadata_apply_non_claim_policy.json`
- `control/policies/live_metadata_operator_instance_apply_policy.json`
- `control/policies/live_metadata_apply_rollback_policy.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/local_apply_live_metadata*.json`
- `docs/architecture/LOCAL_APPLY_LIVE_METADATA_PREVIEWS.md`
- `docs/architecture/LIVE_METADATA_REVIEWED_RECORD_MODEL.md`
- `docs/architecture/LIVE_METADATA_SOURCE_LEAD_MODEL.md`
- `docs/operations/LOCAL_APPLY_LIVE_METADATA_PREVIEWS_RUNBOOK.md`
- `docs/operations/POST_LOCAL_APPLY_LIVE_METADATA_PLAN.md`
- `docs/reference/LIVE_METADATA_LOCAL_APPLY_PLAN.md`
- `docs/reference/LIVE_METADATA_REVIEWED_RECORD.md`
- `docs/reference/LIVE_METADATA_SOURCE_LEAD.md`
- `control/audits/local-apply-live-metadata-previews-00-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `../instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- raw live source responses
- raw IA responses
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## NON_GOALS

- No deployment or publication.
- No public launch or production readiness claim.
- No new live source calls.
- No download, extraction, execution, install, emulation, or model behavior.
- No operator instance, public, or master index mutation.
- No verified-download, malware-clean, rights-clearance, or artifact-verified claim.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add a temp-only live metadata local-apply runtime under `runtime/local_apply/`.
- Add contracts, policies, CLI, examples, inventory evidence, docs, and audit pack.
- Prove one reviewed metadata record and two reviewed source leads in a temp explicit store.
- Preserve useful lead, needs-more-evidence, and rejected/duplicate states as non-applied.

## VALIDATION

- `git diff --check`
- `python scripts/validate_local_apply_live_metadata_previews.py`
- related public alpha, snapshot, review, live metadata, public search, review batch, candidate index, source action, architecture, and generated-artifact validators
- focused local-apply live metadata unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- eligible preview count: 3
- reviewed metadata records created in temp proof: 1
- reviewed source leads created in temp proof: 2
- reviewed record delta count: 3
- operator instance mutated: false
- committed instance state: false
- public/master index mutated: false
- verified-download, malware-clean, rights-clearance, artifact-verified claims: false
- next recommended task: `SNAPSHOT-REFRESH-03`

## TOKEN_ESTIMATE

medium

## OUTPUT_SCHEMA

Final report uses the user-requested `LOCAL_APPLY_LIVE_METADATA` format with
validation and boundary summaries.

## EVIDENCE

- `control/inventory/local_apply_live_metadata_result.json`
- `examples/local_apply/live_metadata/`
- `control/audits/local-apply-live-metadata-previews-00-v0/`
