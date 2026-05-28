# Test Execution Policy

Normal AI-assisted work uses focused lanes from:

```bash
python scripts/eureka_test_select.py --changed --failed-first --json
```

Full unittest discovery is externalized:

```bash
python scripts/run_full_unittest_discovery.py
```

The harness writes local artifacts outside the repository under
`../eureka-test-runs/<run-id>/` by default. Repo-local private roots such as
`.aide.local/test-runs/` are forbidden unless an exceptional debugging command
explicitly opts in. Durable closeout evidence must be a compact summary copied
intentionally into `control/audits/`.

The harness may emit compact heartbeat lines for the operator, but raw unittest
stdout/stderr remain file artifacts and should not be pasted into AI sessions
unless the compact summaries are insufficient.

Allowed waiting status:

```text
WAITING_FOR_EXTERNAL_FULL_DISCOVERY
```
