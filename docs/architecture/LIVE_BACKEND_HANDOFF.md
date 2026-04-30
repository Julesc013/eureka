# Live Backend Handoff

Eureka's publication plane now separates static public artifacts from future
live backend handoff routes.

The static site can expose current repo truth through:

- static HTML under `site/dist/`
- static JSON under `site/dist/data/`
- static compatibility surfaces under `lite/`, `text/`, and `files/`
- static fixture-backed demos under `demo/`

It must not assume a backend exists.

Compatibility Surface Strategy v0 treats `/api/v1` as one optional future
projection among static, lite, text, files, snapshot, relay, CLI, web, and
future native client surfaces. Static and old-client surfaces must degrade
without a live backend.

## Reserved Live Boundary

Live Backend Handoff Contract v0 reserves `/api/v1/` for future hosted
public-alpha backend routes. This prefix is not active on GitHub Pages, is not implemented, and is not a production API.

Static pages may describe `/api/v1/` as future/reserved. They must not link to
it as an available service, and clients must check capability flags before
attempting live behavior.

Public Search API Contract v0 now reserves `/search` and `/api/v1/search` as
future `local_index_only` search routes. This is contract-only: no route
handler, hosted backend, live probe, download/install/upload behavior, local
path search, arbitrary URL fetch, or production API stability is added.

## Capability Flags

Capability state is recorded in:

```text
control/inventory/publication/surface_capabilities.json
```

The current static capabilities are enabled. Live backend, live search, live
probe gateway, and Internet Archive live probe capabilities are disabled by
default. Live Probe Gateway Contract v0 defines policy for future probes, but
does not make any live probe available.

## Relationship To Current Local API

The current local HTTP API under `/api` belongs to the stdlib workbench and
public-alpha wrapper. It is a local/prototype route family used for smoke tests
and supervised rehearsal evidence.

The future `/api/v1/` route family is a handoff contract for later hosted
backend work. It must not inherit public stability from the current local
helper routes.

## Future Hosted Backend

A future hosted backend can coexist with the static site only after separate
operator and contract work defines:

- deployment topology
- CORS posture
- auth/account stance
- rate-limit and abuse controls
- status/capability response shape
- live probe gateway runtime implementation after the contract-only policy
- public search safety and abuse controls before search runtime is hosted
- rollback and disabled-by-default behavior

This milestone adds none of those runtime behaviors.
