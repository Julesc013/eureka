"""Dry-run review integration for Internet Archive metadata outputs.

This module consumes explicit IA-BUNDLE-02 artifacts. It performs no live calls,
does not mutate runtime state, and never accepts source, evidence, candidate,
pack, public-index, or master-index truth.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.local.foundry import pack_builder, review_queue


SOURCE_ID = "internet_archive"
CONNECTOR_ID = "internet_archive_metadata_connector"

FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_source_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "ia_review_output_is_public_truth",
    "ia_review_output_is_truth",
    "ia_source_cache_review_entry_accepts_source",
    "ia_evidence_review_entry_accepts_evidence",
    "ia_candidate_promotion_dry_run_accepts_candidate",
    "ia_pack_draft_is_accepted_pack",
    "ia_quality_delta_is_production_claim",
    "ia_postmortem_enables_future_connectors_automatically",
    "ia_review_can_mutate_public_index",
    "ia_review_can_mutate_master_index",
    "ia_review_can_claim_rights_clearance",
    "ia_review_can_claim_malware_safety",
    "ia_review_can_claim_verified_installability",
    "public_index_mutated",
    "master_index_mutated",
    "mutated_public_index",
    "mutated_master_index",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "pack_imported",
    "pack_submitted",
    "pack_accepted",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "changed_public_search_behavior",
    "enabled_hosting",
    "enabled_live_public_fanout",
    "enabled_source_sync",
    "enabled_downloads",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "mutated_public_index",
    "mutated_master_index",
    "source_cache_runtime_mutated",
    "evidence_ledger_runtime_mutated",
    "review_queue_runtime_mutated",
    "network_used",
    "api_calls_made",
    "model_provider_calls_made",
}


def load_ia_probe_outputs(paths: Mapping[str, str | Path]) -> dict[str, Any]:
    """Load explicit IA-BUNDLE-02 output JSON files."""

    outputs: dict[str, Any] = {}
    for key, path_text in paths.items():
        if not path_text:
            continue
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs[str(key)] = dict(payload)
    return outputs


def build_ia_source_cache_review_entry(source_cache_candidate: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a review entry for an IA source-cache candidate preview."""

    candidate = deepcopy(dict(source_cache_candidate))
    status = _blocked_status(candidate)
    local_entry = review_queue.build_review_queue_entry(
        {
            "input_id": candidate.get("candidate_id") or candidate.get("live_probe_result_ref") or "ia_source_cache_candidate",
            "input_type": "committed_review_fixture",
            "review_subject_type": "policy_blocked_subject" if status == "policy_blocked" else "source_cache_record",
            "review_subject_ref": str(candidate.get("candidate_id") or candidate.get("live_probe_result_ref") or "ia_source_cache_candidate"),
            "review_subject_summary": "IA source-cache candidate review entry from metadata probe output.",
            "review_entry_status": status,
            "review_decision": "policy_block" if status == "policy_blocked" else "no_decision_yet",
            "decision_rationale": _decision_rationale(candidate),
            "required_evidence": ["operator_source_policy", "metadata_probe_output", "human_review"],
            "missing_evidence": _blocked_reasons(candidate),
            "policy_summary": "IA metadata remains a source observation and requires review before persistence.",
            "limitations": _limitations(candidate),
            "notes": ["No source cache runtime write occurred."],
        }
    )
    entry = {
        "schema_version": "internet_archive_source_cache_review_entry.v0",
        "review_integration_id": f"ia_source_cache_review.{_digest(candidate)[:12]}.v0",
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "review_integration_status": "blocked_dry_run" if status == "policy_blocked" else "needs_review",
        "input_status": str(candidate.get("status") or candidate.get("mapping_status") or "unknown"),
        "source_cache_candidate_ref": candidate.get("candidate_id") or candidate.get("live_probe_result_ref"),
        "local_review_queue_entry": local_entry,
        "review_required": True,
        "blocked_reasons": _blocked_reasons(candidate),
        "source_cache_runtime_mutated": False,
        "accepted_source_truth": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": _limitations(candidate),
        "notes": [
            "Review entry is a local rehearsal only.",
            "Source cache candidate is not persisted or accepted by IA-BUNDLE-03.",
        ],
    }
    _raise_if_boundaries_fail(entry)
    return entry


