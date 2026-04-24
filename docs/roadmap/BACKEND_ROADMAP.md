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
- Source Registry v0 as an explicit source inventory and public labeling plane

The current Python implementation should therefore be treated as the reference
backend and architectural oracle for the next phase.

## Next Sequence

The next backend sequence is:

1. Source Registry v0 (implemented)
2. Resolution Run Model v0
3. Query Planner v0
4. Local Index v0
5. Local Worker and Task Model v0
6. Resolution Memory v0
7. Eval Harness Upgrade
8. Public Hosted Alpha Preparation
9. Rust Migration Skeleton and Parity Plan
10. Native App Work Later

## Immediate Next Milestone

The next implementation milestone should be:

> Resolution Run Model v0

Why this comes next:

- Source Registry v0 is now present as the bounded source inventory plane
- the next operational step is to represent search as a resumable bounded run
- later planner, index, worker, and memory work need that run envelope more than another inventory slice

## Explicit Deferrals

The backend roadmap intentionally defers:

- Visual Studio app work
- Xcode app work
- full native app work
- production Rust rewrite
- installer or download automation
- trust scoring
- vector-heavy retrieval
- LLM-heavy planning
- broad live federation
