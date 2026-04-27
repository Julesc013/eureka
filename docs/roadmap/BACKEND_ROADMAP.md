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
- Result Lanes + User-Cost Ranking v0 as the first bounded deterministic
  usefulness-annotation seam, assigning result lanes and user-cost reasons to
  current result records so smaller member records can be explained ahead of
  parent bundles without fuzzy/vector retrieval, LLM scoring, live source
  behavior, production ranking, or new connectors
- Compatibility Evidence Pack v0 as the first bounded source-backed
  compatibility evidence seam, deriving evidence records from committed
  fixture metadata, member paths, README text, and compatibility notes while
  preserving unknown compatibility without installer execution, live source
  behavior, scraping, fuzzy/vector retrieval, LLM behavior, or new connectors
- Search Usefulness Audit Delta v0 as the first stable usefulness-delta pack,
  recording current Search Usefulness Audit counts, historical reported
  baseline limitations, wedge-specific movement, and the next source-coverage
  recommendation without changing retrieval behavior or recording external
  baseline observations
- Old-Platform Source Coverage Expansion v0 as the first follow-up recorded
  fixture expansion for the selected wedge, adding tiny committed
  Internet-Archive-shaped and local bundle fixture data for Windows 7/XP/2000/98
  utility, browser-note, registry-repair, and driver/support-media cases without
  live source calls, scraping, crawling, arbitrary local filesystem ingestion,
  real binaries, or production source claims
- Search Usefulness Audit Delta v1 as the second measured audit/reporting pack
  after source expansion
- Hard Eval Satisfaction Pack v0 as the first source-backed hard-eval
  satisfaction mapping/report pack
- Old-Platform Result Refinement Pack v0 as the first strict result-shape,
  expected-lane, and bad-result evaluation pass over current old-platform hard
  eval partials, moving archive evals to `capability_gap=1`, `partial=4`, and
  `satisfied=1` without adding retrieval behavior or weakening hard tasks
- More Source Coverage Expansion v1 as the targeted recorded-fixture follow-up
  for the remaining old-platform hard partials, moving archive evals to
  `capability_gap=1` and `satisfied=5` without live source behavior, scraping,
  arbitrary local ingestion, real binaries, or external baseline claims
- Article/Scan Fixture Pack v0 as the first bounded article/page/scan fixture
  source, moving archive evals to `satisfied=6` with tiny synthetic OCR-like
  text and page-range evidence while adding no live source behavior, scraping,
  OCR engine, PDF/image parser, real scan, copyrighted article text, or
  external baseline claim
- Manual External Baseline Observation Pack v0 as the first manual-only
  external comparison protocol, defining Google web search, Internet Archive
  metadata search, and Internet Archive full-text/OCR search observation
  records plus 192 pending slots without scraping, automated external queries,
  API calls, or fabricated baselines
- Manual Observation Batch 0 as the first prioritized pending manual
  observation batch, selecting 13 high-value query IDs and 39 query/system
  slots across the three manual-only baselines without performing observations
  or creating external baseline evidence
- Manual Observation Entry Helper v0 as the stdlib-only local helper layer for
  listing pending slots, creating fillable pending files, validating one file
  or all files, and reporting Batch 0 progress without fetching URLs, opening
  browsers, scraping, automating external searches, or fabricating observations
- LIVE_ALPHA_00 Static Public Site Pack as the first no-JS static public-site
  source tree under `public_site/`, with identity, status, source matrix,
  eval/audit state, demo queries, limitations, roadmap, and local quickstart
  pages for later hosting review without deployment, backend hosting, live
  probes, scraping, automated external searches, or production-readiness claims
