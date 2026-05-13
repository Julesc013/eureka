#!/usr/bin/env python3
"""Validate H12 retro/community live-probe framework without live calls."""

from __future__ import annotations

import argparse
import importlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h12_retro_community.live_probe_common import (  # noqa: E402
    H12_SOURCE_IDS,
    detect_h12_retro_community_live_probe_product_boundary_violations,
    detect_h12_retro_community_live_probe_truth_boundary_violations,
    load_h12_retro_community_live_probe_policy_bundle,
    validate_h12_source_approval,
)

EXPECTED_SOURCES = tuple(('winworld_metadata', 'macintosh_garden_metadata', 'macintosh_repository_metadata', 'vetusware_metadata', 'oldversion_metadata', 'my_abandonware_metadata', 'dos_games_archive_metadata', 'hobbes_os2_archive_metadata', 'aminet_metadata', 'atarimania_metadata', 'tucows_ia_legacy_metadata', 'betaarchive_public_metadata_policy_limited', 'generic_retro_community_archive'))
REQUIRED_REQUEST_EXAMPLES = tuple(('winworld_metadata', 'macintosh_garden_metadata', 'macintosh_repository_metadata', 'oldversion_metadata', 'hobbes_os2_archive_metadata', 'aminet_metadata', 'tucows_ia_legacy_metadata', 'generic_retro_community_archive'))
CONTRACTS = tuple("control/schemas/previews/h12/connectors/" + name for name in ('retro_community_live_probe_request.v0.json', 'retro_community_live_probe_result.v0.json', 'retro_community_live_probe_output_bundle.v0.json', 'retro_community_connector_health_summary.v0.json'))
POLICIES = tuple("control/inventory/connectors/" + name for name in ('h12_retro_community_live_probe_policy.json', 'h12_retro_community_live_probe_allowed_requests.json', 'h12_retro_community_live_probe_endpoint_policy.json', 'h12_retro_community_live_probe_rate_limit_policy.json', 'h12_retro_community_live_probe_cache_policy.json', 'h12_retro_community_live_probe_kill_switch_policy.json', 'h12_retro_community_live_probe_output_policy.json', 'h12_retro_community_live_probe_path_policy.json', 'h12_retro_community_live_probe_review_policy.json', 'h12_retro_community_live_probe_truth_policy.json', 'h12_retro_community_live_probe_no_download_execute_policy.json', 'h12_retro_community_live_probe_restricted_source_policy.json'))
DOCS = tuple(('docs/reference/H12_RETRO_COMMUNITY_LIVE_PROBE.md', 'docs/reference/H12_RETRO_COMMUNITY_LIVE_PROBE_RESULT.md', 'docs/reference/H12_RETRO_COMMUNITY_CONNECTOR_HEALTH_SUMMARY.md', 'docs/architecture/H12_RETRO_COMMUNITY_LIVE_PROBE_MODEL.md', 'docs/operations/H12_RETRO_COMMUNITY_LIVE_PROBE_APPROVAL_GATES.md', 'docs/operations/H12_RETRO_COMMUNITY_LIVE_PROBE_REVIEW.md', 'docs/operations/H12_RETRO_COMMUNITY_LIVE_PROBE_BLOCKED_MODE.md', 'docs/operations/H12_RETRO_COMMUNITY_LIVE_PROBE_NO_DOWNLOAD_EXECUTE_POLICY.md', 'docs/operations/H12_RETRO_COMMUNITY_LIVE_PROBE_RESTRICTED_SOURCE_POLICY.md'))
AUDIT_DIR = Path("control/audits/h12-bundle-03-retro-community-live-probes-v0")
AUDIT_FILES = tuple(('README.md', 'h12_bundle_03_report.json', 'live_probe_policy_review.md', 'live_probe_execution_report.md', 'retro_software_identity_candidate_preview.md', 'platform_version_edition_candidate_preview.md', 'archive_item_member_candidate_preview.md', 'compatibility_install_note_candidate_preview.md', 'community_review_comment_candidate_preview.md', 'hash_checksum_candidate_preview.md', 'ia_wayback_corroboration_candidate_preview.md', 'gated_source_boundary_candidate_preview.md', 'retro_rights_safety_candidate_preview.md', 'source_cache_candidate_preview.md', 'evidence_candidate_preview.md', 'review_queue_seed_preview.md', 'connector_health_summary.md', 'no_download_execute_report.md', 'restricted_source_policy_report.md', 'h12_live_probe_blocked_or_completed_summary.md', 'validation.md', 'generated/sample_h12_live_probe_result.json', 'generated/sample_h12_retro_software_identity_candidate_from_probe.json', 'generated/sample_h12_platform_version_edition_candidate_from_probe.json', 'generated/sample_h12_archive_item_member_candidate_from_probe.json', 'generated/sample_h12_compatibility_install_note_candidate_from_probe.json', 'generated/sample_h12_community_review_comment_candidate_from_probe.json', 'generated/sample_h12_hash_checksum_candidate_from_probe.json', 'generated/sample_h12_ia_wayback_corroboration_candidate_from_probe.json', 'generated/sample_h12_gated_source_boundary_candidate_from_probe.json', 'generated/sample_h12_retro_rights_safety_candidate_from_probe.json', 'generated/sample_h12_source_cache_candidate_from_probe.json', 'generated/sample_h12_evidence_candidate_preview_from_probe.json', 'generated/sample_h12_review_queue_seed_from_probe.json', 'generated/sample_h12_connector_health_summary.json', 'generated/sample_h12_live_probe_summary.md'))
PYTHON_FILES = tuple(
    ["control/prototypes/legacy_runtime/connectors/h12_retro_community/live_probe_common.py"]
    + [f"control/prototypes/legacy_runtime/connectors/h12_retro_community/live_probe_{source_id}.py" for source_id in EXPECTED_SOURCES]
    + [
        "scripts/run_h12_retro_community_live_probe.py",
        "scripts/validate_h12_retro_community_live_probe.py",
        "scripts/summarize_h12_retro_community_live_probe_outputs.py",
    ]
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
CLIENT_CALL_RE = re.compile(r"(?<![\"'])\b(requests|httpx|aiohttp|openai|anthropic)\.")
SECRET_KEY_RE = re.compile(r"\"[^\"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^\"]*\"\s*:", re.IGNORECASE)
PAYLOAD_BODY_RE = re.compile(r"\"[^\"]*(software_payload|rom_payload|iso_payload|disc_image_payload|bios_firmware_payload|driver_payload|installer_payload|patch_payload|crack_key_serial_payload|archive_payload|extraction_output|execution_output|acquisition_action_output|file_upload_payload|hash_submission_payload|gated_source_access_result|account_access_result|scraping_output|crawling_output|browser_automation_output|restricted_source_access_output)[^\"]*\"\s*:", re.IGNORECASE)
FORBIDDEN_TRUE_KEYS = set({'gated_source_boundary_candidate_grants_access_permission', 'browser_automation_enabled', 'malware_safety_claimed', 'crawling_used', 'retro_rights_safety_candidate_is_rights_or_safety_truth', 'crawling_enabled', 'enabled_telemetry', 'accepted_compatibility_install_truth', 'compatibility_correctness_claimed', 'checksum_correctness_claimed', 'metadata_probe_approved', 'api_query_enabled', 'source_cache_preview_is_accepted_source', 'enabled_uploads', 'extraction_enabled', 'abandonware_label_is_legal_permission', 'accepted_community_review_truth', 'live_probe_default_enabled', 'mutated_master_index', 'gated_source_access_enabled', 'enabled_downloads', 'execution_enabled', 'bypass_or_automation_used', 'archive_item_member_candidate_is_truth', 'acquisition_action_enabled', 'source_cache_candidate_is_accepted_source', 'community_download_metadata_grants_acquisition_permission', 'hash_checksum_candidate_is_truth', 'enabled_extraction', 'file_upload_enabled', 'live_probe_result_is_public_truth', 'privacy_safety_claimed', 'rights_clearance_claimed', 'enabled_hosting', 'ia_wayback_corroboration_candidate_is_truth', 'enabled_execution', 'bypass_or_automation_enabled', 'accepted_platform_version_truth', 'normalized_record_is_public_truth', 'content_safety_claimed', 'restricted_source_access_used', 'forum_or_comment_fetch_enabled', 'web_archive_trace_fetch_enabled', 'gated_source_access_used', 'public_index_mutated', 'community_review_comment_candidate_is_truth', 'web_archive_trace_fetch_used', 'catalog_fetch_enabled', 'enabled_accounts', 'hash_submission_used', 'installability_claimed', 'execution_used', 'review_seed_is_review_decision', 'public_query_fanout_enabled', 'playability_claimed', 'api_calls_made', 'accepted_archive_item_member_truth', 'verified_authenticity_claimed', 'network_calls_made', 'extraction_used', 'master_index_mutated', 'upload_used', 'live_access_approved', 'accepted_rights_safety_truth', 'retro_software_identity_candidate_is_truth', 'account_access_enabled', 'mutated_public_index', 'archive_item_metadata_grants_download_or_extraction_permission', 'enabled_live_probes', 'accepted_evidence_truth', 'hash_submission_enabled', 'scraping_enabled', 'source_sync_enabled', 'accepted_gated_source_access_truth', 'platform_version_edition_candidate_is_truth', 'compatibility_install_note_candidate_is_truth', 'catalog_fetch_used', 'restricted_source_enabled', 'download_enabled', 'accepted_public_record', 'accepted_source_truth', 'enabled_acquisition_actions', 'html_catalog_fetch_used', 'acquisition_action_used', 'html_catalog_fetch_enabled', 'download_used', 'changed_public_search_behavior', 'evidence_candidate_preview_is_accepted_evidence', 'forum_comment_fetch_used', 'legal_acquisition_claimed', 'scraping_used', 'account_access_used', 'enabled_source_sync', 'file_authenticity_claimed', 'accepted_candidate_truth', 'accepted_retro_software_identity_truth', 'accepted_ia_wayback_corroboration_truth', 'accepted_hash_checksum_truth', 'production_readiness_claimed', 'enabled_crawling', 'community_reputation_claimed', 'evidence_preview_is_accepted_evidence'})


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H12 retro/community live probe validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    for rel in CONTRACTS + POLICIES:
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            payloads[rel] = payload
    for rel in DOCS + PYTHON_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    for name in AUDIT_FILES:
        if not (root / AUDIT_DIR / name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / name).as_posix()}")
    validate_policies(payloads, errors)
    validate_examples(root, errors)
    validate_runtime_imports(errors)
    validate_python_safety(root, errors)
    validate_cli_offline(root, errors)
    validate_generated_outputs(root, errors)
    validate_no_private_roots(root, errors)
    if tuple(H12_SOURCE_IDS) != EXPECTED_SOURCES:
        errors.append("runtime H12 source IDs do not match expected live-probe sources")
    return {
        "schema_version": "h12_retro_community_live_probe_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H12-BUNDLE-03",
        "offline_default": True,
        "network_calls_made": False,
        "query_fetch_download_upload_execute_acquire_used": False,
        "restricted_source_access_used": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    live = payloads.get(POLICIES[0], {})
    for key in (
        "live_probe_default_enabled",
        "source_sync_enabled",
        "public_query_fanout_enabled",
        "api_query_enabled",
        "catalog_fetch_enabled",
        "html_catalog_fetch_enabled",
        "forum_or_comment_fetch_enabled",
        "web_archive_trace_fetch_enabled",
        "gated_source_access_enabled",
        "account_access_enabled",
        "download_enabled",
        "extraction_enabled",
        "execution_enabled",
        "acquisition_action_enabled",
        "file_upload_enabled",
        "hash_submission_enabled",
        "scraping_enabled",
        "crawling_enabled",
        "browser_automation_enabled",
        "restricted_source_enabled",
        "bypass_or_automation_enabled",
    ):
        if live.get(key) is not False:
            errors.append(f"global policy {key} must be false")
    allowed = payloads.get(POLICIES[1], {})
    sources = allowed.get("sources", [])
    if sorted(item.get("source_id") for item in sources if isinstance(item, Mapping)) != sorted(EXPECTED_SOURCES):
        errors.append("allowed requests policy must list all H12 sources")
    bundle = load_h12_retro_community_live_probe_policy_bundle(REPO_ROOT)
    for item in sources:
        if not isinstance(item, Mapping):
            errors.append("allowed request source entry must be object")
            continue
        source_id = str(item.get("source_id"))
        if item.get("approval_status") != "not_approved_for_live_access":
            errors.append(f"{source_id}: approval_status must remain not_approved_for_live_access")
        if item.get("allowed_request_keys") not in ([], None):
            errors.append(f"{source_id}: allowed_request_keys must stay empty without approval")
        for key in ("live_access_approved", "metadata_probe_approved"):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        for key in (
            "source_sync_approved",
            "gated_source_access_approved",
            "account_access_approved",
            "download_approved",
            "rom_download_approved",
            "iso_download_approved",
            "disc_image_download_approved",
            "bios_firmware_download_approved",
            "software_binary_download_approved",
            "driver_download_approved",
            "installer_download_approved",
            "patch_download_approved",
            "crack_key_serial_handling_approved",
            "archive_download_approved",
            "extraction_approved",
            "emulator_execution_approved",
            "install_execute_approved",
            "acquisition_action_approved",
            "file_upload_approved",
            "hash_submission_approved",
            "scraping_approved",
            "crawling_approved",
            "browser_automation_approved",
            "restricted_rights_sensitive_source_approved",
            "gated_private_source_approved",
            "piracy_adjacent_or_leaked_source_approved",
            "drm_or_access_control_bypass_approved",
            "public_query_fanout_approved",
        ):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        request_key = str((item.get("planned_request_keys") or [""])[0])
        if validate_h12_source_approval(source_id, request_key, bundle)["approved"]:
            errors.append(f"{source_id}: live approval unexpectedly passes")
    output = payloads.get(POLICIES[6], {})
    for key in [
        "source_cache_write_current",
        "evidence_ledger_write_current",
        "review_queue_write_current",
        "live_sync_state",
        "api_query_sync_result",
        "catalog_fetch_result",
        "forum_comment_fetch_result",
        "gated_source_access_result",
        "account_access_result",
        "download_payload",
        "software_payload",
        "ROM_payload",
        "ISO_payload",
        "disc_image_payload",
        "BIOS_firmware_payload",
        "driver_payload",
        "installer_payload",
        "patch_payload",
        "crack_key_serial_payload",
        "archive_payload",
        "extraction_output",
        "execution_output",
        "acquisition_action_output",
        "file_upload_payload",
        "hash_submission_payload",
        "scraping_output",
        "crawling_output",
        "restricted_source_access_output",
        "accepted_retro_software_identity_truth",
        "accepted_platform_version_truth",
        "accepted_archive_item_member_truth",
        "accepted_compatibility_install_truth",
        "accepted_community_review_truth",
        "accepted_hash_checksum_truth",
        "accepted_ia_wayback_corroboration_truth",
        "accepted_gated_source_access_truth",
        "accepted_rights_safety_truth",
        "accepted_source_truth",
        "accepted_evidence_truth",
        "accepted_candidate_truth",
        "accepted_public_record",
        "public_index_mutation",
        "master_index_mutation",
        "rights_clearance",
        "legal_acquisition_truth",
        "file_authenticity_truth",
        "checksum_correctness_truth",
        "compatibility_correctness",
        "installability_truth",
        "playability_truth",
        "malware_safety",
        "content_safety_truth",
        "privacy_safety",
        "community_reputation_truth",
        "verified_authenticity",
        "production_readiness_claim",
    ]:
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"output policy must forbid {key}")


