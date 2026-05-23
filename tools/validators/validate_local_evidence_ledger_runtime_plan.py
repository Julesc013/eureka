#!/usr/bin/env python3
"""Validate Track B local evidence ledger runtime planning artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]

INVENTORY_FILES = [
    "control/inventory/evidence_ledger/local_evidence_ledger_runtime_plan.json",
    "control/inventory/evidence_ledger/local_evidence_ledger_runtime_policy.json",
    "control/inventory/evidence_ledger/local_evidence_ledger_path_policy.json",
    "control/inventory/evidence_ledger/local_evidence_ledger_record_policy.json",
    "control/inventory/evidence_ledger/local_evidence_ledger_review_policy.json",
    "control/inventory/evidence_ledger/local_evidence_ledger_append_policy.json",
    "control/inventory/evidence_ledger/source_cache_to_evidence_bridge_plan.json",
    "control/inventory/evidence_ledger/local_evidence_ledger_rollout_plan.json",
]
DOC_FILES = [
    "docs/reference/LOCAL_EVIDENCE_LEDGER_RUNTIME_PLAN.md",
    "docs/architecture/LOCAL_EVIDENCE_LEDGER_MODEL.md",
    "docs/operations/LOCAL_EVIDENCE_LEDGER_APPROVAL_GATES.md",
    "docs/operations/LOCAL_EVIDENCE_LEDGER_PRIVACY_RISK_POLICY.md",
    "docs/operations/SOURCE_CACHE_TO_EVIDENCE_LEDGER_BRIDGE_PLAN.md",
]
EXAMPLE_FILES = [
    "examples/evidence/ledger/plans/minimal_local_evidence_ledger_plan_v0.json",
    "examples/evidence/ledger/plans/source_cache_bridge_evidence_ledger_plan_v0.json",
    "examples/evidence/ledger/plans/fixture_only_evidence_ledger_plan_v0.json",
    "examples/evidence/ledger/plans/policy_blocked_evidence_ledger_plan_v0.json",
]
AUDIT_FILES = [
    "control/audits/track-b-14-local-evidence-ledger-runtime-planning-v0/README.md",
    "control/audits/track-b-14-local-evidence-ledger-runtime-planning-v0/track_b_14_report.json",
    "control/audits/track-b-14-local-evidence-ledger-runtime-planning-v0/evidence_ledger_runtime_readiness.md",
    "control/audits/track-b-14-local-evidence-ledger-runtime-planning-v0/validation.md",
]

CURRENT_RUNTIME_STATUSES = {
    "planning_only",
    "runtime_not_implemented",
    "source_cache_bridge_not_implemented",
    "evidence_acceptance_disabled",
}
REQUIRED_FUTURE_BRIDGE_PHASES = {
    "bridge_phase_0_planning_only",
    "bridge_phase_1_fixture_mapping_future",
    "bridge_phase_2_source_cache_record_to_evidence_candidate_future",
    "bridge_phase_3_review_queue_integration_future",
    "bridge_phase_4_evidence_pack_export_future",
    "bridge_phase_5_reviewed_public_index_bridge_future",
}
REQUIRED_ROLLOUT_PHASES = {
    "phase_0_planning_only",
    "phase_1_fixture_only_runtime_future",
    "phase_2_source_cache_bridge_fixture_future",
    "phase_3_evidence_candidate_runtime_future",
    "phase_4_review_queue_integration_future",
    "phase_5_evidence_pack_export_future",
    "phase_6_reviewed_public_index_bridge_future",
}
REQUIRED_FORBIDDEN_CONVERSIONS = {
    "source_cache_record_to_accepted_evidence",
    "source_observation_to_accepted_truth",
    "evidence_candidate_to_verified_fact",
    "ai_draft_to_evidence_truth",
    "contribution_claim_to_accepted_public_record",
    "metadata_claim_to_rights_clearance",
    "checksum_claim_to_authenticity_proof_without_evidence",
    "compatibility_claim_to_verified_compatibility_without_review",
}
TRUTH_FALSE_FIELDS = {
    "evidence_record_is_public_truth",
    "evidence_record_is_accepted_evidence",
    "evidence_record_can_mutate_master_index",
    "evidence_record_can_claim_rights_clearance",
    "evidence_record_can_claim_malware_safety",
    "evidence_record_can_claim_verified_installability",
    "evidence_record_can_claim_exhaustive_global_search",
    "evidence_record_can_claim_production_readiness",
}
PRODUCT_FALSE_FIELDS = {
    "implemented_evidence_ledger_runtime",
    "implemented_source_cache_bridge",
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
    "enabled_pack_import_runtime",
    "enabled_review_runtime",
    "enabled_model_provider_calls",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}
REVIEW_TRUE_FIELDS = {
    "review_required_before_candidate_store_use",
    "review_required_before_public_index_use",
    "review_required_before_pack_export",
    "review_required_before_master_index",
    "review_required_before_rights_claim",
    "review_required_before_malware_safety_claim",
    "review_required_before_installability_claim",
    "review_required_before_source_cache_bridge",
}
REVIEW_FALSE_FIELDS = {
    "automatic_evidence_acceptance_allowed",
    "automatic_public_index_use_allowed",
    "automatic_master_index_mutation_allowed",
    "automatic_rights_clearance_allowed",
    "automatic_malware_safety_allowed",
    "automatic_installability_verification_allowed",
}
APPEND_TRUE_FIELDS = {
    "append_only_intent",
    "conflict_preservation_required",
    "provenance_required",
    "review_status_required",
    "no_silent_overwrite",
    "no_unreviewed_promotion",
    "no_master_index_mutation",
}
APPEND_FALSE_FIELDS = {
    "append_runtime_implemented",
    "append_storage_created",
}
REQUIRED_RECORD_STATUSES = {
    "example_only",
    "planned",
    "fixture_only",
    "recorded_local",
    "normalized",
    "evidence_candidate",
    "source_observation_candidate",
    "metadata_claim_candidate",
    "identity_claim_candidate",
    "compatibility_claim_candidate",
    "checksum_claim_candidate",
    "filename_or_member_claim_candidate",
    "source_locator_candidate",
    "manual_observation_candidate",
    "pack_claim_candidate",
    "contribution_claim_candidate",
    "conflicting",
    "needs_review",
    "evidence_needed",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "stale",
    "superseded",
    "deferred",
    "accepted_public_future",
    "rejected_future",
}
REQUIRED_RECORD_TYPES = {
    "source_observation",
    "source_cache_derived_claim",
    "metadata_claim",
    "identity_claim",
    "compatibility_claim",
    "checksum_claim",
    "filename_or_member_claim",
    "source_locator",
    "manual_observation_claim",
    "pack_claim",
    "contribution_claim",
    "conflict_record",
    "review_status_record",
    "provenance_link",
    "ai_draft_future",
    "discussion_derived_future",
}
REQUIRED_ALLOWED_FUTURE_ROOTS = {
    ".aide.local/eureka/evidence_ledger/",
    ".local/eureka/evidence_ledger/",
    ".cache/eureka/evidence_ledger/",
    "control/audits/**/generated/evidence_ledger/",
    "explicit temp test directory",
}
REQUIRED_FORBIDDEN_ROOT_HINTS = {
    "site/dist/",
    "runtime/",
    "contracts/",
    "native/",
    "snapshots/",
    "control/inventory/publication/",
    "master-index-related roots",
    ".git/",
}
PRIVATE_ROOTS = [
    Path(".aide.local/eureka/evidence_ledger"),
    Path(".local/eureka/evidence_ledger"),
    Path(".cache/eureka/evidence_ledger"),
]
FORBIDDEN_CLAIM_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\brights?\s+clear(?:ed|ance|ing)\b",
        r"\bmalware\s+(?:safe|safety|clean)\b",
        r"\bverified\s+installability\b",
        r"\binstallability\s+(?:verified|confirmed)\b",
        r"\bexhaustive\s+(?:global\s+)?search\b",
        r"\bproduction\s+ready\b",
        r"\blive\s+probe\s+(?:ran|executed|enabled)\b",
        r"\bsource\s+sync\s+(?:ran|executed|enabled)\b",
        r"\bdownload(?:ed|ing)?\s+binary\b",
        r"\bupload(?:ed|ing)?\s+to\s+hosted\b",
        r"\btelemetry\s+(?:enabled|exported|collected)\b",
        r"\bmaster\s*index\s+(?:mutated|updated|written)\b",
        r"\bconverted\s+source\s+observation\s+to\s+accepted\s+truth\b",
        r"\bevidence\s+candidate\s+(?:is\s+)?(?:converted\s+to\s+)?verified\s+fact\b",
        r"\bAI\s+draft\s+(?:is\s+)?evidence\s+truth\b",
    )
]
SECRET_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|secret|password|token|credential)\s*[:=]\s*[A-Za-z0-9_\-]{8,}"
)
PRIVATE_PATH_PATTERN = re.compile(
    r"(?i)([A-Za-z]:\\(?:Users|Documents and Settings|Windows|Temp)\\|/Users/[^/\s]+|/home/[^/\s]+|\\\\[^\\\s]+\\)"
)


def validate_local_evidence_ledger_runtime_plan(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in sorted(INVENTORY_FILES + DOC_FILES + EXAMPLE_FILES + AUDIT_FILES):
        if not (repo_root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    if errors:
        return _report(errors)

    payloads = {rel: _read_json(repo_root / rel) for rel in INVENTORY_FILES + EXAMPLE_FILES}
    errors.extend(validate_plan_record(payloads[INVENTORY_FILES[0]], INVENTORY_FILES[0]))
    errors.extend(_validate_runtime_policy(payloads[INVENTORY_FILES[1]], INVENTORY_FILES[1]))
    errors.extend(_validate_path_policy(payloads[INVENTORY_FILES[2]], repo_root, INVENTORY_FILES[2]))
    errors.extend(_validate_record_policy(payloads[INVENTORY_FILES[3]], INVENTORY_FILES[3]))
    errors.extend(_validate_review_policy(payloads[INVENTORY_FILES[4]], INVENTORY_FILES[4]))
    errors.extend(validate_append_policy(payloads[INVENTORY_FILES[5]], INVENTORY_FILES[5]))
    errors.extend(validate_bridge_plan(payloads[INVENTORY_FILES[6]], INVENTORY_FILES[6]))
    errors.extend(_validate_rollout_plan(payloads[INVENTORY_FILES[7]], INVENTORY_FILES[7]))

    for rel in EXAMPLE_FILES:
        errors.extend(validate_plan_record(payloads[rel], rel))
        errors.extend(_scan_payload_for_forbidden_content(payloads[rel], rel))

    audit_report = _read_json(repo_root / "control/audits/track-b-14-local-evidence-ledger-runtime-planning-v0/track_b_14_report.json")
    errors.extend(_validate_audit_report(audit_report))
    errors.extend(_validate_docs(repo_root))
    errors.extend(_validate_no_private_roots(repo_root))
    return _report(errors)


def validate_plan_record(record: Mapping[str, Any], ref: str = "plan") -> list[str]:
    errors: list[str] = []
    if record.get("runtime_status") != "runtime_not_implemented":
        errors.append(f"{ref}: runtime_status must be runtime_not_implemented")
    if record.get("source_cache_bridge_status") != "source_cache_bridge_not_implemented":
        errors.append(f"{ref}: source_cache_bridge_status must be source_cache_bridge_not_implemented")
    if record.get("evidence_acceptance_status") != "evidence_acceptance_disabled":
        errors.append(f"{ref}: evidence_acceptance_status must be evidence_acceptance_disabled")
    current_phase = record.get("current_phase")
    if current_phase is None:
        current_phase = _get_nested(record, ("rollout_phases", "current_phase"))
    if current_phase != "phase_0_planning_only":
        errors.append(f"{ref}: current_phase must be phase_0_planning_only")

    truth = _extract_truth_boundary(record)
    errors.extend(_require_false_map(ref, truth, TRUTH_FALSE_FIELDS, "truth_boundary"))
    if truth.get("human_review_required_for_downstream_use") is not True:
        errors.append(f"{ref}: truth_boundary.human_review_required_for_downstream_use must be true")
    product = record.get("product_boundary", {})
    errors.extend(_require_false_map(ref, product, PRODUCT_FALSE_FIELDS, "product_boundary"))

    review = record.get("review_gates", {})
    if review:
        for key in sorted(REVIEW_TRUE_FIELDS):
            if review.get(key) is not True:
                errors.append(f"{ref}: review_gates.{key} must be true")
        for key in sorted(REVIEW_FALSE_FIELDS):
            if review.get(key) is not False:
                errors.append(f"{ref}: review_gates.{key} must be false")

    append = record.get("append_semantics")
    if append is not None:
        errors.extend(validate_append_policy(append, f"{ref}: append_semantics"))

    bridge_requirements = record.get("bridge_requirements")
    if bridge_requirements is not None:
        errors.extend(_validate_bridge_requirements(bridge_requirements, f"{ref}: bridge_requirements"))

    for key in ("allowed_outputs", "forbidden_outputs", "forbidden_inputs"):
        value = record.get(key)
        if value is not None and not isinstance(value, list):
            errors.append(f"{ref}: {key} must be a list")
    return errors


def validate_append_policy(policy: Mapping[str, Any], ref: str = "append_policy") -> list[str]:
    errors: list[str] = []
    for key in sorted(APPEND_TRUE_FIELDS):
        if policy.get(key) is not True:
            errors.append(f"{ref}: {key} must be true")
    for key in sorted(APPEND_FALSE_FIELDS):
        if policy.get(key) is not False:
            errors.append(f"{ref}: {key} must be false")
    return errors


def validate_bridge_plan(plan: Mapping[str, Any], ref: str = "bridge_plan") -> list[str]:
    errors: list[str] = []
    if plan.get("bridge_status") != "source_cache_bridge_not_implemented":
        errors.append(f"{ref}: bridge_status must be source_cache_bridge_not_implemented")
    if plan.get("current_phase") != "bridge_phase_0_planning_only":
        errors.append(f"{ref}: current_phase must be bridge_phase_0_planning_only")
    phases = plan.get("bridge_phases", [])
    if not isinstance(phases, list):
        errors.append(f"{ref}: bridge_phases must be a list")
    else:
        phase_ids = {phase.get("phase_id") for phase in phases if isinstance(phase, Mapping)}
        missing = sorted(REQUIRED_FUTURE_BRIDGE_PHASES - phase_ids)
        if missing:
            errors.append(f"{ref}: bridge_phases missing {missing}")
        for phase in phases:
            if not isinstance(phase, Mapping):
                continue
            if phase.get("review_required_before_bridge") is not True:
                errors.append(f"{ref}: {phase.get('phase_id')} review_required_before_bridge must be true")
            if phase.get("runtime_implemented") is not False:
                errors.append(f"{ref}: {phase.get('phase_id')} runtime_implemented must be false")
    errors.extend(_validate_bridge_requirements(plan, ref))
    missing_conversions = sorted(REQUIRED_FORBIDDEN_CONVERSIONS - set(plan.get("forbidden_conversions", [])))
    if missing_conversions:
        errors.append(f"{ref}: forbidden_conversions missing {missing_conversions}")
    return errors


def output_path_allowed(path: Path, repo_root: Path = REPO_ROOT) -> bool:
    resolved = path.resolve(strict=False)
    root = repo_root.resolve(strict=False)
    try:
        rel = resolved.relative_to(root).as_posix()
    except ValueError:
        return True
    forbidden_prefixes = (
        "site/dist/",
        "runtime/",
        "contracts/",
        "native/",
        "snapshots/",
        "control/inventory/publication/",
        ".git/",
        ".aide.local/",
        ".local/",
        ".cache/",
    )
    if any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in forbidden_prefixes):
        return False
    if "master-index" in rel or "master_index" in rel:
        return False
    if rel.startswith("control/audits/") and "/generated/evidence_ledger/" in rel:
        return True
    return False


def _validate_runtime_policy(policy: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    if policy.get("current_plan_status") != "planning_only":
        errors.append(f"{ref}: current_plan_status must be planning_only")
    if set(policy.get("current_runtime_statuses", [])) != CURRENT_RUNTIME_STATUSES:
        errors.append(f"{ref}: current_runtime_statuses must be {sorted(CURRENT_RUNTIME_STATUSES)}")
    errors.extend(_require_values(ref, "allowed_record_statuses", policy, REQUIRED_RECORD_STATUSES))
    errors.extend(_require_values(ref, "allowed_record_types", policy, REQUIRED_RECORD_TYPES))
    errors.extend(_require_false_map(ref, policy.get("truth_boundary", {}), TRUTH_FALSE_FIELDS, "truth_boundary"))
    if _get_nested(policy, ("truth_boundary", "human_review_required_for_downstream_use")) is not True:
        errors.append(f"{ref}: truth_boundary.human_review_required_for_downstream_use must be true")
    errors.extend(_require_false_map(ref, policy.get("product_boundary", {}), PRODUCT_FALSE_FIELDS, "product_boundary"))
    return errors


def _validate_path_policy(policy: Mapping[str, Any], repo_root: Path, ref: str) -> list[str]:
    errors: list[str] = []
    if policy.get("task_creates_future_private_roots") is not False:
        errors.append(f"{ref}: task_creates_future_private_roots must be false")
    errors.extend(_require_values(ref, "allowed_future_roots", policy, REQUIRED_ALLOWED_FUTURE_ROOTS))
    missing_forbidden = sorted(REQUIRED_FORBIDDEN_ROOT_HINTS - set(policy.get("forbidden_roots", [])))
    if missing_forbidden:
        errors.append(f"{ref}: forbidden_roots missing {missing_forbidden}")
    for root in policy.get("allowed_future_roots", []):
        if _looks_like_private_path(str(root)) and str(root) not in REQUIRED_ALLOWED_FUTURE_ROOTS:
            errors.append(f"{ref}: allowed_future_roots contains private path outside documented future roots: {root}")
    for candidate in (
        repo_root / "control/audits/track-b-14-local-evidence-ledger-runtime-planning-v0/generated/evidence_ledger/example.json",
        repo_root.parent / "__eureka_evidence_ledger_temp" / "example.json",
    ):
        if not output_path_allowed(candidate, repo_root):
            errors.append(f"{ref}: allowed output root rejected: {candidate}")
    for candidate in (
        repo_root / "site/dist/evidence.json",
        repo_root / "runtime/evidence.json",
        repo_root / "contracts/evidence.json",
        repo_root / ".aide.local/eureka/evidence_ledger/evidence.json",
    ):
        if output_path_allowed(candidate, repo_root):
            errors.append(f"{ref}: forbidden output root accepted: {candidate}")
    return errors


def _validate_record_policy(policy: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    errors.extend(_require_values(ref, "allowed_record_statuses", policy, REQUIRED_RECORD_STATUSES))
    errors.extend(_require_values(ref, "allowed_record_types", policy, REQUIRED_RECORD_TYPES))
    current_statuses = set(policy.get("current_allowed_record_statuses", []))
    forbidden_current = current_statuses & {"accepted_public_future", "rejected_future"}
    if forbidden_current:
        errors.append(f"{ref}: future statuses cannot be current: {sorted(forbidden_current)}")
    errors.extend(_require_false_map(ref, policy.get("truth_boundary", {}), TRUTH_FALSE_FIELDS, "truth_boundary"))
    if _get_nested(policy, ("truth_boundary", "human_review_required_for_downstream_use")) is not True:
        errors.append(f"{ref}: truth_boundary.human_review_required_for_downstream_use must be true")
    return errors


def _validate_review_policy(policy: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    for key in sorted(REVIEW_TRUE_FIELDS):
        if policy.get(key) is not True:
            errors.append(f"{ref}: {key} must be true")
    for key in sorted(REVIEW_FALSE_FIELDS):
        if policy.get(key) is not False:
            errors.append(f"{ref}: {key} must be false")
    return errors


def _validate_bridge_requirements(mapping: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    for key in ("review_required_before_bridge", "conflict_preservation_required", "no_truth_conversion", "no_master_index_mutation"):
        if mapping.get(key) is not True:
            errors.append(f"{ref}: {key} must be true")
    for key in ("automatic_bridge_runtime_allowed", "automatic_evidence_acceptance_allowed", "automatic_public_index_use_allowed"):
        if key in mapping and mapping.get(key) is not False:
            errors.append(f"{ref}: {key} must be false")
    return errors


def _validate_rollout_plan(plan: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    if plan.get("current_phase") != "phase_0_planning_only":
        errors.append(f"{ref}: current_phase must be phase_0_planning_only")
    phases = plan.get("phases", [])
    if not isinstance(phases, list):
        return [f"{ref}: phases must be a list"]
    phase_ids = {phase.get("phase_id") for phase in phases if isinstance(phase, Mapping)}
    missing = sorted(REQUIRED_ROLLOUT_PHASES - phase_ids)
    if missing:
        errors.append(f"{ref}: phases missing {missing}")
    current = [phase for phase in phases if isinstance(phase, Mapping) and phase.get("phase_id") == "phase_0_planning_only"]
    if not current:
        return errors
    if current[0].get("phase_status") != "current":
        errors.append(f"{ref}: phase_0_planning_only must be current")
    errors.extend(_require_false_map(ref, current[0].get("product_boundary", {}), {
        "implemented_evidence_ledger_runtime",
        "implemented_source_cache_bridge",
        "created_local_private_state",
        "enabled_network_access",
        "enabled_live_probes",
        "enabled_source_sync",
        "enabled_source_connectors",
        "enabled_downloads",
        "enabled_uploads",
        "enabled_telemetry",
        "mutated_master_index",
    }, "phase_0.product_boundary"))
    return errors


def _validate_audit_report(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    ref = "control/audits/track-b-14-local-evidence-ledger-runtime-planning-v0/track_b_14_report.json"
    if report.get("current_phase") != "phase_0_planning_only":
        errors.append(f"{ref}: current_phase must be phase_0_planning_only")
    runtime_scope = report.get("runtime_scope", {})
    for key in ("implemented_evidence_ledger_runtime", "implemented_source_cache_bridge", "created_local_evidence_ledger_state", "writes_evidence_records"):
        if runtime_scope.get(key) is not False:
            errors.append(f"{ref}: runtime_scope.{key} must be false")
    if runtime_scope.get("writes_no_files_by_default") is not True:
        errors.append(f"{ref}: runtime_scope.writes_no_files_by_default must be true")
    errors.extend(_require_false_map(ref, report.get("truth_boundary", {}), {
        "evidence_record_is_public_truth",
        "evidence_record_is_accepted_evidence",
        "evidence_record_can_mutate_master_index",
    }, "truth_boundary"))
    if _get_nested(report, ("truth_boundary", "human_review_required_for_downstream_use")) is not True:
        errors.append(f"{ref}: truth_boundary.human_review_required_for_downstream_use must be true")
    errors.extend(_require_false_map(ref, report.get("product_boundary", {}), PRODUCT_FALSE_FIELDS, "product_boundary"))
    return errors


def _validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    required_phrases = {
        "docs/reference/LOCAL_EVIDENCE_LEDGER_RUNTIME_PLAN.md": [
            "runtime_not_implemented",
            "source_cache_bridge_not_implemented",
            "evidence_acceptance_disabled",
            "B-14 defines intent only",
        ],
        "docs/architecture/LOCAL_EVIDENCE_LEDGER_MODEL.md": [
            "sits after source cache planning",
            "before candidate promotion",
            "B-14 only authorizes phase 0",
        ],
        "docs/operations/LOCAL_EVIDENCE_LEDGER_APPROVAL_GATES.md": [
            "Before Source-Cache Bridge Runtime",
            "Always Forbidden Now",
            "automatic master-index mutation",
        ],
        "docs/operations/LOCAL_EVIDENCE_LEDGER_PRIVACY_RISK_POLICY.md": [
            "not a telemetry feature",
            "Future local evidence-ledger roots are documented for planning only",
            "Evidence candidates may become reviewed evidence only",
        ],
        "docs/operations/SOURCE_CACHE_TO_EVIDENCE_LEDGER_BRIDGE_PLAN.md": [
            "Bridge runtime: not implemented",
            "Forbidden Conversions",
            "The bridge cannot promote a candidate",
        ],
    }
    for rel, phrases in required_phrases.items():
        text = (repo_root / rel).read_text(encoding="utf-8")
        folded = text.casefold()
        for phrase in phrases:
            if phrase.casefold() not in folded:
                errors.append(f"{rel}: missing phrase {phrase}")
    return errors


def _validate_no_private_roots(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for rel in PRIVATE_ROOTS:
        if (repo_root / rel).exists():
            errors.append(f"local private evidence-ledger root must not exist: {rel.as_posix()}")
    return errors


def _scan_payload_for_forbidden_content(payload: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    text = json.dumps(payload, sort_keys=True)
    for pattern in FORBIDDEN_CLAIM_PATTERNS:
        if pattern.search(text):
            errors.append(f"{ref}: forbidden claim matched {pattern.pattern}")
    if SECRET_PATTERN.search(text):
        errors.append(f"{ref}: credential/API-key shaped text is forbidden")
    private_paths = sorted(set(PRIVATE_PATH_PATTERN.findall(text)))
    if private_paths:
        errors.append(f"{ref}: private path outside documented future roots: {private_paths[0]}")
    return errors


def _extract_truth_boundary(record: Mapping[str, Any]) -> Mapping[str, Any]:
    truth = record.get("truth_boundary")
    if truth is None:
        truth = _get_nested(record, ("evidence_record_model", "truth_boundary"))
    return truth if isinstance(truth, Mapping) else {}


def _require_values(ref: str, key: str, policy: Mapping[str, Any], expected: set[str]) -> list[str]:
    actual = set(policy.get(key, []))
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    errors: list[str] = []
    if missing:
        errors.append(f"{ref}: {key} missing {missing}")
    if extra:
        errors.append(f"{ref}: {key} has unexpected {extra}")
    return errors


def _require_false_map(ref: str, mapping: Any, fields: set[str], name: str) -> list[str]:
    if not isinstance(mapping, Mapping):
        return [f"{ref}: {name} must be an object"]
    return [f"{ref}: {name}.{field} must be false" for field in sorted(fields) if mapping.get(field) is not False]


def _get_nested(mapping: Mapping[str, Any], keys: Sequence[str]) -> Any:
    value: Any = mapping
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def _looks_like_private_path(text: str) -> bool:
    return bool(PRIVATE_PATH_PATTERN.search(text))


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _report(errors: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "local_evidence_ledger_runtime_plan_validation.v0",
        "status": "valid" if not errors else "invalid",
        "errors": sorted(dict.fromkeys(errors)),
        "validated_examples": len(EXAMPLE_FILES),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_local_evidence_ledger_runtime_plan()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"status: {report['status']}")
        print(f"validated_examples: {report['validated_examples']}")
        if report["errors"]:
            print("errors:")
            for error in report["errors"]:
                print(f"  - {error}")
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
