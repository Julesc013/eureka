# Eureka

**Local-first temporal object resolution for archived and current digital
objects.**

Eureka is a reference backend prototype for turning vague requests into
evidence-backed, actionable resolution results. It combines governed source
registries, deterministic planning, local indexing, resolution runs, bounded
provenance, evals, and public-alpha safety checks to answer questions like
"which exact thing should I inspect, fetch, compare, or preserve next?"

**Current status:** Python reference backend prototype / not production.
See [Bootstrap Status](docs/BOOTSTRAP_STATUS.md) and
[Roadmap](docs/ROADMAP.md).

## Why Eureka Exists

Archive and software searches often return the wrong unit of work. A user asks
for an old driver, a pre-support-drop browser release, an app for Windows 7, or
an article inside a scanned magazine, and gets an ISO, a ZIP, a support CD, a
dead website, or a noisy result list. The real work is then manual detective
work:

- containers must be opened before the useful member is visible
- versions, platforms, and compatibility constraints matter
- metadata is inconsistent or absent
- sources disagree or preserve different fragments
- misses rarely explain what was checked
- provenance is often collapsed into one uninspectable answer

Eureka treats search as an investigation. Its direction is to find the smallest
actionable unit supported by evidence, preserve disagreement, explain absence,
and route the user toward a bounded next step without pretending uncertain
results are canonical truth.

## What Eureka Is / Is Not

| Eureka is | Eureka is not |
| --- | --- |
| A temporal object resolver | A production search engine |
| A local-first Python reference backend | An open-internet hosted service |
| An evidence-backed archive/search prototype | An app store, installer, or downloader |
| A governed monorepo for backend, contracts, evals, and surfaces | A native GUI app |
| An eval-governed research-to-product codebase | An LLM-first search wrapper |
| A future Rust migration lane with Python-oracle parity fixtures | An active Rust production backend |

## Current Capabilities

| Area | Current bounded capability |
| --- | --- |
| Source and ingestion | Source Registry v0, Source Coverage and Capability Model v0, Real Source Coverage Pack v0, synthetic fixtures, recorded GitHub Releases fixtures, recorded Internet Archive-like fixtures, local bundle fixtures, article/scan recorded fixtures, governed source IDs, explicit placeholder posture for future sources |
| Resolution and search | exact resolution, deterministic search, Query Planner v0 plus Old-Platform Software Planner Pack v0, local SQLite index with FTS5 preferred and deterministic fallback |
| Evidence and explanation | provenance summaries, source summaries, source-backed compatibility evidence, absence reasoning, comparison/disagreement, subject/state timelines |
| Actions and artifacts | representation/access-path summaries, compatibility checks, strategy-aware action plans, handoff selection, acquisition/fetch, ZIP decomposition, member preview/readback, manifest and bundle export, bundle inspection, local stored artifacts |
| Backend infrastructure | Resolution Run Model v0, Local Worker and Task Model v0, Resolution Memory v0, architecture-boundary checker |
| Surfaces | server-rendered HTML workbench, stdlib local HTTP API, stdlib CLI surface |
| Operations and evals | Archive Resolution Eval Runner v0, Search Usefulness Audit v0, Search Usefulness Backlog Triage v0, Search Usefulness Audit Delta v0/v1, Hard Eval Satisfaction Pack v0, Old-Platform Result Refinement Pack v0, More Source Coverage Expansion v1, Article/Scan Fixture Pack v0, Manual External Baseline Observation Pack v0, Manual Observation Batch 0, Manual Observation Entry Helper v0, LIVE_ALPHA_00 Static Public Site Pack, LIVE_ALPHA_01 Production Public-Alpha Wrapper, Public Publication Plane Contracts v0, GitHub Pages Deployment Enablement v0, Static Site Generation Migration v0, Generated Public Data Summaries v0, Lite/Text/Files Seed Surfaces v0, Static Resolver Demo Snapshots v0, Custom Domain / Alternate Host Readiness v0, Live Backend Handoff Contract v0, Live Probe Gateway Contract v0, Signed Snapshot Format v0, Signed Snapshot Consumer Contract v0, Native Client Contract v0, Native Action / Download / Install Policy v0, Native Local Cache / Privacy Policy v0, Native Client Project Readiness Review v0, Test/Eval Operating Layer v0, Comprehensive Repo Audit v0, Hard Test Pack v0, Public Alpha Safe Mode v0, Deployment Readiness Review, Hosting Pack v0, Python-oracle golden fixture pack |
| Rust lane | minimal workspace plus isolated source-registry and query-planner parity candidates; not wired into Python runtime or surfaces |

