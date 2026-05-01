# Cache Key And Fingerprint Model

The v0 cache key is a non-reversible sha256 value over normalized query,
profile, mode, include flags, and index snapshot.

Examples use:

- `key_algorithm`: `sha256`
- `key_basis`: `normalized_query_plus_profile_plus_index_snapshot`
- `mode`: `local_index_only`
- `salt_policy`: `unsalted_public_aggregate`
- `reversible`: false

No secret salt is stored. Future hosted deployments may choose a secret-salted
policy, but P60 does not implement that runtime.
