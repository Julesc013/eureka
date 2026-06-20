# Status Authority Matrix

| Status | Typical Authority | Accepted Truth |
| --- | --- | --- |
| reviewed | reviewed_record | allowed only with review refs |
| candidate | candidate_only, run_projection, synthetic_test | no |
| near_miss | evidence_summary_only, run_projection, synthetic_test | no |
| need | evidence_summary_only, run_projection, synthetic_test | no |
| absence | absence_finding, run_projection, synthetic_test | no |
| policy_blocked | run_projection, synthetic_test | no |
| unavailable | source_observation_only, evidence_summary_only | no |
| unknown | run_projection, synthetic_test, unknown | no |
| mention_only | source_observation_only, evidence_summary_only | no |

Search may rank across statuses, but authority remains visible on every result.
