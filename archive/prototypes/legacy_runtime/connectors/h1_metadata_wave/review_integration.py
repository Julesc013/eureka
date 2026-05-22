"""Offline H1 metadata-wave review integration helpers.

These helpers consume explicit fixture replay and live-probe output files. They
build review seeds and planning previews only; they do not call networks,
mutate runtime state, accept truth, or write indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h1_metadata_wave.normalizer_common import H1_SOURCE_IDS


FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_candidate_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_source_truth",
    "auto_approves_future_connectors",
    "automatic_future_connector_approval",
    "candidate_promotion_preview_promotes_candidate",
    "evidence_review_seed_accepts_evidence",
    "external_superiority_claimed",
    "h1_postmortem_enables_future_connectors_automatically",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutates_master_index",
    "mutates_public_index",
    "production_readiness_claimed",
    "public_index_mutated",
    "rights_clearance_claimed",
    "source_cache_review_seed_accepts_source",
    "source_pack_preview_is_imported_or_submitted",
    "verified_installability_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "api_calls_made",
    "changed_public_search_behavior",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_hosting",
    "enabled_model_provider_calls",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "evidence_ledger_runtime_mutated",
    "model_provider_calls_made",
    "mutated_master_index",
    "mutated_public_index",
    "network_used",
    "review_queue_runtime_mutated",
    "source_cache_runtime_mutated",
}


def load_h1_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    """Load explicit H1 output JSON files."""

    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h1_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a source-cache review seed from a normalized H1 record or preview."""

    record = _record_from_inputs(inputs)
    source_id = _source_id(record)
    native_id = str(record.get("source_native_id") or record.get("candidate_id") or "unknown")
    seed = {
        "schema_version": "h1_source_cache_review_seed.v0",
        "review_seed_id": f"h1.source_cache_review_seed.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "review_subject_type": "source_cache_candidate_preview",
        "review_subject_ref": record.get("source_cache_candidate_preview", {}).get("candidate_id") or record.get("candidate_id") or record.get("normalized_record_id"),
        "input_basis": _input_basis(record),
        "review_seed_status": "needs_review",
        "review_required": True,
        "source_cache_runtime_mutated": False,
        "accepted_source_truth": False,
        "blocked_reasons": _blocked_reasons(record),
        "limitations": _limitations(record) + ["Review seed is not source-cache persistence."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H1 source-cache review seed is a local review preview only."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h1_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build an evidence candidate review seed from a normalized H1 record or preview."""

    record = _record_from_inputs(inputs)
    source_id = _source_id(record)
    native_id = str(record.get("source_native_id") or record.get("evidence_preview_id") or "unknown")
    evidence_preview = record.get("evidence_candidate_preview") if isinstance(record.get("evidence_candidate_preview"), Mapping) else record
    seed = {
        "schema_version": "h1_evidence_candidate_review_seed.v0",
        "review_seed_id": f"h1.evidence_review_seed.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "review_subject_type": "evidence_candidate_preview",
        "review_subject_ref": evidence_preview.get("evidence_preview_id") or record.get("normalized_record_id"),
        "candidate_count": int(evidence_preview.get("candidate_count", 0)) if isinstance(evidence_preview, Mapping) else 0,
        "input_basis": _input_basis(record),
        "review_seed_status": "needs_review",
        "review_required": True,
        "evidence_ledger_runtime_mutated": False,
        "accepted_evidence": False,
        "blocked_reasons": _blocked_reasons(record),
        "limitations": _limitations(record) + ["Evidence seed is not evidence acceptance."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H1 evidence candidate review seed is a local review preview only."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h1_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a non-promotional candidate promotion preview."""

    source_seeds = _list(inputs.get("source_cache_review_seeds"))
    evidence_seeds = _list(inputs.get("evidence_candidate_review_seeds"))
    blocked_reasons = _blocked_reasons(inputs)
    preview = {
        "schema_version": "h1_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h1.candidate_promotion_preview.{_digest(inputs)[:12]}.v0",
        "wave_id": "H1",
        "preview_status": "not_ready_review_required",
        "source_cache_review_seed_count": len(source_seeds),
        "evidence_candidate_review_seed_count": len(evidence_seeds),
        "blocked_reasons": blocked_reasons,
        "review_required": True,
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "allowed_next_actions": ["human_review", "fixture_extraction_planning"],
        "forbidden_next_actions": ["accept_candidate", "mutate_public_index", "mutate_master_index"],
        "limitations": ["Promotion preview does not promote or accept a candidate."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H1 promotion preview is a rehearsal artifact only."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h1_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a bounded coverage update preview."""

    source_id = str(inputs.get("source_id") or "h1_metadata_wave")
    normalized_count = int(inputs.get("records_normalized", 1 if inputs.get("normalized_record_ref") else 0))
    preview = {
        "schema_version": "h1_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h1.coverage_update.{source_id}.{_digest(inputs)[:10]}.v0",
        "source_id": source_id,
        "coverage_basis": str(inputs.get("coverage_basis", "fixture_only")),
        "coverage_depth_current": str(inputs.get("coverage_depth_current", "D2_metadata_indexed" if normalized_count else "D0_source_known")),
        "records_seen": int(inputs.get("records_seen", normalized_count)),
        "records_normalized": normalized_count,
        "coverage_manifest_is_exhaustive_global_coverage": False,
        "review_required": True,
        "limitations": _limitations(inputs) + ["Coverage update preview is bounded and not exhaustive."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Coverage preview does not mutate coverage ledgers or indexes."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h1_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a connector scorecard update preview."""

    source_id = str(inputs.get("source_id") or "h1_metadata_wave")
    blocked = bool(_blocked_reasons(inputs))
    update = {
        "schema_version": "h1_connector_scorecard_update.v0",
        "connector_scorecard_update_id": f"h1.scorecard_update.{source_id}.{_digest(inputs)[:10]}.v0",
        "source_id": source_id,
        "scorecard_update_status": "blocked_live_probe_reviewed" if blocked else "fixture_review_integrated",
        "fixture_replay_status": "passed" if inputs.get("fixture_replay_used", True) else "not_used",
        "live_probe_status": str(inputs.get("live_probe_status", "blocked_or_not_used")),
        "review_integration_status": "preview_created",
        "quality_delta_status": "planned",
        "production_ready": False,
        "auto_approves_future_connectors": False,
        "metrics": {
            "fixture_replay_pass_count": int(inputs.get("fixture_replay_pass_count", 1 if inputs.get("fixture_replay_used", True) else 0)),
            "policy_block_count": len(_blocked_reasons(inputs)),
            "source_cache_candidate_count": int(inputs.get("source_cache_candidate_count", 1)),
            "evidence_candidate_count": int(inputs.get("evidence_candidate_count", 1)),
            "review_entry_count": int(inputs.get("review_entry_count", 2)),
            "warning_count": int(inputs.get("warning_count", 0)),
            "blocker_count": len(_blocked_reasons(inputs)),
        },
        "limitations": _limitations(inputs) + ["Scorecard update is not production readiness."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Scorecard update summarizes review previews only."],
    }
    _raise_if_boundaries_fail(update, policy)
    return update


def build_h1_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a source-pack update preview without import/submission/acceptance."""

    source_ids = sorted({str(item) for item in _list(inputs.get("sources")) if item})
    preview = {
        "schema_version": "h1_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h1.source_pack_update.{_digest(inputs)[:12]}.v0",
        "wave_id": "H1",
        "sources": source_ids,
        "pack_update_status": "draft_update_preview",
        "source_pack_imported": False,
        "source_pack_submitted": False,
        "source_pack_accepted": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "review_required": True,
        "limitations": ["Source pack update remains a preview and is not imported or submitted."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Source pack update preview is portable planning evidence only."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h1_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build the H1 wave review integration result from explicit outputs."""

    raw_outputs = [deepcopy(dict(item)) for item in _list(inputs.get("outputs")) if isinstance(item, Mapping)]
    records = [_record_from_inputs(item) for item in raw_outputs if _record_from_inputs(item)]
    sources = sorted({source for source in (_source_id(item) for item in records) if source != "unknown_source"})
    live_outputs = [item for item in raw_outputs if item.get("schema_version") == "h1_live_probe_result.v0"]
    fixture_outputs = [item for item in raw_outputs if item.get("schema_version") == "h1_metadata_fixture_replay_result.v0"]
    blocked_sources = sorted({
        str(item.get("source_id"))
        for item in live_outputs
        if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id")
    })

    source_seeds = [build_h1_source_cache_review_seed(record, policy) for record in records]
    evidence_seeds = [build_h1_evidence_candidate_review_seed(record, policy) for record in records]
    coverage_updates = [
        build_h1_coverage_update_preview(
            {
                "source_id": _source_id(record),
                "normalized_record_ref": record.get("normalized_record_id"),
                "records_seen": 1,
                "records_normalized": 1,
                "coverage_basis": "fixture_only",
                "limitations": _limitations(record),
            },
            policy,
        )
        for record in records
    ]
    scorecard_updates = [
        build_h1_connector_scorecard_update(
            {
                "source_id": _source_id(record),
                "fixture_replay_used": True,
                "live_probe_status": "blocked_or_not_used",
            },
            policy,
        )
        for record in records
    ]
    promotion = build_h1_candidate_promotion_preview(
        {
            "source_cache_review_seeds": source_seeds,
            "evidence_candidate_review_seeds": evidence_seeds,
            "blocked_reasons": _blocked_reasons(raw_outputs),
        },
        policy,
    )
    pack_preview = build_h1_source_pack_update_preview({"sources": sources}, policy)
    result = {
        "schema_version": "h1_review_integration_result.v0",
        "review_integration_result_id": f"h1.review_integration.{_digest(raw_outputs)[:12]}.v0",
        "wave_id": "H1",
        "sources": sources,
        "input_refs": _list(inputs.get("input_refs")),
        "used_fixture_outputs": [{"source_id": item.get("source_id"), "ref": item.get("replay_result_id")} for item in fixture_outputs],
        "used_live_probe_outputs": [{"source_id": item.get("source_id"), "ref": item.get("live_probe_result_id"), "status": item.get("result_status")} for item in live_outputs],
        "source_cache_review_seeds": source_seeds,
        "evidence_candidate_review_seeds": evidence_seeds,
        "candidate_promotion_previews": [promotion],
        "coverage_update_previews": coverage_updates,
        "scorecard_updates": scorecard_updates,
        "source_pack_update_previews": [pack_preview],
        "blocked_sources": blocked_sources,
        "warnings": list(inputs.get("warnings", [])),
        "limitations": [
            "Review integration uses explicit committed outputs only.",
            "Review seeds are not review decisions.",
            "Fixture-equivalent H1 outputs are sufficient for extraction sandbox planning, not public truth.",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H1 review integration does not mutate source cache, evidence ledger, review queue, public index, or master index."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h1_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    violations = detect_h1_review_truth_boundary_violations(result, None) + detect_h1_review_product_boundary_violations(result, None)
    return {
        "schema_version": "h1_review_integration_summary.v0",
        "status": "pass" if not violations else "invalid",
        "wave_id": result.get("wave_id", "H1"),
        "source_count": len(result.get("sources", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "candidate_promotion_preview_count": len(result.get("candidate_promotion_previews", [])),
        "coverage_update_preview_count": len(result.get("coverage_update_previews", [])),
        "scorecard_update_count": len(result.get("scorecard_updates", [])),
        "source_pack_update_preview_count": len(result.get("source_pack_update_previews", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_violations": violations,
    }


def detect_h1_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"{path}=true is forbidden for H1 review artifacts" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True]


def detect_h1_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"{path}=true is forbidden for H1 review product boundaries" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True]


def _record_from_inputs(inputs: Mapping[str, Any]) -> dict[str, Any]:
    if not inputs:
        return {}
    payload = deepcopy(dict(inputs))
    if payload.get("schema_version") == "h1_metadata_normalized_record.v0":
        return payload
    if isinstance(payload.get("normalized_record"), Mapping):
        return deepcopy(dict(payload["normalized_record"]))
    envelope = payload.get("connector_output_envelope")
    if isinstance(envelope, Mapping) and isinstance(envelope.get("normalized_record"), Mapping):
        return deepcopy(dict(envelope["normalized_record"]))
    if payload.get("schema_version") in {
        "h1_metadata_source_cache_candidate_preview.v0",
        "h1_metadata_evidence_candidate_preview.v0",
    }:
        return payload
    return {}


def _source_id(value: Mapping[str, Any]) -> str:
    return str(value.get("source_id") or "unknown_source")


def _input_basis(value: Mapping[str, Any]) -> str:
    schema = str(value.get("schema_version", ""))
    if schema == "h1_live_probe_result.v0":
        return "live_probe_output"
    if schema == "h1_metadata_normalized_record.v0":
        return "normalized_record"
    return "fixture_replay_output"


def _limitations(value: Any) -> list[str]:
    limitations: list[str] = []
    for _path, key, child in _iter_key_values(value):
        if key == "limitations" and isinstance(child, list):
            limitations.extend(str(item) for item in child if item)
    return sorted(dict.fromkeys(limitations))


def _blocked_reasons(value: Any) -> list[str]:
    reasons: list[str] = []
    for _path, key, child in _iter_key_values(value):
        if key in {"blocked_reasons", "blocked_sources"} and isinstance(child, list):
            reasons.extend(str(item) for item in child if item)
        elif key == "blocked_reason" and child:
            reasons.append(str(child))
    return sorted(dict.fromkeys(reasons))


def _truth_boundary() -> dict[str, bool]:
    return {
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "production_readiness_claimed": False,
        "external_superiority_claimed": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enables_hosting": False,
        "enables_source_sync": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_boundaries_fail(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    violations = detect_h1_review_truth_boundary_violations(payload, policy) + detect_h1_review_product_boundary_violations(payload, policy)
    if violations:
        raise ValueError("; ".join(violations))


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


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _slug(value: str) -> str:
    text = "".join(char.lower() if char.isalnum() else "_" for char in str(value))
    return "_".join(part for part in text.split("_") if part)[:80] or "unknown"


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def h1_source_ids() -> tuple[str, ...]:
    return tuple(H1_SOURCE_IDS)
