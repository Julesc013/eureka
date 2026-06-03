# Decisions, Open Questions, and Next Steps — Eureka Search Engine: Corpus Growth, Public UX, and Resilient Search Planning

## Decisions

### Defer public launch

Status: final for the current chat, revisitable later.

Who accepted it: the user explicitly corrected the launch trajectory and repeatedly accepted subsequent reassessments that kept launch deferred.

Rationale: routes, UX, candidates, and launch dry-runs did not equal a useful public search engine. Reviewed corpus depth was too low.

Consequences: launch tasks were replaced by active discovery, review-batch apply, snapshot refresh, and reassessment loops.

Revisit conditions: larger reviewed corpus, reviewed artifact records, full discovery, main promotion, publication rehearsal, and manual approval.

### Use review/apply/snapshot/reassess as the corpus-growth heartbeat

Status: accepted plan.

Who accepted it: the user recommended it; the assistant agreed.

Rationale: candidate volume without reviewed records does not create product truth.

Consequences: `REVIEW-BATCH-APPLY-NEXT-00` and `SNAPSHOT-REFRESH-06` became the executed next work.

Revisit conditions: if review throughput fails or a better corpus-growth mechanism is demonstrated.

### Keep long full discovery outside the AI loop

Status: settled operational policy in the chat.

Who accepted it: user and assistant aligned; later tasks implemented harness/policy support.

Rationale: AI polling long test runs wastes tokens and money.

Consequences: future AI tasks should run focused tests only and rely on external summaries for full discovery.

Revisit conditions: only if test runtime becomes short enough or tool execution changes substantially.

### Treat live metadata as evidence, not truth

Status: settled.

Who accepted it: enforced across many task statuses and prompts.

Rationale: metadata can support candidates and limited records but cannot prove downloads, safety, rights, completeness, or compatibility.

Consequences: all live metadata outputs remained review-only or limited reviewed metadata/source-lead records.

Revisit conditions: future artifact-verification gates may allow stronger claims with additional evidence.

### Implement public search UX MVP but not launch

Status: completed work plus deferred launch decision.

Rationale: users need legible status distinctions and no-JS search, but UX does not create corpus depth.

Consequences: public UX MVP exists and is projected through snapshots; launch remains blocked.

Revisit conditions: after reviewed corpus growth, external validation, and launch approval.

## Open Questions

### How many reviewed records are enough?

Known: the chat repeatedly uses 25 as a reviewed-record threshold.

Unknown: whether 25 is actually sufficient for public usefulness.

Resolution path: search usefulness eval and public-alpha reassessments.

Priority: high.

### How should indexless live fallback be implemented?

Known: the design should use connector capabilities, coverage reports, live metadata candidate lanes, and no truth mutation.

Unknown: exact public policy, request budgets, allowed sources, and UX behavior.

Resolution path: implement `INDEXLESS-LIVE-SEARCH-FALLBACK-00`.

Priority: high.

### What qualifies as a reviewed artifact record?

Known: current limited records are not verified artifacts.

Unknown: exact sufficiency standards for artifact identity, version, source, representation, and access posture.

Resolution path: `REVIEWED-ARTIFACT-RECORD-GATE-00`.

Priority: high.

### How useful is Eureka against hard real queries?

Known: candidate counts and limited reviewed counts exist.

Unknown: whether users get useful outcomes for difficult searches.

Resolution path: `SEARCH-USEFULNESS-EVAL-00` with 30–50 hard queries.

Priority: high.

### When should dev be promoted to main?

Known: not after the final visible stack; external full discovery is needed first.

Unknown: exact promotion timing.

Resolution path: external full discovery and promotion review.

Priority: medium-high.

## Next Steps

### 1. PUBLIC-ALPHA-REASSESS-06

Priority: immediate.

Dependencies: `SNAPSHOT-REFRESH-06` completed.

Expected output: updated product decision after reviewed projection count increased to 12.

First action: verify latest branch state and prior result files.

### 2. INDEXLESS-LIVE-SEARCH-FALLBACK-00

Priority: high.

Dependencies: query planner, connector capabilities, public UX, source-action kernel.

Expected output: graceful degraded search when indexes/snapshots/caches are unavailable.

First action: define IndexAvailabilityPacket and live fallback coverage report.

### 3. SEARCH-USEFULNESS-EVAL-00

Priority: high.

Dependencies: current search stack and hard query selection.

Expected output: measurable product KPI beyond candidate count.

First action: draft 30–50 query eval set.

### 4. REVIEWED-ARTIFACT-RECORD-GATE-00

Priority: high but after current reassess/fallback planning.

Dependencies: review/apply patterns and evidence sufficiency rules.

Expected output: governed lane for reviewed artifact records without safety/rights overclaiming.

First action: define artifact record evidence requirements.

### 5. External full discovery and promotion review

Priority: required before launch or major promotion.

Dependencies: current dev stack stabilized.

Expected output: externally run full-discovery summary and dev-to-main promotion review.

First action: run harness outside AI.

## Rejected or Deferred Options

### Public alpha launch now

Why not carried forward: too few reviewed records and unresolved reliability/eval/gate work.

Can return later: yes, after launch gates.

### Public live source fanout now

Why not carried forward: no indexless fallback policy gate and live search should be candidate-only.

Can return later: yes, after fallback and capability policies.

### More seed domains immediately

Why not carried forward: review throughput became the bottleneck.

Can return later: yes, if review/apply loop needs more domain input.

### Full discovery inside AI

Why not carried forward: token/time waste.

Can return later: only if runtime becomes short or explicitly required.
