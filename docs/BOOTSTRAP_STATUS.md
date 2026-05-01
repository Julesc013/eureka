# Bootstrap Status

Current status: foundational scaffold plus sixty-seven executable local deterministic Python thin slices, a placeholder Rust migration skeleton, the first Python-oracle golden fixture pack, the first isolated Rust source-registry parity candidate, Rust Source Registry Parity Catch-up v0, the first isolated Rust query-planner parity candidate, Rust Local Index Parity Planning v0, Search Usefulness Audit v0, Search Usefulness Backlog Triage v0, Search Usefulness Audit Delta v0, Search Usefulness Audit Delta v1, Hard Eval Satisfaction Pack v0, Old-Platform Result Refinement Pack v0, More Source Coverage Expansion v1, Article/Scan Fixture Pack v0, Manual External Baseline Observation Pack v0, Manual Observation Batch 0, Manual Observation Entry Helper v0, LIVE_ALPHA_00 Static Public Site Pack, Public Alpha Rehearsal Evidence v0, LIVE_ALPHA_01 Production Public-Alpha Wrapper, Public Publication Plane Contracts v0, GitHub Pages Deployment Enablement v0, Static Site Generation Migration v0, Generated Public Data Summaries v0, Lite/Text/Files Seed Surfaces v0, Static Resolver Demo Snapshots v0, Custom Domain / Alternate Host Readiness v0, Live Backend Handoff Contract v0, Live Probe Gateway Contract v0, Public Search API Contract v0, Public Search Result Card Contract v0, Public Search Safety / Abuse Guard v0, Local Public Search Runtime v0, Public Search Static Handoff v0, Compatibility Surface Strategy v0, Signed Snapshot Format v0, Signed Snapshot Consumer Contract v0, Native Client Contract v0, Native Action / Download / Install Policy v0, Native Local Cache / Privacy Policy v0, Native Client Project Readiness Review v0, Windows 7 WinForms Native Skeleton Planning v0, Post-Queue State Checkpoint v0, Relay Surface Design v0, Relay Prototype Planning v0, Full Project State Audit v0, Public Data Contract Stability Review v0, Generated Artifact Drift Guard v0, Repository Shape Consolidation v0, Static Artifact Promotion Review v0, GitHub Pages Run Evidence Review v0, Comprehensive Test/Eval Operating Layer and Repo Audit v0, Hard Test Pack v0, and AI-Assisted Evidence Drafting Plan v0, with draft contracts and concrete dependency boundary paths in place while broader product implementation remains intentionally deferred.

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
- Rust Source Registry Parity Catch-up v0 under `crates/eureka-core/src/source_registry.rs`, `tests/parity/rust_source_registry_cases.json`, and `scripts/check_rust_source_registry_parity.py` that updates the isolated Rust source-registry candidate to the current Python oracle shape, including capability booleans, coverage metadata, connector mode, limitations, next coverage steps, and placeholder warnings, while keeping Python authoritative and Rust unwired
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

## Latest Implementation Milestone

The latest implementation milestone is:

> Master Index Review Queue Contract v0

