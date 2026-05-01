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
  source tree under `site/dist/`, with identity, status, source matrix,
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
  publishing path for `site/dist/`, adding a workflow, artifact checker,
  operations doc, and safety tests that upload only the static artifact after
  validating the publication inventory and static site, without deploying the
  Python backend, enabling live probes, adding a custom domain, adding a
  generator, or claiming deployment success without Actions evidence
- Static Site Generation Migration v0 as the first stdlib-only static-site
  source/generator tree under `site/`, rendering the current no-JS public pages
  into `site/dist/` while avoiding Node/npm, frontend frameworks, live backend
  behavior, live probes, and production claims
- Repository Shape Consolidation v0 as the layout consolidation pass that makes
  `site/dist/` the single generated static deployment artifact, removes the
  active legacy static artifact path, and confirms `external/` as the
  outside-reference root without adding public search, backend hosting, live
  probes, relay runtime, native clients, or production claims
- GitHub Pages Run Evidence Review v0 as the passive evidence audit for the
  static Pages workflow, recording a current-head failure at Pages configuration
  after static checks passed and before artifact upload, without triggering
  deployment or adding backend behavior
- Public Search API Contract v0 as the governed definition of
  `local_index_only` public search request, response, error, and route
  envelopes, followed by Local Public Search Runtime v0 as the first
  local/prototype backend implementation of `/search`, `/api/v1/search`,
  `/api/v1/query-plan`, `/api/v1/status`, `/api/v1/sources`, and
  `/api/v1/source/{source_id}` without hosted deployment, static search
  handoff, live probes, fetching URLs, crawling, downloads, installs, uploads,
  local path search, accounts, telemetry, or production API guarantees
- Generated Public Data Summaries v0 as the first static machine-readable
  publication data layer under `site/dist/data/`,
  projecting page, source, eval, route, and build summaries from governed repo
  inputs without adding live API semantics, live probes, external observations,
  deployment behavior, or production API stability claims
- Lite/Text/Files Seed Surfaces v0 as the first static compatibility surface
  layer under `site/dist/lite/`, `site/dist/text/`, and
  `site/dist/files/`, generating old-browser HTML, plain text, file-tree
  manifest/checksum views from public data summaries without adding live search,
  executable downloads, snapshots,
  relay/native runtime behavior, or production support claims
