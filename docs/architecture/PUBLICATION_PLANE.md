# Publication Plane

The publication plane is the governed layer that decides what Eureka may expose
publicly before any host, generator, live backend, or client consumes it.

It exists because public routes, public JSON fields, status words, base-path
rules, and client promises are harder to change than deployment mechanics.
Deployment targets must consume this contract. They must not define Eureka's
public architecture by accident.

## Current Boundary

`site/` is the stdlib-only static-site source and generator tree. It contains
page JSON, templates, static assets, `site/build.py`, and `site/validate.py`.

`site/dist/` is the canonical generated static public artifact. Repository
Shape Consolidation v0 makes it the only GitHub Pages artifact path in active
workflow, validator, and publication inventory configuration.
Static Artifact Promotion Review v0 conditionally promotes this artifact as
the active repo-local static publication artifact, pending GitHub Actions run
evidence before any hosted deployment-success claim.

`site/dist/data/` contains Generated Public Data Summaries v0: deterministic
static JSON projections of site, page, source, eval, route, search handoff,
static search configuration, public index summary, and build state.
`site/build.py` also emits matching summaries into `site/dist/data/` for
generated-output validation. These files are not a live API.
Public Data Contract Stability Review v0 now classifies generated public data
fields as `stable_draft`, `experimental`, `volatile`, `internal`,
`deprecated`, or `future` through
`docs/reference/PUBLIC_DATA_STABILITY_POLICY.md` and the audit pack under
`control/audits/public-data-contract-stability-review-v0/`. The review is
field-level governance only and does not make public JSON a production API.

`site/dist/lite/`, `site/dist/text/`, and `site/dist/files/` contain
Lite/Text/Files Seed Surfaces v0: static compatibility surfaces generated from
public data summaries for old browsers, plain-text readers, and file-tree
inspection. `site/build.py` emits matching validation copies into `site/dist/`.
These files are not live search, executable downloads, production signed
snapshots, relay behavior, or native-client runtime.

`site/dist/demo/` contains Static Resolver Demo Snapshots v0: static no-JS
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

Public Search API Contract v0 adds `contracts/api/search_request.v0.json`,
`contracts/api/search_response.v0.json`,
`contracts/api/error_response.v0.json`,
`control/inventory/publication/public_search_routes.json`,
`docs/reference/PUBLIC_SEARCH_API_CONTRACT.md`, and
`docs/operations/PUBLIC_SEARCH_LOCAL_INDEX_ONLY_MODE.md`. This defines the
future `local_index_only` request, response, error, and reserved-route envelope
before runtime exists. It does not implement `/search` or `/api/v1/search`,
host a backend, enable live probes, fetch URLs, scrape, download, install,
upload, search local paths, or create a production API guarantee.

Public Search Production Contract v0 now freezes the P54 hosted-wrapper
contract by adding source-status, evidence-summary, absence-report, and
public-search status schemas, tightening request/response/error/result-card
alignment, reserving `/healthz`, `/status`, and `/api/v1` route families, and
documenting static-to-dynamic handoff requirements. It is contract governance
only: no backend is deployed, GitHub Pages remains static-only, and hosted
search remains unavailable until a later wrapper milestone implements the
contract honestly.

Hosted Public Search Wrapper v0 now implements that route family as a
local/prototype stdlib wrapper over the gateway public search API. It is
`local_index_only`, read-only, and deployment-unverified. GitHub Pages remains
static-only, and the wrapper does not enable live probes, downloads, uploads,
accounts, telemetry, arbitrary URL fetch, source connectors, AI runtime, index
mutation, pack import, or staging runtime.

Static Site Search Integration v0 now publishes the static search front door,
`data/search_config.json`, and `data/public_index_summary.json`. The default
backend status is `backend_unconfigured`, hosted form submission is disabled,
and no hosted backend URL is exposed without operator evidence.

Public Search Result Card Contract v0 adds
`contracts/api/search_result_card.v0.json`, fixture-safe examples,
`docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`, and
`control/audits/public-search-result-card-contract-v0/`. This defines the
future `results[]` card carried by public search responses. It does not make
public search live, add route handlers, enable downloads/installers/execution,
enable uploads, claim malware safety, claim rights clearance, or create a
production ranking guarantee.

Public Search Safety / Abuse Guard v0 adds
`control/inventory/publication/public_search_safety.json`,
`docs/operations/PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md`,
`docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md`, and
`scripts/validate_public_search_safety.py`. This defines policy-only
`local_index_only` limits, forbidden parameters, disabled live/external modes,
error mapping, privacy posture, operator controls, and runtime gates before
public search runtime exists. It does not implement route handlers, rate-limit
middleware, telemetry runtime, auth/accounts, hosted backend behavior, live
probes, downloads, uploads, local path search, arbitrary URL fetch, or
production safety claims.

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

