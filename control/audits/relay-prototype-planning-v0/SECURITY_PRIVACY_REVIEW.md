# Security Privacy Review

Security/privacy defaults for a future first prototype:

- localhost-only default
- no LAN bind without explicit future approval
- no public internet exposure
- read-only
- no private data
- no credentials
- no write routes
- no admin routes
- no live probes
- no live backend proxy
- no arbitrary file roots
- no telemetry

Logs should be minimal. They should avoid absolute paths, private paths,
queries containing secrets, credentials, account/session identifiers, and
private user history. A future implementation should log enough to diagnose
startup and rejected unsafe requests without creating a privacy record.

Old clients are insecure and untrusted. They must receive public/read-only data
only. Checksums help detect drift, but checksums delivered through the same
untrusted channel are not a full authenticity proof. v0 signatures remain
placeholder documentation until a future signing/key policy exists.

A future threat model is required before implementation. It must cover bind
addresses, path traversal, allowlisted roots, log content, snapshot validation,
disable/rollback behavior, and live-backend/live-probe capability gates.
