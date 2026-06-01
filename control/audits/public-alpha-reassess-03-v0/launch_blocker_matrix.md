# Launch Blocker Matrix

```json
{
  "blockers": [
    {
      "blocker_id": "reviewed_record_count_below_threshold",
      "evidence": "Limited reviewed projection count 4 < threshold 25.",
      "launch_blocking": true,
      "public_explanation": "Limited reviewed projection count 4 < threshold 25.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "insufficient_domain_coverage",
      "evidence": "Reviewed domains 2 < threshold 3.",
      "launch_blocking": true,
      "public_explanation": "Reviewed domains 2 < threshold 3.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "limited_reviewed_records_are_not_verified_artifacts",
      "evidence": "Limited metadata/source-lead records do not establish downloadable artifact verification.",
      "launch_blocking": true,
      "public_explanation": "Limited metadata/source-lead records do not establish downloadable artifact verification.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "candidate_heavy_snapshot",
      "evidence": "Candidate count remains 36 versus 4 limited reviewed projections.",
      "launch_blocking": true,
      "public_explanation": "Candidate count remains 36 versus 4 limited reviewed projections.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "no_public_launch_approval",
      "evidence": "No explicit future manual approval exists for a public launch.",
      "launch_blocking": true,
      "public_explanation": "No explicit future manual approval exists for a public launch.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "public_launch_track_deferred",
      "evidence": "Public alpha launch remains deferred for discovery coverage.",
      "launch_blocking": true,
      "public_explanation": "Public alpha launch remains deferred for discovery coverage.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "no_seed_batch_manuals_scans",
      "evidence": "Manuals/scans discovery batch has not been added.",
      "launch_blocking": true,
      "public_explanation": "Manuals/scans discovery batch has not been added.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "no_seed_batch_driver_support",
      "evidence": "Driver/support discovery batch has not been added.",
      "launch_blocking": true,
      "public_explanation": "Driver/support discovery batch has not been added.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "no_snapshot_publication_rehearsal_after_larger_reviewed_corpus",
      "evidence": "No publication rehearsal has run after a substantially larger reviewed corpus.",
      "launch_blocking": true,
      "public_explanation": "No publication rehearsal has run after a substantially larger reviewed corpus.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    }
  ],
  "blockers_count": 9,
  "created_at": "2026-06-02T00:00:00Z",
  "launch_blocked": true,
  "nonblocking_positives": [
    "candidate_discovery_stack_present",
    "live_metadata_pilot_present",
    "live_metadata_review_present",
    "local_apply_gate_present",
    "limited_reviewed_metadata_record_present",
    "reviewed_source_leads_present",
    "seed_batches_present",
    "review_batch_present",
    "snapshot_refresh_present",
    "public_search_ux_models_present",
    "needs_absences_present"
  ],
  "reassess_id": "public_alpha_reassess_03",
  "schema_version": "public_alpha_launch_blocker_register.v0",
  "warnings": [
    "route correctness is not product usefulness",
    "limited reviewed metadata/source-lead records are not verified artifacts",
    "four limited reviewed records is below public-alpha threshold",
    "candidate-rich snapshots remain internal review material",
    "third-domain corpus growth is still needed"
  ],
  "warnings_count": 5
}
```