The current corpus is intentionally small. The current archive-resolution hard
eval packet is satisfied under strict fixture-backed checks, but that does not
mean broad corpus coverage or production ranking exists. Search Usefulness
Audit still records many source, compatibility, planner, representation, and
member-access gaps.
External Google and Internet Archive baselines remain pending/manual; Manual
Observation Batch 0 only prepares 39 prioritized slots for later human
observation and records no external results.
The static public site pack under `public_site/` and Public Alpha Rehearsal
Evidence v0 under `docs/operations/public_alpha_rehearsal_evidence_v0/` are
documentation/evidence packs for later hosting review. They do not deploy
Eureka, add backend hosting, add live source probes, scrape external systems,
or claim production readiness.
The public-alpha wrapper under `scripts/run_public_alpha_server.py` adds a
localhost-default process/config guard for future supervised rehearsals. It
does not deploy, add provider files, enable live probes, add auth/TLS/rate
limiting/process management, or approve production.
Public Publication Plane Contracts v0 under
`control/inventory/publication/` now governs public routes, route stability,
status vocabulary, client profiles, public data files, base-path portability,
deployment target semantics, and redirects before any GitHub Pages deployment
or static-generation migration. The contract slice itself added no deployment
workflow, generator, DNS, provider configuration, live backend behavior, or
external observations.
GitHub Pages Deployment Enablement v0 now adds a workflow and artifact checker
for publishing only `public_site/` as a static Pages artifact after validation.
It does not deploy the Python backend, enable live probes, add a custom domain,
introduce a generator, or claim a successful public deployment without GitHub
Actions evidence.
Static Site Generation Migration v0 now adds a stdlib-only `site/` source tree
and generator that renders no-JS pages into `site/dist/` for validation.
`public_site/` remains the GitHub Pages deployment artifact; generated output
is not deployed yet and no Node/npm or frontend framework is introduced.
Generated Public Data Summaries v0 now adds deterministic static JSON summaries
under `public_site/data/` and `site/dist/data/` for page, source, eval, route,
and build state. These files now feed the lite/text/files seed surfaces and
remain inputs for future snapshot, relay, and native-client consumers; they are
not a live API, do not add live probes or external observations, and do not
make production stability claims.
Lite/Text/Files Seed Surfaces v0 now adds static compatibility seed surfaces
under `public_site/lite/`, `public_site/text/`, and `public_site/files/`, with
generated validation copies under `site/dist/`. They are no-JS/no-download
publication surfaces for old browsers, text readers, file-tree browsing, and
future snapshot/relay/native-client planning; they are not live search,
snapshots, relay behavior, native-client runtime, executable mirrors, or
production support claims.
Static Resolver Demo Snapshots v0 now adds fixture-backed static no-JS resolver
examples under `public_site/demo/` and generated validation copies under
`site/dist/demo/`. They show query planning, member-level results,
compatibility evidence, absence, comparison, source detail, article/scan
fixtures, and eval summaries; they are not live search, a live API, backend
hosting, external observations, or production resolver behavior.
Custom Domain / Alternate Host Readiness v0 now adds governed domain and
alternate-static-host readiness records, base-path portability guidance,
operator checklist, and `scripts/validate_static_host_readiness.py`. It does
not configure DNS, add `public_site/CNAME`, deploy an alternate host, add
provider config, enable live probes, host a backend, or claim production
readiness.
Live Backend Handoff Contract v0 now adds contract-only `/api/v1` route
reservations, disabled live capability flags, and a future error-envelope
reference. It does not deploy or host a backend, make `/api/v1` live, enable
live probes, finalize CORS/auth/rate-limit policy, or create production API
guarantees.
Live Probe Gateway Contract v0 now adds disabled-by-default source-probe
policy, candidate source limits, cache/evidence expectations, and operator
gates before any external probe. It does not implement live probes, call
Internet Archive, Wayback, GitHub, Software Heritage, package registries, or
other external sources, fetch URLs, scrape, crawl, enable downloads, or turn
Google into a live probe source.
Rust Query Planner Parity Candidate v0 now adds an isolated deterministic Rust
planner model under `crates/eureka-core/`, expands Python-oracle planner
goldens, and adds a stdlib parity-structure check. Python remains the planner
oracle; Rust is not wired into web, CLI, HTTP API, workers, public-alpha paths,
or production runtime.
Rust Source Registry Parity Catch-up v0 updates the isolated Rust source model
to the current nine-source Python capability/coverage shape. Rust Local Index
Parity Planning v0 adds the future local-index parity plan, cases, acceptance
schema, and validator only; it does not implement a Rust index, add SQLite
behavior, or wire Rust into runtime surfaces.
Compatibility Surface Strategy v0 now adds governed multi-surface strategy,
expanded surface capability records, a surface route matrix, old-client
degradation policy, and native/snapshot/relay readiness docs. It does not add
new runtime behavior, snapshots, relay services, native app projects, live
`/api/v1`, live probes, or production API guarantees.
Signed Snapshot Format v0 now adds an experimental static/offline snapshot
contract and a deterministic seed example under
`snapshots/examples/static_snapshot_v0/`, with checksums and
signature-placeholder documentation only. It does not add real signing keys,
production signatures, executable downloads, a public `/snapshots/` route,
relay services, native-client runtime, live backend behavior, or live probes.
Signed Snapshot Consumer Contract v0 defines how future file-tree, text, lite
HTML, relay, native, and audit consumers should read that snapshot format,
validate checksums, and treat v0 signatures as placeholders. It does not
implement a snapshot reader runtime, relay, native client, production signing,
real signing keys, executable downloads, live backend behavior, or live probes.
Native Client Contract v0 defines future Windows/macOS/native client inputs,
lane policy, readiness checks, and prohibited actions while keeping CLI as the
only current native-like surface. It does not create Visual Studio or Xcode
projects, native GUI apps, FFI, installer automation, package-manager behavior,
download/execution automation, relay sidecars, live probes, or Rust runtime
wiring.
Native Action / Download / Install Policy v0 defines future inspect, preview,
export, download, mirror, install handoff, package-manager handoff, execute,
restore, uninstall, rollback, malware-scan, and rights/access policy before any
native or public download surface exists. It does not implement downloads,
installers, package-manager integration, malware scanning, rights clearance,
native clients, relay runtime, or executable trust claims.
Native Local Cache / Privacy Policy v0 defines future public/private cache,
local path, user state, resolution memory, telemetry/logging, credentials,
deletion/export/reset, portable-mode, snapshot, relay, and public-alpha privacy
policy before native project readiness work. It does not implement cache
runtime, private file ingestion, local archive scanning, telemetry, analytics,
accounts, cloud sync, uploads, native clients, or relay runtime.

