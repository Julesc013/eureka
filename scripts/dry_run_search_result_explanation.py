from __future__ import annotations

import argparse
import json
import sys

COMPONENT_TYPES = {
    "query_interpretation",
    "lexical_match",
    "phrase_match",
    "identifier_match",
    "alias_match",
    "source_match",
    "metadata_field_match",
    "compatibility_match",
    "representation_match",
    "member_match",
    "evidence_strength",
    "provenance_strength",
    "source_coverage",
    "ranking_reason",
    "grouping_reason",
    "identity_reason",
    "conflict_warning",
    "candidate_warning",
    "absence_explanation",
    "near_miss_explanation",
    "gap_explanation",
    "action_safety",
    "rights_risk_caution",
    "privacy_redaction_notice",
    "not_checked_notice",
    "unknown",
}
HARD_FALSE = [
    "runtime_explanation_implemented",
    "explanation_generated_by_runtime",
    "explanation_applied_to_live_search",
    "public_search_response_changed",
    "public_search_order_changed",
    "hidden_score_used",
    "hidden_suppression_performed",
    "result_suppressed",
    "model_call_performed",
    "AI_generated_answer",
    "candidate_promotion_performed",
    "ranking_applied_to_live_search",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_exported",
]


def component(component_id: str, component_type: str, text: str) -> dict:
    return {
        "schema_version": "0.1.0",
        "component_id": component_id,
        "component_kind": "search_result_explanation_component",
        "component_type": component_type,
        "status": "synthetic_example",
        "public_user_text": text,
        "audit_text": text + " This stdout-only dry run is not runtime generation.",
        "evidence_refs": ["dry-run-evidence-ref"],
        "source_refs": ["dry-run-source-ref"],
        "confidence": "medium",
        "uncertainty": "dry-run only",
        "limitations": ["No files written.", "No public search response changed."],
        "privacy": {"privacy_classification": "public_safe_example", "publishable": True},
        "no_truth_guarantees": ["Explanation is not truth."],
        "component_claimed_as_truth": False,
        "hidden_from_user": False,
        "private_data_included": False,
        "raw_payload_included": False,
    }


