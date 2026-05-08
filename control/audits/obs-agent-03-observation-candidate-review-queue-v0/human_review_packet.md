# Human Review Packet

This packet is a compact review aid. It records future recommended review actions only.

## Top Candidates

| Candidate | Recommended action | Rationale | Policy status |
| --- | --- | --- | --- |
| `obs_candidate_source_gap_internet_archive_metadata_v0` | `approve_as_source_lead_future` | Highest-scored source gap candidate; old-platform archive metadata and member discovery are strong local fits. | Future source policy required. |
| `obs_candidate_source_gap_wayback_metadata_v0` | `approve_as_source_lead_future` | Temporal capture metadata may address dead vendor and release-note gaps. | Future source policy and URI privacy review required. |
| `obs_candidate_source_gap_github_releases_v0` | `approve_as_source_lead_future` | Release metadata may address source/version identity gaps. | Future repository identity and source policy review required. |
| `obs_candidate_source_gap_package_registry_v0` | `approve_as_source_lead_future` | Package/version metadata may address package identity and source metadata gaps. | Future package identity and source policy review required. |
| `obs_candidate_local_eval_extraction_gap_v0` | `approve_as_workunit_seed_future` | Member-level extraction gap is well scoped to local support-media query classes. | Track B WorkUnit seed contract gate required. |
| `obs_candidate_local_eval_ranking_gap_v0` | `approve_as_search_need_seed_future` | Ranking/source-coverage gap is useful for future SearchNeed triage. | Track B SearchNeed seed contract gate required. |

## What Approval Would Mean

- A later human decision may authorize a candidate to move to a future source-lead, WorkUnit seed, SearchNeed seed, or manual-observation review lane.
- A later human decision may also reject, defer, mark duplicate, mark policy-blocked, or request more evidence.

## What Approval Would Not Mean

- Approving a candidate does not make it observed baseline evidence.
- Approving a candidate does not make it accepted evidence truth.
- Approving a candidate does not mutate the master index.
- Approving a source lead does not approve live source access.
- Approving a WorkUnit or SearchNeed seed does not create those records in this task.

## Review Notes

- Policy-blocked items should remain blocked unless a separate future source policy packet changes their posture.
- Candidates needing more evidence should not be promoted until a reviewer records what evidence is missing and where it can be gathered safely.
