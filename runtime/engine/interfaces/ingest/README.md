# Ingest Interface

`runtime/engine/interfaces/ingest/` is the narrow ingest-facing engine boundary that connectors may target.

Current bootstrap type:

- `SyntheticSourceRecord`: bounded connector-supplied source payload plus source metadata

Connectors may adapt into this path, but they must not define canonical object semantics here.
