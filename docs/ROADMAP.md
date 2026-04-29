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

Current status within this stage: sixty-one local deterministic Python thin slices now exist in the Python stdlib bootstrap lane, alongside a placeholder Rust migration skeleton, the first Python-oracle golden fixture pack, the first isolated Rust source-registry parity candidate, Rust Source Registry Parity Catch-up v0, the first isolated Rust query-planner parity candidate, Rust Local Index Parity Planning v0, Search Usefulness Audit v0, Search Usefulness Backlog Triage v0, Comprehensive Test/Eval Operating Layer and Repo Audit v0, Hard Test Pack v0, Source Coverage and Capability Model v0, Real Source Coverage Pack v0, Old-Platform Software Planner Pack v0, Member-Level Synthetic Records v0, Result Lanes + User-Cost Ranking v0, Compatibility Evidence Pack v0, Search Usefulness Audit Delta v0, Old-Platform Source Coverage Expansion v0, Search Usefulness Audit Delta v1, Hard Eval Satisfaction Pack v0, Old-Platform Result Refinement Pack v0, More Source Coverage Expansion v1, Article/Scan Fixture Pack v0, Manual External Baseline Observation Pack v0, Manual Observation Batch 0, Manual Observation Entry Helper v0, LIVE_ALPHA_00 Static Public Site Pack, Public Alpha Rehearsal Evidence v0, LIVE_ALPHA_01 Production Public-Alpha Wrapper, Public Publication Plane Contracts v0, GitHub Pages Deployment Enablement v0, Static Site Generation Migration v0, Generated Public Data Summaries v0, Lite/Text/Files Seed Surfaces v0, Static Resolver Demo Snapshots v0, Custom Domain / Alternate Host Readiness v0, Live Backend Handoff Contract v0, Live Probe Gateway Contract v0, Compatibility Surface Strategy v0, Signed Snapshot Format v0, Signed Snapshot Consumer Contract v0, Native Client Contract v0, Post-Queue State Checkpoint v0, and Relay Surface Design v0. The current Search Usefulness Audit status counts are 5 covered, 22 partial, 26 source gaps, 9 capability gaps, and 2 unknowns; the external-baseline pack adds 192 pending manual observation slots across 64 queries and three systems, Batch 0 adds 39 prioritized pending slots, the entry helper adds local list/create/validate/report tooling without recording observed external baselines, the static public site pack adds no-JS pages under `public_site/`, the rehearsal evidence pack records local static/smoke/route/eval/baseline evidence without deployment, backend hosting, live probes, scraping, production claims, or observed external baselines, the wrapper adds a localhost-default public-alpha process/config guard without deployment, provider files, live probes, auth/TLS, rate limiting, or production approval, the publication plane adds governed route/data/client/deployment-target inventories, the GitHub Pages slice adds a static-only workflow plus artifact checks for `public_site/`, the static generation slice adds `site/` plus generated `site/dist/` validation while keeping `public_site/` as the deployment artifact, the public-data slice adds static JSON summaries under `public_site/data/` and `site/dist/data/` without live API semantics, the lite/text/files slice adds static compatibility seed surfaces without live search, downloads, snapshots, relay/native runtime, or production claims, the demo-snapshot slice adds static fixture-backed resolver examples under `public_site/demo/` and `site/dist/demo/` without live search, live API semantics, external observations, backend hosting, or production claims, the static host readiness slice adds domain/alternate-host policy and validation without DNS, CNAME, provider config, alternate-host deployment, backend hosting, or live probes, the live backend handoff slice reserves `/api/v1` endpoint families, capability flags, and error-envelope expectations without making `/api/v1` live, deploying a backend, enabling live probes, or creating production API guarantees, the live probe gateway contract records disabled source-probe policy, source caps, cache/evidence expectations, and operator gates without implementing probes or making network calls, the Rust source-registry catch-up updates the isolated Rust source model to current Python capability/coverage/source shapes without runtime wiring, the Rust query-planner candidate adds isolated Rust planner parity against expanded Python-oracle goldens without runtime wiring, Rust Local Index Parity Planning v0 adds a planning-only parity lane with no Rust index implementation or runtime wiring, the compatibility surface strategy records surface capability/route matrices plus old-client/native/snapshot/relay readiness without new runtime behavior, Signed Snapshot Format v0 adds a deterministic repo-local seed example with checksums and signature-placeholder docs only, without real signing keys, production signatures, executable downloads, a public `/snapshots/` route, relay behavior, native-client runtime, live backend behavior, or live probes, Signed Snapshot Consumer Contract v0 defines future snapshot consumption read order, checksum/signature-placeholder handling, and consumer profiles without adding a consumer runtime, relay, native client, production signing, keys, downloads, live backend, or live probes, Native Client Contract v0 defines future Windows/macOS/native client lanes, inputs, readiness checks, and action prohibitions while adding no native projects, GUI, FFI, installers, downloads, relay sidecars, live probes, or Rust wiring, and Relay Surface Design v0 records future local/LAN relay policy without adding a relay runtime, protocol server, network listener, private data exposure, live-probe passthrough, or write/admin route.

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

LIVE_ALPHA_00 Static Public Site Pack now lives under `public_site/` and adds
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
publication inventory, validates `public_site/`, checks the Pages artifact, and
uploads only `public_site/` as a static Pages artifact. It does not deploy the
Python backend, enable live probes, add a custom domain, add secrets, introduce
a generator, or claim deployment success without GitHub Actions evidence.

Static Site Generation Migration v0 now lives under `site/` and adds a
stdlib-only static-site source tree, templates, page JSON, `site/build.py`,
`site/validate.py`, and generated `site/dist/` output for validation. The
GitHub Pages workflow still deploys `public_site/`; this migration does not
add Node/npm, a frontend framework, deployment changes, live backend behavior,
live probes, or production-readiness claims.

Generated Public Data Summaries v0 now adds deterministic static JSON under
`public_site/data/` and generated `site/dist/data/`, covering site, page,
source, eval, route, and build summaries from governed repo inputs. These
summaries are not a live API, do not add live probes or external observations,
and do not make production JSON stability claims.

Lite/Text/Files Seed Surfaces v0 now adds static compatibility seed surfaces
under `public_site/lite/`, `public_site/text/`, and `public_site/files/`, plus
generated validation copies under `site/dist/`. These surfaces reuse the public
data summaries for old-browser HTML, plain text, and file-tree browsing with
SHA256SUMS, but they add no live search, executable downloads, snapshots,
relay/native runtime behavior, or production support claim.

Static Resolver Demo Snapshots v0 now adds static no-JS resolver examples
under `public_site/demo/`, plus generated validation copies under
`site/dist/demo/`. The demos show fixture-backed query planning, member
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

## Immediate Next Milestone

The next implementation milestone is:

> Native Action / Download / Install Policy v0

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
Consumer Contract v0, Native Client Contract v0, Relay Surface
Design v0, Rust Source Registry Parity Catch-up v0, and Rust Local Index
Parity Planning v0 now
mark the start of a more evidence-led backend phase. Rust source-registry
parity now catches up to the expanded Python source capability and coverage
shape for the current nine-source inventory without wiring Rust into runtime
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
