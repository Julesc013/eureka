# E2E Reference Replay Profile

Replay is a recorded run representation for `E2E-REFERENCE-RUNNER-00`. It must
not perform live provider calls or create accepted truth.

In operational language: replay must not perform live provider calls, and replay
must not create accepted truth.

## Minimum Event Envelope

Required fields:

- `schema_version`
- `run_id`
- `event_id`
- `sequence`
- `event_type`
- `producer_plane`
- `occurred_at`
- `payload_schema_ref`
- `payload`
- `payload_hash`
- `previous_event_hash`
- `causation_id`
- `correlation_id`
- `workunit_id`
- `source_provider_id`
- `authority_level`
- `synthetic_only`
- `privacy_posture`

## Requirements

- deterministic event ordering;
- no hidden in-memory state required for replay;
- explicit incomplete/truncated log posture;
- unknown event types are preserved as inert unsupported events;
- invalid hashes fail closed;
- replay events never silently invoke providers;
- replay cannot create accepted truth;
- synthetic replay stays isolated.
