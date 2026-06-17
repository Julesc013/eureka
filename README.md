# Eureka

**Local-first temporal object resolution for hard-to-find digital artifacts.**

Eureka helps an operator turn vague needs such as "latest Firefox before XP
support ended", "driver for a ThinkPad T42 on Windows 2000", or "the article
inside that 1990s magazine scan" into evidence-backed investigation records:
candidate objects, source observations, representations, absence, uncertainty,
and safe next actions.

Unlike ordinary archive search, Eureka is designed to look past the outer
container. It cares about the smallest useful actionable unit, keeps provenance
visible, explains what is unknown, and separates candidate evidence from
accepted truth.

Eureka is currently a local-first Python reference backend and prototype with
local operator workflows, read-only public-alpha foundations, static/snapshot
foundations, and governed evals. It is not deployed, not publicly launched, and
does not claim production readiness.

## Why Eureka Exists

Hard digital-object searches often fail for practical reasons:

- useful files are hidden inside ZIPs, ISOs, support CDs, scans, source
  releases, WARC captures, and dead vendor pages
- metadata is incomplete, inconsistent, or split across sources
- time, version, platform, compatibility, and representation constraints matter
- ordinary search usually returns an outer container, not the actionable member
- failed searches rarely explain what was checked, skipped, or still unknown

Eureka's long-term promise is to reduce detective work: preserve the evidence,
show disagreements, identify the smallest useful unit, and turn uncertainty
into reviewable next steps.

## Status At A Glance

Current branch details move faster than a public README. Use
[docs/STATUS.md](docs/STATUS.md) for the current development posture and
[docs/BOOTSTRAP_STATUS.md](docs/BOOTSTRAP_STATUS.md) for the baseline summary.

| Topic | Current posture | Read more |
| --- | --- | --- |
| Development branch | `dev` is the normal working branch | [Contributing](CONTRIBUTING.md) |
| Runtime lane | Python reference backend / oracle | [Architecture](docs/ARCHITECTURE.md) |
| Local use | Local instance validation, local server, Workbench, CLI/API surfaces | [Local HTTP API](docs/reference/LOCAL_HTTP_API.md) |
| Public alpha | Read-only, snapshot-backed foundations; not launched | [Public Alpha Launch Gates](docs/reference/PUBLIC_ALPHA_LAUNCH_GATES.md) |
| Deployment | Not performed; dry-run and launch remain gated | [Roadmap](docs/ROADMAP.md) |
| Live source fanout | Disabled unless a future reviewed task enables it | [Source Policy Gates](docs/operations/SOURCE_POLICY_GATES.md) |
| Public mutation | Disabled; review and promotion gates protect accepted records | [Master Index Review Queue](docs/reference/MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md) |
| Production readiness | Not claimed | [Security](SECURITY.md) |
| License | Restricted source-available, not open-source | [License](LICENSE.md) |
| Full discovery | Promotion/nightly/manual lane; use harness or CI artifacts | [Test and Eval Lanes](docs/operations/TEST_AND_EVAL_LANES.md) |

## What Eureka Is And Is Not

| Eureka is | Eureka is not |
| --- | --- |
| a temporal object resolver | a production hosted service |
| a local-first archive, software, document, and source-trace investigation backend | a publicly launched product |
| a Python reference implementation / oracle | a full Archive.org search engine or broad web crawler |
| an eval-governed prototype | an app store, installer, downloader, or marketplace manager |
| a multi-surface backend with CLI, local web, local HTTP API, static, text, and file projections | a native Mac/Windows marketplace app |
| a provenance and review workflow for candidates, evidence, absence, and actions | an LLM-first answer engine or AI truth authority |
| a future Rust parity and production-backend candidate lane | a finished Rust backend |
| a local-first, offline-capable direction | a guarantee of artifact safety, rights clearance, or legal permission |

## Current Capabilities

