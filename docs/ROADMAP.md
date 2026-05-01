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

Current status within this stage: sixty-nine local deterministic Python thin slices now exist in the Python stdlib bootstrap lane, alongside a placeholder Rust migration skeleton, the first Python-oracle golden fixture pack, the first isolated Rust source-registry parity candidate, Rust Source Registry Parity Catch-up v0, the first isolated Rust query-planner parity candidate, Rust Local Index Parity Planning v0, Search Usefulness Audit v0, Search Usefulness Backlog Triage v0, Comprehensive Test/Eval Operating Layer and Repo Audit v0, Hard Test Pack v0, Source Coverage and Capability Model v0, Real Source Coverage Pack v0, Old-Platform Software Planner Pack v0, Member-Level Synthetic Records v0, Result Lanes + User-Cost Ranking v0, Compatibility Evidence Pack v0, Search Usefulness Audit Delta v0, Old-Platform Source Coverage Expansion v0, Search Usefulness Audit Delta v1, Hard Eval Satisfaction Pack v0, Old-Platform Result Refinement Pack v0, More Source Coverage Expansion v1, Article/Scan Fixture Pack v0, Manual External Baseline Observation Pack v0, Manual Observation Batch 0, Manual Observation Entry Helper v0, LIVE_ALPHA_00 Static Public Site Pack, Public Alpha Rehearsal Evidence v0, LIVE_ALPHA_01 Production Public-Alpha Wrapper, Public Publication Plane Contracts v0, GitHub Pages Deployment Enablement v0, Static Site Generation Migration v0, Generated Public Data Summaries v0, Lite/Text/Files Seed Surfaces v0, Static Resolver Demo Snapshots v0, Custom Domain / Alternate Host Readiness v0, Live Backend Handoff Contract v0, Live Probe Gateway Contract v0, Public Search API Contract v0, Public Search Result Card Contract v0, Public Search Safety / Abuse Guard v0, Local Public Search Runtime v0, Public Search Static Handoff v0, Compatibility Surface Strategy v0, Signed Snapshot Format v0, Signed Snapshot Consumer Contract v0, Native Client Contract v0, Native Action / Download / Install Policy v0, Native Local Cache / Privacy Policy v0, Native Client Project Readiness Review v0, Windows 7 WinForms Native Skeleton Planning v0, Post-Queue State Checkpoint v0, Relay Surface Design v0, Relay Prototype Planning v0, Repository Shape Consolidation v0, Static Artifact Promotion Review v0, GitHub Pages Run Evidence Review v0, Index Pack Contract v0, Contribution Pack Contract v0, and Master Index Review Queue Contract v0. The current Search Usefulness Audit status counts are 5 covered, 22 partial, 26 source gaps, 9 capability gaps, and 2 unknowns; the external-baseline pack adds 192 pending manual observation slots across 64 queries and three systems, Batch 0 adds 39 prioritized pending slots, the entry helper adds local list/create/validate/report tooling without recording observed external baselines, the static public site pack adds no-JS pages under `site/dist/`, the rehearsal evidence pack records local static/smoke/route/eval/baseline evidence without deployment, backend hosting, live probes, scraping, production claims, or observed external baselines, the wrapper adds a localhost-default public-alpha process/config guard without deployment, provider files, live probes, auth/TLS, rate limiting, or production approval, the publication plane adds governed route/data/client/deployment-target inventories, the GitHub Pages slice adds a static-only workflow plus artifact checks for `site/dist/`, the static generation slice adds `site/` plus generated `site/dist` validation while keeping `site/dist` as the deployment artifact, the promotion review conditionally promotes `site/dist` as the active repo-local static artifact while GitHub Actions evidence remains unverified, the public-data slice adds static JSON summaries under `site/dist/data/` without live API semantics, the lite/text/files slice adds static compatibility seed surfaces without live search, downloads, snapshots, relay/native runtime, or production claims, the public search static handoff adds no-JS `site/dist` handoff pages and `data/search_handoff.json` without hosted backend, live probes, or fake deployment claims, the demo-snapshot slice adds static fixture-backed resolver examples under `site/dist/demo/` without live search, live API semantics, external observations, backend hosting, or production claims, the static host readiness slice adds domain/alternate-host policy and validation without DNS, CNAME, provider config, alternate-host deployment, backend hosting, or live probes, the live backend handoff slice reserves `/api/v1` endpoint families, capability flags, and error-envelope expectations without making `/api/v1` live, deploying a backend, enabling live probes, or creating production API guarantees, the live probe gateway contract records disabled source-probe policy, source caps, cache/evidence expectations, and operator gates without implementing probes or making network calls, the Rust source-registry catch-up updates the isolated Rust source model to current Python capability/coverage/source shapes without runtime wiring, the Rust query-planner candidate adds isolated Rust planner parity against expanded Python-oracle goldens without runtime wiring, Rust Local Index Parity Planning v0 adds a planning-only parity lane with no Rust index implementation or runtime wiring, the compatibility surface strategy records surface capability/route matrices plus old-client/native/snapshot/relay readiness without new runtime behavior, Signed Snapshot Format v0 adds a deterministic repo-local seed example with checksums and signature-placeholder docs only, without real signing keys, production signatures, executable downloads, a public `/snapshots/` route, relay behavior, native-client runtime, live backend behavior, or live probes, Signed Snapshot Consumer Contract v0 defines future snapshot consumption read order, checksum/signature-placeholder handling, and consumer profiles without adding a consumer runtime, relay, native client, production signing, keys, downloads, live backend, or live probes, Native Client Contract v0 defines future Windows/macOS/native client lanes, inputs, readiness checks, and action prohibitions while adding no native projects, GUI, FFI, installers, downloads, relay sidecars, live probes, or Rust wiring, Native Client Project Readiness Review v0 records evidence that the first possible skeleton lane is Windows 7 WinForms only after explicit human approval while adding no project files or native runtime, Windows 7 WinForms Native Skeleton Planning v0 records a future skeleton path and namespace without creating project files, Relay Surface Design v0 records future local/LAN relay policy without adding a relay runtime, protocol server, network listener, private data exposure, live-probe passthrough, or write/admin route, Relay Prototype Planning v0 selects a future localhost-only/read-only/static relay prototype without implementing a relay server or opening sockets, and Master Index Review Queue Contract v0 records queue-entry/decision governance without hosted intake, uploads, accounts, moderation UI, auto-acceptance, or master-index writes.

