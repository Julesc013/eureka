# Engine Interfaces

`runtime/engine/interfaces/` contains the concrete path-based dependency boundaries that other runtime components may consume.

These directories are intentionally lightweight during bootstrap. They exist so dependency policy can point at real repo paths instead of prose.

Current boundary shapes:

- `ingest/` carries connector-supplied source records
- `extract/` carries bounded extracted records from source payloads
- `normalize/` carries engine-consumable normalized records for exact-match resolution
