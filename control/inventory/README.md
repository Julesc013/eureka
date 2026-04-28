# Inventory

`control/inventory/` holds governed inventory records that describe repo-known
assets without turning them into runtime truth by themselves.

Current inventory coverage:

- `sources/` for Source Registry v0 seed records
- `tests/` for the Test and Eval Operating Layer v0 registry and command
  matrix
- `publication/` for Public Publication Plane Contracts v0 public route,
  client-profile, deployment-target, public-data, redirect, and base-path
  inventories
- `public_alpha_routes.json` for the Public Alpha Deployment Readiness Review
  route inventory and current safe/blocked route classification
- `docs/operations/public_alpha_hosting_pack/ROUTE_SAFETY_SUMMARY.md` consumes
  the public-alpha route inventory as an operator-readable summary
- `runtime/source_registry/` is the current stdlib-only runtime consumer of those records

Inventory records are:

- explicit
- inspectable
- honest about placeholder versus implemented status
- usable by bounded runtime loaders and future planning work

They are not:

- live sync state
- trust scores
- health scores
- auth configuration
- background scheduling metadata
- deployment configuration
- deployment execution
- static site generation
- a substitute for connector implementation
