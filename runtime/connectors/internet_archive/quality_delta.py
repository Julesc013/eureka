"""Quality delta and postmortem helpers for IA review integration."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Mapping


SOURCE_ID = "internet_archive"
CONNECTOR_ID = "internet_archive_metadata_connector"

FORBIDDEN_TRUE_KEYS = {
    "beats_google",
    "beats_internet_archive",
    "claims_external_superiority",
    "claims_production_readiness",
    "exhaustive_global_coverage",
    "ia_quality_delta_is_production_claim",
    "ia_postmortem_enables_future_connectors_automatically",
    "rights_clearance",
    "rights_clearance_claimed",
    "malware_safety",
    "malware_safety_claimed",
    "verified_installability",
    "verified_installability_claimed",
    "public_index_mutated",
    "master_index_mutated",
    "auto_approves_future_connectors",
}


def build_ia_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build local-only IA quality delta metrics from review outputs."""

    payload = deepcopy(dict(inputs))
    blocked_reasons = _collect_blocked_reasons(payload)
    has_source_entry = bool(payload.get("source_cache_review_entry"))
    has_evidence_entry = bool(payload.get("evidence_review_entry"))
    has_promotion = bool(payload.get("candidate_promotion_dry_run"))
    has_pack = bool(payload.get("pack_draft_preview"))
    delta = {
        "schema_version": "internet_archive_quality_delta_report.v0",
        "quality_delta_id": f"ia_quality_delta.{_digest(payload)[:12]}.v0",
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "delta_status": "blocked_dry_run" if blocked_reasons else "fixture_only_review_delta",
        "metric_scope": "local_fixture_or_blocked_probe_only",
        "metrics": {
            "candidate_count_delta": 1 if has_promotion else 0,
            "source_cache_record_count_delta": 1 if has_source_entry else 0,
            "evidence_candidate_count_delta": 1 if has_evidence_entry else 0,
            "review_entry_count_delta": int(has_source_entry) + int(has_evidence_entry),
            "result_presence_delta_fixture_only": "blocked_probe_output_present" if blocked_reasons else "fixture_review_output_present",
            "near_match_delta_fixture_only": 0,
            "known_gap_delta": len(_known_gaps(blocked_reasons)),
            "blocked_reason_count": len(blocked_reasons),
            "connector_error_count": 0,
            "pack_draft_preview_count": 1 if has_pack else 0,
        },
        "blocked_reasons": blocked_reasons,
        "known_gaps": _known_gaps(blocked_reasons),
        "limitations": [
            "Quality delta is local audit evidence only.",
            "Blocked IA live approval means no completed live metadata response was measured.",
            "No external superiority or production search quality claim is made.",
        ],
        "claims_external_superiority": False,
        "claims_production_readiness": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    errors = detect_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_ia_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    metrics = delta.get("metrics", {})
    return {
        "schema_version": "internet_archive_quality_delta_summary.v0",
        "quality_delta_id": delta.get("quality_delta_id"),
        "delta_status": delta.get("delta_status"),
        "candidate_count_delta": metrics.get("candidate_count_delta", 0),
        "source_cache_record_count_delta": metrics.get("source_cache_record_count_delta", 0),
        "evidence_candidate_count_delta": metrics.get("evidence_candidate_count_delta", 0),
        "review_entry_count_delta": metrics.get("review_entry_count_delta", 0),
        "blocked_reason_count": metrics.get("blocked_reason_count", 0),
        "claims_external_superiority": False,
        "claims_production_readiness": False,
        "limitations": list(delta.get("limitations", [])),
    }


def build_ia_connector_postmortem(delta: Mapping[str, Any], integration_outputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a structured IA connector postmortem."""

    blocked_reasons = _collect_blocked_reasons(integration_outputs) or list(delta.get("blocked_reasons", []))
    postmortem = {
        "schema_version": "internet_archive_connector_postmortem.v0",
        "postmortem_id": f"ia_connector_postmortem.{_digest({'delta': delta, 'outputs': integration_outputs})[:12]}.v0",
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "postmortem_status": "blocked_dry_run_complete" if blocked_reasons else "fixture_review_complete",
        "what_worked": [
            "Fixture-only normalizer output can enter source-cache and evidence review previews.",
            "Blocked IA-BUNDLE-02 artifacts can preserve policy gate failures without live evidence.",
            "Review, promotion dry-run, pack preview, and quality-delta artifacts remain non-promotional.",
        ],
        "what_failed": [
            "The live metadata probe did not run because operator approval is still missing."
        ] if blocked_reasons else [],
        "policy_gaps": blocked_reasons,
        "data_shape_gaps": [
            "Completed live metadata response shape still needs one approved IA-BUNDLE-02 run.",
            "Coverage ledger and connector scorecard fields should be formalized in H0."
        ],
        "source_cache_mapping_gaps": [
            "Blocked output creates no persisted source-cache record.",
            "H0 should define canonical candidate identity and coverage-depth fields."
        ],
        "evidence_mapping_gaps": [
            "Evidence previews remain unaccepted and require review policy before downstream use."
        ],
        "review_gaps": [
            "No human review decision was made in IA-BUNDLE-03.",
            "Review queue persistence remains a future reviewed step."
        ],
        "quality_delta_summary": summarize_ia_quality_delta(delta, policy),
        "safety_boundary_assessment": {
            "new_live_call_made": False,
            "downloads_made": False,
            "source_sync_enabled": False,
            "accepted_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "boundary_result": "preserved",
        },
        "H0_implications": [
            "Promote IA connector decisions into a source-family registry pattern.",
            "Add coverage ledger and connector scorecard concepts before widening H1 sources.",
            "Keep live-probe envelopes fail-closed and identifier-scoped."
        ],
        "H1_reuse_recommendations": [
            "Reuse source policy, endpoint posture, fixture replay, review output policy, and quality delta templates.",
            "Require each source family to classify allowed metadata endpoints and forbidden acquisition actions."
        ],
        "next_connector_recommendation": "Proceed to H0 Source OS foundation before broad H1 connector expansion.",
        "do_not_repeat_risks": [
            "Do not treat source metadata as accepted truth.",
            "Do not widen from one approved identifier to broad search without a new gate.",
            "Do not add downloads, item fetches, or scraping under metadata connector language."
        ],
        "recommends_h0": True,
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    errors = detect_quality_overclaim(postmortem, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return postmortem


def detect_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]


def build_h0_readiness_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    recommendation = {
        "schema_version": "internet_archive_h0_readiness_recommendation.v0",
        "recommendation_id": f"ia_h0_readiness.{_digest(postmortem)[:12]}.v0",
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "recommendation": "proceed_to_h0_source_os_foundation",
        "recommended_next_task": "H0-BUNDLE-01 - Source OS registry and policy foundation",
        "rationale": [
            "IA fixture and blocked live-probe paths now cover the first connector pattern through review rehearsal.",
            "H0 should formalize source family registry, capability ladder, policy gates, replay harness, live envelope, coverage ledger, and scorecards before more source families are added."
        ],
        "auto_approves_future_connectors": False,
        "operator_approval_still_required_for_live_ia_probe": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    errors = detect_quality_overclaim(recommendation, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return recommendation


def _truth_boundary() -> dict[str, bool]:
    return {
        "ia_review_output_is_public_truth": False,
        "ia_source_cache_review_entry_accepts_source": False,
        "ia_evidence_review_entry_accepts_evidence": False,
        "ia_candidate_promotion_dry_run_accepts_candidate": False,
        "ia_pack_draft_is_accepted_pack": False,
        "ia_quality_delta_is_production_claim": False,
        "ia_postmortem_enables_future_connectors_automatically": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_live_public_fanout": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _collect_blocked_reasons(value: Any) -> list[str]:
    reasons: list[str] = []
    for _path, key, child in _iter_key_values(value):
        if key == "blocked_reasons" and isinstance(child, list):
            reasons.extend(str(item) for item in child if item)
    return sorted(dict.fromkeys(reasons))


def _known_gaps(blocked_reasons: list[str]) -> list[str]:
    gaps = []
    if blocked_reasons:
        gaps.append("ia_live_probe_operator_approval_missing")
    if any("contact" in reason.lower() for reason in blocked_reasons):
        gaps.append("user_agent_contact_policy_pending")
    if any("cache" in reason.lower() for reason in blocked_reasons):
        gaps.append("cache_policy_pending")
    if any("identifier" in reason.lower() for reason in blocked_reasons):
        gaps.append("approved_identifier_policy_pending")
    return sorted(dict.fromkeys(gaps))


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, nested
            yield from _iter_key_values(nested, path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            yield from _iter_key_values(nested, f"{prefix}[{index}]")


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
