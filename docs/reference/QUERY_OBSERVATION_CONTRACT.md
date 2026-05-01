# Query Observation Contract v0

Status: contract-only.

This contract has no telemetry runtime and no runtime persistence.

`contracts/query/query_observation.v0.json` defines the first Query
Intelligence Plane record. It captures a privacy-filtered summary of a search
interaction for future learning, with no runtime persistence, no telemetry
runtime, no public query logging, and no mutation of search or master indexes.

## Required Sections

- `raw_query_policy`: raw query retention default is `none`; public-safe
  examples retain no raw query and mark raw text unsafe to publish by default.
- `normalized_query`: lower-risk normalized terms and safe public terms after
  redaction.
- `query_fingerprint`: query fingerprint over the normalized basis, marked
  non-reversible. Example fingerprints are deterministic and include no salt
  value.
- `query_intent`: coarse intent such as `find_software_version`, `find_driver`,
  `find_inside_container_member`, `check_compatibility`, or `unknown`.
- `destination`: intended user destination, with download/install/emulation
  intents explicitly represented as detected-but-disabled.
- `detected_entities`: public-safe entities such as platform, version,
  artifact type, package name, or source family.
- `result_summary`: summary-only result posture, not a result cache.
- `checked_scope` and `index_refs`: what controlled indexes or summaries were
  checked, with live probes and external calls false.
- `privacy`: publication and aggregate eligibility after filtering.
- `retention_policy`: future policy description only.
- `probe_policy`: probe enqueueing is false in P59.
- `no_mutation_guarantees`: hard false fields for master index, local index,
  candidate index, result cache, miss ledger, probe enqueue, telemetry export,
  and external calls.

## Current Example

`examples/query_observations/minimal_query_observation_v0/` contains a
synthetic `windows 7 apps` observation. It is not from a real user, retains no
raw query, and records only summary posture against the controlled public index.

Validate examples with:

```bash
python scripts/validate_query_observation.py --all-examples
python scripts/validate_query_observation.py --all-examples --json
```

Validate the whole contract pack with:

```bash
python scripts/validate_query_observation_contract.py
python scripts/validate_query_observation_contract.py --json
```

## Runtime Boundary

Public search routes do not write query observations in P59. The dry-run helper
prints a candidate observation to stdout only and writes no files.

## Relation To Shared Result Cache

P60 adds `contracts/query/search_result_cache_entry.v0.json` as the next
contract-only Query Intelligence Plane layer. Cache entries may reference query
observation fingerprints, but P60 still does not persist observations, write
cache entries, publish query logs, mutate miss ledgers, enqueue probes, mutate
candidate indexes, or mutate the master index.

## Relation To Search Miss Ledger

P61 adds `contracts/query/search_miss_ledger_entry.v0.json` as the contract-only
miss layer. Miss entries may reference query observation fingerprints and
optional cache refs, but P61 still does not persist observations, write miss
ledger entries at runtime, create search needs, enqueue probes, mutate result
caches, mutate candidate indexes, or mutate the master index.

## Relation To Search Need Records

P62 adds `contracts/query/search_need_record.v0.json` as the contract-only
unresolved-need layer. Query observations may later contribute privacy-filtered
input references to a search need record after miss/cache classification and
review, but P62 adds no runtime need store, telemetry, public query logging,
probe enqueueing, candidate mutation, or master-index mutation.

## Relation To Probe Queue

P63 adds `contracts/query/probe_queue_item.v0.json` as the contract-only future
work-request layer. Query observations may be referenced by later probe queue
items only after privacy filtering and review. P63 adds no runtime probe queue,
probe execution, source cache mutation, evidence ledger mutation,
candidate-index mutation, external calls, live probes, or master-index
mutation.

## Relation To Candidate Index

P64 adds `contracts/query/candidate_index_record.v0.json` as the contract-only
provisional candidate layer. Query observations may later be referenced as
privacy-filtered inputs to candidate records, but P64 adds no runtime candidate
index, no candidate promotion runtime, no public search candidate injection, no
source cache mutation, no evidence ledger mutation, and no master-index
mutation.

## P65 Candidate Promotion Policy Relationship

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

Known Absence Page v0 is contract-only. It defines scoped absence, not global absence, for future no-result explanations with checked/not-checked scope, near misses, weak hits, gap explanations, safe next actions, privacy redaction, and no download/install/upload/live fetch. Known absence page is not a runtime page yet, not evidence acceptance, not candidate promotion, not master-index mutation, and not telemetry.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

Query Privacy and Poisoning Guard v0 is future/contract-only. It should classify privacy risks, poisoning risks, redaction, public aggregate eligibility, and future query-intelligence eligibility before this record type is used for learning. P67 does not mutate this record type, add telemetry, track accounts or IPs, persist guard decisions, or alter public search runtime behavior.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## Demand Dashboard v0 Relation

Demand Dashboard v0 is future/contract-only. It can later summarize privacy-filtered and poisoning-guarded aggregate demand, but P68 adds no telemetry, public query logging, account/IP tracking, real demand claims, runtime dashboard, candidate promotion, source sync, source cache/evidence ledger mutation, public-search ranking change, or index mutation.
