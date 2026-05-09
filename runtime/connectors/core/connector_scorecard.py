"""Connector scorecard helpers for Source OS.

Scorecards summarize local connector evidence. They do not run connectors,
call networks, approve live access, or accept connector output as truth.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


ALLOWED_STATUS = {
    "example_only",
    "fixture_only",
    "dry_run_only",
    "ready_for_policy_review",
    "ready_for_approved_live_probe_future",
    "blocked_by_policy",
    "blocked_by_missing_fixture",
    "blocked_by_missing_review",
    "warning",
    "not_evaluable",
}
ALLOWED_METRICS = {
    "fixture_replay_pass_count",
    "fixture_replay_fail_count",
    "policy_block_count",
    "source_cache_candidate_count",
    "evidence_candidate_count",
    "review_entry_count",
    "quality_delta_available",
    "postmortem_available",
    "warning_count",
    "blocker_count",
}
FORBIDDEN_TRUE_KEYS = {
    "accepted_candidate_truth",
    "accepted_evidence_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_source_truth",
    "automatic_future_connector_approval",
    "external_superiority",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutated_master_index",
    "mutated_public_index",
    "production_ready",
    "public_index_mutated",
    "rights_clearance_claimed",
    "scorecard_auto_approves_future_connectors",
    "scorecard_claims_production_readiness",
    "scorecard_is_public_truth",
    "verified_installability_claimed",
}


def build_connector_scorecard(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    connector_id = str(inputs.get("connector_id", "unknown_connector"))
    scorecard = {
        "schema_version": "connector_scorecard.v0",
        "connector_scorecard_id": str(inputs.get("connector_scorecard_id", f"scorecard.{connector_id}.v0")),
        "connector_id": connector_id,
        "source_id": str(inputs.get("source_id", "unknown_source")),
        "connector_family": str(inputs.get("connector_family", "unknown")),
        "source_family": str(inputs.get("source_family", "unknown")),
        "scorecard_status": str(inputs.get("scorecard_status", "dry_run_only")),
        "fixture_replay_status": str(inputs.get("fixture_replay_status", "not_evaluable")),
        "policy_evaluation_status": str(inputs.get("policy_evaluation_status", "not_evaluable")),
        "live_probe_envelope_status": str(inputs.get("live_probe_envelope_status", "blocked_by_policy")),
        "live_probe_result_status": str(inputs.get("live_probe_result_status", "not_run")),
        "source_cache_mapping_status": str(inputs.get("source_cache_mapping_status", "not_evaluable")),
        "evidence_mapping_status": str(inputs.get("evidence_mapping_status", "not_evaluable")),
        "review_integration_status": str(inputs.get("review_integration_status", "not_evaluable")),
        "quality_delta_status": str(inputs.get("quality_delta_status", "not_evaluable")),
        "postmortem_status": str(inputs.get("postmortem_status", "not_evaluable")),
        "coverage_ledger_status": str(inputs.get("coverage_ledger_status", "not_evaluable")),
        "pack_export_status": str(inputs.get("pack_export_status", "draft_only")),
        "warnings": list(inputs.get("warnings", [])),
        "blockers": list(inputs.get("blockers", [])),
        "metrics": dict(inputs.get("metrics", _default_metrics())),
        "next_recommended_action": str(inputs.get("next_recommended_action", "review_policy_gates")),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": list(inputs.get("notes", ["Scorecard is not production readiness."])),
    }
    validate_connector_scorecard(scorecard, policy)
    return scorecard


def validate_connector_scorecard(scorecard: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    if scorecard.get("schema_version") != "connector_scorecard.v0":
        raise ValueError("connector scorecard schema_version must be connector_scorecard.v0")
    if scorecard.get("scorecard_status") not in ALLOWED_STATUS:
        raise ValueError(f"unknown scorecard_status: {scorecard.get('scorecard_status')}")
    metrics = scorecard.get("metrics", {})
    if isinstance(metrics, Mapping):
        forbidden_metrics = sorted(set(metrics) - ALLOWED_METRICS)
        if forbidden_metrics:
            raise ValueError(f"forbidden scorecard metrics: {', '.join(forbidden_metrics)}")
    violations = detect_scorecard_truth_boundary_violations(scorecard, policy)
    if violations:
        raise ValueError("; ".join(violations))


def summarize_connector_scorecard(scorecard: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    violations = detect_scorecard_truth_boundary_violations(scorecard, policy)
    metrics = scorecard.get("metrics", {})
    return {
        "schema_version": "connector_scorecard_summary.v0",
        "status": "pass" if not violations else "invalid",
        "connector_id": scorecard.get("connector_id"),
        "source_id": scorecard.get("source_id"),
        "scorecard_status": scorecard.get("scorecard_status"),
        "fixture_replay_status": scorecard.get("fixture_replay_status"),
        "policy_evaluation_status": scorecard.get("policy_evaluation_status"),
        "live_probe_envelope_status": scorecard.get("live_probe_envelope_status"),
        "warning_count": int(metrics.get("warning_count", len(scorecard.get("warnings", [])))) if isinstance(metrics, Mapping) else 0,
        "blocker_count": int(metrics.get("blocker_count", len(scorecard.get("blockers", [])))) if isinstance(metrics, Mapping) else 0,
        "truth_boundary_violations": violations,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }


def build_connector_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    connector_id = str(inputs.get("connector_id", "unknown_connector"))
    delta = {
        "schema_version": "connector_quality_delta.v0",
        "quality_delta_id": str(inputs.get("quality_delta_id", f"quality_delta.{connector_id}.v0")),
        "connector_id": connector_id,
        "source_id": str(inputs.get("source_id", "unknown_source")),
        "comparison_scope": str(inputs.get("comparison_scope", "fixture_only")),
        "before_state": dict(inputs.get("before_state", {})),
        "after_state": dict(inputs.get("after_state", {})),
        "metrics": dict(inputs.get("metrics", {})),
        "limitations": list(inputs.get("limitations", ["quality delta is not production search quality"])),
        "blocked_claims": ["beats_google", "beats_internet_archive", "exhaustive_global_coverage", "production_search_quality", "rights_clearance", "malware_safety", "verified_installability"],
        "review_gates": {"human_review_required_for_public_claims": True},
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": list(inputs.get("notes", [])),
    }
    violations = detect_scorecard_truth_boundary_violations(delta, policy)
    if violations:
        raise ValueError("; ".join(violations))
    return delta


def detect_scorecard_truth_boundary_violations(scorecard: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [
        f"{path}=true is forbidden for scorecard artifacts"
        for path, key, value in _iter_key_values(scorecard)
        if key in FORBIDDEN_TRUE_KEYS and value is True
    ]


def _default_metrics() -> dict[str, int | bool]:
    return {
        "fixture_replay_pass_count": 0,
        "fixture_replay_fail_count": 0,
        "policy_block_count": 0,
        "source_cache_candidate_count": 0,
        "evidence_candidate_count": 0,
        "review_entry_count": 0,
        "quality_delta_available": False,
        "postmortem_available": False,
        "warning_count": 0,
        "blocker_count": 0,
    }


def _truth_boundary() -> dict[str, bool]:
    return {
        "scorecard_is_public_truth": False,
        "scorecard_claims_production_readiness": False,
        "scorecard_auto_approves_future_connectors": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_source_connectors": False,
        "enabled_downloads": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, child
            yield from _iter_key_values(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_key_values(child, f"{prefix}[{index}]")