GitHub Pages Run Evidence Review v0 now records passive Actions evidence for
the static Pages workflow. The current-head run failed at Pages configuration
after `site/dist` build/validation checks passed and before artifact upload,
so deployment success is not claimable and the next Pages milestone is repair
or repository settings configuration.

Public Search API Contract v0 now defines `local_index_only` public search
request, response, error, and route envelopes under `contracts/api/` and
`control/inventory/publication/public_search_routes.json`. Local Public Search
Runtime v0 implements the first local/prototype backend routes for `/search`,
`/api/v1/search`, `/api/v1/query-plan`, `/api/v1/status`, `/api/v1/sources`,
and `/api/v1/source/{source_id}`. This remains local only: it does not add
hosted deployment, live probes, URL fetching, scraping, crawling, downloads,
installs, uploads, local path search, accounts, telemetry, or production API
stability. Public Search Static Handoff v0 now adds `site/dist/search.html`,
lite/text/files handoff outputs, and `data/search_handoff.json` as static/no-JS
handoff surfaces only; hosted public search remains unavailable/unverified.
Public Search Rehearsal v0 now records local/prototype route coverage, safe
query outcomes, blocked request outcomes, static handoff review, public-alpha
review, and contract alignment under
`control/audits/public-search-rehearsal-v0/`. It does not deploy hosted search,
enable live probes, enable downloads/installs/uploads/local paths, add
accounts or telemetry, or claim production API stability.
Source Pack Contract v0, Evidence Pack Contract v0, Index Pack Contract v0, and
Contribution Pack Contract v0 now define the first portable pack formats under
`contracts/packs/` with
synthetic checksum-validated examples, docs, audit packs, validators, and
tests. Source packs cover source metadata and fixture/evidence inputs; evidence
packs narrow that into public-safe claims, observations, source locators,
snippets, and provenance; index packs cover summary-only index build metadata,
source coverage, field coverage, query examples, and public-safe record
summaries; contribution packs wrap review-candidate proposed changes and pack
references for a future governed review process. All remain
contract/validation/example-only and add no import, merge, indexing, upload,
moderation, accounts, raw SQLite/local-cache export, live connector, executable
plugin, master-index acceptance, automatic acceptance, canonical truth
selection, or production extension behavior.
Master Index Review Queue Contract v0 now defines the governance contract under
`contracts/master_index/`, `control/inventory/master_index/`,
`docs/reference/MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md`,
`docs/architecture/MASTER_INDEX_REVIEW_QUEUE.md`, and
`examples/master_index_review_queue/minimal_review_queue_v0/`. It models queue
entries, decisions, validation/review states, acceptance requirements,
privacy/rights/risk review, conflict preservation, and publication policy while
remaining contract/validation/example-only. It does not implement uploads,
imports, moderation, accounts, hosted master index writes, automatic
acceptance, live connectors, canonical truth selection, rights clearance,
malware safety, or production extension behavior.
Source/Evidence/Index Pack Import Planning v0 now defines the planning-only
future local import pipeline under `control/audits/pack-import-planning-v0/`,
`docs/reference/PACK_IMPORT_PLANNING.md`, and
`docs/architecture/PACK_IMPORT_PIPELINE.md`. It chooses validate-only as the
first future mode and private local quarantine as the next mode, while adding
no import runtime, staging directories, local search/index mutation, canonical
registry mutation, upload, hosted/master-index mutation, automatic acceptance,
live fetch, arbitrary directory scan, or executable plugin behavior.
Pack Import Validator Aggregator v0 now implements the validate-only aggregate
command for known pack examples. `python scripts/validate_pack_set.py
--all-examples` delegates to the source, evidence, index, contribution, and
master-index review queue validators and reports all five current examples as
passed without import, staging, local indexing, uploads, hosted/master-index
mutation, or acceptance claims.
AI Provider Contract v0 now defines the disabled-by-default future provider
boundary under `contracts/ai/`, `control/inventory/ai_providers/`,
`examples/ai_providers/disabled_stub_provider_v0/`, and
`control/audits/ai-provider-contract-v0/`. It validates provider manifests,
future task requests, typed output examples, privacy/credential/logging
posture, and forbidden truth/rights/malware/auto-acceptance uses without model
calls, API keys, telemetry, public-search AI, local-index mutation, or
master-index mutation.
Typed AI Output Validator v0 now validates standalone typed AI output
candidates through `scripts/validate_ai_output.py` and the pure
`runtime/engine/ai/typed_output_validator.py` helper. It checks four synthetic
disabled-stub examples, required review, prohibited uses, provider alignment,
generated-text bounds, private-path and secret leakage, and reports no model,
network, import, or mutation side effects.
Pack Import Report Format v0 now defines the durable validate-only report
format under `contracts/packs/pack_import_report.v0.json`,
`examples/import_reports/`, `scripts/validate_pack_import_report.py`, and
`control/audits/pack-import-report-format-v0/`. It records pack validation
results, issues, privacy/rights/risk posture, provenance, next actions, and
hard false mutation fields without implementing import, staging, local index
mutation, uploads, runtime mutation, model calls, or master-index mutation.
Validate-Only Pack Import Tool v0 is now implemented under
`scripts/validate_only_pack_import.py`,
`docs/operations/VALIDATE_ONLY_PACK_IMPORT.md`, and
`control/audits/validate-only-pack-import-tool-v0/`. It validates explicit pack
roots or known examples and emits Pack Import Report v0 without import,
staging, indexing, upload, runtime mutation, network calls, model calls, or
master-index mutation. Local Quarantine/Staging Model v0 is now implemented as
the follow-up planning layer before any staging runtime or staged state exists.
Local Quarantine/Staging Model v0 is now implemented as planning/governance
under `control/inventory/local_state/`,
`docs/architecture/LOCAL_QUARANTINE_STAGING_MODEL.md`,
`docs/reference/LOCAL_STAGING_PATH_POLICY.md`,
`scripts/validate_local_quarantine_staging_model.py`, and
`control/audits/local-quarantine-staging-model-v0/`. It creates no staging
runtime or staged state, keeps future local state private by default, and
preserves no-impact defaults for search and the master index. The next
Codex-safe milestone was Staging Report Path Contract v0.
Staging Report Path Contract v0 is now implemented as planning/governance
under `control/inventory/local_state/staging_report_path_contract.json`,
`docs/reference/STAGING_REPORT_PATH_CONTRACT.md`,
`docs/operations/LOCAL_REPORT_PATHS.md`,
`scripts/validate_staging_report_path_contract.py`, and
`control/audits/staging-report-path-contract-v0/`. It keeps report output on
stdout by default, requires explicit output paths for file writes, blocks
forbidden repo roots, requires redaction, and creates no report path runtime,
staging runtime, staged state, search impact, or master-index impact.
Local Staging Manifest Format v0 is now implemented as contract/example/
validation-only work under `contracts/packs/local_staging_manifest.v0.json`,
`examples/local_staging_manifests/minimal_local_staging_manifest_v0/`,
`docs/reference/LOCAL_STAGING_MANIFEST_FORMAT.md`,
`scripts/validate_local_staging_manifest.py`, and
`control/audits/local-staging-manifest-format-v0/`. It defines future staged
pack references, staged candidate entities, counts, provenance, no-mutation
guarantees, and reset/delete/export policy while creating no staging runtime,
staged state, public-search mutation, local-index mutation, runtime source
registry mutation, upload, or master-index mutation.
Staged Pack Inspector v0 is now implemented as read-only tooling under
`scripts/inspect_staged_pack.py`, `scripts/validate_staged_pack_inspector.py`,
`docs/operations/STAGED_PACK_INSPECTION.md`, and
`control/audits/staged-pack-inspector-v0/`. It inspects explicit Local Staging
Manifest v0 files/roots or committed synthetic examples, validates before
reading by default, emits human and JSON summaries, redacts obvious private
paths/secrets, and creates no staging runtime, staged state, import,
public-search mutation, local-index mutation, runtime source registry
mutation, upload, network/model call, or master-index mutation. The immediate
next milestone is Manual Observation Batch 0 Execution, human-operated; the
Codex-safe alternative is AI-Assisted Evidence Drafting Plan v0.
AI-Assisted Evidence Drafting Plan v0 is now implemented as planning/example/
validation-only work under
`control/inventory/ai_providers/ai_assisted_drafting_policy.json`,
`docs/architecture/AI_ASSISTED_EVIDENCE_DRAFTING.md`,
`docs/reference/AI_ASSISTED_DRAFTING_CONTRACT.md`,
`examples/ai_assisted_drafting/minimal_drafting_flow_v0/`,
`scripts/validate_ai_assisted_drafting_plan.py`, and
`control/audits/ai-assisted-evidence-drafting-plan-v0/`. It defines optional
future AI drafting as candidate-only assistance, maps typed outputs to
evidence/contribution candidates only after validation and required review, and
adds no AI runtime, model calls, API keys, telemetry, evidence/contribution
acceptance, public-search mutation, local-index mutation, or master-index
mutation. Manual Observation Batch 0 Execution remains the expected immediate
next milestone; Public Hosted Search Rehearsal Plan v0 is the Codex-safe
alternative.

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
Compatibility Evidence Pack v0 now derives compact source-backed compatibility
evidence records from committed fixture metadata, member paths, README text,
and compatibility notes. It projects evidence summaries through search, exact
resolution, local index, compatibility, CLI, web, local HTTP API, and eval
summaries while keeping unknown compatibility valid; it does not execute
software, verify installers, add live source behavior, scrape external systems,
or become a universal compatibility oracle.
Search Usefulness Audit Delta v0 now lives under
`control/audits/search-usefulness-delta-v0/`, recording the current
Search Usefulness Audit counts, historical reported baseline limitations,
wedge-specific movement, failure-mode counts, and the recommendation to expand
old-platform recorded source coverage next. It is audit/reporting only and does
not add retrieval behavior, source connectors, live source behavior, or external
baseline observations.
Old-Platform Source Coverage Expansion v0 now expands the committed
Internet-Archive-shaped fixture and local bundle fixture corpus with tiny
text-safe records for Windows 7/XP/2000/98 utility, browser-note,
registry-repair, and driver/support-media cases. It adds no live Internet
Archive calls, scraping, crawling, broad source federation, arbitrary local
filesystem ingestion, or production source claims.
Search Usefulness Audit Delta v1 now lives under
`control/audits/search-usefulness-delta-v1/`, recording the measured movement
after the source expansion: `partial +15`, `source_gap -13`,
`capability_gap -2`, and archive eval movement to `capability_gap=1` plus
`not_satisfied=5`.
It is audit/reporting only and recommends Hard Eval Satisfaction Pack v0 next.
Hard Eval Satisfaction Pack v0 now lives under
`control/audits/hard-eval-satisfaction-v0/` and updates the archive-resolution
eval runner to map existing source-backed member, representation,
compatibility, and source-family evidence into hard expected-result checks.
Archive evals now report `capability_gap=1` and `partial=5`; no hard task is
marked overall satisfied.
Old-Platform Result Refinement Pack v0 now lives under
`control/audits/old-platform-result-refinement-v0/` and updates the
archive-resolution eval runner to score deterministic primary-candidate shape,
expected lanes, and bad-result avoidance. Archive evals now report
`capability_gap=1`, `partial=4`, and `satisfied=1`; the satisfied task is the
source-backed driver support-CD member result, while four old-platform tasks
remain partial with explicit limitations.
More Source Coverage Expansion v1 now lives under
`control/audits/more-source-coverage-expansion-v1/` and extends existing
recorded fixture families with targeted tiny Firefox XP, blue FTP-client XP,
Windows 98 registry repair, and Windows 7 utility/app evidence. Archive evals
now report `capability_gap=1` and `satisfied=5`; the remaining hard capability
gap is `article_inside_magazine_scan`, which still needs bounded scan/page/OCR
or article fixture evidence.
Article/Scan Fixture Pack v0 now lives under
`control/audits/article-scan-fixture-pack-v0/` and adds one tiny
synthetic/recorded article-scan fixture source with parent issue lineage,
page-range metadata, and OCR-like fixture text. Archive evals now report
`satisfied=6`; this does not add live source behavior, scraping, OCR engines,
PDF/image parsing, real magazine scans, copyrighted article text, broad article
search, or external baseline claims.

