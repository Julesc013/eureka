"""Offline H2 package-registry review integration helpers.

These helpers consume explicit H2 fixture replay outputs and blocked or
approved metadata-only live-probe outputs. They create review seeds and
planning previews only; they do not call networks, invoke package managers,
accept truth, or write runtime state or indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from control.prototypes.legacy_runtime.connectors.h2_package_registries.normalizer_common import H2_SOURCE_IDS


FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_candidate_truth",
    "accepted_dependency_correctness",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_package_identity_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_source_truth",
    "accepts_candidate_truth",
    "accepts_dependency_correctness",
    "accepts_evidence_truth",
    "accepts_package_identity_truth",
    "accepts_public_truth",
    "accepts_source_truth",
    "automatic_future_connector_approval",
    "candidate_promotion_preview_promotes_candidate",
    "dependency_candidate_is_correctness_proof",
    "dependency_correctness_accepted",
    "dependency_correctness_claimed",
    "dependency_seed_accepts_correctness",
    "evidence_review_seed_accepts_evidence",
    "file_hash_candidate_is_malware_safety",
    "license_metadata_is_rights_clearance",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutates_master_index",
    "mutates_public_index",
    "package_file_seed_grants_download_or_safety",
    "package_identity_candidate_is_truth",
    "package_identity_seed_accepts_identity",
    "production_readiness_claimed",
    "public_index_mutated",
    "purl_candidate_is_truth",
    "rights_clearance_claimed",
    "source_cache_review_seed_accepts_source",
    "source_pack_preview_is_imported_or_submitted",
    "verified_installability_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "api_calls_made",
    "changed_public_search_behavior",
    "downloads_made",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_execution",
    "enabled_hosting",
    "enabled_installers",
    "enabled_model_provider_calls",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "enables_install_execute",
    "enables_package_downloads",
    "evidence_ledger_runtime_mutated",
    "install_execute_enabled",
    "model_provider_calls_made",
    "mutated_master_index",
    "mutated_public_index",
    "network_calls_made",
    "network_used",
    "package_download_enabled",
    "package_manager_invoked",
    "package_manager_invocation_enabled",
    "review_queue_runtime_mutated",
    "source_cache_runtime_mutated",
    "source_sync_enabled",
}


def load_h2_package_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    """Load explicit H2 output JSON files."""

    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h2_package_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    identity = _identity_from_inputs(inputs, record)
    source_id = _source_id(identity or record)
    native_id = str((identity or record).get("source_native_id") or (identity or record).get("identity_candidate_id") or "unknown")
    seed = {
        "schema_version": "h2_package_identity_review_seed.v0",
        "review_seed_id": f"h2.identity_review_seed.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "review_subject_type": "package_identity_candidate",
        "review_subject_ref": identity.get("identity_candidate_id") or record.get("package_identity_candidate", {}).get("identity_candidate_id"),
        "package_name": identity.get("package_name") or record.get("package_name"),
        "ecosystem": identity.get("ecosystem") or record.get("ecosystem"),
        "purl_candidate": identity.get("purl_candidate") or record.get("purl_candidate"),
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "accepted_package_identity_truth": False,
        "package_identity_seed_accepts_identity": False,
        "blocked_reasons": _blocked_reasons(inputs),
        "limitations": _limitations(inputs) + ["Package identity review seed is not accepted identity truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H2 package identity review seed is a local review preview only."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h2_dependency_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    candidates = _dependency_candidates_from_inputs(inputs, record)
    candidate = candidates[0] if candidates else {}
    source_id = _source_id(candidate or record)
    name = str(candidate.get("dependency_name") or "unknown")
    seed = {
        "schema_version": "h2_dependency_candidate_review_seed.v0",
        "review_seed_id": f"h2.dependency_review_seed.{source_id}.{_slug(name)}.v0",
        "source_id": source_id,
        "review_subject_type": "dependency_candidate",
        "review_subject_ref": candidate.get("dependency_candidate_id"),
        "dependency_name": name,
        "dependency_version_range": candidate.get("dependency_version_range", "unknown"),
        "dependency_kind": candidate.get("dependency_kind", "unknown"),
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "accepted_dependency_correctness": False,
        "dependency_seed_accepts_correctness": False,
        "limitations": _limitations(inputs) + ["Dependency review seed does not prove dependency correctness."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H2 dependency review seed is a candidate-only preview."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h2_package_file_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    candidates = _file_candidates_from_inputs(inputs, record)
    candidate = candidates[0] if candidates else {}
    source_id = _source_id(candidate or record)
    file_name = str(candidate.get("file_name") or "unknown")
    seed = {
        "schema_version": "h2_package_file_candidate_review_seed.v0",
        "review_seed_id": f"h2.file_review_seed.{source_id}.{_slug(file_name)}.v0",
        "source_id": source_id,
        "review_subject_type": "package_file_candidate",
        "review_subject_ref": candidate.get("file_candidate_id"),
        "file_name": file_name,
        "file_kind": candidate.get("file_kind", "unknown"),
        "download_allowed_current": False,
        "payload_available_current": False,
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "package_file_seed_grants_download_or_safety": False,
        "limitations": _limitations(inputs) + ["File/hash review seed grants no download permission and proves no malware safety."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H2 package file review seed is metadata-only."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h2_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    source_cache = _source_cache_from_inputs(inputs, record)
    source_id = _source_id(source_cache or record)
    native_id = str(record.get("source_native_id") or source_cache.get("candidate_id") or "unknown")
    seed = {
        "schema_version": "h2_source_cache_review_seed.v0",
        "review_seed_id": f"h2.source_cache_review_seed.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "review_subject_type": "source_cache_candidate_preview",
        "review_subject_ref": source_cache.get("candidate_id"),
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "source_cache_runtime_mutated": False,
        "accepted_source_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "limitations": _limitations(inputs) + ["Source-cache review seed is not persistence."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H2 source-cache review seed is a preview only."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h2_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    evidence = _evidence_from_inputs(inputs, record)
    source_id = _source_id(evidence or record)
    native_id = str(record.get("source_native_id") or evidence.get("evidence_preview_id") or "unknown")
    seed = {
        "schema_version": "h2_evidence_candidate_review_seed.v0",
        "review_seed_id": f"h2.evidence_review_seed.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "review_subject_type": "evidence_candidate_preview",
        "review_subject_ref": evidence.get("evidence_preview_id"),
        "candidate_count": int(evidence.get("candidate_count", 0)) if evidence else 0,
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "evidence_ledger_runtime_mutated": False,
        "accepted_evidence": False,
        "evidence_review_seed_accepts_evidence": False,
        "limitations": _limitations(inputs) + ["Evidence candidate review seed is not evidence acceptance."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H2 evidence review seed is a candidate-only preview."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h2_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h2_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h2.candidate_promotion_preview.{_digest(inputs)[:12]}.v0",
        "wave_id": "H2",
        "preview_status": "not_ready_review_required",
        "package_identity_review_seed_count": len(_list(inputs.get("package_identity_review_seeds"))),
        "dependency_candidate_review_seed_count": len(_list(inputs.get("dependency_candidate_review_seeds"))),
        "package_file_candidate_review_seed_count": len(_list(inputs.get("package_file_candidate_review_seeds"))),
        "source_cache_review_seed_count": len(_list(inputs.get("source_cache_review_seeds"))),
        "evidence_candidate_review_seed_count": len(_list(inputs.get("evidence_candidate_review_seeds"))),
        "review_required": True,
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "allowed_next_actions": ["human_review", "h3_policy_pack_planning"],
        "forbidden_next_actions": ["accept_candidate", "mutate_public_index", "mutate_master_index", "download_package", "install_or_execute"],
        "limitations": ["Promotion preview does not promote or accept any candidate."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H2 promotion preview is rehearsal evidence only."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h2_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(inputs.get("source_id") or "h2_package_registry")
    normalized_count = int(inputs.get("records_normalized", 1 if inputs.get("normalized_record_ref") else 0))
    preview = {
        "schema_version": "h2_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h2.coverage_update.{source_id}.{_digest(inputs)[:10]}.v0",
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


def build_h2_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(inputs.get("source_id") or "h2_package_registry")
    blocked = bool(_blocked_reasons(inputs))
    update = {
        "schema_version": "h2_connector_scorecard_update.v0",
        "connector_scorecard_update_id": f"h2.scorecard_update.{source_id}.{_digest(inputs)[:10]}.v0",
        "source_id": source_id,
        "scorecard_update_status": "blocked_live_probe_reviewed" if blocked else "fixture_review_integrated",
        "fixture_replay_status": "passed" if inputs.get("fixture_replay_used", True) else "not_used",
        "live_probe_status": str(inputs.get("live_probe_status", "blocked_or_not_used")),
        "review_integration_status": "preview_created",
        "quality_delta_status": "created",
        "production_ready": False,
        "auto_approves_future_connectors": False,
        "metrics": {
            "identity_review_seed_count": int(inputs.get("identity_review_seed_count", 1)),
            "dependency_review_seed_count": int(inputs.get("dependency_review_seed_count", 0)),
            "file_review_seed_count": int(inputs.get("file_review_seed_count", 0)),
            "source_cache_candidate_count": int(inputs.get("source_cache_candidate_count", 1)),
            "evidence_candidate_count": int(inputs.get("evidence_candidate_count", 1)),
            "policy_block_count": len(_blocked_reasons(inputs)),
            "warning_count": int(inputs.get("warning_count", 0)),
        },
        "limitations": _limitations(inputs) + ["Scorecard update is not production readiness."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Scorecard update summarizes review previews only."],
    }
    _raise_if_boundaries_fail(update, policy)
    return update


def build_h2_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_ids = sorted({str(item) for item in _list(inputs.get("sources")) if item})
    preview = {
        "schema_version": "h2_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h2.source_pack_update.{_digest(inputs)[:12]}.v0",
        "wave_id": "H2",
        "sources": source_ids,
        "pack_update_status": "draft_update_preview",
        "source_pack_imported": False,
        "source_pack_submitted": False,
        "source_pack_accepted": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "review_required": True,
        "limitations": ["Source pack update remains a preview and is not imported, submitted, or accepted."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Source pack update preview is planning evidence only."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h2_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    raw_outputs = [deepcopy(dict(item)) for item in _list(inputs.get("outputs")) if isinstance(item, Mapping)]
    records = [_record_from_inputs(item) for item in raw_outputs if _record_from_inputs(item)]
    sources = sorted({source for source in (_source_id(item) for item in records) if source != "unknown_source"})
    live_outputs = [item for item in raw_outputs if item.get("schema_version") == "h2_package_live_probe_result.v0"]
    fixture_outputs = [item for item in raw_outputs if item.get("schema_version") == "h2_package_fixture_replay_result.v0"]
    blocked_sources = sorted({
        str(item.get("source_id"))
        for item in live_outputs
        if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id")
    })

    identity_seeds = [build_h2_package_identity_review_seed(record, policy) for record in records]
    dependency_seeds = [_dependency_review_seed(candidate, policy) for record in records for candidate in _dependency_candidates_from_inputs(record, record)]
    file_seeds = [_file_review_seed(candidate, policy) for record in records for candidate in _file_candidates_from_inputs(record, record)]
    source_seeds = [build_h2_source_cache_review_seed(record, policy) for record in records]
    evidence_seeds = [build_h2_evidence_candidate_review_seed(record, policy) for record in records]
    coverage_updates = [
        build_h2_coverage_update_preview(
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
        build_h2_connector_scorecard_update(
            {
                "source_id": _source_id(record),
                "fixture_replay_used": True,
                "live_probe_status": "blocked_or_not_used" if _source_id(record) in blocked_sources else "not_used",
                "identity_review_seed_count": 1,
                "dependency_review_seed_count": len(_dependency_candidates_from_inputs(record, record)),
                "file_review_seed_count": len(_file_candidates_from_inputs(record, record)),
                "source_cache_candidate_count": 1,
                "evidence_candidate_count": 1,
                "blocked_reasons": blocked_sources if _source_id(record) in blocked_sources else [],
            },
            policy,
        )
        for record in records
    ]
    promotion = build_h2_candidate_promotion_preview(
        {
            "package_identity_review_seeds": identity_seeds,
            "dependency_candidate_review_seeds": dependency_seeds,
            "package_file_candidate_review_seeds": file_seeds,
            "source_cache_review_seeds": source_seeds,
            "evidence_candidate_review_seeds": evidence_seeds,
            "blocked_reasons": _blocked_reasons(raw_outputs),
        },
        policy,
    )
    pack_preview = build_h2_source_pack_update_preview({"sources": sources}, policy)
    result = {
        "schema_version": "h2_package_review_integration_result.v0",
        "review_integration_result_id": f"h2.review_integration.{_digest(raw_outputs)[:12]}.v0",
        "wave_id": "H2",
        "sources": sources,
        "input_refs": _list(inputs.get("input_refs")),
        "used_fixture_outputs": [{"source_id": item.get("source_id"), "ref": item.get("replay_result_id")} for item in fixture_outputs],
        "used_live_probe_outputs": [{"source_id": item.get("source_id"), "ref": item.get("live_probe_result_id"), "status": item.get("result_status")} for item in live_outputs],
        "package_identity_review_seeds": identity_seeds,
        "dependency_candidate_review_seeds": dependency_seeds,
        "package_file_candidate_review_seeds": file_seeds,
        "source_cache_review_seeds": source_seeds,
        "evidence_candidate_review_seeds": evidence_seeds,
        "candidate_promotion_previews": [promotion],
        "coverage_update_previews": coverage_updates,
        "scorecard_updates": scorecard_updates,
        "source_pack_update_previews": [pack_preview],
        "blocked_sources": blocked_sources,
        "warnings": list(inputs.get("warnings", [])),
        "limitations": [
            "Review integration uses explicit committed H2 outputs only.",
            "Review seeds are not review decisions.",
            "Fixture-equivalent H2 outputs support H3 planning, not public truth.",
        ],
        "accepts_package_identity_truth": False,
        "accepts_dependency_correctness": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_package_downloads": False,
        "enables_install_execute": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H2 review integration mutates no source cache, evidence ledger, review queue, public index, or master index."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h2_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    violations = detect_h2_review_truth_boundary_violations(result, None) + detect_h2_review_product_boundary_violations(result, None)
    return {
        "schema_version": "h2_review_integration_summary.v0",
        "status": "pass" if not violations else "invalid",
        "wave_id": result.get("wave_id", "H2"),
        "source_count": len(result.get("sources", [])),
        "package_identity_review_seed_count": len(result.get("package_identity_review_seeds", [])),
        "dependency_candidate_review_seed_count": len(result.get("dependency_candidate_review_seeds", [])),
        "package_file_candidate_review_seed_count": len(result.get("package_file_candidate_review_seeds", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "candidate_promotion_preview_count": len(result.get("candidate_promotion_previews", [])),
        "coverage_update_preview_count": len(result.get("coverage_update_previews", [])),
        "scorecard_update_count": len(result.get("scorecard_updates", [])),
        "source_pack_update_preview_count": len(result.get("source_pack_update_previews", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_violations": violations,
    }


def detect_h2_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"{path}=true is forbidden for H2 review artifacts" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True]


def detect_h2_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"{path}=true is forbidden for H2 review product boundaries" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True]


def _dependency_review_seed(candidate: Mapping[str, Any], policy: Mapping[str, Any] | None) -> dict[str, Any]:
    return build_h2_dependency_candidate_review_seed({"schema_version": "h2_package_dependency_candidate.v0", **dict(candidate)}, policy)


def _file_review_seed(candidate: Mapping[str, Any], policy: Mapping[str, Any] | None) -> dict[str, Any]:
    return build_h2_package_file_candidate_review_seed({"schema_version": "h2_package_file_candidate.v0", **dict(candidate)}, policy)


def _record_from_inputs(inputs: Mapping[str, Any]) -> dict[str, Any]:
    if not inputs:
        return {}
    payload = deepcopy(dict(inputs))
    if payload.get("schema_version") == "h2_package_normalized_record.v0":
        return payload
    if isinstance(payload.get("normalized_record"), Mapping):
        return deepcopy(dict(payload["normalized_record"]))
    envelope = payload.get("connector_output_envelope")
    if isinstance(envelope, Mapping) and isinstance(envelope.get("normalized_record"), Mapping):
        return deepcopy(dict(envelope["normalized_record"]))
    return {}


def _identity_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    if inputs.get("schema_version") == "h2_package_identity_candidate.v0":
        return dict(inputs)
    if isinstance(record.get("package_identity_candidate"), Mapping):
        return dict(record["package_identity_candidate"])
    if isinstance(inputs.get("package_identity_candidate"), Mapping):
        return dict(inputs["package_identity_candidate"])
    return {}


def _dependency_candidates_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> list[dict[str, Any]]:
    if inputs.get("schema_version") == "h2_package_dependency_candidate.v0":
        return [dict(inputs)]
    value = record.get("dependency_candidate_preview") if record else inputs.get("dependency_candidate_preview")
    return [dict(item) for item in value] if isinstance(value, list) else []


def _file_candidates_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> list[dict[str, Any]]:
    if inputs.get("schema_version") == "h2_package_file_candidate.v0":
        return [dict(inputs)]
    value = record.get("file_candidate_preview") if record else inputs.get("package_file_candidate_preview")
    return [dict(item) for item in value] if isinstance(value, list) else []


def _source_cache_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(record.get("source_cache_candidate_preview"), Mapping):
        return dict(record["source_cache_candidate_preview"])
    if isinstance(inputs.get("source_cache_candidate_preview"), Mapping):
        return dict(inputs["source_cache_candidate_preview"])
    return {}


def _evidence_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(record.get("evidence_candidate_preview"), Mapping):
        return dict(record["evidence_candidate_preview"])
    if isinstance(inputs.get("evidence_candidate_preview"), Mapping):
        return dict(inputs["evidence_candidate_preview"])
    return {}


def _source_id(value: Mapping[str, Any]) -> str:
    return str(value.get("source_id") or "unknown_source")


def _input_basis(value: Mapping[str, Any]) -> str:
    schema = str(value.get("schema_version", ""))
    if schema == "h2_package_live_probe_result.v0":
        return "live_probe_output"
    if schema == "h2_package_normalized_record.v0":
        return "normalized_record"
    if schema.startswith("h2_package_") and schema.endswith("candidate.v0"):
        return "candidate_output"
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
        "package_identity_seed_accepts_identity": False,
        "dependency_seed_accepts_correctness": False,
        "package_file_seed_grants_download_or_safety": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "accepts_package_identity_truth": False,
        "accepts_dependency_correctness": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "package_identity_candidate_is_truth": False,
        "purl_candidate_is_truth": False,
        "dependency_candidate_is_correctness_proof": False,
        "file_hash_candidate_is_malware_safety": False,
        "license_metadata_is_rights_clearance": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "production_readiness_claimed": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "package_download_enabled": False,
        "package_manager_invocation_enabled": False,
        "install_execute_enabled": False,
        "source_sync_enabled": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "downloads_made": False,
        "package_manager_invoked": False,
    }


def _raise_if_boundaries_fail(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    violations = detect_h2_review_truth_boundary_violations(payload, policy) + detect_h2_review_product_boundary_violations(payload, policy)
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


def h2_source_ids() -> tuple[str, ...]:
    return tuple(H2_SOURCE_IDS)
