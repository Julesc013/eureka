# Public Publication Inventory

This directory holds the governed publication-plane contracts for Eureka's
public routes, public data files, client profiles, deployment target semantics,
and redirect policy.

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
- `control/inventory/publication/` owns the publication contracts and
  inventories.
- `.github/workflows/pages.yml` is the static-only GitHub Pages publishing
  workflow for `public_site/`; it is not a backend deployment path.

The publication-plane validator is:

```bash
python scripts/validate_publication_inventory.py
python scripts/validate_publication_inventory.py --json
python scripts/generate_public_data_summaries.py --check
```
