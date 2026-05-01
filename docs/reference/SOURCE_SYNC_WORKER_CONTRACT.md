# Source Sync Worker Contract v0

Source Sync Worker Contract v0 defines future source sync worker job and manifest records. A source sync worker is not connector runtime yet. It is not a crawler/scraper, not public-query fanout, not source cache/evidence ledger mutation in v0, not candidate index mutation, and not master-index mutation.

## Job Shape

`contracts/source_sync/source_sync_worker_job.v0.json` records job identity, job kind taxonomy, source target, source policy, approval gates, scheduling, retry/timeout/rate-limit/circuit-breaker policy, User-Agent and source terms policy, input refs, expected outputs, safety requirements, privacy, rights/risk, limitations, and hard no-execution/no-mutation guarantees.

## Future Worker Manifest

`contracts/source_sync/source_sync_worker_manifest.v0.json` describes a future worker family, supported job kinds, allowed source families, defaults, required approvals, safety defaults, output policy, and no-runtime guarantees. Runtime is not implemented.

## Source Policy And Approval

Live source sync requires approval and source policy review. Future live jobs require source policy, rate limit, User-Agent, circuit breaker, cache policy, evidence output, rights/risk, and connector contract review before any source access.

## Scheduling And Limits

Scheduling is not created in P69. Future workers must define bounded schedules, retry backoff, timeouts, per-source rate limits, and circuit breakers before execution.

## Cache-First And Evidence Attribution

Expected outputs are future-only. Source sync workers must feed source cache and evidence ledger later, with validation and review, before any public use or candidate promotion. They must not mutate the master index directly.

## Relations

Probe queue and demand dashboard records may suggest future source sync work, but P69 does not enqueue jobs or wire public search to source fanout. Candidate index and promotion policy remain review-gated future consumers only.