## Quickstart

### Requirements

- Python 3
- no third-party Python packages for the current executable lane
- optional Rust toolchain only for the `crates/` workspace checks

```bash
git clone https://github.com/Julesc013/eureka.git
cd eureka
```

### Verify the Repo

```bash
python -m unittest discover -s runtime -t .
python -m unittest discover -s surfaces -t .
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
python scripts/validate_live_backend_handoff.py
python scripts/validate_live_probe_gateway.py
python scripts/validate_compatibility_surfaces.py
python scripts/check_rust_query_planner_parity.py
```

### Run Evals and Safety Checks

```bash
python scripts/run_archive_resolution_evals.py
python scripts/run_archive_resolution_evals.py --json
python scripts/run_search_usefulness_audit.py
python scripts/public_alpha_smoke.py
python scripts/run_public_alpha_server.py --check-config
python scripts/generate_python_oracle_golden.py --check
python -m unittest discover -s tests/hardening -t .
python scripts/validate_public_static_site.py
python scripts/validate_publication_inventory.py
python scripts/check_github_pages_static_artifact.py
python site/build.py --check
python site/validate.py
python scripts/generate_public_data_summaries.py --check
python scripts/generate_compatibility_surfaces.py --check
python scripts/generate_static_resolver_demos.py --check
python scripts/validate_live_probe_gateway.py
python scripts/validate_compatibility_surfaces.py
python scripts/generate_static_snapshot.py --check
python scripts/validate_static_snapshot.py
python scripts/validate_snapshot_consumer_contract.py
python scripts/validate_native_client_contract.py
python scripts/validate_action_policy.py
python scripts/validate_local_cache_privacy_policy.py
python scripts/check_rust_query_planner_parity.py
python scripts/generate_public_alpha_rehearsal_evidence.py --check
```