Manual External Baseline Observation Pack v0 now lives under
`evals/search_usefulness/external_baselines/` and adds manual-only systems,
schema, template, instructions, pending slots, validation, and status reporting
for Google and Internet Archive observations. It performs no scraping,
automated external querying, live API calls, or external baseline fabrication.

Manual Observation Batch 0 now lives under
`evals/search_usefulness/external_baselines/batches/batch_0/` and selects 13
high-value query IDs across the three manual-only baseline systems. It creates
39 batch-scoped pending slots, operator instructions, and a checklist for later
human observation. It performs no observations, scraping, automation, live API
calls, or fabricated baseline recording.

Manual Observation Entry Helper v0 now adds stdlib-only helper scripts for
listing Batch 0 slots, creating one fillable pending observation file from a
slot, validating one file with `--file`, and summarizing Batch 0 progress. It
does not perform observations, open browsers, fetch URLs, scrape, automate
external searches, fill top results, or count pending/template records as
observed baselines.

LIVE_ALPHA_00 Static Public Site Pack now lives under `site/dist/` and adds
plain no-JS static pages for identity, status, source matrix, eval/audit state,
demo queries, limitations, roadmap, and local quickstart. It is a committed
site source pack for later hosting review only; it does not deploy Eureka, add
backend hosting, add DNS or cloud configuration, add live source probes, scrape
external systems, automate external searches, or claim production readiness.

