# Privacy, Path, And Secret Policy

The dry-run rejects or flags:

- absolute private paths
- path traversal
- home/user paths
- private cache roots
- credentials, secrets, API keys, tokens, and private keys
- private URLs unless a later local-private policy exists
- IP/account/user identifiers in public examples
- arbitrary local filesystem scanning beyond approved example roots

Committed examples use pack-internal logical paths and synthetic labels only.
