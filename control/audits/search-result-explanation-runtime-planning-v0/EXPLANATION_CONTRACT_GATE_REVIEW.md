# Explanation Contract Gate Review

Status: present, contract-only.

Files:

- `contracts/search/search_result_explanation.v0.json`
- `contracts/search/search_result_explanation_component.v0.json`
- `contracts/search/search_result_explanation_policy.v0.json`
- `docs/reference/SEARCH_RESULT_EXPLANATION_CONTRACT.md`
- `control/audits/search-result-explanation-contract-v0/`
- `control/inventory/search/search_result_explanation_policy.json`

Examples:

- `examples/search_result_explanations/minimal_match_explanation_v0`
- `examples/search_result_explanations/minimal_source_evidence_explanation_v0`
- `examples/search_result_explanations/minimal_grouped_result_explanation_v0`
- `examples/search_result_explanations/minimal_compatibility_explanation_v0`
- `examples/search_result_explanations/minimal_absence_gap_explanation_v0`
- `examples/search_result_explanations/minimal_conflict_explanation_v0`
- `examples/search_result_explanations/minimal_action_safety_explanation_v0`

Validators:

- `python scripts/validate_search_result_explanation.py --all-examples`
- `python scripts/validate_search_result_explanation_contract.py`

Required components are present as schema concepts: query interpretation, match
reason, source coverage, evidence/provenance, grouping/identity, ranking
relationship, compatibility, absence/gaps, action safety, rights/risk, and
limitations.

Gaps:

- No runtime explanation generator exists.
- No explanation API/static integration exists.
- No public search response is allowed to include runtime explanations yet.

