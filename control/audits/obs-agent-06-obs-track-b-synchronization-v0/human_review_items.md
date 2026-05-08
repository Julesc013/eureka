# Human Review Items

## Ready For Review

- `obs_candidates_to_human_review`: triage local eval candidates and candidate records.
- `review_queue_to_track_b_candidate_store`: review the OBS queue before any future Track B candidate-store handoff.
- `search_need_seeds_to_track_b_future`: review SearchNeed seed drafts before any runtime SearchNeed path exists.
- `workunit_seeds_to_workunit_contract`: review WorkUnit seed drafts against Track B WorkUnit contract shape.
- `workunit_seeds_to_workunit_result_contract`: review result expectations before any future WorkUnit result path.
- `workunit_seeds_to_local_foundry_state`: review local-state expectations before any future private draft state.

## Still Blocked

- `source_gaps_to_source_policy_decisions`: blocked until explicit source policy review.
- `policy_blocked_items_to_node_policy`: blocked by source and node policy.
- `manual_pending_slots_to_future_observed_records`: blocked until human manual observation occurs.

## Review Boundary

- Reviewing an item does not create evidence truth.
- Reviewing an item does not create runtime SearchNeeds or WorkUnits.
- Reviewing an item does not approve live source access.
- Reviewing an item does not mutate the master index.
