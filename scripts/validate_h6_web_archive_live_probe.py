#!/usr/bin/env python3
"""Validate H6 web archive live-probe framework without live calls."""

from __future__ import annotations

import argparse
import importlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.live_probe_common import (  # noqa: E402
    H6_SOURCE_IDS,
    detect_h6_web_archive_live_probe_product_boundary_violations,
    detect_h6_web_archive_live_probe_truth_boundary_violations,
    load_h6_web_archive_live_probe_policy_bundle,
    validate_h6_source_approval,
)

EXPECTED_SOURCES = ('wayback_cdx_memento',
 'common_crawl_cdxj',
 'public_warc_wacz_collection',
 'gdelt_news_event',
 'chronicling_america',
 'trove_newspapers',
 'cspan_video_library',
 'aapb_broadcast_archive',
 'archive_today_snapshot',
 'generic_newspaper_archive',
 'generic_web_archive',
 'generic_public_event_trace',
 'restricted_public_document_manifest')
CONTRACTS = ('control/schemas/previews/h6/connectors/web_archive_live_probe_request.v0.json',
 'control/schemas/previews/h6/connectors/web_archive_live_probe_result.v0.json',
 'control/schemas/previews/h6/connectors/web_archive_live_probe_output_bundle.v0.json',
 'control/schemas/previews/h6/connectors/web_archive_connector_health_summary.v0.json')
POLICIES = ('control/inventory/connectors/h6_web_archive_live_probe_policy.json',
 'control/inventory/connectors/h6_web_archive_live_probe_allowed_requests.json',
 'control/inventory/connectors/h6_web_archive_live_probe_endpoint_policy.json',
 'control/inventory/connectors/h6_web_archive_live_probe_rate_limit_policy.json',
 'control/inventory/connectors/h6_web_archive_live_probe_cache_policy.json',
 'control/inventory/connectors/h6_web_archive_live_probe_kill_switch_policy.json',
 'control/inventory/connectors/h6_web_archive_live_probe_output_policy.json',
 'control/inventory/connectors/h6_web_archive_live_probe_path_policy.json',
 'control/inventory/connectors/h6_web_archive_live_probe_review_policy.json',
 'control/inventory/connectors/h6_web_archive_live_probe_truth_policy.json',
 'control/inventory/connectors/h6_web_archive_live_probe_no_fetch_crawl_policy.json',
 'control/inventory/connectors/h6_web_archive_live_probe_sensitive_source_policy.json')
DOCS = ('docs/reference/H6_WEB_ARCHIVE_LIVE_PROBE.md',
 'docs/reference/H6_WEB_ARCHIVE_LIVE_PROBE_RESULT.md',
 'docs/reference/H6_WEB_ARCHIVE_CONNECTOR_HEALTH_SUMMARY.md',
 'docs/architecture/H6_WEB_ARCHIVE_LIVE_PROBE_MODEL.md',
 'docs/operations/H6_WEB_ARCHIVE_LIVE_PROBE_APPROVAL_GATES.md',
 'docs/operations/H6_WEB_ARCHIVE_LIVE_PROBE_REVIEW.md',
 'docs/operations/H6_WEB_ARCHIVE_LIVE_PROBE_BLOCKED_MODE.md',
 'docs/operations/H6_WEB_ARCHIVE_LIVE_PROBE_NO_FETCH_CRAWL_POLICY.md',
 'docs/operations/H6_WEB_ARCHIVE_LIVE_PROBE_SENSITIVE_SOURCE_POLICY.md')
