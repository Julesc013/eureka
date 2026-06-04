# Scorecard Report

Task ID: `HARD-QUERY-EVAL-00`

## Scorecard File

Path:

```text
evals/hard_queries/usefulness_scorecard_v0.json
```

## Scale

```text
0 = fail, misleading, or missing
1 = weak but safe
2 = adequate for internal eval
3 = public-alpha useful
```

## Dimensions

```text
status_honesty
smallest_useful_unit
evidence_or_uncertainty_explanation
candidate_need_or_absence_quality
result_reason_quality
public_action_policy_compliance
renderer_profile_coverage
surface_consistency
no_truth_boundary_bypass
no_live_source_fanout
```

## Pass Gates

The current deterministic fixture suite must satisfy all scorecard pass gates. Focused tests verify the suite is stable and all fixture cases pass.
