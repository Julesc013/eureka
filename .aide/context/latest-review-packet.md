# AIDE Review Packet

## Review Objective

Review HUNT-10: Deterministic hunt replay harness.

## Decision Requested

PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED

## Task Packet Reference

`.aide/queue/HUNT-10/task.yaml`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/verification/latest-verification-report.md`

## Evidence Packet References

- `control/audits/hunt-10-deterministic-replay-v0/`
- `control/inventory/hunt_replay_result.json`
- `control/inventory/hunt_replay_demo_result.json`
- `control/inventory/hunt_replay_step_matrix.json`
- `control/inventory/hunt_replay_blocked_step_matrix.json`
- `control/inventory/hunt_10_next_task_decision.json`
- `scripts/validate_hunt_replay.py`

## Changed Files Summary

- Added deterministic Search Hunt replay records, fixtures, diffing, validation, and store support.
- Added replay CLI, demo, validator, policies, inventories, audit pack, docs, and focused tests.
- Added API/workbench visibility and localhost/token-gated replay run controls.
- Advanced queue metadata to HUNT-11.

## Validation Summary

- `python scripts/validate_hunt_replay.py --json`: expected PASS for HUNT-10.
- Hunt replay focused runtime and operations tests cover plan, replay-local, verify-existing, routes, UI, policy, diff, and scripts.
- JSON syntax checks cover HUNT-10 policy, inventory, and audit report files.
- Broad validation status should be reported in the final HUNT-10 response.

## Token Summary

Compact packet only; full historical HUNT prompts are intentionally not copied here.

## Risk Summary

- Replay-local records deterministic local replay effects in the explicit local instance; validators use disposable temp instances for isolation.
- HUNT validators from earlier queue phases may be queue-position sensitive after the queue advances to HUNT-11.
- LOCAL validators may retain pre-existing runtime leakage warnings.

## Non-Goals / Scope Guard

HUNT-10 did not add source probes, extraction, AI/model/provider calls, browser calls, artifact acquisition, artifact launch, master-index mutation, site output mutation, deployment, production readiness, or public launch readiness.

## Reviewer Instructions

Review against repo-local files and HUNT-10 evidence. Treat replay output as local reproducibility/audit data, not truth, evidence acceptance, source approval, or global absence proof.
