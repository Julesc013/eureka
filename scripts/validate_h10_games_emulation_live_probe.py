#!/usr/bin/env python3
"""Validate H10 games/emulation live-probe framework without live calls."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from typing import Any, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h10_games_emulation.live_probe_common import (  # noqa: E402
    H10_SOURCE_IDS,
    detect_h10_games_emulation_live_probe_product_boundary_violations,
    detect_h10_games_emulation_live_probe_truth_boundary_violations,
    load_h10_games_emulation_live_probe_policy_bundle,
    validate_h10_source_approval,
)

EXPECTED_SOURCES = tuple(['mobygames', 'mame_software_lists', 'scummvm_compatibility', 'redump_hash_sets', 'no_intro_hash_sets', 'tosec_hash_sets', 'flashpoint_metadata', 'steam_game_metadata_policy_limited', 'gog_game_metadata_policy_limited', 'itchio_game_metadata_policy_limited', 'generic_game_database', 'generic_emulator_compatibility', 'generic_preservation_hashset', 'games_emulation_policy_blocked'])
RESULT_EXAMPLE_SOURCES = tuple(['mobygames', 'mame_software_lists', 'scummvm_compatibility', 'redump_hash_sets', 'no_intro_hash_sets', 'flashpoint_metadata', 'generic_game_database', 'generic_emulator_compatibility'])
CONTRACTS = tuple(['contracts/connectors/h10_games_emulation_live_probe_request.v0.json', 'contracts/connectors/h10_games_emulation_live_probe_result.v0.json', 'contracts/connectors/h10_games_emulation_live_probe_output_bundle.v0.json', 'contracts/connectors/h10_games_emulation_connector_health_summary.v0.json'])
POLICIES = tuple(['control/inventory/connectors/h10_games_emulation_live_probe_policy.json', 'control/inventory/connectors/h10_games_emulation_live_probe_allowed_requests.json', 'control/inventory/connectors/h10_games_emulation_live_probe_endpoint_policy.json', 'control/inventory/connectors/h10_games_emulation_live_probe_rate_limit_policy.json', 'control/inventory/connectors/h10_games_emulation_live_probe_cache_policy.json', 'control/inventory/connectors/h10_games_emulation_live_probe_kill_switch_policy.json', 'control/inventory/connectors/h10_games_emulation_live_probe_output_policy.json', 'control/inventory/connectors/h10_games_emulation_live_probe_path_policy.json', 'control/inventory/connectors/h10_games_emulation_live_probe_review_policy.json', 'control/inventory/connectors/h10_games_emulation_live_probe_truth_policy.json', 'control/inventory/connectors/h10_games_emulation_live_probe_no_download_execute_policy.json', 'control/inventory/connectors/h10_games_emulation_live_probe_restricted_source_policy.json'])
DOCS = tuple(['docs/reference/H10_GAMES_EMULATION_LIVE_PROBE.md', 'docs/reference/H10_GAMES_EMULATION_LIVE_PROBE_RESULT.md', 'docs/reference/H10_GAMES_EMULATION_CONNECTOR_HEALTH_SUMMARY.md', 'docs/architecture/H10_GAMES_EMULATION_LIVE_PROBE_MODEL.md', 'docs/operations/H10_GAMES_EMULATION_LIVE_PROBE_APPROVAL_GATES.md', 'docs/operations/H10_GAMES_EMULATION_LIVE_PROBE_REVIEW.md', 'docs/operations/H10_GAMES_EMULATION_LIVE_PROBE_BLOCKED_MODE.md', 'docs/operations/H10_GAMES_EMULATION_LIVE_PROBE_NO_DOWNLOAD_EXECUTE_POLICY.md', 'docs/operations/H10_GAMES_EMULATION_LIVE_PROBE_RESTRICTED_SOURCE_POLICY.md'])
AUDIT_DIR = Path("control/audits/h10-bundle-03-games-emulation-live-probes-v0")
AUDIT_FILES = tuple(['README.md', 'h10_bundle_03_report.json', 'live_probe_policy_review.md', 'live_probe_execution_report.md', 'game_software_identity_candidate_preview.md', 'platform_release_edition_candidate_preview.md', 'emulator_compatibility_candidate_preview.md', 'preservation_hashset_candidate_preview.md', 'rom_disc_media_identity_candidate_preview.md', 'game_relation_candidate_preview.md', 'emulator_action_candidate_preview.md', 'games_rights_safety_candidate_preview.md', 'source_cache_candidate_preview.md', 'evidence_candidate_preview.md', 'review_queue_seed_preview.md', 'connector_health_summary.md', 'no_download_execute_report.md', 'restricted_source_policy_report.md', 'h10_live_probe_blocked_or_completed_summary.md', 'validation.md', 'generated/sample_h10_live_probe_result.json', 'generated/sample_h10_game_software_identity_candidate_from_probe.json', 'generated/sample_h10_platform_release_edition_candidate_from_probe.json', 'generated/sample_h10_emulator_compatibility_candidate_from_probe.json', 'generated/sample_h10_preservation_hashset_candidate_from_probe.json', 'generated/sample_h10_rom_disc_media_identity_candidate_from_probe.json', 'generated/sample_h10_game_relation_candidate_from_probe.json', 'generated/sample_h10_emulator_action_candidate_from_probe.json', 'generated/sample_h10_games_rights_safety_candidate_from_probe.json', 'generated/sample_h10_source_cache_candidate_from_probe.json', 'generated/sample_h10_evidence_candidate_preview_from_probe.json', 'generated/sample_h10_review_queue_seed_from_probe.json', 'generated/sample_h10_connector_health_summary.json', 'generated/sample_h10_live_probe_summary.md'])
PYTHON_FILES = tuple(
    ["runtime/connectors/h10_games_emulation/live_probe_common.py"]
    + [f"runtime/connectors/h10_games_emulation/live_probe_{source_id}.py" for source_id in EXPECTED_SOURCES]
    + [
        "scripts/run_h10_games_emulation_live_probe.py",
        "scripts/validate_h10_games_emulation_live_probe.py",
        "scripts/summarize_h10_games_emulation_live_probe_outputs.py",
    ]
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
CLIENT_CALL_RE = re.compile(r"(?<![\"'])\b(requests|httpx|aiohttp|openai|anthropic)\.")
SECRET_KEY_RE = re.compile(r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:', re.IGNORECASE)
PAYLOAD_BODY_RE = re.compile(r'"[^"]*(rom_payload_body|iso_payload_body|disc_image_payload_body|chd_payload_body|bios_payload_body|firmware_payload_body|game_binary_payload_body|emulator_payload_body|installer_payload_body|patch_payload_body|asset_payload_body|restricted_payload_body|scraping_output_body|crawling_output_body|browser_automation_output_body|execution_log_body|acquisition_output_body)[^"]*"\s*:', re.IGNORECASE)
FORBIDDEN_TRUE_KEYS = set(['live_probe_result_is_public_truth', 'normalized_record_is_public_truth', 'game_software_identity_candidate_is_truth', 'platform_release_edition_candidate_is_truth', 'emulator_compatibility_candidate_is_truth', 'preservation_hashset_candidate_is_truth', 'rom_disc_media_identity_candidate_is_truth', 'rom_disc_media_candidate_is_truth', 'game_relation_candidate_is_truth', 'emulator_action_candidate_is_action_permission', 'rights_safety_candidate_is_rights_or_safety_truth', 'hash_metadata_proves_authenticity', 'storefront_metadata_grants_acquisition_permission', 'compatibility_metadata_proves_playability', 'media_identity_grants_download_permission', 'source_cache_candidate_is_accepted_source', 'source_cache_preview_is_accepted_source', 'evidence_candidate_preview_is_accepted_evidence', 'evidence_preview_is_accepted_evidence', 'review_seed_is_review_decision', 'accepted_source_truth', 'accepted_evidence_truth', 'accepted_candidate_truth', 'accepted_game_identity_truth', 'accepted_release_truth', 'accepted_platform_truth', 'accepted_emulator_compatibility_truth', 'accepted_hashset_truth', 'accepted_rom_disc_media_truth', 'accepted_game_relation_truth', 'accepted_action_permission', 'accepted_rights_safety_truth', 'accepted_public_record', 'public_index_mutated', 'master_index_mutated', 'rights_clearance_claimed', 'legal_acquisition_claimed', 'rom_authenticity_claimed', 'disc_authenticity_claimed', 'compatibility_correctness_claimed', 'playability_claimed', 'installability_claimed', 'malware_safety_claimed', 'content_safety_claimed', 'privacy_safety_claimed', 'verified_authenticity_claimed', 'production_readiness_claimed', 'download_permission_granted', 'upload_permission_granted', 'hash_submission_permission_granted', 'execution_permission_granted', 'acquisition_permission_granted', 'changed_public_search_behavior', 'enabled_hosting', 'enabled_live_probes', 'enabled_source_sync', 'enabled_downloads', 'enabled_uploads', 'enabled_execution', 'enabled_acquisition_actions', 'enabled_crawling', 'enabled_scraping', 'enabled_accounts', 'enabled_telemetry', 'mutated_public_index', 'mutated_master_index', 'network_calls_made', 'api_calls_made', 'catalog_fetch_used', 'software_list_fetch_used', 'hashset_fetch_used', 'rom_download_used', 'iso_download_used', 'disc_image_download_used', 'chd_download_used', 'bios_firmware_download_used', 'game_binary_download_used', 'emulator_download_used', 'installer_download_used', 'patch_download_used', 'asset_download_used', 'file_upload_used', 'hash_submission_used', 'emulator_execution_used', 'game_execution_used', 'install_execute_used', 'acquisition_action_used', 'scraping_used', 'crawling_used', 'browser_automation_used', 'restricted_source_access_used', 'bypass_or_automation_used', 'live_probe_default_enabled', 'source_sync_enabled', 'public_query_fanout_enabled', 'api_query_enabled', 'catalog_fetch_enabled', 'software_list_fetch_enabled', 'hashset_fetch_enabled', 'rom_download_enabled', 'iso_download_enabled', 'disc_image_download_enabled', 'chd_download_enabled', 'bios_firmware_download_enabled', 'game_binary_download_enabled', 'emulator_download_enabled', 'installer_download_enabled', 'patch_download_enabled', 'asset_download_enabled', 'file_upload_enabled', 'hash_submission_enabled', 'emulator_execution_enabled', 'game_execution_enabled', 'install_execute_enabled', 'acquisition_action_enabled', 'scraping_enabled', 'crawling_enabled', 'browser_automation_enabled', 'restricted_source_enabled', 'bypass_or_automation_enabled'])


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H10 games emulation live probe validation", file=stdout)
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
    if tuple(H10_SOURCE_IDS) != EXPECTED_SOURCES:
        errors.append("runtime H10 source IDs do not match expected live-probe sources")
    return {
        "schema_version": "h10_games_emulation_live_probe_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H10-BUNDLE-03",
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
        "software_list_fetch_enabled",
        "hashset_fetch_enabled",
        "rom_download_enabled",
        "iso_download_enabled",
        "disc_image_download_enabled",
        "chd_download_enabled",
        "bios_firmware_download_enabled",
        "game_binary_download_enabled",
        "emulator_download_enabled",
        "installer_download_enabled",
        "patch_download_enabled",
        "asset_download_enabled",
        "file_upload_enabled",
        "hash_submission_enabled",
        "emulator_execution_enabled",
        "game_execution_enabled",
        "install_execute_enabled",
        "acquisition_action_enabled",
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
        errors.append("allowed requests policy must list all H10 sources")
    bundle = load_h10_games_emulation_live_probe_policy_bundle(REPO_ROOT)
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
            "api_query_approved",
            "catalog_fetch_approved",
            "software_list_fetch_approved",
            "hashset_fetch_approved",
            "rom_download_approved",
            "iso_download_approved",
            "disc_image_download_approved",
            "chd_download_approved",
            "bios_firmware_download_approved",
            "game_binary_download_approved",
            "emulator_download_approved",
            "installer_download_approved",
            "patch_download_approved",
            "asset_download_approved",
            "file_upload_approved",
            "hash_submission_approved",
            "emulator_execution_approved",
            "game_execution_approved",
            "install_execute_approved",
            "acquisition_action_approved",
            "scraping_approved",
            "crawling_approved",
            "browser_automation_approved",
            "restricted_rights_sensitive_source_approved",
            "drm_or_access_control_bypass_approved",
            "bypass_or_automation_approved",
            "public_query_fanout_approved",
        ):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        request_key = str((item.get("planned_request_keys") or [""])[0])
        if validate_h10_source_approval(source_id, request_key, bundle)["approved"]:
            errors.append(f"{source_id}: live approval unexpectedly passes")
    output = payloads.get(POLICIES[6], {})
    for key in [
        "source_cache_write_current",
        "evidence_ledger_write_current",
        "review_queue_write_current",
        "live_sync_state",
        "api_query_sync_result",
        "catalog_fetch_result",
        "software_list_fetch_result",
        "hashset_fetch_result",
        "ROM_payload",
        "ISO_payload",
        "disc_image_payload",
        "CHD_payload",
        "BIOS_firmware_payload",
        "game_binary_payload",
        "emulator_payload",
        "installer_payload",
        "patch_payload",
        "asset_payload",
        "file_upload_payload",
        "hash_submission_payload",
        "emulator_execution_output",
        "game_execution_output",
        "install_execute_output",
        "acquisition_action_output",
        "scraping_output",
        "crawling_output",
        "restricted_source_access_output",
        "accepted_game_identity_truth",
        "accepted_release_truth",
        "accepted_platform_truth",
        "accepted_emulator_compatibility_truth",
        "accepted_hashset_truth",
        "accepted_rom_disc_media_truth",
        "accepted_game_relation_truth",
        "accepted_action_permission",
        "accepted_rights_safety_truth",
        "accepted_source_truth",
        "accepted_evidence_truth",
        "accepted_candidate_truth",
        "accepted_public_record",
        "public_index_mutation",
        "master_index_mutation",
        "rights_clearance",
        "legal_acquisition_truth",
        "ROM_authenticity_truth",
        "disc_authenticity_truth",
        "compatibility_correctness",
        "playability_truth",
        "installability_truth",
        "malware_safety",
        "content_safety_truth",
        "privacy_safety",
        "verified_authenticity",
        "production_readiness_claim",
    ]:
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"output policy must forbid {key}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for source_id in RESULT_EXAMPLE_SOURCES:
        request_name = f"approved_{source_id}_probe_request_v0.json"
        for path in (
            root / "examples/connectors/h10_games_emulation/live_probe" / request_name,
            root / "examples/connectors/h10_games_emulation/live_probe_results" / f"{source_id}_live_probe_result_example_v0.json",
        ):
            payload = load_json_object(path, errors)
            if payload is not None:
                validate_no_forbidden_claims(path.as_posix(), payload, errors)
    for rel in (
        "examples/connectors/h10_games_emulation/live_probe/blocked_live_probe_request_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_results/blocked_live_probe_result_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/source_cache_candidate_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/evidence_candidate_preview_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/review_queue_seed_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/connector_health_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/game_software_identity_candidate_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/platform_release_edition_candidate_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/emulator_compatibility_candidate_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/preservation_hashset_candidate_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/rom_disc_media_identity_candidate_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/game_relation_candidate_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/emulator_action_candidate_from_h10_probe_v0.json",
        "examples/connectors/h10_games_emulation/live_probe_outputs/games_rights_safety_candidate_from_h10_probe_v0.json",
    ):
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            validate_no_forbidden_claims(rel, payload, errors)


def validate_runtime_imports(errors: list[str]) -> None:
    try:
        importlib.import_module("runtime.connectors.h10_games_emulation.live_probe_common")
        for source_id in EXPECTED_SOURCES:
            importlib.import_module(f"runtime.connectors.h10_games_emulation.live_probe_{source_id}")
        importlib.import_module("scripts.run_h10_games_emulation_live_probe")
        importlib.import_module("scripts.summarize_h10_games_emulation_live_probe_outputs")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"runtime/script import failed: {exc}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"banned network/client/provider import in {rel}")
        if CLIENT_CALL_RE.search(text):
            errors.append(f"banned client/provider call in {rel}")
        if rel.startswith("runtime/") and "urlopen(" in text:
            errors.append(f"live urlopen execution is not implemented in H10-BUNDLE-03: {rel}")


def validate_cli_offline(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        output = Path(tempdir) / "probe.json"
        run = subprocess.run(
            [sys.executable, "scripts/run_h10_games_emulation_live_probe.py", "--source-id", "mobygames", "--request-key", "example_game_metadata", "--output", str(output), "--json"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if run.returncode != 0:
            errors.append(f"live probe CLI offline path failed: {run.stdout} {run.stderr}")
        elif not output.is_file():
            errors.append("live probe CLI did not write explicit temp output")
        else:
            payload = json.loads(output.read_text(encoding="utf-8"))
            if payload.get("network_used") is not False:
                errors.append("live probe CLI output used network")
    forbidden = subprocess.run(
        [sys.executable, "scripts/run_h10_games_emulation_live_probe.py", "--source-id", "mobygames", "--request-key", "example_game_metadata", "--output", "site/dist/probe.json", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if forbidden.returncode == 0:
        errors.append("live probe CLI accepted forbidden site/dist output")
    for forbidden_path in ("data/public_index/probe.json", "roms/probe.json", "bios/probe.json", "emulators/probe.json", "actions/probe.json"):
        run = subprocess.run(
            [sys.executable, "scripts/run_h10_games_emulation_live_probe.py", "--source-id", "mobygames", "--request-key", "example_game_metadata", "--output", forbidden_path, "--json"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if run.returncode == 0:
            errors.append(f"live probe CLI accepted forbidden output root {forbidden_path}")
    summary = subprocess.run(
        [sys.executable, "scripts/summarize_h10_games_emulation_live_probe_outputs.py", "--input", "examples/connectors/h10_games_emulation/live_probe_results", "--check", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if summary.returncode != 0:
        errors.append(f"live probe summary script failed: {summary.stdout} {summary.stderr}")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    for directory in (
        root / "examples/connectors/h10_games_emulation/live_probe_results",
        root / "examples/connectors/h10_games_emulation/live_probe_outputs",
        root / "control/audits/h10-bundle-03-games-emulation-live-probes-v0/generated",
    ):
        for path in directory.glob("*.json"):
            payload = load_json_object(path, errors)
            if payload is not None:
                validate_no_forbidden_claims(path.as_posix(), payload, errors)


def validate_no_forbidden_claims(label: str, payload: Any, errors: list[str]) -> None:
    text = json.dumps(payload, sort_keys=True)
    if SECRET_KEY_RE.search(text):
        errors.append(f"secret-like key in {label}")
    if PAYLOAD_BODY_RE.search(text):
        errors.append(f"game/emulation payload or scrape/crawl body-like key in {label}")
    truth_errors = detect_h10_games_emulation_live_probe_truth_boundary_violations(payload, {})
    product_errors = detect_h10_games_emulation_live_probe_product_boundary_violations(payload, {})
    for err in truth_errors + product_errors:
        errors.append(f"{label}: {err}")
    if isinstance(payload, Mapping) and payload.get("network_used") is True:
        errors.append(f"{label} claims network use")
    if isinstance(payload, Mapping) and payload.get("request_count", 0) not in (0, "0"):
        if payload.get("result_status") != "live_probe_completed":
            errors.append(f"{label} has request_count without live completion")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "roms", "isos", "disc_images", "bios", "firmware", "emulators", "game_installs", "hash_submissions", "storefront_accounts", "restricted_sources"):
        if (root / rel).exists():
            errors.append(f"local private or forbidden root exists: {rel}")


def load_json_object(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"missing required JSON file: {path.relative_to(REPO_ROOT).as_posix() if path.is_absolute() else path.as_posix()}")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path}: {exc}")
        return None
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
