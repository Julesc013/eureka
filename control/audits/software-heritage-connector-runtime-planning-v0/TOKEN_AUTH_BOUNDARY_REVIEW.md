# Token/Auth Boundary Review

P92 keeps v0 token-free and unauthenticated.

- Software Heritage tokens are not configured.
- Credentials are not configured.
- Token use requires a future explicit policy and operator approval.
- Missing or incomplete token policy does not block a token-free future v0 plan, but it does block any authenticated runtime.
- Public query parameters must never select a token, auth mode, repository, origin, SWHID, content hash, revision id, directory id, snapshot id, release id, source archive URL, local path, or filesystem root.
