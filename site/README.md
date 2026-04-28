# Static Site Source Tree

`site/` is the governed stdlib-only source and generator tree for Eureka's
static public site.

Current boundary:

- `site/` contains source JSON, templates, assets, and generator scripts.
- `site/dist/` is generated output from `python site/build.py`.
- `site/dist/data/` is populated by Generated Public Data Summaries v0 for
  validation against the current static publication data.
- `site/dist/lite/`, `site/dist/text/`, and `site/dist/files/` are populated by
  Lite/Text/Files Seed Surfaces v0 for static compatibility validation.
- `site/dist/demo/` is populated by Static Resolver Demo Snapshots v0 for
  fixture-backed static resolver demo validation.
- Host-portability policy is validated by
  `scripts/validate_static_host_readiness.py`; it does not configure DNS,
  CNAME, provider files, alternate hosts, backend hosting, or live probes.
- Live Backend Handoff Contract v0 is validated by
  `scripts/validate_live_backend_handoff.py`; it reserves future `/api/v1`
  routes and disabled live capability flags without making a live API.
- Live Probe Gateway Contract v0 is validated by
  `scripts/validate_live_probe_gateway.py`; it defines disabled-by-default
  future source-probe policy without implementing probes or making network
  calls.
- Compatibility Surface Strategy v0 is validated by
  `scripts/validate_compatibility_surfaces.py`; it records surface capability
  and route matrices plus old-client/native/snapshot/relay readiness without
  adding runtime behavior.
- `public_site/` remains the GitHub Pages deployment artifact for this
  milestone.

The generator uses only Python standard library modules. It does not use
Node/npm, frontend frameworks, live backend calls, live source probes, external
web APIs, scraping, browser automation, or deployment behavior.

Common commands:

```bash
python site/build.py --check
python site/build.py --json
python site/validate.py
python site/validate.py --json
```

The public data generator can also be checked directly:

```bash
python scripts/generate_public_data_summaries.py --check
python scripts/generate_compatibility_surfaces.py --check
python scripts/generate_static_resolver_demos.py --check
python scripts/validate_live_backend_handoff.py
python scripts/validate_live_probe_gateway.py
python scripts/validate_compatibility_surfaces.py
```

Generated output is no-JS static HTML with relative links so it can work under
the GitHub Pages project base path `/eureka/` and a future custom-domain root
path `/`.

`site/build.py --output public_site` is intentionally refused in this milestone
so generated output cannot replace the deployable artifact by accident.

Generated public data and compatibility surfaces remain static only. They do
not create a live API, enable live probes, record external observations, add
executable downloads, create snapshots, add relay/native runtime behavior, or
change deployment behavior. Static resolver demos under `site/dist/demo/` are
also static fixture-backed examples only; they add no live search, backend
hosting, or production behavior. Future `/api/v1` handoff routes are reserved
by contract only and are not live in generated output. The live probe gateway
policy is also contract-only; generated output must not call Internet Archive,
Wayback, GitHub, package registries, or any external source. Compatibility
surface strategy is likewise contract-only in this tree: snapshots, relay
services, native app projects, and live API surfaces remain future/deferred.
