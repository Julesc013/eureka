# Extract Interface

`runtime/engine/interfaces/extract/` is the narrow extract-facing engine boundary that connectors may target.

Current bootstrap types and steps:

- `ExtractedSyntheticRecord`: bounded fixture sections extracted from a source record
- `extract_synthetic_source_record(...)`: minimal extraction step from source payload to extracted record
