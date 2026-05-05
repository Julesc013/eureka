# Privacy Path And Secret Policy

Deep extraction must reject:

- absolute paths
- path traversal
- private cache roots
- home/user paths
- credentials, secrets, API keys, and tokens
- private URLs unless a future local-private policy explicitly allows them
- IP/account/user identifiers in public examples
- raw private query data
- private uploaded filenames in public output

Only pack-internal or container-internal logical member paths may be published.
