# F0 Resource And Security Model

F0 uses conservative limits because the foundation is fixture-only and manifest-only. The starting limits are 1 MiB fixture files, 100 members, 10 MiB declared and uncompressed totals, depth 1, filename length 240, a 10 second timeout posture, and a 64 MiB memory budget.

These limits are not truth about future production extraction. They are a reviewable safety envelope for committed fixtures. F0 performs no downloads, no filesystem extraction, no execution, no arbitrary file extraction, and no model/provider calls.

Security checks include:

- path traversal detection
- absolute path detection
- resource-limit blocking
- nested archive deferral
- symlink and device materialization blocking
- unknown container blocking

Member records remain review-gated observations. The resource model never promotes member paths to evidence or reviewed records.
