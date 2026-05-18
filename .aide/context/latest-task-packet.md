# Latest Task Packet

## PHASE

IA-00 — Internet Archive Metadata Connector Approval Closure completed as PASS.

## GOAL

Approve the fail-closed policy boundary for a future Internet Archive
metadata-only local pilot while keeping runtime disabled.

## WHY

IA-00 answers what IA metadata access may be considered later, what remains
forbidden, what must be proven through fixtures, and where source-cache,
evidence, review, and index promotion boundaries live.

## RESULT

IA-00 added:

- IA metadata connector, source access, User-Agent, rate-limit, kill-switch, and non-claim policies
- allowed endpoint and forbidden action matrices
- runtime gate matrix from IA-00 through IA-07
- fixture, live probe, source-cache, and evidence requirements
- IA metadata policy decision and result inventories
- IA metadata docs and reference mappings
- `scripts/validate_ia_metadata_policy.py`
- focused IA policy tests
- IA-00 audit evidence

## CONTEXT_REFS

- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/ia_00_result.json`
- `control/inventory/ia_metadata_policy_decision.json`
- `control/inventory/ia_metadata_allowed_endpoint_matrix.json`
- `control/inventory/ia_metadata_forbidden_action_matrix.json`
- `control/audits/ia-00-metadata-connector-approval-v0/`
- `docs/operations/IA_METADATA_SOURCE_POLICY.md`
- `.aide/queue/IA-00/task.yaml`
- `.aide/queue/IA-01/task.yaml`

## ALLOWED_PATHS

- `control/policies/ia_metadata_connector_policy.json`
- `control/policies/ia_source_access_policy.json`
- `control/policies/ia_user_agent_policy.json`
- `control/policies/ia_rate_limit_policy.json`
- `control/policies/ia_kill_switch_policy.json`
- `control/policies/ia_non_claim_policy.json`
- `control/inventory/ia_00_*.json`
- `control/inventory/ia_metadata_*.json`
- `control/inventory/ia_existing_material_inventory.json`
- `docs/architecture/IA_METADATA_CONNECTOR_MODEL.md`
- `docs/operations/IA_METADATA_SOURCE_POLICY.md`
- `docs/operations/IA_METADATA_NON_CLAIMS.md`
- `docs/operations/IA_METADATA_PILOT_RUNBOOK.md`
- `docs/reference/IA_METADATA_FIELD_MAPPING.md`
- `docs/reference/IA_METADATA_POLICY_MATRIX.md`
- `scripts/validate_ia_metadata_policy.py`
- `tests/operations/test_ia_metadata_policy.py`
- `tests/operations/test_ia_metadata_non_claims.py`
- `tests/operations/test_ia_metadata_policy_validator.py`
- `.aide/queue/IA-00/task.yaml`
- `.aide/queue/IA-01/**`
- `.aide/queue/IA-02/**`
- `.aide/queue/SYN-00/task.yaml`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/ia-00-metadata-connector-approval-v0/**`

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

IA-00 is policy-only. It approves future metadata-only endpoint classes in
principle, keeps live runtime disabled, and records required User-Agent/contact,
rate, timeout, retry, Retry-After, cache, and kill-switch gates. It also records
that IA metadata is source observation material only, not accepted truth.

## VALIDATION

Required IA-00 focused validation is recorded in
`control/inventory/ia_00_result.json` and the audit pack. Full discovery remains
optional for this policy-only task.

## EVIDENCE

- `control/policies/ia_metadata_connector_policy.json`
- `control/policies/ia_source_access_policy.json`
- `control/inventory/ia_metadata_policy_decision.json`
- `control/inventory/ia_metadata_runtime_gate_matrix.json`
- `control/inventory/ia_00_result.json`
- `control/audits/ia-00-metadata-connector-approval-v0/`

## NON_GOALS

No live IA calls, source probes, source-cache writes, evidence writes,
candidate/reviewed/master index mutation, public fanout, extraction,
model/provider calls, downloads, uploads, deployment, production readiness
claim, public launch readiness claim, or committed local instance state.

## ACCEPTANCE

IA-00 acceptance is recorded as pass in `control/inventory/ia_00_result.json`.
The policy closes allowed metadata endpoint classes, forbidden action classes,
future runtime gates, fixture/live/source-cache/evidence requirements, and
non-claim boundaries.

## OUTPUT_SCHEMA

Use compact structured final reports with status, summary, validation, boundary
flags, commits, and next task.

## TOKEN_ESTIMATE

Compact packet under the normal AIDE token budget.

## NEXT

Recommended next task:

IA-01 — IA Fixture Replay Hardening

Alternative:

SYN-00 — Synthetic Query Foundry planning over Local/HUNT/PLAY/IA
