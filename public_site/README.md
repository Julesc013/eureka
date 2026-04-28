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

Validate it with:

```bash
python scripts/generate_public_data_summaries.py --check
python scripts/generate_compatibility_surfaces.py --check
python scripts/generate_static_resolver_demos.py --check
python scripts/validate_public_static_site.py
python scripts/validate_public_static_site.py --json
python scripts/check_github_pages_static_artifact.py
python scripts/validate_static_host_readiness.py
```

The content intentionally describes Eureka as a Python reference backend
prototype, not production. External baselines remain pending/manual, source
placeholders remain placeholders, and live-alpha backend hosting remains future
work.
