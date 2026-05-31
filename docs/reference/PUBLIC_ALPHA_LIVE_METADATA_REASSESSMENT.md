# Public Alpha Live Metadata Reassessment

The live metadata reassessment packet records how source-backed candidates from
the bounded live metadata pilot affect public-alpha usefulness.

Required semantics:

- live metadata candidates are source observations
- live metadata candidates require review
- live metadata candidates are not reviewed truth
- live metadata candidates do not mutate reviewed, master, or public indexes
- raw live responses are not included
- launch is not recommended while reviewed-record thresholds are unmet

Current packet fields include:

- `live_metadata_pilot_ref`
- `fixture_candidate_count`
- `live_metadata_candidate_count`
- `total_candidate_count`
- `public_search_view_model_status`
- `needs_live_candidate_review`
- `needs_snapshot_refresh_after_review`
- boundary flags for deployment, launch, site output, mutation, downloads,
  extraction, model providers, and live source calls