Public Alpha Rehearsal Evidence v0 now lives under
`docs/operations/public_alpha_rehearsal_evidence_v0/` and records the current
static validator, public-alpha smoke, route inventory, archive eval, search
audit, external-baseline pending status, blocker, next-requirement, and
unsigned signoff evidence. It is evidence/runbook material only and does not
deploy Eureka or approve production.

LIVE_ALPHA_01 Production Public-Alpha Wrapper now adds
`scripts/run_public_alpha_server.py` and a bounded public-alpha config model
under `surfaces/web/server/`. It defaults to localhost, validates closed
public-alpha flags, guards nonlocal binds, reports safe status/capability
fields, and keeps live probes, live Internet Archive access, caller-provided
local paths, downloads/readback, and user storage disabled. It performs no
deployment, adds no provider configuration, and gives no production approval.

Public Publication Plane Contracts v0 now lives under
`control/inventory/publication/` with reference docs under `docs/architecture/`
and `docs/reference/`. It defines public route names, route stability, status
vocabulary, client profiles, public data expectations, static artifact/source
separation, base-path portability, deployment target semantics, redirect
policy, and the rule that no public claim may be published without a repo
source. The contract slice itself did not deploy Eureka, add a GitHub Pages
workflow, add DNS or provider configuration, create `site/`, add a generator,
start a live backend, enable live probes, or record external observations.

GitHub Pages Deployment Enablement v0 now adds `.github/workflows/pages.yml`,
`docs/operations/GITHUB_PAGES_DEPLOYMENT.md`, and
`scripts/check_github_pages_static_artifact.py`. The workflow validates the
publication inventory, validates `site/dist/`, checks the Pages artifact, and
uploads only `site/dist/` as a static Pages artifact. It does not deploy the
Python backend, enable live probes, add a custom domain, add secrets, introduce
a generator, or claim deployment success without GitHub Actions evidence.