- Static Resolver Demo Snapshots v0 as the first static resolver example layer
  under `site/dist/demo/`, with a static demo manifest showing query planning,
  member results,
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
39. Static Site Generation Migration v0 (implemented)
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
50. Rust Source Registry Parity Catch-up v0 (implemented as isolated current-shape source registry parity; no runtime wiring)
51. Rust Local Index Parity Planning v0 (implemented as planning/contract only; no Rust index implementation or runtime wiring)
52. Signed Snapshot Consumer Contract v0 (implemented as contract/design only; no consumer runtime, relay, native client, production signing, real keys, downloads, live backend, or live probes)
53. Native Client Contract v0 (implemented as contract/design only; no Visual Studio/Xcode projects, GUI, FFI, installers, downloads, relay sidecars, live probes, or Rust runtime wiring)
54. Native Action / Download / Install Policy v0 (implemented as policy/contract only; no downloads, installers, package-manager integration, malware scanning, rights clearance, native clients, relay runtime, or executable trust claims)
55. Native Local Cache / Privacy Policy v0 (implemented as policy/contract only; no cache runtime, private ingestion, telemetry, accounts, cloud sync, uploads, native clients, or relay runtime)
56. Native Client Project Readiness Review v0 (implemented as review/evidence only; decision is minimal Windows 7 WinForms skeleton after explicit human approval)
57. Windows 7 WinForms Native Skeleton Planning v0 (implemented as planning only; no project creation)
58. Windows 7 WinForms Native Skeleton Implementation v0 (blocked pending explicit human approval; read-only static-data/snapshot-demo skeleton scope only)
59. Relay Prototype Planning v0 (implemented as planning only; no relay runtime, sockets, protocol servers, private data, live backend proxy, or live probes)
60. Rust Local Index Parity Candidate v0 (blocked pending planning review and Cargo availability)
61. Relay Prototype Implementation v0 (blocked pending explicit human approval; localhost-only read-only static relay scope only)
62. Manual Observation Batch 0 Execution (human-operated parallel work)
63. Native App Work Later
64. Public Data Contract Stability Review v0 (implemented as field-level public data stability governance; no production API claim)
65. Generated Artifact Drift Guard v0 (implemented as validation/audit only; no regeneration by default, runtime behavior, deployment, or network behavior)
66. Repository Shape Consolidation v0 (implemented; site/dist is the single generated static artifact and external is the outside-reference root)
67. Static Artifact Promotion Review v0 (implemented; site/dist is conditionally promoted as active repo-local static artifact)
68. GitHub Pages Run Evidence Review v0 (implemented; current-head Pages run failed at configuration before artifact upload)
69. Public Search API Contract v0 (implemented as governed local_index_only request/response/error/route envelopes)
70. Public Search Result Card Contract v0 (implemented as contract-only result-card schema, examples, audit pack, docs, validator, and tests; no runtime routes or download/install/execute behavior)
71. Public Search Safety / Abuse Guard v0 (implemented as safety, abuse, privacy, operator-control, validator, and readiness-checklist governance; no hosted runtime or middleware)
72. Local Public Search Runtime v0 (implemented as local/prototype backend runtime only; no hosted deployment, live probes, downloads, uploads, accounts, telemetry, or production claim)
73. Public Search Static Handoff v0 (implemented as static/no-JS `site/dist` handoff only; hosted backend remains unavailable/unverified)
74. Public Search Rehearsal v0 (implemented as local/prototype route, safe-query, blocked-request, static-handoff, public-alpha, and contract-alignment evidence only; no hosted deployment, live probes, downloads, uploads, local path search, accounts, telemetry, or production claim)
75. Search Usefulness Source Expansion v2, fixture-only (implemented as six recorded fixture source families and 15 tiny metadata records; no live calls, scraping, crawling, external observations, real binaries, download/install/upload actions, hosted search, or production relevance claim)
76. Search Usefulness Delta v2 (implemented as audit-only measurement of Source Expansion v2 status deltas, query movement, source-family impact, remaining gaps, hard-eval status, public-search smoke status, and pending/manual external baselines)
77. Source Pack Contract v0 (implemented as contract/validation/example-only source-pack format, synthetic example pack, checksum validator, lifecycle docs, and audit pack; no import, indexing, upload, live connectors, executable plugins, hosted submission, or master-index acceptance)
78. Evidence Pack Contract v0 (implemented as contract/validation/example-only evidence-pack format, synthetic example pack, checksum validator, docs, and audit pack; no import, indexing, upload, live connectors, executable plugins, canonical truth selection, hosted submission, or master-index acceptance)
79. Index Pack Contract v0 (implemented as contract/validation/example-only index-pack format, synthetic summary-only example pack, checksum validator, docs, and audit pack; no import, merge, upload, raw SQLite/local-cache export, live connectors, executable plugins, canonical truth selection, hosted ingestion, or master-index acceptance)
80. Contribution Pack Contract v0 (implemented as contract/validation/example-only contribution-pack format, synthetic review-candidate example pack, checksum validator, docs, and audit pack; no upload, import, moderation, accounts, master-index review queue runtime, automatic acceptance, live connectors, executable plugins, canonical truth selection, hosted ingestion, or master-index acceptance)
81. Master Index Review Queue Contract v0 (implemented as contract/validation/example-only queue governance, synthetic defer-decision example queue, schemas, inventory, validator, docs, and audit pack; no queue runtime, upload, import, moderation, accounts, hosted master index, master-index writes, automatic acceptance, live connectors, canonical truth selection, rights-clearance claim, malware-safety claim, or production claim)
82. Source/Evidence/Index Pack Import Planning v0 (implemented as planning-only import boundary, audit pack, docs, validator, and tests; validate-only is the first future mode and private local quarantine is the next future mode; no import runtime, staging directories, local search/index mutation, canonical registry mutation, uploads, hosted/master-index mutation, automatic acceptance, live fetch, arbitrary directory scan, executable plugin behavior, or production claim)
83. Pack Import Validator Aggregator v0 (implemented as validate-only aggregate command, example-pack registry, docs, audit pack, and tests; validates all known source/evidence/index/contribution/master-index review queue examples without import, staging, indexing, uploads, hosted/master-index mutation, automatic acceptance, rights-clearance claim, malware-safety claim, or production claim)
84. AI Provider Contract v0 (implemented as contract/validation/example-only provider manifests, task requests, typed output schemas, disabled stub provider example, policy inventory, validator, docs, audit pack, and tests; no model calls, API keys, credential storage, telemetry, provider runtime loading, AI in public search, AI-generated evidence acceptance, local index mutation, or master-index mutation)
85. Typed AI Output Validator v0 (implemented as offline typed-output validation module, CLI, registry, synthetic examples, docs, audit pack, and tests; no model calls, provider runtime, API keys, telemetry, evidence import, contribution import, local index mutation, public-search AI, upload, or master-index mutation)
86. Pack Import Report Format v0 (implemented as report schema, synthetic passed/failed/unknown examples, stdlib validator, docs, audit pack, and tests; no import runtime, staging, indexing, uploads, runtime mutation, model calls, network behavior, or master-index mutation)
87. Validate-Only Pack Import Tool v0 (implemented as explicit-root/all-examples preflight tooling that delegates to existing validators and emits Pack Import Report v0; no import, staging, indexing, upload, runtime mutation, network behavior, model calls, public-search mutation, or master-index mutation)
88. Local Quarantine/Staging Model v0 (implemented as planning/governance local-state model, path policy, audit pack, validator, and tests; no staging runtime, staged state, pack copying, import, local index mutation, public-search mutation, upload, network/model calls, or master-index mutation)
89. Staging Report Path Contract v0 (implemented as planning/governance report path contract, local-state inventory, docs, audit pack, validator, tests, and validate-only output-root enforcement; no report path runtime, staging runtime, staged state, import, local index mutation, public-search mutation, upload, or master-index mutation)

