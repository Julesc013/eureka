#!/usr/bin/env python3
"""Emit a non-persistent dry-run Search Result Cache Entry v0 record.

This helper prints one hypothetical cache entry to stdout only. It performs no
network calls, telemetry, logging, persistence, cache mutation, miss-ledger
mutation, search-need mutation, probe enqueueing, candidate-index mutation, or
master-index mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_search_result_cache_entry import SENSITIVE_PATTERNS  # noqa: E402


TOKEN_RE = re.compile(r"[a-z0-9_.-]+", re.IGNORECASE)
INDEX_SNAPSHOT_REF = "eureka_public_search_index_v0"


def build_dry_run_cache_entry(query: str) -> dict[str, Any]:
    raw_query = query or ""
    stripped = " ".join(raw_query.strip().split())
    normalized_text = stripped.casefold()
    findings = _privacy_findings(raw_query)
    unsafe = bool(findings)
    safe_terms = [] if unsafe else TOKEN_RE.findall(normalized_text)
    fingerprint_basis = "<redacted>" if unsafe else normalized_text
    query_hash = hashlib.sha256(fingerprint_basis.encode("utf-8")).hexdigest()
    key_basis = f"{fingerprint_basis}|api_client|local_index_only|{INDEX_SNAPSHOT_REF}"
    cache_key = hashlib.sha256(key_basis.encode("utf-8")).hexdigest()
    no_hit = not unsafe and normalized_text == "no-such-local-index-hit"
    status = "rejected_by_privacy_filter" if unsafe else "dry_run_validated"

    return {
        "schema_version": "0.1.0",
        "cache_entry_id": f"dry_run.search_result_cache.{cache_key[:16]}.v0",
        "cache_entry_kind": "search_result_cache_entry",
        "status": status,
        "created_by_tool": "dry_run_search_result_cache_entry.py",
        "query_ref": {
            "query_fingerprint": {
                "algorithm": "sha256",
                "normalized_basis": "redacted_normalized_query.text" if unsafe else "normalized_query.text",
                "value": query_hash,
                "salt_policy": "unsalted_public_aggregate",
                "reversible": False,
            },
            "normalized_query": {
                "text": "<redacted>" if unsafe else normalized_text,
                "safe_public_terms": safe_terms,
                "redaction_applied": unsafe,
            },
            "raw_query_retained": False,
            "raw_query_redacted": True,
            "privacy_classification": "rejected_sensitive" if unsafe else "public_safe_aggregate",
            "limitations": [
                "Dry-run helper retains no raw query text and writes no cache entry."
            ],
        },
        "cache_key": {
            "key_algorithm": "sha256",
            "key_basis": "normalized_query_plus_profile_plus_index_snapshot",
            "normalized_query_hash": query_hash,
            "profile": "api_client",
            "mode": "local_index_only",
            "include_flags": ["evidence", "limitations"],
            "index_snapshot_ref": INDEX_SNAPSHOT_REF,
            "privacy_classification": "rejected_sensitive" if unsafe else "public_safe_aggregate",
            "reversible": False,
            "salt_policy": "unsalted_public_aggregate",
            "value": cache_key,
            "notes": [
                "Dry-run key is deterministic for validation only; no salt value is included."
            ],
        },
        "request_summary": {
            "mode": "local_index_only",
            "profile": "api_client",
            "limit": 10,
            "include": ["evidence", "limitations"],
            "filters": {},
            "forbidden_parameters_present": False,
            "rejected_by_policy": unsafe,
        },
        "response_summary": _response_summary(unsafe=unsafe, no_hit=no_hit),
        "result_summaries": [] if unsafe or no_hit else [_example_result_summary()],
        "absence_summary": _absence_summary(unsafe=unsafe, no_hit=no_hit),
        "checked_scope": {
            "checked_indexes": [] if unsafe else ["public_index"],
            "checked_sources": [] if unsafe else ["data/public_index"],
            "live_probes_attempted": False,
            "external_calls_performed": False,
        },
        "index_refs": {
            "public_index_build_id": INDEX_SNAPSHOT_REF,
            "public_index_manifest_ref": "data/public_index/build_manifest.json",
            "source_coverage_ref": "data/public_index/source_coverage.json",
            "index_snapshot_id": INDEX_SNAPSHOT_REF,
        },
        "source_status_summary": {
            "source_count": 0 if unsafe else 15,
            "source_families": [] if unsafe else ["public_index_fixture_and_recorded_sources"],
            "live_sources_used": False,
            "limitations": [
                "Dry-run helper does not execute search, refresh sources, or call live services."
            ],
        },
        "freshness": {
            "cache_scope": "local_public_index",
            "index_snapshot_ref": INDEX_SNAPSHOT_REF,
            "build_manifest_ref": "data/public_index/build_manifest.json",
            "ttl_policy": "none_for_example",
            "stale_if_index_changes": True,
            "stale_if_contract_changes": True,
            "stale_if_source_status_changes": True,
        },
        "invalidation": {
            "invalidation_required_on": [
                "public_index_rebuild",
                "source_cache_refresh",
                "contract_version_change",
                "candidate_promotion",
                "rights_policy_change",
                "safety_policy_change",
            ],
            "invalidated": False,
        },
        "privacy": _privacy(findings, unsafe),
        "retention_policy": {
            "raw_query_retention": "none",
            "cache_entry_retention": "example_only",
            "deletion_supported_future": True,
            "public_aggregate_allowed": not unsafe,
            "notes": [
                "P60 dry-run helper writes nothing and implements no retention runtime."
            ],
        },
        "limitations": [
            "Dry-run stdout only; no cache entry file is written.",
            "No telemetry, cache mutation, miss ledger mutation, search need mutation, probe enqueue, candidate index mutation, local index mutation, or master-index mutation."
        ],
        "no_mutation_guarantees": {
            "master_index_mutated": False,
            "local_index_mutated": False,
            "candidate_index_mutated": False,
            "query_observation_mutated": False,
            "miss_ledger_mutated": False,
            "search_need_mutated": False,
            "probe_enqueued": False,
            "telemetry_exported": False,
            "external_calls_performed": False,
        },
        "notes": [
            "Dry-run cache entries are examples for validation and future integration planning only."
        ],
    }


def _response_summary(*, unsafe: bool, no_hit: bool) -> dict[str, Any]:
    if unsafe:
        return {
            "ok": False,
            "result_count": 0,
            "returned_count": 0,
            "hit_state": "blocked_by_policy",
            "confidence": "none",
            "warning_count": 1,
            "gap_count": 1,
            "limitation_count": 2,
        }
    if no_hit:
        return {
            "ok": True,
            "result_count": 0,
            "returned_count": 0,
            "hit_state": "no_hits",
            "confidence": "none",
            "warning_count": 1,
            "gap_count": 1,
            "limitation_count": 2,
        }
    return {
        "ok": True,
        "result_count": 1,
        "returned_count": 1,
        "hit_state": "hits",
        "top_score": 1.0,
        "confidence": "low",
        "warning_count": 1,
        "gap_count": 0,
        "limitation_count": 2,
    }


def _example_result_summary() -> dict[str, Any]:
    return {
        "result_ref": "dry_run:public_index:example_result",
        "title": "Dry-run public index result summary",
        "source_id": "synthetic-fixtures",
        "source_family": "synthetic",
        "result_lane": "mentions_or_traces",
        "user_cost": "inspect_metadata_only",
        "evidence_count": 1,
        "compatibility_summary": "Dry-run summary only; no search was executed.",
        "action_summary": {
            "allowed_actions": ["inspect", "cite", "view_provenance"],
            "blocked_actions": ["download", "install_handoff", "execute", "upload", "live_probe"],
        },
        "warning_count": 1,
        "limitation_count": 2,
        "score": 1.0,
        "public_safe": True,
    }


def _absence_summary(*, unsafe: bool, no_hit: bool) -> dict[str, Any]:
    if unsafe:
        return {
            "absence_status": "blocked_by_policy",
            "gap_types": ["privacy_filter"],
            "checked": [],
            "not_checked": ["public_index"],
            "near_miss_count": 0,
            "next_actions": ["Redact or reject unsafe query material before future cache consideration."],
            "limitations": ["Blocked by privacy policy before search or cache lookup."],
        }
    if no_hit:
        return {
            "absence_status": "scoped_absence",
            "gap_types": ["no_verified_result"],
            "checked": ["data/public_index"],
            "not_checked": ["live sources", "private local stores", "future source cache"],
            "near_miss_count": 0,
            "next_actions": ["Future miss-ledger review may convert this into a search need after policy review."],
            "limitations": ["Scoped to the checked public index snapshot."],
        }
    return {
        "absence_status": "not_absent",
        "gap_types": [],
        "checked": ["data/public_index"],
        "not_checked": ["live sources", "private local stores", "future source cache"],
        "near_miss_count": 0,
        "next_actions": [],
        "limitations": ["Result summaries are scoped to the current public index snapshot."],
    }


def _privacy(findings: set[str], unsafe: bool) -> dict[str, Any]:
    return {
        "privacy_classification": "rejected_sensitive" if unsafe else "public_safe_aggregate",
        "contains_raw_query": False,
        "contains_private_path": any(item in findings for item in {"windows_absolute_path", "posix_private_path"}),
        "contains_secret": "api_key_marker" in findings,
        "contains_private_url": "private_url" in findings,
        "contains_user_identifier": "account_identifier" in findings,
        "contains_ip_address": "ip_address" in findings,
        "contains_local_result": False,
        "publishable": False,
        "public_aggregate_allowed": not unsafe,
        "reasons": sorted(findings) if unsafe else ["raw query retention is disabled by default"],
    }


def _privacy_findings(query: str) -> set[str]:
    findings: set[str] = set()
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(query):
            findings.add(label)
    return findings


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Query text to normalize and privacy-filter.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only. Plain mode still prints JSON because this is a dry-run artifact.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    entry = build_dry_run_cache_entry(args.query)
    output = stdout or sys.stdout
    output.write(json.dumps(entry, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