def build_ia_evidence_candidate_review_entry(evidence_candidate: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a review entry for an IA evidence candidate preview."""

    evidence = deepcopy(dict(evidence_candidate))
    status = _blocked_status(evidence)
    local_entry = review_queue.build_review_queue_entry(
        {
            "input_id": evidence.get("evidence_preview_id") or evidence.get("live_probe_result_ref") or "ia_evidence_candidate",
            "input_type": "committed_review_fixture",
            "review_subject_type": "policy_blocked_subject" if status == "policy_blocked" else "evidence_candidate",
            "review_subject_ref": str(evidence.get("evidence_preview_id") or evidence.get("live_probe_result_ref") or "ia_evidence_candidate"),
            "review_subject_summary": "IA evidence candidate review entry from metadata probe output.",
            "review_entry_status": status,
            "review_decision": "policy_block" if status == "policy_blocked" else "no_decision_yet",
            "decision_rationale": _decision_rationale(evidence),
            "required_evidence": ["source_cache_context", "metadata_probe_output", "human_review"],
            "missing_evidence": _blocked_reasons(evidence),
            "policy_summary": "IA metadata may preview evidence candidates but cannot accept evidence.",
            "limitations": _limitations(evidence),
            "notes": ["No evidence ledger runtime write occurred."],
        }
    )
    entry = {
        "schema_version": "internet_archive_evidence_candidate_review_entry.v0",
        "review_integration_id": f"ia_evidence_review.{_digest(evidence)[:12]}.v0",
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "review_integration_status": "blocked_dry_run" if status == "policy_blocked" else "needs_review",
        "input_status": str(evidence.get("status") or "unknown"),
        "evidence_candidate_ref": evidence.get("evidence_preview_id") or evidence.get("live_probe_result_ref"),
        "local_review_queue_entry": local_entry,
        "review_required": True,
        "blocked_reasons": _blocked_reasons(evidence),
        "evidence_ledger_runtime_mutated": False,
        "accepted_evidence": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": _limitations(evidence),
        "notes": [
            "Evidence review entry is a local rehearsal only.",
            "Evidence candidate preview is not accepted by IA-BUNDLE-03.",
        ],
    }
    _raise_if_boundaries_fail(entry)
    return entry


def build_ia_candidate_promotion_dry_run(candidate_or_evidence_inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build an IA-specific promotion dry-run summary without promoting."""

    inputs = deepcopy(dict(candidate_or_evidence_inputs))
    source_review = inputs.get("source_cache_review_entry", {})
    evidence_review = inputs.get("evidence_review_entry", {})
    blocked_reasons = _blocked_reasons(source_review) + _blocked_reasons(evidence_review)
    blocked = bool(blocked_reasons) or _is_policy_blocked(source_review) or _is_policy_blocked(evidence_review)
    record = {
        "schema_version": "internet_archive_candidate_promotion_dry_run.v0",
        "promotion_dry_run_id": f"ia_candidate_promotion_dry_run.{_digest(inputs)[:12]}.v0",
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "promotion_dry_run_status": "policy_blocked" if blocked else "needs_review",
        "promotion_readiness": "not_ready_policy_blocked" if blocked else "not_ready_missing_review",
        "source_cache_review_entry_ref": _entry_ref(source_review),
        "evidence_review_entry_ref": _entry_ref(evidence_review),
        "candidate_ref": "ia_metadata_review_candidate_preview",
        "candidate_summary": "IA metadata review candidate dry-run only.",
        "blockers": _blockers(blocked_reasons),
        "blocked_reasons": sorted(dict.fromkeys(blocked_reasons)),
        "review_required": True,
        "candidate_promotion_dry_run_accepts_candidate": False,
        "accepted_candidate_truth": False,
        "accepted_evidence_truth": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "allowed_next_actions": ["request_operator_policy_decision", "request_h0_source_os_review"],
        "forbidden_next_actions": [
            "accept_candidate",
            "accept_evidence",
            "mutate_public_index",
            "mutate_master_index",
            "claim_rights_clearance",
            "claim_malware_safety",
            "claim_verified_installability",
        ],
        "limitations": [
            "Promotion dry-run does not promote or accept a candidate.",
            "Blocked IA-BUNDLE-02 outputs cannot support downstream promotion readiness.",
        ],
    }
    _raise_if_boundaries_fail(record)
    return record


def build_ia_pack_draft_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a pack draft preview around IA review outputs."""

    source_entry = deepcopy(dict(inputs.get("source_cache_review_entry") or {}))
    evidence_entry = deepcopy(dict(inputs.get("evidence_review_entry") or {}))
    promotion = deepcopy(dict(inputs.get("candidate_promotion_dry_run") or {}))
    records = [item for item in (source_entry, evidence_entry, promotion) if item]
    local_pack = pack_builder.build_pack_draft(records, "review_pack_draft")
    local_pack["pack_status"] = "policy_blocked" if any(_is_policy_blocked(item) for item in records) else local_pack["pack_status"]
    preview = {
        "schema_version": "internet_archive_pack_draft_preview.v0",
        "pack_preview_id": f"ia_pack_draft_preview.{_digest(records)[:12]}.v0",
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "pack_preview_status": local_pack["pack_status"],
        "local_pack_draft": local_pack,
        "pack_imported": False,
        "pack_submitted": False,
        "pack_accepted": False,
        "blocked_reasons": _blocked_reasons({"records": records}),
        "public_index_mutated": False,
        "master_index_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": [
            "Pack draft preview is not imported, submitted, accepted, or published.",
            "Blocked source inputs keep the preview review-gated.",
        ],
    }
    _raise_if_boundaries_fail(preview)
    return preview


def build_ia_review_integration_summary(outputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Summarize IA review integration outputs."""

    payload = deepcopy(dict(outputs))
    blocked_reasons = _blocked_reasons(payload)
    source_entry = payload.get("source_cache_review_entry", {})
    evidence_entry = payload.get("evidence_review_entry", {})
    promotion = payload.get("candidate_promotion_dry_run", {})
    pack = payload.get("pack_draft_preview", {})
    summary = {
        "schema_version": "internet_archive_review_integration_summary.v0",
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "integration_status": "blocked_dry_run" if blocked_reasons or any(_is_policy_blocked(item) for item in (source_entry, evidence_entry, promotion, pack)) else "needs_review",
        "source_cache_review_entry_created": bool(source_entry),
        "evidence_candidate_review_entry_created": bool(evidence_entry),
        "candidate_promotion_dry_run_created": bool(promotion),
        "pack_draft_preview_created": bool(pack),
        "blocked_reason_count": len(blocked_reasons),
        "blocked_reasons": blocked_reasons,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Summary is audit material for IA-BUNDLE-03.",
            "It does not promote or publish records.",
        ],
    }
    _raise_if_boundaries_fail(summary)
    return summary


