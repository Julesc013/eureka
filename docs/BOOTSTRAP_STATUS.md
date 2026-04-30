# Bootstrap Status

Current status: foundational scaffold plus sixty-five executable local deterministic Python thin slices, a placeholder Rust migration skeleton, the first Python-oracle golden fixture pack, the first isolated Rust source-registry parity candidate, Rust Source Registry Parity Catch-up v0, the first isolated Rust query-planner parity candidate, Rust Local Index Parity Planning v0, Search Usefulness Audit v0, Search Usefulness Backlog Triage v0, Search Usefulness Audit Delta v0, Search Usefulness Audit Delta v1, Hard Eval Satisfaction Pack v0, Old-Platform Result Refinement Pack v0, More Source Coverage Expansion v1, Article/Scan Fixture Pack v0, Manual External Baseline Observation Pack v0, Manual Observation Batch 0, Manual Observation Entry Helper v0, LIVE_ALPHA_00 Static Public Site Pack, Public Alpha Rehearsal Evidence v0, LIVE_ALPHA_01 Production Public-Alpha Wrapper, Public Publication Plane Contracts v0, GitHub Pages Deployment Enablement v0, Static Site Generation Migration v0, Generated Public Data Summaries v0, Lite/Text/Files Seed Surfaces v0, Static Resolver Demo Snapshots v0, Custom Domain / Alternate Host Readiness v0, Live Backend Handoff Contract v0, Live Probe Gateway Contract v0, Public Search API Contract v0, Public Search Result Card Contract v0, Public Search Safety / Abuse Guard v0, Local Public Search Runtime v0, Compatibility Surface Strategy v0, Signed Snapshot Format v0, Signed Snapshot Consumer Contract v0, Native Client Contract v0, Native Action / Download / Install Policy v0, Native Local Cache / Privacy Policy v0, Native Client Project Readiness Review v0, Windows 7 WinForms Native Skeleton Planning v0, Post-Queue State Checkpoint v0, Relay Surface Design v0, Relay Prototype Planning v0, Full Project State Audit v0, Public Data Contract Stability Review v0, Generated Artifact Drift Guard v0, Repository Shape Consolidation v0, Static Artifact Promotion Review v0, GitHub Pages Run Evidence Review v0, Comprehensive Test/Eval Operating Layer and Repo Audit v0, and Hard Test Pack v0, with draft contracts and concrete dependency boundary paths in place while broader product implementation remains intentionally deferred.

The executable lane should now be read as a Python reference backend and
architectural oracle rather than as a throwaway scaffold.

## Established

