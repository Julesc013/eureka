# Query Contracts

`contracts/query/` holds governed Query Intelligence Plane contracts. These
contracts are not runtime logging, telemetry, cache, miss-ledger, probe-queue,
candidate-index, or master-index behavior.

Current contracts:

- `query_observation.v0.json`: privacy-filtered query observation record for
  future public search learning. P59 defines the record shape, validation
  posture, example, and privacy policy without adding persistence or public
  query logging.

Query intelligence follows "fast learning, slow truth": public queries may
eventually inform aggregate learning, but they must not mutate authoritative
records, enqueue probes, publish raw private data, or become surveillance.
