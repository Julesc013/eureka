# Public Alpha Safe Mode

Public Alpha Safe Mode v0 is Eureka's first constrained hosting posture for
the existing stdlib web/API backend.

It is safe-mode work, not production deployment. It does not add auth,
accounts, HTTPS/TLS, a process manager, rate limiting, multi-user isolation,
or durable public storage.

## Mode

Run the demo server in public-alpha mode with:

```powershell
python scripts/demo_web_workbench.py --mode public_alpha
python scripts/demo_http_api.py --mode public_alpha status
python scripts/public_alpha_smoke.py
```

The mode can also be selected with:

```powershell
$env:EUREKA_WEB_MODE = "public_alpha"
```

## Safe Routes

Public-alpha mode keeps bounded read-only routes available, including:

- `/status`
- `/api/status`
- `/api`
- `/search` and `/api/search`
- `/query-plan` and `/api/query-plan`
- `/` and `/api/resolve` without `store_root`
- `/sources`, `/source`, `/api/sources`, and `/api/source`
- `/evals/archive-resolution` and `/api/evals/archive-resolution` without `index_path`
- bounded read-only pages for comparison, compatibility, source inventory,
  representations, handoff, absence reports, subject states, and decomposition
  listings

Status output reports configured root kinds only as `configured` or
`not_configured`; it must not expose private local paths.

## Blocked Routes And Parameters

Public-alpha mode blocks caller-provided local filesystem controls:

- `index_path`
- `run_store_root`
- `task_store_root`
- `memory_store_root`
- `store_root`
- `bundle_path`
- arbitrary output paths

It also disables route groups that require those controls or expose local
fixture bytes:

- local index build/status/query routes
- local task routes
- resolution-run persistence routes
- resolution-memory routes
- local stored-export routes
- arbitrary bundle-path inspection
- fetch, raw member readback, and bundle export routes

Blocked API routes return a structured `403` JSON response. Blocked HTML
routes render a compatibility-first blocked page with the mode, reason, and
blocked parameter names where applicable.

The auditable route inventory lives at
`control/inventory/public_alpha_routes.json`. The readiness review and operator
checklist live at:

- `docs/operations/PUBLIC_ALPHA_READINESS_REVIEW.md`
- `docs/operations/PUBLIC_ALPHA_OPERATOR_CHECKLIST.md`
- `docs/operations/public_alpha_hosting_pack/`

## Still Not Production

Public Alpha Safe Mode v0 does not settle:

- authentication or accounts
- HTTPS/TLS
- hosting topology
- abuse controls
- audit logging
- private user storage
- production deployment
- live source sync or crawling
- ranking, fuzzy retrieval, vector search, or LLM planning

It is a bounded public-demo posture for the current local backend, intended to
make unsafe local-path behaviors explicit and blocked before any hosted alpha
is attempted.
