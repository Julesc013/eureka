# Observation Candidate Review Queue

This queue is governance only. It records future recommended review actions without approving candidates.

## Queue Entries

| Priority | Candidate | Type | Source family | Review state | Recommended action |
| --- | --- | --- | --- | --- | --- |
| high 82 | `obs_candidate_source_gap_internet_archive_metadata_v0` | `source_lead` | `internet_archive_metadata` | `ready_for_human_decision` | `approve_as_source_lead_future` |
| high 76 | `obs_candidate_source_gap_wayback_metadata_v0` | `source_lead` | `wayback_cdx_memento_metadata` | `ready_for_human_decision` | `approve_as_source_lead_future` |
| high 70 | `obs_candidate_source_gap_github_releases_v0` | `source_lead` | `github_releases_metadata` | `ready_for_human_decision` | `approve_as_source_lead_future` |
| medium 66 | `obs_candidate_source_gap_package_registry_v0` | `source_lead` | `package_registry_metadata` | `needs_human_review` | `approve_as_source_lead_future` |
| medium 60 | `obs_candidate_local_eval_source_gap_v0` | `source_lead` | `repo_local_candidate` | `queued_for_review` | `approve_as_source_lead_future` |
| medium 60 | `obs_candidate_source_lead_v0` | `source_lead` | `repo_local_candidate` | `queued_for_review` | `approve_as_source_lead_future` |
| medium 55 | `obs_candidate_local_eval_extraction_gap_v0` | `work_unit_seed` | `repo_local_candidate` | `queued_for_review` | `approve_as_workunit_seed_future` |
| medium 50 | `obs_candidate_local_eval_ranking_gap_v0` | `search_need_seed` | `repo_local_candidate` | `queued_for_review` | `approve_as_search_need_seed_future` |
| medium 45 | `obs_candidate_local_eval_failure_mining_batch_0_v0` | `local_eval_failure` | `local_eval` | `needs_human_review` | `request_more_evidence_future` |
| medium 45 | `obs_candidate_local_eval_failure_v0` | `local_eval_failure` | `local_eval` | `needs_human_review` | `request_more_evidence_future` |
| medium 40 | `obs_candidate_minimal_v0` | `manual_slot_suggestion` | `broad_web_policy_blocked` | `needs_human_review` | `approve_for_manual_observation_future` |
| blocked 46 | `obs_candidate_source_gap_manual_only_forum_v0` | `source_lead` | `manual_only_forum_or_community` | `policy_blocked` | `approve_as_source_lead_future` |
| blocked 24 | `obs_candidate_source_gap_policy_blocked_v0` | `policy_blocked_candidate` | `broad_web_policy_blocked` | `policy_blocked` | `mark_policy_blocked_future` |
| blocked 0 | `obs_candidate_local_eval_policy_blocked_v0` | `policy_blocked_candidate` | `broad_web_policy_blocked` | `policy_blocked` | `mark_policy_blocked_future` |
| blocked 0 | `obs_candidate_policy_blocked_v0` | `policy_blocked_candidate` | `broad_web_policy_blocked` | `policy_blocked` | `mark_policy_blocked_future` |

## Review Boundary

- Queue entry is not approval.
- Recommended action is not a review decision.
- No entry is observed baseline evidence.
- No entry is accepted evidence truth.
- No entry can mutate the master index.
- Source access remains unapproved unless a separate future source policy approves it.