Search Usefulness Source Expansion v2 is now implemented as fixture-only source
coverage under `runtime/connectors/source_expansion_recorded/`,
`control/inventory/sources/`, and
`control/audits/search-usefulness-source-expansion-v2/`. It adds six recorded
fixture source families and 15 tiny metadata records, moving the current audit
from covered=5/partial=22/source_gap=26/capability_gap=9/unknown=2 to
covered=5/partial=40/source_gap=10/capability_gap=7/unknown=2. It adds no live
source calls, scraping, crawling, external observations, real binaries,
downloads, installs, uploads, local path search, telemetry, hosted search,
malware-safety claim, rights-clearance claim, or production relevance claim.
Search Usefulness Delta v2 records the measured effect under
`control/audits/search-usefulness-delta-v2/`, with the P32 report as the
machine-derived baseline. It records exact status-count deltas, selected query
movement, current failure modes, source-family impact, public-search smoke
status, hard-eval status, external-baseline pending status, and remaining gaps.
It adds no source/runtime behavior and records no external observations.
Source Pack Contract v0 is now implemented as contract/validation/example-only
work under `contracts/packs/`, `docs/reference/SOURCE_PACK_CONTRACT.md`,
`docs/reference/PACK_LIFECYCLE.md`,
`examples/source_packs/minimal_recorded_source_pack_v0/`, and
`control/audits/source-pack-contract-v0/`. It defines the governed
`SOURCE_PACK.json` manifest shape, source-record alignment, public-safe
evidence inputs, fixture policy, privacy/rights posture, lifecycle status, and
checksum validation. It adds no import, indexing, upload, live connector,
executable plugin, hosted submission, master-index acceptance, download,
installer, or production extension behavior.
Evidence Pack Contract v0 is now implemented as contract/validation/example-only
work under `contracts/packs/evidence_pack.v0.json`,
`docs/reference/EVIDENCE_PACK_CONTRACT.md`,
`examples/evidence_packs/minimal_evidence_pack_v0/`, and
`control/audits/evidence-pack-contract-v0/`. It defines the governed
`EVIDENCE_PACK.json` manifest shape, evidence kinds, claim types, source
reference locators, snippet limits, privacy/rights posture, and checksum
validation. It adds no import, indexing, upload, live connector, executable
plugin, hosted submission, master-index acceptance, canonical truth selection,
download, installer, or production extension behavior.
Index Pack Contract v0 is now implemented as contract/validation/example-only
work under `contracts/packs/index_pack.v0.json`,
`docs/reference/INDEX_PACK_CONTRACT.md`,
`examples/index_packs/minimal_index_pack_v0/`, and
`control/audits/index-pack-contract-v0/`. It defines the governed
`INDEX_PACK.json` manifest shape, summary-only index-build metadata, source
coverage, field coverage, query examples, public-safe record summaries,
privacy/rights posture, and checksum validation. It adds no import, merge,
upload, raw SQLite or local-cache export, live connector, executable plugin,
hosted ingestion, master-index acceptance, canonical truth selection, download,
installer, or production extension behavior.
Contribution Pack Contract v0 is now implemented as contract/validation/example-only
work under `contracts/packs/contribution_pack.v0.json`,
`docs/reference/CONTRIBUTION_PACK_CONTRACT.md`,
`examples/contribution_packs/minimal_contribution_pack_v0/`, and
`control/audits/contribution-pack-contract-v0/`. It defines the governed
`CONTRIBUTION_PACK.json` manifest shape, review-candidate contribution items,
source/evidence/index pack references, manual-observation placeholders,
metadata correction and alias/compatibility/absence/result-feedback vocabulary,
privacy/rights posture, review requirements, and checksum validation. It adds
no upload, import, moderation UI, accounts, identity, master-index review queue
runtime, automatic acceptance, live connector, executable plugin, hosted
ingestion, canonical truth selection, download, installer, or production
extension behavior.
Master Index Review Queue Contract v0 is now implemented as
contract/validation/example-only work under `contracts/master_index/`,
`docs/reference/MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md`,
`docs/architecture/MASTER_INDEX_REVIEW_QUEUE.md`,
`control/inventory/master_index/`,
`examples/master_index_review_queue/minimal_review_queue_v0/`, and
`control/audits/master-index-review-queue-contract-v0/`. It defines queue
manifests, review queue entries, review decisions, validation/review state
taxonomy, acceptance requirements, privacy/rights/risk/conflict review, and a
synthetic defer-decision example. It adds no queue runtime, uploads, imports,
moderation UI, accounts, hosted master index, master-index writes, automatic
acceptance, live connectors, rights-clearance claim, malware-safety claim,
canonical truth selection, or production extension behavior.
Source/Evidence/Index Pack Import Planning v0 is now implemented as
planning-only work under `control/audits/pack-import-planning-v0/`,
`docs/reference/PACK_IMPORT_PLANNING.md`,
`docs/architecture/PACK_IMPORT_PIPELINE.md`, and
`scripts/validate_pack_import_planning.py`. It defines validate-only as the
first future import mode, private local quarantine as the next mode, validation
pipeline requirements, staging/privacy/rights/risk rules, provenance rules,
and local search/master-index boundaries. It adds no import runtime, staging
directories, public search mutation, local index mutation, canonical source
registry mutation, uploads, hosted/master-index mutation, automatic acceptance,
live fetch, arbitrary directory scan, executable plugin behavior, or production
claim.
Pack Import Validator Aggregator v0 is now implemented as validate-only
reporting under `scripts/validate_pack_set.py`,
`control/inventory/packs/example_packs.json`,
`docs/operations/PACK_VALIDATION.md`, and
`control/audits/pack-import-validator-aggregator-v0/`. It validates all five
known source/evidence/index/contribution/master-index review queue examples
through one offline command and reports pass/fail/unavailable/unknown-type
status. It adds no import runtime, staging directories, local index mutation,
uploads, submissions, hosted/master-index mutation, automatic acceptance,
network calls, rights-clearance claim, malware-safety claim, canonical truth
claim, or production extension behavior.
AI Provider Contract v0 is now implemented as contract/validation/example-only
work under `contracts/ai/`, `control/inventory/ai_providers/`,
`examples/ai_providers/disabled_stub_provider_v0/`,
`docs/reference/AI_PROVIDER_CONTRACT.md`,
`docs/reference/TYPED_AI_OUTPUT_CONTRACT.md`,
`docs/architecture/AI_ASSISTANCE_BOUNDARY.md`, and
`control/audits/ai-provider-contract-v0/`. It defines disabled-by-default
provider manifests, task request contracts, typed output contracts, privacy,
credential, logging, cache, evidence-linking, and human-review policies. It
adds no model calls, API keys, credential storage, prompt logging runtime,
telemetry, AI provider runtime, public-search AI, AI evidence acceptance, local
index mutation, or master-index mutation.
Typed AI Output Validator v0 is now implemented as validation-only work under
`runtime/engine/ai/`, `scripts/validate_ai_output.py`,
`control/inventory/ai_providers/typed_output_examples.json`,
`docs/operations/AI_OUTPUT_VALIDATION.md`, and
`control/audits/typed-ai-output-validator-v0/`. It validates four synthetic
disabled-stub output examples and enforces required review, prohibited truth/
rights/malware/automatic-acceptance uses, provider-reference alignment,
generated-text limits, private-path rejection, and secret rejection without
model calls, provider runtime loading, API keys, telemetry, evidence import,
contribution import, local-index mutation, public-search AI, or master-index
mutation.
Pack Import Report Format v0 is now implemented as format/validation/example
work under `contracts/packs/pack_import_report.v0.json`,
`examples/import_reports/`, `scripts/validate_pack_import_report.py`,
`docs/reference/PACK_IMPORT_REPORT_FORMAT.md`, and
`control/audits/pack-import-report-format-v0/`. It records validate-only pack
results, issue summaries, privacy/rights/risk posture, provenance, next
actions, and hard false mutation-safety fields without implementing import,
staging, local index mutation, runtime mutation, uploads, network calls, model
calls, or master-index mutation.
Validate-Only Pack Import Tool v0 is now implemented under
`scripts/validate_only_pack_import.py`,
`docs/operations/VALIDATE_ONLY_PACK_IMPORT.md`, and
`control/audits/validate-only-pack-import-tool-v0/`. It validates explicit pack
roots or known examples, emits Pack Import Report v0, and does not import,
stage, index, upload, call networks, call models, mutate runtime state, mutate
public search, or mutate the master index.
Local Quarantine/Staging Model v0 is now implemented as planning/governance
under `control/inventory/local_state/`,
`docs/architecture/LOCAL_QUARANTINE_STAGING_MODEL.md`,
`docs/reference/LOCAL_STAGING_PATH_POLICY.md`,
`scripts/validate_local_quarantine_staging_model.py`, and
`control/audits/local-quarantine-staging-model-v0/`. No staging runtime exists,
no staged state is created, and future local state remains local_private by
default, ignored for development roots, resettable/deletable, and isolated
from public search and the master index.
Staging Report Path Contract v0 is now implemented as planning/governance
under `control/inventory/local_state/staging_report_path_contract.json`,
`docs/reference/STAGING_REPORT_PATH_CONTRACT.md`,
`docs/operations/LOCAL_REPORT_PATHS.md`,
`scripts/validate_staging_report_path_contract.py`, and
`control/audits/staging-report-path-contract-v0/`. Report output defaults to
stdout; file writes require explicit output paths; forbidden
public/runtime/canonical roots are blocked; private local paths require
redaction before public or committed reports. No report path runtime, staging
runtime, staged state, import behavior, local index mutation, public-search
mutation, upload, or master-index mutation is implemented.
Local Staging Manifest Format v0 is now implemented as contract/example/
validation-only work under `contracts/packs/local_staging_manifest.v0.json`,
`examples/local_staging_manifests/minimal_local_staging_manifest_v0/`,
`docs/reference/LOCAL_STAGING_MANIFEST_FORMAT.md`,
`scripts/validate_local_staging_manifest.py`, and
`control/audits/local-staging-manifest-format-v0/`. It defines validate-report
references, staged pack references, staged candidate entities, counts,
provenance, no-mutation guarantees, and future reset/delete/export policy.
No staging runtime exists, no staged state is created, and the format does not
mutate public search, local indexes, runtime source registry state, uploads,
or the master index.
Staged Pack Inspector v0 is now implemented as read-only inspection tooling
under `scripts/inspect_staged_pack.py`,
`scripts/validate_staged_pack_inspector.py`,
`docs/operations/STAGED_PACK_INSPECTION.md`, and
`control/audits/staged-pack-inspector-v0/`. It inspects explicit Local
Staging Manifest v0 files/roots or committed synthetic examples, validates
before reading by default, emits human and JSON summaries, redacts obvious
private paths/secrets, and creates no staging runtime, staged state, imports,
local indexes, public-search mutation, runtime source registry mutation,
uploads, network/model calls, or master-index mutation.
AI-Assisted Evidence Drafting Plan v0 is now implemented as planning/example/
validation-only work under
`control/inventory/ai_providers/ai_assisted_drafting_policy.json`,
`docs/architecture/AI_ASSISTED_EVIDENCE_DRAFTING.md`,
`docs/reference/AI_ASSISTED_DRAFTING_CONTRACT.md`,
`examples/ai_assisted_drafting/minimal_drafting_flow_v0/`,
`scripts/validate_ai_assisted_drafting_plan.py`, and
`control/audits/ai-assisted-evidence-drafting-plan-v0/`. It defines allowed
and forbidden drafting tasks, public-safe/local-private/forbidden input
contexts, typed-output-to-evidence/contribution candidate mappings, required
typed output validation, and required review. It adds no AI runtime, model
calls, API keys, telemetry, evidence/contribution acceptance, public-search
mutation, local-index mutation, or master-index mutation.

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
source-registry candidate to the current Python source inventory
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
adds no hosted deployment, live probes, crawling, external search automation,
arbitrary URL fetch, downloads, installs, uploads, local path search, accounts,
telemetry, or production API stability claim. Public Search Static Handoff v0
adds `site/dist/search.html`, `lite/search.html`, `text/search.txt`,
`files/search.README.txt`, and `data/search_handoff.json` as static/no-JS
handoff surfaces only; hosted public search remains unavailable/unverified and
GitHub Pages remains static-only.
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
fetch, or production safety claim. Public Search Static Handoff v0 now records
the static handoff without enabling hosted search.
Public Search Rehearsal v0 is now implemented as local/prototype evidence under
`control/audits/public-search-rehearsal-v0/`, `scripts/public_search_smoke.py`,
and `scripts/validate_public_search_rehearsal.py`. It records route coverage,
safe query outcomes, blocked request outcomes, static handoff review,
public-alpha review, and contract alignment without deploying hosted search,
calling external sources, enabling live probes, downloads, installs, uploads,
local path search, accounts, telemetry, or production claims.
The backend program should continue moving from bounded seam proof toward
operational backend infrastructure in this order:

1. Manual Observation Batch 0 Execution, human-operated
2. Search Usefulness Baseline Comparison Report v0 after observations
3. IA Metadata Live Probe Approval Pack v0 only after explicit approval
4. Public Hosted Search Rehearsal Plan v0 after source/safety confidence
5. Local Quarantine/Staging Tool v0 only after explicit approval
6. AI-Assisted Evidence Drafting Runtime Planning v0 only after explicit
   approval
7. GitHub Pages Workflow Repair v0 as an operator/Pages follow-up before any
   deployment-success claim
8. Native Static Data Viewer v0 if client work is prioritized
9. Snapshot Consumer Tooling v0
10. Rust Toolchain Verification Pack v0
11. Contribution Submission Tooling Plan v0
12. Master Index Review Queue Runtime Planning v0
13. Pack Import Report generator hardening only if the validate-only tool needs
   additional schema coverage
14. Rust Local Index Parity Candidate v0 only after planning review and Cargo
   availability expectations are explicit
15. Relay Prototype Implementation v0, only after explicit human approval and
   limited to the approved localhost-only/read-only/static relay scope
16. Windows 7 WinForms Native Skeleton Implementation v0, only after explicit
   human approval and limited to the approved read-only static-data/snapshot-demo
   skeleton scope

Post-P49 Platform Audit v0 is recorded under
`control/audits/post-p49-platform-audit-v0/`. It confirms the current posture:
Python remains the reference/oracle backend, `site/dist` is the active static
artifact, public search is local/prototype only, hosted public search and live
connectors are unavailable, external baselines are still manual-pending, pack
import/staging are validate-only/planning/read-only, and AI work is contract/
planning-only with no provider runtime or model calls. The next Codex-safe
branch is `p51-post-p50-remediation-pack-v0`; Manual Observation Batch 0 and
GitHub Pages repair remain human/operator work.

