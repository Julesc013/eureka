# Query Observation Runtime Model

Query observation follows the Local Foundry State contract. It is the first
small local runtime that can prepare reviewable signals without creating
private local roots or changing public behavior.

## Data Flow

1. A human or test provides an explicit JSON input.
2. The runtime normalizes the record in memory.
3. Privacy filtering hashes or redacts query text when needed.
4. The poisoning guard flags risky input patterns for review.
5. The outcome classifier labels the local result posture.
6. The CLI prints a summary and writes only when an explicit allowed output path
   is provided.

## Runtime Boundary

The runtime is local-only and standard-library only. It does not call sources,
models, providers, browsers, APIs, or public search. It does not observe hosted
users, collect public traffic, enable telemetry, or create local private state
roots.

## Downstream Boundary

Query observations may later inform miss-ledger records, SearchNeeds, WorkUnit
seeds, candidate generation, and search-quality reports. Human review is
required before downstream use. Query demand never becomes object truth,
accepted evidence, or a master-index mutation.

## Replay Posture

The functions are deterministic over explicit input and safe to replay. A
record can be ignored without changing product behavior.
