# Route Safety Summary

This summary is generated from `control/inventory/public_alpha_routes.json`.
The JSON inventory is the machine-readable source of truth for route
classification. This document is an operator-readable summary for the
Public Alpha Hosting Pack v0.

## Current Inventory Status

- inventory kind: `eureka.public_alpha_routes`
- inventory version: `0.1.0`
- total routes: 94
- safe_public_alpha: 38
- blocked_public_alpha: 5
- local_dev_only: 49
- review_required: 2
- deferred: 0

These counts describe the constrained public-alpha demo posture only.
They do not approve open-internet exposure or production deployment.

## Category Examples

### Safe Public Alpha

- `/status`
- `/api/status`
- `/api`
- `/`
- `/api/resolve`
- `/query-plan`
- `/api/query-plan`
- `/search`

### Blocked Public Alpha

- `/api/resolve?store_root`
- `/api/action-plan?store_root`
- `/evals/archive-resolution?index_path`
- `/api/evals/archive-resolution?index_path`
- `/*?output`

### Local Dev Only

- `/fetch`
- `/api/fetch`
- `/member`
- `/api/member`
- `/index/build`
- `/api/index/build`
- `/index/status`
- `/api/index/status`

### Review Required

- `/actions/export-resolution-manifest`
- `/api/export/manifest`

### Deferred

- none currently inventoried

## Operator Notes

- `safe_public_alpha` routes are safe only for the supervised demo
  rehearsal posture when `public_alpha` mode is confirmed.
- `blocked_public_alpha` routes are route variants that policy blocks in
  `public_alpha` mode, usually because they expose caller-provided local
  filesystem parameters.
- `local_dev_only` routes remain available only to a trusted local operator
  in `local_dev` mode.
- `review_required` routes, currently manifest export routes, return
  bounded JSON but still need explicit manual review before any real
  hosted demo exposure.
- `deferred` is currently empty; future entries must stay explicit rather
  than silently disappearing from the inventory.

created_by_slice: `public_alpha_hosting_pack_v0`