For larger tasks, the command registry and lane guidance live in
`control/inventory/tests/` and
`docs/operations/TEST_AND_EVAL_LANES.md`.

### Try the CLI

```bash
python scripts/demo_cli_workbench.py resolve fixture:software/synthetic-demo-app@1.0.0
python scripts/demo_cli_workbench.py search archive
python scripts/demo_cli_workbench.py query-plan "Windows 7 apps"
python scripts/demo_cli_workbench.py sources
python scripts/demo_cli_workbench.py evals-archive-resolution --task windows_7_apps --json
```

### Try the Local HTTP API Helper

```bash
python scripts/demo_http_api.py --mode public_alpha status
python scripts/demo_http_api.py query-plan "Windows 7 apps"
python scripts/demo_http_api.py sources
python scripts/demo_http_api.py resolve github-release:cli/cli@v2.65.0
```

### Try the Web Workbench

Render one page to stdout:

```bash
python scripts/demo_web_workbench.py --render-once
python scripts/demo_web_workbench.py --render-once --search-query archive
```

Start the local stdlib server in trusted local-dev mode:

```bash
python scripts/demo_web_workbench.py --mode local_dev
```

Start the constrained public-alpha mode locally:

```bash
python scripts/run_public_alpha_server.py --check-config
python scripts/run_public_alpha_server.py --print-config-json
python scripts/demo_web_workbench.py --mode public_alpha --host 127.0.0.1 --port 8080
```

`public_alpha` blocks caller-provided local filesystem controls. It is a
supervised demo posture, not production hosting.

### Optional Rust Checks

Run these only where Cargo is installed:

```bash
cargo check --workspace --manifest-path crates/Cargo.toml
cargo test --workspace --manifest-path crates/Cargo.toml
```

The Rust workspace is not an active backend. Python remains the reference
runtime and oracle.

## Example Workflows

### Compile a Hard Archive Query

```bash
python scripts/demo_cli_workbench.py query-plan "Windows 7 apps"
```

This runs the deterministic Query Planner v0 and emits the bounded
`ResolutionTask` shape for a hard archive-resolution query family.

### Build and Query a Local Index

```bash
python scripts/demo_cli_workbench.py index-build --index-path .demo-index/eureka-local-index.sqlite3 --json
python scripts/demo_cli_workbench.py index-query archive --index-path .demo-index/eureka-local-index.sqlite3 --json
```