- repo identity and founding docs
- minimal AIDE repo-operating profile and policies
- concrete advisory dependency policy that points to real engine interface boundary paths
- governed archive draft schema skeletons using one consistent JSON Schema style
- draft gateway public API and shared UI contracts aligned to the normal online path
- governed synthetic software fixture set for one exact-match local resolution path
- Python 3 standard library bootstrap execution lane for the current executable slices
- connector-shaped local source loading for governed synthetic software fixtures
- ingest, extract, and normalize boundary types for the bootstrap execution lane
- exact-match engine resolution over normalized records plus bounded object-summary mapping
- transport-neutral gateway submit and read boundary over an in-memory job service
- transport-neutral public search boundary over the governed synthetic software corpus
- shared workbench-session view-model mapping exercised without implementing web or native shells
- shared search-results view-model mapping exercised without implementing web or native shells
- shared resolution-actions view-model mapping exercised without implementing web or native shells
- local demo command that shows submit, read, and optional shared view-model output over the connector-shaped path
- first server-rendered web workbench slice under `surfaces/web/` that consumes the public gateway boundary and shared workbench session without engine coupling
- tiny stdlib local server entrypoint for the compatibility-first web workbench page
- first deterministic search-and-absence web slice that renders result lists and no-match reports and links back into exact resolution flow
- first bounded action/export slice that exposes a manifest-export action through the public boundary and returns deterministic JSON for known synthetic targets
- first portable bundle/export slice that exposes a deterministic self-contained resolution bundle through the public boundary and returns ZIP content for known synthetic targets
- first portable bundle inspection/readback slice that inspects a previously exported bundle through a public boundary and renders a compatibility-first HTML inspection page without live fixture dependence
- first deterministic local store/cache seam that assigns stable artifact identity, stores exported manifest and bundle artifacts in a local content-addressed store, and reads them back through the public boundary
- first stable resolved-resource identity seam that derives a deterministic bootstrap `resolved_resource_id` and propagates it across resolution, search, action, export, store, inspection, and compatibility-first surface projection
- first non-web local CLI surface under `surfaces/native/cli/` that reuses the same gateway public boundary and shared surface-neutral mappings already proven by the web surface for exact resolution, deterministic search, export, inspection, and stored-export flows
- first repo-local architectural-boundary checker under `scripts/check_architecture_boundaries.py` that enforces the current Python import layering between surfaces, `runtime/gateway/public_api`, connectors, and engine
- first local stdlib machine-readable HTTP API slice under `surfaces/web/server/` that exposes exact resolution, deterministic search, manifest export, bundle export, bundle inspection, and local stored-export flows as JSON or ZIP responses over the same transport-neutral public boundary already consumed by the HTML and CLI surfaces
- first bounded real external-source connector slice under `runtime/connectors/github_releases/` that loads small recorded GitHub Releases fixtures, normalizes them into the existing engine path, and exposes source-family visibility through the public boundary plus current web, CLI, and HTTP API surfaces
- first bounded provenance and evidence seam under `runtime/engine/provenance/` that carries compact source-backed evidence summaries from normalize through exact resolution, deterministic search, export, storage, bundle inspection, and current surfaces without forcing a final truth, trust, or merge model
- first bounded comparison and disagreement seam under `runtime/engine/compare/` that compares exactly two resolved targets side by side, preserves evidence per side, and surfaces explicit agreements and disagreements through the public boundary plus current surfaces without forcing merge or trust-selection behavior
- first bounded object/state timeline seam under `runtime/engine/states/` that groups multiple bounded states under one bootstrap `subject_key`, orders them deterministically, and surfaces compact source plus evidence summaries through the public boundary plus current surfaces without forcing a final object identity or temporal graph model
- first bounded absence-reasoning seam under `runtime/engine/absence/` that explains exact-resolution misses and deterministic search no-result cases with checked source-family summaries, compact near matches, and bounded next steps through the public boundary plus current surfaces without forcing ranking, trust, or final diagnostic behavior
- first bounded representation/access-path seam under `runtime/engine/representations/` that carries multiple known source-backed representation and access-path summaries for one resolved target through normalize, exact resolution, public boundaries, and current surfaces without forcing final download, install, import, restore, or representation-selection semantics
- first bounded compatibility and host-profile seam under `runtime/engine/compatibility/` that evaluates one resolved target against one bootstrap host profile preset, returns compact reasons plus honest `unknown` outcomes, and surfaces the verdict through the public boundary plus current surfaces without forcing installer logic, runtime routing, or a final compatibility oracle
- first bounded action-routing and recommendation seam under `runtime/engine/action_routing/` that combines one resolved target, bounded representations, optional host-profile compatibility, and bounded local export/store context into explicit recommended, available, and unavailable actions through the public boundary plus current surfaces without forcing execution, installer, or workflow-policy behavior
- first bounded user-strategy and intent-profile seam under `runtime/engine/strategy/` plus `runtime/engine/action_routing/` that lets the same resolved target produce different bounded recommendation emphasis under explicit strategy profiles while preserving underlying identity, evidence, and representation truth through the public boundary plus current surfaces
- first bounded representation-selection and handoff seam under `runtime/engine/handoff/` that lets one resolved target surface a preferred bounded representation plus explicit available, unsuitable, and unknown alternatives shaped by optional host and strategy input through the public boundary plus current surfaces without forcing downloads, installers, runtime launches, or final routing semantics
- first bounded acquisition and fetch seam under `runtime/engine/acquisition/` that lets one resolved target plus one explicit bounded representation retrieve tiny deterministic local payload bytes through the public boundary plus current surfaces, while preserving unavailable and blocked outcomes without forcing live downloads, installers, restore flows, or execution semantics
- first bounded decomposition and package-member seam under `runtime/engine/decomposition/` that lets one resolved target plus one explicit fetched bounded representation surface a compact ZIP member listing through the public boundary plus current surfaces, while returning explicit unsupported, unavailable, and blocked outcomes without forcing extraction, installers, import, or restore semantics
- first bounded member-readback and preview seam under `runtime/engine/members/` that lets one resolved target plus one explicit representation and member path surface compact text previews or bounded byte readback through the public boundary plus current surfaces, while returning explicit unsupported, unavailable, and blocked outcomes without forcing extraction to disk, installers, import, or restore semantics
- first repo-level archive-resolution eval corpus under `evals/archive_resolution/` that records hard software-resolution queries, explicit bad-result patterns, minimum granularity expectations, expected future result lanes, and allowed absence outcomes before broader investigation, ranking, decomposition, source-expansion, or optional AI claims are introduced
- first bounded Source Registry v0 seam under `contracts/source_registry/`, `control/inventory/sources/`, and `runtime/source_registry/` that records explicit governed source metadata, validates seed inventory records with stdlib-only runtime checks, and projects bounded source-registry listing plus detail views through the public boundary and current web, CLI, plus local HTTP API surfaces without implying live sync, crawling, health scoring, trust scoring, or implemented placeholder connectors
- first bounded Source Coverage and Capability Model v0 seam under
  `contracts/source_registry/`, `control/inventory/sources/`,
  `runtime/source_registry/`, and current source-registry public projections
  that records explicit capability booleans plus coverage-depth metadata for
  every seed source, keeps placeholder and local/private sources honest, and
  exposes safe source capability summaries through web, CLI, and local HTTP API
  without adding connectors, live source probing, crawling, or acquisition
  behavior
