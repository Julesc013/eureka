#!/usr/bin/env python3
"""Emit a hypothetical Known Absence Page v0 to stdout only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from typing import Any, Sequence, TextIO


ALLOWED_ABSENCE_STATUSES = {
    "no_verified_result",
    "scoped_absence",
    "no_public_index_hit",
    "weak_hits_only",
    "near_misses_only",
    "blocked_by_policy",
    "source_coverage_gap",
    "capability_gap",
    "unknown",
}
SENSITIVE_PATTERNS = (
    re.compile(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE),
    re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE),
    re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key|secret|credential)\b", re.IGNORECASE),
    re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"),
    re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE),
    re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\b", re.IGNORECASE),
)


def build_page(query: str, absence_status: str) -> dict[str, Any]:
    unsafe = _looks_sensitive(query)
    normalized_query = "[redacted]" if unsafe else _normalize(query)
    if absence_status not in ALLOWED_ABSENCE_STATUSES:
        absence_status = "unknown"
    fingerprint = hashlib.sha256(f"known_absence_page:v0:{normalized_query}".encode("utf-8")).hexdigest()
    status = "rejected_by_privacy_filter" if unsafe else "dry_run_validated"
    privacy_classification = "rejected_sensitive" if unsafe else "public_safe_example"
    summary = (
        "Sensitive input was redacted; no runtime known absence page was created."
        if unsafe
        else "No verified result was found in the checked dry-run scope; this is scoped absence, not global absence."
    )
    return {
        "schema_version": "0.1.0",
        "absence_page_id": f"dry_run.known_absence.{fingerprint[:16]}",
        "absence_page_kind": "known_absence_page",
        "status": status,
        "created_by_tool": "dry_run_known_absence_page_v0",
        "query_context": {
            "query_observation_ref": None,
            "search_result_cache_ref": None,
            "search_miss_ledger_ref": None,
            "search_need_ref": None,
            "normalized_query": normalized_query,
            "query_fingerprint": fingerprint,
            "raw_query_retained": False,
            "query_intent": "dry-run unresolved search explanation",
            "target_object_summary": "Hypothetical public-safe target summary.",
            "privacy_classification": privacy_classification,
            "limitations": ["Dry-run output only; no query log, page store, cache, or ledger is written."],
        },
        "absence_summary": {
            "absence_status": absence_status,
            "scoped_to": ["public_index"],
            "confidence": "low",
            "global_absence_claimed": False,
            "exhaustive_search_claimed": False,
            "summary_text": summary,
            "limitations": ["Dry-run scope is synthetic and does not prove wider absence."],
        },
        "checked_scope": {
            "checked_indexes": ["public_index"],
            "checked_sources": ["dry_run_fixture"],
            "checked_source_families": ["fixture_metadata"],
            "checked_capabilities": ["text_metadata_search"],
            "checked_index_snapshot_refs": [],
            "checked_at_policy": "example_static",
            "live_probes_attempted": False,
            "external_calls_performed": False,
        },
        "not_checked_scope": {
            "sources_not_checked": ["live_external_sources", "private_local_collections"],
            "source_families_not_checked": ["live_external_sources"],
            "capabilities_not_checked": ["live_probe", "source_cache_runtime"],
            "reasons_not_checked": ["not_implemented", "disabled_by_policy"],
            "limitations": ["Dry-run helper never calls sources."],
        },
        "near_misses": [],
        "weak_hits": [],
        "gap_explanations": [
            {
                "gap_id": f"dry_run.gap.{fingerprint[:8]}",
                "gap_type": "policy_blocked" if unsafe else "source_coverage_gap",
                "explanation": "Dry-run scope is intentionally bounded and does not call live sources.",
                "evidence_refs": [],
                "related_source_families": ["live_external_sources"],
                "related_capabilities": ["live_probe"],
                "user_visible": True,
                "limitations": ["No external source call is performed."],
            }
        ],
        "source_status_summary": {
            "source_count_checked": 1,
            "source_count_not_checked": 2,
            "checked_source_families": ["fixture_metadata"],
            "not_checked_source_families": ["live_external_sources"],
            "live_sources_enabled": False,
            "live_sources_disabled": True,
            "placeholder_sources": [],
            "fixture_sources": ["dry_run_fixture"],
            "recorded_sources": [],
            "limitations": ["Counts are dry-run only."],
        },
        "evidence_context": {
            "evidence_refs": [],
            "evidence_status": "none",
            "limitations": ["No accepted evidence is created."],
        },
        "candidate_context": {
            "candidate_refs": [],
            "candidate_status": "none",
            "candidate_index_runtime_implemented": False,
            "candidate_promotion_runtime_implemented": False,
            "limitations": ["No candidate index or promotion runtime is used."],
        },
        "safe_next_actions": [
            _action("refine_query", "Refine query", enabled=True),
            _action("view_checked_sources", "View checked sources", enabled=True),
            _action("run_manual_observation_future", "Manual observation after review", human=True),
            _action("enqueue_probe_after_approval_future", "Queue probe after approval", approval=True, operator=True),
        ],
        "user_facing_sections": {
            "title": "No verified result in the checked scope",
            "summary": summary,
            "what_was_checked": ["Dry-run fixture scope."],
            "what_was_not_checked": ["Live sources and private collections."],
            "near_misses_section": [],
            "gaps_section": ["Dry-run source coverage gap."],
            "safe_next_actions_section": ["Informational actions only; future actions are disabled now."],
            "limitations_section": ["Dry-run output is not a hosted runtime page."],
            "evidence_section": ["No accepted evidence record is produced."],
            "privacy_notice": "Raw query data is not retained.",
            "no_global_absence_notice": "Scoped absence, not global absence: unchecked sources may still contain relevant material.",
        },
        "api_projection": {
            "response_kind": "known_absence_response",
            "compatible_with_search_response": True,
            "fields": ["absence_summary", "checked_scope", "not_checked_scope", "gap_explanations", "limitations"],
            "error_response": False,
            "ok": True,
            "result_count": 0,
            "gaps_included": True,
            "absence_summary_included": True,
            "near_misses_included": True,
            "limitations_included": True,
        },
        "static_projection": {
            "static_demo_available": False,
            "static_demo_path": None,
            "generated_static_artifact": False,
            "no_js_required": True,
            "base_path_safe": True,
            "old_client_safe": True,
            "limitations": ["No static demo artifact is emitted by the dry-run helper."],
        },
        "privacy": {
            "privacy_classification": privacy_classification,
            "contains_raw_query": False,
            "contains_private_path": unsafe,
            "contains_secret": unsafe,
            "contains_private_url": unsafe,
            "contains_user_identifier": unsafe,
            "contains_ip_address": unsafe,
            "publishable": not unsafe,
            "public_aggregate_allowed": not unsafe,
            "reasons": ["Input was redacted by the privacy filter."] if unsafe else ["No private data retained."],
        },
        "rights_and_risk": {
            "rights_classification": "public_metadata_only",
            "risk_classification": "metadata_only",
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "downloads_enabled": False,
            "installs_enabled": False,
            "execution_enabled": False,
            "limitations": ["No rights or malware safety decision is made."],
        },
        "limitations": ["Stdout-only dry-run; no files or runtime state are changed."],
        "no_global_absence_guarantees": {
            "global_absence_claimed": False,
            "exhaustive_search_claimed": False,
            "live_probes_performed": False,
            "external_calls_performed": False,
            "downloads_enabled": False,
            "uploads_enabled": False,
            "installs_enabled": False,
            "arbitrary_url_fetch_enabled": False,
        },
        "no_mutation_guarantees": {
            "master_index_mutated": False,
            "public_index_mutated": False,
            "local_index_mutated": False,
            "candidate_index_mutated": False,
            "source_cache_mutated": False,
            "evidence_ledger_mutated": False,
            "result_cache_mutated": False,
            "miss_ledger_mutated": False,
            "search_need_mutated": False,
            "probe_queue_mutated": False,
            "telemetry_exported": False,
        },
        "notes": ["Dry-run helper emits JSON to stdout only."],
    }


def _action(action_type: str, label: str, *, enabled: bool = False, human: bool = False, approval: bool = False, operator: bool = False) -> dict[str, Any]:
    future_only = action_type.endswith("_future")
    return {
        "action_type": action_type,
        "label": label,
        "future_only": future_only,
        "human_required": human,
        "approval_required": approval,
        "operator_required": operator,
        "enabled_now": enabled,
        "limitations": ["Informational action only." if enabled else "Future-only action; no action is performed."],
    }


def _normalize(value: str) -> str:
    return " ".join(value.strip().split())[:120] or "unknown query"


def _looks_sensitive(value: str) -> bool:
    return any(pattern.search(value) for pattern in SENSITIVE_PATTERNS)


def _format_plain(page: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Known Absence Page dry run",
            f"status: {page['status']}",
            f"absence_page_id: {page['absence_page_id']}",
            f"absence_status: {page['absence_summary']['absence_status']}",
            "files_written: false",
        ]
    ) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Public-safe query text for a hypothetical scoped absence page.")
    parser.add_argument("--absence-status", default="scoped_absence", help="Known absence status vocabulary value.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    page = build_page(args.query, args.absence_status)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(page, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(page))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