| Area | Current status | Notes and limitations | Deeper docs |
| --- | --- | --- | --- |
| Source inventory and connectors | Source registry, source-family model, governed metadata/source-wave foundations | Not a crawler; live source fanout and downloads are disabled by default | [Source Family Model](docs/architecture/SOURCE_FAMILY_MODEL.md), [Source Wave Runbook](docs/operations/SOURCE_WAVE_RUNBOOK.md) |
| Query planning and resolution | Local query planning, resolution runs, lanes, candidates, absence, and review handoffs | Current behavior is bounded by fixtures, local indexes, and accepted runtime slices | [Temporal Object Resolver](docs/architecture/TEMPORAL_OBJECT_RESOLVER.md), [Local Product Loop](docs/architecture/LOCAL_PRODUCT_LOOP.md) |
| Search and local index | Deterministic/local search foundations and public-search safety work | No broad corpus coverage or production ranking claim | [Search Benchmark Design](docs/evals/SEARCH_BENCHMARK_DESIGN.md), [Test and Eval Lanes](docs/operations/TEST_AND_EVAL_LANES.md) |
| Evidence and provenance | Evidence summaries, source observations, absence reports, promotion previews, and review gates | Candidates and observations are not accepted truth | [Doctrine](docs/vision/DOCTRINE.md), [Public Alpha Launch Gates](docs/reference/PUBLIC_ALPHA_LAUNCH_GATES.md) |
| Representations and archive inspection | Representation/access-path summaries plus bounded package-member inspection foundations | Broad extraction, arbitrary local-path access, and executable payload handling remain disabled or gated | [Data Model](docs/architecture/DATA_MODEL.md), [Action Download/Install Policy](docs/reference/ACTION_DOWNLOAD_INSTALL_POLICY.md) |
| Compatibility and action routing | Compatibility hints, action-plan foundations, local export/store flows, and local apply gates | No install, execute, package-manager, marketplace, or safety guarantee | [Local Apply Gate Runbook](docs/operations/LOCAL_APPLY_GATE_RUNBOOK.md), [Capability Profile](docs/reference/CAPABILITY_PROFILE.md) |
| Runs, tasks, memory, and evals | Local run/task records, deterministic evals, focused test lanes, and full-discovery harness | Full discovery is handled outside normal AI/chat work | [Operations Docs](docs/operations/README.md), [Eval Docs](docs/evals/README.md) |
| Surfaces | CLI, local web, local HTTP API, static site, lite/text/files, and Workbench projections | These are local or static foundations, not a hosted production product | [Local HTML Routes](docs/reference/LOCAL_HTML_ROUTES.md), [Surfaces](surfaces/README.md) |
| Public-alpha safety | Read-only, snapshot-backed public-alpha route foundations and blocked unsafe route checks | Public alpha is not public launch | [Public Alpha Read-Only Closeout](docs/operations/PUBLIC_ALPHA_READONLY_CLOSEOUT.md) |
| Rust parity lane | Isolated Rust crates and parity candidates exist | Python remains the reference oracle until explicit parity gates promote otherwise | [Rust Backend Lane](docs/architecture/RUST_BACKEND_LANE.md), [crates/](crates/README.md) |

## Quick Start

These commands are local and do not deploy Eureka.

Run focused checks:

```powershell
python scripts/eureka_test_select.py --changed --failed-first --json
python scripts/check_architecture_boundaries.py
python scripts/validate_public_alpha_readonly.py
python scripts/validate_snapshot_relay.py
```

When you have a local instance at `..\instances\default`, validate it and start
the local stdlib server:

```powershell
python scripts/eureka_validate_instance.py --instance ..\instances\default --json
python scripts/eureka_local_server.py --instance ..\instances\default --host 127.0.0.1 --port 8765 --operator-token local-dev-token
```

Useful local URLs after the server starts:

- <http://127.0.0.1:8765/>
- <http://127.0.0.1:8765/search?q=sampleproject>
- <http://127.0.0.1:8765/alpha>
- <http://127.0.0.1:8765/alpha/needs>

For public-alpha gate checks:

```powershell
python scripts/validate_public_alpha_hosting_readiness.py
python scripts/validate_public_alpha_launch_candidate.py
python scripts/public_alpha_smoke.py --json
```

Full unittest discovery is a promotion/nightly/manual lane. Run it through the
harness or CI, keep raw logs out of the repo, and review compact summaries:

```powershell
python scripts/run_full_unittest_discovery.py --out ..\eureka-test-runs\manual_full_discovery
```

