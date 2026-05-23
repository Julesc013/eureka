#!/usr/bin/env python3
"""Validate H13-BUNDLE-01 local/private policy packs offline."""

from __future__ import annotations

import argparse
from pathlib import Path
import json
import re
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_IDS = ['local_folder_metadata', 'local_archive_file_metadata', 'local_removable_media_metadata', 'local_disk_image_metadata', 'local_package_cache_metadata', 'private_nas_metadata_boundary', 'private_object_store_metadata_boundary', 'institutional_private_collection_boundary', 'user_supplied_url_metadata_boundary', 'user_owned_authenticated_source_boundary', 'restricted_source_manifest_only', 'rights_sensitive_source_policy_blocked']
SOURCE_FILES = {source_id: f"{source_id}_source_v2.json" for source_id in SOURCE_IDS}
POLICY_FILES_BY_SOURCE = {'local_folder_metadata': 'local_folder_metadata_policy_pack_v0.json', 'local_archive_file_metadata': 'local_archive_file_metadata_policy_pack_v0.json', 'local_removable_media_metadata': 'local_removable_media_metadata_policy_pack_v0.json', 'local_disk_image_metadata': 'local_disk_image_metadata_policy_pack_v0.json', 'local_package_cache_metadata': 'local_package_cache_metadata_policy_pack_v0.json', 'private_nas_metadata_boundary': 'private_nas_metadata_boundary_policy_pack_v0.json', 'private_object_store_metadata_boundary': 'private_object_store_metadata_boundary_policy_pack_v0.json', 'institutional_private_collection_boundary': 'institutional_private_collection_boundary_policy_pack_v0.json', 'user_supplied_url_metadata_boundary': 'user_supplied_url_metadata_boundary_policy_pack_v0.json', 'user_owned_authenticated_source_boundary': 'user_owned_authenticated_source_boundary_policy_pack_v0.json', 'restricted_source_manifest_only': 'restricted_source_manifest_only_policy_pack_v0.json', 'rights_sensitive_source_policy_blocked': 'rights_sensitive_source_policy_blocked_pack_v0.json'}
INVENTORY_FILES = (
    "control/inventory/source_packs/h13_local_private_source_pack_policy.json",
    "control/inventory/source_packs/h13_local_private_sources.json",
    "control/inventory/source_packs/h13_local_private_connector_families.json",
    "control/inventory/source_packs/h13_local_source_identity_policy.json",
    "control/inventory/source_packs/h13_private_source_boundary_policy.json",
    "control/inventory/source_packs/h13_user_supplied_url_policy.json",
    "control/inventory/source_packs/h13_authenticated_source_boundary_policy.json",
    "control/inventory/source_packs/h13_restricted_source_manifest_policy.json",
    "control/inventory/source_packs/h13_local_cas_import_boundary_policy.json",
    "control/inventory/source_packs/h13_pack_export_import_boundary_policy.json",
    "control/inventory/source_packs/h13_privacy_redaction_policy.json",
    "control/inventory/source_packs/h13_local_private_rights_safety_policy.json",
    "control/inventory/source_packs/h13_local_private_approval_gates.json",
    "control/inventory/source_packs/h13_local_private_output_policy.json",
    "control/inventory/source_packs/h13_local_private_truth_policy.json",
    "control/inventory/source_packs/h13_local_private_no_access_policy.json",
    "control/inventory/source_packs/h13_local_private_no_import_export_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/packs/source/h13_local_private_source_pack_manifest_v0.json",
    "examples/packs/source/h13_local_private_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/connectors/h13_local_private/coverage/h13_local_private_coverage_preview_v0.json",
    "examples/connectors/h13_local_private/scorecards/h13_local_private_scorecard_preview_v0.json",
)
DOCS = (
    "docs/reference/H13_LOCAL_PRIVATE_SOURCE_PACKS.md",
    "docs/reference/H13_LOCAL_SOURCE_IDENTITY_POLICY.md",
    "docs/reference/H13_PRIVATE_SOURCE_BOUNDARY_POLICY.md",
    "docs/reference/H13_USER_SUPPLIED_URL_POLICY.md",
    "docs/reference/H13_AUTHENTICATED_SOURCE_BOUNDARY_POLICY.md",
    "docs/reference/H13_RESTRICTED_SOURCE_MANIFEST_POLICY.md",
    "docs/reference/H13_LOCAL_CAS_IMPORT_BOUNDARY_POLICY.md",
    "docs/reference/H13_PACK_EXPORT_IMPORT_BOUNDARY_POLICY.md",
    "docs/reference/H13_PRIVACY_REDACTION_POLICY.md",
    "docs/reference/H13_LOCAL_PRIVATE_RIGHTS_SAFETY_POLICY.md",
    "docs/architecture/H13_LOCAL_PRIVATE_SOURCE_MODEL.md",
    "docs/architecture/LOCAL_PRIVATE_SOURCE_FAMILY_MODEL.md",
    "docs/operations/H13_LOCAL_PRIVATE_POLICY_GATES.md",
    "docs/operations/H13_LOCAL_PRIVATE_NO_ACCESS_POLICY.md",
    "docs/operations/H13_LOCAL_PRIVATE_NO_IMPORT_EXPORT_POLICY.md",
    "docs/operations/H13_LOCAL_PRIVATE_FIXTURE_PLAN.md",
)
AUDIT_FILES = tuple(
    f"control/audits/h13-bundle-01-local-private-policy-packs-v0/{name}"
    for name in (
        "README.md",
        "h13_bundle_01_report.json",
        "h13_source_pack_summary.md",
        "h13_source_policy_gate_summary.md",
        "h13_connector_family_summary.md",
        "h13_local_source_identity_policy_summary.md",
        "h13_private_source_boundary_policy_summary.md",
        "h13_user_supplied_url_policy_summary.md",
        "h13_authenticated_source_boundary_policy_summary.md",
        "h13_restricted_source_manifest_policy_summary.md",
        "h13_local_cas_import_boundary_policy_summary.md",
        "h13_pack_export_import_boundary_policy_summary.md",
        "h13_privacy_redaction_policy_summary.md",
        "h13_local_private_rights_safety_policy_summary.md",
        "h13_fixture_plan.md",
        "h13_no_access_report.md",
        "h13_no_import_export_report.md",
        "h13_readiness_for_fixture_runtime.md",
        "validation.md",
        "generated/sample_h13_source_summary.json",
        "generated/sample_h13_source_summary.md",
        "generated/sample_h13_option_matrix.json",
    )
)
H13_PYTHON_FILES = (
    "scripts/validate_h13_local_private_policy_packs.py",
    "scripts/summarize_h13_local_private_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = set(['inspect_fixture', 'record_source_policy', 'record_source_boundary', 'record_privacy_redaction_policy', 'record_rights_safety_policy', 'create_coverage_preview', 'create_scorecard_preview'])
FALSE_REQUIRED_KEYS = set(['local_access_enabled', 'private_source_access_enabled', 'user_supplied_url_access_enabled', 'authenticated_source_access_enabled', 'restricted_source_access_enabled', 'live_access_enabled', 'source_sync_enabled', 'connector_runtime_enabled', 'approved_probe_enabled', 'filesystem_scan_enabled', 'directory_listing_enabled', 'archive_listing_enabled', 'removable_media_access_enabled', 'disk_image_access_enabled', 'package_cache_access_enabled', 'private_nas_access_enabled', 'object_store_access_enabled', 'account_access_enabled', 'credential_handling_enabled', 'url_fetch_enabled', 'local_cas_import_enabled', 'CAS_import_enabled', 'cas_import_enabled', 'pack_export_enabled', 'pack_import_enabled', 'file_hashing_enabled', 'fingerprinting_enabled', 'malware_scanning_enabled', 'extraction_enabled', 'execution_enabled', 'acquisition_action_enabled', 'upload_enabled', 'public_share_enabled', 'source_pack_import_enabled'])
FORBIDDEN_TRUE_KEYS = FALSE_REQUIRED_KEYS | set(['source_pack_is_truth', 'source_pack_is_accepted_evidence', 'source_pack_is_imported_state', 'policy_pack_grants_access', 'capability_grants_permission', 'coverage_preview_is_exhaustive', 'coverage_manifest_is_exhaustive_global_coverage', 'scorecard_preview_is_production_ready', 'local_source_identity_is_source_truth', 'private_source_boundary_is_access_permission', 'user_supplied_url_is_fetch_permission', 'authenticated_source_boundary_is_account_permission', 'restricted_source_manifest_grants_access_permission', 'CAS_import_candidate_is_import_permission', 'cas_import_candidate_is_import_permission', 'pack_export_import_candidate_is_export_import_permission', 'redaction_policy_proves_public_safety', 'rights_safety_metadata_is_rights_or_safety_truth', 'rights_safety_candidate_is_rights_or_safety_truth', 'declared_ownership_is_rights_clearance', 'public_index_mutation_allowed', 'master_index_mutation_allowed', 'public_index_mutated', 'master_index_mutated', 'mutated_public_index', 'mutated_master_index', 'accepted_local_source_identity_truth', 'accepted_private_source_truth', 'accepted_user_supplied_url_truth', 'accepted_authenticated_source_truth', 'accepted_restricted_source_truth', 'accepted_CAS_import_truth', 'accepted_cas_import_truth', 'accepted_pack_export_import_truth', 'accepted_privacy_redaction_truth', 'accepted_rights_safety_truth', 'accepted_source_truth', 'accepted_evidence_truth', 'accepted_candidate_truth', 'accepted_public_record', 'rights_clearance_claimed', 'ownership_truth_claimed', 'user_authority_claimed', 'legal_access_claimed', 'publication_permission_claimed', 'privacy_safety_claimed', 'malware_safety_claimed', 'source_safety_claimed', 'verified_authenticity_claimed', 'production_readiness_claimed', 'ownership_truth', 'user_authority_truth', 'legal_access_truth', 'publication_permission_truth', 'privacy_safety', 'malware_safety', 'source_safety_truth', 'verified_authenticity', 'production_ready', 'auto_approves_future_connectors']) | set(['changed_public_search_behavior', 'enabled_hosting', 'enabled_local_access', 'enabled_private_access', 'enabled_url_fetch', 'enabled_account_access', 'enabled_restricted_access', 'enabled_source_sync', 'enabled_cas_import', 'enabled_pack_export_import', 'enabled_extraction', 'enabled_execution', 'enabled_acquisition_actions', 'enabled_uploads', 'enabled_telemetry', 'mutated_public_index', 'mutated_master_index', 'network_calls_made', 'api_calls_made', 'model_provider_calls_made'])
SECRET_KEY_NAMES = {"api_key", "api_token", "access_token", "auth_token", "client_secret", "password", "private_key", "cookie", "session_cookie", "credential", "token"}
PAYLOAD_KEY_RE = re.compile(r"(private_file_payload|local_file_payload|file_content|private_source_payload|account_data|cas_blob|exported_pack|imported_pack|source_cache_write|public_index_write|master_index_write|credential_payload|token_payload|cookie_payload|session_payload)", re.IGNORECASE)
UNREDACTED_PATH_RE = re.compile(r"([A-Za-z]:\\|/Users/|/home/|file://|\\\\)")
BANNED_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON validation result.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H13 local/private policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"][:50]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required = list(INVENTORY_FILES) + list(SOURCE_PACK_EXAMPLES) + list(EXTRA_EXAMPLES) + list(DOCS) + list(AUDIT_FILES) + list(H13_PYTHON_FILES)
    required.extend(f"examples/sources/source_records/{SOURCE_FILES[source_id]}" for source_id in SOURCE_IDS)
    required.extend(f"examples/connectors/h13_local_private/policies/{POLICY_FILES_BY_SOURCE[source_id]}" for source_id in SOURCE_IDS)
    for rel in required:
        if not (repo_root / rel).exists():
            errors.append(f"missing required file: {rel}")
    known = _load_known_values(repo_root, errors)
    for rel in required:
        path = repo_root / rel
        if rel.endswith(".json") and path.exists():
            try:
                payload = _load_json(path)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"invalid JSON in {rel}: {exc}")
                continue
            _scan_forbidden_true(rel, payload, errors)
            _scan_json_payload(rel, payload, errors)
    inventory = _load_json(repo_root / "control/inventory/source_packs/h13_local_private_sources.json")
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        errors.append("source inventory must contain sources list")
    else:
        ids = [item.get("source_id") for item in sources if isinstance(item, Mapping)]
        if len(ids) != len(set(ids)):
            errors.append("source IDs must be unique")
        if set(ids) != set(SOURCE_IDS):
            errors.append("source inventory IDs must match H13 source list")
        for item in sources:
            if isinstance(item, Mapping):
                errors.extend(validate_source_record(str(item.get("source_id")), item, known))
    for source_id in SOURCE_IDS:
        path = repo_root / f"examples/sources/source_records/{SOURCE_FILES[source_id]}"
        if path.exists():
            errors.extend(validate_source_record(source_id, _load_json(path), known))
        pack_path = repo_root / f"examples/connectors/h13_local_private/policies/{POLICY_FILES_BY_SOURCE[source_id]}"
        if pack_path.exists():
            errors.extend(validate_policy_pack(source_id, _load_json(pack_path)))
    coverage = repo_root / "examples/connectors/h13_local_private/coverage/h13_local_private_coverage_preview_v0.json"
    if coverage.exists():
        errors.extend(validate_coverage_preview(_load_json(coverage)))
    scorecard = repo_root / "examples/connectors/h13_local_private/scorecards/h13_local_private_scorecard_preview_v0.json"
    if scorecard.exists():
        errors.extend(validate_scorecard_preview(_load_json(scorecard)))
    _validate_python_files(repo_root, errors)
    _validate_no_private_roots(repo_root, errors)
    return {
        "schema_version": "h13_local_private_policy_pack_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H13-BUNDLE-01",
        "source_count": len(SOURCE_IDS),
        "network_calls_made": False,
        "local_private_access_made": False,
        "errors": errors,
    }


