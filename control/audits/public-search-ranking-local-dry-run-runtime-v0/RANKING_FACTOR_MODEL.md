# Ranking Factor Model

Every factor is explicit and public-auditable. Factor fields are:

- `factor_type`
- `direction`: `positive`, `negative`, `neutral`, or `informational`
- `category_value`: `absent`, `weak`, `medium`, `strong`, `conflicting`, `unknown`, or `not_applicable`
- `public_reason`
- `audit_reason`
- `evidence_refs`
- `limitations`

Implemented factor categories:

- evidence_strength
- provenance_strength
- source_posture
- intrinsic_identifier_match
- compatibility_evidence
- platform_os_match
- architecture_match
- runtime_dependency_match
- representation_availability
- member_access
- freshness
- conflict_penalty
- uncertainty_penalty
- candidate_penalty
- rights_risk_caution
- action_safety
- absence_gap_transparency
- result_merge_group_quality
- identity_resolution_strength
- manual_review_status

Hidden scores are forbidden. Numeric opaque weights are not emitted. The dry-run order uses exposed categorical factors and current-rank tie-breaks only.

