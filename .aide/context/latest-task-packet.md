# AIDE Latest Task Packet

## PHASE

EUREKA-LIVE-PRODUCT-HARDENING-AND-ACCEPTANCE-WAVE-03

## GOAL

Harden the complete local live-discovery product before the operator live
canary and human product acceptance, while preserving the `OPERATOR-LIVE-CANARY-00`
gate.

## WHY

The live queue now stops correctly at the operator canary. The deterministic
Search/Hunt, safe fetch, Preview Index, UX, second-provider, Foundry, and audit
foundations are present, but the product still needs observability, recovery,
performance baselines, operator controls, policy registry validation,
portable-release rehearsal, canary closeout, human-acceptance rehearsal,
external full-discovery handoff, and a second-pass hardening audit.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/EUREKA-REAL-LIVE-SEARCH-HUNT-00/task.yaml`
- `.aide/queue/EUREKA-REAL-LIVE-SEARCH-HUNT-ACCEPTANCE-01/task.yaml`
- `.aide/queue/EUREKA-SECOND-PROVIDER-CONFORMANCE-01/task.yaml`
- `.aide/queue/EUREKA-AUTONOMOUS-INDEX-FOUNDRY-01/task.yaml`
- `.aide/queue/EUREKA-AGENTIC-HUNT-PLANNER-01/task.yaml`
- `control/inventory/product/capability_state.json`
- `control/audits/e2e_reference_system/live_discovery_stack_audit_v1/`
- `runtime/search/`
- `runtime/connectors/web/`
- `runtime/index/preview/`
- `runtime/local/`
- `surfaces/web/`
- `scripts/eureka.py`
- `scripts/check_live_search_hunt_acceptance.py`

## ALLOWED_PATHS

- `.aide/**`
- `README.md`
- `docs/**`
- `control/inventory/**`
- `control/audits/**`
- `control/policies/**`
- `contracts/**`
- `runtime/search/**`
- `runtime/connectors/**`
- `runtime/index/**`
- `runtime/resolution_run/**`
- `runtime/local/**`
- `runtime/engine/interfaces/**`
- `surfaces/web/**`
- `scripts/eureka.py`
- `scripts/check_*.py`
- `scripts/validate_*.py`
- `tests/runtime/**`
- `tests/integration/**`
- `tests/e2e/**`
- `tests/scripts/**`
- `tests/operations/**`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- local instance directories
- raw provider responses
- private caches
- public deployment state
- reviewed/master/public truth stores
- provider credentials and API keys

## IMPLEMENTATION

- Do not enable public exposure, public live fanout, reviewed/master/public
  mutation, automatic ReviewDecision creation, executable downloads, background
  Foundry daemons, model calls, or agentic planner runtime.
- Keep Foundry disabled by default and require explicit local operator commands
  for network work.
- Keep provider SearchLeads transient; persist only policy-approved independent
  SourceObservations or provider metadata explicitly allowed by provider policy.
- If a Brave key is absent, finish deterministic implementation and leave live
  acceptance in `WAITING_FOR_OPERATOR_LIVE_CANARY`.
- Do not run full unittest discovery in-session; prepare an external handoff.

## STAGE_CHAIN

1. `EUREKA-LIVE-PRODUCT-STATE-RECONCILIATION-01`
2. `EUREKA-DISCOVERY-OBSERVABILITY-AND-DIAGNOSTICS-01`
3. `EUREKA-INDEX-RECOVERY-MIGRATION-AND-BACKUP-01`
4. `EUREKA-DISCOVERY-PERFORMANCE-CAPACITY-BASELINE-01`
5. `EUREKA-FOUNDRY-OPERATOR-CONTROLS-AND-UX-01`
6. `EUREKA-PROVIDER-POLICY-REGISTRY-01`
7. `EUREKA-PORTABLE-LOCAL-RELEASE-BUNDLE-01`
8. `EUREKA-OPERATOR-LIVE-CANARY-CLOSEOUT-01`
9. `EUREKA-HUMAN-ACCEPTANCE-REHEARSAL-01`
10. `EUREKA-EXTERNAL-FULL-DISCOVERY-HANDOFF-01`
11. `EUREKA-LIVE-PRODUCT-HARDENING-AUDIT-01`

## EVIDENCE

- `control/inventory/product/capability_state.json`
- `.aide/queue/index.yaml`
- `.aide/queue/OPERATOR-LIVE-CANARY-00/task.yaml`
- `external_full_discovery_handoff.json`
- `control/audits/e2e_reference_system/live_product_hardening_audit_v1/AUDIT_REPORT.md`
- `control/audits/e2e_reference_system/live_product_hardening_audit_v1/findings.json`
- focused Wave 03 runtime, e2e, operations, and architecture tests
- final guard command outputs from the current Codex session

## VALIDATION

- Run focused tests after each stage.
- Final local checks:
  - `python scripts/eureka_test_select.py --changed --failed-first --json`
  - `python scripts/check_architecture_boundaries.py`
  - `python scripts/check_generated_artifact_cleanliness.py --check --json`
  - `python scripts/validate_test_lane_policy.py`
  - `python scripts/validate_public_alpha_readonly.py`
  - `python scripts/validate_snapshot_relay.py`
  - `py -3 .aide/scripts/aide_lite.py doctor`
  - `py -3 .aide/scripts/aide_lite.py validate`
  - `py -3 .aide/scripts/aide_lite.py commit check --latest`
  - `git diff --check`

## NON_GOALS

- No real Brave acceptance claim without the real end-to-end canary.
- No human usefulness approval claim without an explicit operator verdict.
- No production scale, public launch, public exposure, main promotion, or
  agentic Hunt Planner work.

## ACCEPTANCE

- The active packet allows product hardening paths and no longer describes the
  older control-only Wave 01.
- Queue, docs, AIDE memory, and `control/inventory/product/capability_state.json`
  agree about implemented deterministic state and remaining external gates.
- Deterministic hardening stages pass focused tests.
- Final queue recommendation remains the operator canary unless a real canary
  has passed.

## OUTPUT_SCHEMA

Final response must include:

- Overall Status
- Commits
- Capability State
- Observability
- Recovery
- Performance
- Foundry UX
- Provider Registry
- Portable Bundle
- Live Canary
- Human Acceptance
- Full Discovery
- Audit
- Queue State
- Next Task

## TOKEN_ESTIMATE

- packet_tokens: under 1600
- expected_final_response_tokens: under 2500
- risk: medium, because external live and human gates must remain distinct
