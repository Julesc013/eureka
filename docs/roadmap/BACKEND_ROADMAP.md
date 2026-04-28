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
- Rust Query Planner Parity Candidate v0 as the second isolated Rust behavior
  seam, compared against expanded Python-oracle query-planner goldens and not
  wired into runtime behavior
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
- LIVE_ALPHA_01 Production Public-Alpha Wrapper as the first explicit
  public-alpha process/config guard, adding a localhost-default stdlib
  entrypoint, closed live-probe/live-IA gates, nonlocal bind validation, safe
  status/capability reporting, and disabled local path/download/user-storage
  controls without deployment, provider configuration, auth/TLS, rate limiting,
  process management, or production approval
- Public Publication Plane Contracts v0 as the first governed public
  publication contract layer, adding route, route-stability, public status,
  client-profile, public-data, static-export, base-path, deployment-target, and
  redirect inventories before GitHub Pages or static-generation work, without
  adding deployment workflows, provider configuration, a generator, live backend
  behavior, live probes, or external observations
- GitHub Pages Deployment Enablement v0 as the first static-only Pages
  publishing path for `public_site/`, adding a workflow, artifact checker,
  operations doc, and safety tests that upload only the static artifact after
  validating the publication inventory and static site, without deploying the
  Python backend, enabling live probes, adding a custom domain, adding a
  generator, or claiming deployment success without Actions evidence
- Static Site Generation Migration v0 as the first stdlib-only static-site
  source/generator tree under `site/`, rendering the current no-JS public pages
  into `site/dist/` for validation while keeping `public_site/` as the GitHub
  Pages deployment artifact and avoiding Node/npm, frontend frameworks,
  deployment changes, live backend behavior, live probes, and production claims
- Generated Public Data Summaries v0 as the first static machine-readable
  publication data layer under `public_site/data/` and `site/dist/data/`,
  projecting page, source, eval, route, and build summaries from governed repo
  inputs without adding live API semantics, live probes, external observations,
  deployment behavior, or production API stability claims
- Lite/Text/Files Seed Surfaces v0 as the first static compatibility surface
  layer under `public_site/lite/`, `public_site/text/`, and
  `public_site/files/`, generating old-browser HTML, plain text, file-tree
  manifest/checksum views, and `site/dist/` validation copies from public data
  summaries without adding live search, executable downloads, snapshots,
  relay/native runtime behavior, or production support claims
- Static Resolver Demo Snapshots v0 as the first static resolver example layer
  under `public_site/demo/`, with generated `site/dist/demo/` validation copies
  and a static demo manifest showing query planning, member results,
  compatibility evidence, absence, comparison, source detail, article/scan
  results, and eval summaries without live search, live API semantics, backend
  hosting, external observations, or production behavior
- Custom Domain / Alternate Host Readiness v0 as the first static host
  portability readiness layer, adding domain/host inventories, base-path
  guidance, and an unsigned future operator checklist without DNS, `CNAME`,
  provider config, alternate-host deployment, backend hosting, or live probes
- Live Backend Handoff Contract v0 as the first contract-only static-to-live
  handoff layer, reserving future `/api/v1` endpoint families, disabled
  capability flags, and error-envelope expectations without hosting a backend,
  making `/api/v1` live, enabling live probes, or creating production API
  guarantees
- Live Probe Gateway Contract v0 as the first disabled-by-default source-probe
  policy layer, defining candidate sources, global and per-source caps,
  cache/evidence requirements, retry/circuit-breaker posture, and operator
  gates without implementing adapters, calling external services, fetching
  URLs, scraping, crawling, enabling downloads, or making Google a live source