Static Site Generation Migration v0 now lives under `site/` and adds a
stdlib-only static-site source tree, templates, page JSON, `site/build.py`,
`site/validate.py`, and generated `site/dist/` output. Repository Shape
Consolidation v0 makes `site/dist/` the single generated static deployment
artifact. This does not add Node/npm, a frontend framework, live backend
behavior, live probes, or production-readiness claims.

Generated Public Data Summaries v0 now adds deterministic static JSON under
`site/dist/data/`, covering site, page, source, eval, route, and build summaries
from governed repo inputs. These summaries are not a live API, do not add live
probes or external observations, and do not make production JSON stability
claims.

Lite/Text/Files Seed Surfaces v0 now adds static compatibility seed surfaces
under `site/dist/lite/`, `site/dist/text/`, and `site/dist/files/`. These
surfaces reuse the public
data summaries for old-browser HTML, plain text, and file-tree browsing with
SHA256SUMS, but they add no live search, executable downloads, snapshots,
relay/native runtime behavior, or production support claim.

Static Resolver Demo Snapshots v0 now adds static no-JS resolver examples
under `site/dist/demo/`. The demos show fixture-backed query planning, member
results, compatibility evidence, absence, comparison, source detail,
article/scan fixture results, and eval summaries. They add no live search, live
API semantics, backend hosting, external observations, or production behavior.

Custom Domain / Alternate Host Readiness v0 now adds domain and alternate
static-host readiness inventories, base-path portability guidance, an operator
checklist, `scripts/validate_static_host_readiness.py`, and tests. It adds no
DNS records, `CNAME`, provider config, alternate-host deployment, backend
hosting, live probes, or production claim.

Live Backend Handoff Contract v0 now adds contract-only future `/api/v1`
handoff inventories, disabled capability flags, error-envelope reference docs,
and `scripts/validate_live_backend_handoff.py`. It reserves future status,
search, query-plan, source, evidence, object, result, absence, comparison, and
live-probe route families without hosting a backend, making `/api/v1` live,
enabling live probes, or creating a stable production API claim.

Live Probe Gateway Contract v0 now adds
`control/inventory/publication/live_probe_gateway.json`, reference and
architecture docs, an operator policy, `scripts/validate_live_probe_gateway.py`,
and tests. It defines disabled-by-default source-probe policy, source caps,
cache/evidence expectations, retry/circuit-breaker posture, and operator gates
without implementing probes, calling external systems, fetching URLs, scraping,
crawling, enabling downloads, or turning Google into a live source.

Out of scope for bootstrap: finalized runtime semantics, mature connector coverage, production ranking systems, release automation, retrieval strategy expansion, and native runtime embedding beyond scaffolding.

## Latest Implementation Milestone

The latest implementation milestone is:

> Source Pack Contract v0

Search Usefulness Source Expansion v2 is now implemented as fixture-only source
coverage. It adds six recorded fixture source families and 15 tiny metadata
records, moving the current audit from covered=5/partial=22/source_gap=26/
capability_gap=9/unknown=2 to covered=5/partial=40/source_gap=10/
capability_gap=7/unknown=2 without live source calls, scraping, crawling,
external observations, arbitrary local ingestion, real binaries, downloads,
uploads, hosted search, or production relevance claims.
Search Usefulness Delta v2 is now implemented as audit/governance under
`control/audits/search-usefulness-delta-v2/`. It records the P32 baseline
source, current counts, status deltas, selected query movement, current
failure-mode counts, source-family impact, public-search smoke status,
hard-eval status, external-baseline pending status, remaining gaps, and the
Source Pack Contract v0 recommendation without changing retrieval behavior.
Source Pack Contract v0 is now implemented under `contracts/packs/`,
`examples/source_packs/minimal_recorded_source_pack_v0/`,
`docs/reference/SOURCE_PACK_CONTRACT.md`, and
`control/audits/source-pack-contract-v0/`. It defines a portable
source-metadata/evidence-input pack format with required rights/privacy notes,
checksum validation, prohibited behavior, and lifecycle guidance. It remains
contract/validation/example-only and does not implement import, indexing,
uploads, live connectors, executable plugins, hosted submission, downloads, or
master-index acceptance.
Evidence Pack Contract v0, Index Pack Contract v0, and Contribution Pack
Contract v0 are now implemented under `contracts/packs/`,
`examples/evidence_packs/`, `examples/index_packs/`,
`examples/contribution_packs/`, their reference docs, and their audit packs.
Evidence packs are claim/observation bundles; index packs are coverage and
record-summary bundles; contribution packs are review-candidate submission
wrappers. All remain contract/validation/example-only and do not implement
import, merge, indexing, upload, moderation, accounts, raw SQLite/local-cache
export, live connectors, canonical truth selection, hosted submission,
automatic acceptance, downloads, or master-index acceptance.
Master Index Review Queue Contract v0 is now implemented under
`contracts/master_index/`, `control/inventory/master_index/`,
`examples/master_index_review_queue/`, the master-index review docs, and its
audit pack. It is the review-governance contract for future contribution
candidates and adds no queue runtime, upload/import path, moderation UI,
accounts, hosted master index, master-index writes, or automatic acceptance.

