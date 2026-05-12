#!/usr/bin/env python3
"""Validate H13 local/private fixture runtime artifacts offline."""

from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h13_local_private.fixture_loader import load_h13_local_private_fixture  # noqa: E402
from runtime.connectors.h13_local_private.normalizer_common import H13_FIXTURE_KINDS, H13_SOURCE_IDS, detect_h13_product_boundary_violations, detect_h13_secret_or_private_data_violations, detect_h13_truth_boundary_violations  # noqa: E402

CONTRACTS = ['control/schemas/fixtures/h13/connectors/local_private_fixture.v0.json', 'control/schemas/previews/h13/connectors/local_private_normalized_record.v0.json', 'control/schemas/previews/h13/connectors/local_source_identity_candidate.v0.json', 'control/schemas/previews/h13/connectors/private_source_boundary_candidate.v0.json', 'control/schemas/previews/h13/connectors/user_supplied_url_boundary_candidate.v0.json', 'control/schemas/previews/h13/connectors/authenticated_source_boundary_candidate.v0.json', 'control/schemas/previews/h13/connectors/restricted_source_manifest_candidate.v0.json', 'control/schemas/previews/h13/connectors/local_cas_import_boundary_candidate.v0.json', 'control/schemas/previews/h13/connectors/pack_export_import_boundary_candidate.v0.json', 'control/schemas/previews/h13/connectors/privacy_redaction_candidate.v0.json', 'control/schemas/previews/h13/connectors/local_private_rights_safety_candidate.v0.json', 'control/schemas/fixtures/h13/connectors/local_private_fixture_replay_result.v0.json']
POLICIES = ['control/inventory/connectors/h13_local_private_fixture_runtime_policy.json', 'control/inventory/connectors/h13_local_private_normalization_policy.json', 'control/inventory/connectors/h13_local_source_identity_mapping_policy.json', 'control/inventory/connectors/h13_private_source_boundary_mapping_policy.json', 'control/inventory/connectors/h13_user_supplied_url_boundary_mapping_policy.json', 'control/inventory/connectors/h13_authenticated_source_boundary_mapping_policy.json', 'control/inventory/connectors/h13_restricted_source_manifest_mapping_policy.json', 'control/inventory/connectors/h13_local_cas_import_boundary_mapping_policy.json', 'control/inventory/connectors/h13_pack_export_import_boundary_mapping_policy.json', 'control/inventory/connectors/h13_privacy_redaction_mapping_policy.json', 'control/inventory/connectors/h13_local_private_rights_safety_mapping_policy.json', 'control/inventory/connectors/h13_local_private_fixture_output_policy.json', 'control/inventory/connectors/h13_local_private_fixture_path_policy.json', 'control/inventory/connectors/h13_local_private_fixture_truth_policy.json', 'control/inventory/connectors/h13_local_private_source_cache_mapping_policy.json', 'control/inventory/connectors/h13_local_private_evidence_mapping_policy.json', 'control/inventory/connectors/h13_local_private_no_access_policy.json', 'control/inventory/connectors/h13_local_private_no_import_export_policy.json']
FIXTURE_FILES = {'minimal': 'minimal_record.json', 'local_source_identity': 'local_source_identity_record.json', 'private_source_boundary': 'private_source_boundary_record.json', 'user_supplied_url_boundary': 'user_supplied_url_boundary_record.json', 'authenticated_source_boundary': 'authenticated_source_boundary_record.json', 'restricted_source_manifest': 'restricted_source_manifest_record.json', 'local_cas_import_boundary': 'local_cas_import_boundary_record.json', 'pack_export_import_boundary': 'pack_export_import_boundary_record.json', 'privacy_redaction': 'privacy_redaction_record.json', 'rights_safety': 'rights_safety_record.json', 'policy_blocked': 'policy_blocked_record.json'}
EXAMPLES = ['examples/connectors/h13_local_private/identity/local_source_identity_candidate_v0.json', 'examples/connectors/h13_local_private/identity/private_source_boundary_candidate_v0.json', 'examples/connectors/h13_local_private/identity/user_supplied_url_boundary_candidate_v0.json', 'examples/connectors/h13_local_private/identity/authenticated_source_boundary_candidate_v0.json', 'examples/connectors/h13_local_private/identity/restricted_source_manifest_candidate_v0.json', 'examples/connectors/h13_local_private/identity/local_cas_import_boundary_candidate_v0.json', 'examples/connectors/h13_local_private/identity/pack_export_import_boundary_candidate_v0.json', 'examples/connectors/h13_local_private/identity/privacy_redaction_candidate_v0.json', 'examples/connectors/h13_local_private/identity/local_private_rights_safety_candidate_v0.json', 'examples/connectors/h13_local_private/identity/policy_blocked_identity_candidate_v0.json']
RUNTIME_DIR = "runtime/connectors/h13_local_private"
BANNED_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|urllib|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)
FORBIDDEN_TRUE_KEYS = {'credential_or_token_payload_included', 'enabled_execution', 'accepted_user_supplied_url_truth', 'filesystem_scan_performed', 'rights_clearance_claimed', 'authenticated_access_used', 'accepted_candidate_truth', 'cas_import_used', 'external_api_used', 'exported_pack_included', 'restricted_source_manifest_candidate_grants_access_permission', 'filesystem_scan_used', 'accepted_restricted_source_truth', 'execution_output_included', 'credential_handling_used', 'enabled_extraction', 'pack_export_import_boundary_candidate_is_export_import_permission', 'source_cache_preview_is_accepted_source', 'cas_import_candidate_is_import_permission', 'removable_media_accessed', 'publication_permission_claimed', 'directory_listing_performed', 'cas_blob_included', 'license_key_payload_included', 'publication_performed', 'source_cache_write_included', 'accepted_privacy_redaction_truth', 'declared_ownership_is_rights_clearance', 'local_file_content_included', 'authenticated_source_candidate_is_account_permission', 'local_access_used', 'extraction_used', 'normalized_record_is_public_truth', 'evidence_preview_is_accepted_evidence', 'malware_safety_claimed', 'master_index_write_included', 'restricted_source_manifest_grants_access_permission', 'user_supplied_url_fetch_used', 'private_nas_accessed', 'ownership_truth_claimed', 'package_cache_accessed', 'public_index_mutation_allowed', 'restricted_source_access_used', 'cookie_or_session_payload_included', 'enabled_hosting', 'object_store_accessed', 'acquisition_action_performed', 'accepted_authenticated_source_truth', 'pack_export_import_used', 'accepted_evidence_truth', 'enabled_account_access', 'master_index_mutated', 'model_provider_calls_made', 'enabled_source_sync', 'enabled_url_fetch', 'accepted_pack_export_import_truth', 'account_payload_included', 'archive_listing_performed', 'malware_scanning_used', 'enabled_uploads', 'receipt_payload_included', 'accepted_local_source_identity_truth', 'local_cas_import_boundary_candidate_is_import_permission', 'accepted_rights_safety_truth', 'enabled_pack_export_import', 'authenticated_source_boundary_candidate_is_account_permission', 'accepted_cas_import_truth', 'publication_used', 'public_index_mutated', 'verified_authenticity_claimed', 'legal_access_claimed', 'directory_listing_used', 'accepted_public_record', 'mutated_master_index', 'file_hashing_used', 'mutated_public_index', 'enabled_private_access', 'enabled_restricted_access', 'enabled_cas_import', 'upload_used', 'public_index_write_included', 'user_supplied_url_candidate_is_fetch_permission', 'network_used', 'network_calls_made', 'local_source_identity_candidate_is_truth', 'entitlement_payload_included', 'archive_listing_used', 'execution_used', 'local_private_rights_safety_candidate_is_rights_or_safety_truth', 'rights_safety_candidate_is_rights_or_safety_truth', 'fingerprinting_used', 'private_source_access_used', 'accepted_CAS_import_truth', 'account_access_used', 'enabled_telemetry', 'unrestricted_local_path_included', 'enabled_local_access', 'user_supplied_url_boundary_candidate_is_fetch_permission', 'acquisition_action_used', 'privacy_redaction_candidate_proves_public_safety', 'extraction_output_included', 'production_readiness_claimed', 'pack_export_import_candidate_is_export_import_permission', 'user_authority_claimed', 'accepted_source_truth', 'private_source_boundary_candidate_is_access_permission', 'master_index_mutation_allowed', 'accepted_private_source_truth', 'enabled_acquisition_actions', 'model_provider_used', 'source_safety_claimed', 'evidence_write_included', 'disk_image_accessed', 'private_file_payload_included', 'upload_performed', 'privacy_safety_claimed', 'api_calls_made', 'imported_pack_included', 'changed_public_search_behavior'}
SECRET_KEY_RE = re.compile(r"(^|_)(api_key|api_token|access_token|auth_token|client_secret|password|private_key|cookie|session_cookie|credential|token|receipt|license_key|entitlement)($|_)", re.IGNORECASE)
PRIVATE_PAYLOAD_KEY_RE = re.compile(r"(private_file_payload|local_file_content|account_payload|cas_blob|exported_pack|imported_pack|source_cache_write|evidence_write|public_index_write|master_index_write)", re.IGNORECASE)
UNREDACTED_LOCATOR_RE = re.compile(r"(https?://|file://|[A-Za-z]:\\|\\\\|/Users/|/home/|/Volumes/)")


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in CONTRACTS + POLICIES + EXAMPLES:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required artifact: {rel}")
        elif path.suffix == ".json":
            _load_json(path, errors)
    for source_id in H13_SOURCE_IDS:
        source_dir = root / "examples/connectors/h13_local_private/fixtures" / source_id
        if not source_dir.is_dir():
            errors.append(f"missing fixture directory: {source_id}")
            continue
        module = importlib.import_module(f"runtime.connectors.h13_local_private.{source_id}")
        for kind, filename in FIXTURE_FILES.items():
            fixture_path = source_dir / filename
            if not fixture_path.exists():
                errors.append(f"missing fixture: {fixture_path.relative_to(root).as_posix()}")
                continue
            fixture = _load_json(fixture_path, errors)
            if isinstance(fixture, dict):
                if fixture.get("fixture_kind") != kind:
                    errors.append(f"fixture kind mismatch: {fixture_path}")
                _scan_json_boundaries(fixture, fixture_path, errors)
                try:
                    loaded = load_h13_local_private_fixture(fixture_path)
                    normalized = module.normalize(loaded)
                    errors.extend(detect_h13_truth_boundary_violations(normalized))
                    errors.extend(detect_h13_product_boundary_violations(normalized))
                    errors.extend(detect_h13_secret_or_private_data_violations(normalized))
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"normalizer failed for {source_id}/{filename}: {exc}")
        normalized_path = root / "examples/connectors/h13_local_private/normalized" / f"{source_id}_normalized_record_v0.json"
        replay_path = root / "examples/connectors/h13_local_private/replay_results" / f"{source_id}_replay_result_v0.json"
        if not normalized_path.exists():
            errors.append(f"missing normalized example for {source_id}")
        if not replay_path.exists():
            errors.append(f"missing replay example for {source_id}")
    _scan_runtime(root, errors)
    _run_check([sys.executable, "scripts/normalize_h13_local_private_fixture.py", "--source-id", "local_folder_metadata", "--input", "examples/connectors/h13_local_private/fixtures/local_folder_metadata/local_source_identity_record.json", "--check"], root, errors)
    _run_check([sys.executable, "scripts/replay_h13_local_private_fixtures.py", "--check"], root, errors)
    _run_check([sys.executable, "scripts/summarize_h13_local_private_fixture_outputs.py", "--input", "examples/connectors/h13_local_private", "--check"], root, errors)
    _check_forbidden_output_roots(root, errors)
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "local_sources", "cas_roots", "private_sources", "credential_directories", "user_url_fetches", "import_export_staging", "pack_exports", "pack_imports", "archive_extractions"):
        if (root / rel).exists():
            errors.append(f"forbidden local private root exists: {rel}")
    return {
        "schema_version": "h13_local_private_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(H13_SOURCE_IDS),
        "fixture_kind_count": len(H13_FIXTURE_KINDS),
        "network_calls_made": False,
        "local_private_access_used": False,
        "cas_import_pack_export_publication_used": False,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    result = validate_repo()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "valid" else 1


def _scan_runtime(root: Path, errors: list[str]) -> None:
    runtime_root = root / RUNTIME_DIR
    expected_modules = ["__init__.py", "fixture_loader.py", "normalizer_common.py", "redaction.py", "path_safety.py", "local_source_identity.py", "private_source_boundary.py", "user_supplied_url_boundary.py", "authenticated_source_boundary.py", "restricted_source_manifest.py", "local_cas_import_boundary.py", "pack_export_import_boundary.py", "privacy_redaction.py", "local_private_rights_safety.py"] + [f"{source_id}.py" for source_id in H13_SOURCE_IDS]
    for module in expected_modules:
        if not (runtime_root / module).exists():
            errors.append(f"missing runtime module: {module}")
    for path in runtime_root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"runtime module imports forbidden network/provider/browser library: {path}")
        if re.search(r"\b(fetch|download|upload|purchase|checkout|install|launch|scrape|crawl|execute|extract|acquire|scan|list_directory|import_pack|export_pack)\s*\(", text):
            errors.append(f"runtime module appears to define forbidden active behavior: {path}")


def _scan_json_boundaries(value: Any, label: Path | str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
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
        [sys.executable, "scripts/normalize_h13_local_private_fixture.py", "--source-id", "local_folder_metadata", "--input", "examples/connectors/h13_local_private/fixtures/local_folder_metadata/minimal_record.json", "--output", "site/dist/h13.json"],
        [sys.executable, "scripts/normalize_h13_local_private_fixture.py", "--source-id", "local_folder_metadata", "--input", "examples/connectors/h13_local_private/fixtures/local_folder_metadata/minimal_record.json", "--output", "data/public_index/h13.json"],
        [sys.executable, "scripts/normalize_h13_local_private_fixture.py", "--source-id", "local_folder_metadata", "--input", "examples/connectors/h13_local_private/fixtures/local_folder_metadata/minimal_record.json", "--output", "cas_roots/h13.json"],
        [sys.executable, "scripts/normalize_h13_local_private_fixture.py", "--source-id", "local_folder_metadata", "--input", "examples/connectors/h13_local_private/fixtures/local_folder_metadata/minimal_record.json", "--output", "credentials/h13.json"],
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
