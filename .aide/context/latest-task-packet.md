# SNAPSHOT-RELAY-00 Task Packet

## PHASE

SNAPSHOT-RELAY-00 - Reviewed-record snapshot and read-only relay foundation.

## GOAL

Build a read-only snapshot/relay foundation that projects reviewed records into deterministic public-safe snapshot packets, integrity manifests, capability profiles, relay manifests, and read-only API/text/files/lite projections.

## WHY

The local product loop can now create reviewed local records through gated review and apply. Snapshot/relay is the bridge from local reviewed results to public-safe distribution: immutable reviewed-record packets, integrity metadata, and read-only relay projections. It must stay separate from deployment, public launch, live source fanout, source probes, downloads, extraction, and index mutation.

## CONTEXT_REFS

- `control/inventory/source_wave_result.json`
- `runtime/snapshots/relay_foundation.py`
- `runtime/relay/snapshot_relay.py`
- `runtime/capabilities/profiles.py`
- `tools/validators/validate_snapshot_relay.py`
- `control/inventory/snapshot_relay_result.json`
- `control/audits/snapshot-relay-00-v0/`

## ALLOWED_PATHS

- `contracts/snapshot/**`
- `contracts/relay/**`
- `contracts/capabilities/**`
- `contracts/publication/**`
- `contracts/search_interaction/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `contracts/projections/**`
- `contracts/review/**`
- `contracts/evidence/**`
- `contracts/candidates/**`
- `contracts/source/action/**`
- `contracts/source/families/**`
- `runtime/snapshots/**`
- `runtime/relay/**`
- `runtime/capabilities/**`
- `runtime/local_eval/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/resolution_run/**`
- `runtime/public_index/**`
- `runtime/review/queue/**`
- `runtime/source/action/**`
- `runtime/source/observation/**`
- `runtime/source/cache/**`
- `surfaces/files/**`
- `surfaces/text/**`
- `surfaces/lite/**`
- `surfaces/api/**`
- `surfaces/web/**`
- `surfaces/web/workbench/**`
- `snapshots/schema/**`
- `snapshots/examples/**`
- `snapshots/fixtures/**`
- `snapshots/README.md`
- `examples/snapshots/**`
- `examples/relay/**`
- `examples/capabilities/**`
- `examples/publication/**`
- `examples/workbench/live_run/**`
- `examples/local_loop/**`
- `examples/source_actions/**`
- `examples/sources/**`
- `evals/snapshots/**`
- `evals/relay/**`
- `tools/validators/validate_snapshot_relay.py`
- `tools/generators/snapshot_fixture_builder.py`
- `tools/auditors/snapshot_relay_boundary_auditor.py`
- `scripts/validate_snapshot_relay.py`
- `scripts/eureka_snapshot_build.py`
- `scripts/eureka_snapshot_validate.py`
- `scripts/eureka_relay_project.py`
- `scripts/eureka_relay_validate.py`
- `scripts/eureka_capability_profile.py`
- `scripts/eureka_test_select.py`
- `tests/runtime/test_snapshot*.py`
- `tests/runtime/test_relay*.py`
- `tests/runtime/test_capability_profile.py`
- `tests/operations/test_snapshot_relay*.py`
- `tests/scripts/test_validate_snapshot_relay.py`
- `control/policies/snapshot*.json`
- `control/policies/relay*.json`
- `control/policies/capability_profile_policy.json`
- `control/inventory/snapshot*.json`
- `control/inventory/relay*.json`
- `docs/architecture/SNAPSHOT_RELAY.md`
- `docs/architecture/REVIEWED_RECORD_SNAPSHOT_MODEL.md`
- `docs/architecture/READ_ONLY_RELAY_MODEL.md`
- `docs/architecture/CAPABILITY_PROFILE_MODEL.md`
- `docs/operations/SNAPSHOT_RELAY_RUNBOOK.md`
- `docs/operations/POST_SNAPSHOT_RELAY_PLAN.md`
- `docs/reference/SNAPSHOT_ENVELOPE.md`
- `docs/reference/SNAPSHOT_MANIFEST.md`
- `docs/reference/SNAPSHOT_RECORD.md`
- `docs/reference/RELAY_MANIFEST.md`
- `docs/reference/CAPABILITY_PROFILE.md`
- `.aide/queue/AIDE-BATCH-SNAPSHOT-RELAY-00/**`
- `.aide/queue/SNAPSHOT-RELAY-00/task.yaml`
- `.aide/queue/PUBLIC-ALPHA-READONLY-00/task.yaml`
- `.aide/queue/PUBLIC-DEMAND-SIGNAL-00/task.yaml`
- `.aide/queue/PUBLIC-SOURCE-REQUEST-QUEUE-00/**`
- `.aide/queue/NATIVE-SNAPSHOT-CLIENT-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/snapshot-relay-00-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- `private local files`
- `committed operator tokens`
- `committed provider credentials`
- `private signing keys`
- `raw prompts`
- `raw responses`
- `raw live source response bodies`
- `raw live IA response bodies`
- `site/dist/**`
- generated public index artifacts under site or data roots
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `runtime/connectors/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Add snapshot policies, contracts, manifest/integrity/capability/relay matrices, examples, docs, audit evidence, and queue/report updates.
- Add deterministic fixture reviewed records and runtime snapshot builder helpers under `runtime/snapshots/`.
- Add read-only relay projection helpers under `runtime/relay/`.
- Add capability profile negotiation helpers under `runtime/capabilities/`.
- Add minimal files/text/lite/API projection helpers.
- Add `scripts/eureka_snapshot_build.py`, `scripts/eureka_snapshot_validate.py`, `scripts/eureka_relay_project.py`, `scripts/eureka_relay_validate.py`, `scripts/eureka_capability_profile.py`, and `scripts/validate_snapshot_relay.py`.
- Add focused runtime, operation, and validator tests.

## VALIDATION

- `python scripts/validate_snapshot_relay.py`
- `python scripts/validate_source_wave.py`
- `python scripts/validate_source_action_kernel.py`
- Existing local loop, local apply, review/promote, IA lane, workbench, resolution, G0, F0, SCOUT, DOMAIN, SYN, IA-HUNT, result-lane, search-interaction, workbench-foundation, test-lane, contract-taxonomy, and repo-structure validators.
- Focused snapshot relay unittest modules.
- `git diff --check`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check when practical.

## EVIDENCE

- `control/inventory/snapshot_relay_result.json`
- `control/inventory/snapshot_relay_validation_matrix.json`
- `control/inventory/snapshot_relay_smoke_result.json`
- `control/inventory/snapshot_relay_boundary_report.json`
- `control/audits/snapshot-relay-00-v0/`

## NON_GOALS

- No public production deployment, hosted public launch, live source calls, source probes, public live source fanout, crawling, downloads, uploads, extraction, execution, install, emulation, model/provider calls, operator-instance mutation, committed operator instance state, raw live response commits, source-cache/evidence/candidate/review/reviewed-index mutation, master/public index mutation, committed public-index artifacts, fake evidence, fake verified records, production readiness claim, public launch readiness claim, marketplace/app-store readiness claim, private signing key generation, broad public site deployment, or native app implementation.

## ACCEPTANCE

- Snapshot build, integrity, validation, relay manifest, relay query, and capability profiles pass.
- Public, native, and lite projections remain read-only.
- No private local state, tokens, raw live responses, live source calls, source probes, operator-instance mutation, master/public index mutation, downloads, uploads, extraction, model calls, deployment, production readiness claim, or public launch claim.
- Recommended next task is `PUBLIC-ALPHA-READONLY-00`.

## OUTPUT_SCHEMA

`snapshot_relay_result.v0`.

## TOKEN_ESTIMATE

Medium batch packet; use repo files and audit evidence for detail instead of embedding full prompt history.
