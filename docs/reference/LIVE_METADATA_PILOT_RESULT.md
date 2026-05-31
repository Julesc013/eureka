# Live Metadata Pilot Result

`live_metadata_pilot_result.v0` records the pilot status, approval state,
selected query count, request plan count, redacted summary count, candidate
handoffs, SCOUT outputs, review batch output, snapshot refresh handoff, and
public alpha reassess input.

When approval is absent, the expected status is:

```text
waiting_for_operator_live_metadata_approval
```

The result must keep these false:

- `raw_live_response_committed`
- `download_performed`
- `extraction_executed`
- `accepted_truth_created`
- `reviewed_index_mutated`
- `master_index_mutated`
- `public_index_mutated`
- `deployment_performed`
