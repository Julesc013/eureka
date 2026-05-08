# Local Eval Candidate Summary

OBS-AGENT-01 generated review-gated candidates from committed repo-local materials only.

## Inputs Inspected

- `control/audits/obs-replan-01-agent-assisted-observation-workflow-v0/obs_replan_01_report.json`
- `control/audits/obs0-02-manual-observation-batch-0-execution-packet-v0/obs0_02_report.json`
- `control/inventory/observations/manual_observation_batch_0_slot_manifest.json`
- `control/inventory/observations/manual_observation_failure_taxonomy.json`
- `control/inventory/observations/obs_agent_local_eval_failure_mining_policy.json`
- `control/inventory/observations/observation_source_access_modes.json`
- `docs/operations/AGENT_ASSISTED_OBSERVATION_WORKFLOW.md`
- `docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md`
- `docs/operations/OBSERVATION_SOURCE_ACCESS_POLICY.md`
- `evals/search_usefulness/external_baselines/batches/batch_0/batch_manifest.json`
- `evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json`
- `evals/search_usefulness/queries/search_usefulness_v0.json`
- `site/dist/data/eval_summary.json`
- `site/dist/demo/data/demo_snapshots.json`

## Candidate Records

| Candidate | Type | Status | Source mode | Failure modes |
| --- | --- | --- | --- | --- |
| `obs_candidate_local_eval_extraction_gap_v0` | `work_unit_seed` | `proposed` | `repo_local_only` | decomposition_gap, member_access_gap, extraction_gap, source_coverage_gap |
| `obs_candidate_local_eval_failure_mining_batch_0_v0` | `local_eval_failure` | `needs_human_review` | `repo_local_only` | source_coverage_gap, compatibility_evidence_gap, planner_gap, representation_gap, member_access_gap, ranking_gap |
| `obs_candidate_local_eval_policy_blocked_v0` | `policy_blocked_candidate` | `policy_blocked` | `no_autonomous_access` | rights_or_policy_block, external_baseline_unavailable |
| `obs_candidate_local_eval_ranking_gap_v0` | `search_need_seed` | `proposed` | `repo_local_only` | source_coverage_gap, member_access_gap, ranking_gap |
| `obs_candidate_local_eval_source_gap_v0` | `source_lead` | `proposed` | `repo_local_only` | source_coverage_gap, compatibility_evidence_gap, ranking_gap |

## Uncertain

- Ranking gaps are local audit labels, not externally observed ranks.
- Manual external baseline slots remain pending until a human records observations.
- Source leads and WorkUnit seeds remain future review targets.

## Human Review Required

- Reviewers may approve, reject, tune, deduplicate, or defer candidates.
- Review does not turn candidates into observed baselines or evidence truth.
- Track B should consume these records only after matching contracts and review gates exist.

## Future Seeds

- SearchNeed seed candidates: `obs_candidate_local_eval_ranking_gap_v0`.
- WorkUnit seed candidates: `obs_candidate_local_eval_extraction_gap_v0` and source-policy review for `obs_candidate_local_eval_policy_blocked_v0`.
- Source gap candidates may later become source leads after human review.

## Source Policy Blocks

- `obs_candidate_local_eval_policy_blocked_v0` remains blocked for autonomous agent access.
