# Eureka

## Compatibility-First Resolution for Software Memory

Eureka is a compatibility-first software resolution, preservation, and machine-reconstruction system. This repository is the bootstrap and pre-product monorepo for that work.

Version 1 is software-first. The initial effort is aimed at software artifacts, software-derived evidence, and the minimum governed interfaces needed to recover, preserve, and reconstruct machine-usable software state.

## Repository Status

This repo is intentionally bootstrap-only. It establishes structure, boundaries, contracts, and operating policy before real product logic is implemented.

## High-Level Layout

- `control/`: governance material, inventories, research notes, matrices, and packaging decisions
- `contracts/`: governed schemas, protocols, public API contracts, and shared UI contracts
- `runtime/`: engine, gateway, and connector implementation areas
- `surfaces/`: user-facing web and native surfaces
- `tests/` and `evals/`: cross-component verification and evaluation scaffolding
- `.aide/`: pinned repo operating layer for identity, ownership, policies, commands, and eval grouping

## AIDE Scope in This Repo

AIDE is used here as a repo operating layer only. It helps declare the repository identity, governed components, ownership, dependency rules, commands, and compatibility metadata.

AIDE is not the Eureka runtime. It does not define archive object semantics, schema meaning, protocol meaning, action recipe semantics, snapshot semantics, or product behavior.

## Current Architectural Notes

- Web uses gateway public APIs and contracts in the normal online path.
- Native may later use a narrow engine SDK only through an explicit offline or local mode decision.
- Schemas and protocols are first-class governed assets.
- Connectors do not define object truth and do not own trust semantics.

See [VISION.md](docs/VISION.md), [ARCHITECTURE.md](docs/ARCHITECTURE.md), and [REPO_LAYOUT.md](docs/REPO_LAYOUT.md) for the founding bootstrap documents.
