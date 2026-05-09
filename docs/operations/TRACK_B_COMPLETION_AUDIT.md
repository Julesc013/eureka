# Track B Completion Audit

The Track B completion audit verifies the local foundry spine without changing
product behavior. It checks contracts, policies, runtime modules, scripts,
examples, tests, audit reports, and boundary flags from Track B tasks 01
through 22.

## How To Rerun

```bash
python scripts/audit_track_b_integration.py --list
python scripts/audit_track_b_integration.py --check
python scripts/audit_track_b_integration.py --json-output control/audits/track-b-23-integration-audit-v0/track_b_23_report.json
```

## Decision Values

- `PASS`: Track B is complete and no warnings remain.
- `PASS_WITH_WARNINGS`: Track B can proceed, but documented warnings remain.
- `PARTIAL`: remediation is required before first connector approval.
- `FAIL`: Track B is incomplete or unsafe.

## Connector Readiness

Track B prepares the first Internet Archive metadata connector approval pattern
by providing source cache, evidence candidate, bridge, review queue, promotion
dry-run, public-index proposal contract, pack builder, and pack export
boundaries.

Approval is still required before any external call. The IA task must decide
source policy, User-Agent/contact posture, rate limits, cache TTL, and kill
switch behavior.

## No-Goals

- No live source access.
- No source connector runtime.
- No network, API, model, or provider call.
- No WorkUnit execution.
- No public-index or master-index mutation.
- No accepted evidence, accepted candidate, or accepted public truth.
- No downloads, uploads, accounts, telemetry, pack import, pack submission, or
  hosted review.