- first bounded Resolution Run Model v0 seam under `runtime/engine/resolution_runs/` that records synchronous exact-resolution, deterministic-search, and planned-search investigations as local JSON run records with checked source ids and families, current result summaries or bounded absence reports, and bounded public projection through current web, CLI, plus local HTTP API surfaces without implying worker queues, streaming phases, or async orchestration
- first bounded Query Planner v0 seam under `runtime/engine/query_planner/` that deterministically classifies a bounded set of archive-resolution eval query families into structured `ResolutionTask` records with compact platform, product, hardware, date, prefer/exclude, action-hint, and source-hint summaries, and projects those plans through current web, CLI, plus local HTTP API surfaces without implying LLM planning, vector search, fuzzy retrieval, ranking, or full investigation planning
- first bounded Local Index v0 seam under `runtime/engine/index/` that builds a caller-provided local SQLite index over the current bounded corpus, prefers FTS5 when available and falls back to deterministic non-FTS query behavior otherwise, preserves compact source ids, source families, representation and member text, evidence summaries, source-registry records, and bootstrap `resolved_resource_id` values where available, and projects build, status, plus query results through current web, CLI, plus local HTTP API surfaces without implying ranking, fuzzy retrieval, vector search, live source sync, incremental indexing, or final hosted search semantics
- first bounded Local Worker and Task Model v0 seam under `runtime/engine/workers/` that records synchronous local validation and indexing tasks as JSON task records under a caller-provided bootstrap `task_store_root`, wraps existing Source Registry v0, Local Index v0, and archive-resolution eval validation behavior through a transport-neutral public boundary reused by current web, CLI, plus local HTTP API surfaces, and does not imply background scheduling, retries, priorities, async orchestration, or distributed queue semantics
- first bounded Resolution Memory v0 seam under `runtime/engine/memory/` that derives explicit local reusable successful-resolution, successful-search, and absence-finding memory records from persisted completed resolution runs, stores them as JSON under a caller-provided bootstrap `memory_store_root`, and projects them through a transport-neutral public boundary reused by current web, CLI, plus local HTTP API surfaces without implying cloud memory, private user-history tracking, personalization, ranking, or an invalidation engine
- first bounded Archive Resolution Eval Runner v0 seam under `runtime/engine/evals/` that executes the governed hard-query packet through Query Planner v0, Local Index v0 or deterministic search fallback, and bounded absence reasoning, then reports stable JSON task and suite results with explicit satisfied, partial, not-satisfied, not-evaluable, and capability-gap checks without implying ranking, fuzzy retrieval, vector search, LLM planning, crawling, live sync, or production relevance evaluation
- first bounded Public Alpha Safe Mode v0 seam under `surfaces/web/server/` that separates trusted `local_dev` behavior from constrained `public_alpha` behavior, blocks caller-provided local path parameters in public-alpha mode, adds `/status` plus `/api/status`, and keeps safe read-only/search/eval routes available without implying production deployment, auth, accounts, HTTPS/TLS, or multi-user hosting
- first bounded Public Alpha Deployment Readiness Review seam through `control/inventory/public_alpha_routes.json`, `scripts/public_alpha_smoke.py`, and `docs/operations/` that inventories safe, blocked, local-dev-only, and review-required route groups, smoke-tests public-alpha allowed and blocked behavior, and records operator checklist guidance without deploying Eureka or adding auth, HTTPS/TLS, accounts, rate limiting, production process management, or hosting infrastructure
- first bounded Public Alpha Hosting Pack v0 seam under `docs/operations/public_alpha_hosting_pack/` plus `scripts/generate_public_alpha_hosting_pack.py` that packages route inventory status, smoke evidence templates, operator signoff, blockers, and a supervised rehearsal runbook without deploying Eureka or adding Docker, nginx, systemd, cloud infrastructure, auth, HTTPS/TLS, rate limiting, production logging, process management, live crawling, or background workers
- first Rust Migration Skeleton and Parity Plan v0 seam under `crates/`, `docs/architecture/RUST_BACKEND_LANE.md`, and `tests/parity/` that records Rust as the later production backend lane while keeping Python authoritative and requiring seam-by-seam parity before replacement
- first Rust Parity Fixture Pack v0 seam under `tests/parity/golden/python_oracle/v0/` plus `scripts/generate_python_oracle_golden.py` that captures stable Python-oracle JSON outputs for source registry, query planner, resolution runs, local index, resolution memory, and archive-resolution evals without porting Rust behavior, replacing Python, or adding a Rust parity runner
- first Rust Source Registry Parity Candidate v0 seam under `crates/eureka-core/` that loads governed source inventory records, validates bounded source fields, detects duplicate source ids, and compares source-registry public envelopes to Python-oracle goldens without wiring Rust into Python runtime, web, CLI, HTTP API, workers, or production paths
- Rust Source Registry Parity Catch-up v0 under `crates/eureka-core/src/source_registry.rs`, `tests/parity/rust_source_registry_cases.json`, and `scripts/check_rust_source_registry_parity.py` that updates the isolated Rust source-registry candidate to the current nine-source Python oracle shape, including capability booleans, coverage metadata, connector mode, limitations, next coverage steps, and placeholder warnings, while keeping Python authoritative and Rust unwired
- first Rust Query Planner Parity Candidate v0 seam under `crates/eureka-core/`,
  `tests/parity/rust_query_planner_cases.json`, and
  `scripts/check_rust_query_planner_parity.py` that adds an isolated
  deterministic Rust planner model and rule set compared against expanded
  Python-oracle query-planner goldens without wiring Rust into Python runtime,
  web, CLI, HTTP API, workers, public-alpha paths, or production behavior
- first Search Usefulness Audit v0 seam under `evals/search_usefulness/`,
  `runtime/engine/evals/search_usefulness_runner.py`, and
  `scripts/run_search_usefulness_audit.py` that runs a broad 64-query
  archive-resolution-style audit through the current bounded planner, local
  index/search, and absence path, marks external Google and Internet Archive
  baselines as pending manual observations, and aggregates future-work labels
  without scraping external systems or adding new retrieval semantics
- first Comprehensive Test/Eval Operating Layer and Repo Audit v0 seam under
  `control/inventory/tests/`, `control/audits/`,
  `docs/operations/TEST_AND_EVAL_LANES.md`, and `.aide/tasks/` that records
  reusable verification lanes, structured audit finding schemas, a dated
  audit pack, hard-test proposals, and backlog recommendations without adding
  product runtime behavior or production-readiness claims
- first Hard Test Pack v0 seam under `tests/hardening/` and
  `docs/operations/HARD_TEST_PACK.md` that turns the highest-risk audit
  findings into enforceable regression guards for eval hardness, external
  baseline honesty, public-alpha path safety, route/docs/README drift,
  Python-oracle golden drift, Rust parity structure, source placeholder
  honesty, resolution-memory path/privacy scope, and AIDE/test registry
  consistency without adding product runtime behavior
- first Search Usefulness Backlog Triage v0 pack under
  `control/backlog/search_usefulness_triage/` that selects
  old-platform-compatible software search as the primary usefulness wedge,
  member-level discovery inside bundles as the secondary wedge, and a staged
  usefulness backlog without changing runtime behavior or fabricating external
  baselines
- first Search Usefulness Audit Delta v0 pack under
  `control/audits/search-usefulness-delta-v0/` that records the measured
  aggregate delta after source coverage, old-platform planning, member records,
  result lanes/user-cost, and compatibility evidence, using a historical
  reported baseline plus current local audit output without changing retrieval
  behavior or recording external baseline observations
- first Real Source Coverage Pack v0 seam under
  `runtime/connectors/internet_archive_recorded/`,
  `runtime/connectors/local_bundle_fixtures/`, and
  `control/inventory/sources/` that adds tiny committed Internet Archive-like
  metadata/file-list fixtures plus local bundle ZIP fixtures for
  old-platform-compatible software and member-level discovery probes without
  live Internet Archive API calls, scraping, crawling, broad source federation,
  arbitrary local filesystem ingestion, or production source claims
