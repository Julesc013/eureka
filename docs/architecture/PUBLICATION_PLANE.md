# Publication Plane

The publication plane is the governed layer that decides what Eureka may expose
publicly before any host, generator, live backend, or client consumes it.

It exists because public routes, public JSON fields, status words, base-path
rules, and client promises are harder to change than deployment mechanics.
Deployment targets must consume this contract. They must not define Eureka's
public architecture by accident.

## Current Boundary

`public_site/` is the current static public artifact. It is hand-authored,
no-JS, already validated by `scripts/validate_public_static_site.py`, and safe
for later static-hosting review.

`site/` is the stdlib-only static-site source and generator tree introduced by
Static Site Generation Migration v0. It contains page JSON, templates, static
assets, `site/build.py`, and `site/validate.py`.

`site/dist/` is the generated static output used for validation. It is not the
GitHub Pages deployment artifact yet.

`public_site/data/` contains Generated Public Data Summaries v0: deterministic
static JSON projections of site, page, source, eval, route, and build state.
`site/build.py` also emits matching summaries into `site/dist/data/` for
generated-output validation. These files are not a live API.

`public_site/lite/`, `public_site/text/`, and `public_site/files/` contain
Lite/Text/Files Seed Surfaces v0: static compatibility surfaces generated from
public data summaries for old browsers, plain-text readers, and file-tree
inspection. `site/build.py` emits matching validation copies into `site/dist/`.
These files are not live search, executable downloads, production signed
snapshots, relay behavior, or native-client runtime.

`public_site/demo/` contains Static Resolver Demo Snapshots v0: static no-JS
examples of query planning, member-level results, compatibility evidence,
absence, comparison/disagreement, source detail, article/scan fixtures, and
eval summaries. `site/build.py` emits matching validation copies into
`site/dist/demo/`. These files are fixture-backed publication examples, not
live search, a live API, backend hosting, external observations, or production
behavior.

Custom Domain / Alternate Host Readiness v0 adds
`control/inventory/publication/domain_plan.json`,
`control/inventory/publication/static_hosting_targets.json`,
`docs/operations/CUSTOM_DOMAIN_AND_ALTERNATE_HOST_READINESS.md`, and
`scripts/validate_static_host_readiness.py`. This is host-portability policy
only: no DNS record, `CNAME`, provider config, alternate host deployment,
backend hosting, or live probe is configured.

Live Backend Handoff Contract v0 adds
`control/inventory/publication/live_backend_handoff.json`,
`control/inventory/publication/live_backend_routes.json`,
`control/inventory/publication/surface_capabilities.json`,
`docs/architecture/LIVE_BACKEND_HANDOFF.md`, and
`scripts/validate_live_backend_handoff.py`. This reserves `/api/v1` and
disabled live capability flags for future hosted-backend work. It does not
make `/api/v1` live, deploy a backend, enable live probes, or create a
production API guarantee.

Live Probe Gateway Contract v0 adds
`control/inventory/publication/live_probe_gateway.json`,
`docs/reference/LIVE_PROBE_GATEWAY_CONTRACT.md`,
`docs/architecture/LIVE_PROBE_GATEWAY.md`, and
`scripts/validate_live_probe_gateway.py`. This is disabled-by-default source
policy for future external metadata probes. It does not implement probes, call
external services, fetch URLs, scrape, crawl, enable downloads, or make Google
a live probe source.

Compatibility Surface Strategy v0 adds
`docs/architecture/COMPATIBILITY_SURFACES.md`,
`control/inventory/publication/surface_route_matrix.json`, and expanded
`surface_capabilities.json` records. This governs modern web, standard web,
lite, text, files, data, demo, future API, future snapshots, future relay,
CLI, and future native client projections as multiple views of the same
resolver truth.

Signed Snapshot Format v0 adds `snapshot_contract.json`,
`docs/reference/SNAPSHOT_FORMAT_CONTRACT.md`,
`docs/reference/SNAPSHOT_SIGNATURE_POLICY.md`, and a deterministic repo-local
seed example under `snapshots/examples/static_snapshot_v0/`. It is a contract
and seed example only: no production signed release, real signing keys,
executable downloads, public `/snapshots/` route, relay behavior, native app,
live backend behavior, or live probe is implemented.

Signed Snapshot Consumer Contract v0 adds
`snapshot_consumer_contract.json`, `snapshot_consumer_profiles.json`,
`docs/reference/SNAPSHOT_CONSUMER_CONTRACT.md`, and
`scripts/validate_snapshot_consumer_contract.py`. It defines future snapshot
read order, checksum semantics, v0 signature-placeholder handling, and
file-tree/text/lite/relay/native/audit consumer profiles only: no snapshot
reader runtime, relay runtime, native client, production signing, real keys,
executable downloads, live backend, or live probes are implemented.