def validate_examples(root: Path, errors: list[str]) -> None:
    request_dir = root / "examples/connectors/h12_retro_community/live_probe"
    result_dir = root / "examples/connectors/h12_retro_community/live_probe_results"
    for source_id in REQUIRED_REQUEST_EXAMPLES:
        path = request_dir / f"approved_{source_id}_probe_request_v0.json"
        if not path.is_file():
            errors.append(f"missing request example: {path.relative_to(root).as_posix()}")
        else:
            _scan_json_boundaries(load_json_object(path, errors) or {}, path, errors)
    if not (request_dir / "blocked_live_probe_request_v0.json").is_file():
        errors.append("missing blocked live-probe request example")
    required_result_sources = REQUIRED_REQUEST_EXAMPLES
    for source_id in required_result_sources:
        path = result_dir / f"{source_id}_live_probe_result_example_v0.json"
        if not path.is_file():
            errors.append(f"missing live probe result example for {source_id}")
            continue
        payload = load_json_object(path, errors) or {}
        _scan_json_boundaries(payload, path, errors)
        if payload.get("network_used") is not False:
            errors.append(f"{path} must not use network")
        if payload.get("result_status") != "blocked_by_missing_approval":
            errors.append(f"{path} must be blocked by missing approval")
        if detect_h12_retro_community_live_probe_truth_boundary_violations(payload, {}):
            errors.append(f"{path} has truth boundary violations")
        if detect_h12_retro_community_live_probe_product_boundary_violations(payload, {}):
            errors.append(f"{path} has product boundary violations")
    for rel in [
        "source_cache_candidate_from_h12_probe_v0.json",
        "evidence_candidate_preview_from_h12_probe_v0.json",
        "review_queue_seed_from_h12_probe_v0.json",
        "connector_health_from_h12_probe_v0.json",
        "retro_software_identity_candidate_from_h12_probe_v0.json",
        "platform_version_edition_candidate_from_h12_probe_v0.json",
        "archive_item_member_candidate_from_h12_probe_v0.json",
        "compatibility_install_note_candidate_from_h12_probe_v0.json",
        "community_review_comment_candidate_from_h12_probe_v0.json",
        "hash_checksum_candidate_from_h12_probe_v0.json",
        "ia_wayback_corroboration_candidate_from_h12_probe_v0.json",
        "gated_source_boundary_candidate_from_h12_probe_v0.json",
        "retro_rights_safety_candidate_from_h12_probe_v0.json",
    ]:
        path = root / "examples/connectors/h12_retro_community/live_probe_outputs" / rel
        if not path.is_file():
            errors.append(f"missing live probe output example: {rel}")
        else:
            _scan_json_boundaries(load_json_object(path, errors) or {}, path, errors)


