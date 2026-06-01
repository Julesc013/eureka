# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-REASSESS-02 - reassess alpha after live metadata candidate review snapshot

## GOAL

Assess whether the read-only public alpha should launch, remain deferred, or
move to local apply after `SNAPSHOT-REFRESH-02` exposed live metadata review
previews.

## WHY

The snapshot now contains useful review outcomes: one reviewed metadata record
preview, two reviewed source lead previews, one useful lead, two needs-more-
evidence decisions, and two rejected or duplicate decisions. These improve
internal review usefulness, but previews are not applied reviewed records.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/snapshot_refresh_02_result.json`
- `control/inventory/live_metadata_review_result.json`
- `examples/snapshots/refresh/live_metadata_review/`
- `examples/public_alpha/reassess/live_metadata_review/`

## CURRENT_STATE

- reviewed records: 1
- fixture candidates: 28
- live metadata candidates: 8
- reviewed metadata record previews: 1
- reviewed source lead previews: 2
- useful leads: 1
- needs more evidence: 2
- rejected or duplicate: 2
- launch recommended: false
- demo mode recommended: true
- internal review recommended: true
- local apply of review previews needed: true

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-ALPHA-REASSESS-02/**`
- `.aide/queue/LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `contracts/publication/**`
- `runtime/public_alpha/**`
- `scripts/eureka_public_alpha_reassess.py`
- `scripts/eureka_public_alpha_reassess_report.py`
- `scripts/eureka_public_alpha_route_smoke.py`
- `scripts/validate_public_alpha_reassess.py`
- `tests/runtime/test_public_alpha_reassess*.py`
- `tests/operations/test_public_alpha_reassess_scripts.py`
- `tests/scripts/test_validate_public_alpha_reassess.py`
- `examples/public_alpha/reassess/live_metadata_review/**`
- `control/policies/public_alpha_reassess*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_alpha_reassess_02*.json`
- `docs/architecture/PUBLIC_ALPHA_REASSESS_02.md`
- `docs/operations/PUBLIC_ALPHA_REASSESS_02_RUNBOOK.md`
- `docs/operations/PUBLIC_ALPHA_USEFULNESS_THRESHOLDS.md`
- `docs/operations/POST_PUBLIC_ALPHA_REASSESS_02_PLAN.md`
- `docs/reference/PUBLIC_ALPHA_REASSESS_DECISION.md`
- `docs/reference/PUBLIC_ALPHA_USEFULNESS_METRICS.md`
- `docs/reference/PUBLIC_ALPHA_REVIEW_PREVIEW_REASSESSMENT.md`
- `control/audits/public-alpha-reassess-02-v0/**`

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

- No deployment or publication.
- No public launch or production readiness claim.
- No local apply execution.
- No reviewed, master, or public index mutation.
- No accepted truth creation.
- No download, extraction, execution, install, emulation, or model behavior.
- No live source calls.
- No verified-download, malware-clean, or rights-clearance claim.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add `runtime/public_alpha/reassess_02.py`.
- Extend public alpha reassess CLI/report/validator support.
- Add review-preview reassess contract and policy.
- Generate examples, inventory, and audit evidence for `PUBLIC-ALPHA-REASSESS-02`.
- Add focused tests for review-preview metrics and boundaries.

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_alpha_reassess.py`
- related snapshot, review, live metadata, public search, seed, and source validators
- focused public-alpha reassess unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- Launch remains recommended false.
- Review previews do not count as reviewed records.
- Local apply is the next recommended task.
- No deployment, public launch, site/dist write, live source call, download,
  extraction, model call, mutation, accepted truth, malware-clean,
  rights-clearance, or public launch readiness claim.

## TOKEN_ESTIMATE

medium

## OUTPUT_SCHEMA

Final report uses the user-requested `PUBLIC_ALPHA_REASSESS_02` format with
validation and boundary summaries.

## EVIDENCE

- `examples/public_alpha/reassess/live_metadata_review/`
- `control/inventory/public_alpha_reassess_02_result.json`
- `control/audits/public-alpha-reassess-02-v0/`
