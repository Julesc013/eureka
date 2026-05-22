#!/usr/bin/env python3
"""Validate H9-BUNDLE-02 media metadata fixture runtime offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.fixture_loader import load_h9_media_metadata_fixture  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.normalizer_common import (  # noqa: E402
    H9_FIXTURE_KINDS,
    H9_SOURCE_IDS,
    build_h9_fixture_replay_result,
    detect_h9_product_boundary_violations,
    detect_h9_truth_boundary_violations,
)

CONTRACT_FILES = (
    "contracts/control_schemas/fixtures/h9/connectors/media_metadata_fixture.v0.json",
    "contracts/control_schemas/previews/h9/connectors/media_metadata_normalized_record.v0.json",
    "contracts/control_schemas/previews/h9/connectors/media_object_identity_candidate.v0.json",
    "contracts/control_schemas/previews/h9/connectors/music_work_recording_release_candidate.v0.json",
    "contracts/control_schemas/previews/h9/connectors/image_video_map_identity_candidate.v0.json",
    "contracts/control_schemas/previews/h9/connectors/media_creator_collection_relation_candidate.v0.json",
    "contracts/control_schemas/previews/h9/connectors/media_fingerprint_candidate.v0.json",
    "contracts/control_schemas/previews/h9/connectors/media_rights_license_candidate.v0.json",
    "contracts/control_schemas/previews/h9/connectors/media_safety_privacy_candidate.v0.json",
    "contracts/control_schemas/fixtures/h9/connectors/media_metadata_fixture_replay_result.v0.json",
)
POLICY_FILES = (
    "control/inventory/connectors/h9_media_metadata_fixture_runtime_policy.json",
    "control/inventory/connectors/h9_media_metadata_normalization_policy.json",
    "control/inventory/connectors/h9_media_object_identity_mapping_policy.json",
    "control/inventory/connectors/h9_music_work_recording_release_mapping_policy.json",
    "control/inventory/connectors/h9_image_video_map_identity_mapping_policy.json",
    "control/inventory/connectors/h9_media_creator_collection_relation_mapping_policy.json",
    "control/inventory/connectors/h9_media_fingerprint_mapping_policy.json",
    "control/inventory/connectors/h9_media_rights_license_mapping_policy.json",
    "control/inventory/connectors/h9_media_safety_privacy_mapping_policy.json",
    "control/inventory/connectors/h9_media_metadata_fixture_output_policy.json",
    "control/inventory/connectors/h9_media_metadata_fixture_path_policy.json",
    "control/inventory/connectors/h9_media_metadata_fixture_truth_policy.json",
    "control/inventory/connectors/h9_media_metadata_source_cache_mapping_policy.json",
    "control/inventory/connectors/h9_media_metadata_evidence_mapping_policy.json",
    "control/inventory/connectors/h9_media_metadata_no_download_upload_policy.json",
)
DOC_FILES = (
    "docs/reference/H9_MEDIA_METADATA_FIXTURE_RUNTIME.md",
    "docs/reference/H9_MEDIA_METADATA_NORMALIZED_RECORD.md",
    "docs/reference/H9_MEDIA_OBJECT_IDENTITY_CANDIDATE.md",
    "docs/reference/H9_MUSIC_WORK_RECORDING_RELEASE_CANDIDATE.md",
    "docs/reference/H9_IMAGE_VIDEO_MAP_IDENTITY_CANDIDATE.md",
    "docs/reference/H9_MEDIA_CREATOR_COLLECTION_RELATION_CANDIDATE.md",
    "docs/reference/H9_MEDIA_FINGERPRINT_CANDIDATE.md",
    "docs/reference/H9_MEDIA_RIGHTS_LICENSE_CANDIDATE.md",
    "docs/reference/H9_MEDIA_SAFETY_PRIVACY_CANDIDATE.md",
    "docs/architecture/H9_MEDIA_METADATA_NORMALIZER_MODEL.md",
    "docs/architecture/H9_MEDIA_OBJECT_IDENTITY_MODEL.md",
    "docs/architecture/H9_MUSIC_WORK_RECORDING_RELEASE_MODEL.md",
    "docs/architecture/H9_IMAGE_VIDEO_MAP_IDENTITY_MODEL.md",
    "docs/architecture/H9_MEDIA_CREATOR_COLLECTION_RELATION_MODEL.md",
    "docs/architecture/H9_MEDIA_FINGERPRINT_MODEL.md",
    "docs/architecture/H9_MEDIA_RIGHTS_LICENSE_MODEL.md",
    "docs/architecture/H9_MEDIA_SAFETY_PRIVACY_MODEL.md",
    "docs/operations/H9_MEDIA_METADATA_FIXTURE_REPLAY.md",
    "docs/operations/H9_MEDIA_METADATA_FIXTURE_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H9_MEDIA_METADATA_FIXTURE_NO_DOWNLOAD_UPLOAD_POLICY.md",
)
PYTHON_FILES = (
    "scripts/normalize_h9_media_metadata_fixture.py",
    "scripts/replay_h9_media_metadata_fixtures.py",
    "scripts/validate_h9_media_metadata_fixture_runtime.py",
    "scripts/summarize_h9_media_metadata_fixture_outputs.py",
)
TEST_FILES = (
    "tests/connectors/test_h9_media_metadata_fixture_runtime.py",
    "tests/connectors/test_h9_media_object_identity_mapping.py",
    "tests/connectors/test_h9_music_recording_release_mapping.py",
    "tests/connectors/test_h9_image_video_map_mapping.py",
    "tests/connectors/test_h9_fingerprint_rights_safety_mapping.py",
    "tests/operations/test_h9_media_metadata_fixture_scripts.py",
)
IDENTITY_EXAMPLES = (
    "examples/connectors/h9_media_metadata/identity/media_object_identity_candidate_v0.json",
    "examples/connectors/h9_media_metadata/identity/music_work_recording_release_candidate_v0.json",
    "examples/connectors/h9_media_metadata/identity/image_video_map_identity_candidate_v0.json",
    "examples/connectors/h9_media_metadata/identity/media_creator_collection_relation_candidate_v0.json",
    "examples/connectors/h9_media_metadata/identity/media_fingerprint_candidate_v0.json",
    "examples/connectors/h9_media_metadata/identity/media_rights_license_candidate_v0.json",
    "examples/connectors/h9_media_metadata/identity/media_safety_privacy_candidate_v0.json",
    "examples/connectors/h9_media_metadata/identity/policy_blocked_identity_candidate_v0.json",
)
AUDIT_FILES = (
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/README.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/fixture_runtime_summary.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/normalizer_coverage_summary.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/media_object_identity_mapping_summary.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/music_work_recording_release_mapping_summary.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/image_video_map_identity_mapping_summary.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/media_creator_collection_relation_mapping_summary.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/media_fingerprint_mapping_summary.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/media_rights_license_mapping_summary.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/media_safety_privacy_mapping_summary.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/source_cache_mapping_preview.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/evidence_mapping_preview.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/no_live_call_report.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/no_download_upload_report.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/validation.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_normalized_record.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_media_object_identity_candidate.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_music_work_recording_release_candidate.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_image_video_map_identity_candidate.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_media_creator_collection_relation_candidate.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_media_fingerprint_candidate.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_media_rights_license_candidate.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_media_safety_privacy_candidate.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_source_cache_candidate.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_evidence_candidate_preview.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_fixture_replay_result.json",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/generated/sample_h9_fixture_summary.md",
    "control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/h9_bundle_02_report.json",
)
FIXTURE_ROOT = Path("examples/connectors/h9_media_metadata/fixtures")
NORMALIZED_ROOT = Path("examples/connectors/h9_media_metadata/normalized")
REPLAY_ROOT = Path("examples/connectors/h9_media_metadata/replay_results")

BANNED_RUNTIME_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)
SECRET_KEY_RE = re.compile(r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:', re.IGNORECASE)
PAYLOAD_BODY_RE = re.compile(r'"[^"]*(media_payload_body|image_payload_body|video_payload_body|audio_payload_body|map_payload_body|score_payload_body|thumbnail_payload_body|waveform_payload_body|user_media_payload_body|restricted_payload_body|scraping_output_body|crawling_output_body|browser_automation_output_body)[^"]*"\s*:', re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H9 media metadata fixture runtime validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required_paths = list(CONTRACT_FILES + POLICY_FILES + DOC_FILES + PYTHON_FILES + TEST_FILES + IDENTITY_EXAMPLES + AUDIT_FILES)
    for source_id in H9_SOURCE_IDS:
        for kind in H9_FIXTURE_KINDS:
            filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
            required_paths.append(str(FIXTURE_ROOT / source_id / filename))
        required_paths.append(str(NORMALIZED_ROOT / f"{source_id}_normalized.json"))
        required_paths.append(str(REPLAY_ROOT / f"{source_id}_replay_result.json"))
        required_paths.append(f"archive/prototypes/legacy_runtime/connectors/h9_media_metadata/{source_id}.py")
    required_paths.extend([
        "archive/prototypes/legacy_runtime/connectors/h9_media_metadata/__init__.py",
        "archive/prototypes/legacy_runtime/connectors/h9_media_metadata/fixture_loader.py",
        "archive/prototypes/legacy_runtime/connectors/h9_media_metadata/normalizer_common.py",
        "archive/prototypes/legacy_runtime/connectors/h9_media_metadata/media_object_identity.py",
        "archive/prototypes/legacy_runtime/connectors/h9_media_metadata/music_work_recording_release.py",
        "archive/prototypes/legacy_runtime/connectors/h9_media_metadata/image_video_map_identity.py",
        "archive/prototypes/legacy_runtime/connectors/h9_media_metadata/media_creator_collection_relation.py",
        "archive/prototypes/legacy_runtime/connectors/h9_media_metadata/media_fingerprint.py",
        "archive/prototypes/legacy_runtime/connectors/h9_media_metadata/media_rights_license.py",
        "archive/prototypes/legacy_runtime/connectors/h9_media_metadata/media_safety_privacy.py",
    ])
    for rel in required_paths:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required artifact: {rel}")
            continue
        if path.suffix == ".json":
            load_json_object(path, errors)
    validate_fixtures(root, errors)
    validate_examples(root, errors)
    validate_runtime_imports(errors)
    validate_python_safety(root, errors)
    validate_scripts_offline(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h9_media_metadata_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "source_count": len(H9_SOURCE_IDS),
        "fixture_kinds": list(H9_FIXTURE_KINDS),
        "network_calls_made": False,
        "download_upload_fingerprint_used": False,
        "restricted_source_access_used": False,
    }


def validate_fixtures(root: Path, errors: list[str]) -> None:
    for source_id in H9_SOURCE_IDS:
        normalizer = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h9_media_metadata.{source_id}").normalize
        for kind in H9_FIXTURE_KINDS:
            filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
            rel = FIXTURE_ROOT / source_id / filename
            path = root / rel
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if SECRET_KEY_RE.search(text):
                errors.append(f"secret-like key in fixture: {rel}")
            if PAYLOAD_BODY_RE.search(text):
                errors.append(f"media payload/fetch-output-like field in fixture: {rel}")
            try:
                fixture = load_h9_media_metadata_fixture(path)
                for key in ("live_call_used", "network_used", "external_api_used", "catalog_payload_included", "media_payload_included", "image_payload_included", "video_payload_included", "audio_payload_included", "map_payload_included", "score_payload_included", "thumbnail_payload_included", "waveform_payload_included", "fingerprint_payload_included", "user_media_payload_included", "media_upload_performed", "fingerprint_submission_performed", "fingerprint_generation_performed", "scraping_output_included", "crawling_output_included", "restricted_source_accessed", "bypass_or_automation_used"):
                    if fixture.get(key) is True:
                        errors.append(f"{rel}: {key} must be false")
                normalized = normalizer(fixture)
                replay = build_h9_fixture_replay_result(fixture, normalized)
                errors.extend(f"{rel} normalized: {item}" for item in validate_normalized_record(normalized))
                errors.extend(f"{rel} replay: {item}" for item in validate_replay_result(replay))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"failed to normalize fixture {rel}: {exc}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for source_id in H9_SOURCE_IDS:
        normalized_path = root / NORMALIZED_ROOT / f"{source_id}_normalized.json"
        replay_path = root / REPLAY_ROOT / f"{source_id}_replay_result.json"
        if normalized_path.is_file():
            payload = load_json_object(normalized_path, errors)
            if payload is not None:
                errors.extend(f"{normalized_path.relative_to(root)}: {item}" for item in validate_normalized_record(payload))
        if replay_path.is_file():
            payload = load_json_object(replay_path, errors)
            if payload is not None:
                errors.extend(f"{replay_path.relative_to(root)}: {item}" for item in validate_replay_result(payload))
    for rel in IDENTITY_EXAMPLES:
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            errors.extend(f"{rel}: {item}" for item in validate_candidate_boundary(payload))


def validate_normalized_record(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("schema_version") != "h9_media_metadata_normalized_record.v0":
        errors.append("normalized schema_version must be h9_media_metadata_normalized_record.v0")
    for key in ("source_id", "connector_family", "source_record_kind", "source_cache_candidate_preview", "evidence_candidate_preview", "media_object_identity_candidate", "media_rights_license_candidate", "media_safety_privacy_candidate"):
        if key not in record:
            errors.append(f"normalized record missing {key}")
    errors.extend(detect_h9_truth_boundary_violations(record))
    errors.extend(detect_h9_product_boundary_violations(record))
    return errors


def validate_replay_result(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if result.get("schema_version") != "h9_media_metadata_fixture_replay_result.v0":
        errors.append("replay schema_version must be h9_media_metadata_fixture_replay_result.v0")
    for key in ("no_network_used", "no_live_source_used", "no_api_catalog_query_used", "no_download_upload_fingerprint_used", "no_media_payload_used", "no_scraping_crawling_used", "no_restricted_source_access_used", "no_public_master_index_mutation", "no_truth_acceptance"):
        if result.get(key) is not True:
            errors.append(f"{key} must be true")
    errors.extend(detect_h9_truth_boundary_violations(result))
    errors.extend(detect_h9_product_boundary_violations(result))
    return errors


def validate_candidate_boundary(candidate: Mapping[str, Any]) -> list[str]:
    return detect_h9_truth_boundary_violations(candidate) + detect_h9_product_boundary_violations(candidate)


def validate_runtime_imports(errors: list[str]) -> None:
    for source_id in H9_SOURCE_IDS:
        importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h9_media_metadata.{source_id}")
    for module in ("fixture_loader", "normalizer_common", "media_object_identity", "music_work_recording_release", "image_video_map_identity", "media_creator_collection_relation", "media_fingerprint", "media_rights_license", "media_safety_privacy"):
        importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h9_media_metadata.{module}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    runtime_dir = root / "archive/prototypes/legacy_runtime/connectors/h9_media_metadata"
    for path in runtime_dir.glob("*.py"):
        if path.name.startswith("live_probe_"):
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_RUNTIME_IMPORT_RE.search(text):
            errors.append(f"{path.relative_to(root)}: imports network/provider/browser library")
        lowered = text.casefold()
        for marker in ("requests.", "httpx.", "aiohttp.", "urlopen", "urlretrieve", "selenium", "playwright", "scrapy", "socket.", "openai.", "anthropic."):
            if marker in lowered:
                errors.append(f"{path.relative_to(root)}: contains forbidden live/fetch/scrape/provider marker {marker}")


def validate_scripts_offline(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/normalize_h9_media_metadata_fixture.py", "--source-id", "musicbrainz", "--input", "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json", "--check", "--json"],
        [sys.executable, "scripts/replay_h9_media_metadata_fixtures.py", "--check", "--json"],
        [sys.executable, "scripts/summarize_h9_media_metadata_fixture_outputs.py", "--input", "examples/connectors/h9_media_metadata", "--check", "--json"],
    ]
    for command in commands:
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            errors.append(f"offline script failed: {' '.join(command)} :: {completed.stdout} {completed.stderr}")
    forbidden = subprocess.run([sys.executable, "scripts/normalize_h9_media_metadata_fixture.py", "--source-id", "musicbrainz", "--input", "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json", "--output", "site/dist/h9.json"], cwd=root, text=True, capture_output=True, check=False)
    if forbidden.returncode == 0 or "refusing forbidden output root" not in (forbidden.stdout + forbidden.stderr):
        errors.append("normalizer did not reject forbidden output root site/dist")
    with tempfile.TemporaryDirectory() as tmp:
        completed = subprocess.run([sys.executable, "scripts/normalize_h9_media_metadata_fixture.py", "--source-id", "musicbrainz", "--input", "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json", "--output", str(Path(tmp) / "normalized.json")], cwd=root, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            errors.append(f"normalizer temp output failed: {completed.stdout} {completed.stderr}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "media_downloads", "media_uploads", "fingerprint_cache", "fingerprint_uploads", "image_cache", "video_cache", "audio_cache", "map_downloads", "score_downloads", "restricted_sources"):
        if (root / rel).exists():
            errors.append(f"private/generated forbidden root exists: {rel}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON: {path.relative_to(REPO_ROOT)}: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"JSON artifact must be object: {path.relative_to(REPO_ROOT)}")
        return None
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
