#!/usr/bin/env python3
"""Emit a hypothetical Candidate Promotion Assessment v0 to stdout only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from typing import Any, Sequence, TextIO


ALLOWED_CANDIDATE_TYPES = {
    "object_identity_candidate",
    "software_version_candidate",
    "source_record_candidate",
    "evidence_record_candidate",
    "representation_candidate",
    "member_path_candidate",
    "compatibility_claim_candidate",
    "checksum_candidate",
    "release_metadata_candidate",
    "package_metadata_candidate",
    "source_match_candidate",
    "identity_match_candidate",
    "alias_candidate",
    "absence_candidate",
    "extraction_candidate",
    "OCR_text_candidate",
    "query_interpretation_candidate",
    "actionability_candidate",
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


def build_assessment(candidate_label: str, candidate_type: str) -> dict[str, Any]:
    unsafe = _looks_sensitive(candidate_label)
    safe_label = "[redacted candidate label]" if unsafe else _normalize_label(candidate_label)
    if candidate_type not in ALLOWED_CANDIDATE_TYPES:
        candidate_type = "unknown"
    fingerprint_basis = f"candidate_promotion_assessment:v0:{safe_label.casefold()}:{candidate_type}"
    fingerprint = hashlib.sha256(fingerprint_basis.encode("utf-8")).hexdigest()
    status = "promotion_blocked" if unsafe else "dry_run_validated"
    decision = "not_eligible" if unsafe else "request_more_evidence"
    decision_status = "blocked" if unsafe else "recommendation_only"
    privacy_status = "rejected_sensitive" if unsafe else "public_safe"

    return {
        "schema_version": "0.1.0",
        "assessment_id": f"dry_run.candidate_promotion.{fingerprint[:16]}",
        "assessment_kind": "candidate_promotion_assessment",
        "status": status,
        "created_by_tool": "dry_run_candidate_promotion_assessment_v0",
        "candidate_ref": {
            "candidate_id": f"dry_run.candidate_index.{fingerprint[:16]}",
            "candidate_type": candidate_type,
            "candidate_status": "review_required",
            "candidate_fingerprint": fingerprint,
            "candidate_source": "fixture_example",
            "candidate_ref_status": "unavailable_example",
        },
        "candidate_summary": {
            "label": safe_label,
            "subject_kind": "unknown",
            "source_family": "dry_run_fixture",
            "platform": None,
            "version": None,
            "artifact_type": "metadata candidate",
            "claim_types": ["unknown"],
            "current_confidence": "low",
            "review_status": "evidence_required",
            "limitations": ["Dry-run summary only; no candidate record is read or changed."],
        },
        "assessment_scope": {
            "assessment_mode": "dry_run",
            "assessed_for": ["promote_to_review_queue_future"],
            "promotion_destination": "none_v0",
            "destination_runtime_implemented": False,
        },
        "eligibility_gates": _default_gates(unsafe),
        "evidence_sufficiency": {
            "evidence_status": "insufficient",
            "evidence_refs": [],
            "required_evidence_kinds": ["source-backed metadata", "reviewed evidence"],
            "missing_evidence_kinds": ["source-backed metadata", "reviewed evidence"],
            "source_backed_required": True,
            "snippets_public_safe": not unsafe,
            "limitations": ["Dry-run evidence is insufficient for promotion."],
        },
        "provenance_sufficiency": {
            "provenance_status": "partial",
            "provenance_refs": [],
            "validator_refs": ["scripts/validate_candidate_promotion_assessment.py"],
            "pack_refs": [],
            "source_refs": [],
            "limitations": ["Dry-run provenance is synthetic and not sufficient for promotion."],
        },
        "source_policy_assessment": {
            "source_policy_status": "allowed_fixture",
            "source_ids": [],
            "source_families": ["dry_run_fixture"],
            "live_source_called": False,
            "live_probe_enabled": False,
            "source_terms_review_required": True,
            "limitations": ["No source is called by the dry-run helper."],
        },
        "privacy_assessment": {
            "privacy_status": privacy_status,
            "raw_query_retained": False,
            "contains_raw_query": False,
            "contains_private_path": unsafe,
            "contains_secret": unsafe,
            "contains_private_url": unsafe,
            "contains_user_identifier": unsafe,
            "contains_ip_address": unsafe,
            "publishable": False,
            "public_aggregate_allowed": not unsafe,
            "required_redactions": ["candidate_label"] if unsafe else [],
            "limitations": ["Sensitive input is redacted and blocked from public aggregation."] if unsafe else ["No private data retained."],
        },
        "rights_and_risk_assessment": {
            "rights_status": "review_required",
            "risk_status": "metadata_only",
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "downloads_enabled": False,
            "installs_enabled": False,
            "execution_enabled": False,
            "limitations": ["Rights and risk review are not completed by dry-run output."],
        },
        "conflict_assessment": {
            "conflict_status": "unknown",
            "conflict_refs": [],
            "duplicate_candidate_refs": [],
            "required_resolution": "human_review_required",
            "destructive_merge_allowed": False,
            "limitations": ["Dry-run output does not resolve conflicts."],
        },
        "confidence_assessment": {
            "confidence_class": "low",
            "confidence_basis": ["dry-run candidate label only"],
            "confidence_not_truth": True,
            "confidence_sufficient_for_review": False,
            "confidence_sufficient_for_promotion": False,
            "limitations": ["Confidence is not truth and is insufficient for promotion."],
        },
        "review_requirements": {
            "required_review_kinds": [
                "human_review",
                "policy_review",
                "evidence_review",
                "provenance_review",
                "rights_review",
                "risk_review",
                "conflict_review",
            ],
            "reviews_completed": [],
            "reviews_missing": [
                "human_review",
                "policy_review",
                "evidence_review",
                "provenance_review",
                "rights_review",
                "risk_review",
                "conflict_review",
            ],
            "promotion_allowed_now": False,
            "promotion_policy_required": True,
            "master_index_review_queue_required": True,
            "limitations": ["No review queue runtime is used."],
        },
        "recommended_decision": {
            "decision": decision,
            "decision_status": decision_status,
            "automatic": False,
            "requires_human_or_policy_review": True,
            "reasons": ["Sensitive input was redacted and blocked."] if unsafe else ["More evidence and review are required before any future promotion path."],
        },
        "decision_rationale": ["Dry-run recommendation only; no promotion is performed."],
        "future_outputs": [
            {
                "output_kind": "candidate_status_update_future",
                "output_runtime_implemented": False,
                "requires_validation": True,
                "requires_review": True,
                "limitations": ["No future output is emitted by the dry-run helper."],
            }
        ],
        "limitations": ["Stdout-only dry-run; no files, queues, ledgers, candidates, sources, evidence, or indexes are changed."],
        "no_auto_promotion_guarantees": {
            "promotion_performed": False,
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
            "candidate_index_mutated": False,
            "result_cache_mutated": False,
            "miss_ledger_mutated": False,
            "search_need_mutated": False,
            "probe_queue_mutated": False,
            "telemetry_exported": False,
            "external_calls_performed": False,
            "live_source_called": False,
        },
        "notes": ["Dry-run helper emits JSON only and does not persist promotion assessments."],
    }


def _default_gates(unsafe: bool) -> list[dict[str, Any]]:
    gates = [
        ("structure_valid", "passed"),
        ("candidate_type_allowed", "passed"),
        ("source_policy_allowed", "passed"),
        ("provenance_present", "review_required"),
        ("evidence_sufficient", "review_required"),
        ("privacy_safe", "failed" if unsafe else "passed"),
        ("rights_review_complete", "review_required"),
        ("risk_review_complete", "review_required"),
        ("conflict_review_complete", "review_required"),
        ("human_review_complete", "future_only"),
        ("policy_review_complete", "future_only"),
    ]
    return [
        {
            "gate_id": f"dry_run.gate.{gate_type}",
            "gate_type": gate_type,
            "required": True,
            "status": status,
            "reason": "Dry-run gate result is recommendation-only.",
            "evidence_refs": [],
            "limitations": ["No gate completion is persisted."],
        }
        for gate_type, status in gates
    ]


def _normalize_label(value: str) -> str:
    return " ".join(value.strip().split())[:120] or "unknown candidate"


def _looks_sensitive(value: str) -> bool:
    return any(pattern.search(value) for pattern in SENSITIVE_PATTERNS)


def _format_plain(assessment: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Candidate Promotion Assessment dry run",
            f"status: {assessment['status']}",
            f"assessment_id: {assessment['assessment_id']}",
            f"decision: {assessment['recommended_decision']['decision']}",
            "files_written: false",
        ]
    ) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-label", required=True, help="Public-safe candidate label to assess hypothetically.")
    parser.add_argument("--candidate-type", default="unknown", help="Candidate type vocabulary value.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    assessment = build_assessment(args.candidate_label, args.candidate_type)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(assessment, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(assessment))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