Public Data Contract Stability Review v0 is now implemented as field-level
contract governance under
`control/audits/public-data-contract-stability-review-v0/` and
`docs/reference/PUBLIC_DATA_STABILITY_POLICY.md`. It classifies generated
public JSON fields as `stable_draft`, `experimental`, `volatile`, `internal`,
`deprecated`, or `future` without making public JSON a production API.
Generated Artifact Drift Guard v0 is now implemented as validation/audit
governance under `control/inventory/generated_artifacts/`,
`docs/operations/GENERATED_ARTIFACT_DRIFT_GUARD.md`,
`control/audits/generated-artifact-drift-guard-v0/`, and
`scripts/check_generated_artifact_drift.py`. It checks generated public data,
lite/text/files surfaces, demo snapshots, static snapshot seed files,
`site/dist`, Python oracle goldens, public-alpha rehearsal evidence,
publication inventories, test registry metadata, and AIDE metadata without
regenerating artifacts by default, changing runtime behavior, deploying, or
calling external services. Repository Shape Consolidation v0 now promotes
`site/dist/` as the single generated static artifact, retires the active legacy
static artifact path, and confirms `external/` as the outside-reference root.
Static Artifact Promotion Review v0 conditionally promotes `site/dist/` as the
active repo-local static artifact and records the local audit pack under
`control/audits/static-artifact-promotion-review-v0/`; GitHub Actions
deployment evidence has now been checked by GitHub Pages Run Evidence Review
v0. The current-head run failed at Pages configuration before artifact upload,
so no deployment success claim is allowed.
Public Search API Contract v0 is now implemented as contract/governance, and
Local Public Search Runtime v0 is implemented as local/prototype backend
runtime only. It exposes `/search`, `/api/v1/search`, `/api/v1/query-plan`,
`/api/v1/status`, `/api/v1/sources`, and `/api/v1/source/{source_id}` through
the gateway and stdlib web server while staying `local_index_only`.
Public Search Result Card Contract v0 is also implemented as contract/governance
only under `contracts/api/search_result_card.v0.json`,
`docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`, and
`control/audits/public-search-result-card-contract-v0/`. It defines future
result-card fields, lanes, user-cost, evidence, compatibility, member context,
actions, rights, risk, warnings, limitations, and gaps without making public
search live, adding runtime routes, enabling downloads/installers/execution,
claiming malware safety, claiming rights clearance, or promising production
ranking.
Public Search Safety / Abuse Guard v0 is now implemented as policy/governance
under `control/inventory/publication/public_search_safety.json`,
`docs/operations/PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md`, and
`docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md`. It fixes
`local_index_only` as the only allowed v0 mode, bounds request/result/time
behavior, forbids URL/local path/credential/download/install/upload parameters,
maps disallowed behavior to the P26 error envelope, keeps telemetry/logging
runtime off, and records future operator controls. The local runtime and static
handoff add no rate-limit middleware, hosted backend, live probe,
download/install/upload surface, arbitrary URL fetch, account/session behavior,
telemetry persistence, or production safety claim. Search Usefulness Source
Expansion v2 is implemented fixture-only and the next milestone is Search
Usefulness Delta v2. Public Search Rehearsal v0 is implemented as
local/prototype evidence only and adds no hosted deployment, live probes,
downloads, installs, uploads, local path search, accounts, telemetry, or
production claim. GitHub Pages
Workflow Repair v0 remains an operator/Pages follow-up before any hosted
deployment success claim is made.
Rust Local Index Parity Candidate v0 remains blocked on planning review and
Cargo availability.

