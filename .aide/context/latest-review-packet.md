# AIDE Latest Review Packet

## Review Objective

Review HUNT-04 compact evidence and decide whether Search Hunt exhaustion reports are ready to pass their review gate.

## Context Packet Reference

- `.aide/context/latest-context-packet.md`

## Verification Report Reference

- `.aide/verification/latest-verification-report.md`

## Token Summary

- latest_task_packet: compact HUNT-05 packet
- latest_review_packet: compact HUNT-04 review packet

## Decision Requested

Return exactly one of `PASS`, `PASS_WITH_NOTES`, `REQUEST_CHANGES`, or `BLOCKED`.

## Task Packet Reference

- `.aide/context/latest-task-packet.md` now points to HUNT-05 after HUNT-04 completion.

## Evidence Packet References

- `control/audits/hunt-04-hunt-exhaustion-report-v0/README.md`
- `control/audits/hunt-04-hunt-exhaustion-report-v0/hunt_04_report.json`
- `control/inventory/search_hunt_exhaustion_result.json`
- `control/inventory/search_hunt_exhaustion_section_matrix.json`
- `control/inventory/hunt_04_next_task_decision.json`
- `.aide/queue/index.yaml`

## Changed Files Summary

- Search Hunt exhaustion runtime and persisted report rows under `runtime/search_hunt/`
- Local exhaustion routes under `runtime/local_service/`
- Workbench exhaustion visibility under `runtime/local_workbench/`
- Exhaustion CLI, demo, validator, tests, policies, inventories, docs, and audit evidence

## Validation Summary

- HUNT-04 validator: `python scripts/validate_search_hunt_exhaustion.py`
- HUNT-04 focused tests: exhaustion runtime, records, routes, UI, auth, scripts
- Existing HUNT validators: HUNT-03 commands, HUNT-02 UI, HUNT-01 runtime, HUNT-00 track
- LOCAL validators and repo checks per final task report

## Risk Summary

- HUNT-04 writes only Search Hunt exhaustion report rows and command-history entries for report generation.
- WorkUnit creation remains disabled.
- Source probes, extraction, model/provider calls, review/index mutation, LAN generation, deployment, production readiness claims, and public launch readiness claims remain forbidden.
- HUNT-05 should add SearchNeed behavior before hunt-to-WorkUnit behavior.

## Non-Goals / Scope Guard

- No WorkUnit creation
- No source probes
- No extraction
- No SYN or F0 implementation
- No AI/model/provider calls
- No LAN generation
- No deployment
- No production/public launch readiness claim

## Reviewer Instructions

- Review only this packet and the referenced evidence when needed.
- Do not request full chat history unless the packet is insufficient to judge correctness.
- Do not reward scope creep.
- Do not approve missing validation as a pass.
- Required output sections: `DECISION`, `REASONS`, `REQUIRED_FIXES`, `OPTIONAL_NOTES`, `NEXT_PHASE`.
