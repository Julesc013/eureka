"""Offline H5 vendor/update/driver review integration helpers.

These helpers consume explicit H5 fixture replay outputs and blocked or
approved metadata-only live-probe outputs. They create review seeds and
planning previews only; they do not call networks, fetch vendor catalogs,
download artifacts, invoke vendor tools, flash firmware, execute installers,
accept truth, or mutate runtime state or indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.normalizer_common import H5_SOURCE_CONFIGS, H5_SOURCE_IDS


FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_authenticity_truth",
    "accepted_candidate_truth",
    "accepted_compatibility_truth",
    "accepted_driver_identity_truth",
    "accepted_evidence_truth",
    "accepted_firmware_identity_truth",
    "accepted_public_record",
    "accepted_runtime_identity_truth",
    "accepted_safety_truth",
    "accepted_source_truth",
    "accepted_vendor_truth",
    "accepts_authenticity_truth",
    "accepts_candidate_truth",
    "accepts_compatibility_truth",
    "accepts_driver_identity_truth",
    "accepts_evidence_truth",
    "accepts_firmware_identity_truth",
    "accepts_runtime_identity_truth",
    "accepts_safety_truth",
    "accepts_source_truth",
    "accepts_vendor_truth",
    "authenticity_seed_accepts_authenticity_truth",
    "automatic_future_connector_approval",
    "candidate_promotion_preview_promotes_candidate",
    "compatibility_seed_accepts_compatibility_truth",
    "driver_identity_seed_accepts_driver_truth",
    "evidence_review_seed_accepts_evidence",
    "firmware_identity_seed_accepts_firmware_truth",
    "future_connector_auto_approval",
    "h5_postmortem_enables_future_connectors_automatically",
    "license_metadata_is_rights_clearance",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutates_master_index",
    "mutates_public_index",
    "payload_seed_grants_download_or_safety",
    "production_readiness_claimed",
    "public_index_mutated",
    "rights_clearance_claimed",
    "runtime_identity_seed_accepts_runtime_truth",
    "safety_seed_accepts_safety_truth",
    "signature_metadata_is_authenticity_truth",
    "source_cache_review_seed_accepts_source",
    "source_pack_preview_is_imported_or_submitted",
    "vendor_identity_seed_accepts_vendor_truth",
    "verified_authenticity_claimed",
    "verified_compatibility_claimed",
    "verified_installability_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "api_calls_made",
    "catalog_fetch_enabled",
    "changed_public_search_behavior",
    "driver_download_enabled",
    "downloads_enabled",
    "enabled_accounts",
    "enabled_catalog_sync",
    "enabled_downloads",
    "enabled_execution",
    "enabled_firmware_flashing",
    "enabled_hosting",
    "enabled_installers",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "enabled_vendor_tool_invocation",
    "enables_catalog_fetch",
    "enables_downloads",
    "enables_firmware_flash",
    "enables_install_execute",
    "enables_vendor_tool_invocation",
    "firmware_download_enabled",
    "firmware_flash_enabled",
    "install_execute_enabled",
    "installer_download_enabled",
    "mutated_master_index",
    "mutated_public_index",
    "network_calls_made",
    "package_manager_invocation_enabled",
    "runtime_download_enabled",
    "source_cache_runtime_mutated",
    "source_sync_enabled",
    "vendor_catalog_fetch_enabled",
    "vendor_tool_invocation_enabled",
}


def load_h5_vendor_update_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h5_vendor_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    ref = _first_ref(inputs, "vendor_identity_candidate_ref", "vendor_identity_candidate", "vendor_identity_candidate_id")
    seed = _seed_base("vendor_identity", source_id, ref, inputs)
    seed.update(
        {
            "schema_version": "h5_vendor_identity_review_seed.v0",
            "review_subject_type": "vendor_identity_candidate",
            "review_subject_ref": ref,
            "vendor_name": _vendor_name(source_id, inputs),
            "accepted_vendor_truth": False,
            "vendor_identity_seed_accepts_vendor_truth": False,
            "vendor_source_proves_official_status": False,
            "vendor_presence_proves_endorsement": False,
            "limitations": _limitations(inputs) + ["Vendor identity review seed is not accepted vendor truth or official-status proof."],
        }
    )
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h5_driver_device_compatibility_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    ref = _first_ref(inputs, "driver_device_compatibility_candidate_refs", "driver_device_compatibility_candidate", "compatibility_candidate_id")
    seed = _seed_base("driver_device_compatibility", source_id, ref, inputs)
    seed.update(
        {
            "schema_version": "h5_driver_device_compatibility_review_seed.v0",
            "review_subject_type": "driver_device_compatibility_candidate",
            "review_subject_ref": ref,
            "accepted_driver_identity_truth": False,
            "accepted_compatibility_truth": False,
            "driver_identity_seed_accepts_driver_truth": False,
            "compatibility_seed_accepts_compatibility_truth": False,
            "device_id_match_proves_safe_installability": False,
            "os_version_match_proves_runtime_correctness": False,
            "limitations": _limitations(inputs) + ["Driver/device compatibility seed is not verified compatibility or safe installability."],
        }
    )
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h5_firmware_update_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    ref = _first_ref(inputs, "firmware_update_candidate_refs", "firmware_update_candidate", "firmware_update_candidate_id")
    seed = _seed_base("firmware_update", source_id, ref, inputs)
    seed.update(
        {
            "schema_version": "h5_firmware_update_review_seed.v0",
            "review_subject_type": "firmware_update_candidate",
            "review_subject_ref": ref,
            "accepted_firmware_identity_truth": False,
            "firmware_identity_seed_accepts_firmware_truth": False,
            "firmware_update_candidate_is_approved_to_flash": False,
            "firmware_metadata_proves_device_compatibility": False,
            "firmware_hash_proves_malware_safety": False,
            "signature_metadata_is_authenticity_truth": False,
            "flashing_tool_metadata_is_execution_permission": False,
            "limitations": _limitations(inputs) + ["Firmware/update review seed is not install, execute, download, or flash permission."],
        }
    )
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h5_runtime_redistributable_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    ref = _first_ref(inputs, "runtime_redistributable_candidate_refs", "runtime_redistributable_candidate", "runtime_candidate_id")
    seed = _seed_base("runtime_redistributable", source_id, ref, inputs)
    seed.update(
        {
            "schema_version": "h5_runtime_redistributable_review_seed.v0",
            "review_subject_type": "runtime_redistributable_candidate",
            "review_subject_ref": ref,
            "accepted_runtime_identity_truth": False,
            "runtime_identity_seed_accepts_runtime_truth": False,
            "runtime_candidate_is_installability_truth": False,
            "installer_metadata_is_execution_permission": False,
            "dependency_metadata_is_dependency_correctness": False,
            "security_update_metadata_is_safety_proof": False,
            "limitations": _limitations(inputs) + ["Runtime redistributable seed is not installability, dependency correctness, or safety proof."],
        }
    )
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h5_payload_metadata_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    ref = _first_ref(inputs, "payload_metadata_candidate_refs", "payload_metadata_candidate", "payload_candidate_id")
    seed = _seed_base("payload_metadata", source_id, ref, inputs)
    seed.update(
        {
            "schema_version": "h5_payload_metadata_review_seed.v0",
            "review_subject_type": "payload_metadata_candidate",
            "review_subject_ref": ref,
            "payload_seed_grants_download_or_safety": False,
            "download_allowed_current": False,
            "installer_execution_allowed_current": False,
            "firmware_flash_allowed_current": False,
            "payload_hash_proves_malware_safety": False,
            "signature_metadata_is_authenticity_truth": False,
            "limitations": _limitations(inputs) + ["Payload metadata seed grants no download, execution, safety, authenticity, or rights permission."],
        }
    )
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h5_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    ref = str(inputs.get("source_cache_candidate_ref") or _nested(inputs, "source_cache_candidate_preview", "source_cache_candidate_id") or f"h5.source_cache.{source_id}.preview")
    seed = _seed_base("source_cache", source_id, ref, inputs)
    seed.update(
        {
            "schema_version": "h5_source_cache_review_seed.v0",
            "review_subject_type": "source_cache_candidate_preview",
            "review_subject_ref": ref,
            "accepted_source_truth": False,
            "source_cache_review_seed_accepts_source": False,
            "source_cache_runtime_mutated": False,
            "limitations": _limitations(inputs) + ["Source-cache review seed is not accepted source state and is not persisted."],
        }
    )
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h5_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    ref = str(inputs.get("evidence_candidate_preview_ref") or _nested(inputs, "evidence_candidate_preview", "evidence_candidate_preview_id") or f"h5.evidence_preview.{source_id}.preview")
    seed = _seed_base("evidence_candidate", source_id, ref, inputs)
    seed.update(
        {
            "schema_version": "h5_evidence_candidate_review_seed.v0",
            "review_subject_type": "evidence_candidate_preview",
            "review_subject_ref": ref,
            "accepted_evidence_truth": False,
            "accepted_candidate_truth": False,
            "evidence_review_seed_accepts_evidence": False,
            "evidence_ledger_runtime_mutated": False,
            "limitations": _limitations(inputs) + ["Evidence candidate review seed is not evidence acceptance or candidate acceptance."],
        }
    )
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h5_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = _preview_base("candidate_promotion", source_id, inputs)
    preview.update(
        {
            "schema_version": "h5_candidate_promotion_preview.v0",
            "preview_status": "dry_run_only",
            "promotion_allowed": False,
            "candidate_promotion_preview_promotes_candidate": False,
            "accepted_candidate_truth": False,
            "limitations": ["Candidate promotion preview is dry-run only and does not promote or accept anything."],
        }
    )
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h5_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = _preview_base("coverage_update", source_id, inputs)
    preview.update(
        {
            "schema_version": "h5_source_coverage_update_preview.v0",
            "coverage_basis": "fixture_review_and_blocked_live_probe_evidence",
            "coverage_manifest_is_exhaustive_global_coverage": False,
            "records_reviewed": 1,
            "production_vendor_coverage": False,
            "limitations": ["Coverage update is a preview and is not exhaustive global or production vendor coverage."],
        }
    )
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h5_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = _preview_base("connector_scorecard", source_id, inputs)
    preview.update(
        {
            "schema_version": "h5_connector_scorecard_update.v0",
            "fixture_replay_integrated": inputs.get("schema_version") == "h5_vendor_update_fixture_replay_result.v0",
            "live_probe_completed": inputs.get("result_status") == "live_probe_completed",
            "live_probe_blocked": str(inputs.get("result_status", "")).startswith("blocked"),
            "production_ready": False,
            "auto_approves_future_connectors": False,
            "limitations": ["Scorecard update is not production readiness and does not auto-approve future connectors."],
        }
    )
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h5_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = _preview_base("source_pack_update", source_id, inputs)
    preview.update(
        {
            "schema_version": "h5_source_pack_update_preview.v0",
            "source_pack_preview_is_imported_or_submitted": False,
            "source_pack_import_enabled": False,
            "source_pack_submission_enabled": False,
            "source_pack_acceptance_enabled": False,
            "limitations": ["Source pack update preview is not import, submission, or acceptance."],
        }
    )
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h5_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = [dict(item) for item in inputs.get("outputs", []) if isinstance(item, Mapping)]
    replay_outputs = [item for item in outputs if item.get("schema_version") == "h5_vendor_update_fixture_replay_result.v0"]
    live_outputs = [item for item in outputs if item.get("schema_version") == "h5_vendor_update_live_probe_result.v0"]
    sources = sorted({str(item.get("source_id")) for item in outputs if item.get("source_id")} or set(H5_SOURCE_IDS))
    blocked_sources = sorted({str(item.get("source_id")) for item in live_outputs if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id")})
    basis_by_source = _basis_by_source(sources, replay_outputs, live_outputs)
    result = {
        "schema_version": "h5_vendor_update_review_integration_result.v0",
        "review_integration_result_id": f"h5.review_integration.{_digest({'sources': sources, 'inputs': inputs.get('input_refs', [])})[:12]}.v0",
        "wave_id": "H5",
        "sources": sources,
        "input_refs": list(inputs.get("input_refs", [])),
        "used_fixture_outputs": [
            {
                "source_id": item.get("source_id"),
                "replay_result_id": item.get("replay_result_id"),
                "status": item.get("replay_status"),
                "no_network_used": item.get("no_network_used") is True,
            }
            for item in replay_outputs
        ],
        "used_live_probe_outputs": [
            {
                "source_id": item.get("source_id"),
                "live_probe_result_id": item.get("live_probe_result_id"),
                "status": item.get("result_status"),
                "request_count": item.get("request_count", 0),
                "network_used": item.get("network_used") is True,
            }
            for item in live_outputs
        ],
        "vendor_identity_review_seeds": [build_h5_vendor_identity_review_seed(basis_by_source[source_id], policy) for source_id in sources],
        "driver_device_compatibility_review_seeds": [build_h5_driver_device_compatibility_review_seed(basis_by_source[source_id], policy) for source_id in sources],
        "firmware_update_review_seeds": [build_h5_firmware_update_review_seed(basis_by_source[source_id], policy) for source_id in sources],
        "runtime_redistributable_review_seeds": [build_h5_runtime_redistributable_review_seed(basis_by_source[source_id], policy) for source_id in sources],
        "payload_metadata_review_seeds": [build_h5_payload_metadata_review_seed(basis_by_source[source_id], policy) for source_id in sources],
        "source_cache_review_seeds": [build_h5_source_cache_review_seed(basis_by_source[source_id], policy) for source_id in sources],
        "evidence_candidate_review_seeds": [build_h5_evidence_candidate_review_seed(basis_by_source[source_id], policy) for source_id in sources],
        "candidate_promotion_previews": [build_h5_candidate_promotion_preview(basis_by_source[source_id], policy) for source_id in sources],
        "coverage_update_previews": [build_h5_coverage_update_preview(basis_by_source[source_id], policy) for source_id in sources],
        "scorecard_updates": [build_h5_connector_scorecard_update(basis_by_source[source_id], policy) for source_id in sources],
        "source_pack_update_previews": [build_h5_source_pack_update_preview(basis_by_source[source_id], policy) for source_id in sources],
        "blocked_sources": blocked_sources,
        "warnings": ["H5 live probes are blocked pending operator approval"] if blocked_sources else [],
        "limitations": [
            "Review integration uses fixture replay outputs and blocked live-probe reports only.",
            "No vendor metadata is accepted as official status, compatibility, authenticity, safety, installability, rights, or public truth.",
        ],
        "accepts_vendor_truth": False,
        "accepts_driver_identity_truth": False,
        "accepts_firmware_identity_truth": False,
        "accepts_runtime_identity_truth": False,
        "accepts_compatibility_truth": False,
        "accepts_authenticity_truth": False,
        "accepts_safety_truth": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_catalog_fetch": False,
        "enables_downloads": False,
        "enables_vendor_tool_invocation": False,
        "enables_firmware_flash": False,
        "enables_install_execute": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H5 review integration is a local review rehearsal, not promotion."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h5_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    errors = detect_h5_review_truth_boundary_violations(result) + detect_h5_review_product_boundary_violations(result)
    return {
        "schema_version": "h5_review_integration_summary.v0",
        "status": "pass" if not errors else "invalid",
        "review_integration_result_id": result.get("review_integration_result_id"),
        "source_count": len(result.get("sources", [])),
        "vendor_identity_review_seed_count": len(result.get("vendor_identity_review_seeds", [])),
        "driver_device_compatibility_review_seed_count": len(result.get("driver_device_compatibility_review_seeds", [])),
        "firmware_update_review_seed_count": len(result.get("firmware_update_review_seeds", [])),
        "runtime_redistributable_review_seed_count": len(result.get("runtime_redistributable_review_seeds", [])),
        "payload_metadata_review_seed_count": len(result.get("payload_metadata_review_seeds", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_violations": detect_h5_review_truth_boundary_violations(result),
        "product_boundary_violations": detect_h5_review_product_boundary_violations(result),
    }


def detect_h5_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth")


def detect_h5_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product")


def _seed_base(kind: str, source_id: str, ref: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "review_seed_id": f"h5.{kind}_review_seed.{source_id}.{_digest({'ref': ref, 'kind': kind})[:8]}.v0",
        "wave_id": "H5",
        "source_id": source_id,
        "connector_family": _connector_family(source_id, inputs),
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H5 review seed is candidate-only and does not persist runtime state."],
    }


def _preview_base(kind: str, source_id: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "preview_id": f"h5.{kind}.{source_id}.{_digest({'source': source_id, 'kind': kind, 'basis': _input_basis(inputs)})[:8]}.v0",
        "wave_id": "H5",
        "source_id": source_id,
        "connector_family": _connector_family(source_id, inputs),
        "input_basis": _input_basis(inputs),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H5 preview is not an accepted record, decision, or product mutation."],
    }


def _basis_by_source(sources: Sequence[str], replay_outputs: Sequence[Mapping[str, Any]], live_outputs: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    by_source: dict[str, Mapping[str, Any]] = {}
    for source_id in sources:
        replay = next((item for item in replay_outputs if item.get("source_id") == source_id), None)
        live = next((item for item in live_outputs if item.get("source_id") == source_id), None)
        by_source[source_id] = replay or live or {"source_id": source_id, "schema_version": "h5_missing_review_input.v0", "limitations": ["no explicit input found"]}
    return by_source


def _first_ref(inputs: Mapping[str, Any], list_or_ref_key: str, object_key: str, object_id_key: str) -> str:
    value = inputs.get(list_or_ref_key)
    if isinstance(value, list) and value:
        return str(value[0])
    if value:
        return str(value)
    nested = _nested(inputs, object_key, object_id_key)
    if nested:
        return str(nested)
    source_id = _source_id(inputs)
    return f"h5.{object_key}.{source_id}.preview"


def _nested(inputs: Mapping[str, Any], object_key: str, nested_key: str) -> Any:
    value = inputs.get(object_key)
    if isinstance(value, Mapping):
        return value.get(nested_key)
    return None


def _input_basis(inputs: Mapping[str, Any]) -> str:
    schema = str(inputs.get("schema_version") or "unknown")
    if schema == "h5_vendor_update_fixture_replay_result.v0":
        return "fixture_replay_output"
    if schema == "h5_vendor_update_live_probe_result.v0":
        return "live_probe_output"
    if schema == "h5_vendor_update_normalized_record.v0":
        return "normalized_record"
    return schema


def _source_id(inputs: Mapping[str, Any]) -> str:
    source_id = str(inputs.get("source_id") or "")
    if source_id:
        return source_id
    raise ValueError("H5 review input is missing source_id")


def _connector_family(source_id: str, inputs: Mapping[str, Any]) -> str:
    return str(inputs.get("connector_family") or H5_SOURCE_CONFIGS.get(source_id, {}).get("connector_family") or "vendor_update_driver_firmware")


def _vendor_name(source_id: str, inputs: Mapping[str, Any]) -> str:
    return str(inputs.get("vendor_name") or _nested(inputs, "vendor_identity_candidate", "vendor_name") or H5_SOURCE_CONFIGS.get(source_id, {}).get("vendor_name") or "unknown")


def _limitations(inputs: Mapping[str, Any]) -> list[str]:
    values = inputs.get("limitations")
    if isinstance(values, list):
        return [str(item) for item in values]
    return []


def _truth_boundary() -> dict[str, bool]:
    return {
        "vendor_identity_seed_accepts_vendor_truth": False,
        "driver_identity_seed_accepts_driver_truth": False,
        "firmware_identity_seed_accepts_firmware_truth": False,
        "runtime_identity_seed_accepts_runtime_truth": False,
        "compatibility_seed_accepts_compatibility_truth": False,
        "authenticity_seed_accepts_authenticity_truth": False,
        "safety_seed_accepts_safety_truth": False,
        "payload_seed_grants_download_or_safety": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "accepted_vendor_truth": False,
        "accepted_driver_identity_truth": False,
        "accepted_firmware_identity_truth": False,
        "accepted_runtime_identity_truth": False,
        "accepted_compatibility_truth": False,
        "accepted_authenticity_truth": False,
        "accepted_safety_truth": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "accepted_public_record": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "verified_compatibility_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "h5_postmortem_enables_future_connectors_automatically": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_catalog_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "enabled_firmware_flashing": False,
        "enabled_vendor_tool_invocation": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "catalog_fetch_enabled": False,
        "vendor_catalog_fetch_enabled": False,
        "driver_download_enabled": False,
        "firmware_download_enabled": False,
        "runtime_download_enabled": False,
        "installer_download_enabled": False,
        "vendor_tool_invocation_enabled": False,
        "package_manager_invocation_enabled": False,
        "firmware_flash_enabled": False,
        "install_execute_enabled": False,
        "network_calls_made": False,
        "api_calls_made": False,
    }


def _detect_true_keys(value: Any, forbidden: set[str], category: str, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            current = f"{path}.{key}" if path else str(key)
            if key in forbidden and item is True:
                errors.append(f"{category} boundary forbidden true value: {current}")
            errors.extend(_detect_true_keys(item, forbidden, category, current))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_detect_true_keys(item, forbidden, category, f"{path}[{index}]"))
    return sorted(dict.fromkeys(errors))


def _raise_if_boundaries_fail(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h5_review_truth_boundary_violations(record, policy) + detect_h5_review_product_boundary_violations(record, policy)
    if errors:
        raise ValueError("; ".join(errors))


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