Native Client Contract v0 adds `native_client_contract.json`,
`native_client_lanes.json`, `docs/reference/NATIVE_CLIENT_CONTRACT.md`,
`docs/reference/NATIVE_CLIENT_LANES.md`,
`docs/operations/NATIVE_CLIENT_READINESS_CHECKLIST.md`, and
`scripts/validate_native_client_contract.py`. It defines future native client
inputs, Windows/Mac lane policy, CLI current-state boundaries, and readiness
gates only: no Visual Studio/Xcode project, native GUI, FFI, installer
automation, download/execution automation, relay sidecar, live probe, or Rust
runtime wiring is implemented.

Relay Surface Design v0 adds
`control/inventory/publication/relay_surface.json`,
`docs/architecture/RELAY_SURFACE.md`,
`docs/reference/RELAY_SURFACE_CONTRACT.md`,
`docs/reference/RELAY_SECURITY_AND_PRIVACY.md`,
`docs/operations/RELAY_OPERATOR_CHECKLIST.md`, and
`scripts/validate_relay_surface_design.py`. This is future relay policy only:
no relay server, network listener, protocol bridge, FTP, SMB, WebDAV, Gopher,
private data exposure, write/admin route, live-probe passthrough, or native
runtime is implemented.

`control/inventory/publication/` owns the publication contracts and inventories:
routes, route stability, public status vocabulary, client profiles, public data
expectations, deployment target semantics, and redirects.

## Static Artifact Versus Live Backend

The current publication plane governs static public material only. GitHub Pages
Deployment Enablement v0 consumes this plane to upload `public_site/` as a
static artifact, but it does not start or approve a live backend. It does not
add live source probes, Internet Archive calls, Google scraping, crawling,
auth, accounts, TLS, rate limiting, DNS, process management, or generated
artifact deployment.

The live backend handoff contract defines future public API route reservations
and capability flags, but that remains separate from the static artifact
contract. The current static site must treat `/api/v1` as future/reserved.

## Claim Traceability

No public claim without a repo source.

Allowed repo sources are:

- README/status docs
- source inventory
- route inventory
- eval/audit outputs
- manual baseline records
- static site manifest
- publication inventory

This rule applies to public pages, future generated public data, route
summaries, source summaries, demo summaries, status pages, and future client
profiles. If a claim cannot point to one of these sources, it should not be
published yet.

## Base-Path Portability

The publication plane must support both:

- GitHub Pages project path: `/eureka/`
- future custom-domain root path: `/`

Static links and future generated links must stay relative or base-path aware.
Root-only assumptions are not allowed in public contracts.

## Relationship To Future Milestones

GitHub Pages Deployment Enablement v0 configures publishing of the current
`public_site/` artifact only after validating this inventory and the artifact.
Workflow configuration is not a deployment-success claim.

Static Site Generation Migration v0 introduces `site/` and `site/dist/`, but
`public_site/` remains the deployment artifact until a later explicit migration
changes that contract. The generator must preserve the route, data, client, and
redirect contracts here.

Generated Public Data Summaries v0 projects safe machine-readable files under
`/data/` without live data or external observations. Those files prepare later
static clients but do not create production API semantics.

Lite/Text/Files Seed Surfaces v0 consumes those summaries for static
compatibility output. Signed Snapshot Format v0 now defines a repo-local
offline seed format with checksums and signature-placeholder documentation.
Signed Snapshot Consumer Contract v0 defines future consumer read order and
validation posture for that format. Native Client Contract v0 defines future
native client lane/readiness policy, but the public `/snapshots/` route,
snapshot reader runtime, production signing, relay surfaces, native GUI
clients, custom domains, and hosted backend work remain future.

Static Resolver Demo Snapshots v0 adds `/demo/` static examples from governed
data and fixture-backed Python-oracle outputs. They make current behavior easier
to inspect without creating a live resolver endpoint or API promise. Custom
Domain / Alternate Host Readiness v0 now records future host prerequisites and
validates static host portability without configuring a domain or alternate
host. Live Backend Handoff Contract v0 now reserves `/api/v1` contract-only
routes and disabled capabilities. Live Probe Gateway Contract v0 now defines
the disabled source-probe gateway policy before any external probe exists.
Compatibility Surface Strategy v0 now records the cross-surface policy for
old-browser, text, file-tree, snapshot, relay, API, CLI, web, and future native
clients. Relay Surface Design v0 now records future local/LAN bridge policy
without implementing bridge behavior. Production signed snapshots, public
`/snapshots/`, relay runtime, native clients, and any actual Internet Archive
live probe remain future work.
