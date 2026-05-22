#!/usr/bin/env python3
"""Emit a stdout-only hypothetical GitHub Releases approval record."""
from __future__ import annotations

import argparse
import json
from typing import Any, Sequence


def build_record() -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "approval_record_id": "dry_run.connector.github_releases.approval.v0",
        "approval_record_kind": "github_releases_connector_approval",
        "status": "draft_example",
        "created_by_tool": "dry_run_github_releases_connector_approval_v0",
        "connector_ref": {
            "connector_id": "github_releases_connector",
            "connector_label": "GitHub Releases metadata connector",
            "source_family": "github_releases",
            "connector_version": "dry-run",
            "source_inventory_ref": "control/inventory/sources/github-releases-recorded-fixtures.source.json",
            "source_status": "approval_required",
            "limitations": ["Dry-run only; no live connector execution."],
        },
        "approval_checklist_status": "pending",
        "operator_checklist_status": "pending",
        "repository_identity_review_required": True,
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
        "github_api_called": False,
        "repository_cloned": False,
        "releases_fetched": False,
        "release_assets_downloaded": False,
        "source_archive_downloaded": False,
        "public_search_live_fanout_enabled": False,
        "arbitrary_repository_fetch_allowed": False,
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
        "github_token_used": False,
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
