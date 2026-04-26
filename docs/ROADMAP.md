# Roadmap

The roadmap is intentionally staged and bounded. Bootstrap work should make later implementation easier to govern, not attempt to deliver the full product in one pass.

## Detailed Roadmap Docs

Detailed next-phase planning now lives under `docs/roadmap/`:

- [Backend Roadmap](roadmap/BACKEND_ROADMAP.md)
- [Public Alpha](roadmap/PUBLIC_ALPHA.md)
- [Rust Migration](roadmap/RUST_MIGRATION.md)
- [Native Apps Later](roadmap/NATIVE_APPS_LATER.md)

The root roadmap remains the short stage summary. The detailed roadmap docs
record the accepted transition from bounded architecture proof into operational
backend development.

## Stage 0: Bootstrap and Repo Contract

- establish the monorepo structure
- write founding documentation
- pin minimal AIDE repo-operating metadata
- create the initial contract, runtime, surface, test, and eval scaffolding

## Stage 1: Contract Hardening

- refine archive schema placeholders into governed draft contracts
- define the first public gateway contract set
- define shared UI contract and view-model boundaries
- add compatibility and migration rules for contract evolution

## Stage 2: Runtime Skeletons

- add engine interface boundaries without full product logic
- add gateway service boundaries and internal implementation seams
- scaffold connector adapters against `runtime/engine/interfaces/ingest/**`, `runtime/engine/interfaces/extract/**`, and `runtime/engine/interfaces/normalize/**`

Current status within this stage: forty-one local deterministic Python thin slices now exist in the Python stdlib bootstrap lane, alongside a placeholder Rust migration skeleton, the first Python-oracle golden fixture pack, the first isolated Rust source-registry parity candidate, Search Usefulness Audit v0, Search Usefulness Backlog Triage v0, Comprehensive Test/Eval Operating Layer and Repo Audit v0, Hard Test Pack v0, Source Coverage and Capability Model v0, Real Source Coverage Pack v0, Old-Platform Software Planner Pack v0, Member-Level Synthetic Records v0, and Result Lanes + User-Cost Ranking v0. The latest result-lane layer annotates current result records with deterministic lanes and user-cost explanations without broad extraction, arbitrary local filesystem ingestion, fuzzy/vector retrieval, LLM scoring, live source behavior, production ranking, or new connectors.

## Stage 3: Surface Skeletons

- add the initial web workbench shell against gateway public contracts
- add native shell scaffolding with offline-path boundaries still explicitly gated
- add basic cross-component verification paths

Current status within this stage: `surfaces/web/` now contains the first compatibility-first exact-resolution workbench page, the first deterministic search-and-absence page, the first bounded subject-state page, the first bounded representations page, the first bounded compatibility page, the first bounded handoff page, the first bounded action-plan page, the first bounded acquisition page and fetch route, the first bounded decomposition page, the first bounded member-preview page, dedicated bounded miss-explanation pages, a bounded action panel plus manifest-export and bundle-export routes for resolved targets, a stored-exports section plus local-store routes for deterministic stored artifacts, a compatibility-first bundle inspection page, a compatibility-first archive-resolution eval report page, and the first local stdlib machine-readable HTTP API slice for the same bounded capabilities. `surfaces/native/cli/` now provides the first non-web surface proof, including bounded subject-state listing, bounded miss-explanation commands, bounded representations listing, bounded handoff evaluation, bounded acquisition and fetch, bounded decomposition and member inspection, bounded member preview and readback, bounded action-plan evaluation, bounded strategy-aware action-plan evaluation, bounded archive-resolution eval summaries, and bounded compatibility evaluation. These slices are stdlib-only, local-only, consume transport-neutral gateway boundaries plus shared surface view models without importing engine internals directly, and now show bounded source-family visibility, bounded evidence summaries, bounded object/state grouping, bounded absence reasoning, bounded representation and access-path summaries, bounded representation-selection and handoff guidance, bounded acquisition results, bounded decomposition results, bounded member-readback results, bounded action-routing recommendations, bounded strategy-aware recommendation emphasis, bounded archive-resolution eval capability gaps, plus bounded host-profile compatibility verdicts for both synthetic fixtures and recorded GitHub Releases-backed results.

## Stage 4: Bounded Product Work

