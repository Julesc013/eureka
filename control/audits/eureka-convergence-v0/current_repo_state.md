# Current Repo State

This summary is derived from repo-local files only:

- `README.md`
- `docs/ROADMAP.md`
- `docs/roadmap/BACKEND_ROADMAP.md`
- `docs/roadmap/PUBLIC_ALPHA.md`
- `docs/roadmap/NATIVE_APPS_LATER.md`
- `docs/architecture/COMPATIBILITY_SURFACES.md`
- `docs/architecture/PUBLICATION_PLANE.md`
- `control/inventory/publication/`
- AIDE Lite reports under `.aide/reports/`

## Product Status

Eureka is a Python reference backend prototype and not production. The active
product posture is local-first, deterministic, fixture-backed, and
evidence-oriented. Current runtime slices include exact resolution,
deterministic search, source registry, query planner, local index, local worker
and task model, resolution memory, bounded representation/access-path,
compatibility, action plan, acquisition, decomposition, and member readback
seams through local web, CLI, and local HTTP surfaces.

Python remains the executable specification and architecture oracle. Rust is a
parity lane only and is not wired into runtime behavior.

## AIDE Lite Status

AIDE Lite is imported and operational for repo-governance support. It can
generate compact task/review packets, run deterministic checks, record queue
evidence, and enforce token discipline. It is not product truth and must not
define runtime semantics.

## Public, Static, And Search Status

Static publication assets exist under `site/dist/`, with data, lite, text,
files, and demo surfaces generated from governed repo inputs. They are static
artifacts, not a live API.

Local/prototype public search routes exist for `local_index_only` behavior, and
the hosted public search wrapper is local/prototype and deployment-unverified.
No hosted backend URL is configured as live. GitHub Pages/static deployment
evidence remains operator-gated and prior evidence records static URL or Pages
configuration gaps.

## Pack, Source, Evidence, Index, And Contribution Status

Source, evidence, index, contribution, and master-index review queue contracts
exist with examples, validators, and audit evidence. They are contract,
validation, example, planning, or local dry-run surfaces. They do not implement
hosted ingestion, automatic acceptance, canonical truth selection, master-index
mutation, uploads, moderation, accounts, or live connectors.

Source cache and evidence ledger dry-run work exists locally, but it is not
integrated into public search or master-index truth.

## Staging And Import Status

Validate-only pack import tooling, local quarantine/staging policy, staging
report path policy, local staging manifest format, and staged pack inspection
exist. They do not create staging runtime, staged state, pack copying, local
index mutation, public-search mutation, runtime source registry mutation,
uploads, network/model calls, or master-index mutation.

## AI Status

AI provider contracts, typed AI output validation, and AI-assisted evidence
drafting plans exist as disabled-by-default, offline, contract, example, and
validation work. No provider runtime, model calls, API keys, embeddings, AI in
public search, AI-generated truth, telemetry, local index mutation, or
master-index mutation is enabled.

## Native, Relay, And Snapshot Status

Signed snapshot format and consumer contracts exist with a repo-local seed
example. Relay surface design and relay prototype planning exist. Native client
contracts, action/download/install policy, cache/privacy policy, project
readiness review, and Windows 7 WinForms planning exist.

All remain contract/design/planning unless explicitly reviewed later. No native
project, Visual Studio or Xcode project, GUI, FFI, installer, relay runtime,
socket listener, private-data relay, snapshot reader runtime, production
signing, public `/snapshots/` route, or executable download behavior exists.

## Hosting And Deployment Status

The static GitHub Pages workflow targets `site/dist/`, but workflow
configuration is not a deployment success claim. Actual hosted public alpha is
not active. Full hosted/backend operations, DNS/TLS, edge/rate limits,
observability, backend URL configuration, live probes, and operator approvals
remain Track E.
