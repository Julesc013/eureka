# Connector Policy Evaluation

Use policy evaluation before any future connector operation.

Current allowed outcomes:

- `allowed_fixture_replay` for committed offline fixtures
- `allowed_dry_run_only` for future operations represented without execution
- blocked decisions for missing approval, forbidden operations, endpoint policy,
  rate limit policy, kill switch, rights policy, or risk policy

Commands:

```text
python scripts/evaluate_connector_policy.py --request examples/connectors/core/live_probe/policy_blocked_live_probe_request_v0.json --check
python scripts/run_connector_fixture_replay.py --request examples/connectors/core/fixture_replay/minimal_fixture_replay_request_v0.json --check
python scripts/summarize_connector_families.py --input examples/connectors/core/families --check
```
