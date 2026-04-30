# Public Publication Inventory

This directory holds the governed publication-plane contracts for Eureka's
public routes, public data files, client profiles, deployment target semantics,
custom-domain/static-host readiness, future live backend handoff, live probe
gateway policy, compatibility-surface strategy, and redirect policy.

The inventory governs publication shape for static deployment and later public
surfaces. It does not prove GitHub Pages deployment success, add live backend
behavior, configure DNS, add provider-specific backend hosting files, or record
external observations.

Current boundary:

- `site/` is the stdlib-only source/generator tree.
- `site/dist/` is the single generated no-JS static public artifact and GitHub
  Pages deployment artifact path.
- `site/dist/data/` contains Generated Public Data Summaries v0 static JSON.
  They are not a live API and do not record external observations.
- `site/dist/lite/`, `site/dist/text/`, and `site/dist/files/` contain
  Lite/Text/Files Seed Surfaces v0 static compatibility artifacts generated
  from the public data summaries. They add no live search, executable
  downloads, snapshots, relay runtime, or native-client runtime behavior.
- `site/dist/demo/` contains Static Resolver Demo Snapshots v0 static
  fixture-backed examples. They add no live search, live API semantics, backend
  hosting, external observations, or production behavior.
- `domain_plan.json` and `static_hosting_targets.json` contain Custom Domain /
  Alternate Host Readiness v0 policy records. They add no DNS records, no
  `CNAME`, no alternate-host config, no backend hosting, and no live probes.
- `live_backend_handoff.json`, `live_backend_routes.json`, and
  `surface_capabilities.json` contain Live Backend Handoff Contract v0 policy
  records. They reserve `/api/v1` and disabled live capability flags without
  making a backend or API route live.
- `live_probe_gateway.json` contains Live Probe Gateway Contract v0 policy
  records. It records disabled future source candidates, caps, cache/evidence
  posture, and operator gates without implementing probes or making network
  calls.
- `surface_capabilities.json` and `surface_route_matrix.json` now contain
  Compatibility Surface Strategy v0 records for modern web, standard web,
  lite, text, files, data, API handoff, snapshots, relay, CLI, and future
  native clients. They do not implement snapshots, relay, native apps, live
  API behavior, or new runtime product behavior.
- `snapshot_contract.json` contains Signed Snapshot Format v0 policy for the
  repo-local seed example under `snapshots/examples/static_snapshot_v0/`. It
  records required manifests, checksum policy, signature-placeholder policy,
  prohibited contents, and client profiles without adding real signing keys,
  production signed releases, executable downloads, a public `/snapshots/`
  route, relay behavior, or native-client runtime.
- `control/inventory/publication/` owns the publication contracts and
  inventories.
- `.github/workflows/pages.yml` is the static-only GitHub Pages publishing
  workflow for `site/dist/`; it is not a backend deployment path.

The publication-plane validator is:

```bash
python scripts/validate_publication_inventory.py
python scripts/validate_publication_inventory.py --json
python scripts/generate_public_data_summaries.py --check
python scripts/generate_compatibility_surfaces.py --check
python scripts/generate_static_resolver_demos.py --check
python scripts/validate_static_host_readiness.py
python scripts/validate_live_backend_handoff.py
python scripts/validate_live_probe_gateway.py
python scripts/validate_compatibility_surfaces.py
python scripts/generate_static_snapshot.py --check
python scripts/validate_static_snapshot.py
```
