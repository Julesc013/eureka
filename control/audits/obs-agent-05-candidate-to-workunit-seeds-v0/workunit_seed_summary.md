# WorkUnit Seed Draft Summary

This summary is generated from repo-local WorkUnit seed examples, SearchNeed seed drafts, and review queue metadata. It does not create executable WorkUnits.

Proposed WorkUnit seed drafts: 6

## Seed Drafts

| Priority | Seed | Type | Status | Review action | Source family |
| --- | --- | --- | --- | --- | --- |
| high 82 | `workunit_seed_source_policy_review_archive_metadata_v0` | `source_policy_review` | `needs_human_review` | `approve_as_workunit_seed_future` | `internet_archive_metadata` |
| high 72 | `workunit_seed_metadata_probe_planning_archive_v0` | `approved_metadata_probe_planning_future` | `needs_human_review` | `approve_as_workunit_seed_future` | `internet_archive_metadata` |
| medium 55 | `workunit_seed_extraction_gap_driver_inf_v0` | `container_deepening_planning_future` | `needs_human_review` | `approve_as_workunit_seed_future` | `repo_local_candidate` |
| medium 45 | `workunit_seed_compatibility_review_firefox_xp_v0` | `compatibility_evidence_review` | `needs_more_evidence` | `request_more_evidence_future` | `local_eval` |
| medium 40 | `workunit_seed_minimal_v0` | `search_need_review` | `needs_human_review` | `approve_as_workunit_seed_future` | `broad_web_policy_blocked` |
| blocked 24 | `workunit_seed_policy_blocked_broad_web_v0` | `policy_blocked_review` | `policy_blocked` | `mark_policy_blocked_future` | `broad_web_policy_blocked` |

## High-Priority WorkUnit Seed Drafts

- `workunit_seed_source_policy_review_archive_metadata_v0`: `source_policy_review` (Review archive metadata source policy)
- `workunit_seed_metadata_probe_planning_archive_v0`: `approved_metadata_probe_planning_future` (Plan archive metadata probe shape)

## Source-Policy Review WorkUnit Seed Drafts

- `workunit_seed_source_policy_review_archive_metadata_v0`: `source_policy_review` (Review archive metadata source policy)

## Metadata-Probe Planning WorkUnit Seed Drafts

- `workunit_seed_metadata_probe_planning_archive_v0`: `approved_metadata_probe_planning_future` (Plan archive metadata probe shape)

## Extraction-Gap WorkUnit Seed Drafts

- `workunit_seed_extraction_gap_driver_inf_v0`: `container_deepening_planning_future` (Plan container deepening for driver INF discovery)

## Compatibility-Review WorkUnit Seed Drafts

- `workunit_seed_compatibility_review_firefox_xp_v0`: `compatibility_evidence_review` (Review compatibility evidence needed for Firefox XP timeline)

## Policy-Blocked WorkUnit Seed Drafts

- `workunit_seed_policy_blocked_broad_web_v0`: `policy_blocked_review` (Keep broad web WorkUnit idea blocked for policy review)

## Review Boundary

- Approving a WorkUnit seed does not execute it.
- Approving a WorkUnit seed does not make it an observed baseline.
- Approving a WorkUnit seed does not make it accepted evidence.
- Approving a WorkUnit seed does not create a runtime WorkUnit until Track B accepts it.
- Approving a WorkUnit seed does not mutate the master index.
- Approving a WorkUnit seed does not approve live source access.

## Track B Dependencies

- Track B must define and accept runtime WorkUnit semantics before any seed can become executable work.
- Source policy review remains separate from WorkUnit seed review.
- Node capability, local state, idempotency, and recovery semantics remain future/deferred.

## Human Review Needs

- Confirm each proposed work label, scope, allowed action, and forbidden action.
- Tune or deduplicate seeds before any downstream Track B handoff.
- Keep policy-blocked and needs-more-evidence seeds out of executable flows.