- first Old-Platform Software Planner Pack v0 seam under
  `runtime/engine/query_planner/` that adds deterministic OS/platform aliases,
  platform-as-constraint handling, app-vs-OS-media suppression hints,
  latest-compatible release intent, driver/hardware/OS intent, vague identity
  uncertainty, documentation intent, and member-discovery hints without adding
  ranking, fuzzy/vector retrieval, LLM planning, live source behavior, new
  connectors, or planner-owned result routing
- first Member-Level Synthetic Records v0 seam under
  `runtime/engine/synthetic_records/` that derives deterministic
  `member:sha256:<digest>` records from bounded local bundle fixtures, preserves
  parent target refs, source provenance, member paths, evidence summaries, and
  action hints, and projects those records through exact resolution, search,
  local index, CLI, web, and local HTTP API paths without adding broad archive
  extraction, arbitrary local filesystem ingestion, ranking, live source
  behavior, or new connectors
- first Result Lanes + User-Cost Ranking v0 seam under
  `runtime/engine/ranking/` that assigns deterministic result lanes and
  user-cost explanations to current result records, projects those annotations
  through search, exact resolution, local index, CLI, web, local HTTP API, and
  eval summaries, and explains member-vs-parent usefulness without adding
  fuzzy/vector retrieval, LLM scoring, live source behavior, production ranking,
  or new connectors
- first Compatibility Evidence Pack v0 seam under
  `runtime/engine/compatibility/` that derives compact source-backed
  compatibility evidence records from committed fixture metadata, member paths,
  README text, and compatibility notes, projects those records through search,
  exact resolution, local index, compatibility, CLI, web, local HTTP API, and
  eval summaries, and preserves unknown compatibility without adding a
  compatibility oracle, installer execution, live source behavior, scraping,
  fuzzy/vector retrieval, LLM behavior, Rust behavior, or new connectors
- first Old-Platform Source Coverage Expansion v0 seam under
  `runtime/connectors/internet_archive_recorded/` and
  `runtime/connectors/local_bundle_fixtures/` that expands committed
  Internet-Archive-shaped and local bundle fixtures for Windows 7/XP/2000/98
  utility, browser-note, registry-repair, and driver/support-media cases,
  improving local audit partials while adding no live Internet Archive calls,
  scraping, crawling, broad source federation, arbitrary local filesystem
  ingestion, real binaries, or production source claims
- first Search Usefulness Audit Delta v1 pack under
  `control/audits/search-usefulness-delta-v1/` that records the measured
  movement after old-platform source expansion, including `partial +15`,
  `source_gap -13`, `capability_gap -2`, and archive evals at
  `capability_gap=1` plus `not_satisfied=5`, while changing no retrieval
  behavior and recording no external baseline observations
- first Hard Eval Satisfaction Pack v0 under
  `control/audits/hard-eval-satisfaction-v0/` plus structured eval-runner
  evidence mapping that moves archive evals to `capability_gap=1` and
  `partial=5` without weakening hard tasks, changing task definitions, or
  fabricating source/external evidence
- first Old-Platform Result Refinement Pack v0 under
  `control/audits/old-platform-result-refinement-v0/` plus deterministic
  archive-eval primary-candidate shape, expected-lane, and bad-result checks
  that move archive evals to `capability_gap=1`, `partial=4`, and
  `satisfied=1` without weakening hard tasks, adding retrieval behavior, or
  fabricating source/external evidence
- first More Source Coverage Expansion v1 pack under
  `control/audits/more-source-coverage-expansion-v1/` plus targeted tiny
  recorded/fixture-only Firefox XP, blue FTP-client XP, Windows 98 registry
  repair, and Windows 7 utility/app evidence that moves current archive evals
  to `capability_gap=1` and `satisfied=5` without live source behavior,
  scraping, arbitrary local filesystem ingestion, real binaries, weakened hard
  evals, or external baseline claims
- first Article/Scan Fixture Pack v0 under
  `control/audits/article-scan-fixture-pack-v0/` plus a tiny
  synthetic/recorded article-scan fixture source with parent issue lineage,
  page-range metadata, and OCR-like fixture text that moves current archive
  evals to `satisfied=6` without live source behavior, scraping, OCR engines,
  PDF/image parsing, real magazine scans, copyrighted article text, weakened
  hard evals, or external baseline claims
- first Manual External Baseline Observation Pack v0 under
  `evals/search_usefulness/external_baselines/` plus stdlib validation and
  status reporting scripts that define manual-only Google web search, Internet
  Archive metadata search, and Internet Archive full-text/OCR search
  observations, seed 192 pending slots across 64 queries and three systems, and
  prevent pending slots from being treated as observed baselines without
  scraping, automated external querying, live APIs, or fabricated results
- first Manual Observation Batch 0 under
  `evals/search_usefulness/external_baselines/batches/batch_0/` that selects
  13 high-value query IDs and creates 39 batch-scoped pending slots across
  Google web search, Internet Archive metadata search, and Internet Archive
  full-text/OCR search, with validation and reporting support but no observed
  external results, scraping, automated querying, live APIs, or fabricated
  baselines
- first Manual Observation Entry Helper v0 under `scripts/` that lists manual
  observation slots, creates one fillable pending observation file from a
  batch slot, validates a single file or the full observation area, and reports
  Batch 0 progress without performing observations, opening browsers, fetching
  URLs, scraping, automated external querying, or fabricating baselines
- first LIVE_ALPHA_00 Static Public Site Pack under `site/dist/` plus
  `scripts/validate_public_static_site.py` that records a no-JS static public
  site source tree with status, source matrix, eval/audit state, demo queries,
  limitations, roadmap, and local quickstart pages for later hosting review
  without deploying Eureka, adding backend hosting, adding live source probes,
  scraping external systems, or making production-readiness claims