- Public Alpha Rehearsal Evidence v0 as the first supervised local/static
  rehearsal evidence pack, collecting static-site validation, public-alpha
  smoke, route inventory, eval/audit, external-baseline pending status,
  blockers, next deployment requirements, and unsigned signoff preparation
  without deployment, production approval, live probes, or observed external
  baselines

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
22. Result Lanes + User-Cost Ranking v0 (implemented as bounded annotations)
23. Compatibility Evidence Pack v0 (implemented as source-backed evidence annotations)
24. Search Usefulness Audit Delta v0 (implemented as audit/reporting)
25. Old-Platform Source Coverage Expansion v0 (implemented as recorded fixtures only)
26. Search Usefulness Audit Delta v1 (implemented as audit/reporting)
27. Hard Eval Satisfaction Pack v0 (implemented as eval evidence mapping/reporting)
28. Old-Platform Result Refinement Pack v0 (implemented as strict result-shape eval refinement)
29. More Source Coverage Expansion v1 (implemented as targeted recorded fixtures)
30. Article/Scan Fixture Pack v0 (implemented)
31. Manual External Baseline Observation Pack v0 (implemented)
32. Manual Observation Batch 0 (implemented as pending slots only)
33. Manual Observation Entry Helper v0 (implemented)
34. LIVE_ALPHA_00 Static Public Site Pack (implemented)
35. Public Alpha Rehearsal Evidence v0 (implemented)
36. LIVE_ALPHA_01 Production Public-Alpha Wrapper
37. LIVE_ALPHA_02 Deployment Config Pack
38. Manual Observation Batch 0 Execution (human-operated parallel work)
39. LIVE_ALPHA_04 Live Probe Gateway Contract
40. Rust Query Planner Parity Candidate v0
41. Compatibility Surface Strategy v0
42. Native App Work Later

## Immediate Next Milestone

The next implementation milestone should be:

> LIVE_ALPHA_01 Production Public-Alpha Wrapper

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
- Result Lanes + User-Cost Ranking v0 now adds bounded deterministic
  presentation hints for member-vs-parent usefulness without becoming final
  production ranking
- Compatibility Evidence Pack v0 now adds source-backed Windows 7, Windows XP,
  and Windows 2000 fixture evidence where current records support it while
  preserving unknown compatibility
- Search Usefulness Audit Delta v0 records a modest measured movement: partial
  results increased from 1 to 5, `source_gap` decreased from 43 to 41, and
  `capability_gap` decreased from 13 to 11 against the historical reported
  aggregate baseline
- Old-Platform Source Coverage Expansion v0 expanded recorded fixtures and the
  current Search Usefulness Audit now reports `covered=5`, `partial=20`,
  `source_gap=28`, `capability_gap=9`, and `unknown=2`
- Search Usefulness Audit Delta v1 records that movement and shows archive
  evals at `capability_gap=1` and `not_satisfied=5`
- Hard Eval Satisfaction Pack v0 maps current source-backed candidates into
  hard expected-result checks without weakening task definitions; archive evals
  now report `capability_gap=1` and `partial=5`
- Old-Platform Result Refinement Pack v0 scores expected lanes, bad-result
  avoidance, and result-shape quality for the current source-backed partials;
  archive evals now report `capability_gap=1`, `partial=4`, and `satisfied=1`
- More Source Coverage Expansion v1 adds targeted tiny recorded fixture
  evidence for the four old-platform partials; archive evals now report
  `capability_gap=1` and `satisfied=5`
- Article/Scan Fixture Pack v0 adds bounded synthetic article/page/scan
  evidence; archive evals now report `satisfied=6`
- Manual External Baseline Observation Pack v0 adds the manual-only schema,
  templates, pending slots, validation, and status reporting needed to record
  external observations without scraping or fabricated baselines
- Manual Observation Batch 0 selects the first 13-query, 39-slot subset for
  human operation without filling or fabricating observations
- Manual Observation Entry Helper v0 now makes the human entry workflow safer:
  it lists pending slots, creates fillable pending files, validates one file or
  all files, and reports Batch 0 progress without performing any observation
- LIVE_ALPHA_00 Static Public Site Pack now gives the project a committed
  static public-facing explanation of prototype status, source matrix,
  eval/audit posture, demo queries, limitations, roadmap, and local quickstart
  without deploying anything or adding live source behavior
- Public Alpha Rehearsal Evidence v0 now records the static validator,
  smoke-check, route inventory, eval/audit, baseline pending status, blockers,
  next requirements, and unsigned signoff evidence without deploying or
  approving production
- the next Codex-side bottleneck is a bounded production public-alpha wrapper
  design around the current constrained posture; actual Batch 0 observation
  evidence is still a human-operated parallel task, and Google/Internet
  Archive baselines remain pending/manual for all 64 queries globally

## Explicit Deferrals

The backend roadmap intentionally defers:

- Visual Studio app work
- Xcode app work
- full native app work
- production Rust rewrite
- Rust behavior ports that do not match Python-oracle fixtures
- automated Google or Internet Archive scraping
- live Internet Archive probes before a gateway contract and abuse controls
- installer or download automation
- trust scoring
- production relevance benchmarking
- vector-heavy retrieval
- LLM-heavy planning
- broad live federation
- auth, HTTPS/TLS, accounts, and production deployment remain outside this slice
