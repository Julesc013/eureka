# Test Plan

Future implementation tests should prove:

- startup binds localhost only
- startup refuses `0.0.0.0` unless a later explicit policy and flag exist
- only allowlisted static roots are served
- path traversal is rejected
- arbitrary file paths are rejected
- directory escape is rejected
- write HTTP methods are rejected
- uploads are rejected
- admin routes do not exist
- live probe routes do not exist
- backend proxy routes do not exist
- private path leakage does not occur
- credentials are never displayed
- checksum files are served unchanged
- snapshot manifests are served unchanged
- logs are sanitized
- disable/rollback procedure is documented

This milestone does not implement runtime tests for a relay server because no
relay server exists. Current tests validate the planning pack only.
