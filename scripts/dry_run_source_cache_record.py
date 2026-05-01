#!/usr/bin/env python3
"""Emit a hypothetical Source Cache Record v0 to stdout only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from typing import Any, Sequence


SOURCE_FAMILIES = {"internet_archive", "wayback", "github_releases", "pypi", "npm", "software_heritage", "wikidata_open_library", "sourceforge", "manual_source_pack", "local_fixture", "recorded_fixture", "unknown"}
CACHE_KINDS = {"source_metadata", "source_availability", "source_identifier_metadata", "release_metadata", "package_metadata", "wayback_capture_metadata", "file_listing_metadata", "source_health_metadata", "fixture_metadata", "recorded_fixture_metadata", "unknown"}
LIVE_FAMILIES = {"internet_archive", "wayback", "github_releases", "pypi", "npm", "software_heritage", "wikidata_open_library", "sourceforge"}
PRIVATE_OR_SECRET = re.compile(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+|(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/|\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key)\b|\b(?:secret|credential)\s*[:=]", re.IGNORECASE)


def build_record(label: str, source_family: str, kind: str) -> dict[str, Any]:
    if source_family not in SOURCE_FAMILIES:
        source_family = "unknown"
    if kind not in CACHE_KINDS:
        kind = "unknown"
    unsafe = bool(PRIVATE_OR_SECRET.search(label))
    live_future = source_family in LIVE_FAMILIES
    safe_label = "<redacted-source-cache-label>" if unsafe else label
    basis = f"{source_family}:{kind}:{safe_label}:dry_run:v0"
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    return {
        "schema_version": "0.1.0",
        "source_cache_record_id": f"dry_run.source_cache.{digest[:16]}",
        "source_cache_record_kind": "source_cache_record",
        "status": "rejected_by_policy" if unsafe else "dry_run_validated",
        "created_by_tool": "dry_run_source_cache_record_v0",
        "source_ref": {
            "source_id": source_family,
            "source_family": source_family,
            "source_status": "approval_required" if live_future else "future",
            "source_locator": f"synthetic:{source_family}:dry-run",
            "source_identifier": "dry-run-synthetic-identifier",
            "source_terms_ref": "future_source_terms_review",
            "limitations": ["Stdout-only synthetic source reference; no arbitrary URL is included."],
        },
        "cache_identity": {
            "cache_fingerprint": {"algorithm": "sha256", "normalized_basis": basis, "value": digest, "reversible": False},
            "cache_key_basis": {"source_id": source_family, "source_identifier": "dry-run-synthetic-identifier", "bounded_query_future": None, "fixture_record_id": None, "recorded_fixture_id": None},
            "canonical_cache_label": safe_label,
            "duplicate_of": None,
            "supersedes": None,
        },
        "cache_kind": {"kind": kind, "payload_policy": "metadata_summary_only", "raw_payload_allowed": False, "public_safe_summary_allowed": True, "limitations": ["Dry-run metadata summary only."]},
        "source_policy": {
            "source_policy_kind": "live_metadata_sync_after_approval_future" if live_future else "manual_only",
            "live_source_enabled_now": False,
            "source_terms_review_required": live_future,
            "robots_or_source_policy_review_required": live_future,
            "user_agent_required_future": live_future,
            "rate_limit_required_future": True,
            "retry_backoff_required_future": True,
            "circuit_breaker_required_future": True,
            "cache_required_before_public_use": True,
            "evidence_attribution_required": True,
            "max_records_future": 100 if live_future else None,
            "max_runtime_ms_future": 30000 if live_future else None,
            "limitations": ["No live source is enabled now."],
        },
        "acquisition_context": {"acquisition_kind": "source_sync_worker_future" if live_future else "manual_observation", "acquisition_ref": "dry_run.acquisition", "source_sync_job_ref": "future.source_sync.job.synthetic" if live_future else None, "probe_queue_ref": None, "manual_observation_ref": None, "acquired_at_policy": "future_runtime", "live_network_used": False, "external_call_performed": False, "credentials_used": False, "limitations": ["No acquisition is performed."]},
        "cached_payload_summary": {"payload_summary_kind": "metadata_fields", "field_count": 1, "item_count": 1, "summary_text": "Synthetic stdout-only cache record.", "raw_payload_included": False, "raw_payload_ref": None, "public_safe": True, "limitations": ["No raw payload is included."]},
        "normalized_metadata": {"normalized_title": safe_label, "normalized_identifier": "dry-run-synthetic-identifier", "normalized_version": None, "normalized_platforms": [], "normalized_artifact_types": ["metadata_summary"], "normalized_dates": [], "normalized_source_terms": [], "normalized_access_status": "future_only", "normalized_member_count": 0, "normalized_checksum_refs": [], "limitations": []},
        "freshness": {"freshness_status": "example_static", "freshness_basis": "source_sync_time_future", "ttl_policy": "none_for_example", "stale_if_source_policy_changes": True, "stale_if_connector_contract_changes": True, "stale_if_rights_policy_changes": True, "limitations": ["No runtime freshness exists."]},
        "provenance": {"provenance_kind": "source_sync_worker_future" if live_future else "manual_observation", "provenance_refs": ["dry_run.provenance"], "source_sync_job_ref": "future.source_sync.job.synthetic" if live_future else None, "validator_refs": ["scripts/validate_source_cache_record.py"], "generated_by_tool": "dry_run_source_cache_record_v0", "limitations": []},
        "fixity": {"content_hash": digest, "hash_algorithm": "sha256", "checksum_status": "present", "checksum_scope": "metadata_summary", "limitations": ["Hash covers the dry-run basis only."]},
        "privacy": {"privacy_classification": "redacted" if unsafe else "public_safe_example", "contains_private_path": False, "contains_secret": False, "contains_private_url": False, "contains_user_identifier": False, "contains_ip_address": False, "contains_raw_private_query": False, "contains_local_result": False, "publishable": True, "public_aggregate_allowed": not unsafe, "reasons": ["Unsafe label was redacted."] if unsafe else ["Synthetic public-safe dry-run input."]},
        "rights_and_risk": {"rights_classification": "source_terms_apply" if live_future else "review_required", "risk_classification": "metadata_only", "rights_clearance_claimed": False, "malware_safety_claimed": False, "downloads_enabled": False, "installs_enabled": False, "execution_enabled": False, "limitations": ["No rights clearance or malware safety claim is made."]},
        "limitations": ["Dry-run helper emits JSON to stdout only and writes no files."],
        "no_runtime_guarantees": {"source_cache_runtime_implemented": False, "cache_write_performed": False, "live_source_called": False, "external_calls_performed": False, "arbitrary_url_fetched": False, "raw_payload_stored": False, "private_data_stored": False, "executable_payload_stored": False, "telemetry_exported": False, "credentials_used": False},
        "no_mutation_guarantees": {"evidence_ledger_mutated": False, "candidate_index_mutated": False, "public_index_mutated": False, "local_index_mutated": False, "master_index_mutated": False},
        "notes": ["No source cache record is persisted."],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--source-family", required=True)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = build_record(args.label, args.source_family, args.kind)
    print(json.dumps(payload, indent=2) if args.json else payload["source_cache_record_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
