# Live Probe Execution Report

Execution result: `BLOCKED`.

The command path was exercised in dry preflight mode:

```text
python scripts/run_ia_metadata_live_probe.py --identifier eureka-software-fixture --check
```

Observed result:

- attempted: `false`
- request_count: `0`
- network_used: `false`
- result_status: `blocked`

The blocked result is recorded in
`generated/sample_live_probe_result.json`.