def build(title: str, match_kind: str) -> dict:
    data = {
        "schema_version": "0.1.0",
        "search_result_explanation_id": "dry-run-search-result-explanation-v0",
        "search_result_explanation_kind": "search_result_explanation",
        "status": "dry_run_validated",
        "created_by_tool": "dry_run_search_result_explanation.py",
        "explanation_scope": {"scope_kind": "synthetic_example", "search_mode": "fixture_example", "explanation_basis": "synthetic_example", "limitations": ["stdout only"]},
        "explained_result": {"result_ref": "dry-run-result", "result_title": title, "result_kind": "synthetic_example", "result_status": "fixture_backed", "result_lane": "demo", "limitations": ["not a runtime result"]},
        "query_interpretation": {"raw_query_included": False, "normalized_query_included": True, "normalized_query_public_safe": title, "interpreted_intent": "find_software", "extracted_hints": [title], "redacted_hints": [], "interpretation_confidence": "medium", "interpretation_not_truth": True, "limitations": ["raw query omitted"]},
        "match_and_recall": {"match_types": [match_kind], "matched_fields": ["title"], "unmatched_terms": [], "recall_scope": "fixture_only", "exact_identifier_match_present": False, "lexical_match_present": match_kind == "lexical_match", "semantic_match_present_future": False, "compatibility_match_present": match_kind == "compatibility_match", "member_match_present": match_kind == "member_match", "match_strength": "medium", "match_strength_not_truth": True, "limitations": ["dry-run only"]},
        "source_coverage": {"checked_sources": [{"source_id": "dry-run-source", "source_family": "fixture", "source_status": "synthetic_example", "checked_scope": "dry-run", "evidence_refs": ["dry-run-evidence-ref"], "limitations": ["not exhaustive"]}], "not_checked_sources": [{"source_family": "live_connectors", "reason_not_checked": "live_connector_disabled", "limitations": ["P96 disabled"]}], "source_coverage_status": "fixture_backed", "source_gap_types": ["live_sources_disabled"], "source_coverage_not_exhaustive": True, "limitations": ["not exhaustive"]},
        "evidence_and_provenance": {"evidence_summary": "Dry-run evidence ref only.", "provenance_summary": "Stdout-only dry run.", "evidence_refs": ["dry-run-evidence-ref"], "provenance_refs": ["dry-run-provenance-ref"], "evidence_strength": "weak", "provenance_strength": "weak", "evidence_not_truth": True, "provenance_not_truth": True, "accepted_as_truth": False, "limitations": ["not ledger evidence"]},
        "identity_grouping_deduplication": {"identity_relation_explained": "none", "grouping_relation_explained": "none", "deduplication_relation_explained": "none", "identity_assessment_refs": [], "result_merge_group_refs": [], "duplicate_or_variant_status": "not_grouped", "alternatives_preserved": True, "conflicts_hidden": False, "destructive_merge_performed": False, "limitations": ["future only"]},
        "ranking_relationship": {"ranking_explanation_available": False, "ranking_contract_refs": [], "ranking_factors_summarized": [], "ranking_applied_to_live_search": False, "public_search_order_changed": False, "hidden_score_used": False, "numeric_score_publication_policy": "no_numeric_score_v0", "ranking_not_truth": True, "limitations": ["no ranking"]},
        "compatibility": {"compatibility_explanation_available": False, "target_profile_ref": "dry-run-profile", "compatibility_status": "unknown", "compatibility_evidence_refs": [], "compatibility_evidence_strength": "unknown", "compatibility_not_truth": True, "installability_claimed": False, "dependency_safety_claimed": False, "limitations": ["unknown"]},
        "absence_near_miss_gaps": {"absence_status": "not_absent", "global_absence_claimed": False, "near_miss_refs": [], "gaps": [{"gap_type": "live_probe_disabled", "user_visible_explanation": "Live sources were not checked.", "future_next_step": "future approval", "limitations": ["dry-run only"]}], "checked_scope": "dry-run", "not_checked_scope": "live sources", "absence_not_truth": True, "limitations": ["no global absence"]},
        "action_safety": {"safe_actions": ["inspect_metadata", "view_sources", "view_evidence", "compare", "cite"], "disabled_actions": ["download", "install", "execute", "upload", "mirror", "arbitrary_url_fetch", "package_manager_invoke", "emulator_launch", "VM_launch"], "action_safety_status": "inspect_only", "downloads_enabled": False, "installs_enabled": False, "execution_enabled": False, "package_manager_invoked": False, "emulator_vm_launch_enabled": False, "limitations": ["unsafe actions disabled"]},
        "rights_risk": {"rights_classification": "public_metadata_only", "risk_classification": "metadata_only", "rights_clearance_claimed": False, "malware_safety_claimed": False, "dependency_safety_claimed": False, "installability_claimed": False, "risk_caution_required": True, "public_user_caution": "No rights or safety claim.", "limitations": ["caution"]},
        "user_facing_summary": {"summary_text": "Dry-run explanation only.", "why_this_result": "A public-safe title was provided to the dry-run helper.", "evidence_caveat": "Evidence is not truth.", "source_caveat": "Live sources were not checked.", "compatibility_caveat": "Compatibility unknown.", "action_caveat": "Inspect-only actions.", "gap_caveat": "Live checks disabled.", "plain_language_required": True, "no_marketing_claims": True, "no_unscoped_superiority_claims": True, "limitations": ["stdout-only"]},
        "detailed_components": [
            component("dry-run-query", "query_interpretation", "The title is treated as public-safe normalized text."),
            component("dry-run-match", match_kind, "The requested match component is represented without runtime scoring."),
            component("dry-run-source", "source_coverage", "Only synthetic dry-run scope is checked."),
            component("dry-run-evidence", "evidence_strength", "Evidence reference is synthetic."),
            component("dry-run-action", "action_safety", "Only inspect, compare, and cite actions are safe."),
            component("dry-run-risk", "rights_risk_caution", "No rights, safety, or installability claim is made."),
        ],
        "api_projection": {"response_kind": "search_result_explanation_response", "route_future": "/api/v1/result/{result_id}/explanation", "implemented_now": False, "compatible_with_public_search_response": True, "included_sections": ["summary"], "limitations": ["future only"]},
        "static_lite_text_projection": {"static_demo_available": False, "lite_text_available_future": True, "old_client_safe": True, "no_js_required": True, "concise_summary_available": True, "detailed_audit_view_available_future": True, "generated_static_artifact": False, "limitations": ["future only"]},
        "privacy": {"privacy_classification": "public_safe_example", "raw_query_included": False, "contains_private_path": False, "contains_secret": False, "contains_private_url": False, "contains_user_identifier": False, "contains_ip_address": False, "contains_raw_private_query": False, "contains_local_machine_fingerprint": False, "publishable": True, "public_aggregate_allowed": True, "reasons": ["stdout-only dry run"]},
        "limitations": ["dry-run only"],
        "no_truth_guarantees": ["not truth"],
        "no_runtime_guarantees": ["not runtime generation"],
        "no_mutation_guarantees": ["stdout only"],
        "notes": ["No files written."],
    }
    for key in HARD_FALSE:
        data[key] = False
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit a stdout-only hypothetical Search Result Explanation v0 record.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--match-kind", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.match_kind not in COMPONENT_TYPES:
        print(f"unsupported match kind: {args.match_kind}", file=sys.stderr)
        return 2
    payload = build(args.title, args.match_kind)
    print(json.dumps(payload, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
