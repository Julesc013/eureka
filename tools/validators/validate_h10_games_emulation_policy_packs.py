#!/usr/bin/env python3
"""Validate H10-BUNDLE-01 games/emulation policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FAMILY = "games_emulation_software_identity"
SOURCE_IDS = ['mobygames', 'mame_software_lists', 'scummvm_compatibility', 'redump_hash_sets', 'no_intro_hash_sets', 'tosec_hash_sets', 'flashpoint_metadata', 'steam_game_metadata_policy_limited', 'gog_game_metadata_policy_limited', 'itchio_game_metadata_policy_limited', 'generic_game_database', 'generic_emulator_compatibility', 'generic_preservation_hashset', 'games_emulation_policy_blocked']
SOURCE_FILES = {'mobygames': 'mobygames_source_v2.json', 'mame_software_lists': 'mame_software_lists_source_v2.json', 'scummvm_compatibility': 'scummvm_compatibility_source_v2.json', 'redump_hash_sets': 'redump_hash_sets_source_v2.json', 'no_intro_hash_sets': 'no_intro_hash_sets_source_v2.json', 'tosec_hash_sets': 'tosec_hash_sets_source_v2.json', 'flashpoint_metadata': 'flashpoint_metadata_source_v2.json', 'steam_game_metadata_policy_limited': 'steam_game_metadata_policy_limited_source_v2.json', 'gog_game_metadata_policy_limited': 'gog_game_metadata_policy_limited_source_v2.json', 'itchio_game_metadata_policy_limited': 'itchio_game_metadata_policy_limited_source_v2.json', 'generic_game_database': 'generic_game_database_source_v2.json', 'generic_emulator_compatibility': 'generic_emulator_compatibility_source_v2.json', 'generic_preservation_hashset': 'generic_preservation_hashset_source_v2.json', 'games_emulation_policy_blocked': 'games_emulation_policy_blocked_source_v2.json'}
POLICY_FILES_BY_SOURCE = {'mobygames': 'mobygames_policy_pack_v0.json', 'mame_software_lists': 'mame_software_lists_policy_pack_v0.json', 'scummvm_compatibility': 'scummvm_compatibility_policy_pack_v0.json', 'redump_hash_sets': 'redump_hash_sets_policy_pack_v0.json', 'no_intro_hash_sets': 'no_intro_hash_sets_policy_pack_v0.json', 'tosec_hash_sets': 'tosec_hash_sets_policy_pack_v0.json', 'flashpoint_metadata': 'flashpoint_metadata_policy_pack_v0.json', 'steam_game_metadata_policy_limited': 'steam_game_metadata_policy_limited_pack_v0.json', 'gog_game_metadata_policy_limited': 'gog_game_metadata_policy_limited_pack_v0.json', 'itchio_game_metadata_policy_limited': 'itchio_game_metadata_policy_limited_pack_v0.json', 'generic_game_database': 'generic_game_database_policy_pack_v0.json', 'generic_emulator_compatibility': 'generic_emulator_compatibility_policy_pack_v0.json', 'generic_preservation_hashset': 'generic_preservation_hashset_policy_pack_v0.json', 'games_emulation_policy_blocked': 'games_emulation_policy_blocked_pack_v0.json'}
INVENTORY_FILES = (
    "control/inventory/source_packs/h10_games_emulation_source_pack_policy.json",
    "control/inventory/source_packs/h10_games_emulation_sources.json",
    "control/inventory/source_packs/h10_games_emulation_connector_families.json",
    "control/inventory/source_packs/h10_game_software_identity_policy.json",
    "control/inventory/source_packs/h10_platform_release_edition_policy.json",
    "control/inventory/source_packs/h10_emulator_compatibility_policy.json",
    "control/inventory/source_packs/h10_preservation_hashset_policy.json",
    "control/inventory/source_packs/h10_rom_disc_media_identity_policy.json",
    "control/inventory/source_packs/h10_game_relation_policy.json",
    "control/inventory/source_packs/h10_emulator_action_candidate_policy.json",
    "control/inventory/source_packs/h10_games_rights_safety_policy.json",
    "control/inventory/source_packs/h10_games_emulation_approval_gates.json",
    "control/inventory/source_packs/h10_games_emulation_output_policy.json",
    "control/inventory/source_packs/h10_games_emulation_truth_policy.json",
    "control/inventory/source_packs/h10_games_emulation_no_live_call_policy.json",
    "control/inventory/source_packs/h10_games_emulation_no_download_execute_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/source_packs/h10_games_emulation_source_pack_manifest_v0.json",
    "examples/source_packs/h10_games_emulation_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/connectors/h10_games_emulation/coverage/h10_games_emulation_coverage_preview_v0.json",
    "examples/connectors/h10_games_emulation/scorecards/h10_games_emulation_scorecard_preview_v0.json",
)
DOCS = (
    "docs/reference/H10_GAMES_EMULATION_SOURCE_PACKS.md",
    "docs/reference/H10_GAME_SOFTWARE_IDENTITY_POLICY.md",
    "docs/reference/H10_PLATFORM_RELEASE_EDITION_POLICY.md",
    "docs/reference/H10_EMULATOR_COMPATIBILITY_POLICY.md",
    "docs/reference/H10_PRESERVATION_HASHSET_POLICY.md",
    "docs/reference/H10_ROM_DISC_MEDIA_IDENTITY_POLICY.md",
    "docs/reference/H10_GAME_RELATION_POLICY.md",
    "docs/reference/H10_EMULATOR_ACTION_CANDIDATE_POLICY.md",
    "docs/reference/H10_GAMES_RIGHTS_SAFETY_POLICY.md",
    "docs/architecture/H10_GAMES_EMULATION_MODEL.md",
    "docs/architecture/GAMES_EMULATION_SOURCE_FAMILY_MODEL.md",
    "docs/operations/H10_GAMES_EMULATION_POLICY_GATES.md",
    "docs/operations/H10_GAMES_EMULATION_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H10_GAMES_EMULATION_NO_DOWNLOAD_EXECUTE_POLICY.md",
    "docs/operations/H10_GAMES_EMULATION_FIXTURE_PLAN.md",
)
AUDIT_FILES = tuple(
    f"control/audits/h10-bundle-01-games-emulation-policy-packs-v0/{name}"
    for name in (
        "README.md",
        "h10_bundle_01_report.json",
        "h10_source_pack_summary.md",
        "h10_source_policy_gate_summary.md",
        "h10_connector_family_summary.md",
        "h10_game_software_identity_policy_summary.md",
        "h10_platform_release_edition_policy_summary.md",
        "h10_emulator_compatibility_policy_summary.md",
        "h10_preservation_hashset_policy_summary.md",
        "h10_rom_disc_media_identity_policy_summary.md",
        "h10_game_relation_policy_summary.md",
        "h10_emulator_action_candidate_policy_summary.md",
        "h10_games_rights_safety_policy_summary.md",
        "h10_fixture_plan.md",
        "h10_no_live_call_report.md",
        "h10_no_download_execute_report.md",
        "h10_readiness_for_fixture_runtime.md",
        "validation.md",
        "generated/sample_h10_source_summary.json",
        "generated/sample_h10_source_summary.md",
        "generated/sample_h10_option_matrix.json",
    )
)
H10_PYTHON_FILES = (
    "scripts/validate_h10_games_emulation_policy_packs.py",
    "scripts/summarize_h10_games_emulation_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {'record_rights_safety_policy', 'create_scorecard_preview', 'record_identity_policy', 'create_coverage_preview', 'inspect_fixture', 'record_relation_policy', 'record_source_policy', 'record_source_metadata_preview', 'normalize_fixture_future'}
FALSE_REQUIRED_KEYS = {
    "live_access_enabled",
    "source_sync_enabled",
    "connector_runtime_enabled",
    "approved_live_probe_enabled",
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
    "media_asset_download_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "file_upload_enabled",
    "hash_submission_enabled",
    "emulator_execution_enabled",
    "game_execution_enabled",
    "install_execute_enabled",
    "acquisition_action_enabled",
    "scraping_enabled",
    "crawling_enabled",
    "bypass_or_automation_enabled",
    "restricted_rights_sensitive_source_enabled",
    "source_pack_import_enabled",
}
FORBIDDEN_TRUE_KEYS = FALSE_REQUIRED_KEYS | {
    "source_pack_is_truth",
    "source_pack_is_accepted_evidence",
    "source_pack_is_imported_state",
    "policy_pack_grants_live_access",
    "capability_grants_permission",
    "coverage_preview_is_exhaustive",
    "coverage_preview_claims_exhaustive_coverage",
    "coverage_manifest_is_exhaustive_global_coverage",
    "scorecard_preview_is_production_ready",
    "scorecard_claims_production_readiness",
    "scorecard_auto_approves_future_connectors",
    "production_ready",
    "auto_approves_future_connectors",
    "game_software_metadata_is_game_truth",
    "game_software_identity_candidate_is_truth",
    "release_metadata_is_release_truth",
    "platform_metadata_is_platform_truth",
    "platform_release_edition_candidate_is_truth",
    "emulator_compatibility_metadata_is_compatibility_truth",
    "emulator_compatibility_candidate_is_truth",
    "hashset_metadata_is_hashset_truth",
    "preservation_hashset_candidate_is_truth",
    "rom_disc_media_metadata_is_media_truth",
    "rom_disc_media_candidate_is_truth",
    "game_relation_candidate_is_relation_truth",
    "emulator_action_candidate_is_action_permission",
    "rights_safety_metadata_is_rights_or_safety_truth",
    "hash_metadata_proves_authenticity",
    "storefront_metadata_grants_acquisition_permission",
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
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
    "public_index_mutated",
    "master_index_mutated",
    "mutated_public_index",
    "mutated_master_index",
    "rights_clearance_claimed",
    "legal_acquisition_claimed",
    "rom_authenticity_claimed",
    "disc_authenticity_claimed",
    "compatibility_correctness_claimed",
    "installability_claimed",
    "playability_claimed",
    "malware_safety_claimed",
    "content_safety_claimed",
    "privacy_safety_claimed",
    "verified_authenticity_claimed",
    "production_readiness_claimed",
}
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_RE = re.compile(
    r"[^a-z0-9](api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^a-z0-9]",
    re.IGNORECASE,
)
PAYLOAD_KEY_RE = re.compile(
    r"(rom_payload|iso_payload|disc_image_payload|chd_payload|bios_payload|firmware_payload|game_binary_payload|emulator_payload|installer_payload|launcher_payload|patch_payload|crack_payload|key_payload|serial_payload|asset_payload|archive_payload|file_upload_payload|hash_submission_payload|execution_log|acquisition_output|restricted_payload|scraping_output|crawling_output|browser_automation_output)",
    re.IGNORECASE,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON validation result.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H10 games emulation policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"][:25]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required = list(INVENTORY_FILES) + list(SOURCE_PACK_EXAMPLES) + list(EXTRA_EXAMPLES) + list(DOCS) + list(AUDIT_FILES) + list(H10_PYTHON_FILES)
    required.extend(f"examples/sources/source_records/{SOURCE_FILES[source_id]}" for source_id in SOURCE_IDS)
    required.extend(f"examples/connectors/h10_games_emulation/policies/{POLICY_FILES_BY_SOURCE[source_id]}" for source_id in SOURCE_IDS)
    for rel in required:
        path = repo_root / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
    known = _load_known_values(repo_root, errors)
    for rel in required:
        if rel.endswith(".json") and (repo_root / rel).exists():
            try:
                payload = _load_json(repo_root / rel)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{rel} invalid JSON: {exc}")
                continue
            _scan_json_payload(rel, payload, errors)

    inventory_path = repo_root / "control/inventory/source_packs/h10_games_emulation_sources.json"
    if inventory_path.exists():
        inventory = _load_json(inventory_path)
        sources = inventory.get("sources", [])
        if len(sources) != 14:
            errors.append("H10 source inventory must contain 14 sources")
        seen = [str(item.get("source_id")) for item in sources if isinstance(item, Mapping)]
        if sorted(seen) != sorted(SOURCE_IDS):
            errors.append("H10 source inventory source IDs do not match required H10 source IDs")
        if len(seen) != len(set(seen)):
            errors.append("H10 source inventory contains duplicate source IDs")
        for source in sources:
            if isinstance(source, Mapping):
                errors.extend(validate_source_record(str(source.get("source_id", "")), source, known))

    for source_id in SOURCE_IDS:
        source_path = repo_root / "examples/sources/source_records" / SOURCE_FILES[source_id]
        if source_path.exists():
            errors.extend(validate_source_record(source_id, _load_json(source_path), known))
        pack_path = repo_root / "examples/connectors/h10_games_emulation/policies" / POLICY_FILES_BY_SOURCE[source_id]
        if pack_path.exists():
            errors.extend(validate_policy_pack(source_id, _load_json(pack_path)))

    coverage_path = repo_root / "examples/connectors/h10_games_emulation/coverage/h10_games_emulation_coverage_preview_v0.json"
    if coverage_path.exists():
        errors.extend(validate_coverage_preview(_load_json(coverage_path)))
    scorecard_path = repo_root / "examples/connectors/h10_games_emulation/scorecards/h10_games_emulation_scorecard_preview_v0.json"
    if scorecard_path.exists():
        errors.extend(validate_scorecard_preview(_load_json(scorecard_path)))

    for rel in H10_PYTHON_FILES:
        path = repo_root / rel
        if path.exists() and BANNED_IMPORT_RE.search(path.read_text(encoding="utf-8")):
            errors.append(f"{rel} imports network/API/model/browser library")

    return {
        "schema_version": "h10_games_emulation_policy_pack_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": 14,
        "errors": errors,
        "network_calls_made": False,
        "model_provider_calls_made": False,
    }


def validate_source_record(source_id: str, payload: Mapping[str, Any], known: Mapping[str, set[str]]) -> list[str]:
    errors: list[str] = []
    if payload.get("source_id") != source_id:
        errors.append(f"{source_id} source_id mismatch")
    if payload.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{source_id} source_family must be {SOURCE_FAMILY}")
    if SOURCE_FAMILY not in known["source_families"]:
        errors.append("games_emulation_software_identity source family missing from source family registry")
    if payload.get("connector_family") not in known["connector_families"]:
        errors.append(f"{source_id} unknown connector_family: {payload.get('connector_family')}")
    if payload.get("trust_lane") not in known["trust_lanes"]:
        errors.append(f"{source_id} unknown trust_lane: {payload.get('trust_lane')}")
    if payload.get("current_index_depth") not in known["index_depths"]:
        errors.append(f"{source_id} unknown current_index_depth: {payload.get('current_index_depth')}")
    if payload.get("current_access_mode") not in {"no_autonomous_access", "committed_fixture_only"}:
        errors.append(f"{source_id} current_access_mode must remain no_autonomous_access or committed_fixture_only")
    for key in FALSE_REQUIRED_KEYS:
        if key in payload and payload.get(key) is not False:
            errors.append(f"{source_id} {key} must be false")
    for key in (
        "game_software_identity_support",
        "platform_release_edition_support",
        "emulator_compatibility_support",
        "preservation_hashset_support",
        "rom_disc_media_identity_support",
        "game_relation_support",
        "emulator_action_candidate_support",
        "rights_safety_support",
    ):
        if not isinstance(payload.get(key), Mapping):
            errors.append(f"{source_id} missing support mapping: {key}")
    _scan_json_payload(source_id, payload, errors)
    return errors


def validate_policy_pack(source_id: str, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("source_id") != source_id:
        errors.append(f"{source_id} policy pack source_id mismatch")
    if payload.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{source_id} policy pack source_family must be {SOURCE_FAMILY}")
    allowed = set(payload.get("allowed_current_operations", []))
    if not allowed.issubset(ALLOWED_CURRENT_OPERATIONS):
        errors.append(f"{source_id} policy pack has unexpected allowed operation")
    if not ALLOWED_CURRENT_OPERATIONS.issubset(allowed):
        errors.append(f"{source_id} policy pack missing required allowed operations")
    _scan_json_payload(f"{source_id} policy pack", payload, errors)
    return errors


def validate_coverage_preview(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("coverage_manifest_is_exhaustive_global_coverage") is not False:
        errors.append("coverage preview must not claim exhaustive global coverage")
    if payload.get("live_access_enabled") is not False:
        errors.append("coverage preview live_access_enabled must be false")
    for key in (
        "records_seen",
        "api_queries_performed",
        "catalog_fetches_performed",
        "software_list_fetches_performed",
        "hashset_fetches_performed",
        "downloads_performed",
        "uploads_performed",
        "executions_performed",
        "acquisition_actions_performed",
        "scraping_crawling_performed",
    ):
        if payload.get(key) != 0:
            errors.append(f"coverage preview {key} must be 0")
    _scan_json_payload("coverage preview", payload, errors)
    return errors


def validate_scorecard_preview(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("production_ready") is not False:
        errors.append("scorecard preview production_ready must be false")
    if payload.get("auto_approves_future_connectors") is not False:
        errors.append("scorecard preview auto_approves_future_connectors must be false")
    for key in ("download_status", "upload_status", "execution_status", "acquisition_action_status", "scraping_crawling_status"):
        if payload.get(key) != "forbidden_current":
            errors.append(f"scorecard preview {key} must be forbidden_current")
    _scan_json_payload("scorecard preview", payload, errors)
    return errors


def _load_known_values(repo_root: Path, errors: list[str]) -> dict[str, set[str]]:
    source_families = set()
    connector_families = set()
    trust_lanes = {"official", "community", "preservation", "restricted_manifest_only", "web_archive_trace", "package_registry", "research_library", "unknown"}
    index_depths = {"D0_source_known", "D1_catalog_indexed", "D1_catalog_indexed_preview_only", "D2_metadata_indexed"}
    try:
        registry = _load_json(repo_root / "control/inventory/sources/source_family_registry.json")
        source_families = {str(item.get("family_id")) for item in registry.get("families", []) if isinstance(item, Mapping)}
    except Exception as exc:  # noqa: BLE001
        errors.append(f"could not load source family registry: {exc}")
    try:
        mapping = _load_json(repo_root / "control/inventory/source_packs/h10_games_emulation_connector_families.json")
        connector_families.update(str(item.get("connector_family")) for item in mapping.get("connector_families", []) if isinstance(item, Mapping))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"could not load H10 connector family mapping: {exc}")
    try:
        registry = _load_json(repo_root / "control/inventory/connectors/connector_family_registry.json")
        connector_families.update(str(item.get("family_id")) for item in registry.get("families", []) if isinstance(item, Mapping))
    except Exception:
        pass
    return {
        "source_families": source_families,
        "connector_families": connector_families,
        "trust_lanes": trust_lanes,
        "index_depths": index_depths,
    }


def _scan_json_payload(label: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            padded = f" {key_text} "
            if SECRET_KEY_RE.search(padded):
                errors.append(f"{label} contains credential-like key: {key_text}")
            if PAYLOAD_KEY_RE.search(key_text):
                errors.append(f"{label} contains forbidden game/emulation payload key: {key_text}")
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{label} forbidden true claim: {key_text}")
            _scan_json_payload(label, item, errors)
    elif isinstance(value, list):
        for item in value:
            _scan_json_payload(label, item, errors)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
