`runtime/engine/decomposition/` holds the first bounded package-member inspection seam.

Current scope is intentionally narrow:

- accepts one resolved target plus one explicit `representation_id`
- reuses the bounded acquisition seam to retrieve deterministic local payload bytes
- supports ZIP member listing only in this bootstrap slice
- returns explicit `unsupported`, `unavailable`, or `blocked` outcomes for everything else

This is not a general extractor framework, installer, importer, or execution path. It proves only that Eureka can move from one fetched bounded representation to a compact member listing through the engine boundary.
