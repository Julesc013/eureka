# Contract Inventory

The inventory inspected existing contracts, runtime/read-only evidence,
reference docs, prior taxonomy reports, and source-wave contract outputs.

Key prior taxonomy evidence:

- R0-03A counted 322 product contracts and 686 total contracts.
- R0-03B-1 moved 278 taxonomy items without product behavior changes.

The E2E chain therefore reuses existing contracts and profiles instead of
creating a new parallel contract family.

## Concepts

- QueryIntent: fragmented across search request, compiled query, query-plan,
  query hint, and search-need contracts.
- ResolutionRun: formal core contract exists with UI/view projections.
- WorkUnit: formal reference docs and workunit seed/result contracts exist.
- SourceObservation: strict runtime contract exists.
- EvidenceSummary: public-safe projection exists; internal authority maps to
  evidence ledger/store contracts.
- Candidate: several specialized candidate contracts exist; the E2E profile
  selects a common envelope plus typed payload/ref semantics.
- PreviewRecord: projection gap; public result card is not core authority.
- ReviewItem: runtime queue-item contract exists but must not decide truth.
- ReviewDecision: store/ledger decision contract exists.
- ReviewedRecord: limited reviewed metadata contracts exist with explicit
  non-claims.
- IndexDelta: rebuild/apply/result contracts exist; lifecycle profile needed.
- SnapshotManifest: distribution manifests exist; profile distinguishes
  snapshot distribution from truth authority.

