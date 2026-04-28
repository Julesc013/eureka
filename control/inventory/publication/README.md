# Public Publication Inventory

This directory holds the governed publication-plane contracts for Eureka's
public routes, public data files, client profiles, deployment target semantics,
and redirect policy.

The inventory governs publication shape before deployment. It does not deploy
Eureka, create a static site generator, add live backend behavior, configure
DNS, add provider-specific hosting files, or record external observations.

Current boundary:

- `public_site/` is the current hand-authored no-JS static public artifact.
- `site/` is reserved for a future source or generator tree.
- `site/dist/` is reserved for a future generated static artifact.
- `control/inventory/publication/` owns the publication contracts and
  inventories.

The publication-plane validator is:

```bash
python scripts/validate_publication_inventory.py
python scripts/validate_publication_inventory.py --json
```

