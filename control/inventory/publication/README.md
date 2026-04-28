# Public Publication Inventory

This directory holds the governed publication-plane contracts for Eureka's
public routes, public data files, client profiles, deployment target semantics,
custom-domain/static-host readiness, and redirect policy.

The inventory governs publication shape for static deployment and later public
surfaces. It does not deploy generated output, add live backend behavior,
configure DNS, add provider-specific backend hosting files, or record external
observations.

Current boundary:

- `public_site/` is the current no-JS static public artifact and GitHub Pages
  deployment artifact.
- `site/` is the stdlib-only source/generator tree.
- `site/dist/` is generated output for validation, not deployment.
- `public_site/data/` and `site/dist/data/` contain Generated Public Data
  Summaries v0 static JSON. They are not a live API and do not record external
  observations.
- `public_site/lite/`, `public_site/text/`, and `public_site/files/` contain
  Lite/Text/Files Seed Surfaces v0 static compatibility artifacts generated
  from the public data summaries. They add no live search, executable
  downloads, snapshots, relay runtime, or native-client runtime behavior.
- `public_site/demo/` and `site/dist/demo/` contain Static Resolver Demo
  Snapshots v0 static fixture-backed examples. They add no live search, live
  API semantics, backend hosting, external observations, or production
  behavior.
- `domain_plan.json` and `static_hosting_targets.json` contain Custom Domain /
  Alternate Host Readiness v0 policy records. They add no DNS records, no
  `CNAME`, no alternate-host config, no backend hosting, and no live probes.
- `control/inventory/publication/` owns the publication contracts and
  inventories.
- `.github/workflows/pages.yml` is the static-only GitHub Pages publishing
  workflow for `public_site/`; it is not a backend deployment path.

The publication-plane validator is:

```bash
python scripts/validate_publication_inventory.py
python scripts/validate_publication_inventory.py --json
python scripts/generate_public_data_summaries.py --check
python scripts/generate_compatibility_surfaces.py --check
python scripts/generate_static_resolver_demos.py --check
python scripts/validate_static_host_readiness.py
```