- first Public Alpha Rehearsal Evidence v0 under
  `docs/operations/public_alpha_rehearsal_evidence_v0/` plus
  `scripts/generate_public_alpha_rehearsal_evidence.py` that packages static
  validator status, public-alpha smoke status, route inventory counts,
  eval/audit counts, external-baseline pending status, blockers, next
  deployment requirements, and an unsigned signoff template without deploying
  Eureka, approving production, adding live probes, or recording external
  baseline observations
- first LIVE_ALPHA_01 Production Public-Alpha Wrapper under
  `scripts/run_public_alpha_server.py` and
  `surfaces/web/server/public_alpha_config.py` that gives the stdlib web/API
  backend an explicit public-alpha entrypoint, safe config defaults, nonlocal
  bind guard, closed live-probe/live-IA gates, disabled local path/download/user
  storage controls, and JSON-safe capability reporting without deploying
  Eureka, adding hosting provider files, enabling live probes, adding auth/TLS,
  adding rate limiting, or approving production
- first Public Publication Plane Contracts v0 under
  `control/inventory/publication/`, `docs/architecture/PUBLICATION_PLANE.md`,
  `docs/reference/`, `scripts/validate_publication_inventory.py`, and
  publication inventory tests that govern public routes, route stability,
  public status vocabulary, client profiles, public data files, static export
  shape, base-path portability, deployment target semantics, redirect policy,
  and public claim traceability before GitHub Pages deployment or static
  generation without adding deployment workflows, DNS, provider config, a site
  generator, live backend behavior, live probes, or external observations
- first GitHub Pages Deployment Enablement v0 under
  `.github/workflows/pages.yml`, `docs/operations/GITHUB_PAGES_DEPLOYMENT.md`,
  `scripts/check_github_pages_static_artifact.py`, and workflow/artifact safety
  tests that validate the publication inventory and `site/dist/` before
  uploading only the static artifact to GitHub Pages, without deploying the
  Python backend, enabling live probes, adding a custom domain, adding a
  generator, adding secrets, or claiming deployment success without GitHub
  Actions evidence
- first Static Site Generation Migration v0 under `site/`, adding a
  stdlib-only source tree, templates, page JSON, `site/build.py`,
  `site/validate.py`, generated `site/dist/`, and generator tests that render
  the current no-JS static pages into the GitHub Pages artifact without
  Node/npm, a frontend framework, live backend behavior, live probes, or
  production claims
- first Generated Public Data Summaries v0 under `site/dist/data/` and
  `scripts/generate_public_data_summaries.py`, adding
  deterministic static JSON summaries for page, source, eval, route, and build
  state from governed repo inputs without adding a live API, deployment
  behavior, live probes, external observations, Node/npm, or production API
  stability claims
- first Lite/Text/Files Seed Surfaces v0 under `site/dist/lite/`,
  `site/dist/text/`, `site/dist/files/`, and
  `scripts/generate_compatibility_surfaces.py`, adding
  static old-browser/text/file-tree seed surfaces with checksums and no live
  search, executable downloads, snapshots, relay/native runtime behavior,
  backend deployment, live probes, or production support claims
- first Static Resolver Demo Snapshots v0 under `site/dist/demo/` and
  `scripts/generate_static_resolver_demos.py`, adding static fixture-backed
  demo snapshots for query planning, member results, compatibility evidence,
  absence, comparison, source detail, article/scan results, and eval summaries
  without live search, live API semantics, backend hosting, external
  observations, or production claims
- first Custom Domain / Alternate Host Readiness v0 under
  `control/inventory/publication/domain_plan.json`,
  `control/inventory/publication/static_hosting_targets.json`,
  `docs/operations/CUSTOM_DOMAIN_AND_ALTERNATE_HOST_READINESS.md`,
  `docs/reference/BASE_PATH_PORTABILITY.md`, and
  `scripts/validate_static_host_readiness.py`, adding provider-neutral static
  host readiness checks without DNS, CNAME, alternate-host deployment,
  provider config, backend hosting, live probes, or production claims
- first Live Backend Handoff Contract v0 under
  `control/inventory/publication/live_backend_handoff.json`,
  `control/inventory/publication/live_backend_routes.json`,
  `control/inventory/publication/surface_capabilities.json`,
  `docs/architecture/LIVE_BACKEND_HANDOFF.md`, and
  `scripts/validate_live_backend_handoff.py`, adding contract-only `/api/v1`
  reservations, disabled live capability flags, and error-envelope
  expectations without hosting a backend, making `/api/v1` live, enabling live
  probes, or creating production API guarantees
- first Live Probe Gateway Contract v0 under
  `control/inventory/publication/live_probe_gateway.json`,
  `docs/reference/LIVE_PROBE_GATEWAY_CONTRACT.md`,
  `docs/architecture/LIVE_PROBE_GATEWAY.md`,
  `docs/operations/LIVE_PROBE_POLICY.md`, and
  `scripts/validate_live_probe_gateway.py`, adding disabled-by-default
  source-probe policy, per-source caps, cache/evidence requirements, operator
  gates, and candidate-source posture without implementing probes, calling
  external sources, fetching URLs, scraping, crawling, enabling downloads, or
  turning Google into a live probe source
- runtime component layout for engine, gateway, and connectors, including explicit engine interface boundaries
- surface layout for web and native
- component-local and root integration tests for the executable slices

## Accepted Doctrine

The repo now accepts doctrine that:

- Eureka is a temporal object resolver rather than flat archive search
- search is an investigation, not only a query
- the smallest actionable unit should outrank a bulky parent container when the
  evidence supports it
- deterministic identity outranks fuzzy similarity
- user strategy may shape recommendations but not objective truth
- AI is optional, evidence-bounded, and non-authoritative
- the backend should remain useful without LLMs
- eval-governed improvement is required for future search expansion

Accepted doctrine lives primarily under:

- `docs/vision/`
- `docs/architecture/`
- `docs/DECISIONS.md`

