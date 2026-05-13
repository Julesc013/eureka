# Local Auto-Test Runbook

Start with an initialized local instance:

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
python scripts/eureka_local_server.py --instance ./eureka-instance --host 127.0.0.1 --port 8765
```

In another shell, run:

```bash
python scripts/eureka_local_auto_test.py --base-url http://127.0.0.1:8765 --json
python scripts/eureka_local_auto_search.py --base-url http://127.0.0.1:8765 --json
python scripts/eureka_local_eval_report.py --input control/audits/local-10-auto-test-search-harness-v0/generated/sample_auto_test_result.json --output control/audits/local-10-auto-test-search-harness-v0/generated/sample_eval_summary.md
```

The scripts refuse non-localhost base URLs. Reports describe local route,
search, absence, safety, and latency posture only.

LOCAL-10 does not enable LAN, deployment, source probes, extraction, model
calls, downloads, installs, or execution.

## LAN Safety Relationship

LOCAL-11 uses the auto-test harness as localhost regression evidence before
actual LAN smoke. The harness remains localhost-only and does not itself bind to
LAN-facing hosts. LOCAL-12 should run a separate read-only LAN smoke after the
LAN safety gate is in place.

## LOCAL-13 Use

LOCAL-13 clean-machine smoke runs the auto-test and auto-search harness from a
fresh explicit instance. The harness remains deterministic and
local-reviewed-index only; it does not generate synthetic queries, run source
probes, call model providers, or deploy.