## Immediate Next Milestone

The next implementation milestone should be:

> Local Staging Manifest Format v0

Why this comes next:

- Public Data Contract Stability Review v0 now classifies generated public JSON
  files and fields as `stable_draft`, `experimental`, `volatile`, `internal`,
  `deprecated`, or `future`, while keeping public JSON pre-alpha and not a
  production API.
- Repository Shape Consolidation v0 now removes the active dual-artifact model
  and makes `site/dist` the single generated static artifact checked by the
  workflow, validators, inventory, and drift guard.
- Generated Artifact Drift Guard v0 now checks generated and generated-like
  committed artifacts across `site/dist`, public data,
  lite/text/files surfaces, demo snapshots, seed snapshots, Python oracle
  goldens, public-alpha rehearsal evidence, publication inventories, test
  registry metadata, and AIDE metadata without regenerating artifacts by
  default or changing runtime behavior.
- Static Artifact Promotion Review v0 is implemented as the local artifact
  promotion review for `site/dist`.
- GitHub Pages Run Evidence Review v0 is implemented as the passive workflow
  evidence review. It records a current-head failure at Pages configuration,
  with no artifact uploaded and no deployment URL available.
- Public Search API Contract v0 is implemented as contract/governance, and
  Local Public Search Runtime v0 now implements the first local/prototype
  backend routes through the gateway and stdlib web server while keeping
  `local_index_only` as the only mode.
- Public Search Result Card Contract v0 is implemented as contract/governance
  only. It defines the future public result-card shape for web/API/lite/text,
  native, relay, snapshot, and contribution consumers without making search
  live, adding route handlers, enabling downloads/installers/execution/uploads,
  claiming malware safety, claiming rights clearance, or promising production
  ranking.
- Public Search Safety / Abuse Guard v0 is implemented as policy/governance
  over the local runtime and future hosted review. It defines local_index_only
  mode, request/result/time limits, forbidden
  parameters, disabled live/external behavior, error mapping, logging/privacy
  defaults, operator controls, and runtime readiness gates without adding
  rate-limit middleware, telemetry runtime, hosted backend, live probes,
  downloads, uploads, local path search, accounts, or
  production safety claims.
