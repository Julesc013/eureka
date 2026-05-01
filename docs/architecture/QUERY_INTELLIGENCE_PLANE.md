# Query Intelligence Plane

Status: contract-only through P67.

The Query Intelligence Plane is the future layer that lets Eureka learn from
public search demand without turning public queries into surveillance or
authoritative truth. Its first contracts are the P59 query observation record,
the P60 shared query/result cache entry, the P61 search miss ledger entry, the
P62 search need record, the P63 probe queue item, the P64 candidate index
record, the P65 candidate promotion policy, the P66 known absence page, and the
P67 query privacy and poisoning guard decision.

The core doctrine is fast learning, slow truth:

- Public queries may eventually produce privacy-filtered aggregate learning.
- Query observation is not telemetry runtime.
- Query observation is not persistent query logging.
- Query observation is not a result cache, miss ledger, probe queue, candidate
  index, or master-index mutation.
- Shared query/result cache is not telemetry, not source evidence, not
  master-index truth, and not proof outside the checked scope.
- Shared query/result cache is not master-index truth.
- Search miss ledger entries are scoped learning records, not search needs,
  probe jobs, candidate records, or master-index truth.
- Search need records are durable future unresolved-need records, not search
  results, miss ledger entries, probe jobs, candidate records, demand dashboard
  rows, or master-index truth.
- Probe queue items are future work requests, not probe execution, not source
  cache or evidence ledger mutation, not candidate records, and not
  master-index truth.
- Candidate index records are provisional, reviewable records. They are not
  evidence acceptance, not public search authority, not source cache or
  evidence ledger mutation, and not master-index truth.
- Public query learning cannot become object truth without later evidence and
  validation gates.

## P59 Boundary

P59 defines `contracts/query/query_observation.v0.json`, a synthetic example,
validators, docs, and an optional dry-run helper that writes nothing. It does
not wire the public search runtime to write observations.

Hard guarantees for P59:

- no runtime persistence
- no telemetry
- no public query logging
- no raw private-looking query publication
- no probe queue
- no shared result cache mutation
- no miss ledger mutation
- no candidate index mutation
- no local index mutation
- no master-index mutation
- no external calls or live probes

## P60 Boundary

P60 defines `contracts/query/search_result_cache_entry.v0.json` and
`contracts/query/cache_key.v0.json`, synthetic examples, validators, docs, and
an optional dry-run helper that writes nothing. It does not wire public search
runtime to read or write cache entries.

Hard guarantees for P60:

- no runtime cache writes
- no persistent cache storage
- no telemetry
- no public query logging
- no raw private-looking query retention
- no miss ledger mutation
- no search need mutation
- no probe queue
- no candidate index mutation
- no local index mutation
- no master-index mutation
- no external calls or live probes

Cached result summaries are scoped to checked public index snapshots. Cached
absence is scoped absence, not proof outside the checked scope.

## P61 Boundary

P61 defines `contracts/query/search_miss_ledger_entry.v0.json` and
`contracts/query/search_miss_classification.v0.json`, synthetic no-hit and
weak-hit examples, validators, docs, and an optional dry-run helper that writes
nothing. It does not wire the public search runtime to write miss ledger
entries.

Hard guarantees for P61:

- no runtime ledger writes
- no persistent ledger storage
- no telemetry
- no public query logging
- no raw private-looking query retention
- no search need creation
- no probe enqueueing
- no result cache mutation
- no candidate index mutation
- no local index mutation
- no master-index mutation
- no external calls or live probes

Miss ledger entries record scoped absence, weak hits, near misses, blocked
queries, or incomplete searches against checked indexes, source families, and
capabilities. They are contract-only and not master-index truth.

## P62 Boundary

P62 defines `contracts/query/search_need_record.v0.json` and
`contracts/query/search_need_lifecycle.v0.json`, synthetic unresolved software
and compatibility-evidence examples, validators, docs, and an optional dry-run
helper that writes nothing. It does not wire the public search runtime to create
or persist search need records.

Hard guarantees for P62:

- no runtime need store
- no persistent need storage
- no telemetry
- no public query logging
- no demand-count runtime
- no raw private-looking query retention
- no probe enqueueing
- no candidate index mutation
- no result cache mutation
- no miss ledger mutation
- no local index mutation
- no master-index mutation
- no external calls or live probes

