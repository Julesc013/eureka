# OBS0-01 Manual Observation Protocol

This audit adds the Manual Observation Batch 0 protocol and anti-fabrication checklist.

## Added

- Canonical manual observation protocol docs.
- Anti-fabrication checklist.
- Failure taxonomy docs and machine-readable inventory.
- Manual observation policy inventory.
- Batch 0 local protocol references.
- Synthetic valid and invalid examples.
- Local-only validator and tests.

## Why This Follows Track A

Track A established canonical view-model and renderer-parity governance. Manual Observation Batch 0 will feed future SearchNeed, Candidate, Absence, Compare, and WorkUnit fixtures, so the observation method needs anti-fabrication rules before any human-operated collection begins.

## Human-Operated Boundary

This task performs no observations. It opens no browsers, fetches no URLs, calls no APIs, runs no source connectors, and marks no pending slot observed.

## Anti-Fabrication Enforcement

The policy requires observed records to include manual-session evidence fields and attestation. The validator accepts valid synthetic examples, rejects the fabricated example, and checks that Batch 0 pending slots remain pending.

## Deferred

- Actual Batch 0 manual observation execution.
- Comparison synthesis from observed records.
- SearchNeed, Candidate, Absence, Compare, and WorkUnit fixture derivation from real observations.

## Validation

```powershell
python -m json.tool control/inventory/observations/manual_observation_policy.json
python -m json.tool control/inventory/observations/manual_observation_failure_taxonomy.json
python -m json.tool control/audits/obs0-01-manual-observation-protocol-v0/obs0_01_report.json
python scripts/validate_manual_observation_protocol.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

## No-Goals

- No actual external observations.
- No browser automation or browser opening.
- No external search automation, scraping, crawling, URL fetching, APIs, or model/provider calls.
- No fabricated baselines.
- No pending slot marked observed.
- No Eureka product behavior, route, hosting, live probe, connector, download, upload, account, telemetry, native, or master-index change.

## Next

OBS0-02 - Manual Observation Batch 0 execution packet.
