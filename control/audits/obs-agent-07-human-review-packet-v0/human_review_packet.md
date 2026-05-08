# OBS Human Review Packet

Use this packet to decide what should happen next. It is not a decision record.

Approving an item does not make it an observed baseline.
Approving an item does not make it accepted evidence truth.
Approving an item does not approve live source access.
Approving an item does not create runtime SearchNeeds.
Approving an item does not create executable WorkUnits.
Approving an item does not mutate the master index.

## Summary

- Review items: 35
- Source policy items: 2
- SearchNeed seed items: 5
- WorkUnit seed items: 6
- Blocked items: 9
- Track B dependency items: 7

## Decision Table

| Priority | Item | Type | Recommended decision | Policy | Track B dependency | Human decision |
| --- | --- | --- | --- | --- | --- | --- |
| `high` | `review_item::search_need_seed_source_gap_archive_metadata_v0` | `search_need_seed_review` | `approve_as_search_need_seed_future` | `future_deferred_source_policy_required` | `future_track_b_search_need_runtime` |  |
| `high` | `review_item::obs_candidate_source_gap_github_releases_v0` | `source_gap_review` | `approve_as_source_lead_future` | `future_deferred_source_policy_required` | `human_review_queue` |  |
| `high` | `review_item::obs_candidate_source_gap_internet_archive_metadata_v0` | `source_gap_review` | `approve_as_source_lead_future` | `future_deferred_source_policy_required` | `human_review_queue` |  |
| `high` | `review_item::obs_candidate_source_gap_wayback_metadata_v0` | `source_gap_review` | `approve_as_source_lead_future` | `future_deferred_source_policy_required` | `human_review_queue` |  |
| `high` | `review_item::workunit_seed_metadata_probe_planning_archive_v0` | `workunit_seed_review` | `approve_as_workunit_seed_future` | `future_deferred_source_policy_required` | `future_track_b_workunit_runtime` |  |
| `high` | `review_item::workunit_seed_source_policy_review_archive_metadata_v0` | `workunit_seed_review` | `approve_as_workunit_seed_future` | `future_deferred_source_policy_required` | `future_track_b_workunit_runtime` |  |
| `medium` | `review_item::obs_candidate_local_eval_extraction_gap_v0` | `candidate_review` | `approve_as_workunit_seed_future` | `not_external` | `human_review_queue` |  |
| `medium` | `review_item::obs_candidate_local_eval_ranking_gap_v0` | `candidate_review` | `approve_as_search_need_seed_future` | `not_external` | `human_review_queue` |  |
| `medium` | `review_item::obs_candidate_minimal_v0` | `manual_observation_selection` | `approve_for_manual_observation_future` | `not_approved_for_agent_access` | `human_review_queue` |  |
| `medium` | `review_item::obs_candidate_local_eval_failure_mining_batch_0_v0` | `request_more_evidence_review` | `request_more_evidence` | `not_external` | `human_review_queue` |  |
| `medium` | `review_item::obs_candidate_local_eval_failure_v0` | `request_more_evidence_review` | `request_more_evidence` | `not_external` | `human_review_queue` |  |
| `medium` | `review_item::search_need_seed_compatibility_gap_firefox_xp_v0` | `search_need_seed_review` | `request_more_evidence` | `not_external` | `future_track_b_search_need_runtime` |  |
| `medium` | `review_item::search_need_seed_extraction_gap_driver_inf_v0` | `search_need_seed_review` | `approve_as_search_need_seed_future` | `not_external` | `future_track_b_search_need_runtime` |  |
| `medium` | `review_item::search_need_seed_minimal_v0` | `search_need_seed_review` | `approve_for_manual_observation_future` | `not_approved_for_agent_access` | `future_track_b_search_need_runtime` |  |
| `medium` | `review_item::obs_candidate_local_eval_source_gap_v0` | `source_gap_review` | `approve_as_source_lead_future` | `source_policy_required_before_external_access` | `human_review_queue` |  |
| `medium` | `review_item::obs_candidate_source_gap_package_registry_v0` | `source_gap_review` | `approve_as_source_lead_future` | `future_deferred_source_policy_required` | `human_review_queue` |  |
| `medium` | `review_item::obs_candidate_source_lead_v0` | `source_gap_review` | `approve_as_source_lead_future` | `source_policy_required_before_external_access` | `human_review_queue` |  |
| `medium` | `review_item::obs_candidates_to_human_review` | `track_b_dependency_review` | `no_action` | `not_external` | `review_queue_future` |  |
| `medium` | `review_item::review_queue_to_track_b_candidate_store` | `track_b_dependency_review` | `no_action` | `not_external` | `candidate_store_future` |  |
| `medium` | `review_item::search_need_seeds_to_track_b_future` | `track_b_dependency_review` | `no_action` | `not_external` | `candidate_store_future` |  |
| `medium` | `review_item::workunit_seeds_to_local_foundry_state` | `track_b_dependency_review` | `no_action` | `not_external` | `local_foundry_state_future` |  |
| `medium` | `review_item::workunit_seeds_to_workunit_contract` | `track_b_dependency_review` | `no_action` | `not_external` | `workunit_contract_future` |  |
| `medium` | `review_item::workunit_seeds_to_workunit_result_contract` | `track_b_dependency_review` | `no_action` | `not_external` | `workunit_result_contract_future` |  |
| `medium` | `review_item::workunit_seed_compatibility_review_firefox_xp_v0` | `workunit_seed_review` | `request_more_evidence` | `not_external` | `future_track_b_workunit_runtime` |  |
| `medium` | `review_item::workunit_seed_extraction_gap_driver_inf_v0` | `workunit_seed_review` | `approve_as_workunit_seed_future` | `not_external` | `future_track_b_workunit_runtime` |  |
| `medium` | `review_item::workunit_seed_minimal_v0` | `workunit_seed_review` | `approve_as_workunit_seed_future` | `not_approved_for_agent_access` | `future_track_b_workunit_runtime` |  |
| `blocked` | `review_item::obs_candidate_local_eval_policy_blocked_v0` | `blocked_item_review` | `mark_policy_blocked` | `blocked_for_agent_until_source_policy_approval` | `human_review_queue` |  |
| `blocked` | `review_item::obs_candidate_policy_blocked_v0` | `blocked_item_review` | `mark_policy_blocked` | `blocked_for_agent_until_approved_api_exists` | `human_review_queue` |  |
| `blocked` | `review_item::obs_candidate_source_gap_manual_only_forum_v0` | `blocked_item_review` | `approve_as_source_lead_future` | `manual_human_only_permission_required` | `human_review_queue` |  |
| `blocked` | `review_item::obs_candidate_source_gap_policy_blocked_v0` | `blocked_item_review` | `mark_policy_blocked` | `blocked_no_autonomous_access_without_review` | `human_review_queue` |  |
| `blocked` | `review_item::search_need_seed_policy_blocked_broad_web_v0` | `search_need_seed_review` | `mark_policy_blocked` | `blocked_no_autonomous_access_without_review` | `future_track_b_search_need_runtime` |  |
| `blocked` | `review_item::policy_blocked_items_to_node_policy` | `source_policy_decision_preview` | `mark_policy_blocked` | `source_policy_review_required` | `node_policy` |  |
| `blocked` | `review_item::source_gaps_to_source_policy_decisions` | `source_policy_decision_preview` | `request_more_evidence` | `source_policy_review_required` | `node_policy` |  |
| `blocked` | `review_item::manual_pending_slots_to_future_observed_records` | `track_b_dependency_review` | `no_action` | `not_external` | `evidence_ledger_future` |  |
| `blocked` | `review_item::workunit_seed_policy_blocked_broad_web_v0` | `workunit_seed_review` | `mark_policy_blocked` | `blocked_no_autonomous_access_without_review` | `future_track_b_workunit_runtime` |  |

## Next Safe Action

- A human reviewer fills decision fields outside this generated packet.
- Keep source-policy items blocked until explicit source policy review.
- Keep SearchNeed and WorkUnit seeds draft-only until Track B accepts a future conversion path.
