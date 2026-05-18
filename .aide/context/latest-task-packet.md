# Latest Task Packet

## PHASE

IA-02 — IA Local Live Metadata Probe completed as PARTIAL.

## GOAL

Perform the first tightly bounded Internet Archive live metadata probe under
the IA-00 policy and IA-01 fixture replay rules.

## WHY

IA-02 proves the live-probe guardrails before source-cache, evidence, or index
integration. The live attempt is source observation material only, never truth.

## RESULT

IA-02 added:

- IA live-probe policy, request plan, and redaction policy
- stdlib-only bounded IA live transport and probe runtime
- `scripts/eureka_ia_live_metadata_probe.py`
- `scripts/validate_ia_live_metadata_probe.py`
- focused runtime and operation tests
- IA-02 inventories, docs, and audit evidence

The approved live request was attempted once with `--approve-live`, `rows=1`,
`max-requests=2`, User-Agent, contact, and boundary outputs. It failed before
an IA HTTP response was available because local Python TLS verification reported
`ssl_certificate_verify_failed`.

## CONTEXT_REFS

- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `runtime/source_observation/internet_archive_live_transport.py`
- `runtime/source_observation/internet_archive_live_probe.py`
- `scripts/eureka_ia_live_metadata_probe.py`
- `scripts/validate_ia_live_metadata_probe.py`
- `control/inventory/ia_02_result.json`
- `control/inventory/ia_live_probe_result_summary.json`
- `control/inventory/ia_live_probe_boundary_report.json`
- `control/audits/ia-02-local-live-metadata-probe-v0/`
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

IA-02 is a tiny approved metadata-only live probe. It uses only Python standard
library networking in the IA-02 live transport/runtime/script, enforces caps and
redaction, and commits no raw live response bodies.

## VALIDATION

Required IA-02 focused validation is recorded in
`control/inventory/ia_02_result.json` and the audit pack. Full discovery remains
optional for this focused live-probe task.

## EVIDENCE

- `runtime/source_observation/internet_archive_live_transport.py`
- `runtime/source_observation/internet_archive_live_probe.py`
- `control/inventory/ia_live_probe_result_summary.json`
- `control/inventory/ia_live_probe_boundary_report.json`
- `control/inventory/ia_02_result.json`
- `control/audits/ia-02-local-live-metadata-probe-v0/`

## NON_GOALS

No source-cache writes, evidence writes, candidate/reviewed/master index
mutation, public fanout, extraction, model/provider calls, downloads, uploads,
deployment, production readiness claim, public launch readiness claim, or
committed local instance state. IA-02 is the first task where the approved live
metadata request and source probe flags are true.

## ACCEPTANCE

IA-02 is recorded as partial in `control/inventory/ia_02_result.json` because
the local TLS trust failure prevented a successful IA response. Guardrails,
dry-run, tests, and redacted boundary reporting pass.

## OUTPUT_SCHEMA

Use compact structured final reports with status, summary, validation, boundary
flags, commits, and next task.

## TOKEN_ESTIMATE

Compact packet under the normal AIDE token budget.

## NEXT

Recommended next task:

IA-02 — Rerun approved live metadata probe after resolving local TLS trust

Alternative:

SYN-00 — Synthetic Query Foundry planning over Local/HUNT/PLAY/IA
