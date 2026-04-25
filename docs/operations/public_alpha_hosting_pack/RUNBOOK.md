# Public Alpha Rehearsal Runbook

This runbook is for a supervised public-alpha demo rehearsal. It assumes a
trusted operator is present and able to stop the process immediately.

## 1. Preflight

Run:

```powershell
git status --short --branch
git rev-parse --short HEAD
python --version
```

Stop if the working tree contains unexpected changes or if the branch is behind
the origin branch that the operator intends to rehearse.

## 2. Ensure Repo Sync

Run:

```powershell
git fetch origin
git status --short --branch
```

Proceed only if the branch status is understood. For a formal rehearsal, prefer
a clean worktree and a branch that is not behind `origin`.

## 3. Run Tests And Smoke Checks

Run:

```powershell
python scripts/public_alpha_smoke.py
python scripts/public_alpha_smoke.py --json
python scripts/generate_public_alpha_hosting_pack.py --check
python -m unittest discover -s runtime -t .
python -m unittest discover -s surfaces -t .
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
git diff --check
```

Capture the command, timestamp, exit code, and important output for the smoke
evidence template. Stop if any command fails.

## 4. Choose `public_alpha` Mode

Use `public_alpha` explicitly. Do not expose `local_dev` mode for a public-alpha
rehearsal.

Status-only check:

```powershell
python scripts/demo_http_api.py --mode public_alpha status
```

Local demo server:

```powershell
python scripts/demo_web_workbench.py --mode public_alpha --host 127.0.0.1 --port 8781
```

If a non-loopback host is used for a supervised rehearsal, the operator must
provide external network controls outside this repo. This pack does not provide
those controls.

## 5. Verify Status Endpoint

Check:

- `http://127.0.0.1:8781/status`
- `http://127.0.0.1:8781/api/status`

Expected:

- mode is `public_alpha`
- safe mode is enabled
- disabled capabilities include caller local path controls
- configured roots are reported only as kinds, not private path values

## 6. Verify Safe Routes

Use the smoke script as the primary safe-route check:

```powershell
python scripts/public_alpha_smoke.py
```

Optional local checks through the demo HTTP API:

```powershell
python scripts/demo_http_api.py --mode public_alpha search synthetic
python scripts/demo_http_api.py --mode public_alpha query-plan "Windows 7 apps"
python scripts/demo_http_api.py --mode public_alpha sources
```

Expected: safe read-only/search/inspect/eval routes return successful bounded
responses.

## 7. Verify Blocked Unsafe Routes

Use the smoke script as the primary blocked-route check:

```powershell
python scripts/public_alpha_smoke.py --json
```

The smoke checks include public-alpha blocks for caller-provided local
`index_path`, `run_store_root`, `task_store_root`, `memory_store_root`,
`store_root`, `bundle_path`, arbitrary `output`, and fixture byte readback
routes.

Expected: unsafe routes return structured blocked responses.

## 8. Capture Smoke Evidence

Fill in `SMOKE_EVIDENCE_TEMPLATE.md` with:

- date/time
- commit SHA
- branch status
- route inventory version/counts
- test and smoke results
- safe route samples
- blocked route samples
- known failures
- operator decision

Do not pre-fill evidence before running the commands.

## 9. Stop And Cleanup

Stop the stdlib demo server with `Ctrl+C` in the owning terminal.

After stopping, confirm the rehearsal process is no longer listening before
ending the rehearsal. Record any cleanup actions in the evidence notes.

## 10. Operator Signoff Or Failure

Complete `OPERATOR_SIGNOFF_TEMPLATE.md` only after the checks are complete.
Choose one decision:

- pass rehearsal
- fail rehearsal
- blocked

If any required check fails, mark the rehearsal as failed or blocked and record
the exact route, command, or blocker.

## Known Command Gap

No command currently fills the smoke evidence or signoff templates
automatically. The operator records those artifacts manually from command
output.
