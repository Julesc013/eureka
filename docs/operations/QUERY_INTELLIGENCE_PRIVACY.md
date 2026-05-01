# Query Intelligence Privacy

Status: P59/P60/P61/P62 contract-only operations guidance.

Query intelligence is not telemetry. P59 adds no persistent query logging, no
analytics, no IP storage, no account identifiers, no raw private-looking query
retention, no public observation feed, and no runtime hook from public search.
P60 adds no runtime cache writes and no persistent result cache.
P61 adds no runtime ledger writes and no persistent miss ledger.
P62 adds no runtime need store and no persistent search need storage.

## Operator Posture

- Treat all raw public query text as potentially private.
- Keep raw query retention disabled unless a future legal/privacy milestone
  explicitly changes the policy.
- Permit public aggregate summaries only after privacy filtering and poisoning
  review.
- Do not publish individual observations by default.
- Keep query learning separate from master-index truth.

## Current Local Tools

`scripts/dry_run_query_observation.py` emits a non-persistent example
observation to stdout only. It is useful for validating the contract shape, not
for collecting user data.

`scripts/validate_query_observation.py` validates committed examples and rejects
private paths, private URLs, credential markers, and hard mutation flags.

`scripts/dry_run_search_result_cache_entry.py` emits a non-persistent shared
query/result cache entry to stdout only. It is useful for validating the cache
contract shape, not for collecting user data or writing cache state.

`scripts/validate_search_result_cache_entry.py` validates committed cache
examples and rejects private paths, private URLs, credential markers, IP
addresses, account identifiers, hard mutation flags, and global absence claims.

`scripts/dry_run_search_miss_ledger_entry.py` emits a non-persistent search
miss ledger entry to stdout only. It is useful for validating scoped miss
contract shape, not for collecting user data or writing ledger state.

`scripts/validate_search_miss_ledger_entry.py` validates committed miss ledger
examples and rejects private paths, private URLs, credential markers, IP
addresses, account identifiers, broad absence claims, search need creation,
probe enqueueing, result cache mutation, hard mutation flags, and public unsafe
raw query retention.

`scripts/dry_run_search_need_record.py` emits a non-persistent search need
record to stdout only. It is useful for validating unresolved-need contract
shape, not for collecting demand data or writing need state.

`scripts/validate_search_need_record.py` validates committed search need
examples and rejects private paths, private URLs, credential markers, IP
addresses, account identifiers, broad absence claims, demand-count claims,
probe enqueueing, candidate-index mutation, hard mutation flags, and unsafe raw
query retention.

## Operator-Gated Future Work

Hosted deployment, edge/rate-limit evidence, public aggregate publication,
retention/deletion controls, poisoning protection, and any query collection
runtime remain operator-gated or future-milestone work.

P59/P60/P61/P62 do not add probes, result cache runtime, miss ledger runtime,
search need runtime, candidate indexes, telemetry, uploads, accounts, live
source calls, or production public-query learning claims.
