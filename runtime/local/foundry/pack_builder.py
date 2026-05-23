"""Local pack builder helpers.

Pack drafts are explicit-input, review-gated bundles for local review. They are
not pack import, pack submission, accepted packs, accepted evidence, public
truth, public-index mutation, or master-index mutation.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "local_pack_draft.v0"
REQUEST_SCHEMA_VERSION = "pack_builder_request.v0"
RESULT_SCHEMA_VERSION = "pack_builder_result.v0"

REQUEST_STATUSES = {
    "example_only",
    "planned",
    "local_draft_only",
    "fixture_only",
    "policy_blocked",
    "deferred",
    "not_evaluable",
}

ALLOWED_PACK_TYPES = {
    "source_pack_draft",
    "evidence_pack_draft",
    "contribution_pack_draft",
    "review_pack_draft",
    "index_pack_preview",
    "compatibility_pack_draft_future",
    "alias_pack_draft_future",
    "hash_pack_draft_future",
    "extraction_pack_draft_future",
    "query_need_pack_draft_future",
    "snapshot_pack_draft_future",
    "policy_blocked_pack",
}

CURRENT_PACK_TYPES = {
    "source_pack_draft",
    "evidence_pack_draft",
    "contribution_pack_draft",
    "review_pack_draft",
    "index_pack_preview",
    "policy_blocked_pack",
}

FUTURE_PACK_TYPES = ALLOWED_PACK_TYPES - CURRENT_PACK_TYPES

ALLOWED_PACK_STATUSES = {
    "example_only",
    "drafted_local",
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

CURRENT_PACK_STATUSES = {
    "example_only",
    "drafted_local",
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
    "source_cache_record",
    "evidence_ledger_record",
    "candidate_record",
    "search_need_record",
    "search_miss_record",
    "query_observation_record",
    "local_review_queue_entry",
    "source_cache_to_evidence_bridge_result",
    "candidate_promotion_dry_run",
    "reviewed_public_record_proposal",
    "workunit_result",
    "node_policy_evaluation",
    "observation_candidate",
    "committed_pack_example",
    "explicit_fixture",
}

FORBIDDEN_INPUT_TYPES = {
    "unreviewed_live_source_result",
    "scraped_search_result",
    "scraped_forum_thread",
    "bulk_reddit_content",
    "private_user_file",
    "secret_or_credential",
    "executable_download",
    "installer_payload",
    "raw_browser_profile",
    "account_session_data",
    "telemetry_stream",
    "unreviewed_external_api_payload",
    "accepted_truth_without_review",
    "master_index_record_current",
}

ALLOWED_OUTPUT_TYPES = {
    "pack_draft",
    "pack_builder_result",
    "pack_summary",
    "pack_validation_report",
    "pack_blocker_report",
    "source_pack_draft",
    "evidence_pack_draft",
    "contribution_pack_draft",
    "review_pack_draft",
    "index_pack_preview",
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
}

TRUTH_BOUNDARY_FALSE_FIELDS = {
    "pack_draft_is_public_truth",
    "pack_draft_is_accepted_evidence",
    "pack_draft_is_accepted_pack",
    "pack_draft_can_mutate_public_index",
    "pack_draft_can_mutate_master_index",
    "pack_draft_can_claim_rights_clearance",
    "pack_draft_can_claim_malware_safety",
    "pack_draft_can_claim_verified_installability",
    "pack_draft_can_claim_exhaustive_global_search",
    "pack_draft_can_claim_production_readiness",
}

TRUTH_BOUNDARY_TRUE_FIELDS = {"human_review_required_before_submission_or_import"}

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
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}

PRODUCT_BOUNDARY_TRUE_FIELDS = {"implemented_pack_builder_runtime"}

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
    "hosted upload completed",
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
)


def default_policy() -> dict[str, Any]:
    return {
        "allowed_pack_types": sorted(ALLOWED_PACK_TYPES),
        "current_pack_types": sorted(CURRENT_PACK_TYPES),
        "future_pack_types": sorted(FUTURE_PACK_TYPES),
        "allowed_pack_statuses": sorted(ALLOWED_PACK_STATUSES),
        "current_pack_statuses": sorted(CURRENT_PACK_STATUSES),
        "allowed_request_statuses": sorted(REQUEST_STATUSES),
        "allowed_input_types": sorted(ALLOWED_INPUT_TYPES),
        "forbidden_input_types": sorted(FORBIDDEN_INPUT_TYPES),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "review_required_before_pack_import": True,
        "review_required_before_pack_submission": True,
        "pack_import_disabled_current": True,
        "pack_submission_disabled_current": True,
        "pack_acceptance_disabled_current": True,
        "public_index_mutation_disabled_current": True,
        "master_index_mutation_disabled_current": True,
    }


def build_pack_draft(
    input_records: Sequence[Mapping[str, Any]],
    pack_type: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic local pack draft from explicit input records."""

    active_policy = policy or default_policy()
    records = [deepcopy(dict(record)) for record in input_records]
    normalized_pack_type = _normalize_pack_type(pack_type, active_policy)
    input_classes = classify_pack_inputs(records, active_policy)
    forbidden_inputs = detect_forbidden_pack_input(records, active_policy)
    blocked_items = list(forbidden_inputs)
    pack_status = _pack_status(normalized_pack_type, blocked_items)
    input_refs = [_record_ref(record, input_classes[index]) for index, record in enumerate(records)]
    public_summaries = [_record_summary(record, input_classes[index]) for index, record in enumerate(records)]
    pack = {
        "schema_version": SCHEMA_VERSION,
        "pack_draft_id": f"pack_draft.{normalized_pack_type}.{_digest({'type': normalized_pack_type, 'refs': input_refs})[:12]}.v0",
        "pack_type": normalized_pack_type,
        "pack_status": pack_status,
        "pack_label": _pack_label(normalized_pack_type),
        "generated_from": "explicit_input_only",
        "input_record_refs": input_refs,
        "input_record_summary": {
            "input_record_count": len(records),
            "input_type_counts": dict(sorted(Counter(input_classes).items())),
            "public_safe_examples_only": True,
            "input_records_are_imported": False,
            "input_records_are_accepted_truth": False,
        },
        "pack_contents": {
            "content_mode": "local_draft_preview",
            "pack_type": normalized_pack_type,
            "records": public_summaries,
            "imported_state": False,
            "submitted_state": False,
            "accepted_state": False,
            "public_index_mutation": False,
            "master_index_mutation": False,
        },
        "source_summary": _source_summary(records, input_classes),
        "evidence_summary": _evidence_summary(records, input_classes),
        "candidate_summary": _candidate_summary(records, input_classes),
        "review_summary": {
            "review_required": True,
            "review_gate_count": len(REVIEW_GATE_TRUE_FIELDS),
            "review_status": "needs_review",
        },
        "limitations": _limitations(normalized_pack_type, blocked_items),
        "blocked_items": blocked_items,
        "review_gates": _review_gates(),
        "validation_summary": {
            "validation_errors": [],
            "pack_import_enabled": False,
            "pack_submission_enabled": False,
            "pack_acceptance_enabled": False,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "no_goals": [
            "no pack import",
            "no pack submission",
            "no accepted pack",
            "no public index mutation",
            "no master index mutation",
        ],
        "notes": [
            "Pack draft is local review material only.",
            "Review is required before any future import, submission, public use, or index use.",
        ],
    }
    return pack


def validate_pack_builder_request(request: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    active_policy = policy or default_policy()
    errors: list[str] = []
    required = {
        "pack_builder_request_id",
        "requested_pack_type",
        "request_status",
        "input_refs",
        "input_summary",
        "review_gates",
        "truth_boundary",
        "product_boundary",
        "no_goals",
    }
    for field in sorted(required):
        if field not in request:
            errors.append(f"missing required request field: {field}")
    if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
        errors.append(f"schema_version must be {REQUEST_SCHEMA_VERSION}")
    if request.get("request_status") not in active_policy.get("allowed_request_statuses", REQUEST_STATUSES):
        errors.append(f"request_status is not allowed: {request.get('request_status')}")
    if request.get("requested_pack_type") not in active_policy.get("allowed_pack_types", ALLOWED_PACK_TYPES):
        errors.append(f"requested_pack_type is not allowed: {request.get('requested_pack_type')}")
    errors.extend(_detect_request_boundary_violations(request))
    errors.extend(_scan_forbidden_claims(request))
    return sorted(dict.fromkeys(errors))


def validate_pack_draft(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return deterministic validation errors for a local pack draft."""

    active_policy = policy or default_policy()
    errors: list[str] = []
    required = {
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
        "validation_summary",
        "truth_boundary",
        "product_boundary",
        "no_goals",
        "notes",
    }
    for field in sorted(required):
        if field not in pack:
            errors.append(f"missing required pack field: {field}")
    if pack.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if pack.get("pack_type") not in active_policy.get("allowed_pack_types", ALLOWED_PACK_TYPES):
        errors.append(f"pack_type is not allowed: {pack.get('pack_type')}")
    if pack.get("pack_type") not in active_policy.get("current_pack_types", CURRENT_PACK_TYPES):
        errors.append(f"pack_type is not buildable in current runtime: {pack.get('pack_type')}")
    if pack.get("pack_status") not in active_policy.get("allowed_pack_statuses", ALLOWED_PACK_STATUSES):
        errors.append(f"pack_status is not allowed: {pack.get('pack_status')}")
    if pack.get("pack_status") not in active_policy.get("current_pack_statuses", CURRENT_PACK_STATUSES):
        errors.append(f"pack_status is not allowed in current runtime: {pack.get('pack_status')}")
    if pack.get("pack_status") in {"submitted_future", "accepted_public_future"}:
        errors.append(f"pack_status is future-only and not allowed currently: {pack.get('pack_status')}")
    contents = pack.get("pack_contents", {})
    if not isinstance(contents, Mapping):
        errors.append("pack_contents must be an object")
    else:
        for field in ("imported_state", "submitted_state", "accepted_state", "public_index_mutation", "master_index_mutation"):
            if contents.get(field) is not False:
                errors.append(f"pack_contents.{field} must be false")
    errors.extend(detect_pack_truth_boundary_violations(pack, active_policy))
    errors.extend(detect_pack_product_boundary_violations(pack, active_policy))
    errors.extend(_detect_review_gate_violations(pack))
    errors.extend(_scan_forbidden_claims(pack))
    return sorted(dict.fromkeys(errors))


def summarize_pack_draft(pack: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "pack_draft_id": pack.get("pack_draft_id", ""),
        "pack_type": pack.get("pack_type", ""),
        "pack_status": pack.get("pack_status", ""),
        "input_record_count": pack.get("input_record_summary", {}).get("input_record_count", 0),
        "blocked_item_count": len(pack.get("blocked_items", [])),
        "review_required": bool(pack.get("review_summary", {}).get("review_required", True)),
        "pack_draft_is_accepted_pack": bool(pack.get("truth_boundary", {}).get("pack_draft_is_accepted_pack", False)),
        "pack_draft_can_mutate_public_index": bool(pack.get("truth_boundary", {}).get("pack_draft_can_mutate_public_index", False)),
        "pack_draft_can_mutate_master_index": bool(pack.get("truth_boundary", {}).get("pack_draft_can_mutate_master_index", False)),
    }


def classify_pack_type(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    active_policy = policy or default_policy()
    explicit = str(pack.get("pack_type") or pack.get("requested_pack_type") or "").strip()
    if explicit in active_policy.get("allowed_pack_types", ALLOWED_PACK_TYPES):
        return explicit
    return "policy_blocked_pack"


def classify_pack_inputs(input_records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [_classify_input_record(record) for record in input_records]


def detect_pack_truth_boundary_violations(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    truth = pack.get("truth_boundary", {})
    errors: list[str] = []
    if not isinstance(truth, Mapping):
        return ["truth_boundary must be an object"]
    for field in sorted(TRUTH_BOUNDARY_FALSE_FIELDS):
        if truth.get(field) is not False:
            errors.append(f"truth_boundary.{field} must be false")
    for field in sorted(TRUTH_BOUNDARY_TRUE_FIELDS):
        if truth.get(field) is not True:
            errors.append(f"truth_boundary.{field} must be true")
    return errors


def detect_pack_product_boundary_violations(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    product = pack.get("product_boundary", {})
    errors: list[str] = []
    if not isinstance(product, Mapping):
        return ["product_boundary must be an object"]
    for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS):
        if product.get(field) is not False:
            errors.append(f"product_boundary.{field} must be false")
    for field in sorted(PRODUCT_BOUNDARY_TRUE_FIELDS):
        if product.get(field) is not True:
            errors.append(f"product_boundary.{field} must be true")
    return errors


def detect_forbidden_pack_input(input_records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> list[str]:
    active_policy = policy or default_policy()
    forbidden = set(active_policy.get("forbidden_input_types", FORBIDDEN_INPUT_TYPES))
    allowed = set(active_policy.get("allowed_input_types", ALLOWED_INPUT_TYPES))
    errors: list[str] = []
    for index, record in enumerate(input_records):
        input_type = str(record.get("input_type", "")).strip()
        classified = _classify_input_record(record)
        candidate_types = {classified}
        if input_type:
            candidate_types.add(input_type)
        for candidate in sorted(candidate_types):
            if candidate in forbidden:
                errors.append(f"input[{index}] type is forbidden: {candidate}")
        if classified not in allowed:
            errors.append(f"input[{index}] type is not allowed: {classified}")
        errors.extend(f"input[{index}] {error}" for error in _scan_forbidden_claims(record))
    return sorted(dict.fromkeys(errors))


def build_pack_builder_result(
    request: Mapping[str, Any],
    pack: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    active_policy = policy or default_policy()
    request_errors = validate_pack_builder_request(request, active_policy)
    pack_errors = validate_pack_draft(pack, active_policy)
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "pack_builder_result_id": f"pack_builder_result.{_digest({'request': request, 'pack': pack})[:12]}.v0",
        "result_status": "policy_blocked" if pack.get("pack_status") == "policy_blocked" else "drafted_local",
        "request_summary": {
            "pack_builder_request_id": request.get("pack_builder_request_id", ""),
            "requested_pack_type": request.get("requested_pack_type", ""),
            "request_status": request.get("request_status", ""),
        },
        "pack_draft": deepcopy(dict(pack)),
        "pack_summary": summarize_pack_draft(pack),
        "validation": {
            "request_errors": request_errors,
            "pack_errors": pack_errors,
            "error_count": len(request_errors) + len(pack_errors),
        },
        "runtime_scope": {
            "explicit_input_only": True,
            "local_only": True,
            "fixture_only": True,
            "writes_no_files_by_default": True,
            "pack_draft_only": True,
            "pack_import_enabled": False,
            "pack_submission_enabled": False,
            "pack_acceptance_enabled": False,
            "public_index_mutation_enabled": False,
            "master_index_mutation_enabled": False,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Pack builder result records a local draft only.",
            "No pack is imported, submitted, accepted, or published by this result.",
        ],
    }


def summarize_pack_builder_result(result: Mapping[str, Any]) -> dict[str, Any]:
    pack_summary = dict(result.get("pack_summary", {}))
    validation = result.get("validation", {})
    return {
        "pack_builder_result_id": result.get("pack_builder_result_id", ""),
        "result_status": result.get("result_status", ""),
        "pack_type": pack_summary.get("pack_type", ""),
        "pack_status": pack_summary.get("pack_status", ""),
        "input_record_count": pack_summary.get("input_record_count", 0),
        "blocked_item_count": pack_summary.get("blocked_item_count", 0),
        "validation_error_count": validation.get("error_count", 0),
        "pack_import_enabled": result.get("runtime_scope", {}).get("pack_import_enabled", False),
        "pack_submission_enabled": result.get("runtime_scope", {}).get("pack_submission_enabled", False),
        "pack_acceptance_enabled": result.get("runtime_scope", {}).get("pack_acceptance_enabled", False),
    }


def format_pack_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Pack Builder Summary",
        "",
        f"- Pack type: {summary.get('pack_type', '')}",
        f"- Pack status: {summary.get('pack_status', '')}",
        f"- Input records: {summary.get('input_record_count', 0)}",
        f"- Blocked items: {summary.get('blocked_item_count', 0)}",
        f"- Review required: {str(summary.get('review_required', True)).lower()}",
        f"- Accepted pack: {str(summary.get('pack_draft_is_accepted_pack', False)).lower()}",
        f"- Public index mutation: {str(summary.get('pack_draft_can_mutate_public_index', False)).lower()}",
        f"- Master index mutation: {str(summary.get('pack_draft_can_mutate_master_index', False)).lower()}",
    ]
    if summary.get("validation_error_count") is not None:
        lines.append(f"- Validation errors: {summary.get('validation_error_count', 0)}")
    return "\n".join(lines) + "\n"


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON input must be an object")
    return payload


def _normalize_pack_type(pack_type: str, policy: Mapping[str, Any]) -> str:
    if pack_type in policy.get("allowed_pack_types", ALLOWED_PACK_TYPES):
        return pack_type
    return "policy_blocked_pack"


def _pack_status(pack_type: str, blocked_items: Sequence[str]) -> str:
    if pack_type == "policy_blocked_pack" or blocked_items:
        return "policy_blocked"
    if pack_type in FUTURE_PACK_TYPES:
        return "deferred"
    if pack_type == "index_pack_preview":
        return "validate_only"
    return "drafted_local"


def _pack_label(pack_type: str) -> str:
    return pack_type.replace("_", " ").title()


def _classify_input_record(record: Mapping[str, Any]) -> str:
    schema = str(record.get("schema_version", ""))
    if schema == "local_source_cache_record.v0" or record.get("source_cache_record_id"):
        return "source_cache_record"
    if schema == "local_evidence_ledger_record.v0" or record.get("evidence_record_id"):
        return "evidence_ledger_record"
    if schema == "candidate_record.v0" or record.get("candidate_id"):
        return "candidate_record"
    if schema == "search_need_record.v0" or record.get("search_need_id"):
        return "search_need_record"
    if schema == "search_miss_record.v0" or record.get("search_miss_id"):
        return "search_miss_record"
    if schema == "query_observation_record.v0" or record.get("query_observation_id"):
        return "query_observation_record"
    if schema == "local_review_queue_entry.v0" or record.get("review_entry_id"):
        return "local_review_queue_entry"
    if schema == "source_cache_to_evidence_bridge_result.v0" or record.get("bridge_result_id"):
        return "source_cache_to_evidence_bridge_result"
    if schema == "candidate_promotion_dry_run.v0" or record.get("promotion_dry_run_id"):
        return "candidate_promotion_dry_run"
    if schema == "reviewed_public_record_proposal.v0" or record.get("reviewed_public_record_proposal_id"):
        return "reviewed_public_record_proposal"
    if schema == "work_unit_result.v0" or record.get("workunit_result_id"):
        return "workunit_result"
    if schema == "node_policy_evaluation_result.v0" or record.get("node_policy_evaluation_id"):
        return "node_policy_evaluation"
    if schema == "observation_candidate.v0":
        return "observation_candidate"
    return str(record.get("input_type", "explicit_fixture"))


def _record_ref(record: Mapping[str, Any], input_type: str) -> str:
    for key in (
        "source_cache_record_id",
        "evidence_record_id",
        "candidate_id",
        "review_entry_id",
        "bridge_result_id",
        "promotion_dry_run_id",
        "reviewed_public_record_proposal_id",
        "workunit_result_id",
        "search_need_id",
        "input_id",
    ):
        if record.get(key):
            return str(record[key])
    return f"{input_type}.{_digest(record)[:12]}.v0"


def _record_summary(record: Mapping[str, Any], input_type: str) -> dict[str, Any]:
    label = (
        record.get("source_label")
        or record.get("evidence_label")
        or record.get("candidate_label")
        or record.get("proposal_label")
        or record.get("review_subject_summary")
        or record.get("input_summary")
        or _record_ref(record, input_type)
    )
    status = (
        record.get("source_cache_record_status")
        or record.get("evidence_record_status")
        or record.get("candidate_status")
        or record.get("review_entry_status")
        or record.get("proposal_status")
        or record.get("input_status")
        or "fixture_only"
    )
    return {
        "input_type": input_type,
        "record_ref": _record_ref(record, input_type),
        "record_status": str(status),
        "record_label": str(label),
        "public_safe_summary_only": True,
    }


def _source_summary(records: Sequence[Mapping[str, Any]], input_classes: Sequence[str]) -> dict[str, Any]:
    source_refs: list[str] = []
    for record in records:
        for key in ("source_id", "source_locator", "source_label"):
            if record.get(key):
                source_refs.append(str(record[key]))
    return {
        "source_ref_count": len(source_refs),
        "source_refs": sorted(dict.fromkeys(source_refs)),
        "source_pack_candidate": "source_cache_record" in input_classes,
        "source_truth_claimed": False,
    }


def _evidence_summary(records: Sequence[Mapping[str, Any]], input_classes: Sequence[str]) -> dict[str, Any]:
    evidence_refs = [_record_ref(record, "evidence_ledger_record") for index, record in enumerate(records) if input_classes[index] == "evidence_ledger_record"]
    return {
        "evidence_ref_count": len(evidence_refs),
        "evidence_refs": evidence_refs,
        "evidence_acceptance_claimed": False,
        "review_required": True,
    }


def _candidate_summary(records: Sequence[Mapping[str, Any]], input_classes: Sequence[str]) -> dict[str, Any]:
    candidate_refs = [_record_ref(record, "candidate_record") for index, record in enumerate(records) if input_classes[index] == "candidate_record"]
    return {
        "candidate_ref_count": len(candidate_refs),
        "candidate_refs": candidate_refs,
        "candidate_acceptance_claimed": False,
        "review_required": True,
    }


def _limitations(pack_type: str, blocked_items: Sequence[str]) -> list[str]:
    limitations = [
        "Pack draft is not imported, submitted, accepted, published, or public truth.",
        "Pack draft cannot mutate public index or master index.",
        "Pack draft cannot claim rights clearance, malware safety, or verified installability.",
    ]
    if pack_type == "index_pack_preview":
        limitations.append("Index pack preview is a preview only and does not rebuild or mutate an index.")
    if blocked_items:
        limitations.append("Policy-blocked inputs prevent downstream pack use without review.")
    return limitations


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


def _detect_review_gate_violations(pack: Mapping[str, Any]) -> list[str]:
    gates = pack.get("review_gates", {})
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
    review_gates = request.get("review_gates", {})
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
    if isinstance(review_gates, Mapping):
        for field in sorted(REVIEW_GATE_TRUE_FIELDS):
            if review_gates.get(field) is not True:
                errors.append(f"review_gates.{field} must be true")
    else:
        errors.append("review_gates must be an object")
    return errors


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _scan_forbidden_claims(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text in {"api_key", "secret", "credential", "password", "cookie", "session_token", "token"}:
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
    )
    return any(marker in prefix for marker in allowed_markers)
