# Latest Task Packet

## PHASE

IA-01 — IA Fixture Replay Hardening completed as PASS.

## GOAL

Add deterministic Internet Archive metadata fixture replay coverage for the
metadata-only local pilot approved in IA-00.

## WHY

IA-01 proves local parser, normalizer, and boundary behavior before any future
operator-approved live metadata probe.

## RESULT

IA-01 added:

- eight committed IA metadata fixtures
- normalized source-observation candidate records
- boundary reports proving no live/write/download side effects
- local fixture replay runtime under `runtime/source_observation/`
- `scripts/eureka_ia_fixture_replay.py`
- `scripts/validate_ia_fixture_replay.py`
- focused runtime and operation tests
- IA-01 inventories, docs, queue handoff, and audit evidence

## CONTEXT_REFS

- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `examples/internet_archive_metadata/`
- `runtime/source_observation/internet_archive_fixture_replay.py`
- `runtime/source_observation/internet_archive_normalization.py`
- `scripts/eureka_ia_fixture_replay.py`
- `scripts/validate_ia_fixture_replay.py`
- `control/inventory/ia_01_result.json`
- `control/audits/ia-01-fixture-replay-hardening-v0/`
- `.aide/queue/IA-01/task.yaml`
- `.aide/queue/IA-02/task.yaml`

## ALLOWED_PATHS

- `examples/internet_archive_metadata/**`
- `runtime/source_observation/internet_archive_metadata.py`
- `runtime/source_observation/internet_archive_fixture_replay.py`
- `runtime/source_observation/internet_archive_normalization.py`
- `runtime/source_observation/internet_archive_validation.py`
- `scripts/eureka_ia_fixture_replay.py`
- `scripts/validate_ia_fixture_replay.py`
- `scripts/validate_ia_metadata_policy.py`
- `tests/runtime/test_ia_metadata_fixture_replay.py`
- `tests/runtime/test_ia_metadata_normalization.py`
- `tests/runtime/test_ia_metadata_boundary.py`
- `tests/operations/test_ia_fixture_replay_scripts.py`
- `control/inventory/ia_01_*.json`
- `control/inventory/ia_fixture_*.json`
- `control/policies/ia_metadata_connector_policy.json`
- `control/policies/ia_source_access_policy.json`
- `control/policies/ia_user_agent_policy.json`
- `control/policies/ia_rate_limit_policy.json`
- `control/policies/ia_kill_switch_policy.json`
- `control/policies/ia_non_claim_policy.json`
- `docs/architecture/IA_METADATA_CONNECTOR_MODEL.md`
- `docs/operations/IA_METADATA_SOURCE_POLICY.md`
- `docs/operations/IA_METADATA_NON_CLAIMS.md`
- `docs/operations/IA_METADATA_PILOT_RUNBOOK.md`
- `docs/reference/IA_METADATA_FIELD_MAPPING.md`
- `docs/reference/IA_METADATA_FIXTURE_REPLAY.md`
- `docs/reference/IA_METADATA_POLICY_MATRIX.md`
- `.aide/queue/IA-01/task.yaml`
- `.aide/queue/IA-01/**`
- `.aide/queue/IA-02/**`
- `.aide/queue/SYN-00/task.yaml`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/ia-01-fixture-replay-hardening-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- private local files
- committed operator tokens
- committed provider credentials
- raw prompts
- raw responses
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

IA-01 is local fixture replay only. It reads committed fixture files, normalizes
them into source-observation candidate records, and emits boundary reports. It
does not add network-capable connector runtime.

## VALIDATION

Required IA-01 focused validation is recorded in
`control/inventory/ia_01_result.json` and the audit pack. Full discovery remains
optional for this focused fixture-replay task.

## EVIDENCE

- `examples/internet_archive_metadata/`
- `runtime/source_observation/internet_archive_fixture_replay.py`
- `control/inventory/ia_fixture_inventory.json`
- `control/inventory/ia_01_result.json`
- `control/audits/ia-01-fixture-replay-hardening-v0/`

## NON_GOALS

No live IA calls, source probes, source-cache writes, evidence writes,
candidate/reviewed/master index mutation, public fanout, extraction,
model/provider calls, downloads, uploads, deployment, production readiness
claim, public launch readiness claim, or committed local instance state.

## ACCEPTANCE

IA-01 acceptance is recorded as pass in `control/inventory/ia_01_result.json`.
All eight required fixtures replay deterministically, expected records match,
and no-download proof passes.

## OUTPUT_SCHEMA

Use compact structured final reports with status, summary, validation, boundary
flags, commits, and next task.

## TOKEN_ESTIMATE

Compact packet under the normal AIDE token budget.

## NEXT

Recommended next task:

IA-02 — IA Local Live Metadata Probe

Alternative:

SYN-00 — Synthetic Query Foundry planning over Local/HUNT/PLAY/IA
