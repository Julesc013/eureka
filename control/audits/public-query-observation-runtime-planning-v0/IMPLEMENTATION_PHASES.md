# Implementation Phases

Phase 0: keep disabled; add local dry-run observation builder tests only. Rollback: remove flag/test hook. Validation: no writes.
Phase 1: local development observation store behind env flag; no hosted use. Rollback: disable flag and discard local store. Validation: no raw query/IP/account fields.
Phase 2: hosted staging with private retention controls; no public aggregates. Rollback: disable writer and isolate store. Validation: rate limits, deletion, backup, access control.
Phase 3: production alpha with retention/deletion/backup/rate-limit evidence; still no raw query retention. Rollback: feature flag off and preserve deletion workflow.
Phase 4: aggregate query intelligence after poisoning/privacy guard. Rollback: disable aggregates and purge unsafe buckets.