- Rust Query Planner Parity Candidate v0 as the isolated Rust planner
  candidate under `crates/eureka-core/`, with expanded Python-oracle planner
  goldens, a case map, and a stdlib parity check, without wiring Rust into the
  Python planner, gateway, web, CLI, HTTP API, workers, public-alpha paths, or
  production behavior

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
36. LIVE_ALPHA_01 Production Public-Alpha Wrapper (implemented)
37. Public Publication Plane Contracts v0 (implemented)
38. GitHub Pages Deployment Enablement v0 (implemented as static workflow configuration; deployment success unverified)
39. Static Site Generation Migration v0 (implemented; generated output not deployed)
40. Generated Public Data Summaries v0 (implemented as static JSON summaries)
41. Lite/Text/Files Seed Surfaces v0 (implemented as static compatibility seed surfaces)
42. Static Resolver Demo Snapshots v0 (implemented as static fixture-backed demos)
43. Custom Domain / Alternate Host Readiness v0 (implemented as static host readiness policy; no DNS/CNAME/provider config)
44. Live Backend Handoff Contract v0 (implemented as contract-only `/api/v1` handoff reservation; no live backend)
45. Live Probe Gateway Contract v0 (implemented as contract-only source-probe policy; no probes or network calls)
46. Rust Query Planner Parity Candidate v0 (implemented as isolated parity seam)
47. Compatibility Surface Strategy v0 (implemented as strategy/contracts/inventory only; no new runtime behavior)
48. Signed Snapshot Format v0 (implemented as contract and repo seed example; no real keys, production signatures, downloads, public route, relay, native runtime, live backend, or live probes)
49. Relay Surface Design v0 (implemented as design/contract/checklist only; no relay runtime, sockets, protocol servers, private data exposure, write/admin routes, or live-probe passthrough)
50. Rust Source Registry Parity Catch-up v0
51. Rust Local Index Parity Planning v0
52. Signed Snapshot Consumer Contract v0
53. Manual Observation Batch 0 Execution (human-operated parallel work)
54. Native App Work Later

## Immediate Next Milestone

The next implementation milestone should be:

> Rust Source Registry Parity Catch-up v0

Why this comes next:

- Live Probe Gateway Contract v0 now defines the disabled-by-default source
  policy that must exist before any live external probe.
- The repo still has no live probe implementation, no Internet Archive live
  calls, no URL fetching, no downloads, and no source adapters for external
  probing.
- Rust Query Planner Parity Candidate v0 is now implemented as a non-network,
  isolated candidate and remains unwired from runtime behavior.
- Manual Observation Batch 0 remains human-operated parallel work, and all
  Google/Internet Archive baseline observations remain pending/manual until
  real human evidence records exist.
- Compatibility Surface Strategy v0 is now implemented as strategy, route
  matrix, capability matrix, and old-client/native/snapshot/relay readiness
  policy without new runtime behavior.
- Signed Snapshot Format v0 is implemented as the current non-network contract
  step after lite/text/files, public data summaries, static demo snapshots, and
  surface strategy. It adds only a deterministic seed example plus checksum and
  signature-placeholder policy, with no real signing keys, production
  signatures, executable downloads, public `/snapshots/` route, relay/native
  runtime, live backend behavior, or live probes.
- Relay Surface Design v0 is implemented as design, inventory, validation, and
  operator/security guidance only. It defines the future local/LAN relay posture
  without implementing FTP, SMB, WebDAV, Gopher, proxy behavior, sockets,
  backend hosting, native clients, private data exposure, write/admin routes, or
  live-probe passthrough.
- Rust Source Registry Parity Catch-up v0 is now the next non-network planning
  step because the source/capability shape has expanded since the first isolated
  Rust source-registry parity seam.
- Internet Archive Live Probe v0 should remain unstarted unless a human
  explicitly approves live external-source behavior after separate review.

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

## Backend Roadmap Checkpoint

Post-Queue State Checkpoint v0 records the current post-queue evidence and
verification state under `control/audits/post-queue-state-checkpoint-v0/`. It
is audit/reporting only; it does not add backend hosting, live probes,
production deployment, Rust runtime wiring, relay services, or native app
projects.
