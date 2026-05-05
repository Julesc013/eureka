# Privacy Path Traversal And Secret Policy

- reject absolute paths
- reject path traversal
- reject private cache roots
- reject home/user paths
- reject credentials/secrets/API keys/tokens
- reject private URLs unless redaction policy explicitly allows local-private future
- reject IP/account/user identifiers in public examples
- normalize paths as pack-internal logical paths only
- no local filesystem scanning beyond approved pack root
