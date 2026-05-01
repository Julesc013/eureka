# Query Intelligence Privacy

Status: P59/P60/P61/P62/P63/P64 contract-only operations guidance.

Query intelligence is not telemetry. P59 adds no persistent query logging, no
analytics, no IP storage, no account identifiers, no raw private-looking query
retention, no public observation feed, and no runtime hook from public search.
P60 adds no runtime cache writes and no persistent result cache.
P61 adds no runtime ledger writes and no persistent miss ledger.
P62 adds no runtime need store and no persistent search need storage.
P63 adds no runtime probe queue, no persistent probe queue, and no probe
execution.
P64 adds no runtime candidate index, no persistent candidate index, no public
search candidate injection, and no candidate promotion runtime.

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

`scripts/dry_run_probe_queue_item.py` emits a non-persistent probe queue item
to stdout only. It is useful for validating the probe queue contract shape, not
for collecting user data, writing queue state, running probes, or writing source
cache/evidence/candidate state.

`scripts/validate_probe_queue_item.py` validates committed probe queue examples
and rejects private paths, private URLs, credential markers, IP addresses,
account identifiers, probe execution, live source calls, source cache mutation,
evidence ledger mutation, candidate-index mutation, hard mutation flags, and
unsafe raw query retention.

`scripts/dry_run_candidate_index_record.py` emits a non-persistent candidate
index record to stdout only. It is useful for validating candidate contract
shape, not for collecting user data, writing candidate state, injecting public
search results, or accepting truth.

`scripts/validate_candidate_index_record.py` validates committed candidate
examples and rejects private paths, private URLs, credential markers, IP
addresses, account identifiers, accepted truth flags, promotion flags, live
source calls, live probe flags, source cache mutation, evidence ledger mutation,
hard mutation flags, and unsafe raw query retention.

## Operator-Gated Future Work

Hosted deployment, edge/rate-limit evidence, public aggregate publication,
retention/deletion controls, poisoning protection, and any query collection
runtime remain operator-gated or future-milestone work.

P59/P60/P61/P62/P63/P64 add no result cache runtime, no miss ledger runtime, no
search need runtime, no runtime probe queue, no runtime candidate index, no
candidate promotion runtime, no telemetry, no uploads, no accounts, no live
source calls, and no production public-query learning claims. Public aggregate
candidate summaries remain future work after privacy and poisoning review.

## P65 Candidate Promotion Privacy Boundary

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

Known Absence Page v0 is contract-only. It defines scoped absence, not global absence, for future no-result explanations with checked/not-checked scope, near misses, weak hits, gap explanations, safe next actions, privacy redaction, and no download/install/upload/live fetch. Known absence page is not a runtime page yet, not evidence acceptance, not candidate promotion, not master-index mutation, and not telemetry.

## P66 Known Absence Operations

Known absence page work is contract-only and not telemetry. It adds no persistent query logging, no hosted query intelligence runtime, no source calls, and no mutation. Future user-facing absence explanations must stay scoped and public-safe.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

The query privacy and poisoning guard is contract-only and not telemetry. It does not create persistent query logging, account tracking, IP tracking, analytics, WAF behavior, rate limiting, public search mutation, or query-intelligence mutation. It defines future decisions for redaction, rejection, quarantine, aggregate exclusion, and review before query learning.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## Demand Dashboard v0 Relation

Demand Dashboard v0 is future/contract-only. It can later summarize privacy-filtered and poisoning-guarded aggregate demand, but P68 adds no telemetry, public query logging, account/IP tracking, real demand claims, runtime dashboard, candidate promotion, source sync, source cache/evidence ledger mutation, public-search ranking change, or index mutation.
