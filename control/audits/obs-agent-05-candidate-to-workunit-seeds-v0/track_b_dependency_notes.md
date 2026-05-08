# Track B Dependency Notes

OBS-AGENT-05 does not create runtime WorkUnit records.

Before any seed can be promoted by a future task, Track B must provide:

- Runtime WorkUnit acceptance semantics.
- Review decision mapping from seed draft to runtime record.
- Node capability and policy matching.
- Local state and replay/idempotency handling.
- WorkUnit result and audit packet handling.
- Source policy integration for source-derived WorkUnit seeds.

The current local Track B packet was observed at TRACK-B-06. OBS-AGENT-05 did
not update `.aide/queue/index.yaml` or latest task packets because Track B may
be advancing on another machine.
