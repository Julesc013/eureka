# Query Contracts

`contracts/query/` holds governed Query Intelligence Plane contracts. These
contracts are not runtime logging, telemetry, cache, miss-ledger, probe-queue,
candidate-index, or master-index behavior.

Current contracts:

- `query_observation.v0.json`: privacy-filtered query observation record for
  future public search learning. P59 defines the record shape, validation
  posture, example, and privacy policy without adding persistence or public
  query logging.
- `search_result_cache_entry.v0.json`: shared query/result cache entry record
  for future reuse of safe result summaries and scoped absence/gap outcomes.
  P60 defines the cache boundary without adding runtime cache writes,
  persistence, telemetry, miss-ledger mutation, probes, candidate-index
  mutation, or master-index mutation.
- `cache_key.v0.json`: reusable non-reversible cache-key model for future
  cache entries and aggregate grouping.
- `search_miss_ledger_entry.v0.json`: search miss ledger entry record for
  future privacy-filtered tracking of no-hit, weak-hit, near-miss, blocked, and
  incomplete searches. P61 defines scoped miss records without adding miss
  ledger runtime writes, persistence, telemetry, search need creation, probe
  enqueueing, result-cache mutation, candidate-index mutation, or master-index
  mutation.
- `search_miss_classification.v0.json`: reusable miss classification taxonomy
  for scoped absence and weak-result categories. It forbids global absence
  claims in v0.
- `search_need_record.v0.json`: search need record contract for future
  aggregation of privacy-filtered unresolved needs. P62 defines need identity,
  target object, input refs, gap model, aggregation posture, and no-mutation
  guarantees without adding a runtime need store, telemetry, probe queue,
  candidate index, demand dashboard, or master-index mutation.
- `search_need_lifecycle.v0.json`: reusable lifecycle status contract for
  future search need review, merge, supersede, and resolve states.

Query intelligence follows "fast learning, slow truth": public queries may
eventually inform aggregate learning, but they must not mutate authoritative
records, enqueue probes, publish raw private data, or become surveillance.
Shared cache entries are summaries scoped to an index snapshot, never source
truth or proof outside the checked scope.
Miss ledger entries are scoped learning records, not search needs, probe jobs,
candidate records, source truth, or master-index truth.
Search need records are scoped unresolved-need records, not search results,
probe jobs, candidate records, demand counts, source truth, or master-index
truth.
