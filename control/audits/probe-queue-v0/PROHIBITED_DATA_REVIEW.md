# Prohibited Data Review

P63 probe queue examples exclude:

- raw private queries
- private paths and private URLs
- IP addresses and account IDs
- sensitive tokens
- executable payloads or binaries
- raw copyrighted payload dumps
- private local result identifiers

The validator rejects committed examples that contain common private path,
private URL, user identifier, IP, or sensitive-token patterns.