Post-P50 Remediation Pack v0 is recorded under
`control/audits/post-p50-remediation-v0/`. It adds minimal root governance
placeholders, records license selection as pending, repairs individual pack
validator example flags, records Pages evidence as operator-gated, and adds P51
validator/test metadata. It adds no hosted backend, live probes, source
connector runtime, AI runtime, pack import runtime, staging runtime, index
mutation, external observations, or deployment-success claim. The next branch
is `p52-static-deployment-evidence-github-pages-repair-v0` unless Pages
deployment evidence is verified first.

Static Deployment Evidence / GitHub Pages Repair v0 is recorded under
`control/audits/static-deployment-evidence-v0/`. It confirms the Pages workflow
is configured for `site/dist` and local static artifact validation passes, but
`gh` is unavailable in this environment and current-head GitHub Actions/Pages
status remains unverified. Prior committed evidence still records a Pages
configuration failure before artifact upload. P52 adds no backend hosting,
public search hosting, live probes, source connector runtime, credentials,
telemetry, accounts, uploads, downloads, installers, or deployment-success
claim. Codex-safe next work may proceed to
`p53-public-search-production-contract-v0`; operator-parallel work remains
GitHub Pages settings enablement and evidence capture.

Public Search Production Contract v0 is recorded under
`control/audits/public-search-production-contract-v0/`. It freezes the
production-facing v0 contract for the future hosted local-index wrapper:
`local_index_only` remains the only active mode, query length is capped at 160,
the default/max result limits are 10/25, public-safe error codes are stable, and
result-card/source-status/evidence-summary/absence/status schemas are aligned.
P53 adds no hosted backend, live probes, source connector runtime, telemetry
runtime, accounts, uploads, downloads, installers, arbitrary URL fetching, AI
runtime, index mutation, or hosted-search claim. The next Codex-safe branch is
`p54-hosted-public-search-wrapper-v0`; GitHub Pages evidence capture remains
operator-parallel work.

