"""Local pack quarantine helpers.

Quarantine is a review boundary. It verifies structure, fixity posture,
signature-envelope posture, import-preview posture, and contribution-review
seeds without importing, submitting, publishing, uploading, accepting, or
trusting packs.
"""

from __future__ import annotations

from copy import deepcopy
import json
import re
from pathlib import Path
from typing import Any, Mapping

from runtime.extraction.guards import REPO_ROOT, stable_id
from runtime.local.foundry import pack_export
from runtime.local.foundry.contribution_review import (
    build_contribution_review_seed,
    build_pack_revocation_preview,
    build_pack_trust_preview,
    validate_contribution_review_seed,
    validate_pack_trust_preview,
)
from runtime.local.foundry.pack_fixity import (
    build_pack_fixity_report,
    pack_product_boundary,
    validate_pack_fixity_report,
)
from runtime.local.foundry.pack_import_preview import (
    build_pack_import_preview,
    import_preview_truth_boundary,
    validate_pack_import_preview,
)
from runtime.local.foundry.pack_signature import (
    build_signature_verification_report,
    parse_pack_signature_envelope,
    signature_truth_boundary,
    validate_signature_envelope,
    validate_signature_verification_report,
)


REQUEST_SCHEMA_VERSION = "pack_quarantine_request.v0"
RESULT_SCHEMA_VERSION = "pack_quarantine_result.v0"
QUARANTINE_STATUSES = {
    "example_only",
    "quarantined_local",
    "validate_only",
    "needs_review",
    "blocked_by_schema",
    "blocked_by_fixity",
    "blocked_by_signature_policy",
    "blocked_by_policy",
    "blocked_by_rights",
    "blocked_by_risk",
    "incomplete",
    "deferred",
    "not_evaluable",
}
ALLOWED_PACK_TYPES = {
    "exported_pack_draft",
    "source_pack_export",
    "evidence_pack_export",
    "contribution_pack_export",
    "review_pack_export",
    "index_pack_preview_export",
    "policy_blocked_pack_export",
}
FORBIDDEN_TRUE_FIELDS = {
    "import_allowed_current",
    "submission_allowed_current",
    "acceptance_allowed_current",
    "quarantined_pack_is_accepted",
    "quarantined_pack_is_imported",
    "quarantined_pack_is_submitted",
    "fixity_implies_authenticity",
    "signature_placeholder_implies_trust",
    "import_preview_imports_records",
    "review_seed_is_review_decision",
    "accepted_evidence",
    "accepted_candidate",
    "accepted_public_record",
    "public_index_mutated",
    "master_index_mutated",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "private_key_used",
    "real_signature_created",
}
PRIVATE_KEY_RE = re.compile(r"private[_ -]?key|-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE)


def load_quarantine_policy(root: Path = REPO_ROOT) -> dict[str, Any]:
    policy_root = root / "control" / "inventory" / "packs"
    names = [
        "pack_quarantine_policy",
        "pack_quarantine_input_policy",
        "pack_quarantine_output_policy",
        "pack_quarantine_path_policy",
        "pack_quarantine_truth_policy",
        "pack_fixity_verification_policy",
        "pack_signature_verification_policy",
        "pack_import_preview_policy",
        "contribution_review_seed_policy",
        "pack_trust_revocation_policy",
    ]
    bundle = {name: load_json(policy_root / f"{name}.json") for name in names}
    path_policy = bundle["pack_quarantine_path_policy"]
    return {
        "schema_version": "pack_quarantine_policy_bundle.v0",
        **bundle,
        "allowed_input_roots": path_policy.get("allowed_input_roots", []),
        "allowed_output_roots": path_policy.get("allowed_output_roots", []),
        "forbidden_output_roots": path_policy.get("forbidden_output_roots", []),
    }


def load_pack_for_quarantine(path: str | Path) -> dict[str, Any]:
    return load_json(Path(path))


def build_pack_quarantine_request(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    pack_ref = _pack_ref(pack)
    pack_type = _pack_type(pack)
    return {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "quarantine_request_id": stable_id("pack_quarantine_request", {"pack": pack_ref, "type": pack_type}),
        "request_status": "local_quarantine_only",
        "input_pack_ref": pack_ref,
        "input_pack_type": pack_type,
        "requested_checks": [
            "schema_validation",
            "sha256_fixity",
            "signature_envelope_validation",
            "import_preview",
            "contribution_review_seed",
            "trust_revocation_preview",
        ],
        "requested_output_paths": [],
        "expected_pack_status": "needs_review",
        "review_required": True,
        "import_allowed_current": False,
        "submission_allowed_current": False,
        "acceptance_allowed_current": False,
        "truth_boundary": quarantine_truth_boundary(),
        "product_boundary": pack_product_boundary(),
        "no_goals": [
            "no pack import",
            "no pack submission",
            "no pack publication",
            "no hosted upload",
            "no pack acceptance",
            "no evidence acceptance",
            "no candidate acceptance",
            "no public index mutation",
            "no master index mutation",
            "no private signing keys",
            "no real signing",
        ],
        "notes": ["Request is local quarantine-only over an explicit exported pack draft."],
    }


def build_pack_quarantine_result(
    pack: Mapping[str, Any],
    checks: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    schema_errors = _schema_errors(pack)
    fixity_report = checks.get("fixity_report", {})
    signature_report = checks.get("signature_verification_report", {})
    import_preview = checks.get("import_preview", {})
    review_seed = checks.get("contribution_review_seed", {})
    trust_preview = checks.get("trust_preview", {})
    revocation_preview = checks.get("revocation_preview", {})
    blockers = _blockers(pack, schema_errors, fixity_report, signature_report, import_preview)
    request = checks.get("request") if isinstance(checks.get("request"), Mapping) else build_pack_quarantine_request(pack, policy)
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "quarantine_result_id": stable_id("pack_quarantine_result", {"pack": _pack_ref(pack), "blockers": blockers}),
        "request_ref": request.get("quarantine_request_id", ""),
        "input_pack_ref": _pack_ref(pack),
        "input_pack_type": _pack_type(pack),
        "quarantine_status": _status_for(pack, blockers, schema_errors, signature_report),
        "schema_validation_summary": {
            "schema_version": pack.get("schema_version", ""),
            "validation_errors": schema_errors,
            "error_count": len(schema_errors),
        },
        "fixity_report_ref": fixity_report.get("fixity_report_id", ""),
        "signature_verification_report_ref": signature_report.get("signature_verification_report_id", ""),
        "import_preview_ref": import_preview.get("import_preview_id", ""),
        "contribution_review_seed_refs": [review_seed.get("contribution_review_seed_id", "")] if review_seed else [],
        "blocker_summary": {
            "blockers": blockers,
            "blocker_count": len(blockers),
            "requires_review": True,
        },
        "provenance_summary": _provenance_summary(pack),
        "trust_preview_ref": trust_preview.get("trust_preview_id", ""),
        "revocation_preview_ref": revocation_preview.get("trust_preview_id", ""),
        "allowed_next_actions": [
            "human_review",
            "request_more_evidence",
            "defer_import_policy_review",
            "discard_quarantined_preview",
        ],
        "forbidden_next_actions": [
            "import_pack",
            "submit_pack",
            "publish_pack",
            "hosted_upload",
            "accept_pack",
            "accept_evidence",
            "accept_candidate",
            "mutate_public_index",
            "mutate_master_index",
            "use_private_key",
            "real_signing",
        ],
        "limitations": [
            "Quarantine result is review-gated and does not imply import or acceptance.",
            "Fixity is local content identity only.",
            "Signature handling is envelope validation only.",
        ],
        "truth_boundary": quarantine_truth_boundary(),
        "product_boundary": pack_product_boundary(),
        "notes": ["No pack was imported, submitted, published, uploaded, accepted, trusted, or revoked."],
    }
    return result


def build_full_quarantine_bundle(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    request = build_pack_quarantine_request(pack, policy)
    fixity_report = build_pack_fixity_report(pack, policy)
    envelope = parse_pack_signature_envelope(pack, policy)
    signature_report = build_signature_verification_report(envelope, policy)
    partial_result = build_pack_quarantine_result(
        pack,
        {
            "request": request,
            "fixity_report": fixity_report,
            "signature_verification_report": signature_report,
        },
        policy,
    )
    import_preview = build_pack_import_preview(pack, partial_result, policy)
    review_seed = build_contribution_review_seed(pack, partial_result, policy)
    trust_preview = build_pack_trust_preview(pack, partial_result, policy)
    revocation_preview = build_pack_revocation_preview(pack, partial_result, policy)
    result = build_pack_quarantine_result(
        pack,
        {
            "request": request,
            "fixity_report": fixity_report,
            "signature_verification_report": signature_report,
            "import_preview": import_preview,
            "contribution_review_seed": review_seed,
            "trust_preview": trust_preview,
            "revocation_preview": revocation_preview,
        },
        policy,
    )
    return {
        "request": request,
        "fixity_report": fixity_report,
        "signature_envelope": envelope,
        "signature_verification_report": signature_report,
        "import_preview": import_preview,
        "contribution_review_seed": review_seed,
        "trust_preview": trust_preview,
        "revocation_preview": revocation_preview,
        "quarantine_result": result,
    }


def validate_pack_quarantine_result(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "quarantine_result_id",
        "request_ref",
        "input_pack_ref",
        "input_pack_type",
        "quarantine_status",
        "schema_validation_summary",
        "fixity_report_ref",
        "signature_verification_report_ref",
        "import_preview_ref",
        "contribution_review_seed_refs",
        "blocker_summary",
        "provenance_summary",
        "trust_preview_ref",
        "revocation_preview_ref",
        "allowed_next_actions",
        "forbidden_next_actions",
        "limitations",
        "truth_boundary",
        "product_boundary",
        "notes",
    }
    for field in sorted(required):
        if field not in result:
            errors.append(f"missing quarantine result field: {field}")
    if result.get("schema_version") != RESULT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {RESULT_SCHEMA_VERSION}")
    if result.get("quarantine_status") not in QUARANTINE_STATUSES:
        errors.append(f"quarantine_status is not allowed: {result.get('quarantine_status')}")
    if result.get("input_pack_type") not in ALLOWED_PACK_TYPES:
        errors.append(f"input_pack_type is not allowed: {result.get('input_pack_type')}")
    errors.extend(detect_pack_quarantine_truth_boundary_violations(result, policy))
    errors.extend(detect_pack_quarantine_product_boundary_violations(result, policy))
    return sorted(dict.fromkeys(errors))


def summarize_pack_quarantine_result(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    blockers = result.get("blocker_summary", {})
    return {
        "schema_version": "pack_quarantine_summary.v0",
        "quarantine_result_id": result.get("quarantine_result_id"),
        "input_pack_type": result.get("input_pack_type"),
        "quarantine_status": result.get("quarantine_status"),
        "blocker_count": blockers.get("blocker_count", 0),
        "requires_review": blockers.get("requires_review", True),
        "pack_imported": False,
        "pack_submitted": False,
        "pack_accepted": False,
        "real_signing": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def detect_pack_quarantine_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_forbidden_true(result)


def detect_pack_quarantine_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_forbidden_true(result)


def quarantine_truth_boundary() -> dict[str, bool]:
    truth = import_preview_truth_boundary()
    truth.update(signature_truth_boundary())
    truth.update(
        {
            "quarantined_pack_is_accepted": False,
            "quarantined_pack_is_imported": False,
            "quarantined_pack_is_submitted": False,
            "fixity_implies_authenticity": False,
            "signature_placeholder_implies_trust": False,
            "import_preview_imports_records": False,
            "review_seed_is_review_decision": False,
        }
    )
    return truth


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return payload


def _pack_ref(pack: Mapping[str, Any]) -> str:
    return str(pack.get("pack_export_id") or pack.get("pack_id") or pack.get("pack_draft_id") or stable_id("pack.local", pack))


def _pack_type(pack: Mapping[str, Any]) -> str:
    pack_type = str(pack.get("export_pack_type") or pack.get("input_pack_type") or pack.get("pack_type") or "exported_pack_draft")
    return pack_type if pack_type in ALLOWED_PACK_TYPES else "exported_pack_draft"


def _schema_errors(pack: Mapping[str, Any]) -> list[str]:
    if pack.get("schema_version") == pack_export.SCHEMA_VERSION:
        return pack_export.validate_pack_export(pack)
    errors: list[str] = []
    if "schema_version" not in pack:
        errors.append("missing schema_version")
    if _pack_type(pack) not in ALLOWED_PACK_TYPES:
        errors.append(f"unsupported pack type: {_pack_type(pack)}")
    errors.extend(_detect_private_key_material(pack))
    return sorted(dict.fromkeys(errors))


def _blockers(
    pack: Mapping[str, Any],
    schema_errors: list[str],
    fixity_report: Mapping[str, Any],
    signature_report: Mapping[str, Any],
    import_preview: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    blockers.extend(f"schema:{error}" for error in schema_errors)
    blockers.extend(f"fixity:{error}" for error in validate_pack_fixity_report(fixity_report) if fixity_report)
    blockers.extend(f"signature:{error}" for error in validate_signature_verification_report(signature_report) if signature_report)
    blockers.extend(f"import_preview:{error}" for error in validate_pack_import_preview(import_preview) if import_preview)
    if pack.get("export_status") == "policy_blocked" or pack.get("export_pack_type") == "policy_blocked_pack_export":
        blockers.append("policy_blocked_pack_export")
    if str(signature_report.get("verification_status", "")).startswith("malformed"):
        blockers.append("malformed_signature_envelope")
    blockers.extend(_detect_private_key_material(pack))
    return sorted(dict.fromkeys(blockers))


def _status_for(
    pack: Mapping[str, Any],
    blockers: list[str],
    schema_errors: list[str],
    signature_report: Mapping[str, Any],
) -> str:
    if any("policy_blocked" in blocker for blocker in blockers):
        return "blocked_by_policy"
    if schema_errors:
        return "blocked_by_schema"
    if str(signature_report.get("verification_status", "")).startswith("malformed"):
        return "blocked_by_signature_policy"
    if blockers:
        return "needs_review"
    if pack.get("export_status") == "validate_only":
        return "validate_only"
    return "quarantined_local"


def _provenance_summary(pack: Mapping[str, Any]) -> dict[str, Any]:
    exported = pack.get("exported_pack", {})
    draft = exported.get("source_pack_draft", {}) if isinstance(exported, Mapping) else {}
    records = draft.get("pack_contents", {}).get("records", []) if isinstance(draft, Mapping) else []
    proposed = []
    for record in records if isinstance(records, list) else []:
        if not isinstance(record, Mapping):
            continue
        input_type = str(record.get("input_type", "unknown"))
        proposed.append(
            {
                "record_ref": record.get("record_ref", ""),
                "candidate_record_type": _candidate_record_type(input_type),
                "record_label": record.get("record_label", ""),
                "proposal_only": True,
                "accepted": False,
                "imported": False,
            }
        )
    return {
        "pack_ref": _pack_ref(pack),
        "pack_type": _pack_type(pack),
        "generated_from_pack_draft_ref": pack.get("generated_from_pack_draft_ref", ""),
        "export_status": pack.get("export_status", ""),
        "proposed_record_summary": proposed,
        "proposed_record_count": len(proposed),
        "source_authenticity_claimed": False,
        "trust_created": False,
    }


def _candidate_record_type(input_type: str) -> str:
    if "source" in input_type:
        return "source_record"
    if "evidence" in input_type:
        return "evidence_record"
    if "candidate" in input_type:
        return "candidate_record"
    if "review" in input_type:
        return "review_record"
    return "proposal_record"


def _detect_forbidden_true(value: Any, prefix: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in FORBIDDEN_TRUE_FIELDS and child is True:
                errors.append(f"{path} must be false")
            errors.extend(_detect_forbidden_true(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_detect_forbidden_true(child, f"{prefix}[{index}]"))
    return errors


def _detect_private_key_material(value: Any, prefix: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).casefold()
            if ("private_key" in key_text or key_text == "privatekey") and child not in (False, "", None):
                errors.append(f"{prefix}.{key}: private key field is forbidden")
            errors.extend(_detect_private_key_material(child, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_detect_private_key_material(child, f"{prefix}[{index}]"))
    elif isinstance(value, str) and PRIVATE_KEY_RE.search(value):
        errors.append(f"{prefix}: private key material is forbidden")
    return errors
