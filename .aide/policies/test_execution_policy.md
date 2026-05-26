# Test Execution Policy

Normal AI-assisted work uses focused lanes from:

```bash
python scripts/eureka_test_select.py --changed --failed-first --json
```

Full unittest discovery is externalized:

```bash
python scripts/run_full_unittest_discovery.py
```

The harness writes local artifacts under `.aide.local/test-runs/<run-id>/`.
That local directory is not committed. Durable closeout evidence must be a
compact summary copied intentionally into `control/audits/`.

Allowed waiting status:

```text
WAITING_FOR_EXTERNAL_FULL_DISCOVERY
```
