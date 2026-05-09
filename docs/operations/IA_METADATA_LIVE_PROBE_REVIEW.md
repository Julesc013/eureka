# IA Metadata Live Probe Review

Current review decision: `blocked_pending_operator_approval`.

Before an operator approves a live run, review these records:

- `control/inventory/connectors/internet_archive_source_policy.json`
- `control/inventory/connectors/internet_archive_endpoint_policy.json`
- `control/inventory/connectors/internet_archive_rate_limit_policy.json`
- `control/inventory/connectors/internet_archive_cache_policy.json`
- `control/inventory/connectors/internet_archive_kill_switch_policy.json`
- `control/inventory/connectors/internet_archive_live_probe_policy.json`
- `control/inventory/connectors/internet_archive_live_probe_allowed_identifiers.json`

The approval must name exactly one identifier and must keep download, item file
fetch, scraping, broad search, public fanout, source sync, public-index
mutation, and master-index mutation disabled.

## Blocked Behavior

When approval is missing, run:

```text
python scripts/run_ia_metadata_live_probe.py --identifier eureka-software-fixture --check
```

The expected result is:

- `result_status: blocked`
- `attempted: false`
- `request_count: 0`
- `network_used: false`

## Review Seeds

After a future approved live probe, source-cache candidates, evidence previews,
and review queue seeds still require human review before persistence or
downstream use.
