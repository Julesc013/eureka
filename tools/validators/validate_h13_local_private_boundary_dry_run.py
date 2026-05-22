#!/usr/bin/env python3
"""Validate H13 local/private boundary dry-run framework offline."""

from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h13_local_private.boundary_dry_run_common import H13_SOURCE_IDS, detect_h13_boundary_private_data_violations, detect_h13_boundary_product_boundary_violations, detect_h13_boundary_truth_boundary_violations, load_h13_local_private_boundary_policy_bundle, validate_h13_boundary_source_approval  # noqa: E402

CONTRACTS = ['contracts/control_schemas/previews/h13/connectors/local_private_boundary_dry_run_request.v0.json', 'contracts/control_schemas/previews/h13/connectors/local_private_boundary_dry_run_result.v0.json', 'contracts/control_schemas/previews/h13/connectors/local_private_boundary_dry_run_output_bundle.v0.json', 'contracts/control_schemas/previews/h13/connectors/local_private_boundary_health_summary.v0.json']
POLICIES = ['control/inventory/connectors/h13_local_private_boundary_dry_run_policy.json', 'control/inventory/connectors/h13_local_private_boundary_dry_run_allowed_requests.json', 'control/inventory/connectors/h13_local_private_boundary_operation_policy.json', 'control/inventory/connectors/h13_local_private_boundary_kill_switch_policy.json', 'control/inventory/connectors/h13_local_private_boundary_output_policy.json', 'control/inventory/connectors/h13_local_private_boundary_path_policy.json', 'control/inventory/connectors/h13_local_private_boundary_review_policy.json', 'control/inventory/connectors/h13_local_private_boundary_truth_policy.json', 'control/inventory/connectors/h13_local_private_boundary_no_access_policy.json', 'control/inventory/connectors/h13_local_private_boundary_no_import_export_policy.json', 'control/inventory/connectors/h13_local_private_boundary_private_data_policy.json']
DOCS = ['docs/reference/H13_LOCAL_PRIVATE_BOUNDARY_DRY_RUN.md', 'docs/reference/H13_LOCAL_PRIVATE_BOUNDARY_DRY_RUN_RESULT.md', 'docs/reference/H13_LOCAL_PRIVATE_BOUNDARY_HEALTH_SUMMARY.md', 'docs/architecture/H13_LOCAL_PRIVATE_BOUNDARY_DRY_RUN_MODEL.md', 'docs/operations/H13_LOCAL_PRIVATE_BOUNDARY_DRY_RUN_APPROVAL_GATES.md', 'docs/operations/H13_LOCAL_PRIVATE_BOUNDARY_DRY_RUN_REVIEW.md', 'docs/operations/H13_LOCAL_PRIVATE_BOUNDARY_DRY_RUN_BLOCKED_MODE.md', 'docs/operations/H13_LOCAL_PRIVATE_BOUNDARY_DRY_RUN_NO_ACCESS_POLICY.md', 'docs/operations/H13_LOCAL_PRIVATE_BOUNDARY_DRY_RUN_NO_IMPORT_EXPORT_POLICY.md', 'docs/operations/H13_LOCAL_PRIVATE_BOUNDARY_DRY_RUN_PRIVATE_DATA_POLICY.md']
AUDIT_DIR = Path("control/audits/h13-bundle-03-local-private-boundary-dry-runs-v0")
AUDIT_FILES = ['README.md', 'h13_bundle_03_report.json', 'boundary_dry_run_policy_review.md', 'boundary_dry_run_execution_report.md', 'local_source_identity_candidate_preview.md', 'private_source_boundary_candidate_preview.md', 'user_supplied_url_boundary_candidate_preview.md', 'authenticated_source_boundary_candidate_preview.md', 'restricted_source_manifest_candidate_preview.md', 'local_cas_import_boundary_candidate_preview.md', 'pack_export_import_boundary_candidate_preview.md', 'privacy_redaction_candidate_preview.md', 'local_private_rights_safety_candidate_preview.md', 'source_cache_candidate_preview.md', 'evidence_candidate_preview.md', 'review_queue_seed_preview.md', 'boundary_health_summary.md', 'no_access_report.md', 'no_import_export_report.md', 'private_data_policy_report.md', 'h13_boundary_dry_run_blocked_or_completed_summary.md', 'validation.md', 'generated/sample_h13_boundary_dry_run_result.json', 'generated/sample_h13_local_source_identity_candidate_from_boundary.json', 'generated/sample_h13_private_source_boundary_candidate_from_boundary.json', 'generated/sample_h13_user_supplied_url_boundary_candidate_from_boundary.json', 'generated/sample_h13_authenticated_source_boundary_candidate_from_boundary.json', 'generated/sample_h13_restricted_source_manifest_candidate_from_boundary.json', 'generated/sample_h13_local_cas_import_boundary_candidate_from_boundary.json', 'generated/sample_h13_pack_export_import_boundary_candidate_from_boundary.json', 'generated/sample_h13_privacy_redaction_candidate_from_boundary.json', 'generated/sample_h13_local_private_rights_safety_candidate_from_boundary.json', 'generated/sample_h13_source_cache_candidate_from_boundary.json', 'generated/sample_h13_evidence_candidate_preview_from_boundary.json', 'generated/sample_h13_review_queue_seed_from_boundary.json', 'generated/sample_h13_boundary_health_summary.json', 'generated/sample_h13_boundary_dry_run_summary.md']
PYTHON_FILES = ["archive/prototypes/legacy_runtime/connectors/h13_local_private/boundary_dry_run_common.py"] + [f"archive/prototypes/legacy_runtime/connectors/h13_local_private/boundary_dry_run_{source_id}.py" for source_id in H13_SOURCE_IDS] + [
    "scripts/run_h13_local_private_boundary_dry_run.py",
    "scripts/validate_h13_local_private_boundary_dry_run.py",
    "scripts/summarize_h13_local_private_boundary_outputs.py",
]
BANNED_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|urllib|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)
SECRET_KEY_RE = re.compile(r"(^|_)(api_key|api_token|access_token|auth_token|client_secret|password|private_key|cookie|session_cookie|credential|token|receipt|license_key|entitlement)($|_)", re.IGNORECASE)
PRIVATE_PAYLOAD_KEY_RE = re.compile(r"(private_file_payload|local_file_content|account_payload|cas_blob|exported_pack|imported_pack|source_cache_write|evidence_write|public_index_write|master_index_write)", re.IGNORECASE)
UNREDACTED_LOCATOR_RE = re.compile(r"(https?://|file://|[A-Za-z]:\\|\\\\|/Users/|/home/|/Volumes/)")
FORBIDDEN_TRUE_KEYS = set(['accepted_CAS_import_truth', 'accepted_authenticated_source_truth', 'accepted_candidate_truth', 'accepted_cas_import_truth', 'accepted_evidence_truth', 'accepted_local_source_identity_truth', 'accepted_pack_export_import_truth', 'accepted_privacy_redaction_truth', 'accepted_private_source_truth', 'accepted_public_record', 'accepted_restricted_source_truth', 'accepted_rights_safety_truth', 'accepted_source_truth', 'accepted_user_supplied_url_truth', 'account_access_approved', 'account_access_requested', 'account_access_used', 'acquisition_action_approved', 'acquisition_action_requested', 'acquisition_action_used', 'api_calls_made', 'archive_listing_approved', 'archive_listing_performed', 'archive_listing_requested', 'archive_listing_used', 'authenticated_access_used', 'authenticated_source_access_approved', 'authenticated_source_access_requested', 'authenticated_source_boundary_candidate_is_account_permission', 'authenticated_source_candidate_is_account_permission', 'boundary_dry_run_result_is_public_truth', 'cas_import_candidate_is_import_permission', 'cas_import_performed', 'cas_import_used', 'changed_public_search_behavior', 'credential_handling_approved', 'credential_handling_requested', 'credential_handling_used', 'credential_or_token_output_approved', 'directory_listing_approved', 'directory_listing_performed', 'directory_listing_requested', 'directory_listing_used', 'disk_image_access_approved', 'disk_image_access_requested', 'enabled_account_access', 'enabled_acquisition_actions', 'enabled_cas_import', 'enabled_execution', 'enabled_extraction', 'enabled_hosting', 'enabled_local_access', 'enabled_pack_export_import', 'enabled_private_access', 'enabled_restricted_access', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'enabled_url_fetch', 'evidence_candidate_preview_is_accepted_evidence', 'evidence_preview_is_accepted_evidence', 'evidence_write_approved', 'evidence_write_performed', 'evidence_write_requested', 'execution_approved', 'execution_requested', 'execution_used', 'external_api_approved', 'external_api_requested', 'external_api_used', 'extraction_approved', 'extraction_requested', 'extraction_used', 'file_hashing_approved', 'file_hashing_requested', 'file_hashing_used', 'filesystem_scan_approved', 'filesystem_scan_performed', 'filesystem_scan_requested', 'filesystem_scan_used', 'fingerprinting_approved', 'fingerprinting_requested', 'fingerprinting_used', 'legal_access_claimed', 'local_access_approved', 'local_access_requested', 'local_access_used', 'local_cas_import_approved', 'local_cas_import_boundary_candidate_is_import_permission', 'local_cas_import_requested', 'local_private_rights_safety_candidate_is_rights_or_safety_truth', 'local_source_identity_candidate_is_truth', 'malware_safety_claimed', 'malware_scanning_approved', 'malware_scanning_requested', 'malware_scanning_used', 'master_index_mutated', 'master_index_write_approved', 'master_index_write_performed', 'model_provider_approved', 'model_provider_calls_made', 'model_provider_requested', 'model_provider_used', 'mutated_master_index', 'mutated_public_index', 'network_access_approved', 'network_access_requested', 'network_calls_made', 'network_used', 'normalized_record_is_public_truth', 'object_store_access_approved', 'object_store_access_requested', 'ownership_truth_claimed', 'pack_export_approved', 'pack_export_import_boundary_candidate_is_export_import_permission', 'pack_export_import_candidate_is_export_import_permission', 'pack_export_import_used', 'pack_export_performed', 'pack_export_requested', 'pack_import_approved', 'pack_import_performed', 'pack_import_requested', 'package_cache_access_approved', 'package_cache_access_requested', 'privacy_redaction_candidate_proves_public_safety', 'privacy_safety_claimed', 'private_nas_access_approved', 'private_nas_access_requested', 'private_payload_output_approved', 'private_source_access_approved', 'private_source_access_requested', 'private_source_access_used', 'private_source_boundary_candidate_is_access_permission', 'production_readiness_claimed', 'public_index_mutated', 'public_index_write_approved', 'public_index_write_performed', 'public_index_write_requested', 'public_share_approved', 'public_share_requested', 'publication_permission_claimed', 'publication_used', 'removable_media_access_approved', 'removable_media_access_requested', 'restricted_source_access_approved', 'restricted_source_access_requested', 'restricted_source_access_used', 'restricted_source_manifest_candidate_grants_access_permission', 'restricted_source_manifest_grants_access_permission', 'review_queue_write_approved', 'review_queue_write_requested', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'rights_safety_candidate_is_rights_or_safety_truth', 'source_cache_candidate_is_accepted_source', 'source_cache_preview_is_accepted_source', 'source_cache_write_approved', 'source_cache_write_performed', 'source_cache_write_requested', 'source_safety_claimed', 'unrestricted_local_path_output_approved', 'upload_approved', 'upload_requested', 'upload_used', 'user_authority_claimed', 'user_supplied_url_boundary_candidate_is_fetch_permission', 'user_supplied_url_candidate_is_fetch_permission', 'user_supplied_url_fetch_approved', 'user_supplied_url_fetch_requested', 'user_supplied_url_fetch_used', 'verified_authenticity_claimed'])
ALLOWED_TRUE_KEYS = {"boundary_dry_run_only", "default_offline_preflight", "dry_run_requires_committed_approval", "review_required_before_local_access", "review_required_before_private_access", "review_required_before_user_supplied_url_fetch", "review_required_before_authenticated_access", "review_required_before_restricted_source_access", "review_required_before_cas_import", "review_required_before_pack_export_import", "review_required_before_source_cache_persistence", "review_required_before_evidence_acceptance", "review_required_before_candidate_acceptance", "review_required_before_public_index_use", "review_required_before_master_index", "kill_switch_defaults_fail_closed", "no_local_filesystem_access", "no_private_source_access", "no_user_supplied_url_fetch", "no_authenticated_access", "no_restricted_source_access", "no_network_calls", "no_api_calls", "no_model_provider_calls", "no_filesystem_scan", "no_directory_listing", "no_archive_listing", "no_account_access", "no_credential_token_session_cookie_handling", "manifest_only_allowed_candidate", "review_required", "privacy_review_required", "fixture_equivalent_outputs_sufficient"}


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads: dict[str, Mapping[str, Any]] = {}
    for rel in CONTRACTS + POLICIES:
        payload = _load_json(root / rel, errors)
        if isinstance(payload, Mapping):
            payloads[rel] = payload
    for rel in DOCS + PYTHON_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    for name in AUDIT_FILES:
        if not (root / AUDIT_DIR / name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / name).as_posix()}")
    _validate_policies(payloads, errors)
    _validate_examples(root, errors)
    _validate_runtime_imports(errors)
    _scan_python_safety(root, errors)
    _run_check([sys.executable, "scripts/run_h13_local_private_boundary_dry_run.py", "--source-id", "local_folder_metadata", "--request-key", "example_local_source_boundary", "--check"], root, errors)
    _run_check([sys.executable, "scripts/summarize_h13_local_private_boundary_outputs.py", "--input", "examples/connectors/h13_local_private/boundary_dry_run_results", "--check"], root, errors)
    _check_forbidden_output_roots(root, errors)
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "local_sources", "cas_roots", "private_sources", "credential_directories", "user_url_fetches", "accounts", "import_export_staging", "pack_exports", "pack_imports", "archive_extractions"):
        if (root / rel).exists():
            errors.append(f"forbidden local private root exists: {rel}")
    return {
        "schema_version": "h13_local_private_boundary_dry_run_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(H13_SOURCE_IDS),
        "offline_default": True,
        "local_private_access_used": False,
        "network_calls_made": False,
        "cas_import_pack_export_publication_used": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    result = validate_repo()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "valid" else 1


def _validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    global_policy = payloads.get("control/inventory/connectors/h13_local_private_boundary_dry_run_policy.json", {})
    for key, value in global_policy.items():
        if key.endswith("_enabled") and value is not False:
            errors.append(f"global policy {key} must be false")
    if global_policy.get("allowed_operation_scope") != "boundary_dry_run_only":
        errors.append("global policy must be boundary_dry_run_only")
    allowed = payloads.get("control/inventory/connectors/h13_local_private_boundary_dry_run_allowed_requests.json", {})
    sources = allowed.get("sources", [])
    if sorted(item.get("source_id") for item in sources if isinstance(item, Mapping)) != sorted(H13_SOURCE_IDS):
        errors.append("allowed request policy must list all H13 sources")
    bundle = load_h13_local_private_boundary_policy_bundle(REPO_ROOT)
    for item in sources:
        if not isinstance(item, Mapping):
            errors.append("allowed source entry must be object")
            continue
        source_id = str(item.get("source_id"))
        if item.get("approval_status") != "not_approved_for_boundary_dry_run":
            errors.append(f"{source_id}: approval_status must remain not_approved_for_boundary_dry_run")
        if item.get("allowed_request_keys") not in ([], None):
            errors.append(f"{source_id}: allowed_request_keys must stay empty without approval")
        if item.get("boundary_dry_run_approved") is not False:
            errors.append(f"{source_id}: boundary_dry_run_approved must be false")
        for key in ['local_access_approved', 'private_source_access_approved', 'user_supplied_url_fetch_approved', 'authenticated_source_access_approved', 'restricted_source_access_approved', 'network_access_approved', 'external_api_approved', 'model_provider_approved', 'filesystem_scan_approved', 'directory_listing_approved', 'archive_listing_approved', 'removable_media_access_approved', 'disk_image_access_approved', 'package_cache_access_approved', 'private_nas_access_approved', 'object_store_access_approved', 'account_access_approved', 'credential_handling_approved', 'local_cas_import_approved', 'pack_export_approved', 'pack_import_approved', 'file_hashing_approved', 'fingerprinting_approved', 'malware_scanning_approved', 'extraction_approved', 'execution_approved', 'acquisition_action_approved', 'upload_approved', 'public_share_approved', 'source_cache_write_approved', 'evidence_write_approved', 'review_queue_write_approved', 'public_index_write_approved', 'master_index_write_approved', 'unrestricted_local_path_output_approved', 'credential_or_token_output_approved', 'private_payload_output_approved']:
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        request_key = str((item.get("planned_request_keys") or [""])[0])
        if validate_h13_boundary_source_approval(source_id, request_key, bundle)["approved"]:
            errors.append(f"{source_id}: boundary approval unexpectedly passes")
    kill = payloads.get("control/inventory/connectors/h13_local_private_boundary_kill_switch_policy.json", {})
    if kill.get("kill_switch_defaults_fail_closed") is not True:
        errors.append("kill switch must default fail-closed")
    if kill.get("boundary_dry_run_kill_switch_enabled") is not True:
        errors.append("current kill switch must remain enabled without approval")


def _validate_examples(root: Path, errors: list[str]) -> None:
    required = [
        "examples/connectors/h13_local_private/boundary_dry_run/blocked_boundary_dry_run_request_v0.json",
        "examples/connectors/h13_local_private/boundary_dry_run_results/blocked_boundary_dry_run_result_v0.json",
        "examples/connectors/h13_local_private/boundary_dry_run_outputs/boundary_health_from_h13_boundary_v0.json",
    ]
    for rel in required:
        if not (root / rel).is_file():
            errors.append(f"missing boundary example: {rel}")
    for directory in ("examples/connectors/h13_local_private/boundary_dry_run", "examples/connectors/h13_local_private/boundary_dry_run_results", "examples/connectors/h13_local_private/boundary_dry_run_outputs", str(AUDIT_DIR / "generated")):
        path = root / directory
        if not path.exists():
            errors.append(f"missing example directory: {directory}")
            continue
        for json_path in path.rglob("*.json"):
            payload = _load_json(json_path, errors)
            _scan_json_boundaries(payload, json_path, errors)
            if isinstance(payload, Mapping):
                errors.extend(detect_h13_boundary_truth_boundary_violations(payload, {}))
                errors.extend(detect_h13_boundary_product_boundary_violations(payload, {}))
                errors.extend(detect_h13_boundary_private_data_violations(payload, {}))


def _validate_runtime_imports(errors: list[str]) -> None:
    importlib.import_module("archive.prototypes.legacy_runtime.connectors.h13_local_private.boundary_dry_run_common")
    for source_id in H13_SOURCE_IDS:
        importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h13_local_private.boundary_dry_run_{source_id}")


def _scan_python_safety(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"python file imports forbidden network/provider/browser library: {rel}")
        if re.search(r"\b(requests|httpx|aiohttp|openai|anthropic)\.", text):
            errors.append(f"python file appears to call forbidden client: {rel}")


def _scan_json_boundaries(value: Any, label: Path | str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_TRUE_KEYS and key_text not in ALLOWED_TRUE_KEYS and item is True:
                errors.append(f"{label} forbidden true value: {key_text}")
            if SECRET_KEY_RE.search(key_text) and item not in (False, None, "", "unknown", "blocked_current_no_credentials", "blocked_current_no_sessions", "not_evaluated_no_account_access"):
                errors.append(f"{label} forbidden secret/account key value: {key_text}")
            if PRIVATE_PAYLOAD_KEY_RE.search(key_text) and item not in (False, None, "", [], {}, "no_blob_present"):
                errors.append(f"{label} forbidden private payload key: {key_text}")
            _scan_json_boundaries(item, label, errors)
    elif isinstance(value, list):
        for item in value:
            _scan_json_boundaries(item, label, errors)
    elif isinstance(value, str):
        if UNREDACTED_LOCATOR_RE.search(value):
            errors.append(f"{label} unrestricted local path or URL-like locator must be redacted")


def _check_forbidden_output_roots(root: Path, errors: list[str]) -> None:
    checks = [
        [sys.executable, "scripts/run_h13_local_private_boundary_dry_run.py", "--source-id", "local_folder_metadata", "--request-key", "example_local_source_boundary", "--output", "site/dist/h13.json"],
        [sys.executable, "scripts/run_h13_local_private_boundary_dry_run.py", "--source-id", "local_folder_metadata", "--request-key", "example_local_source_boundary", "--output", "site/dist/data/public_index/h13.json"],
        [sys.executable, "scripts/run_h13_local_private_boundary_dry_run.py", "--source-id", "local_folder_metadata", "--request-key", "example_local_source_boundary", "--output", "cas_roots/h13.json"],
        [sys.executable, "scripts/run_h13_local_private_boundary_dry_run.py", "--source-id", "local_folder_metadata", "--request-key", "example_local_source_boundary", "--output", "credentials/h13.json"],
    ]
    for cmd in checks:
        proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode == 0:
            errors.append(f"forbidden output root was not rejected: {cmd[-1]}")


def _run_check(cmd: list[str], root: Path, errors: list[str]) -> None:
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        errors.append(f"command failed: {' '.join(cmd)} :: {proc.stdout} {proc.stderr}")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path}: {exc}")
        return {}


if __name__ == "__main__":
    raise SystemExit(main())