## Example Use Cases

These examples describe what Eureka is meant to help investigate. They are not
claims that the current corpus fully satisfies every request.

| Need | Eureka should help by |
| --- | --- |
| "Windows 7 apps" | separating compatible candidates, unknowns, and unsafe assumptions |
| "latest Firefox before XP support ended" | preserving time/version constraints and evidence for why a release is in or out |
| "driver for ThinkPad T42 Wi-Fi Windows 2000" | tracking device/platform clues, source observations, support media, and gaps |
| "article about ray tracing in a 1994 magazine" | representing an article as a member inside a scan or issue, not just the outer item |
| "manual for Sound Blaster CT1740" | connecting model identifiers, manuals, source posture, and absence/conflict notes |
| "inspect a member inside a package" | moving from container to representation to member list without claiming broad extraction |

## How It Works

```text
raw query or need
  -> query planner
  -> resolution run
  -> source registry + local index + resolver
  -> evidence, candidates, representations, compatibility, and absence
  -> review, promotion preview, action plan, or memory
  -> CLI, local web, local API, static/lite/text/files, or read-only alpha view
```

The governing idea is simple: protocol executes, evidence proves, knowledge
explains, and public docs orient. A result is useful only when its provenance,
uncertainty, and next action are visible.

## Architecture Map

```text
control/      governance, audits, inventories, policies, evidence
contracts/    schemas, protocols, packets, public APIs, shared UI contracts
runtime/      Python reference engine, gateway, connectors, stores, workers
surfaces/     CLI, web, API, static, text, file, lite, and native projections
snapshots/    read-only snapshot schemas and examples
crates/       Rust parity and future migration lane
```

Start with:

- [Architecture](docs/ARCHITECTURE.md)
- [Temporal Object Resolver](docs/architecture/TEMPORAL_OBJECT_RESOLVER.md)
- [Logical Graphs](docs/architecture/LOGICAL_GRAPHS.md)
- [Physical Subsystems](docs/architecture/PHYSICAL_SUBSYSTEMS.md)
- [Data Model](docs/architecture/DATA_MODEL.md)
- [Source Action Kernel](docs/architecture/SOURCE_ACTION_KERNEL.md)
- [Snapshot Relay](docs/architecture/SNAPSHOT_RELAY.md)
- [AI Policy](docs/architecture/AI_POLICY.md)

## Project Layout

| Path | Purpose |
| --- | --- |
| `.aide/` | repo operating metadata and compact task context; not product truth |
| `.github/` | GitHub Actions workflows for quick lanes, full discovery, pages, and promotion gates |
| `archive/` | retired, historical, or quarantined material |
| `contracts/` | governed schemas, protocols, APIs, packets, and shared UI contracts |
| `control/` | governance, audits, inventories, policies, research, and evidence |
| `crates/` | Rust parity/future backend lane |
| `docs/` | public documentation, architecture, roadmap, operations, standards, and reference material |
| `evals/` | repo-level evaluation fixtures and benchmarks |
| `examples/` | public-safe fixtures, packs, nodes, and examples |
| `external/` | external references, licenses, specs, and upstream snapshots |
| `native/` | native client planning and skeleton lane |
| `release/` | release, hosting, launch, and promotion planning |
| `runtime/` | Python reference runtime |
| `scripts/` | stable command wrappers |
| `site/` | static site source and generated static artifact tree |
| `snapshots/` | snapshot schemas and public-safe examples |
| `surfaces/` | user-facing projections over contracts and gateway boundaries |
| `tests/` | cross-component and repo-operating tests |
| `tools/` | implementation helpers for validators, generators, reporters, and auditors |

## Documentation Map

Start here:

- [Documentation index](docs/README.md)
- [Current status](docs/STATUS.md)
- [Bootstrap status](docs/BOOTSTRAP_STATUS.md)
- [Vision](docs/VISION.md)
- [Roadmap](docs/ROADMAP.md)

Architecture:

- [Architecture overview](docs/ARCHITECTURE.md)
- [Architecture docs](docs/architecture/README.md)
- [Repo layout](docs/REPO_LAYOUT.md)