Search need records aggregate future privacy-filtered inputs into scoped,
reviewable unresolved needs. They may later guide reviewed packs, manual
observation, approved probes, candidate review, or promotion policy, but P62
does none of that runtime work.

## P63 Boundary

P63 defines `contracts/query/probe_queue_item.v0.json` and
`contracts/query/probe_kind.v0.json`, synthetic manual-observation,
source-metadata, and deep-extraction examples, validators, docs, and an optional
dry-run helper that writes nothing. It does not wire the public search runtime
to create queue records, execute probes, or mutate any source/evidence/candidate
store.

Hard guarantees for P63:

- no runtime probe queue
- no persistent probe queue
- no telemetry
- no public query logging
- no raw private-looking query retention
- no probe execution
- no live source call
- no source cache mutation
- no evidence ledger mutation
- no candidate index mutation
- no search need mutation
- no result cache mutation
- no miss ledger mutation
- no local index mutation
- no master-index mutation
- no external calls or live probes

Probe queue records may later guide approved source-cache, manual observation,
deep extraction, evidence review, or candidate review work. P63 only defines the
bounded contract and approval posture.

## P64 Boundary

P64 defines `contracts/query/candidate_index_record.v0.json` and
`contracts/query/candidate_lifecycle.v0.json`, synthetic object, evidence,
absence, and conflict examples, validators, docs, and an optional dry-run
helper that writes nothing. It does not wire the public search runtime to
create candidates, rank from candidates, promote candidates, or mutate any
source/evidence/master store.

Hard guarantees for P64:

- no runtime candidate index
- no persistent candidate index
- no telemetry
- no public query logging
- no public search candidate injection
- no candidate promotion runtime
- no source cache mutation
- no evidence ledger mutation
- no probe queue mutation
- no search need mutation
- no result cache mutation
- no miss ledger mutation
- no local index mutation
- no master-index mutation
- no external calls or live probes

Candidate records are contract-only, confidence-not-truth, conflict-preserving,
and review-gated. They may later support candidate promotion policy, known
absence pages, privacy/poisoning guardrails, demand dashboards, and
source/evidence ledger contracts.

## Future Path

Future milestones may define candidate promotion policy, known absence pages,
query privacy and poisoning guard, demand dashboard, source sync workers, and
source cache/evidence ledger contracts. Each must preserve the separation
between observed demand, reusable summaries, future work requests, provisional
candidates, and accepted truth.

## P65 Candidate Promotion Policy v0

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

Known Absence Page v0 is contract-only. It defines scoped absence, not global absence, for future no-result explanations with checked/not-checked scope, near misses, weak hits, gap explanations, safe next actions, privacy redaction, and no download/install/upload/live fetch. Known absence page is not a runtime page yet, not evidence acceptance, not candidate promotion, not master-index mutation, and not telemetry.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

P67 Query Privacy and Poisoning Guard v0 adds privacy before learning and poisoning defense before aggregation. It is contract-only: no runtime guard, no telemetry, no account tracking, no IP tracking, no public query logging, no query-intelligence mutation, no public/local/master index mutation, no external calls, and no live probes.

The guard classifies privacy risks, poisoning risks, policy actions, redaction, aggregate eligibility, and future object eligibility for query observations, shared result cache entries, miss ledgers, search needs, probe queue items, candidate records, promotion assessments, and known absence pages.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## Demand Dashboard v0

Demand Dashboard v0 completes the first Query Intelligence Plane contract sequence with a future aggregate visibility layer for privacy-filtered aggregate demand. It is contract-only: no telemetry, account/IP tracking, persistent aggregation, public search mutation, query-intelligence mutation, source sync, candidate promotion, or index mutation is implemented.

## Source Sync Worker v0 Relation

Source Sync Worker Contract v0 is future/contract-only. It may later consume probe queue and demand dashboard signals to plan approved, bounded source sync jobs, but P69 adds no connector runtime, source calls, public-query fanout, source cache mutation, evidence ledger mutation, candidate mutation, or index mutation.

## P70 Source Cache And Evidence Ledger Relation

Source Cache Contract v0 and Evidence Ledger Contract v0 are future source-ingestion outputs that query intelligence may reference indirectly through probe queue and demand dashboard priorities. They remain contract-only and add no public query logging, telemetry, source calls, cache writes, ledger writes, or index mutation.
