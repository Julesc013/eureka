# Backend Roadmap

Eureka has completed most of its bounded architecture-proof phase. The next
program is operational backend development, still in the Python reference lane,
before public alpha or Rust migration work begins.

## Current Status

The repo has already proven:

- multiple bounded runtime seams
- multiple surfaces over one public boundary
- deterministic search and exact resolution
- evidence visibility, miss explanation, and action-routing seams
- decomposition and member-readback seams
- a first archive-resolution eval packet
- Archive Resolution Eval Runner v0 as the first executable regression harness
  over that hard-query packet
- Source Registry v0 as an explicit source inventory and public labeling plane
- Query Planner v0 as the first deterministic raw-query compiler into structured
  `ResolutionTask` records plus planned-search run summaries
- Local Index v0 as the first durable local search substrate over the current
  bounded corpus, with SQLite plus FTS5 preferred and deterministic fallback
  behavior when FTS5 is unavailable
- Local Worker and Task Model v0 as the first synchronous local execution
  substrate for source-registry validation, local-index build/query, and
  archive-resolution eval validation
- Resolution Memory v0 as the first explicit local reusable investigation
  memory layer derived from persisted completed runs

The current Python implementation should therefore be treated as the reference
backend and architectural oracle for the next phase.

## Next Sequence

The next backend sequence is:

1. Source Registry v0 (implemented)
2. Resolution Run Model v0 (implemented)
3. Query Planner v0 (implemented)
4. Local Index v0 (implemented)
5. Local Worker and Task Model v0 (implemented)
6. Resolution Memory v0 (implemented)
7. Archive Resolution Eval Runner v0 (implemented)
8. Public Hosted Alpha Preparation
9. Rust Migration Skeleton and Parity Plan
10. Native App Work Later

## Immediate Next Milestone

The next implementation milestone should be:

> Public Hosted Alpha Preparation

Why this comes next:

- Source Registry v0 is now present as the bounded source inventory plane
- Resolution Run Model v0 now provides a synchronous durable investigation
  envelope
- Query Planner v0 now provides deterministic structured intent for current
  archive-resolution families
- Local Index v0 now provides the first durable local search substrate
- Local Worker and Task Model v0 now provides the first bounded synchronous
  execution substrate for repeatable backend jobs
- Resolution Memory v0 now provides the first bounded reusable solved-work layer
- Archive Resolution Eval Runner v0 now provides the first executable regression
  harness over the hard-query packet, including explicit capability gaps
- the next backend bottleneck is public-alpha-safe configuration and route
  hardening, not broader retrieval semantics

## Explicit Deferrals

The backend roadmap intentionally defers:

- Visual Studio app work
- Xcode app work
- full native app work
- production Rust rewrite
- installer or download automation
- trust scoring
- production relevance benchmarking
- vector-heavy retrieval
- LLM-heavy planning
- broad live federation
