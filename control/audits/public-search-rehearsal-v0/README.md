# Public Search Rehearsal v0

This audit pack records the local/prototype rehearsal for Eureka public search.

Decision: `local_rehearsal_passed`.

The rehearsal exercises the local public search runtime, static search handoff,
public-alpha posture, and governed request/error/result-card contracts without
deploying anything and without enabling live probes, downloads, installs,
uploads, telemetry, accounts, arbitrary URL fetch, external search calls, or
caller-provided local paths.

Hosted public search remains unavailable. This pack is local evidence only.

## Files

- `REHEARSAL_SCOPE.md`: local-only scope and non-goals.
- `ROUTE_MATRIX.md`: public search route coverage.
- `SAFE_QUERY_RESULTS.md`: representative successful/no-result query evidence.
- `BLOCKED_REQUEST_RESULTS.md`: governed rejection evidence.
- `STATIC_HANDOFF_REVIEW.md`: static search handoff review.
- `PUBLIC_ALPHA_REVIEW.md`: public-alpha route/smoke review.
- `CONTRACT_ALIGNMENT_REVIEW.md`: contract alignment review.
- `LIMITATIONS_AND_BLOCKERS.md`: remaining limits and blockers.
- `NEXT_STEPS.md`: next milestone sequence.
- `public_search_rehearsal_report.json`: structured report for validation.
