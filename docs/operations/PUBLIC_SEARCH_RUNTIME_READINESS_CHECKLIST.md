# Public Search Runtime Readiness Checklist

Status: local runtime implemented; hosted checklist unsigned.

This checklist records Local Public Search Runtime v0 and gates future hosted
public-search rehearsal. It is not approval to add hosted backend deployment,
live probes, downloads, installers, uploads, accounts, telemetry, rate-limit
middleware, or production API claims. Static handoff is implemented by Public
Search Static Handoff v0 as a no-JS, disabled-hosted-backend entry point.

## Contract Gates

- [x] `python scripts/validate_public_search_contract.py` passes locally.
- [x] `python scripts/validate_public_search_production_contract.py` passes locally.
- [x] `python scripts/validate_public_search_result_card_contract.py` passes locally.
- [x] `python scripts/validate_public_search_safety.py` passes locally.
- [x] `contracts/api/search_request.v0.json` remains `local_index_only` only.
- [x] `contracts/api/search_response.v0.json` still aligns with result cards.
- [x] `contracts/api/error_response.v0.json` contains required safety error
  codes.
- [x] `contracts/api/source_status.v0.json`,
  `contracts/api/evidence_summary.v0.json`,
  `contracts/api/absence_report.v0.json`, and
  `contracts/api/public_search_status.v0.json` exist for the P54 wrapper
  contract.

## Runtime Boundary Gates

- [x] Local index root is server-owned, configured by operator policy, and never
  caller-provided.
- [x] Request parser rejects local path, URL, credential, download, install,
  execute, upload, live-probe, and arbitrary-source parameters.
- [x] No live probes or external source calls are reachable from public search.
- [x] No arbitrary URL fetch is reachable from public search.
- [x] No downloads, installers, execution, mirrors, restore, rollback, or uploads
  are exposed.
- [x] Raw source payloads and private local paths are never returned.
- [x] Query length, include count, and result limit are enforced locally; hosted
  timeout middleware remains future.
- [x] Stable error mapping is implemented for forbidden parameters and disabled
  capabilities.

## Surface Gates

- [x] HTML and JSON behavior are both defined for successful search.
- [x] Lite/text static handoff degradation preserves source, evidence, compatibility,
  limitations, and blocked action posture.
- [x] Result cards expose allowed, blocked, and future-gated actions honestly.
- [x] Absence reports remain bounded and do not imply global non-existence.
- [x] Static `site/dist` continues to be static-only.

## Operator And Privacy Gates

- [ ] `EUREKA_PUBLIC_SEARCH_ENABLED` defaults off until rehearsal approval.
- [ ] `EUREKA_OPERATOR_KILL_SWITCH` or equivalent fails closed.
- [ ] Live probes, downloads, installs, local paths, uploads, and telemetry flags
  default disabled.
- [ ] Logging/privacy posture is accepted before any hosted rehearsal.
- [ ] Raw query logging is disabled by default or sanitized with short retention
  after policy review.
- [ ] Private paths, credentials, source secrets, user files, and raw source
  payloads are never logged.

## Verification Gates

- [x] Public search safety tests exist for disabled modes and forbidden
  parameters.
- [x] Public-alpha smoke tests remain compatible.
- [ ] Architecture-boundary checks pass.
- [ ] Generated static artifact checks pass.
- [x] No documentation claims hosted deployment success.
- [ ] No documentation claims production API stability or production readiness.

## Approval State

- checklist_status: `local_runtime_implemented_hosted_unsigned`
- local_runtime_implemented: true
- implementation_approved: true
- Static handoff is implemented by Public Search Static Handoff v0.
- hosted_public_runtime_approved: false
- static_search_handoff_implemented: true
- hosted_search_handoff_approved: false
- production_claim_allowed: false
