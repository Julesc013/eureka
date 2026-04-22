# Eureka

## Compatibility-First Resolution for Software Memory

Eureka is a compatibility-first system for software resolution, preservation, and machine reconstruction.

This repository is the bootstrap, pre-product monorepo for that work. It is intentionally small, local, deterministic, stdlib-only, and architecture-first.

## What Eureka Is Right Now

This repo is not a finished product. It is a working architectural bootstrap that proves a set of bounded end-to-end seams:

- synthetic and GitHub Releases-backed connector paths
- ingest -> extract -> normalize -> engine flow
- exact resolution and deterministic search
- bounded provenance and evidence summaries
- bounded absence reasoning for misses
- bounded side-by-side comparison and disagreement
- bounded subject/state timeline listing
- manifest export, bundle export, bundle inspection, and local stored exports
- shared transport-neutral gateway public boundaries
- compatibility-first HTML, CLI, and local HTTP API surfaces
- repo-local architectural-boundary enforcement for Python imports

Version 1 remains software-first. The repo focuses on software artifacts, software-derived evidence, and the minimum governed contracts and runtime seams needed to make those flows inspectable.

## Status at a Glance

Current repo state:

- bootstrap and pre-product
- one monorepo
- Python stdlib only in the executable lane
- local-only and deterministic
- small recorded fixtures instead of broad live federation
- contract-first and boundary-first

What is already proven:

- seventeen executable local deterministic thin slices
- one synthetic connector family
- one bounded real external-source connector family using recorded GitHub Releases fixtures
- one transport-neutral gateway public boundary family reused across multiple surfaces
- one compatibility-first web surface
- one bootstrap native CLI surface
- one local stdlib HTTP API surface

What remains intentionally unresolved:

- final object and state identity semantics
- trust scoring and broader provenance ontology work
- merge logic or truth selection
- ranking and fuzzy retrieval
- downloads, installers, restore or import flows
- auth, async workers, deployment, and production HTTP semantics
- final CLI, TUI, or GUI direction

## Core Architectural Boundaries

High-level component split:

- `control/`: governance and planning material, not product runtime behavior
- `contracts/`: governed schemas, protocols, public API contracts, and shared UI contracts
- `runtime/engine/`: engine behavior plus concrete interface boundaries
- `runtime/gateway/`: gateway-facing runtime behavior over engine public/service interfaces
- `runtime/connectors/`: bounded acquisition adapters feeding ingest/extract/normalize seams
- `surfaces/web/` and `surfaces/native/`: user-facing surfaces
- `.aide/`: repo-operating metadata only

Important dependency law:

- surfaces stay on the public side of the architecture
- web and native use `runtime/gateway/public_api/**` in the normal path
- gateway does not depend on surfaces
- connectors do not define object truth
- connectors do not own trust semantics
- engine does not depend on surfaces
- `.aide/` does not define product runtime behavior

The repo also includes a narrow boundary checker at `scripts/check_architecture_boundaries.py` to mechanically enforce the current Python import layering.

## What You Can Run Today

Everything in the current bootstrap lane runs with Python 3 and the standard library only.

Useful entry points:

- Exact resolution: `python scripts/demo_cli_workbench.py resolve fixture:software/synthetic-demo-app@1.0.0`
- Deterministic search: `python scripts/demo_cli_workbench.py search archive`
- Subject states: `python scripts/demo_cli_workbench.py states archivebox`
- Resolve miss explanation: `python scripts/demo_cli_workbench.py explain-resolve-miss fixture:software/archivebox@9.9.9`
- Search miss explanation: `python scripts/demo_cli_workbench.py explain-search-miss "archive box"`
- Comparison: `python scripts/demo_cli_workbench.py compare fixture:software/archivebox@0.8.5 github-release:archivebox/archivebox@v0.8.5`
- Manifest export: `python scripts/demo_cli_workbench.py export-manifest fixture:software/synthetic-demo-app@1.0.0 --json`
- Bundle export: `python scripts/demo_cli_workbench.py export-bundle fixture:software/synthetic-demo-app@1.0.0 --json`
- HTTP API fetch helper: `python scripts/demo_http_api.py states archivebox`
- Local web workbench server: `python scripts/demo_web_workbench.py`
- Architecture boundary check: `python scripts/check_architecture_boundaries.py`

The current demos exercise:

- known synthetic targets
- known GitHub Releases-backed targets from recorded fixtures
- missing-target and missing-subject blocked paths
- bounded miss explanations for known-subject-different-state and no-result search cases
- bundle export and inspection
- local stored-export listing and readback
- shared surface projections over the same public boundary

## Verification

Common verification commands:

- `python -m unittest discover -s runtime -t .`
- `python -m unittest discover -s surfaces -t .`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`

These checks are still bootstrap-scale, but they cover the current runtime, gateway, surface, and integration seams with deterministic recorded data.

## Current Repo Layout

Top-level layout:

- `contracts/archive/`: draft archive schemas and governed fixtures
- `contracts/gateway/public_api/`: draft public API contract placeholders
- `contracts/ui/`: shared view models and UI contracts used across surfaces
- `runtime/engine/resolve/`: exact resolution and deterministic search
- `runtime/engine/provenance/`: bounded evidence summaries
- `runtime/engine/absence/`: bounded miss explanation
- `runtime/engine/compare/`: bounded side-by-side comparison
- `runtime/engine/states/`: bounded subject/state timeline listing
- `runtime/engine/actions/`: manifest export
- `runtime/engine/snapshots/`: bundle export and inspection
- `runtime/engine/store/`: deterministic local content-addressed export store
- `runtime/connectors/synthetic_software/`: governed synthetic fixture connector
- `runtime/connectors/github_releases/`: recorded GitHub Releases connector
- `runtime/gateway/public_api/`: transport-neutral public runtime boundary reused by surfaces
- `surfaces/web/`: compatibility-first HTML pages plus local stdlib HTTP API
- `surfaces/native/cli/`: bootstrap CLI surface
- `scripts/`: demo entry points and repo-local checks

## How to Read This Repo

If you are new to the project, a good reading order is:

1. `docs/VISION.md`
2. `docs/ARCHITECTURE.md`
3. `docs/REPO_LAYOUT.md`
4. `docs/BOOTSTRAP_STATUS.md`
5. `docs/DECISIONS.md`
6. `runtime/gateway/public_api/README.md`
7. `surfaces/web/README.md` and `surfaces/native/cli/README.md`

If you want the fastest practical orientation, start with:

1. this `README.md`
2. `docs/BOOTSTRAP_STATUS.md`
3. `scripts/README.md`
4. one demo command from CLI or HTTP API

## AIDE in This Repo

AIDE is present here as a repo-operating layer only.

It helps declare:

- repo identity
- governed components
- command metadata
- ownership and policy hints

It does not define:

- archive object semantics
- protocol meaning
- runtime behavior
- trust semantics
- surface behavior

## Scope Honesty

This repo proves that the architecture can work across connectors, engine seams, public boundaries, and multiple surfaces.

It does not yet prove:

- broad live-source federation
- final product semantics
- production deployment choices
- final long-term persistence or reconstruction machinery

That is deliberate. The current value of the repo is that the seams are explicit, inspectable, testable, and replaceable.
