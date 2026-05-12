#!/usr/bin/env python3
"""Validate H12 retro/community fixture runtime artifacts offline."""

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

from runtime.connectors.h12_retro_community.fixture_loader import load_h12_retro_community_fixture  # noqa: E402
from runtime.connectors.h12_retro_community.normalizer_common import H12_FIXTURE_KINDS, H12_SOURCE_IDS, detect_h12_product_boundary_violations, detect_h12_truth_boundary_violations  # noqa: E402

CONTRACTS = ['control/schemas/fixtures/h12/connectors/retro_community_fixture.v0.json', 'control/schemas/previews/h12/connectors/retro_community_normalized_record.v0.json', 'control/schemas/previews/h12/connectors/retro_software_identity_candidate.v0.json', 'control/schemas/previews/h12/connectors/platform_version_edition_candidate.v0.json', 'control/schemas/previews/h12/connectors/archive_item_member_candidate.v0.json', 'control/schemas/previews/h12/connectors/compatibility_install_note_candidate.v0.json', 'control/schemas/previews/h12/connectors/community_review_comment_candidate.v0.json', 'control/schemas/previews/h12/connectors/hash_checksum_candidate.v0.json', 'control/schemas/previews/h12/connectors/ia_wayback_corroboration_candidate.v0.json', 'control/schemas/previews/h12/connectors/gated_source_boundary_candidate.v0.json', 'control/schemas/previews/h12/connectors/retro_rights_safety_candidate.v0.json', 'control/schemas/fixtures/h12/connectors/retro_community_fixture_replay_result.v0.json']
POLICIES = ['control/inventory/connectors/h12_retro_community_fixture_runtime_policy.json', 'control/inventory/connectors/h12_retro_community_normalization_policy.json', 'control/inventory/connectors/h12_retro_software_identity_mapping_policy.json', 'control/inventory/connectors/h12_platform_version_edition_mapping_policy.json', 'control/inventory/connectors/h12_archive_item_member_mapping_policy.json', 'control/inventory/connectors/h12_compatibility_install_note_mapping_policy.json', 'control/inventory/connectors/h12_community_review_comment_mapping_policy.json', 'control/inventory/connectors/h12_hash_checksum_mapping_policy.json', 'control/inventory/connectors/h12_ia_wayback_corroboration_mapping_policy.json', 'control/inventory/connectors/h12_gated_source_boundary_mapping_policy.json', 'control/inventory/connectors/h12_retro_rights_safety_mapping_policy.json', 'control/inventory/connectors/h12_retro_community_fixture_output_policy.json', 'control/inventory/connectors/h12_retro_community_fixture_path_policy.json', 'control/inventory/connectors/h12_retro_community_fixture_truth_policy.json', 'control/inventory/connectors/h12_retro_community_source_cache_mapping_policy.json', 'control/inventory/connectors/h12_retro_community_evidence_mapping_policy.json', 'control/inventory/connectors/h12_retro_community_no_download_execute_policy.json']
FIXTURE_FILES = {'minimal': 'minimal_record.json', 'retro_software_identity': 'retro_software_identity_record.json', 'platform_version_edition': 'platform_version_edition_record.json', 'archive_item_member': 'archive_item_member_record.json', 'compatibility_install_note': 'compatibility_install_note_record.json', 'community_review_comment': 'community_review_comment_record.json', 'hash_checksum': 'hash_checksum_record.json', 'ia_wayback_corroboration': 'ia_wayback_corroboration_record.json', 'gated_source_boundary': 'gated_source_boundary_record.json', 'rights_safety': 'rights_safety_record.json', 'policy_blocked': 'policy_blocked_record.json'}
EXAMPLES = ['examples/connectors/h12_retro_community/identity/retro_software_identity_candidate_v0.json', 'examples/connectors/h12_retro_community/identity/platform_version_edition_candidate_v0.json', 'examples/connectors/h12_retro_community/identity/archive_item_member_candidate_v0.json', 'examples/connectors/h12_retro_community/identity/compatibility_install_note_candidate_v0.json', 'examples/connectors/h12_retro_community/identity/community_review_comment_candidate_v0.json', 'examples/connectors/h12_retro_community/identity/hash_checksum_candidate_v0.json', 'examples/connectors/h12_retro_community/identity/ia_wayback_corroboration_candidate_v0.json', 'examples/connectors/h12_retro_community/identity/gated_source_boundary_candidate_v0.json', 'examples/connectors/h12_retro_community/identity/retro_rights_safety_candidate_v0.json', 'examples/connectors/h12_retro_community/identity/policy_blocked_identity_candidate_v0.json']
RUNTIME_DIR = "runtime/connectors/h12_retro_community"
BANNED_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|urllib|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)
FORBIDDEN_TRUE_KEYS = {'software_binary_payload_included', 'enabled_telemetry', 'account_access_used', 'installer_payload_included', 'production_readiness_claimed', 'gated_source_access_used', 'bypass_or_automation_used', 'normalized_record_is_public_truth', 'accepted_ia_wayback_corroboration_truth', 'master_index_mutated', 'live_call_used', 'accepted_gated_source_access_truth', 'accepted_platform_version_truth', 'hash_submission_performed', 'accepted_rights_safety_truth', 'accepted_evidence_truth', 'enabled_uploads', 'scraping_output_included', 'patch_payload_included', 'extraction_used', 'acquisition_action_used', 'mutated_master_index', 'archive_item_metadata_grants_download_or_extraction_permission', 'retro_rights_safety_candidate_is_rights_or_safety_truth', 'accepted_hash_checksum_truth', 'capability_grants_permission', 'file_upload_performed', 'execution_used', 'accepted_public_record', 'public_index_mutated', 'extraction_output_included', 'malware_safety_claimed', 'playability_claimed', 'content_safety_claimed', 'forum_or_comment_payload_included', 'checksum_correctness_claimed', 'evidence_preview_is_accepted_evidence', 'network_calls_made', 'crawling_used', 'retro_software_identity_candidate_is_truth', 'privacy_safety_claimed', 'driver_payload_included', 'crawling_output_included', 'restricted_source_accessed', 'community_review_comment_candidate_is_truth', 'external_api_used', 'rights_clearance_claimed', 'source_pack_is_accepted_evidence', 'changed_public_search_behavior', 'enabled_accounts', 'compatibility_install_note_candidate_is_truth', 'installability_claimed', 'accepted_candidate_truth', 'enabled_downloads', 'enabled_hosting', 'enabled_acquisition_actions', 'forum_comment_fetch_used', 'enabled_source_sync', 'accepted_community_review_truth', 'html_catalog_fetch_used', 'compatibility_correctness_claimed', 'acquisition_action_performed', 'community_download_metadata_grants_acquisition_permission', 'accepted_source_truth', 'archive_item_member_candidate_is_truth', 'iso_payload_included', 'accepted_compatibility_install_truth', 'platform_version_edition_candidate_is_truth', 'source_pack_is_imported_state', 'source_cache_preview_is_accepted_source', 'bios_firmware_payload_included', 'catalog_payload_included', 'ia_wayback_corroboration_candidate_is_truth', 'enabled_extraction', 'enabled_crawling', 'enabled_execution', 'chd_payload_included', 'community_reputation_claimed', 'disc_image_payload_included', 'hash_checksum_candidate_is_truth', 'archive_payload_included', 'gated_source_boundary_candidate_grants_access_permission', 'crack_key_serial_payload_included', 'hash_submission_used', 'download_used', 'mutated_public_index', 'enabled_live_probes', 'accepted_archive_item_member_truth', 'execution_output_included', 'rom_payload_included', 'abandonware_label_is_legal_permission', 'accepted_retro_software_identity_truth', 'upload_used', 'network_used', 'policy_pack_grants_live_access', 'verified_authenticity_claimed', 'gated_source_payload_included', 'account_payload_included', 'file_authenticity_claimed', 'legal_acquisition_claimed', 'restricted_source_access_used', 'scraping_used', 'api_calls_made', 'source_pack_is_truth', 'catalog_fetch_used'}
SECRET_KEY_RE = re.compile(r"(^|_)(api_key|api_token|access_token|auth_token|client_secret|password|private_key|cookie|session_cookie)($|_)", re.IGNORECASE)
FORBIDDEN_PAYLOAD_KEY_RE = re.compile(r"(software_binary_payload|rom_payload|iso_payload|chd_payload|bios_payload|firmware_payload|driver_payload|installer_payload|patch_payload|crack_payload|serial_payload|archive_payload|extraction_log|execution_log|acquisition_output|uploaded_file|submitted_hash|gated_private_content|restricted_content|scraping_output|crawling_output|browser_automation_output)", re.IGNORECASE)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in CONTRACTS + POLICIES + EXAMPLES:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required artifact: {rel}")
        elif path.suffix == ".json":
            _load_json(path, errors)
    for source_id in H12_SOURCE_IDS:
        source_dir = root / "examples/connectors/h12_retro_community/fixtures" / source_id
        if not source_dir.is_dir():
            errors.append(f"missing fixture directory: {source_id}")
            continue
        module = importlib.import_module(f"runtime.connectors.h12_retro_community.{source_id}")
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
                    loaded = load_h12_retro_community_fixture(fixture_path)
                    normalized = module.normalize(loaded)
                    errors.extend(detect_h12_truth_boundary_violations(normalized))
                    errors.extend(detect_h12_product_boundary_violations(normalized))
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"normalizer failed for {source_id}/{filename}: {exc}")
        normalized_path = root / "examples/connectors/h12_retro_community/normalized" / f"{source_id}_normalized_record_v0.json"
        replay_path = root / "examples/connectors/h12_retro_community/replay_results" / f"{source_id}_replay_result_v0.json"
        if not normalized_path.exists():
            errors.append(f"missing normalized example for {source_id}")
        if not replay_path.exists():
            errors.append(f"missing replay example for {source_id}")
    _scan_runtime(root, errors)
    _run_check([sys.executable, "scripts/normalize_h12_retro_community_fixture.py", "--source-id", "winworld_metadata", "--input", "examples/connectors/h12_retro_community/fixtures/winworld_metadata/retro_software_identity_record.json", "--check"], root, errors)
    _run_check([sys.executable, "scripts/replay_h12_retro_community_fixtures.py", "--check"], root, errors)
    _run_check([sys.executable, "scripts/summarize_h12_retro_community_fixture_outputs.py", "--input", "examples/connectors/h12_retro_community", "--check"], root, errors)
    _check_forbidden_output_roots(root, errors)
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "roms", "isos", "disc_images", "emulators", "bios", "firmware", "vintage_software_downloads", "installers", "patches", "cracks", "keys", "serials", "gated_source_accounts", "forum_sessions", "archive_extractions"):
        if (root / rel).exists():
            errors.append(f"forbidden local private root exists: {rel}")
    return {
        "schema_version": "h12_retro_community_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(H12_SOURCE_IDS),
        "fixture_kind_count": len(H12_FIXTURE_KINDS),
        "network_calls_made": False,
        "download_extract_execute_acquire_used": False,
        "restricted_source_access_used": False,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    result = validate_repo()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "valid" else 1


def _scan_runtime(root: Path, errors: list[str]) -> None:
    runtime_root = root / RUNTIME_DIR
    expected_modules = ["__init__.py", "fixture_loader.py", "normalizer_common.py", "retro_software_identity.py", "platform_version_edition.py", "archive_item_member.py", "compatibility_install_note.py", "community_review_comment.py", "hash_checksum.py", "ia_wayback_corroboration.py", "gated_source_boundary.py", "retro_rights_safety.py"] + [f"{source_id}.py" for source_id in H12_SOURCE_IDS]
    for module in expected_modules:
        if not (runtime_root / module).exists():
            errors.append(f"missing runtime module: {module}")
    for path in runtime_root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"runtime module imports forbidden network/provider/browser library: {path}")
        if re.search(r"\b(fetch|download|upload|purchase|checkout|install|launch|scrape|crawl|execute|extract|acquire)\s*\(", text):
            errors.append(f"runtime module appears to define forbidden active behavior: {path}")


