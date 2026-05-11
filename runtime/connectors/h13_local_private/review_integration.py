"""Offline H13 local/private review integration helpers.

These helpers consume committed H13 fixture replay outputs and blocked boundary
dry-run reports. They produce review seeds and previews only; they do not
access local/private/restricted sources, scan, fetch, hash files, import CAS,
export/import packs, publish, accept truth, or mutate indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from runtime.connectors.h13_local_private.normalizer_common import (
    H13_SOURCE_CONFIGS,
    H13_SOURCE_IDS,
    PRODUCT_FORBIDDEN_TRUE_KEYS as H13_PRODUCT_FORBIDDEN_TRUE_KEYS,
    TRUTH_FORBIDDEN_TRUE_KEYS as H13_TRUTH_FORBIDDEN_TRUE_KEYS,
    detect_h13_secret_or_private_data_violations,
)

EXTRA_TRUTH_FORBIDDEN_TRUE_KEYS = set(['accepted_CAS_import_truth', 'accepted_authenticated_source_truth', 'accepted_candidate_truth', 'accepted_cas_import_truth', 'accepted_evidence_truth', 'accepted_local_source_identity_truth', 'accepted_pack_export_import_truth', 'accepted_privacy_redaction_truth', 'accepted_private_source_truth', 'accepted_public_record', 'accepted_restricted_source_truth', 'accepted_rights_safety_truth', 'accepted_source_truth', 'accepted_user_supplied_url_truth', 'account_entitlement_claimed', 'authenticated_source_seed_grants_account_permission', 'automatic_future_connector_approval', 'candidate_promotion_preview_promotes_candidate', 'cas_import_seed_grants_import_permission', 'evidence_review_seed_accepts_evidence', 'legal_access_claimed', 'local_source_identity_seed_accepts_source_truth', 'malware_safety_claimed', 'master_index_mutated', 'mutated_master_index', 'mutated_public_index', 'ownership_truth_claimed', 'pack_export_import_seed_grants_export_import_permission', 'privacy_redaction_seed_proves_public_safety', 'privacy_safety_claimed', 'private_source_boundary_seed_grants_access_permission', 'production_readiness_claimed', 'public_index_mutated', 'publication_permission_claimed', 'restricted_source_manifest_seed_grants_access_permission', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'rights_safety_seed_accepts_rights_safety_truth', 'source_cache_review_seed_accepts_source', 'source_pack_preview_is_imported_or_submitted', 'source_safety_claimed', 'user_authority_claimed', 'user_supplied_url_seed_grants_fetch_permission', 'verified_authenticity_claimed'])
EXTRA_PRODUCT_FORBIDDEN_TRUE_KEYS = set(['account_access_used', 'acquisition_action_used', 'api_calls_made', 'archive_listing_used', 'authenticated_access_used', 'cas_import_used', 'changed_public_search_behavior', 'credential_handling_used', 'directory_listing_used', 'enabled_account_access', 'enabled_acquisition_actions', 'enabled_cas_import', 'enabled_evidence_writes', 'enabled_execution', 'enabled_extraction', 'enabled_hosting', 'enabled_local_access', 'enabled_pack_export_import', 'enabled_private_access', 'enabled_publication', 'enabled_restricted_access', 'enabled_source_cache_writes', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'enabled_url_fetch', 'evidence_write_used', 'execution_used', 'extraction_used', 'file_hashing_used', 'filesystem_scan_used', 'fingerprinting_used', 'local_access_used', 'malware_scanning_used', 'model_provider_calls_made', 'mutated_master_index', 'mutated_public_index', 'network_calls_made', 'pack_export_import_used', 'private_source_access_used', 'publication_used', 'restricted_source_access_used', 'source_cache_write_used', 'upload_used', 'user_supplied_url_fetch_used'])
FORBIDDEN_TRUTH_TRUE_KEYS = set(H13_TRUTH_FORBIDDEN_TRUE_KEYS) | EXTRA_TRUTH_FORBIDDEN_TRUE_KEYS
FORBIDDEN_PRODUCT_TRUE_KEYS = set(H13_PRODUCT_FORBIDDEN_TRUE_KEYS) | EXTRA_PRODUCT_FORBIDDEN_TRUE_KEYS
REVIEW_SEED_KEYS = tuple(['local_source_identity_review_seeds', 'private_source_boundary_review_seeds', 'user_supplied_url_boundary_review_seeds', 'authenticated_source_boundary_review_seeds', 'restricted_source_manifest_review_seeds', 'local_cas_import_boundary_review_seeds', 'pack_export_import_boundary_review_seeds', 'privacy_redaction_review_seeds', 'local_private_rights_safety_review_seeds', 'source_cache_review_seeds', 'evidence_candidate_review_seeds'])

KIND_CONFIG = {
    "local_source_identity": ("h13_local_source_identity_review_seed.v0", "local_source_identity_candidate", "accepted_local_source_identity_truth", "local_source_identity_seed_accepts_source_truth", "Local source identity review seed is not accepted local source truth, ownership proof, local file identity proof, import permission, export permission, or publication permission."),
    "private_source_boundary": ("h13_private_source_boundary_review_seed.v0", "private_source_boundary_candidate", "accepted_private_source_truth", "private_source_boundary_seed_grants_access_permission", "Private source boundary review seed does not grant access, inspection, export, sharing, indexing, or publication permission."),
    "user_supplied_url_boundary": ("h13_user_supplied_url_boundary_review_seed.v0", "user_supplied_url_boundary_candidate", "accepted_user_supplied_url_truth", "user_supplied_url_seed_grants_fetch_permission", "User-supplied URL boundary review seed does not grant fetch, scrape, crawl, mirror, download, index, or publication permission."),
    "authenticated_source_boundary": ("h13_authenticated_source_boundary_review_seed.v0", "authenticated_source_boundary_candidate", "accepted_authenticated_source_truth", "authenticated_source_seed_grants_account_permission", "Authenticated source boundary review seed does not grant account, credential, token, session, receipt, entitlement, subscription, or user-library access permission."),
    "restricted_source_manifest": ("h13_restricted_source_manifest_review_seed.v0", "restricted_source_manifest_candidate", "accepted_restricted_source_truth", "restricted_source_manifest_seed_grants_access_permission", "Restricted-source manifest review seed is manifest-only and does not grant direct access, scraping, crawling, bypass, acquisition, or publication permission."),
    "local_cas_import_boundary": ("h13_local_cas_import_boundary_review_seed.v0", "local_cas_import_boundary_candidate", "accepted_cas_import_truth", "cas_import_seed_grants_import_permission", "Local CAS import boundary review seed does not grant file hashing, copy, deduplication, CAS write, import, export, or publication permission."),
    "pack_export_import_boundary": ("h13_pack_export_import_boundary_review_seed.v0", "pack_export_import_boundary_candidate", "accepted_pack_export_import_truth", "pack_export_import_seed_grants_export_import_permission", "Pack export/import boundary review seed does not grant private pack export, pack import, redistribution, submission, acceptance, or publication permission."),
    "privacy_redaction": ("h13_privacy_redaction_review_seed.v0", "privacy_redaction_candidate", "accepted_privacy_redaction_truth", "privacy_redaction_seed_proves_public_safety", "Privacy/redaction review seed does not prove public safety, privacy safety, or publication permission."),
    "local_private_rights_safety": ("h13_local_private_rights_safety_review_seed.v0", "local_private_rights_safety_candidate", "accepted_rights_safety_truth", "rights_safety_seed_accepts_rights_safety_truth", "Local/private rights-safety review seed is not rights clearance, legal access, ownership proof, account entitlement proof, privacy safety, malware safety, source safety, or publication permission."),
    "source_cache": ("h13_source_cache_review_seed.v0", "source_cache_candidate_preview", "accepted_source_truth", "source_cache_review_seed_accepts_source", "Source-cache review seed is not accepted source truth and does not write source cache state."),
    "evidence_candidate": ("h13_evidence_candidate_review_seed.v0", "evidence_candidate_preview", "accepted_evidence_truth", "evidence_review_seed_accepts_evidence", "Evidence candidate review seed is not accepted evidence and does not write the evidence ledger."),
}


def load_h13_local_private_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def _build_review_seed(kind: str, inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    schema, subject_type, accept_key, permission_key, limitation = KIND_CONFIG[kind]
    source_id = _source_id(inputs)
    seed = _seed_base(kind, source_id, _first_ref(inputs, subject_type, "candidate_id", "preview_id"), inputs)
    seed.update({
        "schema_version": schema,
        "review_subject_type": subject_type,
        accept_key: False,
        permission_key: False,
        "review_seed_is_review_decision": False,
        "source_cache_write_allowed_current": False,
        "evidence_ledger_write_allowed_current": False,
        "limitations": _limitations(inputs) + [limitation],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h13_local_source_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("local_source_identity", inputs, policy)


def build_h13_private_source_boundary_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("private_source_boundary", inputs, policy)


def build_h13_user_supplied_url_boundary_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("user_supplied_url_boundary", inputs, policy)


def build_h13_authenticated_source_boundary_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("authenticated_source_boundary", inputs, policy)


def build_h13_restricted_source_manifest_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("restricted_source_manifest", inputs, policy)


def build_h13_local_cas_import_boundary_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("local_cas_import_boundary", inputs, policy)


def build_h13_pack_export_import_boundary_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("pack_export_import_boundary", inputs, policy)


def build_h13_privacy_redaction_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("privacy_redaction", inputs, policy)


def build_h13_local_private_rights_safety_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("local_private_rights_safety", inputs, policy)


def build_h13_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("source_cache", inputs, policy)


def build_h13_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("evidence_candidate", inputs, policy)


def build_h13_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h13_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h13.candidate_promotion.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "promotes_candidate": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "review_required_before_promotion": True,
        "limitations": _limitations(inputs) + ["Candidate promotion preview does not promote, accept, persist, publish, import, export, access, or write H13 candidates."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h13_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h13_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h13.coverage_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "coverage_basis": "fixture_replay_and_blocked_boundary_dry_run_evidence",
        "coverage_preview_only": True,
        "coverage_manifest_is_exhaustive_global_coverage": False,
        "production_local_private_coverage": False,
        "limitations": ["Coverage update preview is not exhaustive global coverage, private-source completeness proof, local file identity proof, rights proof, safety proof, or production quality proof."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h13_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    update = {
        "schema_version": "h13_connector_scorecard_update.v0",
        "connector_scorecard_update_id": f"h13.scorecard_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "fixture_replay_status": "integrated",
        "boundary_dry_run_status": "blocked_or_fixture_equivalent_without_approval",
        "review_integration_status": "preview_created",
        "production_ready": False,
        "auto_approves_future_connectors": False,
        "automatic_future_connector_approval": False,
        "limitations": ["Connector scorecard update is not production readiness, access permission, import/export permission, publication permission, safety proof, rights clearance, or future connector approval."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(update, policy)
    return update


def build_h13_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h13_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h13.source_pack_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "source_pack_imported": False,
        "source_pack_submitted": False,
        "source_pack_accepted": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "limitations": ["Source pack update preview is not import, submission, acceptance, public truth, source sync, pack export/import, local/private access, URL fetch, account access, restricted-source access, or publication permission."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h13_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = list(inputs.get("outputs") or [])
    input_refs = [_public_safe_input_ref(ref) for ref in list(inputs.get("input_refs") or [])]
    by_source = _best_inputs_by_source(outputs)
    sources = [source_id for source_id in H13_SOURCE_IDS if source_id in by_source] or list(H13_SOURCE_IDS)
    if set(sources) != set(H13_SOURCE_IDS):
        sources = list(H13_SOURCE_IDS)
    source_inputs = {source_id: by_source.get(source_id, _minimal_source_input(source_id)) for source_id in sources}
    result: dict[str, Any] = {
        "schema_version": "h13_local_private_review_integration_result.v0",
        "review_integration_result_id": f"h13.review_integration.{_digest({'inputs': input_refs, 'sources': sources})[:12]}.v0",
        "wave_id": "H13",
        "sources": sources,
        "source_count": len(sources),
        "input_refs": input_refs,
        "used_fixture_outputs": [item for item in outputs if _is_fixture_output(item)],
        "used_boundary_dry_run_outputs": [item for item in outputs if _is_boundary_output(item)],
        "blocked_sources": _blocked_sources(outputs),
        "warnings": [],
        "limitations": [
            "H13 review integration is a wave-level audit rehearsal only.",
            "Fixture replay and blocked boundary dry-run outputs do not grant local/private/restricted access, URL fetch, account access, CAS import, pack export/import, source-cache writes, evidence writes, publication, or truth acceptance.",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H13 outputs remain candidate/previews only."],
        "accepts_local_source_identity_truth": False,
        "accepts_private_source_truth": False,
        "accepts_user_supplied_url_truth": False,
        "accepts_authenticated_source_truth": False,
        "accepts_restricted_source_truth": False,
        "accepts_cas_import_truth": False,
        "accepts_pack_export_import_truth": False,
        "accepts_privacy_redaction_truth": False,
        "accepts_rights_safety_truth": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_local_access": False,
        "enables_private_source_access": False,
        "enables_user_supplied_url_fetch": False,
        "enables_authenticated_access": False,
        "enables_restricted_source_access": False,
        "enables_cas_import": False,
        "enables_pack_export_import": False,
        "enables_source_cache_write": False,
        "enables_evidence_write": False,
        "enables_publication": False,
    }
    builders = {
        "local_source_identity_review_seeds": build_h13_local_source_identity_review_seed,
        "private_source_boundary_review_seeds": build_h13_private_source_boundary_review_seed,
        "user_supplied_url_boundary_review_seeds": build_h13_user_supplied_url_boundary_review_seed,
        "authenticated_source_boundary_review_seeds": build_h13_authenticated_source_boundary_review_seed,
        "restricted_source_manifest_review_seeds": build_h13_restricted_source_manifest_review_seed,
        "local_cas_import_boundary_review_seeds": build_h13_local_cas_import_boundary_review_seed,
        "pack_export_import_boundary_review_seeds": build_h13_pack_export_import_boundary_review_seed,
        "privacy_redaction_review_seeds": build_h13_privacy_redaction_review_seed,
        "local_private_rights_safety_review_seeds": build_h13_local_private_rights_safety_review_seed,
        "source_cache_review_seeds": build_h13_source_cache_review_seed,
        "evidence_candidate_review_seeds": build_h13_evidence_candidate_review_seed,
        "candidate_promotion_previews": build_h13_candidate_promotion_preview,
        "coverage_update_previews": build_h13_coverage_update_preview,
        "scorecard_updates": build_h13_connector_scorecard_update,
        "source_pack_update_previews": build_h13_source_pack_update_preview,
    }
    for key, builder in builders.items():
        result[key] = [builder(source_inputs[source_id], policy) for source_id in sources]
    if result["blocked_sources"]:
        result["warnings"].append("H13 boundary dry-runs remain blocked pending committed operator/user approvals.")
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h13_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    errors = detect_h13_review_truth_boundary_violations(result) + detect_h13_review_product_boundary_violations(result) + detect_h13_review_private_data_violations(result)
    return {
        "schema_version": "h13_review_integration_summary.v0",
        "status": "pass" if not errors else "invalid",
        "review_integration_result_id": result.get("review_integration_result_id"),
        "source_count": result.get("source_count", 0),
        "local_source_identity_review_seed_count": len(result.get("local_source_identity_review_seeds", [])),
        "private_source_boundary_review_seed_count": len(result.get("private_source_boundary_review_seeds", [])),
        "user_supplied_url_boundary_review_seed_count": len(result.get("user_supplied_url_boundary_review_seeds", [])),
        "authenticated_source_boundary_review_seed_count": len(result.get("authenticated_source_boundary_review_seeds", [])),
        "restricted_source_manifest_review_seed_count": len(result.get("restricted_source_manifest_review_seeds", [])),
        "local_cas_import_boundary_review_seed_count": len(result.get("local_cas_import_boundary_review_seeds", [])),
        "pack_export_import_boundary_review_seed_count": len(result.get("pack_export_import_boundary_review_seeds", [])),
        "privacy_redaction_review_seed_count": len(result.get("privacy_redaction_review_seeds", [])),
        "local_private_rights_safety_review_seed_count": len(result.get("local_private_rights_safety_review_seeds", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "errors": errors,
    }


def detect_h13_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth", violations)
    return sorted(dict.fromkeys(violations))


def detect_h13_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product", violations)
    return sorted(dict.fromkeys(violations))


def detect_h13_review_private_data_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return detect_h13_secret_or_private_data_violations(result, policy)


def _seed_base(kind: str, source_id: str, source_ref: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "review_seed_id": f"h13.review_seed.{kind}.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "source_record_ref": source_ref,
        "input_schema_version": inputs.get("schema_version", "unknown"),
        "review_status": "preview_only_review_required",
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "mutates_source_cache": False,
        "mutates_evidence_ledger": False,
        "mutates_review_queue": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H13 review seed is a preview and not a review decision."],
    }


def _source_id(inputs: Mapping[str, Any]) -> str:
    source_id = str(inputs.get("source_id") or "")
    if source_id in H13_SOURCE_CONFIGS:
        return source_id
    nested = inputs.get("normalized_record")
    if isinstance(nested, Mapping) and nested.get("source_id") in H13_SOURCE_CONFIGS:
        return str(nested.get("source_id"))
    return "unknown"


def _first_ref(inputs: Mapping[str, Any], nested_key: str, *id_keys: str) -> str:
    nested = inputs.get(nested_key)
    if isinstance(nested, Mapping):
        for key in id_keys:
            value = nested.get(key)
            if value:
                return str(value)
    for key in ("fixture_replay_result_id", "boundary_dry_run_result_id", "normalized_record_ref", "fixture_ref"):
        if inputs.get(key):
            return str(inputs[key])
    return f"h13.{nested_key}.{_source_id(inputs)}.preview"


def _limitations(inputs: Mapping[str, Any]) -> list[str]:
    values = inputs.get("limitations")
    if isinstance(values, list):
        return [str(value) for value in values]
    return ["Input carries no additional limitations beyond H13 no-access/no-truth policy."]


def _best_inputs_by_source(outputs: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    by_source: dict[str, Mapping[str, Any]] = {}
    for item in outputs:
        source_id = _source_id(item)
        if source_id not in H13_SOURCE_CONFIGS:
            continue
        if source_id not in by_source or _score_input(item) > _score_input(by_source[source_id]):
            by_source[source_id] = item
    return by_source


def _score_input(item: Mapping[str, Any]) -> int:
    if _is_boundary_output(item):
        return 3
    if _is_fixture_output(item):
        return 2
    return 1


def _is_fixture_output(item: Mapping[str, Any]) -> bool:
    return item.get("schema_version") == "h13_local_private_fixture_replay_result.v0" or item.get("result_status") == "normalized_fixture"


def _is_boundary_output(item: Mapping[str, Any]) -> bool:
    return item.get("schema_version") == "h13_local_private_boundary_dry_run_result.v0"


def _blocked_sources(outputs: Sequence[Mapping[str, Any]]) -> list[str]:
    blocked = set()
    for item in outputs:
        status = str(item.get("result_status") or "")
        if status.startswith("blocked_"):
            source_id = _source_id(item)
            if source_id in H13_SOURCE_CONFIGS:
                blocked.add(source_id)
    return sorted(blocked)


def _minimal_source_input(source_id: str) -> dict[str, Any]:
    config = H13_SOURCE_CONFIGS[source_id]
    return {
        "schema_version": "h13_minimal_review_source.v0",
        "source_id": source_id,
        "connector_family": config["connector_family"],
        "limitations": ["Source represented by H13 policy/fixture-equivalent review integration only."],
    }


def _public_safe_input_ref(value: Any) -> str:
    text = str(value).replace("\\", "/")
    marker = "examples/connectors/h13_local_private/"
    if marker in text:
        return marker + text.split(marker, 1)[1]
    audit_marker = "control/audits/h13-"
    if audit_marker in text:
        return audit_marker + text.split(audit_marker, 1)[1]
    return Path(text).name or "h13_input_ref_redacted"


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_TRUTH_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_PRODUCT_TRUE_KEYS}


def _raise_if_boundaries_fail(value: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h13_review_truth_boundary_violations(value, policy) + detect_h13_review_product_boundary_violations(value, policy) + detect_h13_review_private_data_violations(value, policy)
    if errors:
        raise ValueError("; ".join(errors))


def _collect_true_keys(value: Any, forbidden: set[str], prefix: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, inner in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in forbidden and inner is True:
                errors.append(f"{path}=true")
            _collect_true_keys(inner, forbidden, path, errors)
    elif isinstance(value, list):
        for index, inner in enumerate(value):
            _collect_true_keys(inner, forbidden, f"{prefix}[{index}]", errors)


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
