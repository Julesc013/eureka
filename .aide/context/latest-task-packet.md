# AIDE Latest Task Packet

## PHASE

SYN-00 - Synthetic Query Foundry planning over Local Appliance

## GOAL

Plan the Synthetic Query Foundry track after HUNT remediation closed the Search
Hunt spine with no hard blockers or remaining HUNT closeout warnings.

## WHY

Search Hunt now provides the active local investigation spine: Search Hunt
Sessions, exhaustion reports, SearchNeeds, WorkUnits, deterministic workers,
replay, agent-task contracts, and a disabled AI escalation gate. SYN should
create query and eval pressure before extraction/source expansion resumes.

## CONTEXT_REFS

- `control/inventory/search_hunt_closeout_result.json`
- `control/inventory/search_hunt_capability_matrix.json`
- `control/inventory/search_hunt_handoff_to_syn.json`
- `control/inventory/hunt_remediation_next_task_decision.json`
- `control/inventory/hunt_12_next_task_decision.json`
- `control/audits/hunt-remediation-v0/`
- `control/audits/hunt-12-search-hunt-closeout-v0/`
- `.aide/queue/index.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `.aide/**`
- `.aide/cache/**`
- `.aide/context/**`
- `.aide/controller/**`
- `.aide/gateway/**`
- `.aide/providers/**`
- `.aide/reports/**`
- `.aide/verification/**`
- `control/**`
- `docs/**`
- `scripts/**`
- `tests/**`
- `runtime/local_appliance/**`
- `runtime/local_eval/**`
- `runtime/local_operator/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- `secrets/**`
- `site/dist/**`
- private local files
- operator tokens
- provider credentials

## IMPLEMENTATION

- Start from the remediation and closeout evidence, not chat history.
- Keep SYN planning local and deterministic.
- Use HUNT/WorkUnit/Local Appliance boundaries for query pressure planning.
- Do not implement SYN runtime, F0 extraction, source probes, AI execution, or deployment.

## VALIDATION

- Run the task-state guard before substantive work.
- Use HUNT remediation, closeout, generated artifact cleanliness, architecture
  boundary, and relevant AIDE checks before handoff.
- Report every command actually run and its outcome.

## EVIDENCE

- `control/inventory/hunt_remediation_result.json`
- `control/inventory/hunt_remediation_validation_matrix.json`
- `control/inventory/search_hunt_closeout_result.json`
- `control/inventory/search_hunt_handoff_to_syn.json`
- `control/audits/hunt-remediation-v0/`

## ACCEPTANCE

- SYN-00 remains the recommended next task.
- F0-00 remains resumable but not recommended before SYN unless explicitly chosen.
- No source probes, extraction, provider/model calls, deployment, production
  readiness claim, or public launch readiness claim are introduced.

## OUTPUT_SCHEMA

- STATUS: PASS / PASS_WITH_WARNINGS / PARTIAL / BLOCKED / FAIL
- SUMMARY: concise bullets
- VALIDATION: commands and outcomes
- NEXT_TASK: SYN-00 or explicit blocked/remediation alternative

## TOKEN_ESTIMATE

- small

## NON_GOALS

Do not start F0 implementation, source probes, extraction, model/provider
calls, deployment, production readiness, or public launch readiness.