Source Registry v0, Resolution Run Model v0, Query Planner v0, Local Index v0,
Local Worker and Task Model v0, Resolution Memory v0, and Archive Resolution
Eval Runner v0, Public Alpha Safe Mode v0, Public Alpha Deployment Readiness
Review, Public Alpha Hosting Pack v0, Rust Migration Skeleton and Parity
Plan v0, Rust Parity Fixture Pack v0, Rust Source Registry Parity Candidate
v0, Search Usefulness Audit v0, Search Usefulness Backlog Triage v0,
Comprehensive Test/Eval Operating Layer and Repo Audit v0, Hard Test Pack v0,
Source Coverage and Capability Model v0, Real Source Coverage Pack v0,
Old-Platform Software Planner Pack v0, Member-Level Synthetic Records v0,
Result Lanes + User-Cost Ranking v0, Compatibility Evidence Pack v0,
Search Usefulness Audit Delta v0, and Old-Platform Source Coverage Expansion
v0, Search Usefulness Audit Delta v1, Hard Eval Satisfaction Pack v0,
Old-Platform Result Refinement Pack v0, More Source Coverage Expansion v1,
Article/Scan Fixture Pack v0, Manual External Baseline Observation Pack v0,
Manual Observation Batch 0, Manual Observation Entry Helper v0,
LIVE_ALPHA_00 Static Public Site Pack, Public Alpha Rehearsal Evidence v0, and
LIVE_ALPHA_01 Production Public-Alpha Wrapper, Public Publication Plane
Contracts v0, GitHub Pages Deployment Enablement v0, Static Site
Generation Migration v0, Generated Public Data Summaries v0,
Lite/Text/Files Seed Surfaces v0, Static Resolver Demo Snapshots v0,
Custom Domain / Alternate Host Readiness v0, Live Backend Handoff Contract
v0, Live Probe Gateway Contract v0, Rust Query Planner Parity Candidate v0,
Compatibility Surface Strategy v0, Signed Snapshot Format v0, Signed Snapshot
Consumer Contract v0, Native Client Contract v0, Native Action / Download /
Install Policy v0, Native Local Cache / Privacy Policy v0, Native Client
Project Readiness Review v0, Relay Surface Design v0, Generated Artifact Drift
Guard v0, Rust Source Registry
Parity
Catch-up v0, and Rust Local Index
Parity Planning v0 now
mark the start of a more evidence-led backend phase. Rust source-registry
parity now catches up to the expanded Python source capability and coverage
shape for the current source inventory without wiring Rust into runtime
behavior. Relay Surface
Design v0 is implemented as contract/checklist work only
and does not add relay services, protocol bridges, sockets, private data
exposure, write/admin routes, live-probe passthrough, native sidecars, or
network behavior.
Signed Snapshot Format v0 is implemented as a contract and deterministic seed
example only; it adds no real signing keys, production signatures, executable
downloads, public /snapshots/ route, relay behavior, native-client runtime,
live backend behavior, or live probes.
Signed Snapshot Consumer Contract v0 is implemented as contract/design only; it
defines future consumer read order, checksum semantics, v0 signature-placeholder
handling, and file-tree/text/lite/relay/native/audit consumer profiles without
adding a snapshot reader runtime, relay runtime, native client, production
signing, real signing keys, executable downloads, live backend behavior, or live
probes.
Native Client Contract v0 is implemented as contract/design only; it defines
future Windows and Mac lane policy, allowed static/snapshot/API/relay inputs,
CLI current-state boundaries, readiness gates, and install/download/action
prohibitions without adding Visual Studio/Xcode projects, native GUI clients,
FFI, installer automation, package-manager behavior, native snapshot reader
runtime, relay sidecars, live probes, or Rust runtime wiring.
Native Action / Download / Install Policy v0 is implemented as policy/contract
only; it defines safe read-only actions, bounded local fixture actions, future
gated download/mirror/install/package-manager/execute/restore/uninstall
classes, prohibited silent/privileged/private actions, warning classes, and
static/public-alpha defaults while adding no downloads, installers,
package-manager integration, malware scanning, rights clearance, native clients,
relay runtime, or executable trust claims.
Native Local Cache / Privacy Policy v0 is implemented as policy/contract only;
it defines future public/private cache, local path, user state, resolution
memory, telemetry/logging, credentials, deletion/export/reset, portable-mode,
snapshot, relay, and public-alpha privacy gates while adding no cache runtime,
private file ingestion, local archive scanning, telemetry, accounts, cloud
sync, uploads, native clients, relay runtime, or private-data relay behavior.
Native Client Project Readiness Review v0 is implemented as review/evidence
only; it records contract coverage, lane readiness, risks, a pre-native
checklist, and the decision
`ready_for_minimal_project_skeleton_after_human_approval` for the
`windows_7_x64_winforms_net48` lane. It does not create Visual Studio/Xcode
projects, native app source trees, GUI behavior, FFI, cache runtime, downloads,
installers, relay runtime, live probes, or runtime wiring.
Windows 7 WinForms Native Skeleton Planning v0 is implemented as planning only;
it proposes the future path `clients/windows/winforms-net48/` and namespace
`Eureka.Clients.Windows.WinForms`, records Windows host, Visual Studio 2022,
.NET Framework 4.8, x64, and Windows 7 SP1+ build-host requirements, and keeps
the future skeleton read-only/static-data/snapshot-demo only. It does not create
`clients/`, Visual Studio solutions, `.csproj`, C# source, GUI behavior, FFI,
cache runtime, downloads, installers, telemetry, relay runtime, live probes, or
runtime wiring. Implementation remains blocked until explicit human approval.
Relay Prototype Planning v0 is implemented as planning only; it selects the
future `local_static_http_relay_prototype` as the first relay candidate with a
localhost-only, read-only, static public-data/seed-snapshot scope. It does not
implement a relay server, open sockets, add local HTTP relay behavior, add
FTP/SMB/AFP/NFS/WebDAV/Gopher support, translate protocols, mount snapshots,
serve private files, expose native sidecars, proxy a live backend, enable live
probes, or claim old-client relay support.
Full Project State Audit v0 is implemented as audit/reporting only under
`control/audits/full-project-state-audit-v0/`; it records current milestone
status, verification, eval/search state, external-baseline pending state,
publication/static/public-alpha status, source/retrieval state,
snapshot/relay/native/Rust status, risks, blockers, human-operated work,
deferrals, and next milestones without adding product behavior.
Rust Query Planner Parity Candidate v0 remains isolated and does not wire Rust
into runtime behavior. Rust Local Index Parity Planning v0 is implemented as
planning-only parity governance for future local-index Rust work; it adds no
Rust index implementation, SQLite/indexing behavior, Python local-index
replacement, or runtime/surface wiring. Manual
Observation Batch 0 Execution remains
human-operated parallel work: external Google and Internet Archive observations
remain pending/manual. The next Codex-side work must still avoid live crawling,
external scraping, live probes, installer execution, fuzzy/vector search, LLM
planning, broad source federation, OCR claims, external baseline fabrication,
provider-specific backend hosting overreach, custom-domain setup, and
production benchmark claims. Internet Archive Live Probe v0 remains future
work that requires explicit human approval after live probe gateway review and separate
implementation review.

## Post-Queue Checkpoint

Post-Queue State Checkpoint v0 now records the actual post-queue repo state,
verification matrix, eval/audit posture, external-baseline pending state,
publication/static/live-alpha/Rust/snapshot status, risks, and next planning
under `control/audits/post-queue-state-checkpoint-v0/`. It is reporting only
and does not add runtime behavior.

