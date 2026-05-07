# AIDE Latest Review Packet

## Review Objective

Review the current AIDE queue phase from compact evidence only and decide whether it is ready to pass its review gate.

## Decision Requested

Return exactly one of `PASS`, `PASS_WITH_NOTES`, `REQUEST_CHANGES`, or `BLOCKED`.

## Task Packet Reference

- `.aide/context/latest-task-packet.md` (3792 chars, 948 approximate tokens)

## Context Packet Reference

- `.aide/context/latest-context-packet.md` (1807 chars, 452 approximate tokens)
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`

## Verification Report Reference

- `.aide/verification/latest-verification-report.md`
- verifier_result: WARN
- report_chars: 5571
- report_approx_tokens: 1393

## Evidence Packet References

- `.aide/queue/README.template.md`

## Changed Files Summary

- unknown: `.aide.local.example` (??; does not match active task allowed paths)
- unknown: `.aide/cache/latest-cache-keys.json` (??; does not match active task allowed paths)
- unknown: `.aide/cache/latest-cache-keys.md` (??; does not match active task allowed paths)
- allowed: `.aide/context/context-index.json` (??; matches active task allowed path)
- allowed: `.aide/context/latest-context-packet.md` (??; matches active task allowed path)
- allowed: `.aide/context/latest-review-packet.md` (??; matches active task allowed path)
- allowed: `.aide/context/latest-task-packet.md` (??; matches active task allowed path)
- allowed: `.aide/context/repo-map.json` (??; matches active task allowed path)
- allowed: `.aide/context/repo-map.md` (??; matches active task allowed path)
- allowed: `.aide/context/repo-snapshot.json` (??; matches active task allowed path)
- allowed: `.aide/context/test-map.json` (??; matches active task allowed path)
- allowed: `.aide/controller` (??; matches active task allowed path)
- allowed: `.aide/evals/runs` (??; matches active task allowed path)
- unknown: `.aide/generated` (??; does not match active task allowed paths)
- unknown: `.aide/import-policy.yaml` (M; does not match active task allowed paths)
- allowed: `.aide/models/README.md` (??; matches active task allowed path)
- allowed: `.aide/reports/token-baselines.yaml` (??; matches active task allowed path)
- allowed: `.aide/reports/token-ledger.jsonl` (??; matches active task allowed path)
- allowed: `.aide/reports/token-savings-summary.md` (??; matches active task allowed path)
- allowed: `.aide/routing/latest-route-decision.json` (??; matches active task allowed path)
- allowed: `.aide/routing/latest-route-decision.md` (??; matches active task allowed path)
- allowed: `.aide/verification/latest-verification-report.md` (??; matches active task allowed path)

## Validation Summary

- validation evidence not found

## Token Summary

- packet_path: `.aide/context/latest-review-packet.md`
- method: chars / 4, rounded up
- chars: 5340
- approx_tokens: 1335
- budget_status: PASS
- max_token_warning: 2400
- warnings:
- none
- formal ledger: `.aide/reports/token-ledger.jsonl`

## Outcome Controller Summary

- outcome_report: `.aide/controller/latest-outcome-report.md`
- outcome_result: WARN
- recommendations: `.aide/controller/latest-recommendations.md` (missing)
- applies_automatically: false

## Route Decision Summary

- route_decision: `.aide/routing/latest-route-decision.json`
- route_class: local_strong
- task_class: bounded_code_patch
- hard_floor_applied: none
- quality_gate_status: WARN
- advisory_only: true

## Cache / Local State Summary

- cache_keys: `.aide/cache/latest-cache-keys.json`
- local_state_ignored: true
- tracked_local_state_paths: 0
- raw_prompt_storage: false
- raw_response_storage: false
- cache_key_count: 7

## Gateway Skeleton Summary

- gateway_status: `.aide/gateway/latest-gateway-status.json` (missing; run gateway status)
- local_skeleton: true
- provider_or_model_calls: none

## Provider Adapter Summary

- provider_status: `.aide/providers/latest-provider-status.json` (missing; run provider status)
- offline_metadata_only: true
- live_provider_calls: false

## Risk Summary

- This is the first real target-repo import; target adaptation may expose pack assumptions that were invisible inside AIDE.
- Eureka-specific golden tasks are not yet established, so quality evidence is limited to AIDE Lite substrate checks and packet review.
- No provider routing, Gateway forwarding, model-call enforcement, or autonomous loop is enabled in this pilot.
- Token measurement uses the approximate `chars / 4` method, not an exact tokenizer or provider billing integration.
- Imported pack commands may need follow-up adaptation after Q22 if direct import behavior or validation warnings are too broad for target repos.

## Non-Goals / Scope Guard

- Gateway
- provider calls
- model routing
- Runtime/Service/Commander/UI/Mobile
- MCP/A2A
- automatic model calls or repair

## Reviewer Instructions

- Review only this packet and the referenced evidence when needed.
- Do not request full chat history unless the packet is insufficient to judge correctness.
- Do not re-summarize the whole project.
- Do not reward scope creep.
- Do not approve missing validation as a pass.
- Required output sections: `DECISION`, `REASONS`, `REQUIRED_FIXES`, `OPTIONAL_NOTES`, `NEXT_PHASE`.
- Decision policy: `.aide/verification/review-decision-policy.yaml`.
