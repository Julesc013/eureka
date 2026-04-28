# Public Publication Inventory

This directory holds the governed publication-plane contracts for Eureka's
public routes, public data files, client profiles, deployment target semantics,
and redirect policy.

The inventory governs publication shape for static deployment and later public
surfaces. It does not create a static site generator, add live backend
behavior, configure DNS, add provider-specific backend hosting files, or record
external observations.

Current boundary:

- `public_site/` is the current hand-authored no-JS static public artifact.
- `site/` is reserved for a future source or generator tree.
- `site/dist/` is reserved for a future generated static artifact.
- `control/inventory/publication/` owns the publication contracts and
  inventories.
- `.github/workflows/pages.yml` is the static-only GitHub Pages publishing
  workflow for `public_site/`; it is not a backend deployment path.

The publication-plane validator is:

```bash
python scripts/validate_publication_inventory.py
python scripts/validate_publication_inventory.py --json
```
