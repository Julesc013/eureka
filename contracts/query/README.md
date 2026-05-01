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

Query intelligence follows "fast learning, slow truth": public queries may
eventually inform aggregate learning, but they must not mutate authoritative
records, enqueue probes, publish raw private data, or become surveillance.
Shared cache entries are summaries scoped to an index snapshot, never source
truth or global absence proof.