## Research Still Separate

The repo still keeps speculative or not-yet-accepted material under:

- `control/research/`

In particular, the temporal-object-resolution research note remains governed
research rather than a claim that the current repo already implements shared
evidence services, streaming run phases, hosted operation, or production
subsystem choices.

## Next Implementation Milestone

The next implementation milestone is:

> Public Search Static Handoff v0

Source Registry v0, Resolution Run Model v0, Query Planner v0, Local Index v0,
Local Worker and Task Model v0, Resolution Memory v0, and Archive Resolution
Eval Runner v0, Public Alpha Safe Mode v0, and Public Alpha Deployment
Readiness Review, Public Alpha Hosting Pack v0, Rust Migration Skeleton and
Parity Plan v0, Rust Parity Fixture Pack v0, Rust Source Registry Parity
Candidate v0, Search Usefulness Audit v0, Search Usefulness Backlog Triage v0,
and Comprehensive Test/Eval Operating Layer and Repo Audit v0, plus Hard Test
Pack v0, Source Coverage and Capability Model v0, Real Source Coverage Pack
v0, Old-Platform Software Planner Pack v0, Member-Level Synthetic Records v0,
Result Lanes + User-Cost Ranking v0, Compatibility Evidence Pack v0,
Search Usefulness Audit Delta v0, and Old-Platform Source Coverage Expansion
v0, Search Usefulness Audit Delta v1, Hard Eval Satisfaction Pack v0,
Old-Platform Result Refinement Pack v0, More Source Coverage Expansion v1,
Article/Scan Fixture Pack v0, Manual External Baseline Observation Pack v0,
Manual Observation Batch 0, Manual Observation Entry Helper v0,
LIVE_ALPHA_00 Static Public Site Pack, Public Alpha Rehearsal Evidence v0,
LIVE_ALPHA_01 Production Public-Alpha Wrapper, Public Publication Plane
Contracts v0, GitHub Pages Deployment Enablement v0, Static Site
Generation Migration v0, Generated Public Data Summaries v0,
Lite/Text/Files Seed Surfaces v0, Static Resolver Demo Snapshots v0,
Custom Domain / Alternate Host Readiness v0, Live Backend Handoff Contract
v0, Live Probe Gateway Contract v0, Rust Query Planner Parity Candidate v0,
Compatibility Surface Strategy v0, Signed Snapshot Format v0, Signed Snapshot
Consumer Contract v0, Native Client Contract v0, Native Action / Download /
Install Policy v0, Native Local Cache / Privacy Policy v0, Native Client
Project Readiness Review v0, Relay Surface Design v0, Rust Source Registry
Parity Catch-up v0, and Rust Local Index Parity Planning v0
are
now implemented as the first
inventory-backed source-control plane, synchronous durable investigation
envelope, deterministic raw-query compiler, durable local search substrate,
synchronous local execution substrate, explicit local reusable investigation
memory layer, executable eval guardrail, constrained public-demo posture, and
auditable public-alpha route/smoke checklist plus supervised rehearsal evidence
packet, committed Python-oracle golden fixture pack, isolated Rust
source-registry parity seam, updated current-shape Rust source-registry
parity catch-up seam, isolated Rust query-planner parity seam, broad usefulness-audit backlog generator, and
repo-native test/eval governance, executable hardening guard layer,
evidence-backed usefulness backlog, explicit source capability/coverage
metadata layer, first recorded source-coverage fixture pack, deterministic
old-platform planner interpretation layer, first bounded member-level synthetic
target-ref and parent-lineage layer, first deterministic result-lane and
user-cost explanation layer, first source-backed compatibility evidence layer,
first measured usefulness-delta reporting pack, first expanded old-platform
fixture coverage pack, second measured usefulness-delta reporting pack, and
first hard-eval satisfaction mapping/report pack, plus first strict
old-platform hard-eval result-shape refinement pack, targeted old-platform
fixture evidence expansion pack, bounded article/page/scan fixture pack,
manual external-baseline observation protocol, first prioritized pending
manual observation batch plus local human-entry helper tooling, first static
public-facing documentation pack for live-alpha review, and first supervised
local/static public-alpha rehearsal evidence pack, plus the first explicit
public-alpha process wrapper and config guard, and the first publication-plane
contract/inventory layer, plus the first static-only GitHub Pages workflow and
artifact-readiness validation layer, plus the first stdlib static-site
generation source tree and generated-output validation layer, plus the first
deterministic public data summary layer under `site/dist/data/` and
`site/dist/data/`, plus the first static compatibility seed surfaces under
`site/dist/lite/`, `site/dist/text/`, and `site/dist/files/`.
The static demo snapshot layer under `site/dist/demo/` shows representative
fixture-backed resolver examples without adding live search or API behavior.
The static host readiness layer records custom-domain and alternate-host
prerequisites without adding DNS, CNAME, provider config, alternate-host
deployment, backend hosting, or live probes.
The live backend handoff layer reserves `/api/v1` and disabled capability flags
without adding route handlers, backend hosting, live probes, CORS/auth/rate
limit policy, or production API guarantees.
The live probe gateway contract records disabled-by-default source policy,
candidate source caps, cache/evidence expectations, and operator gates without
adding adapters, network calls, downloads, scraping, crawling, or live source
behavior.
The Rust query-planner parity candidate matches the expanded Python-oracle
query-planner fixture map as an isolated Rust seam only; it does not replace
the Python planner or wire Rust into web, CLI, HTTP API, workers, public-alpha,
or production paths.
Rust Source Registry Parity Catch-up v0 updates the isolated Rust
source-registry candidate to the current nine-source Python source inventory
shape, including capability booleans, coverage metadata, connector mode,
limitations, next coverage steps, and placeholder warnings; Python remains the
oracle and Rust remains unwired from runtime and surfaces.
Rust Local Index Parity Planning v0 records the future Rust local-index parity
lane with a plan, fixture map, acceptance-report schema, validator, and tests.
It is planning only: no Rust local-index implementation, SQLite/indexing
behavior, Python local-index replacement, or runtime/surface wiring is added.
The compatibility surface strategy records current and future surface families,
old-client degradation, native-client prerequisites, snapshot readiness, relay
readiness, and route/capability matrices without adding runtime behavior.
Signed Snapshot Format v0 records the static/offline snapshot contract and
repo-local seed example under `snapshots/examples/static_snapshot_v0/` with
checksums and signature-placeholder docs only; it adds no real signing keys,
production signatures, executable downloads, public `/snapshots/` route, relay
service, native-client runtime, live backend behavior, or live probes.
Signed Snapshot Consumer Contract v0 defines future snapshot read order,
checksum-validation semantics, v0 signature-placeholder handling, missing
optional file behavior, and consumer profiles for file-tree, text, lite HTML,
relay, native, and audit consumers. It is contract/design only and adds no
snapshot reader runtime, relay runtime, native client, production signing, real
signing keys, executable downloads, live backend behavior, or live probes.
Native Client Contract v0 defines future Windows/macOS/native client inputs,
lane policy, readiness checklist, CLI boundary, snapshot/public-data
dependencies, live-backend/relay/Rust constraints, and install/download
prohibitions. It is contract/design only and adds no Visual Studio/Xcode
projects, native GUI, FFI, native snapshot reader runtime, relay sidecar,
installer automation, package-manager behavior, executable download/execution
automation, live probes, or Rust runtime wiring.
Relay Surface Design v0 records future local/LAN relay policy, protocol
candidates, security/privacy defaults, and an unsigned operator checklist as
design governance only; it adds no relay runtime, sockets, FTP, SMB, WebDAV,
Gopher, protocol proxy, private data exposure, write/admin routes, live-probe
passthrough, native sidecar, or production relay claim.
Native Action / Download / Install Policy v0 records future inspect, preview,
export, download, mirror, install handoff, package-manager handoff, execute,
restore, uninstall, rollback, malware-scan, and rights/access gates as policy
only. It adds no downloads, installers, package-manager integration, malware
scanning, rights clearance, native clients, relay runtime, or executable trust
claims.
Native Local Cache / Privacy Policy v0 records future local/public/private
cache, private-data, local path, telemetry/logging, diagnostics, credentials,
deletion/export/reset, portable-mode, snapshot, relay, and public-alpha privacy
gates as policy only. It adds no cache runtime, private file ingestion, local
archive scanning, telemetry, accounts, cloud sync, uploads, native clients, or
relay runtime.
Native Client Project Readiness Review v0 records an evidence-only audit pack
under `control/audits/native-client-project-readiness-v0/`. Its decision is
`ready_for_minimal_project_skeleton_after_human_approval` for the
`windows_7_x64_winforms_net48` lane only. It adds no Visual Studio/Xcode
project, native app source tree, GUI behavior, FFI, cache runtime, downloads,
installers, relay runtime, live probes, or runtime wiring.
Windows 7 WinForms Native Skeleton Planning v0 records a planning pack under
`control/audits/windows-7-winforms-native-skeleton-planning-v0/`. It proposes
`clients/windows/winforms-net48/` and
`Eureka.Clients.Windows.WinForms`, defines Windows host, Visual Studio 2022,
.NET Framework 4.8, x64, and Windows 7 SP1+ build-host requirements, and keeps
the future skeleton read-only/static-data/snapshot-demo only. It adds no
`clients/`, Visual Studio solution, `.csproj`, C# source, GUI behavior, FFI,
cache runtime, downloads, installers, telemetry, relay runtime, live probes, or
runtime wiring. Implementation remains blocked until explicit human approval.
Relay Prototype Planning v0 records a planning pack under
`control/audits/relay-prototype-planning-v0/`. It selects a future
`local_static_http_relay_prototype` as the first relay candidate with
localhost-only, read-only, static public-data/seed-snapshot scope. It adds no
relay server, socket listener, local HTTP relay, FTP, SMB, AFP, NFS, WebDAV,
Gopher, TLS/protocol translation, native sidecar, snapshot mount, private file
serving, live backend proxy, live source probe, write/admin route, telemetry,
download/install behavior, or old-client relay support claim.
Full Project State Audit v0 records a repo-native full checkpoint under
`control/audits/full-project-state-audit-v0/`. It captures current milestone
classifications, broad verification, eval/search status, external-baseline
pending status, publication/static/public-alpha status, source/retrieval state,
snapshot/relay/native/Rust status, risks, blockers, human-operated work,
explicit deferrals, and next milestone recommendations. It is audit/reporting
only and adds no product runtime behavior.
Public Data Contract Stability Review v0 records a field-level stability review
under `control/audits/public-data-contract-stability-review-v0/` and
`docs/reference/PUBLIC_DATA_STABILITY_POLICY.md`. It classifies generated
public JSON files and fields as `stable_draft`, `experimental`, `volatile`,
`internal`, `deprecated`, or `future` so future snapshot, relay, native, and
static clients know what they may consume. It does not change runtime behavior,
generated public data output, live APIs, deployment behavior, relay/native
runtime, or production API stability.
Generated Artifact Drift Guard v0 records generated and generated-like artifact
ownership under `control/inventory/generated_artifacts/`, adds
`scripts/check_generated_artifact_drift.py`, and records an audit pack under
`control/audits/generated-artifact-drift-guard-v0/`. It checks public data,
compatibility surfaces, static demos, snapshot seed files, `site/dist`, Python
oracle goldens, public-alpha rehearsal evidence, publication inventories, test
registry metadata, and AIDE metadata without regenerating artifacts by default,
changing runtime behavior, deploying, calling external services, or opening
network sockets.
Repository Shape Consolidation v0 promotes `site/dist/` as the single generated
static deployment artifact, removes the active legacy static artifact path,
confirms `external/` as the outside-reference root, and adds layout validation
without public search runtime, backend hosting, live probes, relay runtime,
native clients, or production claims.
Static Artifact Promotion Review v0 conditionally promotes `site/dist/` as the
active repo-local static publication artifact, records local validation and
workflow/generated-artifact/static-safety evidence under
`control/audits/static-artifact-promotion-review-v0/`.
GitHub Pages Run Evidence Review v0 records passive current-head Actions
evidence under `control/audits/github-pages-run-evidence-v0/`: the Pages run
passed the static build/validation steps, then failed at Pages configuration
before artifact upload or deployment because the repository Pages site was not
found/enabled for GitHub Actions. It adds no deployment behavior, backend
hosting, live search, live probes, or production claim.
Public Search API Contract v0 defines governed public-search request,
response, error, and route envelopes under `contracts/api/`,
`control/inventory/publication/public_search_routes.json`, and
`docs/reference/PUBLIC_SEARCH_API_CONTRACT.md`. The first allowed mode is
`local_index_only`. Local Public Search Runtime v0 implements `/search`,
`/api/v1/search`, `/api/v1/query-plan`, `/api/v1/status`, `/api/v1/sources`,
and `/api/v1/source/{source_id}` as local/prototype backend routes only. This
adds no hosted deployment, static search handoff page, live probes, crawling,
external search automation, arbitrary URL fetch, downloads, installs, uploads,
local path search, accounts, telemetry, or production API stability claim.
Public Search Result Card Contract v0 defines the contract-only future result
card under `contracts/api/search_result_card.v0.json`,
`contracts/api/examples/`, `docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`,
and `control/audits/public-search-result-card-contract-v0/`. It records lanes,
user-cost, source, identity, evidence, compatibility, member/representation
context, action gating, rights/risk caveats, warnings, limitations, and gaps
without making public search live, adding runtime routes, enabling downloads,
installers, execution, uploads, live probes, malware-safety claims,
rights-clearance claims, or production ranking guarantees.
Public Search Safety / Abuse Guard v0 defines guardrails under
`control/inventory/publication/public_search_safety.json`,
`docs/operations/PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md`, and
`docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md`. It fixes
`local_index_only` as the only allowed v0 mode, bounds query/result/time
behavior, forbids URL/local path/credential/download/install/upload parameters,
maps disallowed behavior to the P26 error envelope, keeps telemetry/logging
runtime off, and lists future operator controls. It adds no public search
runtime, rate-limit middleware, auth/accounts, telemetry runtime, hosted
backend, live probes, downloads, uploads, local path search, arbitrary URL
fetch, static search handoff, or production safety claim.
The backend program should continue moving from bounded seam proof toward
operational backend infrastructure in this order:

