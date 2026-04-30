# Public Alpha Safe Mode

Public Alpha Safe Mode v0 is Eureka's first constrained hosting posture for
the existing stdlib web/API backend.

It is safe-mode work, not production deployment. It does not add auth,
accounts, HTTPS/TLS, a process manager, rate limiting, multi-user isolation,
or durable public storage.

## Mode

Run the demo server in public-alpha mode with:

```powershell
python scripts/run_public_alpha_server.py --check-config
python scripts/run_public_alpha_server.py --print-config-json
python scripts/demo_web_workbench.py --mode public_alpha
python scripts/demo_http_api.py --mode public_alpha status
python scripts/public_alpha_smoke.py
```

LIVE_ALPHA_01 Production Public-Alpha Wrapper adds
`scripts/run_public_alpha_server.py` as the preferred public-alpha process
entrypoint for future supervised rehearsals. The wrapper defaults to
`127.0.0.1:8781`, requires `public_alpha` mode, refuses nonlocal bind hosts
unless explicitly acknowledged, and keeps live probes, live Internet Archive
access, caller-provided local paths, downloads/readback, user storage,
deployment approval, and production readiness closed by default. It performs
no deployment and adds no auth, TLS, rate limiting, or process manager.

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
- `docs/operations/PUBLIC_ALPHA_WRAPPER.md`
- `docs/operations/public_alpha_hosting_pack/`

Live Backend Handoff Contract v0 reserves future `/api/v1` routes separately
from these current local `/api` helper routes. Public Alpha Safe Mode does not
make `/api/v1` live and does not enable live probes.

Live Probe Gateway Contract v0 defines future disabled-by-default probe policy
separately from safe-mode runtime behavior. Public Alpha Safe Mode still does
not call external sources, fetch URLs, enable downloads, or make Internet
Archive live probing available.

Native Action / Download / Install Policy v0 keeps public-alpha action posture
read-only and metadata-first. Public-alpha does not enable downloads, fixture
byte fetch, install handoff, package-manager handoff, mirrors, execution,
malware scanning, rights-clearance claims, private uploads, or system-changing
actions.

Native Local Cache / Privacy Policy v0 keeps public-alpha privacy posture
closed by default. Public-alpha does not enable private cache, private file
ingestion, local archive scanning, telemetry, analytics, accounts, cloud sync,
diagnostics upload, source credentials, or private path exposure.

Public Search Safety / Abuse Guard v0 now defines the policy-only guardrails for
future `/search` and `/api/v1/search` work. Public Alpha Safe Mode remains
compatible with that guard: `local_index_only` is the only future allowed mode,
public search is not live, live probes are disabled, downloads/installers/
uploads/local paths are forbidden, telemetry defaults off, and no rate-limit,
auth, account, or logging runtime is added by the safety policy.

## Still Not Production

Public Alpha Safe Mode v0 does not settle:

- authentication or accounts
- HTTPS/TLS
- hosting topology
- abuse controls
- audit logging
- private user storage
- private cache or private file ingestion
- telemetry, analytics, diagnostics upload, accounts, or cloud sync
- production deployment
- live source sync or crawling
- live source probes or live Internet Archive calls
- live `/api/v1` backend handoff
- download, mirror, install, execute, restore, uninstall, or rollback actions
- malware scanning or rights-clearance claims
- ranking, fuzzy retrieval, vector search, or LLM planning

It is a bounded public-demo posture for the current local backend, intended to
make unsafe local-path behaviors explicit and blocked before any hosted alpha
is attempted.
