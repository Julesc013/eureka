#!/usr/bin/env python3
"""Emit a hypothetical Evidence Ledger Record v0 to stdout only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from typing import Any, Sequence


EVIDENCE_KINDS = {"source_metadata_observation", "availability_observation", "release_metadata_observation", "package_metadata_observation", "compatibility_observation", "member_listing_observation", "checksum_observation", "absence_observation", "source_health_observation", "manual_observation", "fixture_observation", "unknown"}
PRIVATE_OR_SECRET = re.compile(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+|(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/|\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key)\b|\b(?:secret|credential)\s*[:=]", re.IGNORECASE)


def build_record(label: str, evidence_kind: str) -> dict[str, Any]:
    if evidence_kind not in EVIDENCE_KINDS:
        evidence_kind = "unknown"
    unsafe = bool(PRIVATE_OR_SECRET.search(label))
    safe_label = "<redacted-evidence-ledger-label>" if unsafe else label
    family = "compatibility" if evidence_kind == "compatibility_observation" else "absence" if evidence_kind == "absence_observation" else "source"
    claim_type = "supports_platform" if evidence_kind == "compatibility_observation" else "scoped_absence" if evidence_kind == "absence_observation" else "describes"
    subject_kind = "compatibility_evidence" if family == "compatibility" else "absence" if family == "absence" else "source_identity"
    basis = f"{evidence_kind}:{safe_label}:dry_run:v0"
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    return {
        "schema_version": "0.1.0",
        "evidence_ledger_record_id": f"dry_run.evidence_ledger.{digest[:16]}",
        "evidence_ledger_record_kind": "evidence_ledger_record",
        "status": "rejected_future" if unsafe else "dry_run_validated",
        "created_by_tool": "dry_run_evidence_ledger_record_v0",
        "evidence_identity": {"evidence_fingerprint": {"algorithm": "sha256", "normalized_basis": basis, "value": digest, "reversible": False}, "canonical_evidence_label": safe_label, "duplicate_of": None, "supersedes": None},
        "evidence_kind": {"kind": evidence_kind, "evidence_family": family, "accepted_evidence_now": False, "review_required": True, "limitations": ["Dry-run evidence observation only."]},
        "subject_ref": {"subject_kind": subject_kind, "subject_id": "dry_run.subject", "subject_label": safe_label, "source_id": "dry_run.source", "source_family": "recorded_fixture", "limitations": []},
        "claim": {"claim_type": claim_type, "claim_value": {"label": safe_label}, "claim_status": "review_required", "global_absence_claimed": False, "limitations": ["Observation only."]},
        "source_cache_refs": [{"source_cache_record_id": "dry_run.source_cache.ref", "ref_status": "synthetic_ref", "limitations": []}],
        "provenance": {"provenance_kind": "source_cache_record", "provenance_refs": ["dry_run.source_cache.ref"], "validator_refs": ["scripts/validate_evidence_ledger_record.py"], "generated_by_tool": "dry_run_evidence_ledger_record_v0", "limitations": []},
        "observation": {"observation_text": f"Synthetic observation for {safe_label}.", "observation_data": {"dry_run": True}, "locator": "synthetic:evidence:dry-run", "snippet": "Synthetic short metadata observation.", "snippet_public_safe": True, "observation_scope": "metadata_summary", "checked_scope": ["synthetic fixture"] if family == "absence" else [], "not_checked_scope": ["live external sources"] if family == "absence" else [], "limitations": ["No raw payload dump."]},
        "confidence": {"confidence_class": "low" if unsafe else "medium", "confidence_basis": "insufficient_evidence" if unsafe else "source_cache_record", "confidence_not_truth": True, "limitations": ["Confidence is not truth."]},
        "review": {"review_status": "human_review_required", "promotion_policy_required": True, "master_index_review_required": True, "limitations": ["Review required before authoritative use."]},
        "conflicts": {"conflict_status": "none_known", "conflicting_evidence_refs": [], "preservation_policy": "preserve_conflict", "destructive_merge_allowed": False, "limitations": []},
        "privacy": {"privacy_classification": "redacted" if unsafe else "public_safe_example", "contains_private_path": False, "contains_secret": False, "contains_private_url": False, "contains_user_identifier": False, "contains_ip_address": False, "contains_raw_private_query": False, "contains_local_result": False, "publishable": True, "public_aggregate_allowed": not unsafe, "reasons": ["Unsafe label was redacted."] if unsafe else ["Synthetic public-safe dry-run input."]},
        "rights_and_risk": {"rights_classification": "public_metadata_only", "risk_classification": "metadata_only", "rights_clearance_claimed": False, "malware_safety_claimed": False, "downloads_enabled": False, "installs_enabled": False, "execution_enabled": False, "limitations": ["No rights clearance or malware safety claim is made."]},
        "limitations": ["Dry-run helper emits JSON to stdout only and writes no files."],
        "no_truth_guarantees": {"accepted_as_truth": False},
        "no_runtime_guarantees": {"evidence_ledger_runtime_implemented": False, "ledger_write_performed": False, "live_source_called": False, "external_calls_performed": False, "telemetry_exported": False, "credentials_used": False},
        "no_mutation_guarantees": {"source_cache_mutated": False, "candidate_index_mutated": False, "public_index_mutated": False, "local_index_mutated": False, "master_index_mutated": False},
        "notes": ["No evidence ledger record is persisted."],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--evidence-kind", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = build_record(args.label, args.evidence_kind)
    print(json.dumps(payload, indent=2) if args.json else payload["evidence_ledger_record_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
