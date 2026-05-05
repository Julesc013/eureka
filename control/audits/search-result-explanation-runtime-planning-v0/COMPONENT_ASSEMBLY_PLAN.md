# Component Assembly Plan

Required future components:

- `query_interpretation`: result envelope query intent summary; fallback is
  redacted or omitted interpretation.
- `match_and_recall`: public matched fields and terms; fallback is "match detail
  not available".
- `source_coverage`: checked/not-checked source scope; fallback is scoped
  coverage unknown.
- `evidence_and_provenance`: public evidence refs and caveats; fallback is no
  evidence ref available.
- `identity_grouping_deduplication`: grouping and identity relation if present;
  fallback is no grouping explanation.
- `ranking_relationship`: public ranking factors only; fallback hides scores and
  says ranking explanation not available.
- `compatibility`: platform/dependency caveats; fallback is compatibility
  unknown.
- `absence_near_miss_gaps`: scoped gaps and near misses; fallback is not checked.
- `action_safety`: allowed/disabled actions; fallback keeps risky actions
  disabled.
- `rights_risk`: rights, malware, installability cautions; fallback is caution.
- `limitations`: known uncertainty, conflicts, and provenance limits; fallback
  is generic public-safe limitation.

Each component needs public-safe input fields, user-facing copy, audit copy,
privacy constraints, and explicit unknown/gap handling.

