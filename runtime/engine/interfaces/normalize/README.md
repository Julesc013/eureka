# Normalize Interface

`runtime/engine/interfaces/normalize/` is the narrow normalize-facing engine boundary that connectors may target.

Current bootstrap types and steps:

- `NormalizedResolutionRecord`: engine-consumable normalized record for exact-match resolution
- `normalize_extracted_record(...)`: minimal normalization step from extracted record to normalized record

Trust semantics and canonical object meaning remain governed elsewhere under `contracts/`.
