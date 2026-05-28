# Public Alpha Read-Only Closeout

`PUBLIC-ALPHA-READONLY-CLOSEOUT-01` closes the public alpha read-only route
foundation and hosting-readiness baseline before promotion. It is not a launch
task and does not deploy or publish anything.

## Verified Baseline

- Public alpha web routes exist for search, object, source, evidence, absence,
  and known needs.
- Public alpha API routes are read-only.
- Object, source, evidence, absence, and known-need packets are backed by the
  reviewed snapshot and read-only relay foundation.
- Hosting readiness exists for static snapshot site, read-only relay service,
  local preview server, and a blocked future dynamic gateway.
- Security headers, rate limits, observability, privacy, abuse/takedown, and
  rollback plans are recorded.

## Boundaries

No deployment, production readiness claims, no public launch readiness claims,
live source fanout, source probes, downloads, uploads, extraction,
model/provider calls, public mutation, account systems, public/master index
mutation, committed instance state, secrets, and raw full-discovery logs remain
forbidden.

## External Full Discovery

No external full-discovery summary has been provided for the current dev head.
The closeout therefore stops at `WAITING_FOR_EXTERNAL_FULL_DISCOVERY` with this
operator command:

```powershell
python scripts/run_full_unittest_discovery.py `
  --out ../eureka-test-runs/public_alpha_readonly_closeout
```

The harness prints an immediate start banner and periodic heartbeat while
keeping raw unittest stdout/stderr in files. Operators may also use the
background workflow:

```powershell
python scripts/start_full_discovery.py --run-id public_alpha_readonly_closeout
python scripts/check_full_discovery.py --run-id public_alpha_readonly_closeout
```

For a non-spammy live console watcher that prints the paste-ready compact
handoff at completion:

```powershell
python scripts/check_full_discovery.py --run-id public_alpha_readonly_closeout --watch --interval-seconds 300 --handoff
```

The operator should paste back only the compact summary, failure families, failed
tests list, and `git status --short --branch`.
