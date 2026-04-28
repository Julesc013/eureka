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

A future live backend handoff contract may define public API routes and
capability flags, but that is separate from the static artifact contract.

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

Generated Public Data Summaries v0 should project safe machine-readable files
under `/data/` without live data or external observations unless evidence
records exist.

Lite, text, files, snapshots, relay surfaces, native clients, custom domains,
and live backend handoff work are reserved by this plane, but they are not
implemented by this milestone.
