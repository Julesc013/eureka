# Source Cache Local Dry-Run Runtime v0

P98 implements a bounded local dry-run source-cache runtime. It reads
repo-local synthetic examples, validates candidate shape, classifies candidate
effects, and emits deterministic reports.

It is not authoritative source-cache storage. It performs no live source calls,
connector execution, source-sync worker execution, evidence-ledger mutation,
candidate index mutation, public/local/master index mutation, public-search
integration, hosted runtime, telemetry, credentials, downloads, installs, or
execution.
