# AIDE Review Packet

## Review Objective

Review HUNT-09: Agent research task contract, provider disabled.

## Decision Requested

PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED

## Task Packet Reference

`.aide/queue/HUNT-09/task.yaml`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/verification/latest-verification-report.md`

## Evidence Packet References

- `control/audits/hunt-09-agent-research-task-contract-v0/`
- `control/inventory/agent_research_task_result.json`
- `control/inventory/agent_research_disabled_boundary_result.json`
- `control/inventory/agent_research_report_schema_inventory.json`
- `control/inventory/hunt_09_next_task_decision.json`
- `scripts/validate_agent_research_task_contract.py`

## Changed Files Summary

- Added `runtime/agent_research/` records, schema, store, task builder, report schema, validation, and queries.
- Added local appliance store integration for `db/agent_research.sqlite`.
- Added CLI, demo, validator, policies, inventories, audit pack, docs, and focused tests.
- Added API/workbench visibility for disabled agent research task drafts on hunt and SearchNeed pages.
- Advanced queue metadata to HUNT-10.

## Validation Summary

- `python scripts/validate_agent_research_task_contract.py --json`: PASS.
- Agent research focused runtime and operations tests: PASS.
- JSON syntax checks for HUNT-09 policy, inventory, and audit report files: PASS.
- `git diff --check`: PASS with line-ending warnings.
- `python scripts/check_architecture_boundaries.py`: PASS.
- Generated artifact cleanliness is expected to pass after commit; pre-commit drift is the new audit pack.
- Broad `python -m unittest discover -s tests -t .` timed out and should be treated as a validation warning.

## Token Summary

Compact packet only; full historical HUNT prompts are intentionally not copied here.

## Risk Summary

- Provider and task execution remain disabled.
- HUNT-06 through HUNT-08 validators are queue-position sensitive and fail after the queue advances to HUNT-10.
- LOCAL validators carry pre-existing runtime leakage warnings.

## Non-Goals / Scope Guard

HUNT-09 did not add model/provider calls, browser calls, source probes, extraction, agent execution, review/index mutation, deployment, production readiness, or public launch readiness.

## Reviewer Instructions

Review against repo-local files and HUNT-09 evidence. Treat agent research output as candidate-only contract scaffolding, not truth, evidence acceptance, provider approval, or execution readiness.
