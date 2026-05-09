# First Connector Prerequisite Review

Decision: `READY_WITH_WARNINGS`.

This review assesses readiness for the first Internet Archive metadata
connector approval pattern. It does not approve, implement, or run a connector.

## Passed Prerequisites

- Source cache runtime exists.
- Evidence ledger runtime exists.
- Source-cache-to-evidence bridge exists.
- Local review queue exists.
- Candidate promotion dry-run exists.
- Pack builder and pack export exist.
- Reviewed public-index rebuild contract exists.
- No live connector is enabled.
- No external call is allowed by this audit.

## Still Required Before Any External Call

- Source policy approval.
- User-Agent and contact decision.
- Rate-limit, quota, and cache TTL decision.
- Kill switch and failure-mode decision.
- Explicit connector approval task.

## Rationale

The local foundry spine can represent connector-derived observations as source
cache records, evidence candidates, review queue entries, promotion dry-runs,
and pack drafts. It still cannot call the Internet Archive or any other
external source until IA approval is explicitly granted.