- Public Search Static Handoff v0 now connects the static publication plane to
  the already-local route with no-JS `site/dist` handoff outputs while keeping
  hosted backend search unavailable/unverified and GitHub Pages static-only.
- Public Search Rehearsal v0 now records local/prototype route checks, nine
  safe-query outcomes, fourteen blocked-request outcomes, static handoff
  review, public-alpha review, and contract alignment without hosted
  deployment, live probes, downloads, uploads, local path search, accounts,
  telemetry, or production claims.
- Search Usefulness Source Expansion v2 is implemented as fixture-only source
  coverage. It moved the current audit from covered=5/partial=22/source_gap=26/
  capability_gap=9/unknown=2 to covered=5/partial=40/source_gap=10/
  capability_gap=7/unknown=2 without live source calls, scraping, crawling,
  external observations, arbitrary local ingestion, real binaries, downloads,
  uploads, hosted search, or production relevance claims.
- Search Usefulness Delta v2 is implemented as audit/governance. It records
  the measured Source Expansion v2 delta, selected query movement,
  source-family impact, current failure modes, public-search smoke status,
  hard-eval status, external-baseline pending status, and remaining gaps
  without adding source/runtime behavior.
- Source Pack Contract v0 is implemented as contract/validation/example-only
  work. It defines portable source metadata packs, required rights/privacy
  notes, checksum validation, source-record alignment, prohibited behavior,
  and lifecycle guidance without import, indexing, upload, live connectors,
  executable plugins, hosted submission, downloads, or master-index
  acceptance.
- Evidence Pack Contract v0 is implemented as contract/validation/example-only
  work. It defines portable claim/observation packs, source locators, allowed
  evidence kinds and claim types, snippet limits, rights/privacy posture, and
  checksum validation without import, indexing, upload, live connectors,
  executable plugins, canonical truth selection, hosted submission, downloads,
  or master-index acceptance.
- Index Pack Contract v0 is implemented as contract/validation/example-only
  work. It defines summary-only index build metadata, source coverage, field
  coverage, query examples, record summaries, privacy/rights posture, and
  checksum validation without import, merge, upload, raw SQLite/local-cache
  export, live connectors, executable plugins, canonical truth selection,
  hosted ingestion, downloads, or master-index acceptance.
- Contribution Pack Contract v0 is implemented as contract/validation/example-only
  work. It defines review-candidate contribution items, source/evidence/index
  pack references, manual-observation placeholders, alias/compatibility/absence
  and result-feedback candidates, privacy/rights posture, review requirements,
  and checksum validation without upload, import, moderation, accounts,
  master-index review queue runtime, automatic acceptance, live connectors,
  executable plugins, hosted ingestion, downloads, or master-index acceptance.
- Master Index Review Queue Contract v0 is implemented as
  contract/validation/example-only work. It defines queue entries, review
  decisions, validation/review states, acceptance requirements,
  privacy/rights/risk review, conflict preservation, and publication policy
  without queue runtime, upload, import, moderation, accounts, hosted master
  index, master-index writes, automatic acceptance, live connectors,
  executable plugins, rights-clearance claims, malware-safety claims, or
  production claims.
- Source/Evidence/Index Pack Import Planning v0 is implemented as planning
  only. It defines import scope, validate-only and quarantine modes, staging
  policy, validation pipeline, privacy/rights/risk review, provenance, local
  search boundaries, native/snapshot/relay impact, and master-index review
  interaction. It adds no import runtime, staging directories, local
  search/index mutation, canonical source registry mutation, upload,
  hosted/master-index mutation, automatic acceptance, live fetch, arbitrary
  directory scanning, executable plugin behavior, or production claim.
- Pack Import Validator Aggregator v0 is implemented as validate-only
  reporting. It adds `scripts/validate_pack_set.py` and
  `control/inventory/packs/example_packs.json`, validates all five known
  examples through existing validators, reports pass/fail/unavailable/
  unknown-type status, and still adds no import, staging, local index mutation,
  upload, hosted/master-index mutation, automatic acceptance, rights-clearance
  claim, malware-safety claim, or production claim.
