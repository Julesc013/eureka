# AIDE Latest Task Packet

## PHASE

SNAPSHOT-REFRESH-03 - refresh snapshots after local apply of live metadata previews

## GOAL

Package the temp local-apply proof into the read-only snapshot and relay layer.
The refresh projects one limited reviewed metadata record and two limited
reviewed source leads while preserving all non-claims.

## WHY

`LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00` proved three eligible live metadata
review previews in a temp explicit instance. This task makes that evidence
visible to snapshots, relay projections, public search view models, and the next
public alpha reassessment without mutating operator, public, master, or reviewed
indexes.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `control/inventory/local_apply_live_metadata_result.json`
- `control/inventory/snapshot_refresh_03_result.json`
- `examples/local_apply/live_metadata/`
- `examples/snapshots/refresh/local_apply_live_metadata/`
- `control/audits/snapshot-refresh-03-v0/`

## CURRENT_STATE

- existing reviewed records: 1
- reviewed metadata records from local apply: 1
- reviewed source leads from local apply: 2
- reviewed record delta count: 3
- total limited reviewed record projection count: 4
- useful leads not applied: 1
- needs more evidence not applied: 2
- rejected or duplicate not applied: 2

## ALLOWED_PATHS

- `.aide/queue/SNAPSHOT-REFRESH-03/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-03/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `contracts/snapshot/**`
- `contracts/relay/**`
- `contracts/candidates/**`
- `contracts/review/**`
- `contracts/local_apply/**`
- `runtime/snapshots/**`
- `runtime/relay/**`
- `runtime/local_apply/**`
- `runtime/review/live_metadata/**`
- `runtime/public_alpha/**`
- `scripts/eureka_snapshot_refresh.py`
- `scripts/eureka_snapshot_refresh_report.py`
- `scripts/validate_snapshot_refresh.py`
- `tests/runtime/test_snapshot_refresh*.py`
- `tests/operations/test_snapshot_refresh_scripts.py`
- `tests/scripts/test_validate_snapshot_refresh.py`
- `examples/snapshots/refresh/local_apply_live_metadata/**`
- `examples/relay/refresh/local_apply_live_metadata_refreshed_relay_projection.json`
- `examples/public_alpha/reassess/local_apply_live_metadata/**`
- `control/policies/snapshot_refresh*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/snapshot_refresh_03*.json`
- `docs/architecture/SNAPSHOT_REFRESH_03.md`
- `docs/architecture/SNAPSHOT_LOCAL_APPLY_LIVE_METADATA_HANDOFFS.md`
- `docs/architecture/REVIEWED_METADATA_RECORD_SNAPSHOT_SECTION.md`
- `docs/architecture/REVIEWED_SOURCE_LEAD_SNAPSHOT_SECTION.md`
- `docs/operations/SNAPSHOT_REFRESH_03_RUNBOOK.md`
- `docs/operations/POST_SNAPSHOT_REFRESH_03_PLAN.md`
- `docs/reference/SNAPSHOT_REVIEWED_METADATA_RECORD_SECTION.md`
- `docs/reference/SNAPSHOT_REVIEWED_SOURCE_LEAD_SECTION.md`
- `docs/reference/SNAPSHOT_LOCAL_APPLY_SECTION.md`
- `control/audits/snapshot-refresh-03-v0/**`

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
- No operator instance, public, master, or reviewed index mutation.
- No verified-download, malware-clean, rights-clearance, or artifact-verified claim.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add `runtime/snapshots/refresh_03.py`.
- Add snapshot contracts and policies for local-apply sections.
- Add CLI/report flags for local-apply live metadata refresh examples.
- Add docs, examples, inventory matrices, audit evidence, and focused tests.

## VALIDATION

- `git diff --check`
- `python scripts/validate_snapshot_refresh.py`
- related local apply, review, live metadata, public alpha, public search, seed batch, review batch, scout, candidate index, query planner, snapshot relay, public alpha readonly, source action, architecture, and generated-artifact validators
- focused snapshot refresh unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- existing reviewed records: 1
- reviewed metadata records from local apply: 1
- reviewed source leads from local apply: 2
- reviewed record delta count: 3
- total limited reviewed record projection count: 4
- operator instance mutated: false
- reviewed/master/public index mutated: false
- verified-download, malware-clean, rights-clearance, artifact-verified claims: false
- next recommended task: `PUBLIC-ALPHA-REASSESS-03`

## EVIDENCE

- `control/inventory/snapshot_refresh_03_result.json`
- `examples/snapshots/refresh/local_apply_live_metadata/`
- `control/audits/snapshot-refresh-03-v0/`

## TOKEN_ESTIMATE

medium

## OUTPUT_SCHEMA

Final report uses the user-requested `SNAPSHOT_REFRESH_03` format with validation
and boundary summaries.
