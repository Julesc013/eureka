# Page Local Dry-Run Runtime

`runtime/pages` contains the P103 local dry-run page runtime for approved repo
examples only.

It can load object, source, comparison, and P103 dry-run page example JSON
records, classify them conservatively, and render deterministic text, HTML, and
JSON previews for audit output.

It does not add public routes, API routes, hosted routes, public-search links,
database storage, source-cache reads, evidence-ledger reads, live source calls,
connector execution, candidate promotion, downloads, uploads, installs,
execution, telemetry, accounts, or index mutation.
