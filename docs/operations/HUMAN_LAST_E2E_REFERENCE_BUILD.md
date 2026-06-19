# Human-Last E2E Reference Build

This runbook records the operating posture for
`HUMAN-LAST-E2E-REFERENCE-BUILD-00`.

## Operating Posture

Routine human candidate review pauses while Eureka builds a coherent local
reference system. The human returns for product-level calibration and later
end-to-end acceptance, not for routine mid-build candidate debugging.

Real discoveries remain provisional until explicit human review.

## Current Frozen Review Material

The IA review packet remains available for later acceptance testing:

- 56 prepared IA candidates
- 8 `request_more_evidence` decisions
- 48 parent-batch items still pending
- 0 promoted candidates
- 0 reviewed records

The eight decisions are provisional Review Ledger evidence requests. They are
not accepted truth and may be revisited after new evidence.

## Synthetic Truth Path

Automation may prove the truth-changing mechanism only in an isolated synthetic
namespace:

```text
synthetic observation
-> synthetic candidate
-> predetermined synthetic review decision
-> isolated Review Ledger
-> synthetic reviewed record
-> test index rebuild
-> search-result status change
-> rollback
-> snapshot verification
```

This does not authorize promotion of real IA candidates.

## Deferred Human Review

Resume real review after the local reference system provides a coherent
operator experience:

```text
enter query
-> inspect local results
-> start or continue a Hunt
-> observe WorkUnits and source activity
-> inspect candidate, evidence, absence, and near-miss lanes
-> save and replay the run
-> test synthetic review/index mechanics
-> verify rollback and snapshots
```

## Hard Gates

Keep explicit approval for:

- new live-provider access
- real Review Ledger decisions
- reviewed-record materialization
- reviewed/master-index mutation
- public-index mutation
- public exposure
- downloads, installation, or execution behavior
- license changes

Next task:

```text
E2E-REFERENCE-SYSTEM-TRACK-00
```

