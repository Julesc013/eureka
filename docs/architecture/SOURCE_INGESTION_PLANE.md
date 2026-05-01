# Source Ingestion Plane

Source Ingestion Plane v0 begins with P69 Source Sync Worker Contract v0. Source sync workers are future bounded jobs for approved sources. They are not connector runtime yet, not crawlers, not scrapers, not public-query fanout, not source cache or evidence ledger mutation in v0, and not master-index mutation.

Future live source sync requires approval, source policy review, rate limits, timeouts, circuit breakers, User-Agent policy, source terms review, cache-first handling, evidence attribution, and operator controls. P69 adds no worker queue, database, deployment, credentials, telemetry, live source calls, downloads, uploads, installs, or arbitrary URL fetching.

## P70 Source Cache And Evidence Ledger v0

P70 adds Source Cache Contract v0 and Evidence Ledger Contract v0 as contract-only storage models. They are not runtime, not public-query fanout, not arbitrary URL cache, not raw payload store, not private data store, and not source/evidence/candidate/public/local/master index mutation. Future approved source sync workers may write cache-first, evidence-attributed metadata only after approval, source policy, rate limits, timeouts, circuit breakers, and descriptive User-Agent policy.