1. Public Search Static Handoff v0
2. Public Search Rehearsal v0
3. Search Usefulness Source Expansion v2, fixture-only
4. Source Pack Contract v0
5. Evidence Pack Contract v0
6. Index Pack Contract v0
7. Contribution Pack Contract v0
8. Master Index Review Queue Contract v0
9. AI Provider Contract v0
10. GitHub Pages Workflow Repair v0 as an operator/Pages follow-up before any
   deployment-success claim
11. Rust Local Index Parity Candidate v0 only after planning review and Cargo
   availability expectations are explicit
12. Relay Prototype Implementation v0, only after explicit human approval and
   limited to the approved localhost-only/read-only/static relay scope
13. Windows 7 WinForms Native Skeleton Implementation v0, only after explicit
   human approval and limited to the approved read-only static-data/snapshot-demo
   skeleton scope
14. Manual Observation Batch 0 Execution (human-operated parallel work)
15. Internet Archive Live Probe v0 only after explicit human approval and
   separate implementation review

## Deferred Priorities

These are intentionally not the next milestone:

- Visual Studio app work
- Xcode app work
- full native app work
- public hosted alpha
- Rust production rewrite
- Rust behavior ports before matching Python-oracle parity fixtures
- broad live federation
- installer or restore automation

## Intentionally Deferred