This is a local-dev workflow. Public-alpha mode blocks arbitrary caller-provided
local path controls.

### Inspect Source Registry State

```bash
python scripts/demo_cli_workbench.py sources
python scripts/demo_cli_workbench.py sources --coverage-depth source_known
python scripts/demo_cli_workbench.py sources --capability recorded_fixture_backed
python scripts/demo_cli_workbench.py source github-releases-recorded-fixtures
```

This shows the governed source inventory, capability flags, coverage depth, and
placeholder posture through the public boundary. Placeholder sources remain
placeholders; this does not imply live connector support.

### Run the Archive Eval Harness

```bash
python scripts/run_archive_resolution_evals.py --task windows_7_apps
```

The eval runner reports satisfied, partial, not-satisfied, not-evaluable, and
capability-gap checks. It is not a ranking benchmark.

### Run the Search Usefulness Audit

```bash
python scripts/run_search_usefulness_audit.py --query windows_7_apps
```

The usefulness audit runs a broad local query pack and aggregates source,
planner, index, decomposition, representation, compatibility, actionability,
and UX gaps. Google and Internet Archive baselines are pending manual
observations; the script performs no scraping.

### Check Public-Alpha Posture

```bash
python scripts/public_alpha_smoke.py
python scripts/demo_http_api.py --mode public_alpha status
```

These checks exercise safe public-alpha routes and blocked local-path routes
without deploying anything.

## Architecture At a Glance

```text
raw query or target_ref
  -> query planner / exact resolver / deterministic search
  -> source registry + local corpus + optional local index
  -> resolution run, evidence, absence, representations, actions
  -> gateway public boundary
  -> CLI / HTML / local HTTP API
  -> memory, evals, public-alpha checks, Python-oracle goldens
```

Boundary rule of thumb:

```text
control/       governance and inventories
contracts/     governed schemas and surface contracts
runtime/engine engine behavior and interfaces
runtime/gateway public runtime boundary
surfaces/      CLI, HTML, and local HTTP API
crates/        future Rust lane, isolated from active runtime
```

The accepted architecture frames Eureka through:

- six logical graphs:
  [object, representation, temporal, claim/provenance, access/action,
  user/strategy](docs/architecture/LOGICAL_GRAPHS.md)
- five physical subsystem directions:
  [CAS store, canonical core, lexical index, semantic recall index,
  worker plane](docs/architecture/PHYSICAL_SUBSYSTEMS.md)

Only bounded Python reference slices are active today. Vector/semantic recall,
production queues, and production Rust services remain future work.

## Repository Map

| Path | Purpose |
| --- | --- |
| `.aide/` | Repo-operating metadata only; not product runtime behavior |
| `contracts/` | Governed schemas, protocols, public API contracts, UI contracts |
| `control/` | Governance material, source inventory, route inventory, research notes |
| `control/inventory/publication/` | Public publication-plane contracts for routes, client profiles, data files, deployment targets, redirects, and base-path portability |
| `crates/` | Future Rust backend lane; currently skeleton plus source-registry parity candidate |
| `docs/` | Vision, architecture, roadmap, operations, standards, decisions |
| `docs/operations/public_alpha_hosting_pack/` | Supervised public-alpha hosting-pack runbook and templates |
| `docs/operations/public_alpha_rehearsal_evidence_v0/` | Supervised local/static public-alpha rehearsal evidence pack; no deployment approval |
| `evals/` | Archive-resolution eval packet and related eval scaffolding |
| `public_site/` | No-JS static public artifact for static Pages publication review; no backend or live source behavior |
| `runtime/` | Python reference engine, connectors, gateway public boundary, source registry |
| `scripts/` | Demo commands, eval runner, safety checks, golden generators |
| `snapshots/` | Static/offline snapshot format schema and deterministic seed examples; no real keys or executable downloads |
| `surfaces/` | Server-rendered web workbench, local HTTP API, native CLI surface |
| `tests/` | Integration, operations, parity, architecture, and script tests |