- begin software-first resolution, preservation, and reconstruction implementation
- add real evidence handling, compatibility reasoning, and snapshot workflows
- expand only where contract governance and architectural boundaries already exist

Current status within this stage: the first repo-level archive-resolution eval corpus now lives under `evals/archive_resolution/`. It records hard software-resolution queries, explicit bad-result patterns, minimum granularity expectations, expected future result lanes, and allowed absence outcomes as a guardrail for future investigation, ranking, decomposition, source-expansion, and optional AI work without changing current runtime semantics. Source Registry v0 now also lives under `contracts/source_registry/`, `control/inventory/sources/`, and `runtime/source_registry/`, making source inventory explicit and inspectable without introducing live sync, crawling, or source scoring.
Resolution Run Model v0 now also lives under `runtime/engine/resolution_runs/`, giving the repo a first synchronous durable investigation envelope without introducing worker queues, streaming updates, or full investigation-planner semantics.
Query Planner v0 now also lives under `runtime/engine/query_planner/`, giving the repo a first deterministic rule-based compiler from raw query text into structured `ResolutionTask` records without introducing LLM planning, vector retrieval, fuzzy matching, ranking, or full planner-driven retrieval.
Local Index v0 now also lives under `runtime/engine/index/`, giving the repo a first durable local SQLite index over the current bounded corpus with FTS5 preferred and deterministic fallback behavior without introducing ranking, fuzzy retrieval, vector search, live source sync, incremental indexing, or worker-driven rebuilds.
Local Worker and Task Model v0 now also lives under `runtime/engine/workers/`, giving the repo a first synchronous local execution substrate for source-registry validation, local-index build/query, and archive-resolution eval validation without introducing background scheduling, distributed queues, retries, or async orchestration.
Resolution Memory v0 now also lives under `runtime/engine/memory/`, giving the repo a first explicit local reusable investigation-memory seam derived from persisted completed runs without introducing shared/cloud memory, personalization, ranking, or automatic invalidation.
Archive Resolution Eval Runner v0 now also lives under `runtime/engine/evals/`, giving the repo a first executable regression harness over the hard-query packet without introducing ranking, fuzzy retrieval, vector search, LLM planning, crawling, live source sync, or production relevance evaluation.
Public Alpha Safe Mode v0 now also lives under `surfaces/web/server/`, giving the stdlib web/API backend explicit `local_dev` and `public_alpha` modes, status reporting, and route-policy blocking for arbitrary local path parameters without introducing auth, HTTPS/TLS, accounts, production deployment, or multi-user hosting.
Public Alpha Deployment Readiness Review now also lives under `control/inventory/`, `scripts/`, and `docs/operations/`, giving the project an auditable route inventory, repeatable public-alpha smoke checks, and operator checklist without introducing deployment infrastructure, auth, HTTPS/TLS, accounts, rate limiting, or production process management.
Public Alpha Hosting Pack v0 now also lives under `docs/operations/public_alpha_hosting_pack/`, giving the project a supervised rehearsal evidence packet without introducing deployment infrastructure, auth, HTTPS/TLS, accounts, rate limiting, production logging, or process management.
Rust Migration Skeleton and Parity Plan v0 now also lives under `crates/`, `docs/architecture/RUST_BACKEND_LANE.md`, and `tests/parity/`, giving the project a governed Rust lane without making Rust an active backend or changing Python reference behavior.
Rust Parity Fixture Pack v0 now also lives under `tests/parity/golden/python_oracle/v0/` and `scripts/generate_python_oracle_golden.py`, giving future Rust migration work stable Python-oracle outputs without porting Rust runtime behavior or replacing Python.
Rust Source Registry Parity Candidate v0 now also lives under `crates/eureka-core/`, giving the project its first Rust behavior seam while keeping Python runtime authoritative.
Search Usefulness Audit v0 now also lives under `evals/search_usefulness/`,
`runtime/engine/evals/search_usefulness_runner.py`, and
`scripts/run_search_usefulness_audit.py`, giving the project a broad local
usefulness audit and future-work backlog generator without scraping Google or
Internet Archive, adding live crawling, or claiming global search superiority.
Comprehensive Test/Eval Operating Layer and Repo Audit v0 now also lives under
`control/inventory/tests/`, `control/audits/`,
`docs/operations/TEST_AND_EVAL_LANES.md`, and `.aide/tasks/`, giving the
project reusable verification lanes, structured findings, hard-test proposals,
and next-milestone recommendations without changing runtime product behavior.
Hard Test Pack v0 now also lives under `tests/hardening/` and
`docs/operations/HARD_TEST_PACK.md`, giving the project enforceable regression
guards for eval hardness, external baseline honesty, public-alpha path safety,
route/docs/README drift, Python-oracle golden drift, Rust parity structure,
source placeholder honesty, memory path/privacy scope, and AIDE/test registry
consistency without changing runtime product behavior.
Search Usefulness Backlog Triage v0 now also lives under
`control/backlog/search_usefulness_triage/`, selecting old-platform-compatible
software search and member-level discovery as the next usefulness wedges. Its
selected immediate milestone, Source Coverage and Capability Model v0, is now
implemented as the metadata/projection layer before Real Source Coverage Pack
v0.
Source Coverage and Capability Model v0 now extends Source Registry v0 with
explicit capability flags, a six-level coverage-depth ladder, connector-mode
metadata, current limitations, and next coverage steps for each seed source.
It keeps Internet Archive, Wayback/Memento, Software Heritage, and local-files
records as placeholders or local/private future sources and does not add any
new connector, live probe, crawl, or acquisition behavior.
Real Source Coverage Pack v0 now adds separate active fixture records for
`internet-archive-recorded-fixtures` and `local-bundle-fixtures`, with tiny
committed metadata/file-list and ZIP bundle fixtures. It keeps the Internet
Archive and local-files placeholders unimplemented and does not add live source
probing, crawling, scraping, broad source federation, or arbitrary local
filesystem ingestion.
Old-Platform Software Planner Pack v0 now extends Query Planner v0 with
deterministic old-platform software interpretation, including OS aliases,
latest-compatible release intent, driver/hardware/OS intent, vague identity
uncertainty, documentation intent, member-discovery hints, and app-vs-OS-media
suppression hints. It improves interpretation only and does not add ranking,
fuzzy/vector retrieval, LLM planning, live source behavior, or new connectors.
Member-Level Synthetic Records v0 now derives deterministic
`member:sha256:<digest>` records for files inside bounded local bundle fixtures,
preserving parent target refs, parent representation ids, source provenance,
member paths, evidence summaries, content metadata, and action hints. It makes
member candidates visible through exact resolution, deterministic search, local
index, CLI, web, and local HTTP API projections without adding broad archive
extraction, arbitrary local filesystem ingestion, ranking, live source behavior,
or new connectors.
Result Lanes + User-Cost Ranking v0 now assigns deterministic result lanes and
user-cost explanations to current result records, including synthetic member
records and parent bundles. It projects those hints through search, exact
resolution, local index, CLI, web, local HTTP API, and eval summaries without
adding fuzzy/vector retrieval, LLM scoring, live source behavior, production
ranking, or new connectors.