Operations and public alpha:

- [Operations docs](docs/operations/README.md)
- [Test and Eval Lanes](docs/operations/TEST_AND_EVAL_LANES.md)
- [Public Alpha Launch Candidate Runbook](docs/operations/PUBLIC_ALPHA_LAUNCH_CANDIDATE_RUNBOOK.md)
- [Public Alpha Deploy Dry-Run Plan](docs/operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md)
- [Public Alpha Manual Approval Gate](docs/operations/PUBLIC_ALPHA_MANUAL_APPROVAL_GATE.md)

Standards, contracts, and evidence:

- [Standards docs](docs/standards/README.md)
- [Reference docs](docs/reference/README.md)
- [Contracts](contracts/README.md)
- [Control](control/README.md)
- [Decisions](docs/DECISIONS.md)
- [Open Questions](docs/OPEN_QUESTIONS.md)

Research, evals, and migration:

- [Research](control/research/README.md)
- [Eval docs](docs/evals/README.md)
- [Repo evals](evals/README.md)
- [Rust migration](docs/roadmap/RUST_MIGRATION.md)
- [Native apps later](docs/roadmap/NATIVE_APPS_LATER.md)

## Public Alpha Posture

Eureka has read-only public-alpha foundations and launch-candidate evidence, but
public alpha is not launched. Local development mode and public-alpha posture
are distinct.

Current public-alpha constraints:

- snapshot-backed/read-only route foundations exist
- public live source fanout is disabled
- public mutation is disabled
- downloads, uploads, installer behavior, executable actions, accounts,
  telemetry, and model/provider calls are disabled
- public open-internet exposure remains gated by deploy dry-run evidence,
  manual approval, hosting evidence, and safety validation

Read:

- [Public Alpha Read-Only Closeout](docs/operations/PUBLIC_ALPHA_READONLY_CLOSEOUT.md)
- [Public Alpha Launch Gates](docs/reference/PUBLIC_ALPHA_LAUNCH_GATES.md)
- [Public Alpha Roadmap](docs/roadmap/PUBLIC_ALPHA.md)

## Development Workflow

For normal development:

- use focused checks selected by `python scripts/eureka_test_select.py --changed --failed-first --json`
- run `python scripts/check_architecture_boundaries.py` when Python layering could be affected
- keep surfaces on public/gateway/contract boundaries rather than engine internals
- keep source observations, evidence, candidates, and accepted truth separate
- treat Python as the oracle while Rust parity candidates prove matching outputs
- keep full unittest discovery in the harness or CI artifact lane rather than normal chat/model loops
- keep local instances, private caches, raw logs, secrets, tokens, and generated private state out of commits

## Roadmap

Near-term work is staged around evidence rather than promises:

- public docs polish and navigation
- public-alpha deploy dry-run and hosting rehearsal evidence
- public-alpha launch only after explicit manual approval
- source/eval/corpus expansion under review gates
- Rust parity candidates that match Python-oracle outputs before migration

Later work may include broader source families, stronger indexing and search,
worker/streaming improvements, hosted alpha, native app shells, app-store-style
clients, and safer action manifests. These are planned or gated directions, not
current capability claims.

Read [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/roadmap/README.md](docs/roadmap/README.md)
for details.

## Contributing, Security, And Conduct

- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Code of conduct](CODE_OF_CONDUCT.md)
- [Agent instructions](AGENTS.md)

Contributors and agents should preserve evidence boundaries, avoid false
readiness claims, and use validators that match the changed paths.

## License

Eureka is source-available under a custom restricted source-viewing license:
[Eureka Temporal Object Resolver - Restricted Source Viewing License](LICENSE.md).

Eureka is **not open-source software**. The license permits viewing, private
study, private local evaluation, limited public-doc quotation, and contribution
submission through the official repository workflow. It prohibits
redistribution, public or competing forks, packages, binaries, hosted services,
commercial/professional/institutional use, incorporation into other projects,
and machine-learning/model-training reuse without written permission.

Read the [license summary](LICENSE-SUMMARY.md), [notice](NOTICE.md), and
[license posture note](docs/operations/LICENSE_SELECTION_REQUIRED.md).