Hosted Public Search Wrapper v0 is recorded under
`control/audits/hosted-public-search-wrapper-v0/`. It adds the stdlib
`scripts/run_hosted_public_search.py` wrapper, config validation, local
rehearsal checks, template deployment files, operations docs, validator/tests,
and metadata for local_index_only public search only. It is not deployed and
does not enable live probes, source connector runtime, telemetry, accounts,
uploads, downloads, installers, arbitrary URL fetching, AI runtime, index
mutation, pack import, staging runtime, or hosted-search evidence. The next
Codex-safe branch is `p55-public-search-index-builder-v0`.

Public Search Index Builder v0 is recorded under
`control/audits/public-search-index-builder-v0/`. It adds a deterministic
stdlib builder, validator, committed `data/public_index` JSON/NDJSON artifacts,
generated-artifact drift metadata, docs, tests, and local public-search
integration over controlled fixture/recorded metadata only. The local and
hosted-wrapper paths now require the generated public index for hosted-safe
checks and report `generated_public_search_index` with 584 documents in this
checkout. It adds no live source calls, arbitrary URL fetching, private local
ingestion, executable payloads, downloads, uploads, telemetry, AI runtime,
pack import, staging runtime, master-index mutation, hosted deployment, or
production search-quality claim. The next Codex-safe branch is
`p56-static-site-search-integration-v0`.

Static Site Search Integration v0 is recorded under
`control/audits/static-site-search-integration-v0/`. It adds generated static
search handoff configuration and public-index summary data, keeps
`site/dist/search.html` plus lite/text/files search surfaces no-JS compatible,
and leaves the hosted backend `backend_unconfigured` because no verified
backend URL exists. It adds no hosted deployment, live probes, downloads,
uploads, accounts, telemetry, arbitrary URL fetching, AI runtime, index
mutation, pack import, staging runtime, or production search-quality claim. The
next Codex-safe branch is `p57-public-search-safety-evidence-v0`.

