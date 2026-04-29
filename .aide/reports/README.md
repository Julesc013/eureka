# AIDE Reports

This directory is reserved for repo-operating reports. It does not contain
product runtime state and should not be treated as a source of product truth.

Native Action / Download / Install Policy v0 records policy/contract
validation for future action, download, install handoff, package-manager
handoff, mirror, execute, executable-risk, and rights/access behavior without
implementing downloads, installers, package-manager integration, malware
scanning, rights clearance, native clients, relay runtime, or executable trust
claims.

Audit reports that belong under version control should usually live in
`control/audits/` with structured findings. Temporary local run output should
stay outside the repo unless a prompt explicitly asks for a committed evidence
artifact.

Search Usefulness Backlog Triage v0 records its governed backlog under
`control/backlog/search_usefulness_triage/`. If an operator later captures a
triage review report, keep it as evidence here and leave runtime behavior in
the product layers.

Search Usefulness Audit Delta v0 records its committed audit/reporting pack
under `control/audits/search-usefulness-delta-v0/`. It is the canonical place
for the current usefulness-delta summary; do not duplicate volatile local audit
run dumps here.

Search Usefulness Audit Delta v1 records the post-source-expansion delta under
`control/audits/search-usefulness-delta-v1/`. It is also reporting-only and
does not belong in runtime state.

Hard Eval Satisfaction Pack v0 records the archive-resolution hard-eval
satisfaction pass under `control/audits/hard-eval-satisfaction-v0/`. It is
source-backed eval evidence, not AIDE runtime state.

Old-Platform Result Refinement Pack v0 records the archive-resolution
result-shape refinement pass under
`control/audits/old-platform-result-refinement-v0/`. It is deterministic eval
evidence, not AIDE runtime state.

Generated Public Data Summaries v0 records committed static machine-readable
summaries under `public_site/data/` and generated validation copies under
`site/dist/data/`. No separate AIDE runtime report is needed; those JSON files
are publication artifacts, not AIDE product state.

Lite/Text/Files Seed Surfaces v0 records committed static compatibility
surfaces under `public_site/lite/`, `public_site/text/`, and
`public_site/files/`, with generated validation copies under `site/dist/`.
No separate AIDE runtime report is needed; those files are publication
artifacts and do not add live search, downloads, snapshots, relay behavior, or
native-client runtime.

Static Resolver Demo Snapshots v0 records committed static resolver examples
under `public_site/demo/`, with generated validation copies under
`site/dist/demo/`. No separate AIDE runtime report is needed; those files are
publication artifacts and do not add live search, live API semantics, backend
hosting, external observations, or production behavior.

Custom Domain / Alternate Host Readiness v0 records readiness inventories under
`control/inventory/publication/` and operations/reference docs under `docs/`.
No separate AIDE runtime report is needed; this is host-portability governance
only and does not add DNS records, `CNAME`, provider config, alternate-host
deployment, backend hosting, live probes, or production behavior.

Live Backend Handoff Contract v0 records future `/api/v1` handoff inventories
under `control/inventory/publication/` and architecture/reference docs under
`docs/`. No separate AIDE runtime report is needed; this is contract-only
publication governance and does not host a backend, make `/api/v1` live, enable
live probes, implement CORS/auth/rate limits, or create production API
guarantees.

Live Probe Gateway Contract v0 records disabled-by-default source-probe policy
under `control/inventory/publication/` and architecture/reference/operations
docs under `docs/`. No separate AIDE runtime report is needed; this is
contract and policy governance only and does not implement probes, call
external sources, fetch URLs, scrape, crawl, enable downloads, or make Google a
live probe source.

Compatibility Surface Strategy v0 records cross-surface strategy, capability
and route matrices, old-client degradation policy, native-client readiness, and
snapshot/relay readiness notes under `control/inventory/publication/` and
`docs/`. No separate AIDE runtime report is needed; this is strategy and
contract governance only and does not add runtime behavior, snapshots, relay
services, native apps, live backend routes, live probes, or frontend
frameworks.

Signed Snapshot Format v0 records its contract, schema notes, generator,
validator, and deterministic seed example under `control/inventory/publication/`,
`docs/reference/`, `scripts/`, and `snapshots/examples/static_snapshot_v0/`.
No separate AIDE runtime report is needed; this is static export governance and
does not add real signing keys, production signatures, executable downloads, a
public `/snapshots/` route, relay behavior, native-client runtime, live backend
behavior, or live probes.

Signed Snapshot Consumer Contract v0 records future snapshot consumption
contracts, profile inventories, reference docs, validator, and tests under
`control/inventory/publication/`, `docs/reference/`, `scripts/`, and `tests/`.
No separate AIDE runtime report is needed; this is contract/design governance
and does not implement a snapshot reader runtime, relay, native client,
production signing, real signing keys, executable downloads, live backend
behavior, or live probes.

Native Client Contract v0 records future native client contracts, lane
inventories, readiness checklist, validator, and tests under
`control/inventory/publication/`, `docs/reference/`, `docs/operations/`,
`scripts/`, and `tests/`. No separate AIDE runtime report is needed; this is
contract/design governance and does not create Visual Studio/Xcode projects,
native GUI clients, FFI, installers, downloads, relay sidecars, live probes, or
Rust runtime wiring.

Post-Queue State Checkpoint v0 records its committed audit/reporting pack under
`control/audits/post-queue-state-checkpoint-v0/`. No separate AIDE runtime
report is needed; the pack is repo-governance evidence and does not add product
runtime behavior, deployment behavior, live probes, external observations,
production signing, relay services, or native clients.

Relay Surface Design v0 records its future relay inventory, architecture and
reference docs, security/privacy posture, unsigned operator checklist,
validator, and tests under `control/inventory/publication/`, `docs/`, and
`scripts/`. No separate AIDE runtime report is needed; this is design and
governance only and does not add a relay runtime, sockets, protocol servers,
private data exposure, write/admin routes, live-probe passthrough, native
sidecars, or production relay claims.

Rust Source Registry Parity Catch-up v0 records its Rust candidate update,
Python-oracle source-registry goldens, parity case map, stdlib checker, and
structure tests under `crates/eureka-core/`, `tests/parity/`, `tests/scripts/`,
and `scripts/`. No separate AIDE runtime report is needed; this is isolated
parity governance only and does not wire Rust into Python runtime, web, CLI,
HTTP API, workers, public-alpha paths, or production behavior.

Rust Local Index Parity Planning v0 records a planning-only parity lane under
`tests/parity/`, `tests/scripts/`, and `scripts/`. No separate AIDE runtime
report is needed; this adds a future parity plan, fixture map, acceptance
schema, validator, and tests only, with no Rust local-index implementation,
SQLite/indexing behavior, Python runtime replacement, or runtime/surface
wiring.
