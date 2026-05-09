"""Local pack export helpers.

Pack exports are explicit-input draft artifacts with local fixity metadata.
They are not pack import, pack submission, hosted upload, accepted packs,
accepted evidence, public truth, real signatures, public-index mutation, or
master-index mutation.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

from runtime.local_foundry import pack_builder


SCHEMA_VERSION = "local_pack_export.v0"
REQUEST_SCHEMA_VERSION = "pack_export_request.v0"
RESULT_SCHEMA_VERSION = "pack_export_result.v0"
MANIFEST_SCHEMA_VERSION = "exported_pack_manifest.v0"

REQUEST_STATUSES = {
    "example_only",
    "planned",
    "local_export_only",
    "fixture_only",
    "policy_blocked",
    "deferred",
    "not_evaluable",
}

ALLOWED_EXPORT_TYPES = {
    "source_pack_export",
    "evidence_pack_export",
    "contribution_pack_export",
    "review_pack_export",
    "index_pack_preview_export",
    "compatibility_pack_export_future",
    "alias_pack_export_future",
    "hash_pack_export_future",
    "extraction_pack_export_future",
    "query_need_pack_export_future",
    "snapshot_pack_export_future",
    "policy_blocked_pack_export",
}

CURRENT_EXPORT_TYPES = {
    "source_pack_export",
    "evidence_pack_export",
    "contribution_pack_export",
    "review_pack_export",
    "index_pack_preview_export",
    "policy_blocked_pack_export",
}

FUTURE_EXPORT_TYPES = ALLOWED_EXPORT_TYPES - CURRENT_EXPORT_TYPES

PACK_TYPE_TO_EXPORT_TYPE = {
    "source_pack_draft": "source_pack_export",
    "evidence_pack_draft": "evidence_pack_export",
    "contribution_pack_draft": "contribution_pack_export",
    "review_pack_draft": "review_pack_export",
    "index_pack_preview": "index_pack_preview_export",
    "policy_blocked_pack": "policy_blocked_pack_export",
}

ALLOWED_EXPORT_STATUSES = {
    "example_only",
    "exported_local",
    "validate_only",
    "needs_review",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "incomplete",
    "deferred",
    "not_evaluable",
    "submitted_future",
    "accepted_public_future",
    "rejected_future",
}

CURRENT_EXPORT_STATUSES = {
    "example_only",
    "exported_local",
    "validate_only",
    "needs_review",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "incomplete",
    "deferred",
    "not_evaluable",
}

ALLOWED_INPUT_TYPES = {
    "source_pack_draft",
    "evidence_pack_draft",
    "contribution_pack_draft",
    "review_pack_draft",
    "index_pack_preview",
    "policy_blocked_pack_draft",
}

FORBIDDEN_INPUT_TYPES = {
    "raw_unreviewed_live_source_result",
    "scraped_search_result",
    "private_user_file",
    "secret_or_credential",
    "executable_download",
    "installer_payload",
    "account_session_data",
    "telemetry_stream",
    "submitted_pack",
    "accepted_pack",
    "hosted_upload_result",
    "master_index_record_current",
    "public_index_mutation_current",
}

ALLOWED_OUTPUT_TYPES = {
    "exported_pack_draft",
    "exported_pack_manifest",
    "pack_export_result",
    "pack_export_summary",
    "pack_fixity_report",
    "pack_validation_report",
    "pack_blocker_report",
}

FORBIDDEN_OUTPUT_TYPES = {
    "pack_import",
    "pack_submission",
    "hosted_upload",
    "accepted_pack",
    "accepted_evidence_truth",
    "accepted_public_record",
    "public_index_mutation",
    "master_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "production_readiness_claim",
    "real_signature",
}

ALLOWED_FORMATS = {
    "json_pack_export",
    "json_pack_manifest",
    "json_pack_export_report",
    "markdown_pack_summary",
}

FUTURE_FORMATS = {
    "signed_json_pack_future",
    "zipped_pack_future",
    "tar_pack_future",
    "snapshot_pack_future",
    "hosted_submission_package_future",
}

TRUTH_BOUNDARY_FALSE_FIELDS = {
    "exported_pack_is_public_truth",
    "exported_pack_is_truth",
    "exported_pack_is_accepted_evidence",
    "exported_pack_is_accepted_pack",
    "exported_pack_is_public_record",
    "exported_pack_is_imported_state",
    "exported_pack_is_submitted",
    "exported_pack_can_mutate_public_index",
    "exported_pack_can_mutate_master_index",
    "exported_pack_can_claim_rights_clearance",
    "exported_pack_can_claim_malware_safety",
    "exported_pack_can_claim_verified_installability",
    "exported_pack_can_claim_exhaustive_global_search",
    "exported_pack_can_claim_production_readiness",
}

TRUTH_BOUNDARY_TRUE_FIELDS = {"human_review_required_before_import_or_submission"}

PRODUCT_BOUNDARY_FALSE_FIELDS = {
    "implemented_pack_import_runtime",
    "implemented_pack_submission_runtime",
    "implemented_hosted_upload_runtime",
    "created_local_private_state",
    "enabled_network_access",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_model_provider_calls",
    "mutated_public_index",
    "mutated_master_index",
    "implemented_evidence_acceptance",
    "implemented_candidate_acceptance",
    "changed_public_search_behavior",
    "enabled_real_signing",
    "used_private_keys",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}

PRODUCT_BOUNDARY_TRUE_FIELDS = {"implemented_pack_export_runtime"}

REVIEW_GATE_TRUE_FIELDS = {
    "review_required_before_pack_import",
    "review_required_before_pack_submission",
    "review_required_before_public_use",
    "review_required_before_evidence_acceptance",
    "review_required_before_public_index_use",
    "review_required_before_master_index",
}

FORBIDDEN_CLAIM_PHRASES = {
    "accepted pack",
    "accepted public truth",
    "accepted evidence truth",
    "accepted public record",
    "pack import completed",
    "pack submission completed",
    "pack published",
    "hosted upload completed",
    "uploaded to hosted",
    "real signature",
    "private key",
    "cryptographic signing complete",
    "public index mutation allowed",
    "master-index mutation allowed",
    "master index mutation allowed",
    "rights are cleared",
    "rights clearance confirmed",
    "malware safe",
    "malware safety established",
    "installability is verified",
    "verified installability",
    "exhaustive global search",
    "production readiness",
    "telemetry enabled",
    "hosted backend enabled",
    "source sync enabled",
    "live probe enabled",
    "download enabled",
    "upload enabled",
    "account enabled",
}

PRIVATE_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"/home/[^/\s]+", re.IGNORECASE),
    re.compile(r"/Users/[^/\s]+", re.IGNORECASE),
    re.compile(r"\.aide\.local/", re.IGNORECASE),
    re.compile(r"\.local/eureka/", re.IGNORECASE),
    re.compile(r"\.cache/eureka/", re.IGNORECASE),
)

CREDENTIAL_PATTERNS = (
    re.compile(r"\b(api[_-]?key|secret|token|password|cookie|session)\b\s*[:=]", re.IGNORECASE),
    re.compile(r"\bsk-[A-Za-z0-9]{12,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{12,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


def default_policy() -> dict[str, Any]:
    return {
        "allowed_export_types": sorted(ALLOWED_EXPORT_TYPES),
        "current_export_types": sorted(CURRENT_EXPORT_TYPES),
        "future_export_types": sorted(FUTURE_EXPORT_TYPES),
        "allowed_export_statuses": sorted(ALLOWED_EXPORT_STATUSES),
        "current_export_statuses": sorted(CURRENT_EXPORT_STATUSES),
        "allowed_request_statuses": sorted(REQUEST_STATUSES),
        "allowed_input_types": sorted(ALLOWED_INPUT_TYPES),
        "forbidden_input_types": sorted(FORBIDDEN_INPUT_TYPES),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "allowed_formats": sorted(ALLOWED_FORMATS),
        "future_formats": sorted(FUTURE_FORMATS),
        "allowed_hash_algorithms": ["sha256"],
        "fixity_required_for_export": True,
        "real_signing_enabled": False,
        "signature_placeholder_allowed": True,
        "no_private_keys_allowed": True,
    }


def build_pack_export(input_pack_draft: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a deterministic local export record from one pack draft."""

    active_policy = policy or default_policy()
    draft = deepcopy(dict(input_pack_draft))
    export_type = PACK_TYPE_TO_EXPORT_TYPE.get(str(draft.get("pack_type", "")), "policy_blocked_pack_export")
    export_status = _export_status(draft, export_type)
    export_record = {
        "schema_version": SCHEMA_VERSION,
        "pack_export_id": f"pack_export.{export_type}.{_digest({'draft_id': draft.get('pack_draft_id'), 'type': export_type})[:12]}.v0",
        "export_pack_type": export_type,
        "export_status": export_status,
        "export_label": export_type.replace("_", " ").title(),
        "export_format": "json_pack_export",
        "generated_from_pack_draft_ref": str(draft.get("pack_draft_id", "")),
        "input_pack_draft_summary": pack_builder.summarize_pack_draft(draft),
        "exported_pack": {
            "exported_pack_kind": "draft_export",
            "source_pack_draft": _public_draft_payload(draft),
            "export_metadata": {
                "exported_local": True,
                "submitted": False,
                "imported": False,
                "published": False,
                "accepted": False,
                "hosted_upload": False,
                "public_index_mutation": False,
                "master_index_mutation": False,
            },
            "review_required_marker": True,
            "no_claim_summary": [
                "not accepted truth",
                "not imported state",
                "not submitted",
                "not public index mutation",
                "not master index mutation",
                "not rights clearance",
                "not malware safety",
                "not verified installability",
                "not real signing",
            ],
        },
        "export_manifest": {},
        "fixity": {},
        "signature_policy": _signature_policy(),
        "review_gates": _review_gates(),
        "limitations": _limitations(export_type, export_status),
        "blocked_items": _blocked_items(draft, active_policy),
        "validation_summary": {
            "validation_errors": [],
            "pack_import_enabled": False,
            "pack_submission_enabled": False,
            "hosted_upload_enabled": False,
            "pack_acceptance_enabled": False,
            "real_signing_enabled": False,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "no_goals": [
            "no pack import",
            "no pack submission",
            "no hosted upload",
            "no accepted pack",
            "no real signing",
            "no public index mutation",
            "no master index mutation",
        ],
        "notes": [
            "Export is a local draft artifact only.",
            "SHA-256 fixity is local deterministic hashing, not a real signature.",
        ],
    }
    export_record["fixity"] = compute_pack_fixity(export_record, active_policy)
    export_record["export_manifest"] = build_export_manifest(export_record, active_policy)
    return export_record


def validate_pack_export_request(request: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    active_policy = policy or default_policy()
    errors: list[str] = []
    required = {
        "schema_version",
        "pack_export_request_id",
        "requested_pack_type",
        "request_status",
        "input_pack_draft_ref",
        "input_pack_draft_summary",
        "requested_output_path",
        "export_format",
        "fixity_policy",
        "signature_policy",
        "review_gates",
        "truth_boundary",
        "product_boundary",
        "no_goals",
        "notes",
    }
    for field in sorted(required):
        if field not in request:
            errors.append(f"missing required request field: {field}")
    if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
        errors.append(f"schema_version must be {REQUEST_SCHEMA_VERSION}")
    if request.get("request_status") not in active_policy.get("allowed_request_statuses", REQUEST_STATUSES):
        errors.append(f"request_status is not allowed: {request.get('request_status')}")
    requested_type = str(request.get("requested_pack_type", ""))
    if requested_type not in active_policy.get("allowed_export_types", ALLOWED_EXPORT_TYPES):
        errors.append(f"requested_pack_type is not allowed: {requested_type}")
    if requested_type not in active_policy.get("current_export_types", CURRENT_EXPORT_TYPES):
        errors.append(f"requested_pack_type is not current behavior: {requested_type}")
    if request.get("export_format") not in active_policy.get("allowed_formats", ALLOWED_FORMATS):
        errors.append(f"export_format is not allowed: {request.get('export_format')}")
    errors.extend(_detect_request_boundary_violations(request))
    errors.extend(_scan_forbidden_claims(request))
    return sorted(dict.fromkeys(errors))


def validate_pack_export(export_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    active_policy = policy or default_policy()
    errors: list[str] = []
    required = {
        "schema_version",
        "pack_export_id",
        "export_pack_type",
        "export_status",
        "export_label",
        "export_format",
        "generated_from_pack_draft_ref",
        "input_pack_draft_summary",
        "exported_pack",
        "export_manifest",
        "fixity",
        "signature_policy",
        "review_gates",
        "limitations",
        "blocked_items",
        "validation_summary",
        "truth_boundary",
        "product_boundary",
        "no_goals",
        "notes",
    }
    for field in sorted(required):
        if field not in export_record:
            errors.append(f"missing required export field: {field}")
    if export_record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if export_record.get("export_pack_type") not in active_policy.get("allowed_export_types", ALLOWED_EXPORT_TYPES):
        errors.append(f"export_pack_type is not allowed: {export_record.get('export_pack_type')}")
    if export_record.get("export_pack_type") not in active_policy.get("current_export_types", CURRENT_EXPORT_TYPES):
        errors.append(f"export_pack_type is not current behavior: {export_record.get('export_pack_type')}")
    if export_record.get("export_status") not in active_policy.get("allowed_export_statuses", ALLOWED_EXPORT_STATUSES):
        errors.append(f"export_status is not allowed: {export_record.get('export_status')}")
    if export_record.get("export_status") not in active_policy.get("current_export_statuses", CURRENT_EXPORT_STATUSES):
        errors.append(f"export_status is not allowed in current runtime: {export_record.get('export_status')}")
    if export_record.get("export_status") in {"submitted_future", "accepted_public_future"}:
        errors.append(f"export_status is future-only and not allowed currently: {export_record.get('export_status')}")
    if export_record.get("export_format") not in active_policy.get("allowed_formats", ALLOWED_FORMATS):
        errors.append(f"export_format is not allowed: {export_record.get('export_format')}")
    exported_pack = export_record.get("exported_pack", {})
    if isinstance(exported_pack, Mapping):
        metadata = exported_pack.get("export_metadata", {})
        if isinstance(metadata, Mapping):
            for field in ("submitted", "imported", "published", "accepted", "hosted_upload", "public_index_mutation", "master_index_mutation"):
                if metadata.get(field) is not False:
                    errors.append(f"exported_pack.export_metadata.{field} must be false")
        else:
            errors.append("exported_pack.export_metadata must be an object")
    else:
        errors.append("exported_pack must be an object")
    errors.extend(_validate_fixity(export_record, active_policy))
    errors.extend(_validate_signature_policy(export_record))
    errors.extend(detect_pack_export_truth_boundary_violations(export_record, active_policy))
    errors.extend(detect_pack_export_product_boundary_violations(export_record, active_policy))
    errors.extend(_detect_review_gate_violations(export_record))
    errors.extend(_scan_forbidden_claims(export_record))
    return sorted(dict.fromkeys(errors))


def summarize_pack_export(export_record: Mapping[str, Any]) -> dict[str, Any]:
    fixity = export_record.get("fixity", {})
    truth = export_record.get("truth_boundary", {})
    metadata = export_record.get("exported_pack", {}).get("export_metadata", {})
    return {
        "pack_export_id": export_record.get("pack_export_id", ""),
        "export_pack_type": export_record.get("export_pack_type", ""),
        "export_status": export_record.get("export_status", ""),
        "generated_from_pack_draft_ref": export_record.get("generated_from_pack_draft_ref", ""),
        "sha256": fixity.get("sha256", ""),
        "fixity_algorithm": fixity.get("algorithm", ""),
        "review_required": bool(export_record.get("review_gates", {}).get("review_required_before_pack_import", True)),
        "exported_pack_is_submitted": bool(truth.get("exported_pack_is_submitted", False)),
        "exported_pack_is_accepted_pack": bool(truth.get("exported_pack_is_accepted_pack", False)),
        "exported_pack_can_mutate_public_index": bool(truth.get("exported_pack_can_mutate_public_index", False)),
        "exported_pack_can_mutate_master_index": bool(truth.get("exported_pack_can_mutate_master_index", False)),
        "hosted_upload": bool(metadata.get("hosted_upload", False)),
        "real_signing_enabled": bool(export_record.get("signature_policy", {}).get("real_signing_enabled", False)),
    }


def classify_export_pack_type(export_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    active_policy = policy or default_policy()
    explicit = str(export_record.get("export_pack_type") or export_record.get("requested_pack_type") or "").strip()
    if explicit in active_policy.get("allowed_export_types", ALLOWED_EXPORT_TYPES):
        return explicit
    draft_type = str(export_record.get("pack_type", ""))
    return PACK_TYPE_TO_EXPORT_TYPE.get(draft_type, "policy_blocked_pack_export")


def compute_pack_fixity(export_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    active_policy = policy or default_policy()
    allowed_algorithms = set(active_policy.get("allowed_hash_algorithms", ["sha256"]))
    if "sha256" not in allowed_algorithms:
        return {
            "algorithm": "sha256",
            "status": "policy_blocked",
            "sha256": "",
            "hash_input_scope": "deterministic_export_payload_without_fixity_or_manifest",
            "deterministic_serialization": True,
        }
    payload = deepcopy(dict(export_record))
    payload["fixity"] = {}
    payload["export_manifest"] = {}
    digest = hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()
    return {
        "algorithm": "sha256",
        "status": "computed_local",
        "sha256": digest,
        "hash_input_scope": "deterministic_export_payload_without_fixity_or_manifest",
        "deterministic_serialization": True,
        "real_signature": False,
        "authenticity_claim": "local_fixity_only_not_signature",
    }


def build_export_manifest(export_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fixity = export_record.get("fixity", {})
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "manifest_id": f"export_manifest.{_digest({'export': export_record.get('pack_export_id'), 'sha256': fixity.get('sha256', '')})[:12]}.v0",
        "pack_export_id": export_record.get("pack_export_id", ""),
        "export_pack_type": export_record.get("export_pack_type", ""),
        "export_status": export_record.get("export_status", ""),
        "export_format": export_record.get("export_format", ""),
        "generated_from_pack_draft_ref": export_record.get("generated_from_pack_draft_ref", ""),
        "fixity": deepcopy(dict(fixity)),
        "signature_status": "unsigned_placeholder_only",
        "review_required": True,
        "import_allowed": False,
        "submission_allowed": False,
        "hosted_upload_allowed": False,
        "acceptance_allowed": False,
        "public_index_mutation_allowed": False,
        "master_index_mutation_allowed": False,
    }


def detect_pack_export_truth_boundary_violations(export_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    truth = export_record.get("truth_boundary", {})
    if not isinstance(truth, Mapping):
        return ["truth_boundary must be an object"]
    errors: list[str] = []
    for field in sorted(TRUTH_BOUNDARY_FALSE_FIELDS):
        if truth.get(field) is not False:
            errors.append(f"truth_boundary.{field} must be false")
    for field in sorted(TRUTH_BOUNDARY_TRUE_FIELDS):
        if truth.get(field) is not True:
            errors.append(f"truth_boundary.{field} must be true")
    return errors


def detect_pack_export_product_boundary_violations(export_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    product = export_record.get("product_boundary", {})
    if not isinstance(product, Mapping):
        return ["product_boundary must be an object"]
    errors: list[str] = []
    for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS):
        if product.get(field) is not False:
            errors.append(f"product_boundary.{field} must be false")
    for field in sorted(PRODUCT_BOUNDARY_TRUE_FIELDS):
        if product.get(field) is not True:
            errors.append(f"product_boundary.{field} must be true")
    return errors


def detect_forbidden_export_input(input_pack_draft: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    active_policy = policy or default_policy()
    errors: list[str] = []
    input_type = _classify_input_pack_draft(input_pack_draft)
    if input_type not in active_policy.get("allowed_input_types", ALLOWED_INPUT_TYPES):
        errors.append(f"input pack draft type is not allowed: {input_type}")
    if input_type in active_policy.get("forbidden_input_types", FORBIDDEN_INPUT_TYPES):
        errors.append(f"input pack draft type is forbidden: {input_type}")
    if input_pack_draft.get("schema_version") != pack_builder.SCHEMA_VERSION:
        errors.append(f"input pack draft schema_version must be {pack_builder.SCHEMA_VERSION}")
    errors.extend(_scan_forbidden_claims(input_pack_draft))
    return sorted(dict.fromkeys(errors))


def build_pack_export_result(
    request: Mapping[str, Any],
    export_record: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    active_policy = policy or default_policy()
    request_errors = validate_pack_export_request(request, active_policy)
    export_errors = validate_pack_export(export_record, active_policy)
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "pack_export_result_id": f"pack_export_result.{_digest({'request': request, 'export': export_record})[:12]}.v0",
        "result_status": "policy_blocked" if export_record.get("export_status") == "policy_blocked" else "exported_local",
        "request_summary": {
            "pack_export_request_id": request.get("pack_export_request_id", ""),
            "requested_pack_type": request.get("requested_pack_type", ""),
            "request_status": request.get("request_status", ""),
        },
        "pack_export": deepcopy(dict(export_record)),
        "export_summary": summarize_pack_export(export_record),
        "validation": {
            "request_errors": request_errors,
            "export_errors": export_errors,
            "error_count": len(request_errors) + len(export_errors),
        },
        "runtime_scope": {
            "explicit_input_only": True,
            "local_only": True,
            "fixture_only": True,
            "writes_no_files_by_default": True,
            "pack_export_only": True,
            "pack_import_enabled": False,
            "pack_submission_enabled": False,
            "hosted_upload_enabled": False,
            "pack_acceptance_enabled": False,
            "real_signing_enabled": False,
            "public_index_mutation_enabled": False,
            "master_index_mutation_enabled": False,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Pack export result records a local export draft only.",
            "No pack is imported, submitted, uploaded, accepted, or signed with a real key.",
        ],
    }


def format_pack_export_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Pack Export Summary",
        "",
        f"- Export type: {summary.get('export_pack_type', '')}",
        f"- Export status: {summary.get('export_status', '')}",
        f"- Pack draft: {summary.get('generated_from_pack_draft_ref', '')}",
        f"- SHA-256: {summary.get('sha256', '')}",
        f"- Review required: {str(summary.get('review_required', True)).lower()}",
        f"- Submitted: {str(summary.get('exported_pack_is_submitted', False)).lower()}",
        f"- Accepted pack: {str(summary.get('exported_pack_is_accepted_pack', False)).lower()}",
        f"- Hosted upload: {str(summary.get('hosted_upload', False)).lower()}",
        f"- Public index mutation: {str(summary.get('exported_pack_can_mutate_public_index', False)).lower()}",
        f"- Master index mutation: {str(summary.get('exported_pack_can_mutate_master_index', False)).lower()}",
        f"- Real signing enabled: {str(summary.get('real_signing_enabled', False)).lower()}",
    ]
    return "\n".join(lines) + "\n"


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON input must be an object")
    return payload


def _export_status(draft: Mapping[str, Any], export_type: str) -> str:
    if export_type == "policy_blocked_pack_export" or draft.get("pack_status") == "policy_blocked":
        return "policy_blocked"
    if export_type in FUTURE_EXPORT_TYPES:
        return "deferred"
    if export_type == "index_pack_preview_export":
        return "validate_only"
    return "exported_local"


def _classify_input_pack_draft(draft: Mapping[str, Any]) -> str:
    pack_type = str(draft.get("pack_type", ""))
    if pack_type == "policy_blocked_pack":
        return "policy_blocked_pack_draft"
    return pack_type


def _public_draft_payload(draft: Mapping[str, Any]) -> dict[str, Any]:
    allowed_fields = [
        "schema_version",
        "pack_draft_id",
        "pack_type",
        "pack_status",
        "pack_label",
        "generated_from",
        "input_record_refs",
        "input_record_summary",
        "pack_contents",
        "source_summary",
        "evidence_summary",
        "candidate_summary",
        "review_summary",
        "limitations",
        "blocked_items",
        "review_gates",
        "truth_boundary",
        "product_boundary",
        "no_goals",
        "notes",
    ]
    return {field: deepcopy(draft[field]) for field in allowed_fields if field in draft}


def _blocked_items(draft: Mapping[str, Any], policy: Mapping[str, Any]) -> list[str]:
    blocked = list(draft.get("blocked_items", [])) if isinstance(draft.get("blocked_items", []), list) else []
    blocked.extend(detect_forbidden_export_input(draft, policy))
    return sorted(dict.fromkeys(str(item) for item in blocked))


def _limitations(export_type: str, export_status: str) -> list[str]:
    limitations = [
        "Export is not imported, submitted, uploaded, published, accepted, or public truth.",
        "Export cannot mutate public index or master index.",
        "Export cannot claim rights clearance, malware safety, verified installability, or production readiness.",
        "SHA-256 fixity is local deterministic hashing only and not a real signature.",
    ]
    if export_type == "index_pack_preview_export":
        limitations.append("Index pack preview export does not rebuild or mutate an index.")
    if export_status == "policy_blocked":
        limitations.append("Policy-blocked export remains blocked until separate review.")
    return limitations


def _signature_policy() -> dict[str, Any]:
    return {
        "signature_status": "unsigned_placeholder_only",
        "real_signing_enabled": False,
        "signature_placeholder_allowed": True,
        "private_keys_allowed": False,
        "claims_cryptographic_signature": False,
        "notes": "No real signing keys are used by this runtime.",
    }


def _truth_boundary(existing: Any = None) -> dict[str, bool]:
    truth = {field: False for field in TRUTH_BOUNDARY_FALSE_FIELDS}
    truth.update({field: True for field in TRUTH_BOUNDARY_TRUE_FIELDS})
    if isinstance(existing, Mapping):
        for key in truth:
            if key in existing:
                truth[key] = bool(existing[key])
    return truth


def _product_boundary(existing: Any = None) -> dict[str, bool]:
    product = {field: False for field in PRODUCT_BOUNDARY_FALSE_FIELDS}
    product.update({field: True for field in PRODUCT_BOUNDARY_TRUE_FIELDS})
    if isinstance(existing, Mapping):
        for key in product:
            if key in existing:
                product[key] = bool(existing[key])
    return product


def _review_gates(existing: Any = None) -> dict[str, bool]:
    gates = {field: True for field in REVIEW_GATE_TRUE_FIELDS}
    if isinstance(existing, Mapping):
        for key in gates:
            if key in existing:
                gates[key] = bool(existing[key])
    return gates


def _validate_fixity(export_record: Mapping[str, Any], policy: Mapping[str, Any]) -> list[str]:
    fixity = export_record.get("fixity", {})
    if not isinstance(fixity, Mapping):
        return ["fixity must be an object"]
    errors: list[str] = []
    if fixity.get("algorithm") != "sha256":
        errors.append("fixity.algorithm must be sha256")
    if fixity.get("deterministic_serialization") is not True:
        errors.append("fixity.deterministic_serialization must be true")
    sha256_value = str(fixity.get("sha256", ""))
    if not re.fullmatch(r"[0-9a-f]{64}", sha256_value):
        errors.append("fixity.sha256 must be a lowercase SHA-256 hex digest")
    if fixity.get("real_signature") is not False:
        errors.append("fixity.real_signature must be false")
    expected = compute_pack_fixity(export_record, policy).get("sha256")
    if sha256_value and expected and sha256_value != expected:
        errors.append("fixity.sha256 does not match deterministic export payload")
    return errors


def _validate_signature_policy(export_record: Mapping[str, Any]) -> list[str]:
    signature = export_record.get("signature_policy", {})
    if not isinstance(signature, Mapping):
        return ["signature_policy must be an object"]
    errors: list[str] = []
    required_false = {
        "real_signing_enabled",
        "private_keys_allowed",
        "claims_cryptographic_signature",
    }
    for field in sorted(required_false):
        if signature.get(field) is not False:
            errors.append(f"signature_policy.{field} must be false")
    if signature.get("signature_status") != "unsigned_placeholder_only":
        errors.append("signature_policy.signature_status must be unsigned_placeholder_only")
    if signature.get("signature_placeholder_allowed") is not True:
        errors.append("signature_policy.signature_placeholder_allowed must be true")
    return errors


def _detect_review_gate_violations(export_record: Mapping[str, Any]) -> list[str]:
    gates = export_record.get("review_gates", {})
    if not isinstance(gates, Mapping):
        return ["review_gates must be an object"]
    errors: list[str] = []
    for field in sorted(REVIEW_GATE_TRUE_FIELDS):
        if gates.get(field) is not True:
            errors.append(f"review_gates.{field} must be true")
    return errors


def _detect_request_boundary_violations(request: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    truth = request.get("truth_boundary", {})
    product = request.get("product_boundary", {})
    gates = request.get("review_gates", {})
    signature = request.get("signature_policy", {})
    fixity = request.get("fixity_policy", {})
    if isinstance(truth, Mapping):
        for field in sorted(TRUTH_BOUNDARY_FALSE_FIELDS):
            if truth.get(field) is not False:
                errors.append(f"truth_boundary.{field} must be false")
        for field in sorted(TRUTH_BOUNDARY_TRUE_FIELDS):
            if truth.get(field) is not True:
                errors.append(f"truth_boundary.{field} must be true")
    else:
        errors.append("truth_boundary must be an object")
    if isinstance(product, Mapping):
        for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS):
            if product.get(field) is not False:
                errors.append(f"product_boundary.{field} must be false")
    else:
        errors.append("product_boundary must be an object")
    if isinstance(gates, Mapping):
        for field in sorted(REVIEW_GATE_TRUE_FIELDS):
            if gates.get(field) is not True:
                errors.append(f"review_gates.{field} must be true")
    else:
        errors.append("review_gates must be an object")
    if isinstance(signature, Mapping):
        for field in ("real_signing_enabled", "private_keys_allowed", "claims_cryptographic_signature"):
            if signature.get(field) is not False:
                errors.append(f"signature_policy.{field} must be false")
    else:
        errors.append("signature_policy must be an object")
    if isinstance(fixity, Mapping):
        if fixity.get("algorithm") != "sha256":
            errors.append("fixity_policy.algorithm must be sha256")
        if fixity.get("real_signing_enabled") is not False:
            errors.append("fixity_policy.real_signing_enabled must be false")
    else:
        errors.append("fixity_policy must be an object")
    return errors


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def _scan_forbidden_claims(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text in {"api_key", "secret", "credential", "password", "cookie", "session_token", "token", "private_key"}:
                errors.append(f"{path}.{key}: credential-like field is forbidden")
            errors.extend(_scan_forbidden_claims(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_scan_forbidden_claims(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        for phrase in sorted(FORBIDDEN_CLAIM_PHRASES):
            if phrase in lowered and not _negated_or_boundary_phrase(lowered, phrase):
                errors.append(f"{path}: forbidden claim phrase: {phrase}")
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path}: private local path is forbidden")
        for pattern in CREDENTIAL_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path}: credential-like text is forbidden")
    return errors


def _negated_or_boundary_phrase(lowered: str, phrase: str) -> bool:
    start = lowered.find(phrase)
    if start < 0:
        return False
    prefix = lowered[max(0, start - 96) : start]
    allowed_markers = (
        "no ",
        "not ",
        "cannot ",
        "can not ",
        "must not ",
        "does not ",
        "do not ",
        "without ",
        "false",
        "placeholder",
        "unsigned",
    )
    return any(marker in prefix for marker in allowed_markers)