- finalized archive schema meaning
- broader automated dependency-policy enforcement tooling beyond the current narrow Python import checker
- mature gateway API semantics, wider public read coverage, and durable submit versus read guarantees
- final HTTP API route naming, auth, HTTPS/TLS, deployment topology, and multi-user semantics beyond the current local bootstrap slice
- final action semantics, installer behavior, download handling, restore/import handling, and durable manifest, bundle, inspection, or store guarantees
- final global identity semantics, cross-source merge behavior, and any durable resource-identity guarantees beyond the current bootstrap seam
- final provenance graph semantics, trust scoring, and broader evidence or claim ontology work beyond the current bounded summary seam
- final comparison semantics, merge behavior, and truth-selection behavior beyond the current bounded disagreement seam
- final object, subject, and state identity plus ordering semantics beyond the current bounded timeline seam
- final diagnostic and absence-reasoning semantics beyond the current bounded miss-explanation seam
- final representation, access-path, download, install, import, and restore semantics beyond the current bounded representation seam
- final compatibility, host-profile, installer, and runtime-routing semantics beyond the current bounded compatibility seam
- final action-routing, representation-selection, handoff, acquisition, decomposition, member-readback, strategy, execution, installer, workflow-policy, extraction, and personalization semantics beyond the current bounded recommendation seams
- mature search semantics, ranking, and broader retrieval architecture
- real web application structure, browser-side behavior, authentication, and deployment assumptions
- broader live external-source federation, live GitHub acquisition, ranking, retrieval, and broader provenance or trust semantics
- persistence beyond the local bootstrap filesystem store, background workers, and async orchestration
- richer web routing and page structure beyond the bootstrap compatibility-first workbench, search, subject-state, representations, manifest-export, bundle-export, stored-export, bundle-inspection, and local HTTP API slices, plus native runtime behavior
- final native CLI, TUI, GUI, and offline mode decisions
- serious Visual Studio/Xcode/native app shell work before backend infrastructure is stronger
- Rust production implementation work before parity planning and backend-roadmap prerequisites are met
- release automation and packaging implementation
