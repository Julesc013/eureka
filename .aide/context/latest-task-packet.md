# AIDE Latest Task Packet

## PHASE

SNAPSHOT-REFRESH-02 - refresh snapshots after live metadata candidate review

## GOAL

Package live metadata review outcomes into read-only snapshot, relay, public search view-model, and public alpha reassessment input packets.

## WHY

The public alpha remains reviewed-record poor, but live metadata review produced one reviewed metadata record preview, two reviewed source lead previews, one useful lead, two needs-more-evidence decisions, and two rejected/duplicate decisions. The snapshot layer should make these outcomes visible without applying them as accepted truth.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/live_metadata_review_result.json`
- `control/inventory/public_alpha_reassess_01_result.json`
- `control/inventory/snapshot_refresh_01_result.json`
- `examples/review/live_metadata/`
- `examples/snapshots/refresh/live_metadata_review/`

## CURRENT_STATE

- live metadata candidates reviewed: 8
- reviewed metadata record previews: 1
- reviewed source lead previews: 2
- useful leads: 1
- needs more evidence: 2
- rejected or duplicate: 2
- review preview applied: false
- reviewed/master/public index mutation: false

## ALLOWED_PATHS

- `.aide/queue/SNAPSHOT-REFRESH-02/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-02/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `contracts/snapshot/**`
- `contracts/relay/**`
- `contracts/candidates/**`
- `contracts/review/**`
- `contracts/source/action/**`
- `contracts/view/models/public_search/**`
- `contracts/projections/**`
- `runtime/snapshots/**`
- `runtime/relay/**`
- `runtime/review/live_metadata/**`
- `runtime/public_alpha/**`
- `scripts/eureka_snapshot_refresh.py`
- `scripts/eureka_snapshot_refresh_report.py`
- `scripts/validate_snapshot_refresh.py`
- `tests/runtime/test_snapshot_refresh*.py`
- `tests/operations/test_snapshot_refresh_scripts.py`
- `tests/scripts/test_validate_snapshot_refresh.py`
- `examples/snapshots/refresh/live_metadata_review/**`
- `examples/relay/refresh/**`
- `examples/public_alpha/reassess/live_metadata/**`
- `control/policies/snapshot_refresh*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/snapshot_refresh_02*.json`
- `docs/architecture/SNAPSHOT_REFRESH_02.md`
- `docs/architecture/SNAPSHOT_LIVE_METADATA_REVIEW_HANDOFFS.md`
- `docs/architecture/REVIEWED_METADATA_PREVIEW_SNAPSHOT_SECTION.md`
- `docs/architecture/REVIEWED_SOURCE_LEAD_PREVIEW_SNAPSHOT_SECTION.md`
- `docs/operations/SNAPSHOT_REFRESH_02_RUNBOOK.md`
- `docs/operations/POST_SNAPSHOT_REFRESH_02_PLAN.md`
- `docs/reference/SNAPSHOT_LIVE_METADATA_REVIEW_SECTION.md`
- `docs/reference/SNAPSHOT_REVIEWED_METADATA_PREVIEW_SECTION.md`
- `docs/reference/SNAPSHOT_REVIEWED_SOURCE_LEAD_PREVIEW_SECTION.md`
- `control/audits/snapshot-refresh-02-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `../eureka-test-runs/**`
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

- No new live source calls.
- No deployment or publication.
- No public launch or production readiness claim.
- No download, extraction, execution, install, emulation, or model behavior.
- No reviewed, master, or public index mutation.
- No accepted truth creation.
- No verified download, malware-clean, or rights-clearance claim.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add snapshot contracts and policies for live metadata review sections and reviewed preview sections.
- Add `runtime/snapshots/refresh_02.py`.
- Extend snapshot refresh CLI/report/validator support.
- Generate examples, inventory, and audit evidence for `SNAPSHOT-REFRESH-02`.
- Add focused tests for review and preview sections.

## VALIDATION

- `git diff --check`
- `python scripts/validate_snapshot_refresh.py`
- related source/review/public alpha validators
- focused snapshot refresh unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- Review outcomes are visible in snapshot and relay projections.
- Preview records remain preview-only and local-apply-required.
- No raw responses, live calls, downloads, extraction, model calls, mutation, accepted truth, malware-clean, rights-clearance, or public launch claim.
- Next recommended task is `PUBLIC-ALPHA-REASSESS-02`.

## TOKEN_ESTIMATE

medium

## OUTPUT_SCHEMA

Final report uses the user-requested `SNAPSHOT_REFRESH_02` format with validation and boundary summaries.

## EVIDENCE

- `examples/snapshots/refresh/live_metadata_review/`
- `control/inventory/snapshot_refresh_02_result.json`
- `control/audits/snapshot-refresh-02-v0/`
