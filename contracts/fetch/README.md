# Fetch Contracts

These contracts describe the safe independent page-fetching milestone for
`EUREKA-REAL-LIVE-SEARCH-HUNT-00`.

Fetch output is not reviewed truth. A successful fetch may produce an
unreviewed `SourceObservation` that later becomes a Preview Index document.
Provider SearchLead fields such as Brave snippets, ranks, and raw responses are
not part of these durable fetch contracts.

The safe fetch surface includes:

- `FetchRequest`
- `FetchPolicy`
- `FetchBudget`
- `FetchOutcome`
- `FetchError`
- `RobotsDecision`
- `ExtractedDocument`
- `SourceObservation`
- `LinkEdge`