Public Search Safety Evidence v0 is recorded under
`control/audits/public-search-safety-evidence-v0/`. It adds a local in-process
hosted-wrapper evidence runner, validator, docs, tests, and audit report for
safe queries, blocked request categories, limit/status checks, static handoff
safety, public-index safety, privacy/redaction, and operator-gated
rate-limit/edge status. It adds no hosted deployment, live probes, downloads,
uploads, installs, accounts, telemetry, arbitrary URL fetching, AI runtime,
index mutation, pack import, staging runtime, or production claim. The next
Codex-safe branch is `p58-hosted-public-search-rehearsal-v0`.

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
## P58 Hosted Public Search Rehearsal v0

Status: completed locally. P58 starts the hosted public search wrapper on
localhost, verifies health/status/search/query-plan/source routes, safe queries,
34 blocked request cases, static handoff compatibility, public index
compatibility, and deployment-template safety. Hosted deployment, backend URL,
edge/rate limits, and production readiness remain unverified/operator-gated.


## P59 Query Observation Contract v0

P59 adds the first Query Intelligence Plane contract under `contracts/query/`, a privacy policy inventory, a synthetic query observation example, validators, docs, and an audit pack. Runtime query observation persistence, telemetry, public query logging, cache writes, miss ledger writes, probe enqueueing, candidate-index mutation, local-index mutation, and master-index mutation remain unimplemented.

## P60 Shared Query/Result Cache v0

P60 adds the shared query/result cache contract under `contracts/query/`, cache
key schema, synthetic result and scoped-absence examples, validators, docs, and
an audit pack. Runtime cache reads/writes, persistent cache storage, telemetry,
public query logging, miss ledger writes, search need writes, probe enqueueing,
candidate-index mutation, local-index mutation, and master-index mutation remain
unimplemented.

## P61 Search Miss Ledger v0

P61 adds the search miss ledger contract under `contracts/query/`, a
classification taxonomy, synthetic no-hit and weak-hit examples, validators,
docs, and an audit pack. Runtime ledger writes, persistent ledger storage,
telemetry, public query logging, search need creation, probe enqueueing, result
cache mutation, candidate-index mutation, local-index mutation, and
master-index mutation remain unimplemented.

## P62 Search Need Record v0

P62 adds the search need record contract under `contracts/query/`, a lifecycle
model, scoped synthetic unresolved software and compatibility-evidence examples,
validators, docs, and an audit pack. Runtime need storage, persistent need
storage, telemetry, public query logging, demand-count runtime, probe
enqueueing, candidate-index mutation, result-cache mutation, miss-ledger
mutation, local-index mutation, and master-index mutation remain unimplemented.

## P63 Probe Queue v0

P63 adds the probe queue item contract under `contracts/query/`, a probe kind
taxonomy, source policy and approval model, synthetic manual/source/deepening
examples, validators, docs, and an audit pack. Runtime queue storage,
persistent queue storage, probe execution, live source calls, source cache
mutation, evidence ledger mutation, candidate-index mutation, local-index
mutation, and master-index mutation remain unimplemented.

## P64 Candidate Index v0

P64 adds the candidate index record contract under `contracts/query/`, a
candidate lifecycle model, synthetic object/evidence/absence/conflict examples,
validators, docs, and an audit pack. Runtime candidate storage, persistent
candidate storage, public search candidate injection, candidate promotion
runtime, source-cache mutation, evidence-ledger mutation, local-index mutation,
and master-index mutation remain unimplemented.

## P65 Candidate Promotion Policy v0

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

Known Absence Page v0 is contract-only. It defines scoped absence, not global absence, for future no-result explanations with checked/not-checked scope, near misses, weak hits, gap explanations, safe next actions, privacy redaction, and no download/install/upload/live fetch. Known absence page is not a runtime page yet, not evidence acceptance, not candidate promotion, not master-index mutation, and not telemetry.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

P67 Query Privacy and Poisoning Guard v0 is complete as contract/schema/example/validator work. It keeps raw query retention default none, classifies privacy and poisoning risk, blocks unsafe public aggregation, and adds no runtime guard, telemetry, account/IP tracking, query logging, external calls, or index mutation.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->
