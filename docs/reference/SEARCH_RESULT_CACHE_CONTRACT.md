# Search Result Cache Contract v0

Status: contract-only.

The v0 boundary is no runtime cache writes.

This contract defines future shared query/result cache entries. It has no
runtime cache writes. It also has no persistent cache storage, no telemetry runtime, no
public query logging, and no mutation of query observations, search miss ledger
entries, search needs, probe queues, candidate indexes, local indexes, or the master
index.

## Purpose

`contracts/query/search_result_cache_entry.v0.json` describes a safe summary of
a public search response that a future cache runtime may reuse. A cache entry is
not source evidence, not master-index truth, and not a replacement for result
cards. It is a bounded summary tied to a checked public index snapshot and
source-status posture.

## Cache Entry Model

Required sections:

- `query_ref`: normalized query reference, non-reversible query fingerprint,
  raw query retention default `none`, and privacy classification.
- `cache_key`: sha256 cache key over normalized query, profile, mode, include
  flags, and index snapshot. The key is non-reversible and includes no salt
  value in examples.
- `request_summary`: local_index_only mode, profile, limit, safe include flags,
  and forbidden-parameter posture.
- `response_summary`: ok/result-count/hit-state/confidence/warning/gap/
  limitation counts only.
- `result_summaries`: public-safe result-card summaries, not raw result
  payloads.
- `absence_summary`: scoped absence or gap summary.
- `checked_scope` and `index_refs`: checked controlled index and build
  references, with live probes and external calls false.
- `freshness` and `invalidation`: when a cache entry becomes stale.
- `privacy` and `retention_policy`: prohibited data checks and future retention
  policy only.
- `no_mutation_guarantees`: hard false fields for master index, local index,
  candidate index, query observation mutation, miss ledger mutation, search need
  mutation, probe enqueue, telemetry export, and external calls.

## Cache Key

The v0 cache key uses:

- `key_algorithm`: `sha256`
- `key_basis`: `normalized_query_plus_profile_plus_index_snapshot`
- `normalized_query_hash`: sha256 over the normalized query basis
- `profile`: requester profile such as `api_client`
- `mode`: `local_index_only`
- `include_flags`: safe expansions such as `evidence`, `limitations`, or `gaps`
- `index_snapshot_ref`: public index snapshot/build reference
- `reversible`: false
- `salt_policy`: `unsalted_public_aggregate` for deterministic examples, with
  salted deployment/local policies reserved for future runtime design

No secret salt is stored in examples or contracts.

## Cached Result Summary

Result summaries contain only public-safe fields:

- result reference and title
- source id/family
- result lane and user-cost summary
- evidence count
- compatibility summary
- allowed and blocked action summaries
- warning and limitation counts
- optional score

They must not include raw source payloads, private paths, executable bytes,
download/install promises, user identifiers, or credentials.

## Absence And Gaps

Cached absence is scoped absence, not proof outside the checked scope. An absence entry must state
what was checked, what was not checked, near-miss count, next actions, and
limitations. `scoped_absence` means only that the referenced public index
snapshot did not yield a verified result.

## Search Miss Ledger Relationship

P61 adds the search miss ledger contract as the next contract-only layer after
the shared result cache. Cache entries may summarize no-hit, weak-hit, and gap
outcomes; miss ledger entries explain why those outcomes were scoped misses and
what future-only work could follow. P60 still does not write miss ledger
entries, and P61 does not write cache entries.

## Search Need Record Relationship

P62 adds search need records as the next contract-only layer. Shared cache
entries may provide summary context for repeated scoped absence or weak-hit
patterns, but cache entries do not create needs, enqueue probes, mutate
candidates, or become master-index truth.

## Probe Queue Relationship

P63 adds probe queue items as the next contract-only future work-request layer.
Shared cache entries may be referenced as context for future probe planning, but
cache entries do not create queue items, execute probes, mutate source cache,
mutate evidence ledger, mutate candidates, or become master-index truth.

## Candidate Index Relationship

P64 adds the candidate index as the next contract-only provisional record
layer. Cache entries may provide scoped result or absence context for later
candidate review, but cache entries do not create candidates, promote
candidates, mutate source cache, mutate evidence ledger, inject candidates into
public search, or become master-index truth.

## Freshness And Invalidation

Future cache entries become stale when the public index is rebuilt, source
cache refreshes, contracts change, candidates are promoted, rights policy
changes, or safety policy changes. P60 examples use `ttl_policy:
none_for_example`; no retention runtime is implemented.

## Privacy And Retention

Raw query retention default is `none`. Public-safe cache entries must not
contain IP address, account ID, email, phone number, API key, auth token,
password, private key, private path, private URL, private local result
identifier, or user-uploaded filename without consent.

The public aggregate policy allows aggregate use only after privacy filtering.
Individual entries are not publishable by default.

## Runtime Boundary

P60 does not wire public search routes to a cache. The optional dry-run helper
prints a candidate cache entry to stdout only and writes no files.

Validate examples with:

```bash
python scripts/validate_search_result_cache_entry.py --all-examples
python scripts/validate_search_result_cache_entry.py --all-examples --json
```

Validate the whole contract pack with:

```bash
python scripts/validate_shared_query_result_cache_contract.py
python scripts/validate_shared_query_result_cache_contract.py --json
```
