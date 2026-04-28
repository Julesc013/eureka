# Public Alpha Operator Checklist

This checklist is operator guidance for a constrained Eureka public-alpha demo
rehearsal. It is not deployment infrastructure.

## Preflight

- Confirm the working tree is clean.
- Confirm the route inventory exists at
  `control/inventory/public_alpha_routes.json`.
- Confirm the readiness review has been read:
  `docs/operations/PUBLIC_ALPHA_READINESS_REVIEW.md`.
- Confirm the hosting pack has been read:
  `docs/operations/public_alpha_hosting_pack/README.md`.
- Confirm Public Alpha Rehearsal Evidence v0 has been read:
  `docs/operations/public_alpha_rehearsal_evidence_v0/README.md`.
- Confirm Public Alpha Wrapper guidance has been read:
  `docs/operations/PUBLIC_ALPHA_WRAPPER.md`.
- Confirm the demo does not need auth, accounts, private user state, live
  crawling, broad downloads, installer behavior, or background workers.

## Configuration

- Prefer `python scripts/run_public_alpha_server.py` for the process
  entrypoint.
- Run `python scripts/run_public_alpha_server.py --check-config` before any
  supervised rehearsal.
- Start only with `public_alpha` mode.
- Do not bind outside localhost unless a supervisor explicitly acknowledges the
  wrapper's nonlocal bind warning. This is still no deployment approval.
- Do not pass local-dev roots such as `--store-root`, `--run-store-root`,
  `--task-store-root`, or `--memory-store-root`.
- Keep live probes, live Internet Archive access, downloads/readback, local
  path controls, and user storage disabled.
- Do not expose `local_dev` mode to a public network.
- Keep any external reverse proxy, TLS, access controls, logging, or abuse
  controls outside this repo until a future hosting pack defines them.

## Route Safety

- Check `/api/status` before exposing any route.
- Expose only route groups classified as `safe_public_alpha` in
  `control/inventory/public_alpha_routes.json`.
- Treat `review_required` route groups as opt-in for a supervised demo only.
- Do not expose routes classified as `local_dev_only` or
  `blocked_public_alpha`.

## Local Path Exposure

- Confirm `/api/status` reports root kinds only as `configured` or
  `not_configured`.
- Confirm no response contains private absolute local paths.
- Confirm caller-provided `index_path`, `run_store_root`, `task_store_root`,
  `memory_store_root`, `store_root`, `bundle_path`, and `output` parameters
  return blocked responses in public-alpha mode.

## Smoke Commands

Run:

```powershell
python scripts/public_alpha_smoke.py
python scripts/public_alpha_smoke.py --json
python scripts/run_public_alpha_server.py --check-config
python scripts/run_public_alpha_server.py --print-config-json
python scripts/generate_public_alpha_hosting_pack.py --check
python scripts/generate_public_alpha_rehearsal_evidence.py --check
python -m unittest tests.operations.test_public_alpha_route_inventory
```

Capture:

- command
- timestamp
- exit code
- plain-text smoke summary
- JSON smoke report
- commit SHA

For a supervised rehearsal, record the result in:

- `docs/operations/public_alpha_hosting_pack/SMOKE_EVIDENCE_TEMPLATE.md`
- `docs/operations/public_alpha_hosting_pack/OPERATOR_SIGNOFF_TEMPLATE.md`
- `docs/operations/public_alpha_rehearsal_evidence_v0/SIGNOFF_TEMPLATE.md`

## Stop Procedure

- Stop the stdlib demo process with `Ctrl+C` in the owning terminal.
- If the process was launched by another wrapper, stop that wrapper first.
- Re-run `/api/status` only if the process is still expected to be reachable.
- Record any blocked-route failures before restarting.

## Known Limitations

- No auth or accounts.
- No Eureka-provided HTTPS/TLS.
- No rate limiting or abuse controls.
- No production process manager.
- No multi-user storage isolation.
- No final public route contract.
- No live source sync or crawling.
- No live probes or live Internet Archive access.
- No installer, execution, restore, or import behavior.

## Do Not Expose If

- The server is not in `public_alpha` mode.
- The smoke script fails.
- The hosting pack summary check fails.
- `/api/status` leaks an absolute local path.
- Any caller-provided local path route returns success in public-alpha mode.
- A demo requires local-dev-only routes such as local index, local task, run,
  memory, store, fetch, member, or arbitrary bundle inspection routes.
- The operator cannot stop the server immediately.