def detect_ia_review_truth_boundary_violations(outputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(outputs) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True]


def detect_ia_review_product_boundary_violations(outputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(outputs) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True]


def _truth_boundary() -> dict[str, bool]:
    return {
        "ia_review_output_is_public_truth": False,
        "ia_source_cache_review_entry_accepts_source": False,
        "ia_evidence_review_entry_accepts_evidence": False,
        "ia_candidate_promotion_dry_run_accepts_candidate": False,
        "ia_pack_draft_is_accepted_pack": False,
        "ia_quality_delta_is_production_claim": False,
        "ia_postmortem_enables_future_connectors_automatically": False,
        "ia_review_can_mutate_public_index": False,
        "ia_review_can_mutate_master_index": False,
        "ia_review_can_claim_rights_clearance": False,
        "ia_review_can_claim_malware_safety": False,
        "ia_review_can_claim_verified_installability": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "human_review_required_before_downstream_use": True,
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
        "source_cache_runtime_mutated": False,
        "evidence_ledger_runtime_mutated": False,
        "review_queue_runtime_mutated": False,
        "network_used": False,
        "api_calls_made": False,
        "model_provider_calls_made": False,
    }


def _blocked_status(payload: Mapping[str, Any]) -> str:
    if _is_policy_blocked(payload):
        return "policy_blocked"
    return "needs_review"


def _is_policy_blocked(payload: Mapping[str, Any]) -> bool:
    text = json.dumps(payload, sort_keys=True, default=str).lower()
    return "blocked" in text or str(payload.get("review_integration_status", "")).startswith("blocked")


def _decision_rationale(payload: Mapping[str, Any]) -> str:
    if _is_policy_blocked(payload):
        return "IA-BUNDLE-02 output is blocked by committed policy, so review records preserve the block."
    return "Human review is required before any downstream source or evidence use."


def _limitations(payload: Mapping[str, Any]) -> list[str]:
    limitations = [str(item) for item in payload.get("limitations", []) if item] if isinstance(payload.get("limitations"), list) else []
    base = [
        "IA review integration is a dry-run and does not accept source or evidence truth.",
        "No public index or master index mutation is allowed.",
    ]
    if _is_policy_blocked(payload):
        base.append("Input is blocked or fixture-equivalent because IA live probe approval is missing.")
    return sorted(dict.fromkeys(limitations + base))


def _blocked_reasons(payload: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    for _path, key, value in _iter_key_values(payload):
        if key == "blocked_reasons" and isinstance(value, list):
            reasons.extend(str(item) for item in value if item)
    return sorted(dict.fromkeys(reasons))


def _blockers(reasons: Sequence[str]) -> list[dict[str, Any]]:
    if not reasons:
        return []
    return [
        {
            "blocker_id": f"ia_review_blocker.{index + 1}.v0",
            "blocker_category": "policy_block",
            "blocker_summary": str(reason),
            "automatic_resolution_allowed": False,
            "automatic_merge_allowed": False,
            "automatic_delete_allowed": False,
        }
        for index, reason in enumerate(sorted(dict.fromkeys(reasons)))
    ]


def _entry_ref(payload: Mapping[str, Any]) -> str:
    return str(payload.get("review_integration_id") or payload.get("review_entry_id") or payload.get("schema_version") or "")


def _raise_if_boundaries_fail(payload: Mapping[str, Any]) -> None:
    errors = detect_ia_review_truth_boundary_violations(payload) + detect_ia_review_product_boundary_violations(payload)
    if errors:
        raise ValueError("; ".join(errors))


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