## Post-P49 Platform Audit

Post-P49 Platform Audit v0 records the P50 checkpoint under
`control/audits/post-p49-platform-audit-v0/`. Current search-usefulness counts
are `covered=5`, `partial=40`, `source_gap=10`, `capability_gap=7`, and
`unknown=2`; archive-resolution hard evals remain `satisfied=6`; external
baselines remain `192` pending and `0` observed. The next branch is
`p51-post-p50-remediation-pack-v0`, with Manual Observation Batch 0 and
GitHub Pages repair kept as human/operator work.

## Post-P50 Remediation

Post-P50 Remediation Pack v0 records the P51 checkpoint under
`control/audits/post-p50-remediation-v0/`. It fixes bounded repo-local drift:
minimal root governance docs, license-selection guidance, pack-validator
`--all-examples`/`--known-examples` alignment, P51 validator/tests, and
operator-facing GitHub Pages evidence steps. It keeps hosted search
unavailable, external baselines pending/manual, live probes disabled, AI
runtime absent, and Rust optional/parity-only. The next branch is
`p52-static-deployment-evidence-github-pages-repair-v0` unless Pages evidence
is verified separately first.

Static Deployment Evidence / GitHub Pages Repair v0 records the P52 checkpoint
under `control/audits/static-deployment-evidence-v0/`. It verifies the local
static deployment path as configured and valid for `site/dist`, records `gh` as
unavailable in this environment, keeps current-head Pages deployment
unverified/operator-gated, and preserves the prior committed evidence of a
Pages configuration failure before artifact upload. It adds no hosted backend,
public search hosting, live probes, credentials, telemetry, accounts, uploads,
downloads, installers, or production claim. The Codex-safe next branch is
`p53-public-search-production-contract-v0`; the operator-parallel follow-up is
GitHub Pages evidence capture after repository Pages settings are enabled.

Public Search Production Contract v0 records the P53 checkpoint under
`control/audits/public-search-production-contract-v0/`. It hardens the future
hosted local-index contract without deploying it: GET-only v0 routes are
classified, request/response/error/result-card/source/evidence/absence/status
schemas are aligned, forbidden parameters cover local paths, arbitrary URL
fetch, credentials, live probes, downloads, installs, uploads, and execution,
and P54 wrapper requirements are documented. The next Codex-safe branch is
`p54-hosted-public-search-wrapper-v0`; the wrapper must still implement
local_index_only only and preserve all disabled capability flags.

Hosted Public Search Wrapper v0 records the P54 checkpoint under
`control/audits/hosted-public-search-wrapper-v0/`. It adds a stdlib wrapper,
safe environment validation, in-process route rehearsal, Docker/Render
templates, hosted-operation docs, and metadata for local_index_only public
search only. Hosted deployment remains unverified and operator-gated; no live
probes, source connectors, downloads, uploads, accounts, telemetry, arbitrary
URL fetch, AI runtime, index mutation, pack import, staging runtime, or hosted
availability claim is added. The next Codex-safe branch is
`p55-public-search-index-builder-v0`; operator-parallel work is backend host
deployment evidence capture.

Public Search Index Builder v0 records the P55 checkpoint under
`control/audits/public-search-index-builder-v0/`. It creates the first
controlled public-safe generated search index under `data/public_index`, with
584 JSON/NDJSON documents derived from committed fixture and recorded metadata,
validated source coverage, deterministic drift checks, and local public-search
runtime integration. SQLite/FTS5 availability is observed but not required for
the committed artifact; the runtime remains deterministic lexical
local_index_only search. The next Codex-safe branch is
`p56-static-site-search-integration-v0`; hosted deployment evidence remains
operator-gated.

Static Site Search Integration v0 records the P56 checkpoint under
`control/audits/static-site-search-integration-v0/`. It wires the static
publication site to the public search path through generated no-JS search
surfaces, `data/search_config.json`, and `data/public_index_summary.json`
while keeping hosted backend status `backend_unconfigured` and hosted form
submission disabled until operator evidence exists. The next Codex-safe branch
is `p57-public-search-safety-evidence-v0`; hosted deployment and backend URL
verification remain operator-gated.

Public Search Safety Evidence v0 records the P57 checkpoint under
`control/audits/public-search-safety-evidence-v0/`. It runs a local in-process
hosted-wrapper safety matrix for safe queries, blocked dangerous parameters,
query/result limits, status honesty, static handoff safety, public index
safety, privacy/redaction, and operator-gated rate-limit/edge status. It adds
no hosted deployment, live probes, downloads, uploads, installs, accounts,
telemetry, arbitrary URL fetching, AI runtime, index mutation, or production
claim. The next Codex-safe branch is
`p58-hosted-public-search-rehearsal-v0`.
## P58 Hosted Public Search Rehearsal v0

P58 completes the local hosted-mode rehearsal for the public search wrapper
without deploying it. The next Codex-safe branch is P59 Query Observation
Contract v0; operator parallel work remains hosted deployment evidence, backend
URL configuration after evidence, edge/rate limits, static-site verification,
and Manual Observation Batch 0.


## P59 Query Observation Contract v0

Completed: privacy-filtered query observation contract and validation. Next Codex-safe branch: P60 Shared Query/Result Cache v0. Human/operator parallel work remains hosted wrapper deployment evidence, backend URL configuration, edge/rate-limit setup, static site verification, and Manual Observation Batch 0 Execution.
