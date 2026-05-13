#!/usr/bin/env python3
"""Validate H9 media metadata live-probe framework without live calls."""

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

from control.prototypes.legacy_runtime.connectors.h9_media_metadata.live_probe_common import (  # noqa: E402
    H9_SOURCE_IDS,
    detect_h9_media_metadata_live_probe_product_boundary_violations,
    detect_h9_media_metadata_live_probe_truth_boundary_violations,
    load_h9_media_metadata_live_probe_policy_bundle,
    validate_h9_source_approval,
)

EXPECTED_SOURCES = tuple(['wikimedia_commons', 'openverse', 'flickr_commons', 'david_rumsey_maps', 'nasa_image_video', 'met_museum_collection', 'art_institute_chicago', 'musicbrainz', 'discogs', 'rate_your_music_policy_limited', 'acoustid_policy_limited', 'imslp', 'librivox', 'freesound', 'great_78_project', 'live_music_archive', 'smithsonian_folkways', 'prelinger_archives', 'ubuweb_policy_limited', 'vimeo_creative_commons_policy_limited'])
CONTRACTS = tuple(['control/schemas/previews/h9/connectors/media_metadata_live_probe_request.v0.json', 'control/schemas/previews/h9/connectors/media_metadata_live_probe_result.v0.json', 'control/schemas/previews/h9/connectors/media_metadata_live_probe_output_bundle.v0.json', 'control/schemas/previews/h9/connectors/media_metadata_connector_health_summary.v0.json'])
POLICIES = tuple(['control/inventory/connectors/h9_media_metadata_live_probe_policy.json', 'control/inventory/connectors/h9_media_metadata_live_probe_allowed_requests.json', 'control/inventory/connectors/h9_media_metadata_live_probe_endpoint_policy.json', 'control/inventory/connectors/h9_media_metadata_live_probe_rate_limit_policy.json', 'control/inventory/connectors/h9_media_metadata_live_probe_cache_policy.json', 'control/inventory/connectors/h9_media_metadata_live_probe_kill_switch_policy.json', 'control/inventory/connectors/h9_media_metadata_live_probe_output_policy.json', 'control/inventory/connectors/h9_media_metadata_live_probe_path_policy.json', 'control/inventory/connectors/h9_media_metadata_live_probe_review_policy.json', 'control/inventory/connectors/h9_media_metadata_live_probe_truth_policy.json', 'control/inventory/connectors/h9_media_metadata_live_probe_no_download_upload_policy.json', 'control/inventory/connectors/h9_media_metadata_live_probe_restricted_source_policy.json'])
DOCS = tuple(['docs/reference/H9_MEDIA_METADATA_LIVE_PROBE.md', 'docs/reference/H9_MEDIA_METADATA_LIVE_PROBE_RESULT.md', 'docs/reference/H9_MEDIA_METADATA_CONNECTOR_HEALTH_SUMMARY.md', 'docs/architecture/H9_MEDIA_METADATA_LIVE_PROBE_MODEL.md', 'docs/operations/H9_MEDIA_METADATA_LIVE_PROBE_APPROVAL_GATES.md', 'docs/operations/H9_MEDIA_METADATA_LIVE_PROBE_REVIEW.md', 'docs/operations/H9_MEDIA_METADATA_LIVE_PROBE_BLOCKED_MODE.md', 'docs/operations/H9_MEDIA_METADATA_LIVE_PROBE_NO_DOWNLOAD_UPLOAD_POLICY.md', 'docs/operations/H9_MEDIA_METADATA_LIVE_PROBE_RESTRICTED_SOURCE_POLICY.md'])
AUDIT_DIR = Path("control/audits/h9-bundle-03-media-metadata-live-probes-v0")
AUDIT_FILES = tuple(['README.md', 'h9_bundle_03_report.json', 'live_probe_policy_review.md', 'live_probe_execution_report.md', 'media_object_identity_candidate_preview.md', 'music_work_recording_release_candidate_preview.md', 'image_video_map_identity_candidate_preview.md', 'media_creator_collection_relation_candidate_preview.md', 'media_fingerprint_candidate_preview.md', 'media_rights_license_candidate_preview.md', 'media_safety_privacy_candidate_preview.md', 'source_cache_candidate_preview.md', 'evidence_candidate_preview.md', 'review_queue_seed_preview.md', 'connector_health_summary.md', 'no_download_upload_report.md', 'restricted_source_policy_report.md', 'h9_live_probe_blocked_or_completed_summary.md', 'validation.md', 'generated/sample_h9_live_probe_result.json', 'generated/sample_h9_media_object_identity_candidate_from_probe.json', 'generated/sample_h9_music_work_recording_release_candidate_from_probe.json', 'generated/sample_h9_image_video_map_identity_candidate_from_probe.json', 'generated/sample_h9_media_creator_collection_relation_candidate_from_probe.json', 'generated/sample_h9_media_fingerprint_candidate_from_probe.json', 'generated/sample_h9_media_rights_license_candidate_from_probe.json', 'generated/sample_h9_media_safety_privacy_candidate_from_probe.json', 'generated/sample_h9_source_cache_candidate_from_probe.json', 'generated/sample_h9_evidence_candidate_preview_from_probe.json', 'generated/sample_h9_review_queue_seed_from_probe.json', 'generated/sample_h9_connector_health_summary.json', 'generated/sample_h9_live_probe_summary.md'])
PYTHON_FILES = tuple(
    ["control/prototypes/legacy_runtime/connectors/h9_media_metadata/live_probe_common.py"]
    + [f"control/prototypes/legacy_runtime/connectors/h9_media_metadata/live_probe_{source_id}.py" for source_id in EXPECTED_SOURCES]
    + [
        "scripts/run_h9_media_metadata_live_probe.py",
        "scripts/validate_h9_media_metadata_live_probe.py",
        "scripts/summarize_h9_media_metadata_live_probe_outputs.py",
    ]
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
CLIENT_CALL_RE = re.compile(r"(?<![\"'])\b(requests|httpx|aiohttp|openai|anthropic)\.")
SECRET_KEY_RE = re.compile(r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:', re.IGNORECASE)
PAYLOAD_BODY_RE = re.compile(r'"[^"]*(media_payload_body|image_payload_body|video_payload_body|audio_payload_body|map_payload_body|score_payload_body|thumbnail_payload_body|waveform_payload_body|user_media_payload_body|restricted_payload_body|scraping_output_body|crawling_output_body|browser_automation_output_body)[^"]*"\s*:', re.IGNORECASE)
FORBIDDEN_TRUE_KEYS = set(['accepted_candidate_truth', 'accepted_creator_collection_relation_truth', 'accepted_evidence_truth', 'accepted_fingerprint_identity_truth', 'accepted_image_video_map_truth', 'accepted_media_identity_truth', 'accepted_music_identity_truth', 'accepted_public_record', 'accepted_rights_license_truth', 'accepted_safety_privacy_truth', 'accepted_source_truth', 'api_calls_made', 'api_query_enabled', 'audio_download_enabled', 'audio_download_used', 'browser_automation_enabled', 'browser_automation_used', 'bypass_or_automation_enabled', 'bypass_or_automation_used', 'catalog_fetch_enabled', 'catalog_fetch_used', 'changed_public_search_behavior', 'content_safety_claimed', 'crawling_enabled', 'crawling_used', 'creative_commons_metadata_is_license_truth', 'creative_commons_truth_claimed', 'creator_collection_relation_candidate_is_truth', 'enabled_accounts', 'enabled_crawling', 'enabled_downloads', 'enabled_fingerprinting', 'enabled_hosting', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'evidence_candidate_preview_is_accepted_evidence', 'evidence_preview_is_accepted_evidence', 'fingerprint_generation_enabled', 'fingerprint_generation_used', 'fingerprint_lookup_enabled', 'fingerprint_lookup_used', 'fingerprint_match_candidate_is_truth', 'fingerprint_submission_enabled', 'fingerprint_submission_used', 'image_download_enabled', 'image_download_used', 'image_video_map_identity_candidate_is_truth', 'license_metadata_is_rights_clearance', 'live_probe_default_enabled', 'live_probe_result_is_public_truth', 'malware_safety_claimed', 'map_download_enabled', 'map_download_used', 'master_index_mutated', 'media_download_enabled', 'media_download_used', 'media_object_identity_candidate_is_truth', 'media_upload_enabled', 'media_upload_used', 'music_identity_candidate_is_truth', 'mutated_master_index', 'mutated_public_index', 'network_calls_made', 'normalized_record_is_public_truth', 'privacy_safety_claimed', 'production_readiness_claimed', 'public_domain_metadata_is_public_domain_truth', 'public_domain_truth_claimed', 'public_index_mutated', 'public_query_fanout_enabled', 'restricted_source_access_used', 'restricted_source_enabled', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'rights_license_candidate_is_rights_truth', 'safety_privacy_candidate_is_safety_truth', 'score_download_enabled', 'score_download_used', 'scraping_enabled', 'scraping_used', 'source_cache_candidate_is_accepted_source', 'source_cache_preview_is_accepted_source', 'source_sync_enabled', 'thumbnail_fetch_enabled', 'thumbnail_fetch_used', 'verified_authenticity_claimed', 'video_download_enabled', 'video_download_used'])


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H9 media metadata live probe validation", file=stdout)
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
    return {
        "schema_version": "h9_media_metadata_live_probe_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H9-BUNDLE-03",
        "offline_default": True,
        "network_calls_made": False,
        "query_fetch_download_upload_fingerprint_used": False,
        "restricted_source_access_used": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    live = payloads.get(POLICIES[0], {})
    for key in ("live_probe_default_enabled", "source_sync_enabled", "public_query_fanout_enabled", "api_query_enabled", "catalog_fetch_enabled", "media_download_enabled", "image_download_enabled", "video_download_enabled", "audio_download_enabled", "map_download_enabled", "score_download_enabled", "thumbnail_fetch_enabled", "media_upload_enabled", "fingerprint_lookup_enabled", "fingerprint_submission_enabled", "fingerprint_generation_enabled", "scraping_enabled", "crawling_enabled", "browser_automation_enabled", "restricted_source_enabled", "bypass_or_automation_enabled"):
        if live.get(key) is not False:
            errors.append(f"global policy {key} must be false")
    allowed = payloads.get(POLICIES[1], {})
    sources = allowed.get("sources", [])
    if sorted(item.get("source_id") for item in sources if isinstance(item, Mapping)) != sorted(EXPECTED_SOURCES):
        errors.append("allowed requests policy must list all H9 sources")
    bundle = load_h9_media_metadata_live_probe_policy_bundle(REPO_ROOT)
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
        for key in ("source_sync_approved", "media_download_approved", "image_download_approved", "video_download_approved", "audio_download_approved", "map_download_approved", "score_download_approved", "thumbnail_fetch_approved", "media_upload_approved", "fingerprint_lookup_approved", "fingerprint_submission_approved", "fingerprint_generation_approved", "user_media_upload_approved", "scraping_approved", "crawling_approved", "browser_automation_approved", "restricted_rights_sensitive_source_approved", "bypass_or_access_control_automation_approved", "public_query_fanout_approved"):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        request_key = str((item.get("planned_request_keys") or [""])[0])
        if validate_h9_source_approval(source_id, request_key, bundle)["approved"]:
            errors.append(f"{source_id}: live approval unexpectedly passes")
    truth = payloads.get(POLICIES[9], {})
    for key in FORBIDDEN_TRUE_KEYS:
        if truth.get(key) is True:
            errors.append(f"truth policy {key} must be false")
    output = payloads.get(POLICIES[6], {})
    for key in ['source_cache_write_current', 'evidence_ledger_write_current', 'review_queue_write_current', 'live_sync_state', 'api_query_sync_result', 'catalog_fetch_result', 'media_payload', 'image_payload', 'video_payload', 'audio_payload', 'map_payload', 'score_payload', 'thumbnail_payload', 'media_upload_payload', 'fingerprint_submission_payload', 'fingerprint_generation_output', 'scraping_output', 'crawling_output', 'restricted_source_access_output', 'accepted_media_identity_truth', 'accepted_music_identity_truth', 'accepted_image_video_map_truth', 'accepted_creator_collection_relation_truth', 'accepted_fingerprint_identity_truth', 'accepted_rights_license_truth', 'accepted_safety_privacy_truth', 'accepted_source_truth', 'accepted_evidence_truth', 'accepted_candidate_truth', 'accepted_public_record', 'public_index_mutation', 'master_index_mutation', 'rights_clearance', 'public_domain_truth', 'creative_commons_truth', 'content_safety_truth', 'privacy_safety', 'malware_safety', 'verified_authenticity', 'production_readiness_claim']:
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"output policy must forbid {key}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for source_id in ('wikimedia_commons', 'openverse', 'nasa_image_video', 'met_museum_collection', 'art_institute_chicago', 'musicbrainz', 'discogs', 'acoustid_policy_limited', 'freesound', 'david_rumsey_maps'):
        for path in (
            root / "examples/connectors/h9_media_metadata/live_probe" / f"approved_{source_id}_probe_request_v0.json",
            root / "examples/connectors/h9_media_metadata/live_probe_results" / f"{source_id}_live_probe_result_example_v0.json",
        ):
            payload = load_json_object(path, errors)
            if payload is not None:
                validate_no_forbidden_claims(path.as_posix(), payload, errors)
    for rel in (
        "examples/connectors/h9_media_metadata/live_probe/blocked_live_probe_request_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_results/blocked_live_probe_result_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/source_cache_candidate_from_h9_probe_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/evidence_candidate_preview_from_h9_probe_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/review_queue_seed_from_h9_probe_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/connector_health_from_h9_probe_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/media_object_identity_candidate_from_h9_probe_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/music_work_recording_release_candidate_from_h9_probe_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/image_video_map_identity_candidate_from_h9_probe_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/media_creator_collection_relation_candidate_from_h9_probe_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/media_fingerprint_candidate_from_h9_probe_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/media_rights_license_candidate_from_h9_probe_v0.json",
        "examples/connectors/h9_media_metadata/live_probe_outputs/media_safety_privacy_candidate_from_h9_probe_v0.json",
    ):
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            validate_no_forbidden_claims(rel, payload, errors)


def validate_runtime_imports(errors: list[str]) -> None:
    try:
        importlib.import_module("control.prototypes.legacy_runtime.connectors.h9_media_metadata.live_probe_common")
        for source_id in EXPECTED_SOURCES:
            importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h9_media_metadata.live_probe_{source_id}")
        importlib.import_module("scripts.run_h9_media_metadata_live_probe")
        importlib.import_module("scripts.summarize_h9_media_metadata_live_probe_outputs")
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
        if "urlopen(" in text and "validate_h9_media_metadata_live_probe_request" not in text:
            errors.append(f"unapproved urlopen path in {rel}")


def validate_cli_offline(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        output = Path(tempdir) / "probe.json"
        run = subprocess.run(
            [sys.executable, "scripts/run_h9_media_metadata_live_probe.py", "--source-id", "musicbrainz", "--request-key", "example_recording_metadata", "--output", str(output), "--json"],
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
        [sys.executable, "scripts/run_h9_media_metadata_live_probe.py", "--source-id", "musicbrainz", "--request-key", "example_recording_metadata", "--output", "site/dist/probe.json", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if forbidden.returncode == 0:
        errors.append("live probe CLI accepted forbidden site/dist output")
    summary = subprocess.run(
        [sys.executable, "scripts/summarize_h9_media_metadata_live_probe_outputs.py", "--input", "examples/connectors/h9_media_metadata/live_probe_results", "--check", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if summary.returncode != 0:
        errors.append(f"live probe summary script failed: {summary.stdout} {summary.stderr}")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    for directory in (
        root / "examples/connectors/h9_media_metadata/live_probe_results",
        root / "examples/connectors/h9_media_metadata/live_probe_outputs",
        root / "control/audits/h9-bundle-03-media-metadata-live-probes-v0/generated",
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
        errors.append(f"media payload or scrape/crawl body-like key in {label}")
    truth_errors = detect_h9_media_metadata_live_probe_truth_boundary_violations(payload, {})
    product_errors = detect_h9_media_metadata_live_probe_product_boundary_violations(payload, {})
    for err in truth_errors + product_errors:
        errors.append(f"{label}: {err}")
    if isinstance(payload, Mapping) and payload.get("network_used") is True:
        errors.append(f"{label} claims network use")
    if isinstance(payload, Mapping) and payload.get("request_count", 0) not in (0, "0"):
        if payload.get("result_status") != "live_probe_completed":
            errors.append(f"{label} has request_count without live completion")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root exists: {rel}")


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
