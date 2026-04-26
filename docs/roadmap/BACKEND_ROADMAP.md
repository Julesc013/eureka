# Backend Roadmap

Eureka has completed most of its bounded architecture-proof phase. The next
program is operational backend development, still in the Python reference lane,
with public-alpha rehearsal evidence and Rust migration scaffolding now present
but not production-active.

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
- Public Alpha Safe Mode v0 as the first explicit constrained web/API hosting
  posture that separates trusted local-dev behavior from public-alpha route
  blocking
- Public Alpha Deployment Readiness Review as the first auditable route
  inventory, smoke-test, and operator-checklist gate for that posture
- Public Alpha Hosting Pack v0 as the first supervised rehearsal evidence
  packet for that posture
- Rust Migration Skeleton and Parity Plan v0 as the first governed Rust lane
  skeleton, with Python still authoritative
- Rust Parity Fixture Pack v0 as the first committed Python-oracle golden
  output pack for future Rust seam checks, with no Rust behavior port
- Rust Source Registry Parity Candidate v0 as the first isolated Rust behavior
  seam, compared against Python-oracle source-registry goldens and not wired
  into runtime behavior
- Search Usefulness Audit v0 as the first broad usefulness/backlog audit over
  64 archive-resolution-style queries, with external baselines left pending
  manual observation and no scraping or new retrieval semantics
- Comprehensive Test/Eval Operating Layer and Repo Audit v0 as the first
  structured verification lane registry, audit finding schema, dated audit
  pack, hard-test proposal set, and next-milestone backlog
- Hard Test Pack v0 as the first executable high-risk regression guard lane
  over eval truth, external baseline honesty, public-alpha path safety,
  route/docs/README drift, Python-oracle golden drift, Rust parity structure,
  source placeholder honesty, memory path privacy, and AIDE/test registry
  consistency
- Search Usefulness Backlog Triage v0 as the first governed usefulness backlog
  pack selecting old-platform-compatible software search, member-level
  discovery, and Source Coverage and Capability Model v0 as the next milestone
- Source Coverage and Capability Model v0 as the first bounded extension of
  Source Registry v0 from source inventory into explicit capability flags,
  coverage-depth metadata, connector modes, current limitations, and next
  coverage steps, projected through current public source-registry surfaces
  without adding connectors, live probing, crawling, scraping, or acquisition
  behavior
- Real Source Coverage Pack v0 as the first recorded source-coverage fixture
  pack for old-platform software and member-level discovery, adding separate
  `internet-archive-recorded-fixtures` and `local-bundle-fixtures` records
  without live Internet Archive API calls, scraping, crawling, broad source
  federation, or arbitrary local filesystem ingestion
- Old-Platform Software Planner Pack v0 as the first deterministic
  usefulness-wedge planner expansion, adding OS/platform aliases,
  platform-as-constraint handling, app-vs-OS-media suppression hints,
  latest-compatible release intent, driver/hardware/OS intent, vague identity
  uncertainty, documentation intent, and member-discovery hints without
  ranking, fuzzy/vector retrieval, LLM planning, live source behavior, or new
  connectors
- Member-Level Synthetic Records v0 as the first bounded member target-ref and
  parent-lineage seam for committed local bundle fixtures, making useful inner
  files visible to exact resolution, deterministic search, local index, and
  current public projections without broad extraction, arbitrary local
  filesystem ingestion, ranking, live source behavior, or new connectors

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
8. Public Alpha Safe Mode v0 (implemented)
9. Public Alpha Deployment Readiness Review (implemented)
10. Public Alpha Hosting Pack v0 (implemented)
11. Rust Migration Skeleton and Parity Plan (implemented as skeleton only)
12. Rust Parity Fixture Pack v0 (implemented as Python-oracle goldens only)
13. Rust Source Registry Parity Candidate v0 (implemented as isolated parity seam)
14. Search Usefulness Audit v0 (implemented as local audit/backlog generator)
15. Comprehensive Test/Eval Operating Layer and Repo Audit v0 (implemented as governance/audit layer)
16. Hard Test Pack v0 (implemented as high-risk regression guards)
17. Search Usefulness Backlog Triage v0 (implemented as governed backlog selection)
18. Source Coverage and Capability Model v0 (implemented as metadata/projection only)
19. Real Source Coverage Pack v0 (implemented as recorded fixtures only)
20. Old-Platform Software Planner Pack v0 (implemented as deterministic interpretation only)
21. Member-Level Synthetic Records v0 (implemented as bounded fixture-derived member records)
22. Result Lanes + User-Cost Ranking v0
23. Compatibility Evidence Pack v0
24. Search Usefulness Audit Delta v0
25. Rust Query Planner Parity Candidate v0
26. Public Alpha Rehearsal Evidence v0
27. Compatibility Surface Strategy v0
28. Native App Work Later

## Immediate Next Milestone

The next implementation milestone should be:

> Result Lanes + User-Cost Ranking v0

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
- Public Alpha Safe Mode v0 now blocks arbitrary local-path controls in
  public-alpha mode while preserving local-dev behavior
- Public Alpha Deployment Readiness Review now inventories route safety,
  validates policy alignment, and smoke-tests public-alpha behavior
- Public Alpha Hosting Pack v0 now packages route inventory status, smoke
  evidence templates, operator signoff, blockers, and a supervised rehearsal
  runbook without adding deployment infrastructure
- Rust Migration Skeleton and Parity Plan v0 now creates placeholder crates and
  parity documentation without porting behavior or replacing Python
- Rust Parity Fixture Pack v0 now captures Python oracle outputs as stable
  parity fixtures before any Rust seam ports begin
- Rust Source Registry Parity Candidate v0 now proves the first isolated Rust
  behavior seam against committed Python goldens without replacing Python
- Search Usefulness Audit v0 now shows a broad observed backlog dominated by
  source coverage, planner/query-interpretation, compatibility evidence,
  representation, decomposition, and member-access gaps
- Comprehensive Test/Eval Operating Layer and Repo Audit v0 now records hard
  test proposals and structured findings that should become executable
  guardrails before source, planner, or Rust parity work widens
- Hard Test Pack v0 now turns the first selected audit findings into
  executable guardrails without changing runtime behavior
- Search Usefulness Backlog Triage v0 now selects old-platform-compatible
  software search as the primary wedge and member-level discovery as the
  secondary wedge
- Source Coverage and Capability Model v0 now defines source capability depth
  and placeholder posture so recorded fixture coverage can improve usefulness
  without slipping into live crawling, ranking, fuzzy/vector retrieval, or
  source-coverage overreach
- Real Source Coverage Pack v0 has added the first recorded source coverage
  fixtures
- Old-Platform Software Planner Pack v0 has reduced planner/query
  interpretation gaps with deterministic hints while preserving hard eval
  honesty
- Member-Level Synthetic Records v0 has added member-level target refs,
  member-level index records, and parent lineage over the existing fixture
  corpus
- the next backend bottleneck is presentation and lane policy: promoting the
  smallest actionable member when evidence supports it while preserving parent
  bundles as lineage, without adding fuzzy ranking, vector search, LLM planning,
  live source behavior, or production relevance claims

## Explicit Deferrals

The backend roadmap intentionally defers:

- Visual Studio app work
- Xcode app work
- full native app work
- production Rust rewrite
- Rust behavior ports that do not match Python-oracle fixtures
- automated Google or Internet Archive scraping
- installer or download automation
- trust scoring
- production relevance benchmarking
- vector-heavy retrieval
- LLM-heavy planning
- broad live federation
- auth, HTTPS/TLS, accounts, and production deployment remain outside this slice
