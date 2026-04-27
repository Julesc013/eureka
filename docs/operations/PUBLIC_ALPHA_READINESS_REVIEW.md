# Public Alpha Deployment Readiness Review

Public Alpha Deployment Readiness Review is an audit and smoke-test checkpoint
for Eureka's current stdlib web/API backend. It does not deploy Eureka and does
not add auth, accounts, HTTPS/TLS, rate limiting, process supervision, cloud
configuration, containers, native apps, Rust code, live crawling, or background
workers.

## Verdict

Current verdict: conditionally ready for a short-lived, operator-supervised
constrained demo rehearsal, but not ready for open public internet exposure from
this repo alone.

The current `public_alpha` mode has evidence that caller-provided local path
controls are blocked and safe read-only/search/inspect/eval routes still work.
Real public hosting remains blocked on externally provided hosting posture,
abuse controls, logging expectations, final route review, and an operator stop
plan. Eureka itself still provides no auth, TLS, accounts, rate limiting,
process manager, or multi-user isolation.

## Evidence

- Route inventory: `control/inventory/public_alpha_routes.json`
- Smoke command: `python scripts/public_alpha_smoke.py`
- JSON smoke command: `python scripts/public_alpha_smoke.py --json`
- Hosting pack: `docs/operations/public_alpha_hosting_pack/`
- Static public site pack: `public_site/`
- Static site validator: `python scripts/validate_public_static_site.py`
- Inventory validator: `python -m unittest tests.operations.test_public_alpha_route_inventory`
- Script smoke tests: `python -m unittest tests.scripts.test_public_alpha_scripts`

## Safe Public-Alpha Route Groups

The route inventory classifies the current safe public-alpha route groups. In
summary, public-alpha mode may expose:

- `/status`, `/api/status`, and `/api`
- exact-resolution workspace and `/api/resolve` without `store_root`
- deterministic search and query-plan routes
- source registry list/detail routes
- absence, subject-state, comparison, compatibility, representation, handoff,
  and decomposition listing routes
- archive-resolution eval reports without `index_path`

These routes are safe only in the constrained demo sense. They are not a final
security or production contract.

## Blocked Route Groups

Public-alpha mode blocks routes or route variants that accept or depend on:

- `index_path`
- `run_store_root`
- `task_store_root`
- `memory_store_root`
- `store_root`
- `bundle_path`
- arbitrary `output` path controls

It also blocks local fixture byte readback and bundle ZIP export routes pending
a later explicit route review.

## Review-Required Routes

Manifest export routes are currently allowed because they return bounded JSON
responses and do not write to caller-provided paths. They remain
`review_required` in the inventory because they expose structured resolution
metadata and should be manually reviewed again before any real hosted demo.

## Required Manual Checks Before Hosting

- Confirm the process is started with `--mode public_alpha`.
- Confirm `/api/status` reports `mode: public_alpha` and
  `safe_mode_enabled: true`.
- Confirm status output does not show absolute local paths.
- Run `python scripts/public_alpha_smoke.py --json` and retain the report.
- Inspect `control/inventory/public_alpha_routes.json` for every route that
  will be linked from the demo entry page.
- Confirm no demo page advertises local-dev-only path controls as available.
- Confirm no external crawler, sync, download automation, or background worker
  is enabled.
- Confirm the operator has a simple stop/rollback procedure.

## Blockers For Real Public Hosting

- No auth or accounts.
- No HTTPS/TLS provided by Eureka.
- No rate limiting or abuse controls.
- No production process manager.
- No durable public storage model.
- No multi-user isolation.
- No final public route contract.
- No audit logging or operational monitoring policy.

## Static Site Pack

LIVE_ALPHA_00 Static Public Site Pack adds a committed no-JS `public_site/`
tree for later static-hosting review. It explains Eureka's prototype status,
source matrix, eval/audit state, safe demo queries, limitations, roadmap, and
local quickstart without starting a server, deploying anything, adding backend
hosting, adding live source probes, scraping external systems, or claiming
production readiness.

## Next Recommendation

Public Alpha Rehearsal Evidence v0 should come next on the Codex-side
live-alpha lane. Public Alpha Hosting Pack v0 and LIVE_ALPHA_00 Static Public
Site Pack now package enough local/static evidence for rehearsal planning, but
a real hosted alpha remains blocked on external hosting posture, final route
review, abuse-control decisions, TLS/auth ownership, and operator approval.
