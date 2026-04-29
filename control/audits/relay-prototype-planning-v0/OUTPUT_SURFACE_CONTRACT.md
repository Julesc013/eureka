# Output Surface Contract

Allowed initial outputs for a future approved prototype:

- read-only HTTP pages
- plain text pages
- JSON static summaries
- file-tree index views
- checksum files
- snapshot manifest views

Outputs must preserve the same resolver/publication truth. They may change
presentation but must not rewrite evidence, status, limitations, source posture,
checksum meaning, or snapshot signature-placeholder limits.

Disallowed initial outputs:

- write endpoints
- upload endpoints
- admin endpoints
- install automation
- download automation
- package-manager handoff
- executable launch
- live probe endpoints
- live backend proxy routes
- arbitrary file serving
- private path display
- credential display
- telemetry endpoints
- account/session views

Any future HTTP implementation must reject write methods and must not provide a
generic file browser outside allowlisted static roots.