- AI Provider Contract v0 is implemented as a disabled-by-default AI boundary.
  It defines provider manifests, typed output shape, task requests, privacy,
  credential, logging, evidence-linking, and review posture without model
  calls, API keys, telemetry, provider runtime loading, AI in public search,
  local-index mutation, or master-index mutation.
- Typed AI Output Validator v0 is implemented as an offline validation layer
  for standalone typed AI output candidates. It adds a pure Python validation
  module, CLI, example registry, four synthetic output examples, docs, audit
  pack, and tests; it enforces required review, prohibited truth/rights/
  malware/auto-acceptance uses, provider alignment, generated-text bounds,
  private-path and secret rejection, and no model/network/import/mutation side
  effects.
- Pack Import Report Format v0 is implemented as format/validation/example-only
  work. It defines `pack_import_report.v0`, validates synthetic passed/failed/
  unknown reports, records privacy/rights/risk and issue outcomes, and keeps
  import/staging/index/upload/runtime/master-index mutation fields false.
  Validate-Only Pack Import Tool v0 is now implemented so validation can emit
  the durable report format without staging or importing packs.
- Validate-Only Pack Import Tool v0 is implemented as validate-only preflight
  tooling. It validates explicit pack roots or known examples, can include
  typed AI output examples when requested, writes only an explicit report file
  when `--output` is provided, and still does not import, stage, index, upload,
  mutate runtime state, mutate public search, call networks, call models, or
  mutate the master index.
- Local Quarantine/Staging Model v0 is implemented as planning/governance only.
  It defines future private roots, staged entity vocabulary, Pack Import
  Report v0 linking, reset/delete/export requirements, and native/relay/
  snapshot boundaries while creating no staging runtime or staged state and
  preserving no-impact defaults for search and the master index.
- Staging Report Path Contract v0 is implemented as planning/governance only.
  It defines stdout-by-default report output, explicit output paths,
  forbidden public/runtime/canonical roots, future ignored local-private report
  roots, filename safety, redaction, and validate-only output-root enforcement
  while creating no report path runtime, staging runtime, staged state, import,
  search impact, or master-index impact. Local Staging Manifest Format v0 is
  the next Codex-safe milestone; Manual Observation Batch 0 Execution remains
  human-operated parallel work.
- GitHub Pages Workflow Repair v0 remains an operator/Pages follow-up before
  any hosted deployment-success claim is made.
- Native Client Project Readiness Review v0 now records the evidence decision
  `ready_for_minimal_project_skeleton_after_human_approval` for the
  `windows_7_x64_winforms_net48` lane only.
- Windows 7 WinForms Native Skeleton Planning v0 now records the proposed
  `clients/windows/winforms-net48/` path,
  `Eureka.Clients.Windows.WinForms` namespace, Windows host / Visual Studio
  2022 / .NET Framework 4.8 / x64 / Windows 7 SP1+ requirements, read-only
  static-data/snapshot-demo scope, prohibited features, and approval gate
  without creating project files.
- Any skeleton implementation must wait for explicit human approval and must
  remain inside the approved read-only planning scope.
- Relay Prototype Planning v0 now records the recommended first future relay
  prototype as `local_static_http_relay_prototype`, localhost-only by default,
  read-only, static, and limited to allowlisted public data plus seed snapshot
  files. It adds no relay runtime, sockets, local HTTP relay, protocol server,
  private data, live backend proxy, live probes, or old-client relay support.
- Relay Prototype Implementation v0 must wait for explicit human approval and
  must remain inside that approved localhost-only/read-only/static scope.
- Manual Observation Batch 0 remains human-operated parallel work, and all
  Google/Internet Archive baseline observations remain pending/manual until
  real human evidence records exist.
- Rust Local Index Parity Candidate v0 should not start until the planning lane
  is reviewed and Cargo availability/expectations are explicit.
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

Full Project State Audit v0 records the current post-relay-planning project
state under `control/audits/full-project-state-audit-v0/`. Its immediate
recommendation is Public Data Contract Stability Review v0, with Generated
Artifact Drift Guard v0 as the alternative. Rust Local Index Parity Candidate
v0 remains blocked on review and Cargo availability; native and relay
implementation remain blocked on explicit human approval.