## Documentation Map

Start here:

- [Bootstrap Status](docs/BOOTSTRAP_STATUS.md)
- [Roadmap](docs/ROADMAP.md)
- [Decisions](docs/DECISIONS.md)
- [Open Questions](docs/OPEN_QUESTIONS.md)
- [Scripts](scripts/README.md)

Product and doctrine:

- [Eureka Thesis](docs/vision/EUREKA_THESIS.md)
- [Doctrine](docs/vision/DOCTRINE.md)
- [Product Promise](docs/vision/PRODUCT_PROMISE.md)
- [Temporal Object Resolver](docs/architecture/TEMPORAL_OBJECT_RESOLVER.md)
- [Research note: temporal object resolution engine](control/research/temporal-object-resolution-engine.md)

Architecture:

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Logical Graphs](docs/architecture/LOGICAL_GRAPHS.md)
- [Physical Subsystems](docs/architecture/PHYSICAL_SUBSYSTEMS.md)
- [Query Planner](docs/architecture/QUERY_PLANNER.md)
- [Resolution Memory](docs/architecture/RESOLUTION_MEMORY.md)
- [AI Policy](docs/architecture/AI_POLICY.md)
- [Rust Backend Lane](docs/architecture/RUST_BACKEND_LANE.md)
- [Publication Plane](docs/architecture/PUBLICATION_PLANE.md)
- [Live Probe Gateway](docs/architecture/LIVE_PROBE_GATEWAY.md)
- [Compatibility Surfaces](docs/architecture/COMPATIBILITY_SURFACES.md)

Roadmaps and operations:

- [Backend Roadmap](docs/roadmap/BACKEND_ROADMAP.md)
- [Public Alpha](docs/roadmap/PUBLIC_ALPHA.md)
- [Rust Migration](docs/roadmap/RUST_MIGRATION.md)
- [Native Apps Later](docs/roadmap/NATIVE_APPS_LATER.md)
- [Public Alpha Safe Mode](docs/operations/PUBLIC_ALPHA_SAFE_MODE.md)
- [Public Alpha Readiness Review](docs/operations/PUBLIC_ALPHA_READINESS_REVIEW.md)
- [Public Alpha Hosting Pack](docs/operations/public_alpha_hosting_pack/README.md)
- [Public Route Contract](docs/reference/PUBLIC_ROUTE_CONTRACT.md)
- [Public Data Contract](docs/reference/PUBLIC_DATA_CONTRACT.md)
- [Client Profile Contract](docs/reference/CLIENT_PROFILE_CONTRACT.md)
- [Live Probe Gateway Contract](docs/reference/LIVE_PROBE_GATEWAY_CONTRACT.md)
- [Snapshot Format Contract](docs/reference/SNAPSHOT_FORMAT_CONTRACT.md)
- [Snapshot Signature Policy](docs/reference/SNAPSHOT_SIGNATURE_POLICY.md)
- [Test and Eval Lanes](docs/operations/TEST_AND_EVAL_LANES.md)
- [Hard Test Pack](docs/operations/HARD_TEST_PACK.md)
- [Comprehensive Audit Pack](control/audits/2026-04-25-comprehensive-test-eval-audit/README.md)
- [Search Usefulness Backlog Triage](control/backlog/search_usefulness_triage/README.md)
- [Search Usefulness Audit Delta](control/audits/search-usefulness-delta-v0/README.md)

Evals and parity:

- [Archive Resolution Evals](evals/archive_resolution/README.md)
- [Search Usefulness Audit](evals/search_usefulness/README.md)
- [Search Benchmark Design](docs/evals/SEARCH_BENCHMARK_DESIGN.md)
- [Rust Parity Plan](tests/parity/PARITY_PLAN.md)
- [Python Oracle Golden Fixtures](tests/parity/golden/python_oracle/v0/README.md)

## Current Maturity

