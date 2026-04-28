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
These files are not live search, executable downloads, snapshots, relay
behavior, or native-client runtime.

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
compatibility output. Snapshots, relay surfaces, native clients, custom
domains, and live backend handoff work remain future work after the seed
surfaces.

Static Resolver Demo Snapshots v0 adds `/demo/` static examples from governed
data and fixture-backed Python-oracle outputs. They make current behavior easier
to inspect without creating a live resolver endpoint or API promise. Custom
Domain / Alternate Host Readiness v0 now records future host prerequisites and
validates static host portability without configuring a domain or alternate
host. Live Backend Handoff Contract v0 now reserves `/api/v1` contract-only
routes and disabled capabilities. Live Probe Gateway Contract v0 now defines
the disabled source-probe gateway policy before any external probe exists.
Signed snapshots, relays, native clients, and any actual Internet Archive live
probe remain future work.
