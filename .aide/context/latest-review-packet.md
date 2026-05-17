# AIDE Latest Review Packet

## Review Objective

Review INSTANCE-LAYOUT-PREFLIGHT-01 evidence and confirm the next task can be INSTANCE-LAYOUT-01.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

Confirm whether the four pre-existing local-instance docs were safely classified and preserved.

## Task Packet Reference

- `.aide/context/latest-task-packet.md`

## Context Packet Reference

- `.aide/context/latest-context-packet.md`

## Verification Report Reference

- `.aide/verification/latest-verification-report.md`
- `.aide/verification/review-decision-policy.yaml`

## Evidence Packet References

- `control/inventory/instance_layout_preflight_input_state.json`
- `control/inventory/instance_layout_preflight_diff_classification.json`
- `control/inventory/instance_layout_preflight_result.json`
- `control/audits/instance-layout-preflight-01-v0/`

## Changed Files Summary

- Local-instance docs were preserved.
- Preflight classification inventories and audit evidence were added.
- Queue/context metadata now points to INSTANCE-LAYOUT-01.

## Validation Summary

- JSON and diff validation are required for the preflight evidence.
- Commit check should run after committing the preflight docs and evidence.

## Token Summary

- Review packet is compact and evidence-only; raw prompt/response bodies are not included.

## Risk Summary

- No runtime, script, test, instance, source-probe, extraction, model/provider, deployment, production-readiness, or public-launch behavior is changed.

## Non-Goals / Scope Guard

No operator instance moves or deletion, source probes, extraction, model/provider calls, downloads, installs, deployment, force push, history rewrite, or product behavior change.

## Reviewer Instructions

- Check the diff classification and preflight result before accepting INSTANCE-LAYOUT-01 as the next task.
