# Native Relay Snapshot Impact

Future native clients may use application-local private report roots. They must
not sync, upload, or expose private reports by default.

Relay must not expose private local reports, local paths, or staging manifests
by default.

Snapshots must not include local/private reports or private paths by default.
Any public-safe export needs validation, review, and redaction.
