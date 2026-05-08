# Track B Dependency Notes

OBS-AGENT-04 does not create runtime SearchNeed records.

Before any seed can be promoted by a future task, Track B must provide:

- Runtime SearchNeed contract and acceptance semantics.
- Review decision mapping from seed draft to runtime record.
- Duplicate and merge behavior.
- Source policy integration for source-gap-derived seeds.
- Evidence and observation gates separate from demand signals.

The current local Track B packet was observed at TRACK-B-06. OBS-AGENT-04 did
not update `.aide/queue/index.yaml` or latest task packets because Track B may
be advancing on another machine.
