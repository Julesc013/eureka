# Query Observation Schema

The schema file is `contracts/query/query_observation.v0.json`.

Required top-level sections:

- `raw_query_policy`
- `normalized_query`
- `query_fingerprint`
- `query_intent`
- `destination`
- `detected_entities`
- `filters`
- `result_summary`
- `checked_scope`
- `index_refs`
- `privacy`
- `retention_policy`
- `probe_policy`
- `no_mutation_guarantees`

The schema marks runtime persistence, telemetry, and public query logging as
not implemented.