Native Action / Download / Install Policy v0 adds
`control/inventory/publication/action_policy.json`,
`docs/reference/ACTION_DOWNLOAD_INSTALL_POLICY.md`,
`docs/reference/EXECUTABLE_RISK_POLICY.md`,
`docs/reference/RIGHTS_AND_ACCESS_POLICY.md`,
`docs/reference/INSTALL_HANDOFF_CONTRACT.md`, and
`scripts/validate_action_policy.py`. It defines future action classes, warning
classes, public-alpha/static defaults, and native/snapshot/relay requirements
only: no downloads, installers, package-manager integration, malware scanning,
rights clearance, native clients, relay runtime, executable trust claims, or
public download surface is implemented.

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
Deployment Enablement v0 consumes this plane to upload `site/dist/` as a
static artifact, but it does not start or approve a live backend. It does not
add live source probes, Internet Archive calls, Google scraping, crawling,
auth, accounts, TLS, rate limiting, DNS, process management, or production
deployment claims.

The live backend handoff contract defines future public API route reservations
and capability flags, but that remains separate from the static artifact
contract. Public Search API Contract v0 narrows the future search part of that
handoff to `local_index_only` while still keeping the current static site from
treating `/search` or `/api/v1/search` as live.

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
`site/dist/` artifact only after validating this inventory and the artifact.
Workflow configuration is not a deployment-success claim.

Static Site Generation Migration v0 introduces `site/` and `site/dist/`, but
`site/dist/` remains the deployment artifact until a later explicit migration
changes that contract. The generator must preserve the route, data, client, and
redirect contracts here.
Repository Shape Consolidation v0 and Static Artifact Promotion Review v0 make
`site/dist/` the active static artifact for local validation and Pages upload
configuration. They do not add public search, backend hosting, live probes, or
production claims.
Static Deployment Evidence / GitHub Pages Repair v0 confirms the workflow still
uploads `site/dist` and the local artifact validates, but current-head GitHub
Actions/Pages status is unverified because `gh` is unavailable in the local
environment. Prior committed evidence records a Pages configuration failure
before artifact upload. This is an operator-gated deployment evidence gap, not
a live backend or public search deployment.

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
routes and disabled capabilities. Public Search API Contract v0 now defines
local-index-only search envelopes and Local Public Search Runtime v0 implements
local/prototype routes without hosted deployment. Public Search Static Handoff
v0 now publishes static/no-JS `search.html`, lite/text/files handoff outputs,
and `data/search_handoff.json` without making GitHub Pages dynamic or claiming
hosted search. Static Site Search Integration v0 extends that static handoff
with `data/search_config.json` and `data/public_index_summary.json`, again
without making GitHub Pages dynamic or claiming hosted search. Public Search
Safety / Abuse Guard v0 defines the safety and
abuse policy around those surfaces. Public Search Production Contract v0 now
freezes the future P54 wrapper route, error, safety, source-status, evidence,
absence, status, and versioning requirements while still adding no hosted
runtime behavior. Live Probe Gateway Contract v0 now defines the disabled
source-probe gateway policy before any external probe exists.
Compatibility Surface Strategy v0 now records the cross-surface policy for
old-browser, text, file-tree, snapshot, relay, API, CLI, web, and future native
clients. Relay Surface Design v0 now records future local/LAN bridge policy
without implementing bridge behavior. Source/Evidence/Index Pack Import
Planning v0 does not publish pack-derived records; validate-only and private
quarantine modes have no static publication or public-search impact by default.
Production signed snapshots, public
`/snapshots/`, relay runtime, native clients, and any actual Internet Archive
live probe remain future work.

<!-- P79-OBJECT-PAGE-CONTRACT-START -->
## P79 Object Page Contract v0

Object Page Contract v0 is contract-only and evidence-first. It defines future public object pages that preserve provisional identity, source/evidence/provenance, compatibility, conflicts, scoped absence, and gaps without implementing runtime object pages.

Boundary notes:

- No runtime object routes, database, persistent object-page store, source connector runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, installs, execution, uploads, telemetry, accounts, rights clearance, or malware safety claim are added.
- Public search may reference object page links only after a future governed integration; P79 does not mutate public search result cards or the public index.
- Object pages are not app-store, downloader, installer, or execution surfaces.
<!-- P79-OBJECT-PAGE-CONTRACT-END -->
