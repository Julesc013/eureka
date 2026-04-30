# Public Search Runtime Readiness Checklist

Status: future checklist, unsigned.

This checklist gates Local Public Search Runtime v0. It is not approval to add a
hosted backend, public deployment, live probes, downloads, installers, uploads,
accounts, telemetry, rate-limit middleware, or production API claims.

## Contract Gates

- [ ] `python scripts/validate_public_search_contract.py` passes.
- [ ] `python scripts/validate_public_search_result_card_contract.py` passes.
- [ ] `python scripts/validate_public_search_safety.py` passes.
- [ ] `contracts/api/search_request.v0.json` remains `local_index_only` only.
- [ ] `contracts/api/search_response.v0.json` still aligns with result cards.
- [ ] `contracts/api/error_response.v0.json` contains required safety error
  codes.

## Runtime Boundary Gates

- [ ] Local index root is server-owned, configured by operator policy, and never
  caller-provided.
- [ ] Request parser rejects local path, URL, credential, download, install,
  execute, upload, live-probe, and arbitrary-source parameters.
- [ ] No live probes or external source calls are reachable from public search.
- [ ] No arbitrary URL fetch is reachable from public search.
- [ ] No downloads, installers, execution, mirrors, restore, rollback, or uploads
  are exposed.
- [ ] Raw source payloads and private local paths are never returned.
- [ ] Query length, include count, result limit, and timeout limits are enforced.
- [ ] Stable error mapping is implemented for forbidden parameters and disabled
  capabilities.

## Surface Gates

- [ ] HTML and JSON behavior are both defined for successful search.
- [ ] Lite/text degradation preserves source, evidence, compatibility,
  limitations, and blocked action posture.
- [ ] Result cards expose allowed, blocked, and future-gated actions honestly.
- [ ] Absence reports remain bounded and do not imply global non-existence.
- [ ] Static `site/dist` continues to be static-only.

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

- [ ] Public search safety tests exist for disabled modes and forbidden
  parameters.
- [ ] Public-alpha smoke tests remain compatible.
- [ ] Architecture-boundary checks pass.
- [ ] Generated static artifact checks pass.
- [ ] No documentation claims public search is live.
- [ ] No documentation claims production API stability or production readiness.

## Approval State

- checklist_status: `future_unsigned`
- implementation_approved: false
- hosted_public_runtime_approved: false
- production_claim_allowed: false
