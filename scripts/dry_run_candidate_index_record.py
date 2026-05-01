#!/usr/bin/env python3
"""Emit a non-persistent dry-run Candidate Index Record v0.

This helper prints one hypothetical candidate record to stdout only. It
performs no network calls, telemetry, logging, persistence, candidate index
writes, source cache writes, evidence ledger writes, probe queue writes,
candidate promotion, public-search injection, local-index mutation, or
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

from scripts.validate_candidate_index_record import ALLOWED_CANDIDATE_TYPES, SENSITIVE_PATTERNS  # noqa: E402


TOKEN_RE = re.compile(r"[a-z0-9_.-]+", re.IGNORECASE)


def build_dry_run_candidate_record(label: str, candidate_type: str) -> dict[str, Any]:
    raw_label = label or ""
    stripped = " ".join(raw_label.strip().split())
    normalized_label = stripped.casefold()
    findings = _privacy_findings(raw_label)
    unsafe = bool(findings)
    normalized_type = candidate_type if candidate_type in ALLOWED_CANDIDATE_TYPES else "unknown"
    type_family = _type_family(normalized_type)
    subject_kind = "compatibility_evidence" if normalized_type == "compatibility_claim_candidate" else "software_version"
    safe_terms = [] if unsafe else TOKEN_RE.findall(normalized_label)
    basis = "<redacted>" if unsafe else f"{normalized_label}|{normalized_type}|candidate_index"
    candidate_hash = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    status = "rejected_future" if unsafe else "dry_run_validated"

    return {
        "schema_version": "0.1.0",
        "candidate_id": f"dry_run.candidate_index.{candidate_hash[:16]}.v0",
        "candidate_kind": "candidate_index_record",
        "status": status,
        "created_by_tool": "dry_run_candidate_index_record.py",
        "candidate_identity": {
            "candidate_fingerprint": {
                "algorithm": "sha256",
                "normalized_basis": "redacted_candidate_label" if unsafe else "canonical_candidate_label|candidate_type|candidate_index",
                "value": candidate_hash,
                "reversible": False,
                "salt_policy": "unsalted_public_aggregate",
            },
            "canonical_candidate_label": "<redacted>" if unsafe else stripped,
            "normalized_terms": safe_terms,
            "alias_terms": [],
        },
        "candidate_type": {
            "type": normalized_type,
            "type_family": type_family,
            "allowed_future_destinations": ["candidate_index_only", "master_index_review_queue_future"],
        },
        "candidate_subject": {
            "subject_kind": subject_kind,
            "product_name": "<redacted>" if unsafe else stripped,
            "artifact_type": "candidate summary",
            "limitations": ["Dry-run subject only; no accepted record is created."],
        },
        "candidate_claims": [
            {
                "claim_id": "claim.dry_run.describes",
                "claim_type": "describes",
                "claim_value": "<redacted>" if unsafe else "A provisional candidate may need review.",
                "claim_status": "rejected_future" if unsafe else "review_required",
                "confidence": "low",
                "limitations": ["Dry-run claim only; not accepted evidence."],
            }
        ],
        "provenance": {
            "provenance_kind": "fixture_example",
            "created_from": "dry_run_stdout_only",
            "source_refs": [],
            "pack_refs": [],
            "validator_refs": ["scripts/validate_candidate_index_record.py"],
            "tool_refs": ["dry_run_candidate_index_record.py"],
            "limitations": ["No runtime candidate index emitted this record."],
        },
        "input_refs": {
            "query_observation_refs": [],
            "search_result_cache_refs": [],
            "search_miss_ledger_refs": [],
            "search_need_refs": [
                {
                    "ref_id": "dry_run.search_need.unwritten",
                    "ref_kind": "search_need",
                    "status": "dry_run_validated" if not unsafe else "rejected_future",
                    "privacy_classification": "public_safe_aggregate" if not unsafe else "rejected_sensitive",
                    "limitations": ["Dry-run ref only; no search need store emitted this input."],
                }
            ],
            "probe_queue_refs": [],
        },
        "evidence_refs": [
            {
                "evidence_ref": "none.current",
                "evidence_kind": "dry_run_candidate_context",
                "evidence_status": "none",
                "limitations": ["Evidence is required before any review path."],
            }
        ],
        "source_policy": {
            "source_policy_kind": "no_source_call",
            "live_source_called": False,
            "live_probe_enabled": False,
            "source_terms_review_required": True,
            "rights_review_required": True,
            "allowed_source_ids": [],
            "allowed_source_families": [],
            "limitations": ["Dry-run helper performs no source call."],
        },
        "confidence": {
            "confidence_class": "low",
            "confidence_basis": ["fixture_example", "insufficient_evidence"],
            "confidence_notes": ["Dry-run confidence is not truth."],
            "confidence_not_truth": True,
        },
        "review": {
            "review_status": "evidence_required",
            "required_reviews": ["human_review", "evidence_review", "rights_review"],
            "promotion_allowed_now": False,
            "promotion_policy_required": True,
            "reviewer_notes": ["Candidate promotion policy is required before acceptance."],
        },
        "conflicts": {
            "conflict_status": "none_known",
            "conflicting_candidate_refs": [],
            "conflicting_source_refs": [],
            "conflict_summary": "No conflict is known in this dry-run record.",
            "preservation_policy": "not_applicable",
        },
        "visibility": {
            "visibility_class": "review_required",
            "public_result_visibility_allowed": False,
            "public_candidate_visibility_allowed_future": False,
            "public_label": "<redacted>" if unsafe else stripped,
            "redaction_required": unsafe,
            "limitations": ["Dry-run record is not current public search authority."],
        },
        "privacy": _privacy(findings, unsafe),
        "rights_and_risk": {
            "rights_classification": "review_required",
            "risk_classification": "metadata_only",
            "downloads_enabled": False,
            "installs_enabled": False,
            "execution_enabled": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "limitations": ["No payload action is represented."],
        },
        "retention_policy": {
            "raw_query_retention": "none",
            "candidate_record_retention": "example_only",
            "deletion_supported_future": True,
            "notes": ["Dry-run helper writes nothing and implements no retention runtime."],
        },
        "limitations": [
            "Dry-run stdout only; no candidate index file is written.",
            "No telemetry, source cache write, evidence ledger write, public search injection, local-index mutation, or master-index mutation.",
        ],
        "no_truth_guarantees": {
            "accepted_as_truth": False,
            "promoted_to_master_index": False,
        },
        "no_mutation_guarantees": {
            "master_index_mutated": False,
            "local_index_mutated": False,
            "public_index_mutated": False,
            "source_registry_mutated": False,
            "source_cache_mutated": False,
            "evidence_ledger_mutated": False,
            "result_cache_mutated": False,
            "miss_ledger_mutated": False,
            "search_need_mutated": False,
            "probe_queue_mutated": False,
            "telemetry_exported": False,
            "external_calls_performed": False,
            "live_source_called": False,
        },
        "notes": ["Dry-run candidate records are validation examples only."],
    }


def _privacy(findings: set[str], unsafe: bool) -> dict[str, Any]:
    return {
        "privacy_classification": "rejected_sensitive" if unsafe else "public_safe_aggregate",
        "raw_query_retained": False,
        "contains_raw_query": False,
        "contains_private_path": any(item in findings for item in {"windows_absolute_path", "posix_private_path"}),
        "contains_secret": "api_key_marker" in findings,
        "contains_private_url": "private_url" in findings,
        "contains_user_identifier": "account_identifier" in findings,
        "contains_ip_address": "ip_address" in findings,
        "contains_local_result": False,
        "publishable": False,
        "public_aggregate_allowed": not unsafe,
        "reasons": ["redacted_for_privacy"] if unsafe else ["raw query retention is disabled by default"],
    }


def _privacy_findings(text: str) -> set[str]:
    findings: set[str] = set()
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            findings.add(label)
    return findings


def _type_family(candidate_type: str) -> str:
    if candidate_type in {"compatibility_claim_candidate"}:
        return "compatibility"
    if candidate_type in {"evidence_record_candidate"}:
        return "evidence"
    if candidate_type in {"absence_candidate"}:
        return "absence"
    if candidate_type in {"identity_match_candidate", "alias_candidate", "object_identity_candidate"}:
        return "identity"
    if candidate_type in {"member_path_candidate"}:
        return "member"
    if candidate_type in {"query_interpretation_candidate"}:
        return "query"
    return "object" if candidate_type != "unknown" else "unknown"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="Public-safe candidate label to normalize.")
    parser.add_argument("--candidate-type", default="unknown", help="Candidate type.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only. Plain mode still prints JSON because this is a dry-run artifact.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    record = build_dry_run_candidate_record(args.label, args.candidate_type)
    output = stdout or sys.stdout
    output.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
