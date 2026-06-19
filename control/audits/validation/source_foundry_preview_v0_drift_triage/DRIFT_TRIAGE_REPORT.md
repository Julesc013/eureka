# Drift Triage Report

Status: `BLOCKED_UNKNOWN_FAILURES`

## Summary

- classified tests: 50
- failure families: 31
- counts by classification: `{"historical_queue_expectation_drift": 26, "historical_validator_drift": 20, "obsolete_test_candidate": 1, "unknown_requires_investigation": 3}`
- repaired count: 0
- unknown groups: `["local_worker_validator_unknown_or_slow", "runtime_leakage_safety_unknown"]`
- external rerun justified now: false

## Posture

- public safety: unchanged; public exposure remains paused
- truth/index mutation: unchanged; no reviewed truth or index mutation authorized
- main promotion: blocked until targeted repairs are green and a later external full-discovery rerun returns failures=0 and errors=0

## Blocker

No targeted repairs were applied in this triage pass; runtime leakage and local worker groups remain unresolved/unknown; historical validators still fail targeted probes.

Recommended next task: `SOURCE-FOUNDRY-PREVIEW-V0-FULL-DISCOVERY-DRIFT-REPAIR-01`
