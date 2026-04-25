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
| Source and ingestion | Source Registry v0, synthetic fixtures, recorded GitHub Releases fixtures, governed source IDs |
| Resolution and search | exact resolution, deterministic search, query planning, local SQLite index with FTS5 preferred and deterministic fallback |
| Evidence and explanation | provenance summaries, source summaries, absence reasoning, comparison/disagreement, subject/state timelines |
| Actions and artifacts | representation/access-path summaries, compatibility checks, strategy-aware action plans, handoff selection, acquisition/fetch, ZIP decomposition, member preview/readback, manifest and bundle export, bundle inspection, local stored artifacts |
| Backend infrastructure | Resolution Run Model v0, Local Worker and Task Model v0, Resolution Memory v0, architecture-boundary checker |
| Surfaces | server-rendered HTML workbench, stdlib local HTTP API, stdlib CLI surface |
| Operations and evals | Archive Resolution Eval Runner v0, Public Alpha Safe Mode v0, Deployment Readiness Review, Hosting Pack v0, Python-oracle golden fixture pack |
| Rust lane | minimal workspace plus first isolated source-registry parity candidate; not wired into Python runtime or surfaces |

The current corpus is intentionally small. Many archive-resolution eval tasks
are expected to report partial results, not-satisfied checks, or capability
gaps. That honesty is part of the benchmark.

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
```

### Run Evals and Safety Checks

```bash
python scripts/run_archive_resolution_evals.py
python scripts/run_archive_resolution_evals.py --json
python scripts/public_alpha_smoke.py
python scripts/generate_python_oracle_golden.py --check
```

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
python scripts/demo_cli_workbench.py source github-releases-recorded-fixtures
```

This shows the governed source inventory through the public boundary.

### Run the Archive Eval Harness

```bash
python scripts/run_archive_resolution_evals.py --task windows_7_apps
```

The eval runner reports satisfied, partial, not-satisfied, not-evaluable, and
capability-gap checks. It is not a ranking benchmark.

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
| `crates/` | Future Rust backend lane; currently skeleton plus source-registry parity candidate |
| `docs/` | Vision, architecture, roadmap, operations, standards, decisions |
| `docs/operations/public_alpha_hosting_pack/` | Supervised public-alpha rehearsal evidence packet |
| `evals/` | Archive-resolution eval packet and related eval scaffolding |
| `runtime/` | Python reference engine, connectors, gateway public boundary, source registry |
| `scripts/` | Demo commands, eval runner, safety checks, golden generators |
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

Roadmaps and operations:

- [Backend Roadmap](docs/roadmap/BACKEND_ROADMAP.md)
- [Public Alpha](docs/roadmap/PUBLIC_ALPHA.md)
- [Rust Migration](docs/roadmap/RUST_MIGRATION.md)
- [Native Apps Later](docs/roadmap/NATIVE_APPS_LATER.md)
- [Public Alpha Safe Mode](docs/operations/PUBLIC_ALPHA_SAFE_MODE.md)
- [Public Alpha Readiness Review](docs/operations/PUBLIC_ALPHA_READINESS_REVIEW.md)
- [Public Alpha Hosting Pack](docs/operations/public_alpha_hosting_pack/README.md)

Evals and parity:

- [Archive Resolution Evals](evals/archive_resolution/README.md)
- [Search Benchmark Design](docs/evals/SEARCH_BENCHMARK_DESIGN.md)
- [Rust Parity Plan](tests/parity/PARITY_PLAN.md)
- [Python Oracle Golden Fixtures](tests/parity/golden/python_oracle/v0/README.md)

## Current Maturity

Eureka is substantial, but it is still a prototype/reference backend:

- Python is the executable specification, reference backend, and oracle.
- Public-alpha safe mode exists, but it is not production deployment.
- The hosting pack supports supervised rehearsal evidence, not open-internet
  approval.
- Rust has a workspace, parity fixtures, and one isolated source-registry
  candidate. It does not replace Python and is not used by web, CLI, HTTP API,
  workers, or production paths.
- Native apps are deferred. The current native surface is a stdlib CLI proof.
- Live crawling, source sync, ranking, fuzzy retrieval, vector search, LLM
  planning, auth, accounts, HTTPS/TLS, rate limiting, process supervision, and
  deployment infrastructure are intentionally out of scope.

## Roadmap

Accepted immediate next milestone:

1. Rust Query Planner Parity Candidate v0

Broader near-term direction:

1. keep Python as oracle while adding Rust candidates only when parity fixtures
   exist
2. preserve public-alpha safety checks and capture rehearsal evidence
3. expand source and eval coverage without weakening hard queries
4. harden backend contracts, run models, memory, and local index behavior
5. move toward hosted alpha only after explicit blockers are resolved
6. keep native app shells later, after backend infrastructure is stronger

No exact dates are promised.

## Development Rules

- Keep the Python executable lane stdlib-only unless the repo deliberately
  changes that policy.
- Preserve architecture boundaries; surfaces must not import engine internals.
- Use gateway public APIs from web, CLI, and HTTP-facing code.
- Treat evals and Python-oracle goldens as guardrails, not decoration.
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