def validate_runtime_imports(errors: list[str]) -> None:
    try:
        importlib.import_module("control.prototypes.legacy_runtime.connectors.h12_retro_community.live_probe_common")
        for source_id in EXPECTED_SOURCES:
            module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h12_retro_community.live_probe_{source_id}")
            for name in ("build_request_url_or_metadata_request", "parse_response_payload", "normalize_response_payload"):
                if not hasattr(module, name):
                    errors.append(f"missing {name} in live_probe_{source_id}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"runtime import failed: {exc}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"forbidden network/provider/browser import: {rel}")
        if CLIENT_CALL_RE.search(text):
            errors.append(f"forbidden client call in default live-probe framework: {rel}")
        if re.search(r"\b(playwright|selenium|browser_automation)\s*\(", text):
            errors.append(f"browser automation call pattern found: {rel}")


def validate_cli_offline(root: Path, errors: list[str]) -> None:
    _run_check([sys.executable, "scripts/run_h12_retro_community_live_probe.py", "--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--check"], root, errors)
    _run_check([sys.executable, "scripts/summarize_h12_retro_community_live_probe_outputs.py", "--input", "examples/connectors/h12_retro_community/live_probe_results", "--check"], root, errors)
    forbidden_checks = [
        [sys.executable, "scripts/run_h12_retro_community_live_probe.py", "--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--output", "site/dist/h12.json"],
        [sys.executable, "scripts/run_h12_retro_community_live_probe.py", "--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--output", "data/public_index/h12.json"],
        [sys.executable, "scripts/run_h12_retro_community_live_probe.py", "--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--output", "roms/h12.json"],
        [sys.executable, "scripts/run_h12_retro_community_live_probe.py", "--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--output", "isos/h12.json"],
        [sys.executable, "scripts/run_h12_retro_community_live_probe.py", "--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--output", "bios/h12.json"],
        [sys.executable, "scripts/run_h12_retro_community_live_probe.py", "--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--output", "archive_extractions/h12.json"],
        [sys.executable, "scripts/run_h12_retro_community_live_probe.py", "--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--output", "gated_source_accounts/h12.json"],
    ]
    for cmd in forbidden_checks:
        proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode == 0:
            errors.append(f"forbidden output root was not rejected: {cmd[-1]}")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    for rel in [
        "control/audits/h12-bundle-03-retro-community-live-probes-v0/generated/sample_h12_live_probe_result.json",
        "control/audits/h12-bundle-03-retro-community-live-probes-v0/generated/sample_h12_connector_health_summary.json",
    ]:
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            _scan_json_boundaries(payload, root / rel, errors)


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "roms", "isos", "disc_images", "bios", "firmware", "vintage_software_downloads", "installers", "patches", "cracks", "keys", "serials", "gated_source_accounts", "forum_sessions", "archive_extractions", "execution_actions", "restricted_sources"):
        if (root / rel).exists():
            errors.append(f"forbidden local private root exists: {rel}")


def _scan_json_boundaries(value: Any, label: Path, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{label} forbidden true value: {key_text}")
            if SECRET_KEY_RE.search(json.dumps(key_text)) and item not in (False, None, "", "blocked_fixture_boundary", "blocked_current_no_credentials"):
                errors.append(f"{label} forbidden secret-like key value: {key_text}")
            if PAYLOAD_BODY_RE.search(json.dumps(key_text)) and item not in (False, None, "", [], {}):
                errors.append(f"{label} forbidden payload key: {key_text}")
            _scan_json_boundaries(item, label, errors)
    elif isinstance(value, list):
        for item in value:
            _scan_json_boundaries(item, label, errors)


def _run_check(cmd: list[str], root: Path, errors: list[str]) -> None:
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        errors.append(f"command failed: {' '.join(cmd)} :: {proc.stdout} {proc.stderr}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path}: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"JSON object expected: {path}")
        return None
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
