# Batch 0 Slot Completion Guide

Use the canonical guide at `docs/operations/MANUAL_OBSERVATION_SLOT_COMPLETION_GUIDE.md`.

Batch 0-specific reminders:

- Select one slot from `observations/pending_batch_0_observations.json`.
- Keep the original `query_id` and `system_id`.
- Enter the query manually in the named system.
- Record short public-safe snippets or summaries only.
- Use failure classes from `docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md`.
- Validate before changing any status away from `pending_manual_observation`.

Do not mark observed unless the human observation was actually performed.
