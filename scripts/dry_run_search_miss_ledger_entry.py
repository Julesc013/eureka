#!/usr/bin/env python3
"""Emit a non-persistent dry-run Search Miss Ledger Entry v0 record.

This helper prints one hypothetical miss ledger entry to stdout only. It
performs no network calls, telemetry, logging, persistence, ledger mutation,
search need creation, probe enqueueing, result cache mutation, candidate-index
mutation, or master-index mutation.
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

from scripts.validate_search_miss_ledger_entry import SENSITIVE_PATTERNS  # noqa: E402


TOKEN_RE = re.compile(r"[a-z0-9_.-]+", re.IGNORECASE)
INDEX_SNAPSHOT_REF = "eureka_public_search_index_v0"


def build_dry_run_miss_entry(query: str, miss_type: str) -> dict[str, Any]:
    raw_query = query or ""
    stripped = " ".join(raw_query.strip().split())
    normalized_text = stripped.casefold()
    findings = _privacy_findings(raw_query)
    unsafe = bool(findings)
    safe_terms = [] if unsafe else TOKEN_RE.findall(normalized_text)
    fingerprint_basis = "<redacted>" if unsafe else normalized_text
    query_hash = hashlib.sha256(fingerprint_basis.encode("utf-8")).hexdigest()
    miss_key = hashlib.sha256(f"{fingerprint_basis}|{miss_type}|{INDEX_SNAPSHOT_REF}".encode("utf-8")).hexdigest()
    normalized_miss_type = miss_type if miss_type in {"no_hits", "weak_hits", "near_miss_only", "blocked_by_policy"} else "unknown"
    if unsafe:
        normalized_miss_type = "blocked_by_policy"
    status = "rejected_by_privacy_filter" if unsafe else "dry_run_validated"

    return {
        "schema_version": "0.1.0",
        "miss_entry_id": f"dry_run.search_miss_ledger.{miss_key[:16]}.v0",
        "miss_entry_kind": "search_miss_ledger_entry",
        "status": status,
        "created_by_tool": "dry_run_search_miss_ledger_entry.py",
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
                "Dry-run helper retains no raw query text and writes no miss entry."
            ],
        },
        "cache_ref": {
            "cache_entry_id": "dry_run.search_result_cache.unwritten",
            "cache_hit_state": "no_cache_runtime",
            "limitations": [
                "P61 dry-run does not read or write a shared result cache."
            ],
        },
        "miss_classification": {
            "miss_type": normalized_miss_type,
            "severity": "medium" if normalized_miss_type == "no_hits" else "low",
            "confidence": "medium",
            "scoped_absence": normalized_miss_type in {"no_hits", "weak_hits", "near_miss_only"},
            "global_absence_claimed": False,
        },
        "miss_causes": _miss_causes(unsafe=unsafe, miss_type=normalized_miss_type),
        "checked_scope": {
            "checked_indexes": [] if unsafe else ["public_index", "local_index_only"],
            "checked_sources": [] if unsafe else ["data/public_index"],
            "checked_source_families": [] if unsafe else ["public_index_fixture_and_recorded_sources"],
            "checked_capabilities": [] if unsafe else ["lexical_public_index_search"],
            "checked_index_snapshot_refs": [] if unsafe else [INDEX_SNAPSHOT_REF],
            "live_probes_attempted": False,
            "external_calls_performed": False,
        },
        "not_checked_scope": {
            "sources_not_checked": ["future source cache", "private local stores", "approved live probes"],
            "source_families_not_checked": ["live_source_families_future"],
            "capabilities_not_checked": ["live_probe", "candidate_index", "search_need_runtime"],
            "reasons_not_checked": ["disabled_by_policy", "not_implemented"],
            "limitations": [
                "Dry-run miss is scoped and does not claim anything outside checked local_index_only behavior."
            ],
        },
        "near_misses": [] if normalized_miss_type != "near_miss_only" else [_near_miss()],
        "weak_hits": [] if normalized_miss_type != "weak_hits" else [_weak_hit()],
        "result_summary": _result_summary(normalized_miss_type),
        "absence_summary": _absence_summary(normalized_miss_type),
        "suggested_next_steps": [
            {
                "step_type": "create_search_need_future",
                "reason": "A future search need may be created after privacy and poisoning review.",
                "future_only": True,
                "approval_required": False,
                "human_required": False,
            }
        ],
        "privacy": _privacy(findings, unsafe),
        "retention_policy": {
            "raw_query_retention": "none",
            "miss_entry_retention": "example_only",
            "deletion_supported_future": True,
            "notes": [
                "P61 dry-run helper writes nothing and implements no retention runtime."
            ],
        },
        "aggregation_policy": {
            "aggregate_allowed": not unsafe,
            "aggregate_fields_allowed": ["miss_type", "cause_type", "source_family", "capability_gap"],
            "raw_query_aggregation_allowed": False,
            "private_identifier_aggregation_allowed": False,
            "notes": [
                "Aggregate policy is future-only and excludes raw queries and private identifiers."
            ],
        },
        "limitations": [
            "Dry-run stdout only; no miss ledger file is written.",
            "No telemetry, ledger mutation, search need creation, probe enqueue, result cache mutation, candidate index mutation, local index mutation, or master-index mutation."
        ],
        "no_mutation_guarantees": {
            "master_index_mutated": False,
            "local_index_mutated": False,
            "candidate_index_mutated": False,
            "search_need_created": False,
            "probe_enqueued": False,
            "result_cache_mutated": False,
            "query_observation_mutated": False,
            "telemetry_exported": False,
            "external_calls_performed": False,
        },
        "notes": [
            "Dry-run miss entries are examples for validation and future integration planning only."
        ],
    }


def _miss_causes(*, unsafe: bool, miss_type: str) -> list[dict[str, Any]]:
    if unsafe:
        return [
            {
                "cause_type": "query_blocked_by_policy",
                "explanation": "Unsafe query material was rejected before search or ledger consideration.",
                "limitations": ["No query execution or persistence occurred."],
            }
        ]
    if miss_type == "weak_hits":
        return [
            {
                "cause_type": "low_score_result",
                "explanation": "Dry-run weak hit indicates insufficient evidence for a verified result.",
                "limitations": ["No runtime search was executed by this helper."],
            }
        ]
    return [
        {
            "cause_type": "no_public_index_hit",
            "explanation": "Dry-run no-hit is scoped to the public index contract.",
            "limitations": ["No runtime search was executed by this helper."],
        }
    ]


def _near_miss() -> dict[str, Any]:
    return {
        "result_ref": "dry_run:near_miss",
        "title": "Dry-run near miss",
        "source_id": "synthetic-fixtures",
        "source_family": "synthetic",
        "reason": "weak_identity_match",
        "score": 0.35,
        "limitations": ["Dry-run summary only; no result payload is stored."],
    }


def _weak_hit() -> dict[str, Any]:
    return {
        "result_ref": "dry_run:weak_hit",
        "title": "Dry-run weak hit",
        "source_id": "synthetic-fixtures",
        "source_family": "synthetic",
        "score": 0.5,
        "weakness": "insufficient_evidence",
        "limitations": ["Dry-run summary only; no result payload is stored."],
    }


def _result_summary(miss_type: str) -> dict[str, Any]:
    if miss_type == "weak_hits":
        return {"result_count": 1, "returned_count": 1, "hit_state": "weak_hits", "top_score": 0.5, "gap_count": 1, "warning_count": 1, "limitation_count": 2}
    if miss_type == "near_miss_only":
        return {"result_count": 1, "returned_count": 1, "hit_state": "near_misses", "top_score": 0.35, "gap_count": 1, "warning_count": 1, "limitation_count": 2}
    if miss_type == "blocked_by_policy":
        return {"result_count": 0, "returned_count": 0, "hit_state": "blocked_by_policy", "gap_count": 1, "warning_count": 1, "limitation_count": 2}
    return {"result_count": 0, "returned_count": 0, "hit_state": "no_hits", "gap_count": 1, "warning_count": 1, "limitation_count": 2}


def _absence_summary(miss_type: str) -> dict[str, Any]:
    status = "blocked_by_policy" if miss_type == "blocked_by_policy" else ("no_verified_result" if miss_type == "weak_hits" else "scoped_absence")
    return {
        "absence_status": status,
        "scoped_to": ["data/public_index", INDEX_SNAPSHOT_REF],
        "checked": [] if miss_type == "blocked_by_policy" else ["public_index", "local_index_only"],
        "not_checked": ["future source cache", "private local stores", "approved live probes"],
        "global_absence_claimed": False,
        "limitations": ["Scoped to the checked public index snapshot; no global absence is claimed."],
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
    parser.add_argument("--miss-type", default="no_hits", help="Miss type to project in dry-run output.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only. Plain mode still prints JSON because this is a dry-run artifact.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    entry = build_dry_run_miss_entry(args.query, args.miss_type)
    output = stdout or sys.stdout
    output.write(json.dumps(entry, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
