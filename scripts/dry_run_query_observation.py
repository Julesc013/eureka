#!/usr/bin/env python3
"""Emit a non-persistent dry-run Query Observation v0 record.

This helper prints one observation to stdout only. It performs no network
calls, no telemetry, no logging, no persistence, no cache writes, no miss-ledger
writes, no probe enqueueing, and no index mutation.
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

from scripts.validate_query_observation import SENSITIVE_PATTERNS  # noqa: E402


TOKEN_RE = re.compile(r"[a-z0-9_.-]+", re.IGNORECASE)


def build_dry_run_observation(query: str) -> dict[str, Any]:
    raw_query = query or ""
    stripped = " ".join(raw_query.strip().split())
    normalized_text = stripped.casefold()
    findings = _privacy_findings(raw_query)
    unsafe = bool(findings)
    safe_terms = [] if unsafe else TOKEN_RE.findall(normalized_text)
    fingerprint_basis = "<redacted>" if unsafe else normalized_text
    fingerprint = hashlib.sha256(fingerprint_basis.encode("utf-8")).hexdigest()
    status = "rejected_by_privacy_filter" if unsafe else "dry_run_validated"
    privacy_classification = "rejected_sensitive" if unsafe else "public_safe_aggregate"
    redaction_reasons = sorted(findings) if unsafe else ["raw query retention is disabled by default"]

    return {
        "schema_version": "0.1.0",
        "observation_id": f"dry_run.query_observation.{fingerprint[:16]}.v0",
        "observation_kind": "query_observation",
        "status": status,
        "created_by_tool": "dry_run_query_observation.py",
        "raw_query_policy": {
            "raw_query_retained": False,
            "raw_query_retention_class": "not_retained",
            "raw_query_redacted": True,
            "raw_query_length": len(raw_query),
            "redaction_reasons": redaction_reasons,
            "safe_to_publish_raw_query": False,
        },
        "normalized_query": {
            "text": "<redacted>" if unsafe else normalized_text,
            "language": "unknown",
            "tokens": safe_terms,
            "normalized_terms": safe_terms,
            "redaction_applied": unsafe,
            "redaction_notes": sorted(findings),
            "safe_public_terms": safe_terms,
        },
        "query_fingerprint": {
            "algorithm": "sha256",
            "normalized_basis": "redacted_normalized_query.text" if unsafe else "normalized_query.text",
            "value": fingerprint,
            "salt_policy": "unsalted_public_aggregate",
            "reversible": False,
            "notes": [
                "Dry-run hash is deterministic for validation only; no salt value is included."
            ],
        },
        "query_intent": {
            "primary_intent": _infer_intent(safe_terms) if not unsafe else "unknown",
            "confidence": "low" if safe_terms else "none",
            "secondary_intents": [],
        },
        "destination": {
            "primary_destination": _infer_destination(safe_terms) if not unsafe else "unknown",
            "disabled_destination_intent_detected": any(term in {"download", "install", "installer", "emulator"} for term in safe_terms),
        },
        "detected_entities": _detect_entities(safe_terms),
        "filters": {
            "mode": "local_index_only",
            "source": "dry_run_no_query_executed",
        },
        "result_summary": {
            "result_count": 0,
            "returned_count": 0,
            "confidence": "none",
            "hit_state": "blocked_by_policy" if unsafe else "no_query_executed",
            "near_miss_count": 0,
            "gap_types": ["privacy_filter"] if unsafe else ["dry_run_no_search_executed"],
            "warnings": [
                "Dry run does not execute search or store observations."
            ],
            "limitations": [
                "Summary only; not a result cache.",
                "No runtime persistence or telemetry is implemented."
            ],
        },
        "checked_scope": {
            "checked_indexes": [],
            "checked_sources": [],
            "live_probes_attempted": False,
            "external_calls_performed": False,
        },
        "index_refs": {},
        "privacy": {
            "privacy_classification": privacy_classification,
            "pii_detected": any(item in findings for item in {"email_address", "phone_number"}),
            "secret_detected": "api_key_marker" in findings,
            "private_path_detected": any(item in findings for item in {"windows_absolute_path", "posix_private_path"}),
            "private_url_detected": "private_url" in findings,
            "credential_detected": "api_key_marker" in findings,
            "local_identifier_detected": any(item in findings for item in {"windows_absolute_path", "posix_private_path", "private_url"}),
            "publishable": False,
            "public_aggregate_allowed": not unsafe,
            "reasons": redaction_reasons,
        },
        "retention_policy": {
            "raw_query_retention": "none",
            "aggregate_retention": "disabled" if unsafe else "allowed",
            "deletion_supported_future": True,
            "notes": [
                "P59 dry-run helper writes nothing and implements no retention runtime."
            ],
        },
        "probe_policy": {
            "probe_enqueue_allowed": False,
            "suggested_probe_kinds": [],
            "reason": "P59 dry-run helper cannot enqueue probes.",
            "future_only": True,
        },
        "limitations": [
            "Dry-run stdout only; no observation file is written.",
            "No telemetry, cache mutation, miss ledger mutation, probe enqueue, candidate index mutation, local index mutation, or master-index mutation."
        ],
        "no_mutation_guarantees": {
            "master_index_mutated": False,
            "local_index_mutated": False,
            "candidate_index_mutated": False,
            "probe_enqueued": False,
            "result_cache_mutated": False,
            "miss_ledger_mutated": False,
            "telemetry_exported": False,
            "external_calls_performed": False,
        },
        "notes": [
            "Dry-run observations are examples for validation and future integration planning only."
        ],
    }


def _privacy_findings(query: str) -> set[str]:
    findings: set[str] = set()
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(query):
            findings.add(label)
    return findings


def _infer_intent(terms: list[str]) -> str:
    term_set = set(terms)
    if "driver" in term_set or ".inf" in term_set:
        return "find_driver"
    if "manual" in term_set or "documentation" in term_set:
        return "find_manual_or_documentation"
    if "source" in term_set or "code" in term_set:
        return "find_source_code"
    if "inside" in term_set or "iso" in term_set or "zip" in term_set:
        return "find_inside_container_member"
    if "compatibility" in term_set:
        return "check_compatibility"
    if terms:
        return "find_software_version"
    return "unknown"


def _infer_destination(terms: list[str]) -> str:
    term_set = set(terms)
    if {"download", "install", "installer"} & term_set:
        return "download_or_install_intent_detected_but_actions_disabled"
    if {"emulate", "emulator", "reconstruct"} & term_set:
        return "emulate_or_reconstruct_intent_detected_but_actions_disabled"
    if "cite" in term_set:
        return "cite"
    if "compare" in term_set:
        return "compare"
    if terms:
        return "inspect"
    return "unknown"


def _detect_entities(terms: list[str]) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    for term in terms:
        if term in {"windows", "xp", "vista", "linux", "mac", "dos"}:
            entities.append(_entity("platform", term))
        elif term.isdigit():
            entities.append(_entity("version", term))
        elif "." in term:
            entities.append(_entity("file_name" if not term.startswith(".") else "extension", term))
    return entities[:8]


def _entity(kind: str, value: str) -> dict[str, Any]:
    return {
        "entity_kind": kind,
        "value": value,
        "normalized_value": value,
        "confidence": "low",
        "privacy_classification": "public_safe",
    }


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Query text to normalize and privacy-filter.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only. Plain mode still prints JSON because this is a dry-run artifact.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    observation = build_dry_run_observation(args.query)
    output = stdout or sys.stdout
    output.write(json.dumps(observation, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
