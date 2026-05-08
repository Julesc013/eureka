# Candidate Store Model

The Candidate Store follows the node policy evaluator because policy evaluation
decides whether a WorkUnit or node posture can produce reviewable proposals.
The candidate store records those proposals as provisional objects without
turning them into truth.

## Model

A candidate record contains:

- status, type, origin, label, and canonical key
- proposed object/source/evidence/representation/compatibility/state summaries
- related query observation, search miss, SearchNeed, WorkUnit, WorkUnitResult,
  node policy evaluation, observation candidate, source lead, evidence, pack,
  and review references
- confidence or uncertainty
- conflict and deduplication summaries
- review gates
- truth and product boundaries

A candidate store snapshot contains explicit records, counts by status/type and
origin, a non-mutating deduplication report, warnings, review counts, and the
same truth/product boundaries.

## Deduplication

Deduplication is exact-key and report-only. It can identify
`duplicate_possible` records but must not merge records, delete records, mutate
canonical data, or promote a winner automatically.

## Relationship To Other Track B Work

SearchNeeds and search miss ledgers suggest unresolved demand. WorkUnit dry-run
results and node policy evaluations suggest reviewable work or blockers.
Candidate records can preserve those signals for later source cache and
evidence ledger planning while keeping every candidate provisional.

## Product Boundary

The runtime does not call networks, APIs, browsers, models, providers, or live
sources. It does not change public search behavior, create local private roots,
enable source sync, create accounts, emit telemetry, upload or download files,
or mutate the master index.

