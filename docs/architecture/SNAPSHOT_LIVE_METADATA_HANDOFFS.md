# Snapshot Live Metadata Handoffs

The live metadata pilot hands snapshot refresh only redacted summaries and
review-only candidate records. Raw Internet Archive responses are excluded from
the committed handoff.

Snapshot refresh consumes:

- `control/inventory/live_metadata_pilot_result.json`
- `control/inventory/live_metadata_pilot_candidate_matrix.json`
- `control/inventory/live_metadata_pilot_scout_matrix.json`
- `control/inventory/live_metadata_pilot_review_matrix.json`
- `control/inventory/live_metadata_pilot_snapshot_handoff_matrix.json`
- `control/inventory/live_metadata_pilot_public_alpha_reassess_matrix.json`

The output is a candidate-facing projection. Local apply, review decisions, and
public snapshot publication remain separate gates.
