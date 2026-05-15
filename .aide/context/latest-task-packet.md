# AIDE Latest Task Packet

## PHASE

HUNT-REMEDIATION-CONTINUE - Finish remaining Search Hunt remediation

## GOAL

Close the remaining Search Hunt remediation continuation evidence, verify that
all HUNT and LOCAL dependency gates are green, and leave the handoff ready for
SYN-00 with F0 resumable but not recommended first.

## WHY

The previous remediation pass returned Search Hunt to a green closeout state,
but the continuation pass must prove that no child blockers, stale validation
records, or warning-gated gaps remain before SYN/F0 handoff.

## CONTEXT_REFS

- `control/inventory/hunt_remediation_result.json`
- `control/inventory/hunt_remediation_blocker_register.json`
- `control/inventory/hunt_remediation_warning_disposition.json`
- `control/inventory/hunt_remediation_validation_matrix.json`
- `control/inventory/hunt_remediation_next_task_decision.json`
- `control/inventory/hunt_remediation_continue_input_state.json`
- `control/inventory/hunt_remediation_continue_issue_register.json`
- `control/inventory/hunt_remediation_continue_repair_result.json`
- `control/inventory/hunt_remediation_continue_validation_matrix.json`
- `control/inventory/hunt_remediation_continue_smoke_result.json`
- `control/inventory/hunt_remediation_continue_boundary_audit.json`
- `control/inventory/hunt_remediation_continue_result.json`
- `control/inventory/hunt_remediation_continue_next_task_decision.json`
- `control/inventory/search_hunt_closeout_result.json`
- `control/inventory/search_hunt_capability_matrix.json`
- `control/inventory/search_hunt_validation_matrix.json`
- `control/inventory/search_hunt_warning_disposition.json`
- `control/inventory/search_hunt_blocker_register.json`
- `control/inventory/search_hunt_handoff_to_syn.json`
- `control/inventory/search_hunt_handoff_to_f0.json`
- `control/inventory/search_hunt_handoff_to_g_h_k.json`
- `control/audits/hunt-remediation-continue-v0/`
- `control/audits/hunt-remediation-v0/`
- `control/audits/hunt-12-search-hunt-closeout-v0/`
- `.aide/queue/index.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`

## ALLOWED_PATHS

- `.aide/**`
- `control/**`
- `docs/**`
- `scripts/**`
- `tests/**`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`
- `runtime/local_worker/**`
- `runtime/agent_research/**`
- `runtime/ai_escalation/**`
- `runtime/local_appliance/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/local_operator/**`
- `runtime/local_eval/**`

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

- Inspect repo-local remediation, closeout, validation, warning, and blocker evidence.
- Classify remaining HUNT issues and repair only safe evidence or validation drift.
- Update continuation inventories, audit pack, queue state, and repo-health.
- Keep the next task decision pointed at SYN-00 when validation remains green.

## NON_GOALS

- Do not implement SYN.
- Do not implement F0 extraction.
- Do not enable or run source probes.
- Do not run extraction.
- Do not call model or provider APIs.
- Do not browse the internet.
- Do not deploy.
- Do not claim production or public launch readiness.

## VALIDATION

- `python scripts/validate_hunt_remediation_continue.py --json`
- `python -m unittest tests.operations.test_hunt_remediation_continue`
- `python -m unittest tests.operations.test_hunt_remediation_continue_gate`
- `python -m unittest tests.operations.test_hunt_remediation_continue_handoff`
- all HUNT validators
- LOCAL dependency validators
- integrated local HUNT smoke
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/audit_runtime_architecture_leakage.py --check --json`
- `python scripts/validate_runtime_architecture_leakage.py`

## EVIDENCE

- Continuation input state, issue register, repair result, boundary audit,
  validation matrix, smoke result, final result, and next-task decision are under
  `control/inventory/`.
- Continuation audit evidence and generated samples are under
  `control/audits/hunt-remediation-continue-v0/`.
- Focused continuation tests live under `tests/operations/`.
- The continuation validator is `scripts/validate_hunt_remediation_continue.py`.
- Queue and repo-health metadata keep SYN-00 as the recommended next task.

## ACCEPTANCE

- All remaining issues are reviewed.
- Hard blockers remaining is zero.
- Warnings remaining is zero.
- All HUNT validators pass.
- LOCAL dependency validators pass.
- HUNT workflow smoke passes.
- Full unittest discovery passes.
- Generated artifact cleanliness passes after commit.
- Architecture and runtime leakage gates pass.
- SYN can start.
- F0 can resume but is not recommended before SYN.
- Main promotion remains a separate review task.

## OUTPUT_SCHEMA

- status
- summary
- commits
- remediation_continue
- validation
- boundaries
- handoff
- next_task

## TOKEN_ESTIMATE

- method: chars / 4 rounded up
- budget_status: pass
