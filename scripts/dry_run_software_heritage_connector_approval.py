#!/usr/bin/env python3
"""Emit a stdout-only hypothetical Software Heritage approval record."""
from __future__ import annotations

import argparse
import json
from typing import Any, Sequence


def build_record() -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "approval_record_id": "dry_run.connector.software_heritage.approval.v0",
        "approval_record_kind": "software_heritage_connector_approval",
        "status": "draft_example",
        "created_by_tool": "dry_run_software_heritage_connector_approval_v0",
        "connector_ref": {
            "connector_id": "software_heritage_connector",
            "connector_label": "Software Heritage connector",
            "source_family": "software_heritage",
            "connector_version": "dry-run",
            "source_inventory_ref": "control/inventory/sources/software-heritage-placeholder.source.json",
            "source_status": "approval_required",
            "limitations": ["Dry-run only; no live connector execution."],
        },
        "approval_checklist_status": "pending",
        "operator_checklist_status": "pending",
        "swhid_review_required": True,
        "origin_url_review_required": True,
        "repository_identity_review_required": True,
        "source_code_content_risk_policy_required": True,
        "source_policy_review_required": True,
        "token_policy_review_required": True,
        "user_agent_contact_required_future": True,
        "rate_limit_required_future": True,
        "timeout_required_future": True,
        "retry_backoff_required_future": True,
        "circuit_breaker_required_future": True,
        "cache_first_required": True,
        "connector_runtime_implemented": False,
        "connector_approved_now": False,
        "live_source_called": False,
        "external_calls_performed": False,
        "software_heritage_api_called": False,
        "swhid_resolved_live": False,
        "origin_lookup_performed": False,
        "visit_lookup_performed": False,
        "snapshot_lookup_performed": False,
        "release_lookup_performed": False,
        "revision_lookup_performed": False,
        "directory_lookup_performed": False,
        "content_blob_lookup_performed": False,
        "repository_cloned": False,
        "source_code_downloaded": False,
        "source_archive_downloaded": False,
        "source_file_retrieved": False,
        "public_search_live_fanout_enabled": False,
        "arbitrary_origin_fetch_allowed": False,
        "arbitrary_swhid_fetch_allowed": False,
        "source_cache_mutated": False,
        "evidence_ledger_mutated": False,
        "candidate_index_mutated": False,
        "public_index_mutated": False,
        "local_index_mutated": False,
        "master_index_mutated": False,
        "downloads_enabled": False,
        "file_retrieval_enabled": False,
        "mirroring_enabled": False,
        "installs_enabled": False,
        "execution_enabled": False,
        "credentials_used": False,
        "software_heritage_token_used": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "source_code_safety_claimed": False,
        "source_completeness_claimed": False,
        "telemetry_exported": False,
        "notes": ["Stdout-only dry run. No files are written, no network is used, and no connector/source/cache/ledger/index runtime is called."],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    record = build_record()
    if args.json:
        print(json.dumps(record, indent=2))
    else:
        print("status: draft_example")
        print("connector_runtime_implemented: false")
        print("connector_approved_now: false")
        print("live_source_called: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
