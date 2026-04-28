# LIVE_ALPHA_00 Static Public Site Pack

`public_site/` is a committed static public site pack for Eureka live-alpha
preparation. It is plain HTML plus CSS and can be reviewed locally by opening
`index.html`.

This pack is static only. The GitHub Pages workflow can upload this directory
after validation, but the directory itself does not add backend hosting,
configure DNS, fetch external data, run live source probes, scrape external
systems, or start a server.

Generated Public Data Summaries v0 adds deterministic JSON summaries under
`public_site/data/`. Lite/Text/Files Seed Surfaces v0 consumes those summaries
to add static compatibility seed surfaces under `public_site/lite/`,
`public_site/text/`, and `public_site/files/`. They are not live search, a live
API, executable downloads, snapshots, relay behavior, native-client runtime, or
a production contract.

Static Resolver Demo Snapshots v0 adds static no-JS fixture-backed examples
under `public_site/demo/`. They show current bounded resolver behavior without
adding live search, a live API, backend hosting, external observations, or a
production claim.

Custom Domain / Alternate Host Readiness v0 adds readiness contracts and
validation for future host portability. It does not configure DNS, add
`public_site/CNAME`, deploy alternate hosts, add provider config, enable live
probes, or host a backend.

Live Backend Handoff Contract v0 adds contract-only future `/api/v1`
reservations, disabled live capability flags, and error-envelope expectations.
It does not make `/api/v1` live, host a backend, enable live probes, implement
production CORS/auth/rate limits, or create a production API guarantee.

Live Probe Gateway Contract v0 adds disabled-by-default source-probe policy,
candidate-source caps, cache/evidence expectations, and operator gates. It
does not implement probes, call external sources, fetch URLs, scrape, crawl,
enable downloads, or make Google a live probe source.

Rust Query Planner Parity Candidate v0 adds an isolated Rust planner candidate
against expanded Python-oracle query-planner goldens. It does not replace the
Python planner, wire Rust into runtime surfaces, call live sources, or make
Rust a production backend.

Compatibility Surface Strategy v0 records how modern web, standard web,
lite HTML, text, file-tree, static data, demo snapshots, future API handoff,
future snapshots, future relay, CLI, and future native clients share the same
resolver truth through different static or local projections. It does not add
new runtime behavior, live API routes, snapshots, relay services, native apps,
frontend frameworks, or production support claims.

Signed Snapshot Format v0 records a static/offline snapshot contract and a
deterministic repo-local seed example under
`snapshots/examples/static_snapshot_v0/`. It does not add real signing keys,
production signatures, executable downloads, a public `/snapshots/` route,
relay behavior, native-client runtime, live backend behavior, or live probes.

Validate it with:

```bash
python scripts/generate_public_data_summaries.py --check
python scripts/generate_compatibility_surfaces.py --check
python scripts/generate_static_resolver_demos.py --check
python scripts/validate_live_backend_handoff.py
python scripts/validate_live_probe_gateway.py
python scripts/validate_compatibility_surfaces.py
python scripts/generate_static_snapshot.py --check
python scripts/validate_static_snapshot.py
python scripts/check_rust_query_planner_parity.py
python scripts/validate_public_static_site.py
python scripts/validate_public_static_site.py --json
python scripts/check_github_pages_static_artifact.py
python scripts/validate_static_host_readiness.py
```

The content intentionally describes Eureka as a Python reference backend
prototype, not production. External baselines remain pending/manual, source
placeholders remain placeholders, and live-alpha backend hosting remains future
work.