Eureka is substantial, but it is still a prototype/reference backend:

- Python is the executable specification, reference backend, and oracle.
- Public-alpha safe mode exists, but it is not production deployment.
- The public-alpha wrapper exists as a local process/config guard; it is not
  hosting infrastructure or production approval.
- Public Publication Plane Contracts v0 exist as route/data/client/deployment
  inventory governance. They do not deploy anything or add static generation.
- GitHub Pages Deployment Enablement v0 configures a static-only workflow for
  `public_site/`, with deployment success still unverified until GitHub Actions
  evidence exists.
- Static Site Generation Migration v0 adds a stdlib-only generator under
  `site/` that builds `site/dist/` for validation. It does not switch the
  Pages artifact away from `public_site/`.
- Generated Public Data Summaries v0 adds static machine-readable summaries
  under `public_site/data/` and generated `site/dist/data/`. They are not live
  API semantics and do not add external observations.
- Lite/Text/Files Seed Surfaces v0 adds static compatibility seed surfaces
  under `public_site/lite/`, `public_site/text/`, and `public_site/files/`.
  They do not add live search, downloads, snapshots, relay behavior, or native
  runtime.
- Static Resolver Demo Snapshots v0 adds static fixture-backed demo pages under
  `public_site/demo/`. They do not add live search, a live API, external
  observations, backend hosting, or production behavior.
- Custom Domain / Alternate Host Readiness v0 adds static-host portability
  contracts and validation. It does not configure DNS, add CNAME, deploy an
  alternate host, add provider config, or make Eureka production-ready.
- Live Backend Handoff Contract v0 reserves `/api/v1`, capability flags, and
  an error-envelope expectation for a future hosted backend. It does not make
  `/api/v1` live, deploy backend hosting, enable live probes, or create a
  stable production API.
- Live Probe Gateway Contract v0 defines disabled-by-default source-probe
  policy, per-source caps, cache/evidence expectations, and operator gates.
  It does not implement probes, call external sources, fetch URLs, scrape,
  crawl, enable downloads, or promote Google beyond manual baselines.
- The hosting pack supports supervised rehearsal evidence, not open-internet
  approval.
- Rust has a workspace, parity fixtures, and isolated source-registry plus
  query-planner candidates. It does not replace Python and is not used by web,
  CLI, HTTP API, workers, public-alpha paths, or production paths.
- Compatibility Surface Strategy v0 is strategy/contracts/inventory only. It
  guides old-browser, text, file-tree, snapshot, relay, API, CLI, web, and
  future native clients without implementing snapshots, relay services, native
  apps, live API behavior, or new runtime behavior.
- Signed Snapshot Format v0 is a contract and deterministic seed example only.
  It does not add real signing keys, production signatures, executable
  downloads, a public `/snapshots/` route, relay behavior, native-client
  runtime, live backend behavior, or live probes.
- Signed Snapshot Consumer Contract v0 is contract/design only. It does not
  implement a snapshot reader runtime, relay, native client, production signing,
  real signing keys, executable downloads, live backend behavior, or live
  probes.
- Native Client Contract v0 is contract/design only. It does not create native
  app projects, GUI clients, FFI, installer automation, downloads, relay
  sidecars, live probes, or Rust runtime wiring; CLI remains the only current
  native-like surface.
- Native Action / Download / Install Policy v0 is policy/contract only. It does
  not implement downloads, installers, package-manager integration, malware
  scanning, rights clearance, native clients, relay runtime, or executable
  trust claims.
- Native Local Cache / Privacy Policy v0 is policy/contract only. It does not
  implement local cache runtime, private file ingestion, local archive scanning,
  telemetry, analytics, accounts, cloud sync, uploads, native clients, or relay
  runtime.