Out of scope for bootstrap: finalized runtime semantics, mature connector coverage, production ranking systems, release automation, retrieval strategy expansion, and native runtime embedding beyond scaffolding.

## Immediate Next Milestone

The next implementation milestone is:

> Compatibility Evidence Pack v0

Source Registry v0, Resolution Run Model v0, Query Planner v0, Local Index v0,
Local Worker and Task Model v0, Resolution Memory v0, and Archive Resolution
Eval Runner v0, Public Alpha Safe Mode v0, Public Alpha Deployment Readiness
Review, Public Alpha Hosting Pack v0, Rust Migration Skeleton and Parity
Plan v0, Rust Parity Fixture Pack v0, Rust Source Registry Parity Candidate
v0, Search Usefulness Audit v0, Search Usefulness Backlog Triage v0,
Comprehensive Test/Eval Operating Layer and Repo Audit v0, Hard Test Pack v0,
Source Coverage and Capability Model v0, Real Source Coverage Pack v0,
Old-Platform Software Planner Pack v0, Member-Level Synthetic Records v0, and
Result Lanes + User-Cost Ranking v0 now
mark the start of a more evidence-led backend phase. The next step is to add
source-backed compatibility evidence so old-platform usefulness can distinguish
known, unknown, inferred, and incompatible outcomes while preserving truth and
uncertainty. That next step must still avoid live crawling, external scraping,
installer execution, fuzzy/vector search, LLM planning, broad source federation,
and production compatibility-oracle claims.
