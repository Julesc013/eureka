# Candidate Review Queue Preview

This preview is non-truth planning material. It does not approve candidates or complete observations.

| Candidate | Suggested review action | Boundary |
| --- | --- | --- |
| `obs_candidate_local_eval_failure_mining_batch_0_v0` | Review aggregate Batch 0 gap classes before downstream seeding. | Not observed evidence. |
| `obs_candidate_local_eval_source_gap_v0` | Decide whether to approve as a future source lead. | No source validation. |
| `obs_candidate_local_eval_extraction_gap_v0` | Decide whether to approve as a future WorkUnit seed. | No extraction runtime. |
| `obs_candidate_local_eval_ranking_gap_v0` | Decide whether to approve as a future SearchNeed seed. | No external rank evidence. |
| `obs_candidate_local_eval_policy_blocked_v0` | Keep blocked or route to source-policy review. | No autonomous source access. |

Human review remains required before any downstream use.