AUDIT_DIR = Path("control/audits/h6-bundle-03-web-archive-live-probes-v0")
AUDIT_FILES = ('README.md',
 'h6_bundle_03_report.json',
 'live_probe_policy_review.md',
 'live_probe_execution_report.md',
 'web_capture_identity_candidate_preview.md',
 'archived_url_time_state_candidate_preview.md',
 'news_event_mention_candidate_preview.md',
 'dead_link_trace_candidate_preview.md',
 'public_document_trace_candidate_preview.md',
 'media_transcript_metadata_candidate_preview.md',
 'source_cache_candidate_preview.md',
 'evidence_candidate_preview.md',
 'review_queue_seed_preview.md',
 'connector_health_summary.md',
 'no_fetch_crawl_report.md',
 'sensitive_source_policy_report.md',
 'h6_live_probe_blocked_or_completed_summary.md',
 'validation.md',
 'generated/sample_h6_live_probe_result.json',
 'generated/sample_h6_web_capture_identity_candidate_from_probe.json',
 'generated/sample_h6_archived_url_time_state_candidate_from_probe.json',
 'generated/sample_h6_news_event_mention_candidate_from_probe.json',
 'generated/sample_h6_dead_link_trace_candidate_from_probe.json',
 'generated/sample_h6_public_document_trace_candidate_from_probe.json',
 'generated/sample_h6_media_transcript_metadata_candidate_from_probe.json',
 'generated/sample_h6_source_cache_candidate_from_probe.json',
 'generated/sample_h6_evidence_candidate_preview_from_probe.json',
 'generated/sample_h6_review_queue_seed_from_probe.json',
 'generated/sample_h6_connector_health_summary.json',
 'generated/sample_h6_live_probe_summary.md')
