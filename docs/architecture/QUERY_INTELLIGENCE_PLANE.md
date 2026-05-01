# Query Intelligence Plane

Status: contract-only through P61.

The Query Intelligence Plane is the future layer that lets Eureka learn from
public search demand without turning public queries into surveillance or
authoritative truth. Its first contracts are the P59 query observation record,
the P60 shared query/result cache entry, and the P61 search miss ledger entry.

The core doctrine is fast learning, slow truth:

- Public queries may eventually produce privacy-filtered aggregate learning.
- Query observation is not telemetry runtime.
- Query observation is not persistent query logging.
- Query observation is not a result cache, miss ledger, probe queue, candidate
  index, or master-index mutation.
- Shared query/result cache is not telemetry, not source evidence, not
  master-index truth, and not proof outside the checked scope.
- Shared query/result cache is not master-index truth.
- Search miss ledger entries are scoped learning records, not search needs,
  probe jobs, candidate records, or master-index truth.
- Public query learning cannot become object truth without later evidence and
  validation gates.

## P59 Boundary

P59 defines `contracts/query/query_observation.v0.json`, a synthetic example,
validators, docs, and an optional dry-run helper that writes nothing. It does
not wire the public search runtime to write observations.

Hard guarantees for P59:

- no runtime persistence
- no telemetry
- no public query logging
- no raw private-looking query publication
- no probe queue
- no shared result cache mutation
- no miss ledger mutation
- no candidate index mutation
- no local index mutation
- no master-index mutation
- no external calls or live probes

## P60 Boundary

P60 defines `contracts/query/search_result_cache_entry.v0.json` and
`contracts/query/cache_key.v0.json`, synthetic examples, validators, docs, and
an optional dry-run helper that writes nothing. It does not wire public search
runtime to read or write cache entries.

Hard guarantees for P60:

- no runtime cache writes
- no persistent cache storage
- no telemetry
- no public query logging
- no raw private-looking query retention
- no miss ledger mutation
- no search need mutation
- no probe queue
- no candidate index mutation
- no local index mutation
- no master-index mutation
- no external calls or live probes

Cached result summaries are scoped to checked public index snapshots. Cached
absence is scoped absence, not proof outside the checked scope.

## P61 Boundary

P61 defines `contracts/query/search_miss_ledger_entry.v0.json` and
`contracts/query/search_miss_classification.v0.json`, synthetic no-hit and
weak-hit examples, validators, docs, and an optional dry-run helper that writes
nothing. It does not wire the public search runtime to write miss ledger
entries.

Hard guarantees for P61:

- no runtime ledger writes
- no persistent ledger storage
- no telemetry
- no public query logging
- no raw private-looking query retention
- no search need creation
- no probe enqueueing
- no result cache mutation
- no candidate index mutation
- no local index mutation
- no master-index mutation
- no external calls or live probes

Miss ledger entries record scoped absence, weak hits, near misses, blocked
queries, or incomplete searches against checked indexes, source families, and
capabilities. They are contract-only and not master-index truth.

## Future Path

Future milestones may define search need record, probe queue, candidate index,
candidate promotion policy, query privacy and poisoning guard, and demand
dashboard. Each must preserve the separation between observed demand, reusable
summaries, candidate work, and accepted truth.
