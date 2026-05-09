# SearchNeed Seed Draft Summary

This summary is generated from repo-local seed examples and review queue metadata. It does not create runtime SearchNeeds.

Proposed seed drafts: 5

## Seed Drafts

| Priority | Seed | Type | Status | Review action | Source family |
| --- | --- | --- | --- | --- | --- |
| high 82 | `search_need_seed_source_gap_archive_metadata_v0` | `source_gap_need_seed` | `needs_human_review` | `approve_as_search_need_seed_future` | `internet_archive_metadata` |
| medium 55 | `search_need_seed_extraction_gap_driver_inf_v0` | `extraction_gap_need_seed` | `needs_human_review` | `approve_as_search_need_seed_future` | `repo_local_candidate` |
| medium 45 | `search_need_seed_compatibility_gap_firefox_xp_v0` | `compatibility_gap_need_seed` | `needs_more_evidence` | `request_more_evidence_future` | `local_eval` |
| medium 40 | `search_need_seed_minimal_v0` | `manual_observation_need_seed` | `needs_human_review` | `approve_for_manual_observation_future` | `broad_web_policy_blocked` |
| blocked 24 | `search_need_seed_policy_blocked_broad_web_v0` | `policy_blocked_need_seed` | `policy_blocked` | `mark_policy_blocked_future` | `broad_web_policy_blocked` |

## High-Priority Seed Drafts

- `search_need_seed_source_gap_archive_metadata_v0`: `source_gap_need_seed` (Archive metadata need for legacy software discovery)

## Policy-Blocked Seed Drafts

- `search_need_seed_policy_blocked_broad_web_v0`: `policy_blocked_need_seed` (Policy-blocked broad web source gap for Windows 7 applications)

## Duplicate Or Ambiguous Seed Drafts

- No duplicate seed is asserted by this generated manifest; compatibility and manual-observation seeds still require human review for ambiguity.

## Source-Gap-Derived Seed Drafts

- `search_need_seed_source_gap_archive_metadata_v0`: `source_gap_need_seed` (Archive metadata need for legacy software discovery)

## Extraction-Gap-Derived Seed Drafts

- `search_need_seed_extraction_gap_driver_inf_v0`: `extraction_gap_need_seed` (Need for finding driver INF files inside support media)

## Compatibility-Gap-Derived Seed Drafts

- `search_need_seed_compatibility_gap_firefox_xp_v0`: `compatibility_gap_need_seed` (Compatibility timeline need for Firefox on Windows XP)

## Review Boundary

- Approving a seed does not make it an observed baseline.
- Approving a seed does not make it accepted evidence.
- Approving a seed does not create a runtime SearchNeed until Track B runtime accepts it.
- Approving a seed does not mutate the master index.
- Approving a seed does not approve live source access.

## Track B Dependency

- Track B must define and accept runtime SearchNeed semantics before any seed can become runtime state.
- Source policy review remains separate from SearchNeed seed review.

## Human Review Needs

- Confirm whether each draft describes a useful future SearchNeed.
- Tune labels and aliases before any downstream Track B handoff.
- Keep policy-blocked and needs-more-evidence seeds out of runtime flows.
