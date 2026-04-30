# Staged Entity Model

Future staged metadata types:

- `staged_pack_reference`: local pointer to a validated pack root, pack ID,
  pack version, checksum, and Pack Import Report v0 ID.
- `staged_validation_report`: local copy or reference to validation status and
  issues.
- `staged_source_candidate`: source metadata claim candidate with provenance.
- `staged_evidence_candidate`: evidence claim candidate with provenance.
- `staged_index_summary`: summary-only index coverage candidate, never a raw
  database.
- `staged_contribution_candidate`: review-submission candidate, not accepted
  truth.
- `staged_ai_output_candidate`: typed AI output candidate that remains
  review-required.
- `staged_issue`: privacy, rights, checksum, schema, or risk issue.
- `staged_decision_note`: local operator note for later review.

Each entity must record privacy classification, review status, local-only or
public-safe status, source pack/report provenance, whether it may enter a
future local index candidate mode, and whether it may enter a future
contribution queue candidate mode.

This document defines entity vocabulary only; it implements no entities.
