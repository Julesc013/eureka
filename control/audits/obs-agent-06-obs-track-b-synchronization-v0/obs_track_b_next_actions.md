# OBS to Track B Next Actions

## Next OBS Side-Lane Task

- `OBS-AGENT-07 - Human review packet for OBS candidates`

Prepare a compact human review packet over the existing OBS candidate queue, source policy items, SearchNeed seeds, and WorkUnit seeds. Keep every item review-gated and non-runtime.

## Next Track B Main-Lane Task

- `TRACK-B-07 - Query observation runtime`

Track B should continue to define runtime structure and review gates. OBS should not mutate Track B contracts or runtime files.

## Synchronization Point

- Re-run the sync audit after Track B has explicit runtime acceptance paths for SearchNeed and WorkUnit records.
- Re-run the sync audit after source policy decisions exist for metadata access families.
- Re-run the sync audit after Track B defines candidate store, review queue, source cache, and evidence ledger runtime behavior.

## Human Review Actions

- Review high-priority source family items before planning source access.
- Review SearchNeed seeds for duplicate or ambiguous needs.
- Review WorkUnit seeds for bounded scope, allowed actions, forbidden actions, idempotency, and recovery policy.
- Keep policy-blocked items blocked until source policy approval exists.

## Explicit Non-Actions

- Do not create runtime SearchNeeds.
- Do not create or execute runtime WorkUnits.
- Do not approve source access.
- Do not mark pending observations as observed.
- Do not create accepted evidence truth.
- Do not mutate the master index.