- Native Client Project Readiness Review v0 is review/evidence only. It records
  the decision `ready_for_minimal_project_skeleton_after_human_approval` for the
  `windows_7_x64_winforms_net48` lane, but it does not create Visual Studio or
  Xcode projects, native app source trees, GUI behavior, FFI, cache runtime,
  downloads, installers, relay runtime, live probes, or runtime wiring.
- Native apps are deferred. The current native surface is a stdlib CLI proof.
- Live crawling, source sync, fuzzy retrieval, vector search, LLM planning,
  auth, accounts, HTTPS/TLS, rate limiting, process supervision, and deployment
  infrastructure are intentionally out of scope. Current result lanes and
  user-cost scores are bounded deterministic hints, not production ranking.

## Roadmap

Accepted immediate next milestone:

1. Windows 7 WinForms Native Skeleton Planning v0, not implementation
2. Relay Prototype Planning v0, not implementation
3. Rust Local Index Parity Candidate v0 only after planning review and Cargo
   availability expectations are explicit
4. Manual Observation Batch 0 Execution (human-operated parallel work)
5. Internet Archive Live Probe v0 only after explicit human approval and
   separate implementation review

Broader near-term direction:

1. keep the GitHub Pages workflow static-only and driven by publication-plane
   contracts, with `public_site/` as the only uploaded artifact
2. keep validating generated `site/dist/` against the current `public_site/`
   artifact before changing the Pages deployment artifact
3. fill a first manual Google and Internet Archive baseline batch without
   scraping or fabricated comparisons
4. keep using audit deltas to measure source, planner, representation,
   member, lane, and compatibility-evidence movement
5. keep Python as oracle while adding Rust candidates only when parity fixtures
   exist
6. preserve public-alpha safety checks and capture rehearsal evidence
7. keep snapshot contracts checksum/signature-policy governed before relay or
   native-client consumption
8. expand source and eval coverage without weakening hard queries
9. harden backend contracts, run models, memory, and local index behavior
10. move toward hosted alpha only after explicit blockers are resolved
11. keep native app shells later, after backend infrastructure is stronger

No exact dates are promised.

## Development Rules

- Keep the Python executable lane stdlib-only unless the repo deliberately
  changes that policy.
- Preserve architecture boundaries; surfaces must not import engine internals.
- Use gateway public APIs from web, CLI, and HTTP-facing code.
- Treat evals and Python-oracle goldens as guardrails, not decoration.
- Use the test registry and command matrix when choosing verification lanes for
  larger tasks.
- Do not claim production readiness without evidence and accepted decisions.
- For nontrivial Codex/agent tasks, work in two passes: implementation, then
  hardening.
- Verify before claiming completion.
- Sync the branch to origin at the end of each completed prompt/task when the
  environment supports it.

Useful checks:

```bash
python -m unittest discover -s runtime -t .
python -m unittest discover -s surfaces -t .
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
python scripts/public_alpha_smoke.py
python scripts/validate_publication_inventory.py
python -m unittest discover -s tests/hardening -t .
```

## Contributing

There is not yet a formal open-source contribution process. For now, useful
contributions should be small, evidence-backed, boundary-preserving, and honest
about maturity. Start with the docs above, run the verification commands, and
avoid broadening scope into production deployment, native apps, live crawling,
or ungoverned retrieval semantics.

## License

No license file is present in this repository yet. Licensing is not finalized.

## Acknowledgements

Eureka is shaped by the archive, preservation, software-history, search,
package-inspection, and reproducibility ecosystems. This README also borrows
general quality principles from public README curation projects: strong
opening identity, honest status, useful quickstart commands, clear navigation,
and no decorative claims the repo cannot support.

## Current Checkpoint

Post-Queue State Checkpoint v0 now lives under
`control/audits/post-queue-state-checkpoint-v0/`. It records the post-P01..P09
repo state, verification results, eval/audit status, external-baseline pending
status, risks, deferrals, and next recommended work. It is audit/reporting only
and does not add product runtime behavior, deployment behavior, live probes,
external observations, production signing, relay services, or native clients.
