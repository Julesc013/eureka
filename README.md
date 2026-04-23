# Eureka

## Compatibility-First Resolution for Software Memory

Eureka is a **bootstrap, pre-product monorepo** for a compatibility-first system focused on software resolution, preservation, evidence-aware inspection, and machine reconstruction.

This repository is intentionally:

- local
- deterministic
- stdlib-only in the executable lane
- contract-first
- architecture-first
- honest about what is still deferred

> Eureka is **not** a finished product, package manager, installer, downloader, deployment stack, or trust engine.
> It is a working architectural proof that exercises real runtime seams end to end.

## Status

| Area | Current State |
| --- | --- |
| Product maturity | Bootstrap / pre-product |
| Runtime lane | Python 3 standard library only |
| Data sources | Governed synthetic fixtures plus recorded GitHub Releases fixtures |
| Surfaces | HTML workbench, native CLI, local stdlib HTTP API |
| Search | Deterministic, bounded, no ranking, no fuzzy retrieval |
| Persistence | Local bounded content-addressed export store only |
| Identity | Bootstrap deterministic `resolved_resource_id` seam |
| Architecture enforcement | Repo-local Python import boundary checker |

## What Eureka Proves Today

The current repo proves a set of bounded executable seams across connectors, engine, gateway public boundaries, and multiple surfaces.

### Resolution and Search

- exact resolution of bounded `target_ref` values
- deterministic search over a small bounded corpus
- honest no-result and miss explanation paths
- shared transport-neutral public boundary reuse across web, CLI, and HTTP API

### Source and Evidence Visibility

- synthetic connector path
- recorded GitHub Releases connector path
- bounded source-family and source-origin visibility
- bounded provenance and evidence summaries
- bounded absence reasoning for misses

### Object and State Views

- bounded side-by-side comparison and disagreement
- bounded subject/state listing
- bounded representation and access-path summaries
- bounded compatibility / host-profile verdicts
- bounded action-routing / recommendation plans
- bounded user-strategy / intent-profile variation over the same resolved target

### Export, Inspection, and Local Storage

- manifest export
- bundle export
- bundle inspection
- deterministic local stored-export listing and readback
- bootstrap `resolved_resource_id` propagation through resolution, search, export, inspection, and storage flows

## What Eureka Deliberately Does Not Claim Yet

The repository is intentionally explicit about unresolved scope.

It does **not** yet settle:

- final object or state identity semantics
- trust scoring or a broader provenance ontology
- merge logic or truth selection across sources
- ranking or fuzzy retrieval
- actual downloads, installers, or restore/import flows
- async workers, auth, deployment, or production HTTP semantics
- final CLI, TUI, or GUI direction
- personalization, saved user profiles, or durable recommendation memory

## Quick Start

### Requirements

- Python 3
- no third-party Python dependencies required for the bootstrap lane

### Useful Demo Commands

#### CLI

```bash
python scripts/demo_cli_workbench.py resolve fixture:software/synthetic-demo-app@1.0.0
python scripts/demo_cli_workbench.py search archive
python scripts/demo_cli_workbench.py states archivebox
python scripts/demo_cli_workbench.py compare fixture:software/archivebox@0.8.5 github-release:archivebox/archivebox@v0.8.5
python scripts/demo_cli_workbench.py plan github-release:cli/cli@v2.65.0 --strategy acquire --host windows-x86_64 --json
python scripts/demo_cli_workbench.py explain-resolve-miss fixture:software/archivebox@9.9.9
```

#### HTTP API Helper

```bash
python scripts/demo_http_api.py index
python scripts/demo_http_api.py resolve github-release:cli/cli@v2.65.0
python scripts/demo_http_api.py action-plan github-release:cli/cli@v2.65.0 --strategy preserve
python scripts/demo_http_api.py states archivebox
```

#### Web Workbench

```bash
python scripts/demo_web_workbench.py
```

Then open the local URLs printed by the script, including the exact-resolution workbench, search page, action-plan page, and local HTTP API index.

#### Architecture Guardrail

```bash
python scripts/check_architecture_boundaries.py
```

## Architecture At a Glance

Normal bounded flow:

```text
connectors
  -> ingest / extract / normalize seams
  -> engine behavior
  -> gateway public boundary
  -> shared view models / UI contracts
  -> web / native / local HTTP API surfaces
```

High-level component ownership:

| Path | Responsibility |
| --- | --- |
| `control/` | Governance and planning material |
| `contracts/` | Governed schemas, public API contracts, shared UI contracts |
| `runtime/connectors/` | Bounded acquisition adapters |
| `runtime/engine/` | Engine behavior and concrete interface boundaries |
| `runtime/gateway/` | Gateway-facing runtime behavior over engine public/service interfaces |
| `surfaces/web/` | Compatibility-first HTML workbench plus local HTTP API |
| `surfaces/native/` | Native surface family, currently CLI-first |
| `.aide/` | Repo-operating metadata only |

Key dependency law:

- surfaces stay on the public side of the architecture
- web and native use `runtime/gateway/public_api/**` in the normal path
- gateway does not depend on surfaces
- engine does not depend on surfaces
- connectors do not invent object truth
- connectors do not own trust semantics
- `.aide/` does not define runtime behavior

The repo enforces the current proven Python import layering with:

- `scripts/check_architecture_boundaries.py`

## Current Executable Scope

Current bootstrap status includes **twenty-one executable local deterministic thin slices**.

Important highlights:

- one governed synthetic connector family
- one bounded real-source connector family using recorded GitHub Releases fixtures
- one transport-neutral gateway public boundary family reused across multiple surfaces
- one compatibility-first HTML surface
- one bootstrap native CLI surface
- one local stdlib HTTP API surface
- one repo-local architecture-boundary checker

This means the repo is already useful for:

- demonstrating architecture reuse across multiple surfaces
- inspecting current public-boundary shapes
- validating bounded runtime semantics against deterministic fixtures
- iterating on contracts and view-model seams without pretending product completeness

## Verification

Common repo verification commands:

```bash
python -m unittest discover -s runtime -t .
python -m unittest discover -s surfaces -t .
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

These checks are still bootstrap-scale, but they cover the current runtime, gateway, surface, and integration seams with deterministic recorded data.

## Repo Map

Useful paths to know:

- `contracts/archive/` — draft archive schemas and governed fixtures
- `contracts/gateway/public_api/` — public API contract placeholders
- `contracts/ui/` — shared view models and UI contracts
- `runtime/connectors/synthetic_software/` — governed synthetic fixture connector
- `runtime/connectors/github_releases/` — recorded GitHub Releases connector
- `runtime/engine/resolve/` — exact resolution and deterministic search
- `runtime/engine/provenance/` — bounded evidence summaries
- `runtime/engine/absence/` — bounded miss explanation
- `runtime/engine/compare/` — bounded comparison and disagreement
- `runtime/engine/states/` — bounded subject/state listing
- `runtime/engine/representations/` — bounded representation and access-path summaries
- `runtime/engine/compatibility/` — bounded host-profile compatibility
- `runtime/engine/action_routing/` — bounded next-step planning
- `runtime/engine/strategy/` — bounded user-strategy profiles
- `runtime/engine/actions/` — manifest export
- `runtime/engine/snapshots/` — bundle export and inspection
- `runtime/engine/store/` — deterministic local content-addressed export store
- `runtime/gateway/public_api/` — transport-neutral public runtime boundary reused by surfaces
- `surfaces/web/` — compatibility-first HTML workbench plus local stdlib HTTP API
- `surfaces/native/cli/` — bootstrap CLI surface
- `scripts/` — demo entry points and repo-local checks

## Recommended Reading Order

### Fastest Practical Orientation

1. `README.md`
2. `docs/BOOTSTRAP_STATUS.md`
3. `scripts/README.md`
4. one CLI or HTTP API demo command

### Deeper Architectural Orientation

1. `docs/VISION.md`
2. `docs/ARCHITECTURE.md`
3. `docs/REPO_LAYOUT.md`
4. `docs/BOOTSTRAP_STATUS.md`
5. `docs/DECISIONS.md`
6. `runtime/gateway/public_api/README.md`
7. `surfaces/web/README.md`
8. `surfaces/native/cli/README.md`

## AIDE in This Repo

AIDE is present here as a **repo-operating layer only**.

It helps declare:

- repo identity
- governed components
- command metadata
- ownership and policy hints

It does **not** define:

- archive object semantics
- protocol meaning
- runtime behavior
- trust semantics
- surface behavior

## Scope Honesty

The current value of this repository is not “feature completeness.”
It is that the seams are:

- explicit
- inspectable
- testable
- reusable across surfaces
- replaceable later without hiding coupling

Eureka is intentionally proving the architecture one bounded slice at a time.