PYTHON_FILES = tuple(
    ["control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/live_probe_common.py"]
    + [f"control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/live_probe_{source_id}.py" for source_id in EXPECTED_SOURCES]
    + [
        "scripts/run_h6_web_archive_live_probe.py",
        "scripts/validate_h6_web_archive_live_probe.py",
        "scripts/summarize_h6_web_archive_live_probe_outputs.py",
    ]
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
CLIENT_CALL_RE = re.compile(r"(?<![\"'])\b(requests|httpx|aiohttp|openai|anthropic)\.")
SECRET_KEY_RE = re.compile(r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:', re.IGNORECASE)
FORBIDDEN_TRUE_KEYS = set(['accepted_article_truth', 'accepted_candidate_truth', 'accepted_event_truth', 'accepted_evidence_truth', 'accepted_public_document_truth', 'accepted_public_record', 'accepted_source_truth', 'accepted_time_state_truth', 'accepted_web_capture_truth', 'archived_content_proves_rights_clearance', 'archived_time_state_candidate_is_truth', 'capture_digest_proves_authenticity', 'dead_link_trace_grants_acquisition_permission', 'evidence_candidate_preview_is_accepted_evidence', 'live_probe_result_is_public_truth', 'malware_safety_claimed', 'master_index_mutated', 'media_transcript_metadata_is_full_context', 'news_event_mention_candidate_is_event_truth', 'normalized_record_is_public_truth', 'privacy_safety_claimed', 'production_readiness_claimed', 'public_document_trace_is_public_truth', 'public_index_mutated', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'source_cache_candidate_is_accepted_source', 'source_cache_preview_is_accepted_source', 'time_state_candidate_is_historical_truth', 'verified_authenticity_claimed', 'web_capture_candidate_is_truth']) | set(['changed_public_search_behavior', 'enabled_accounts', 'enabled_browser_automation', 'enabled_crawling', 'enabled_downloads', 'enabled_fetching', 'enabled_hosting', 'enabled_live_probes', 'enabled_scraping', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'mutated_master_index', 'mutated_public_index', 'restricted_sensitive_source_access_used']) | {
    "warc_wacz_fetch_enabled",
    "archived_page_fetch_enabled",
    "live_page_fetch_enabled",
    "media_download_enabled",
    "scraping_enabled",
    "crawling_enabled",
    "restricted_sensitive_source_enabled",
    "source_sync_enabled",
    "public_query_fanout_enabled",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H6 web archive live probe validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    for rel in CONTRACTS + POLICIES:
        payloads[rel] = load_json_object(root / rel, errors)
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
        "schema_version": "h6_web_archive_live_probe_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H6-BUNDLE-03",
        "offline_default": True,
        "network_calls_made": False,
        "fetch_crawl_used": False,
        "restricted_source_access_used": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    live = payloads.get("control/inventory/connectors/h6_web_archive_live_probe_policy.json", {})
    for key in (
        "live_probe_default_enabled",
        "source_sync_enabled",
        "public_query_fanout_enabled",
        "warc_wacz_fetch_enabled",
        "archived_page_fetch_enabled",
        "live_page_fetch_enabled",
        "media_download_enabled",
        "scraping_enabled",
        "crawling_enabled",
        "browser_automation_enabled",
        "restricted_sensitive_source_enabled",
        "bypass_or_automation_enabled",
    ):
        if live.get(key) is not False:
            errors.append(f"global policy {key} must be false")
    allowed = payloads.get("control/inventory/connectors/h6_web_archive_live_probe_allowed_requests.json", {})
    sources = allowed.get("sources", [])
    if sorted(item.get("source_id") for item in sources if isinstance(item, Mapping)) != sorted(EXPECTED_SOURCES):
        errors.append("allowed requests policy must list all H6 sources")
    bundle = load_h6_web_archive_live_probe_policy_bundle(REPO_ROOT)
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
            "warc_wacz_fetch_approved",
            "archived_page_fetch_approved",
            "live_page_fetch_approved",
            "media_download_approved",
            "transcript_download_approved",
            "newspaper_page_download_approved",
            "public_document_fetch_approved",
            "restricted_sensitive_source_approved",
            "scraping_approved",
            "crawling_approved",
            "browser_automation_approved",
            "bypass_or_access_control_automation_approved",
            "public_query_fanout_approved",
        ):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        request_key = str((item.get("planned_request_keys") or [""])[0])
        approval = validate_h6_source_approval(source_id, request_key, bundle)
        if approval["approved"]:
            errors.append(f"{source_id}: live approval unexpectedly passes")
    truth = payloads.get("control/inventory/connectors/h6_web_archive_live_probe_truth_policy.json", {})
    for key in ['accepted_article_truth', 'accepted_candidate_truth', 'accepted_event_truth', 'accepted_evidence_truth', 'accepted_public_document_truth', 'accepted_public_record', 'accepted_source_truth', 'accepted_time_state_truth', 'accepted_web_capture_truth', 'archived_content_proves_rights_clearance', 'archived_time_state_candidate_is_truth', 'capture_digest_proves_authenticity', 'dead_link_trace_grants_acquisition_permission', 'evidence_candidate_preview_is_accepted_evidence', 'live_probe_result_is_public_truth', 'malware_safety_claimed', 'master_index_mutated', 'media_transcript_metadata_is_full_context', 'news_event_mention_candidate_is_event_truth', 'normalized_record_is_public_truth', 'privacy_safety_claimed', 'production_readiness_claimed', 'public_document_trace_is_public_truth', 'public_index_mutated', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'source_cache_candidate_is_accepted_source', 'source_cache_preview_is_accepted_source', 'time_state_candidate_is_historical_truth', 'verified_authenticity_claimed', 'web_capture_candidate_is_truth']:
        if truth.get(key) is not False:
            errors.append(f"truth policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h6_web_archive_live_probe_output_policy.json", {})
    for key in (
        "warc_wacz_fetch_result",
        "archived_page_payload",
        "live_page_payload",
        "media_payload",
        "transcript_payload",
        "public_document_payload",
        "scraping_output",
        "crawling_output",
        "sensitive_source_access_output",
        "accepted_web_capture_truth",
        "accepted_time_state_truth",
        "accepted_event_truth",
        "accepted_article_truth",
        "accepted_public_document_truth",
        "accepted_source_truth",
        "accepted_evidence_truth",
        "accepted_candidate_truth",
        "accepted_public_record",
        "public_index_mutation",
        "master_index_mutation",
        "rights_clearance",
        "privacy_safety",
        "malware_safety",
        "verified_authenticity",
        "production_readiness_claim",
    ):
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"output policy must forbid {key}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for source_id in EXPECTED_SOURCES:
        request_path = root / "examples/connectors/h6_web_archive_news_event/live_probe" / f"approved_{source_id}_probe_request_v0.json"
        result_path = root / "examples/connectors/h6_web_archive_news_event/live_probe_results" / f"{source_id}_live_probe_result_example_v0.json"
        for path in (request_path, result_path):
            payload = load_json_object(path, errors)
            validate_no_forbidden_claims(path.as_posix(), payload, errors)
    for rel in (
        "examples/connectors/h6_web_archive_news_event/live_probe/blocked_live_probe_request_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_results/blocked_live_probe_result_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_outputs/source_cache_candidate_from_h6_probe_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_outputs/evidence_candidate_preview_from_h6_probe_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_outputs/review_queue_seed_from_h6_probe_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_outputs/connector_health_from_h6_probe_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_outputs/web_capture_identity_candidate_from_h6_probe_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_outputs/archived_url_time_state_candidate_from_h6_probe_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_outputs/news_event_mention_candidate_from_h6_probe_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_outputs/dead_link_trace_candidate_from_h6_probe_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_outputs/public_document_trace_candidate_from_h6_probe_v0.json",
        "examples/connectors/h6_web_archive_news_event/live_probe_outputs/media_transcript_metadata_candidate_from_h6_probe_v0.json",
    ):
        payload = load_json_object(root / rel, errors)
        validate_no_forbidden_claims(rel, payload, errors)


def validate_runtime_imports(errors: list[str]) -> None:
    for source_id in EXPECTED_SOURCES:
        importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.live_probe_{source_id}")
    importlib.import_module("control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.live_probe_common")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"banned network/model/browser import in {rel}")
        if CLIENT_CALL_RE.search(text):
            errors.append(f"banned provider/network client call in {rel}")


def validate_cli_offline(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/run_h6_web_archive_live_probe.py", "--source-id", "wayback_cdx_memento", "--request-key", "example_capture_metadata", "--check", "--json"],
        [sys.executable, "scripts/summarize_h6_web_archive_live_probe_outputs.py", "--input", "examples/connectors/h6_web_archive_news_event/live_probe_results", "--check", "--json"],
    ]
    for command in commands:
        proc = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            errors.append(f"offline CLI failed: {' '.join(command)} :: {proc.stdout} {proc.stderr}")
    with tempfile.TemporaryDirectory() as tempdir:
        output = Path(tempdir) / "h6_probe.json"
        proc = subprocess.run([
            sys.executable,
            "scripts/run_h6_web_archive_live_probe.py",
            "--source-id",
            "wayback_cdx_memento",
            "--request-key",
            "example_capture_metadata",
            "--output",
            str(output),
            "--json",
        ], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0 or not output.is_file():
            errors.append("CLI explicit temp output failed")
    proc = subprocess.run([
        sys.executable,
        "scripts/run_h6_web_archive_live_probe.py",
        "--source-id",
        "wayback_cdx_memento",
        "--request-key",
        "example_capture_metadata",
        "--output",
        "site/dist/probe.json",
        "--json",
    ], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode == 0:
        errors.append("CLI accepted forbidden site/dist output")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    generated = root / AUDIT_DIR / "generated"
    if generated.is_dir():
        for path in generated.glob("*.json"):
            payload = load_json_object(path, errors)
            validate_no_forbidden_claims(path.as_posix(), payload, errors)


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "crawl", "warc_cache", "media_downloads", "document_dump"):
        if (root / rel).exists():
            errors.append(f"forbidden private/output root exists: {rel}")


def validate_no_forbidden_claims(label: str, payload: Any, errors: list[str]) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if key in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{label} claims forbidden true key: {key}")
            if SECRET_KEY_RE.search(json.dumps({key: value}, sort_keys=True)):
                errors.append(f"{label} includes credential-like key: {key}")
            validate_no_forbidden_claims(label, value, errors)
    elif isinstance(payload, list):
        for item in payload:
            validate_no_forbidden_claims(label, item, errors)


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid or missing JSON {path.as_posix()}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON must be object: {path.as_posix()}")
        return {}
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
