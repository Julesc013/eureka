#!/usr/bin/env python3
"""Validate H10 games/emulation fixture runtime artifacts offline."""

from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h10_games_emulation.fixture_loader import load_h10_games_emulation_fixture  # noqa: E402
from runtime.connectors.h10_games_emulation.normalizer_common import (  # noqa: E402
    H10_FIXTURE_KINDS,
    H10_SOURCE_IDS,
    detect_h10_product_boundary_violations,
    detect_h10_truth_boundary_violations,
)

CONTRACTS = [
    "contracts/connectors/h10_games_emulation_fixture.v0.json",
    "contracts/connectors/h10_games_emulation_normalized_record.v0.json",
    "contracts/connectors/h10_game_software_identity_candidate.v0.json",
    "contracts/connectors/h10_platform_release_edition_candidate.v0.json",
    "contracts/connectors/h10_emulator_compatibility_candidate.v0.json",
    "contracts/connectors/h10_preservation_hashset_candidate.v0.json",
    "contracts/connectors/h10_rom_disc_media_identity_candidate.v0.json",
    "contracts/connectors/h10_game_relation_candidate.v0.json",
    "contracts/connectors/h10_emulator_action_candidate.v0.json",
    "contracts/connectors/h10_games_rights_safety_candidate.v0.json",
    "contracts/connectors/h10_games_emulation_fixture_replay_result.v0.json",
]
POLICIES = [
    "control/inventory/connectors/h10_games_emulation_fixture_runtime_policy.json",
    "control/inventory/connectors/h10_games_emulation_normalization_policy.json",
    "control/inventory/connectors/h10_game_software_identity_mapping_policy.json",
    "control/inventory/connectors/h10_platform_release_edition_mapping_policy.json",
    "control/inventory/connectors/h10_emulator_compatibility_mapping_policy.json",
    "control/inventory/connectors/h10_preservation_hashset_mapping_policy.json",
    "control/inventory/connectors/h10_rom_disc_media_identity_mapping_policy.json",
    "control/inventory/connectors/h10_game_relation_mapping_policy.json",
    "control/inventory/connectors/h10_emulator_action_candidate_mapping_policy.json",
    "control/inventory/connectors/h10_games_rights_safety_mapping_policy.json",
    "control/inventory/connectors/h10_games_emulation_fixture_output_policy.json",
    "control/inventory/connectors/h10_games_emulation_fixture_path_policy.json",
    "control/inventory/connectors/h10_games_emulation_fixture_truth_policy.json",
    "control/inventory/connectors/h10_games_emulation_source_cache_mapping_policy.json",
    "control/inventory/connectors/h10_games_emulation_evidence_mapping_policy.json",
    "control/inventory/connectors/h10_games_emulation_no_download_execute_policy.json",
]
FIXTURE_FILES = {
    "minimal": "minimal_record.json",
    "game_identity": "game_identity_record.json",
    "platform_release_edition": "platform_release_edition_record.json",
    "emulator_compatibility": "emulator_compatibility_record.json",
    "preservation_hashset": "preservation_hashset_record.json",
    "rom_disc_media_identity": "rom_disc_media_identity_record.json",
    "game_relation": "game_relation_record.json",
    "emulator_action_blocked": "emulator_action_blocked_record.json",
    "rights_safety": "rights_safety_record.json",
    "policy_blocked": "policy_blocked_record.json",
}
EXAMPLES = [
    "examples/connectors/h10_games_emulation/identity/game_software_identity_candidate_v0.json",
    "examples/connectors/h10_games_emulation/identity/platform_release_edition_candidate_v0.json",
    "examples/connectors/h10_games_emulation/identity/emulator_compatibility_candidate_v0.json",
    "examples/connectors/h10_games_emulation/identity/preservation_hashset_candidate_v0.json",
    "examples/connectors/h10_games_emulation/identity/rom_disc_media_identity_candidate_v0.json",
    "examples/connectors/h10_games_emulation/identity/game_relation_candidate_v0.json",
    "examples/connectors/h10_games_emulation/identity/emulator_action_candidate_v0.json",
    "examples/connectors/h10_games_emulation/identity/games_rights_safety_candidate_v0.json",
    "examples/connectors/h10_games_emulation/identity/policy_blocked_identity_candidate_v0.json",
]
DOCS = [
    "docs/reference/H10_GAMES_EMULATION_FIXTURE_RUNTIME.md",
    "docs/reference/H10_GAMES_EMULATION_NORMALIZED_RECORD.md",
    "docs/reference/H10_GAME_SOFTWARE_IDENTITY_CANDIDATE.md",
    "docs/reference/H10_PLATFORM_RELEASE_EDITION_CANDIDATE.md",
    "docs/reference/H10_EMULATOR_COMPATIBILITY_CANDIDATE.md",
    "docs/reference/H10_PRESERVATION_HASHSET_CANDIDATE.md",
    "docs/reference/H10_ROM_DISC_MEDIA_IDENTITY_CANDIDATE.md",
    "docs/reference/H10_GAME_RELATION_CANDIDATE.md",
    "docs/reference/H10_EMULATOR_ACTION_CANDIDATE.md",
    "docs/reference/H10_GAMES_RIGHTS_SAFETY_CANDIDATE.md",
    "docs/architecture/H10_GAMES_EMULATION_NORMALIZER_MODEL.md",
    "docs/architecture/H10_GAME_SOFTWARE_IDENTITY_MODEL.md",
    "docs/architecture/H10_PLATFORM_RELEASE_EDITION_MODEL.md",
    "docs/architecture/H10_EMULATOR_COMPATIBILITY_MODEL.md",
    "docs/architecture/H10_PRESERVATION_HASHSET_MODEL.md",
    "docs/architecture/H10_ROM_DISC_MEDIA_IDENTITY_MODEL.md",
    "docs/architecture/H10_GAME_RELATION_MODEL.md",
    "docs/architecture/H10_EMULATOR_ACTION_CANDIDATE_MODEL.md",
    "docs/architecture/H10_GAMES_RIGHTS_SAFETY_MODEL.md",
    "docs/operations/H10_GAMES_EMULATION_FIXTURE_REPLAY.md",
    "docs/operations/H10_GAMES_EMULATION_FIXTURE_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H10_GAMES_EMULATION_FIXTURE_NO_DOWNLOAD_EXECUTE_POLICY.md",
]
SCRIPTS = [
    "scripts/normalize_h10_games_emulation_fixture.py",
    "scripts/replay_h10_games_emulation_fixtures.py",
    "scripts/summarize_h10_games_emulation_fixture_outputs.py",
]
RUNTIME_DIR = "runtime/connectors/h10_games_emulation"
BANNED_IMPORT_RE = re.compile(r"\b(requests|httpx|aiohttp|urllib|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b")
FORBIDDEN_PAYLOAD_KEY_RE = re.compile(r"(downloaded|upload(ed)?|payload_body|binary_body|execution_log|acquisition_output|scraping_output|crawling_output)", re.IGNORECASE)
SECRET_KEY_RE = re.compile(r"(^|_)(api_key|api_token|access_token|auth_token|client_secret|password|private_key|cookie)($|_)", re.IGNORECASE)
FORBIDDEN_TRUE_KEYS = {
    "live_call_used",
    "network_used",
    "external_api_used",
    "rom_payload_included",
    "iso_payload_included",
    "disc_image_payload_included",
    "chd_payload_included",
    "bios_firmware_payload_included",
    "game_binary_payload_included",
    "emulator_payload_included",
    "installer_payload_included",
    "patch_payload_included",
    "asset_payload_included",
    "file_upload_performed",
    "hash_submission_performed",
    "emulator_execution_performed",
    "game_execution_performed",
    "install_execute_performed",
    "acquisition_action_performed",
    "scraping_output_included",
    "crawling_output_included",
    "restricted_source_accessed",
    "bypass_or_automation_used",
}
CLAIM_KEYS = {
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_game_identity_truth",
    "accepted_release_truth",
    "accepted_platform_truth",
    "accepted_emulator_compatibility_truth",
    "accepted_hashset_truth",
    "accepted_rom_disc_media_truth",
    "accepted_game_relation_truth",
    "accepted_action_permission",
    "accepted_rights_safety_truth",
    "accepted_public_record",
    "public_index_mutated",
    "master_index_mutated",
    "rights_clearance_claimed",
    "legal_acquisition_claimed",
    "rom_authenticity_claimed",
    "disc_authenticity_claimed",
    "compatibility_correctness_claimed",
    "playability_claimed",
    "installability_claimed",
    "malware_safety_claimed",
    "content_safety_claimed",
    "privacy_safety_claimed",
    "verified_authenticity_claimed",
    "production_readiness_claimed",
    "download_permission_granted",
    "upload_permission_granted",
    "hash_submission_permission_granted",
    "execution_permission_granted",
    "acquisition_permission_granted",
}


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in CONTRACTS + POLICIES + EXAMPLES + DOCS + SCRIPTS:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required artifact: {rel}")
        elif path.suffix == ".json":
            _load_json(path, errors)
    for source_id in H10_SOURCE_IDS:
        source_dir = root / "examples/connectors/h10_games_emulation/fixtures" / source_id
        if not source_dir.is_dir():
            errors.append(f"missing fixture directory: {source_id}")
            continue
        module = importlib.import_module(f"runtime.connectors.h10_games_emulation.{source_id}")
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
                    loaded = load_h10_games_emulation_fixture(fixture_path)
                    normalized = module.normalize(loaded)
                    errors.extend(detect_h10_truth_boundary_violations(normalized))
                    errors.extend(detect_h10_product_boundary_violations(normalized))
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"normalizer failed for {source_id}/{filename}: {exc}")
        normalized_path = root / "examples/connectors/h10_games_emulation/normalized" / f"{source_id}_normalized_record_v0.json"
        replay_path = root / "examples/connectors/h10_games_emulation/replay_results" / f"{source_id}_replay_result_v0.json"
        if not normalized_path.exists():
            errors.append(f"missing normalized example for {source_id}")
        if not replay_path.exists():
            errors.append(f"missing replay example for {source_id}")
    _scan_runtime(root, errors)
    _run_check([sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--check"], root, errors)
    _run_check([sys.executable, "scripts/replay_h10_games_emulation_fixtures.py", "--check"], root, errors)
    _run_check([sys.executable, "scripts/summarize_h10_games_emulation_fixture_outputs.py", "--input", "examples/connectors/h10_games_emulation", "--check"], root, errors)
    _check_forbidden_output_roots(root, errors)
    for rel in (
        ".aide.local",
        ".local/eureka",
        ".cache/eureka",
        "roms",
        "isos",
        "disc_images",
        "chd",
        "bios",
        "firmware",
        "game_binaries",
        "emulators",
        "installers",
        "patches",
        "game_installs",
        "launchers",
        "hash_submissions",
        "storefront_accounts",
        "restricted_sources",
    ):
        if (root / rel).exists():
            errors.append(f"forbidden private/runtime root exists: {rel}")
    return {
        "schema_version": "h10_games_emulation_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(H10_SOURCE_IDS),
        "fixture_kind_count": len(H10_FIXTURE_KINDS),
        "errors": errors,
        "warnings": warnings,
        "network_calls_made": False,
        "download_upload_execute_acquire_used": False,
        "restricted_source_access_used": False,
    }


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path}: {exc}")
        return None


def _scan_json_boundaries(value: Any, path: Path, errors: list[str], prefix: str = "") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{prefix}.{key}" if prefix else key
            if key in FORBIDDEN_TRUE_KEYS and child is True:
                errors.append(f"forbidden fixture flag true in {path}: {child_path}")
            if key in CLAIM_KEYS and child is True:
                errors.append(f"forbidden truth/product claim in {path}: {child_path}")
            if FORBIDDEN_PAYLOAD_KEY_RE.search(key) and child is not False:
                errors.append(f"forbidden payload/acquisition key in {path}: {child_path}")
            if SECRET_KEY_RE.search(key):
                errors.append(f"forbidden secret-like key in {path}: {child_path}")
            _scan_json_boundaries(child, path, errors, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_json_boundaries(child, path, errors, f"{prefix}[{index}]")


def _scan_runtime(root: Path, errors: list[str]) -> None:
    for path in sorted((root / RUNTIME_DIR).glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"runtime imports or references banned live/network library: {path.relative_to(root).as_posix()}")
        for marker in ("urlopen", "requests.", "httpx.", "aiohttp.", "download(", "upload(", "subprocess.", "Popen", "selenium", "playwright"):
            if marker in text:
                errors.append(f"runtime contains forbidden live/acquisition/execution marker {marker}: {path.relative_to(root).as_posix()}")


def _run_check(command: list[str], root: Path, errors: list[str]) -> None:
    result = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        errors.append(f"command failed: {' '.join(command)} :: {result.stdout}{result.stderr}")


def _check_forbidden_output_roots(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", "site/dist/h10.json"],
        [sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", "data/public_index/h10.json"],
        [sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", "roms/h10.json"],
        [sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", "bios/h10.json"],
        [sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", "emulators/h10.json"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if result.returncode == 0 or "refusing forbidden output root" not in (result.stdout + result.stderr):
            errors.append(f"forbidden output root was not rejected: {' '.join(command)}")
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "normalized.json"
        result = subprocess.run([sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", str(output)], cwd=root, text=True, capture_output=True, check=False)
        if result.returncode != 0 or not output.exists():
            errors.append("normalizer did not write explicit temp output")


def main() -> int:
    result = validate_repo(REPO_ROOT)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
