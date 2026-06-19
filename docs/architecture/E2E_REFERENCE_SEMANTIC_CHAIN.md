# E2E Reference Semantic Chain

Task: `E2E-REFERENCE-CONTRACT-00`

## Purpose

The E2E reference semantic chain is a map over Eureka's existing contracts. It
does not create a second model and it does not implement the runner.

The chain is:

```text
QueryIntent
-> ResolutionRun
-> WorkUnit
-> SourceObservation
-> EvidenceSummary
-> Candidate
-> PreviewRecord
-> ReviewItem
-> ReviewDecision
-> ReviewedRecord
-> IndexDelta
-> SnapshotManifest
```

## Plane Ownership

| Concept | Owning Plane | Boundary |
| --- | --- | --- |
| QueryIntent | Discovery | User/search meaning before work is scheduled |
| ResolutionRun | Discovery | A bounded run over a compiled query |
| WorkUnit | Discovery | A bounded work proposal or execution unit |
| SourceObservation | Evidence | What a source said, with provenance and limits |
| EvidenceSummary | Evidence | Evidence support or absence, not accepted truth |
| Candidate | Preview | Provisional object requiring review |
| PreviewRecord | Preview | Searchable status-aware projection |
| ReviewItem | Truth | Review queue entry, not a decision |
| ReviewDecision | Truth | Attributable operator decision event |
| ReviewedRecord | Truth | Materialized reviewed local record |
| IndexDelta | Distribution | Rebuildable change set for an index |
| SnapshotManifest | Distribution | Snapshot integrity and distribution manifest |

## Invariant

Discovery may propose. Evidence may support. Preview may project. Review may
decide. Truth may materialize. Distribution may publish permitted projections.
Control may constrain and verify.

No concept may silently assume a later concept's authority.

## Key Distinctions

- `contracts/api/evidence_summary.v0.json` is public-safe projection; internal
  evidence authority is mapped to evidence ledger/store contracts.
- `ReviewItem` cannot substitute for `ReviewDecision`.
- A `Candidate` cannot become a `ReviewedRecord` without explicit decision and
  materialization.
- `PreviewRecord` is not the same as a public result card.
- `ReviewedRecord` does not imply binary verification, malware safety, rights
  clearance, download safety, or public eligibility.
- `SnapshotManifest` distributes permitted projections; it does not create
  review authority.

## Dependency Diagram

```text
QueryIntent
  -> ResolutionRun
    -> WorkUnit
      -> SourceObservation
        -> EvidenceSummary
          -> Candidate
            -> PreviewRecord
            -> ReviewItem
              -> ReviewDecision
                -> ReviewedRecord
                  -> IndexDelta
                    -> SnapshotManifest
```