def validate_source_record(source_id: str, record: Mapping[str, Any], known: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if source_id not in SOURCE_IDS or record.get("source_id") != source_id:
        errors.append(f"{source_id}: source_id mismatch or unknown")
    if record.get("source_family") != "local_private_user_supplied_source":
        errors.append(f"{source_id}: source_family must be local_private_user_supplied_source")
    if record.get("connector_family") not in known.get("connector_families", set()):
        errors.append(f"{source_id}: connector family is not in H13 connector family inventory")
    if record.get("trust_lane") not in {'user_supplied', 'policy_blocked', 'restricted_manifest_only', 'local_private'}:
        errors.append(f"{source_id}: invalid trust lane")
    if record.get("current_index_depth") != "D0_source_known":
        errors.append(f"{source_id}: current_index_depth must be D0_source_known")
    if record.get("current_access_mode") not in {"no_access", "committed_fixture_only"}:
        errors.append(f"{source_id}: invalid current_access_mode")
    _scan_forbidden_true(source_id, record, errors)
    _scan_json_payload(source_id, record, errors)
    return errors


def validate_policy_pack(source_id: str, pack: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if pack.get("source_id") != source_id:
        errors.append(f"{source_id}: policy pack source_id mismatch")
    if pack.get("policy_pack_grants_access") is not False:
        errors.append(f"{source_id}: policy pack must not grant access")
    allowed = set(pack.get("allowed_current_operations") or [])
    if not allowed <= ALLOWED_CURRENT_OPERATIONS:
        errors.append(f"{source_id}: allowed_current_operations include forbidden operations")
    for operation in ("local_filesystem_access", "private_source_access", "user_supplied_url_fetch", "authenticated_account_access", "restricted_source_access", "local_cas_import", "pack_export", "pack_import"):
        if operation not in pack.get("forbidden_current_operations", []):
            errors.append(f"{source_id}: missing forbidden operation {operation}")
    _scan_forbidden_true(source_id, pack, errors)
    _scan_json_payload(source_id, pack, errors)
    return errors


def validate_coverage_preview(coverage: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if coverage.get("coverage_basis") != "policy_pack_only":
        errors.append("coverage preview must be policy_pack_only")
    if coverage.get("coverage_manifest_is_exhaustive_global_coverage") is not False:
        errors.append("coverage preview must not claim exhaustive coverage")
    for key in ("local_access_enabled", "private_access_enabled"):
        if coverage.get(key) is True:
            errors.append(f"coverage preview must keep {key} false")
    for key in ("url_fetches_performed", "authenticated_accesses_performed", "filesystem_scans_performed", "directory_listings_performed", "archive_listings_performed", "CAS_imports_performed", "pack_exports_performed", "pack_imports_performed", "source_cache_writes_performed", "public_index_writes_performed"):
        if coverage.get(key) not in (0, None):
            errors.append(f"coverage preview must keep {key} at 0")
    _scan_forbidden_true("coverage", coverage, errors)
    return errors


def validate_scorecard_preview(scorecard: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if scorecard.get("production_ready") is not False:
        errors.append("scorecard must not claim production readiness")
    if scorecard.get("auto_approves_future_connectors") is not False:
        errors.append("scorecard must not auto-approve future connectors")
    if scorecard.get("access_envelope_status") != "not_approved":
        errors.append("scorecard access envelope must be not_approved")
    _scan_forbidden_true("scorecard", scorecard, errors)
    return errors


def _load_known_values(repo_root: Path, errors: list[str]) -> dict[str, set[str]]:
    known = {"connector_families": set(), "source_ids": set(SOURCE_IDS)}
    path = repo_root / "control/inventory/source_packs/h13_local_private_connector_families.json"
    if path.exists():
        payload = _load_json(path)
        for item in payload.get("connector_families", []):
            if isinstance(item, Mapping) and item.get("connector_family"):
                known["connector_families"].add(str(item["connector_family"]))
    return known


def _scan_forbidden_true(label: str, payload: Any, errors: list[str]) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if str(key) in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{label}: forbidden true claim {key}")
            _scan_forbidden_true(label, value, errors)
    elif isinstance(payload, list):
        for item in payload:
            _scan_forbidden_true(label, item, errors)


def _scan_json_payload(label: str, payload: Any, errors: list[str]) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key)
            if key_text in SECRET_KEY_NAMES or PAYLOAD_KEY_RE.fullmatch(key_text):
                errors.append(f"{label}: forbidden private/credential/payload key {key_text}")
            _scan_json_payload(label, value, errors)
    elif isinstance(payload, list):
        for item in payload:
            _scan_json_payload(label, item, errors)
    elif isinstance(payload, str):
        if UNREDACTED_PATH_RE.search(payload):
            errors.append(f"{label}: unrestricted local/private path or URL-like locator must be redacted")


def _validate_python_files(repo_root: Path, errors: list[str]) -> None:
    for rel in H13_PYTHON_FILES:
        path = repo_root / rel
        if path.exists() and BANNED_IMPORT_RE.search(path.read_text(encoding="utf-8")):
            errors.append(f"{rel}: imports network/model/provider/browser library")


def _validate_no_private_roots(repo_root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "local_sources", "local_source_roots", "cas", "cas_store", "private_sources", "credential_store", "account_sessions", "import_staging", "export_staging", "archive_extractions"):
        if (repo_root / rel).exists():
            errors.append(f"local/private state root must not exist: {rel}")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
