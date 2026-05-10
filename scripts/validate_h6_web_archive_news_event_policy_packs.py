#!/usr/bin/env python3
"""Validate H6-BUNDLE-01 web archive/news/event policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FAMILY = "web_archive_news_event"
EXPECTED_SOURCES = {
    "wayback_cdx_memento": {
        "source_record": "examples/sources/source_records/wayback_cdx_memento_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/wayback_cdx_memento_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/wayback_cdx_memento_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/wayback_cdx_memento_scorecard_preview_v0.json",
    },
    "common_crawl_cdxj": {
        "source_record": "examples/sources/source_records/common_crawl_cdxj_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/common_crawl_cdxj_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/common_crawl_cdxj_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/common_crawl_cdxj_scorecard_preview_v0.json",
    },
    "public_warc_wacz_collection": {
        "source_record": "examples/sources/source_records/public_warc_wacz_collection_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/public_warc_wacz_collection_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/public_warc_wacz_collection_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/public_warc_wacz_collection_scorecard_preview_v0.json",
    },
    "gdelt_news_event": {
        "source_record": "examples/sources/source_records/gdelt_news_event_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/gdelt_news_event_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/gdelt_news_event_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/gdelt_news_event_scorecard_preview_v0.json",
    },
    "chronicling_america": {
        "source_record": "examples/sources/source_records/chronicling_america_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/chronicling_america_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/chronicling_america_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/chronicling_america_scorecard_preview_v0.json",
    },
    "trove_newspapers": {
        "source_record": "examples/sources/source_records/trove_newspapers_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/trove_newspapers_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/trove_newspapers_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/trove_newspapers_scorecard_preview_v0.json",
    },
    "cspan_video_library": {
        "source_record": "examples/sources/source_records/cspan_video_library_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/cspan_video_library_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/cspan_video_library_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/cspan_video_library_scorecard_preview_v0.json",
    },
    "aapb_broadcast_archive": {
        "source_record": "examples/sources/source_records/aapb_broadcast_archive_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/aapb_broadcast_archive_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/aapb_broadcast_archive_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/aapb_broadcast_archive_scorecard_preview_v0.json",
    },
    "archive_today_snapshot": {
        "source_record": "examples/sources/source_records/archive_today_snapshot_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/archive_today_snapshot_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/archive_today_snapshot_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/archive_today_snapshot_scorecard_preview_v0.json",
    },
    "generic_newspaper_archive": {
        "source_record": "examples/sources/source_records/generic_newspaper_archive_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/generic_newspaper_archive_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/generic_newspaper_archive_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/generic_newspaper_archive_scorecard_preview_v0.json",
    },
    "generic_web_archive": {
        "source_record": "examples/sources/source_records/generic_web_archive_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/generic_web_archive_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/generic_web_archive_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/generic_web_archive_scorecard_preview_v0.json",
    },
    "generic_public_event_trace": {
        "source_record": "examples/sources/source_records/generic_public_event_trace_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/generic_public_event_trace_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/generic_public_event_trace_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/generic_public_event_trace_scorecard_preview_v0.json",
    },
    "restricted_public_document_manifest": {
        "source_record": "examples/sources/source_records/restricted_public_document_manifest_source_v2.json",
        "policy_pack": "examples/connectors/h6_web_archive_news_event/policies/restricted_public_document_manifest_policy_pack_v0.json",
        "coverage": "examples/connectors/h6_web_archive_news_event/coverage/restricted_public_document_manifest_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h6_web_archive_news_event/scorecards/restricted_public_document_manifest_scorecard_preview_v0.json",
    },
}
INVENTORY_FILES = (
    "control/inventory/source_packs/h6_web_archive_news_event_source_pack_policy.json",
    "control/inventory/source_packs/h6_web_archive_news_event_sources.json",
    "control/inventory/source_packs/h6_web_archive_news_event_connector_families.json",
    "control/inventory/source_packs/h6_web_capture_identity_policy.json",
    "control/inventory/source_packs/h6_archived_url_time_state_policy.json",
    "control/inventory/source_packs/h6_news_event_mention_policy.json",
    "control/inventory/source_packs/h6_dead_link_trace_policy.json",
    "control/inventory/source_packs/h6_public_document_trace_policy.json",
    "control/inventory/source_packs/h6_web_archive_news_event_approval_gates.json",
    "control/inventory/source_packs/h6_web_archive_news_event_output_policy.json",
    "control/inventory/source_packs/h6_web_archive_news_event_truth_policy.json",
    "control/inventory/source_packs/h6_web_archive_news_event_no_live_call_policy.json",
    "control/inventory/source_packs/h6_web_archive_news_event_no_fetch_crawl_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/source_packs/h6_web_archive_news_event_source_pack_manifest_v0.json",
    "examples/source_packs/h6_web_archive_news_event_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/sources/source_records/web_archive_news_event_policy_blocked_source_v2.json",
    "examples/connectors/h6_web_archive_news_event/policies/web_archive_news_event_policy_blocked_pack_v0.json",
)
DOCS = (
    "docs/reference/H6_WEB_ARCHIVE_NEWS_EVENT_SOURCE_PACKS.md",
    "docs/reference/H6_WEB_CAPTURE_IDENTITY_POLICY.md",
    "docs/reference/H6_ARCHIVED_URL_TIME_STATE_POLICY.md",
    "docs/reference/H6_NEWS_EVENT_MENTION_POLICY.md",
    "docs/reference/H6_DEAD_LINK_TRACE_POLICY.md",
    "docs/reference/H6_PUBLIC_DOCUMENT_TRACE_POLICY.md",
    "docs/architecture/H6_WEB_ARCHIVE_NEWS_EVENT_MODEL.md",
    "docs/architecture/WEB_ARCHIVE_NEWS_EVENT_SOURCE_FAMILY_MODEL.md",
    "docs/operations/H6_WEB_ARCHIVE_NEWS_EVENT_POLICY_GATES.md",
    "docs/operations/H6_WEB_ARCHIVE_NEWS_EVENT_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H6_WEB_ARCHIVE_NEWS_EVENT_NO_FETCH_CRAWL_POLICY.md",
    "docs/operations/H6_WEB_ARCHIVE_NEWS_EVENT_FIXTURE_PLAN.md",
)
AUDIT_FILES = tuple(
    f"control/audits/h6-bundle-01-web-archive-news-event-policy-packs-v0/{name}"
    for name in (
        "README.md",
        "h6_bundle_01_report.json",
        "h6_source_pack_summary.md",
        "h6_source_policy_gate_summary.md",
        "h6_connector_family_summary.md",
        "h6_web_capture_identity_policy_summary.md",
        "h6_archived_url_time_state_policy_summary.md",
        "h6_news_event_mention_policy_summary.md",
        "h6_dead_link_trace_policy_summary.md",
        "h6_public_document_trace_policy_summary.md",
        "h6_fixture_plan.md",
        "h6_no_live_call_report.md",
        "h6_no_fetch_crawl_report.md",
        "h6_readiness_for_fixture_runtime.md",
        "validation.md",
        "generated/sample_h6_source_summary.json",
        "generated/sample_h6_source_summary.md",
        "generated/sample_h6_option_matrix.json",
    )
)
H6_PYTHON_FILES = (
    "scripts/validate_h6_web_archive_news_event_policy_packs.py",
    "scripts/summarize_h6_web_archive_news_event_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {
    "inspect_fixture",
    "normalize_fixture_future",
    "record_source_policy",
    "record_source_metadata_preview",
    "record_web_capture_identity_policy",
    "record_archived_url_time_state_policy",
    "record_news_event_mention_policy",
    "record_dead_link_trace_policy",
    "record_public_document_trace_policy",
    "create_coverage_preview",
    "create_scorecard_preview",
}
FORBIDDEN_TRUE_KEYS = {
    "live_access_enabled",
    "source_sync_enabled",
    "connector_runtime_enabled",
    "approved_live_probe_enabled",
    "cdx_query_enabled",
    "memento_lookup_enabled",
    "warc_wacz_fetch_enabled",
    "archived_page_fetch_enabled",
    "media_download_enabled",
    "transcript_download_enabled",
    "newspaper_page_download_enabled",
    "public_document_fetch_enabled",
    "restricted_sensitive_source_enabled",
    "scraping_enabled",
    "crawling_enabled",
    "bypass_or_automation_enabled",
    "policy_pack_grants_live_access",
    "source_pack_is_truth",
    "source_pack_is_accepted_evidence",
    "source_pack_is_imported_state",
    "capability_grants_permission",
    "coverage_preview_is_exhaustive",
    "coverage_manifest_is_exhaustive_global_coverage",
    "scorecard_preview_is_production_ready",
    "scorecard_claims_production_readiness",
    "scorecard_auto_approves_future_connectors",
    "production_ready",
    "auto_approves_future_connectors",
    "web_capture_metadata_is_capture_truth",
    "web_capture_candidate_is_truth",
    "capture_record_is_complete",
    "archived_url_time_state_is_historical_truth",
    "time_state_candidate_is_historical_truth",
    "news_event_mention_is_event_truth",
    "news_event_mention_candidate_is_event_truth",
    "article_metadata_is_claim_truth",
    "public_document_trace_is_public_truth",
    "dead_link_trace_grants_acquisition_permission",
    "capture_digest_proves_authenticity",
    "archived_content_proves_rights_clearance",
    "source_authenticity_verified",
    "event_truth_accepted",
    "article_truth_accepted",
    "rights_clearance_claimed",
    "privacy_safety_claimed",
    "malware_safety_claimed",
    "verified_authenticity_claimed",
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_web_capture_truth",
    "accepted_time_state_truth",
    "accepted_event_truth",
    "accepted_article_truth",
    "accepted_public_document_truth",
    "accepted_public_record",
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
    "public_index_mutated",
    "master_index_mutated",
    "mutated_public_index",
    "mutated_master_index",
}
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_RE = re.compile(
    r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:',
    re.IGNORECASE,
)
PAYLOAD_RE = re.compile(
    r'"[^"]*(archived_page_payload|warc_payload|wacz_payload|media_payload|video_payload|audio_payload|transcript_payload|newspaper_page_payload|public_document_payload|sensitive_document|scraping_output|crawling_output|browser_automation_output)[^"]*"\s*:',
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
        print("H6 web archive/news/event policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    required_paths = list(INVENTORY_FILES + SOURCE_PACK_EXAMPLES + EXTRA_EXAMPLES + DOCS + AUDIT_FILES + H6_PYTHON_FILES)
    for source_paths in EXPECTED_SOURCES.values():
        required_paths.extend(source_paths.values())
    for rel in required_paths:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required path: {rel}")
            continue
        if path.suffix == ".json":
            try:
                payload = _load_json(path)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(f"{rel}: invalid JSON: {exc}")
                continue
            payloads[rel] = payload
            _scan_json_payload(rel, payload, errors)
    known = _load_known_values(root, errors)
    inventory = payloads.get("control/inventory/source_packs/h6_web_archive_news_event_sources.json", {})
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        errors.append("h6 source inventory must contain sources list")
        sources = []
    source_ids = [item.get("source_id") for item in sources if isinstance(item, Mapping)]
    if len(sources) != 13:
        errors.append(f"h6 source inventory expected 13 sources, got {len(sources)}")
    if sorted(source_ids) != sorted(EXPECTED_SOURCES):
        errors.append("h6 source inventory source IDs do not match expected set")
    if len(source_ids) != len(set(source_ids)):
        errors.append("h6 source inventory source IDs must be unique")
    for source_id, paths in EXPECTED_SOURCES.items():
        errors.extend(validate_source_record(source_id, payloads.get(paths["source_record"], {}), known))
        errors.extend(validate_policy_pack(source_id, payloads.get(paths["policy_pack"], {})))
        errors.extend(validate_coverage_preview(source_id, payloads.get(paths["coverage"], {})))
        errors.extend(validate_scorecard_preview(source_id, payloads.get(paths["scorecard"], {})))
    blocked_record = payloads.get("examples/sources/source_records/web_archive_news_event_policy_blocked_source_v2.json", {})
    if blocked_record:
        errors.extend(validate_source_record("web_archive_news_event_policy_blocked", blocked_record, known, allow_blocked=True))
    blocked_pack = payloads.get("examples/connectors/h6_web_archive_news_event/policies/web_archive_news_event_policy_blocked_pack_v0.json", {})
    if blocked_pack:
        errors.extend(validate_policy_pack("web_archive_news_event_policy_blocked", blocked_pack, allow_blocked=True))
    errors.extend(validate_policies(payloads))
    errors.extend(validate_registry_entries(root))
    errors.extend(scan_python_files(root))
    errors.extend(scan_for_private_roots(root))
    return {
        "schema_version": "h6_web_archive_news_event_policy_pack_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(EXPECTED_SOURCES),
        "errors": errors,
    }


def validate_source_record(source_id: str, record: Mapping[str, Any], known: Mapping[str, set[str]], allow_blocked: bool = False) -> list[str]:
    errors: list[str] = []
    prefix = f"source_record {source_id}"
    if record.get("schema_version") != "source_record.v2":
        errors.append(f"{prefix}: schema_version must be source_record.v2")
    if record.get("source_id") != source_id:
        errors.append(f"{prefix}: source_id mismatch")
    if record.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{prefix}: source_family must be {SOURCE_FAMILY}")
    if SOURCE_FAMILY not in known.get("source_families", set()):
        errors.append(f"{prefix}: source family {SOURCE_FAMILY} is not registered")
    if record.get("connector_family") not in known.get("connector_families", set()):
        errors.append(f"{prefix}: connector_family is not registered")
    if record.get("trust_lane") not in known.get("trust_lanes", set()):
        errors.append(f"{prefix}: unknown trust_lane {record.get('trust_lane')}")
    if record.get("current_access_mode") not in known.get("access_modes", set()):
        errors.append(f"{prefix}: unknown current_access_mode {record.get('current_access_mode')}")
    if record.get("current_index_depth") not in known.get("index_depths", set()):
        errors.append(f"{prefix}: unknown current_index_depth {record.get('current_index_depth')}")
    if record.get("target_index_depth_future") not in known.get("index_depths", set()):
        errors.append(f"{prefix}: unknown target_index_depth_future {record.get('target_index_depth_future')}")
    if record.get("current_status") not in {"policy_pack_only", "policy_blocked"}:
        errors.append(f"{prefix}: current_status must be policy_pack_only or policy_blocked")
    if allow_blocked and record.get("current_status") != "policy_blocked":
        errors.append(f"{prefix}: blocked record must be policy_blocked")
    for key in ("web_capture_identity_support", "archived_url_time_state_support", "news_event_mention_support", "dead_link_trace_support", "public_document_trace_support"):
        if not isinstance(record.get(key), Mapping):
            errors.append(f"{prefix}: missing {key}")
    for key in ("fixture_required", "live_probe_required_future", "scorecard_required", "coverage_required"):
        if record.get(key) is not True:
            errors.append(f"{prefix}: {key} must be true")
    errors.extend(_detect_forbidden_true_values(record, prefix))
    errors.extend(_detect_boundary_overclaim(record, prefix))
    return errors


def validate_policy_pack(source_id: str, pack: Mapping[str, Any], allow_blocked: bool = False) -> list[str]:
    errors: list[str] = []
    prefix = f"policy_pack {source_id}"
    if pack.get("schema_version") != "h6_web_archive_news_event_policy_pack.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if pack.get("source_id") != source_id:
        errors.append(f"{prefix}: source_id mismatch")
    if pack.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{prefix}: source_family must be {SOURCE_FAMILY}")
    if pack.get("current_status") not in {"policy_pack_only", "policy_blocked"}:
        errors.append(f"{prefix}: current_status must be policy_pack_only or policy_blocked")
    if allow_blocked and pack.get("current_status") != "policy_blocked":
        errors.append(f"{prefix}: blocked pack must be policy_blocked")
    allowed_ops = pack.get("allowed_current_operations")
    if not isinstance(allowed_ops, list):
        errors.append(f"{prefix}: allowed_current_operations must be a list")
    elif not set(allowed_ops).issubset(ALLOWED_CURRENT_OPERATIONS):
        errors.append(f"{prefix}: allowed_current_operations contains unapproved operation")
    for key in (
        "endpoint_or_metadata_classes_planned",
        "endpoint_or_metadata_classes_forbidden_current",
        "fixture_requirements",
        "live_probe_requirements_future",
        "web_capture_identity_mapping_future",
        "archived_url_time_state_mapping_future",
        "news_event_mention_mapping_future",
        "dead_link_trace_mapping_future",
        "public_document_trace_mapping_future",
        "source_cache_mapping_future",
        "evidence_mapping_future",
        "review_requirements",
        "scorecard_requirements",
        "coverage_requirements",
        "no_goals",
    ):
        if key not in pack:
            errors.append(f"{prefix}: missing {key}")
    errors.extend(_detect_forbidden_true_values(pack, prefix))
    errors.extend(_detect_boundary_overclaim(pack, prefix))
    return errors


def validate_coverage_preview(source_id: str, coverage: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = f"coverage {source_id}"
    if coverage.get("schema_version") != "source_coverage_ledger.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if coverage.get("source_id") != source_id:
        errors.append(f"{prefix}: source_id mismatch")
    if coverage.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{prefix}: source_family must be {SOURCE_FAMILY}")
    if coverage.get("coverage_basis") not in {"policy_pack_only", "example_only"}:
        errors.append(f"{prefix}: coverage_basis must be policy_pack_only or example_only")
    if coverage.get("coverage_depth_current") not in {"D0_source_known", "D1_catalog_indexed"}:
        errors.append(f"{prefix}: coverage_depth_current must be D0 or D1 preview")
    for key in ("records_seen", "cdx_queries_performed", "memento_lookups_performed", "warc_wacz_fetches_performed", "archived_page_fetches_performed", "media_downloads_performed", "crawls_performed"):
        if coverage.get(key) != 0:
            errors.append(f"{prefix}: {key} must be 0")
    errors.extend(_detect_forbidden_true_values(coverage, prefix))
    errors.extend(_detect_boundary_overclaim(coverage, prefix))
    return errors


def validate_scorecard_preview(source_id: str, scorecard: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = f"scorecard {source_id}"
    if scorecard.get("schema_version") != "connector_scorecard.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if scorecard.get("source_id") != source_id:
        errors.append(f"{prefix}: source_id mismatch")
    expected_statuses = {
        "fixture_replay_status": "not_started",
        "policy_evaluation_status": "planned",
        "live_probe_envelope_status": "not_approved",
        "source_cache_mapping_status": "planned",
        "evidence_mapping_status": "planned",
        "web_capture_identity_mapping_status": "planned",
        "archived_url_time_state_mapping_status": "planned",
        "news_event_mention_mapping_status": "planned",
        "dead_link_trace_mapping_status": "planned",
        "public_document_trace_mapping_status": "planned",
        "quality_delta_status": "not_started",
        "cdx_query_status": "forbidden_current",
        "memento_lookup_status": "forbidden_current",
        "warc_wacz_fetch_status": "forbidden_current",
        "archived_page_fetch_status": "forbidden_current",
        "media_download_status": "forbidden_current",
        "scraping_crawling_status": "forbidden_current",
    }
    for key, expected in expected_statuses.items():
        if scorecard.get(key) != expected:
            errors.append(f"{prefix}: {key} must be {expected}")
    errors.extend(_detect_forbidden_true_values(scorecard, prefix))
    errors.extend(_detect_boundary_overclaim(scorecard, prefix))
    return errors


def validate_policies(payloads: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    source_policy = payloads.get("control/inventory/source_packs/h6_web_archive_news_event_source_pack_policy.json", {})
    for key in (
        "live_access_enabled",
        "source_sync_enabled",
        "connector_runtime_enabled",
        "approved_live_probe_enabled",
        "cdx_query_enabled",
        "memento_lookup_enabled",
        "warc_wacz_fetch_enabled",
        "archived_page_fetch_enabled",
        "media_download_enabled",
        "transcript_download_enabled",
        "newspaper_page_download_enabled",
        "public_document_fetch_enabled",
        "restricted_sensitive_source_enabled",
        "scraping_enabled",
        "crawling_enabled",
        "bypass_or_automation_enabled",
        "source_pack_import_enabled",
    ):
        if source_policy.get(key) is not False:
            errors.append(f"source policy: {key} must be false")
    for key in ("source_pack_export_only", "review_required_before_live_access", "review_required_before_source_cache_write", "review_required_before_evidence_acceptance", "review_required_before_public_index_use", "review_required_before_master_index"):
        if source_policy.get(key) is not True:
            errors.append(f"source policy: {key} must be true")
    checks = [
        ("control/inventory/source_packs/h6_web_capture_identity_policy.json", "identity_boundary", (
            "web_capture_identity_candidate_is_not_accepted_object_truth",
            "capture_presence_does_not_prove_completeness",
            "capture_digest_does_not_prove_source_authenticity_without_review",
            "archived_page_existence_does_not_prove_rights_clearance",
            "archived_content_may_be_stale_partial_harmful_private_or_context_dependent",
            "url_normalization_can_collapse_distinct_resources_and_requires_review",
        )),
        ("control/inventory/source_packs/h6_archived_url_time_state_policy.json", "time_state_boundary", (
            "time_state_candidate_is_not_historical_truth",
            "nearest_capture_does_not_prove_page_state_at_exact_time",
            "missing_capture_does_not_prove_absence",
            "archived_download_page_candidate_does_not_grant_download_permission",
            "url_status_does_not_prove_source_availability_or_safety",
        )),
        ("control/inventory/source_packs/h6_news_event_mention_policy.json", "mention_boundary", (
            "news_event_mention_candidate_is_not_event_truth",
            "article_metadata_does_not_prove_claim_accuracy",
            "transcript_metadata_does_not_prove_full_context",
            "mentions_are_evidence_candidates_requiring_review",
            "news_coverage_can_be_biased_stale_incomplete_or_duplicated",
        )),
        ("control/inventory/source_packs/h6_dead_link_trace_policy.json", "dead_link_boundary", (
            "dead_link_trace_is_not_acquisition_permission",
            "mirror_candidate_is_not_authenticity_or_rights_proof",
            "checksum_candidate_is_not_malware_safety",
            "old_download_page_is_not_current_availability",
            "absence_capture_gaps_require_explicit_uncertainty",
        )),
        ("control/inventory/source_packs/h6_public_document_trace_policy.json", "public_document_boundary", (
            "restricted_sensitive_public_document_sources_are_policy_blocked_by_default",
            "manifest_only_references_do_not_approve_fetching",
            "sensitive_source_metadata_must_not_expose_private_data",
            "legal_privacy_safety_and_rights_review_required_before_connector_work",
            "do_not_bypass_access_controls_paywalls_captchas_or_authentication",
        )),
    ]
    for rel, section, keys in checks:
        errors.extend(_require_true(payloads.get(rel, {}).get(section, {}), keys, rel))
    approvals = payloads.get("control/inventory/source_packs/h6_web_archive_news_event_approval_gates.json", {})
    for item in approvals.get("source_gates", []):
        if isinstance(item, Mapping) and item.get("approval_state_current") != "not_approved_for_live_access":
            errors.append(f"approval gates {item.get('source_id')}: current approval must be not_approved_for_live_access")
    return errors


def validate_registry_entries(root: Path) -> list[str]:
    errors: list[str] = []
    source_registry = _load_json(root / "control/inventory/sources/source_family_registry.json")
    if SOURCE_FAMILY not in {item.get("family_id") for item in source_registry.get("families", []) if isinstance(item, Mapping)}:
        errors.append(f"source family registry missing {SOURCE_FAMILY}")
    connector_registry = _load_json(root / "control/inventory/connectors/connector_family_registry.json")
    registered = {item.get("family_id") for item in connector_registry.get("families", []) if isinstance(item, Mapping)}
    for family in ("warc_cdx", "warc_wacz_manifest", "api_json", "newspaper_archive_metadata", "media_archive_metadata", "html_catalog_policy_blocked", "html_catalog", "restricted_manifest_only"):
        if family not in registered:
            errors.append(f"connector family registry missing {family}")
    return errors


def scan_python_files(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in H6_PYTHON_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"{rel}: imports network/provider/browser library")
    return errors


def scan_for_private_roots(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "crawl_cache", "warc_wacz_cache", "media_downloads"):
        if (root / rel).exists():
            errors.append(f"forbidden private/fetch root exists: {rel}")
    return errors


def _load_known_values(root: Path, errors: list[str]) -> dict[str, set[str]]:
    try:
        source_families = _load_json(root / "control/inventory/sources/source_family_registry.json")
        connector_families = _load_json(root / "control/inventory/connectors/connector_family_registry.json")
        trust_lanes = _load_json(root / "control/inventory/sources/source_trust_lane_policy.json")
        index_depths = _load_json(root / "control/inventory/sources/source_index_depth_registry.json")
        access_modes = _load_json(root / "control/inventory/sources/source_access_mode_policy.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"unable to load registry values: {exc}")
        return {"source_families": set(), "connector_families": set(), "trust_lanes": set(), "index_depths": set(), "access_modes": set()}
    return {
        "source_families": {str(item.get("family_id")) for item in source_families.get("families", []) if isinstance(item, Mapping)},
        "connector_families": {str(item.get("family_id")) for item in connector_families.get("families", []) if isinstance(item, Mapping)},
        "trust_lanes": {str(item.get("trust_lane")) for item in trust_lanes.get("trust_lanes", []) if isinstance(item, Mapping)},
        "index_depths": {str(item.get("depth_id")) for item in index_depths.get("depths", []) if isinstance(item, Mapping)},
        "access_modes": set(str(item) for item in access_modes.get("access_modes", [])),
    }


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _require_true(section: Any, keys: Sequence[str], label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(section, Mapping):
        return [f"{label}: expected policy boundary object"]
    for key in keys:
        if section.get(key) is not True:
            errors.append(f"{label}: {key} must be true")
    return errors


def _detect_forbidden_true_values(value: Any, prefix: str, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            current = f"{path}.{key}" if path else str(key)
            if key in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{prefix}: forbidden true value {current}")
            errors.extend(_detect_forbidden_true_values(item, prefix, current))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_detect_forbidden_true_values(item, prefix, f"{path}[{index}]"))
    return errors


def _detect_boundary_overclaim(value: Any, prefix: str) -> list[str]:
    return _detect_forbidden_true_values(value, prefix)


def _scan_json_payload(rel: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    text = json.dumps(payload, sort_keys=True)
    if SECRET_KEY_RE.search(text):
        errors.append(f"{rel}: contains credential/cookie/token-like key")
    if PAYLOAD_RE.search(text):
        errors.append(f"{rel}: contains forbidden payload/scraping-output-like key")


if __name__ == "__main__":
    raise SystemExit(main())