def _scan_json_boundaries(value: Any, label: Path | str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{label} forbidden true value: {key_text}")
            if SECRET_KEY_RE.search(key_text) and item not in (False, None, "", "blocked_fixture_boundary", "blocked_current_no_credentials"):
                errors.append(f"{label} forbidden secret-like key value: {key_text}")
            if FORBIDDEN_PAYLOAD_KEY_RE.search(key_text) and item not in (False, None, "", [], {}):
                errors.append(f"{label} forbidden payload key: {key_text}")
            _scan_json_boundaries(item, label, errors)
    elif isinstance(value, list):
        for item in value:
            _scan_json_boundaries(item, label, errors)


def _check_forbidden_output_roots(root: Path, errors: list[str]) -> None:
    checks = [
        [sys.executable, "scripts/normalize_h12_retro_community_fixture.py", "--source-id", "winworld_metadata", "--input", "examples/connectors/h12_retro_community/fixtures/winworld_metadata/minimal_record.json", "--output", "site/dist/h12.json"],
        [sys.executable, "scripts/normalize_h12_retro_community_fixture.py", "--source-id", "winworld_metadata", "--input", "examples/connectors/h12_retro_community/fixtures/winworld_metadata/minimal_record.json", "--output", "data/public_index/h12.json"],
        [sys.executable, "scripts/normalize_h12_retro_community_fixture.py", "--source-id", "winworld_metadata", "--input", "examples/connectors/h12_retro_community/fixtures/winworld_metadata/minimal_record.json", "--output", "roms/h12.json"],
        [sys.executable, "scripts/normalize_h12_retro_community_fixture.py", "--source-id", "winworld_metadata", "--input", "examples/connectors/h12_retro_community/fixtures/winworld_metadata/minimal_record.json", "--output", "archive_extractions/h12.json"],
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
