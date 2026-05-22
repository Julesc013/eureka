#!/usr/bin/env python3
"""Validate Track B local source cache runtime planning artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]

INVENTORY_FILES = [
    "control/inventory/source_cache/local_source_cache_runtime_plan.json",
    "control/inventory/source_cache/local_source_cache_runtime_policy.json",
    "control/inventory/source_cache/local_source_cache_path_policy.json",
    "control/inventory/source_cache/local_source_cache_source_access_policy.json",
    "control/inventory/source_cache/local_source_cache_record_policy.json",
    "control/inventory/source_cache/local_source_cache_review_policy.json",
    "control/inventory/source_cache/local_source_cache_rollout_plan.json",
]
DOC_FILES = [
    "docs/reference/LOCAL_SOURCE_CACHE_RUNTIME_PLAN.md",
    "docs/architecture/LOCAL_SOURCE_CACHE_MODEL.md",
    "docs/operations/LOCAL_SOURCE_CACHE_APPROVAL_GATES.md",
    "docs/operations/LOCAL_SOURCE_CACHE_PRIVACY_RISK_POLICY.md",
]
EXAMPLE_FILES = [
    "examples/source_cache_plans/minimal_local_source_cache_plan_v0.json",
    "examples/source_cache_plans/fixture_only_source_cache_plan_v0.json",
    "examples/source_cache_plans/approved_metadata_probe_future_plan_v0.json",
    "examples/source_cache_plans/policy_blocked_source_cache_plan_v0.json",
]
AUDIT_FILES = [
    "control/audits/track-b-13-local-source-cache-runtime-planning-v0/README.md",
    "control/audits/track-b-13-local-source-cache-runtime-planning-v0/track_b_13_report.json",
    "control/audits/track-b-13-local-source-cache-runtime-planning-v0/source_cache_runtime_readiness.md",
    "control/audits/track-b-13-local-source-cache-runtime-planning-v0/validation.md",
]

CURRENT_ALLOWED_ACCESS_MODES = {
    "committed_fixture_only",
    "repo_local_only",
    "manual_human_only",
    "no_autonomous_access",
}
ALL_ACCESS_MODES = CURRENT_ALLOWED_ACCESS_MODES | {
    "approved_metadata_probe_future",
    "approved_api_future",
    "approved_static_dump_future",
    "approved_common_crawl_or_archive_future",
    "permission_needed",
    "robots_blocked",
    "terms_blocked",
    "restricted_demand_signal_only",
}
FUTURE_ACCESS_MODES = ALL_ACCESS_MODES - CURRENT_ALLOWED_ACCESS_MODES
REQUIRED_FUTURE_GATES = {
    "explicit_source_policy_approval",
    "operator_approval",
    "user_agent_contact_decision",
    "rate_limit",
    "timeout",
    "retry_policy",
    "cache_ttl",
    "kill_switch",
    "terms_robots_review",
    "privacy_risk_review",
    "human_review_before_downstream_evidence_use",
}
FORBIDDEN_ACCESS_NAMES = {
    "google_result_page_scraping",
    "unapproved_forum_scraping",
    "bulk_reddit_ingestion",
    "arbitrary_url_fetch",
    "credentialed_access_without_approval",
    "captcha_bypass",
    "paywall_bypass",
    "access_control_bypass",
    "binary_download",
    "installer_execution",
}
TRUTH_FALSE_FIELDS = {
    "source_cache_record_is_public_truth",
    "source_cache_record_is_accepted_evidence",
    "source_cache_record_can_mutate_master_index",
    "source_cache_record_can_claim_rights_clearance",
    "source_cache_record_can_claim_malware_safety",
    "source_cache_record_can_claim_verified_installability",
    "source_cache_record_can_claim_exhaustive_global_search",
    "source_cache_record_can_claim_production_readiness",
}
PRODUCT_FALSE_FIELDS = {
    "implemented_source_cache_runtime",
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
    "review_required_before_evidence_ledger_bridge",
    "review_required_before_candidate_store_use",
    "review_required_before_public_index_use",
    "review_required_before_pack_export",
    "review_required_before_source_policy_change",
    "review_required_before_live_probe",
    "review_required_before_connector_runtime",
}
REVIEW_FALSE_FIELDS = {
    "automatic_evidence_acceptance_allowed",
    "automatic_public_index_use_allowed",
    "automatic_master_index_mutation_allowed",
    "automatic_connector_enable_allowed",
}
REQUIRED_RECORD_STATUSES = {
    "example_only",
    "planned",
    "fixture_only",
    "recorded_local",
    "normalized",
    "source_observation",
    "candidate_source_record",
    "needs_review",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "stale",
    "superseded",
    "deferred",
    "future_live_probe_result",
    "accepted_public_future",
}
REQUIRED_RECORD_TYPES = {
    "source_metadata",
    "source_locator",
    "source_policy_record",
    "source_health_record",
    "source_coverage_record",
    "source_lead_record",
    "connector_fixture_record",
    "approved_metadata_probe_result_future",
    "approved_api_result_future",
    "static_dump_record_future",
}
REQUIRED_ALLOWED_FUTURE_ROOTS = {
    ".aide.local/eureka/source_cache/",
    ".local/eureka/source_cache/",
    ".cache/eureka/source_cache/",
    "control/audits/**/generated/source_cache/",
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
    Path(".aide.local/eureka/source_cache"),
    Path(".local/eureka/source_cache"),
    Path(".cache/eureka/source_cache"),
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
    )
]
SECRET_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|secret|password|token|credential)\s*[:=]\s*[A-Za-z0-9_\-]{8,}"
)
PRIVATE_PATH_PATTERN = re.compile(
    r"(?i)([A-Za-z]:\\(?:Users|Documents and Settings|Windows|Temp)\\|/Users/[^/\s]+|/home/[^/\s]+|\\\\[^\\\s]+\\)"
)


def validate_local_source_cache_runtime_plan(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required = sorted(INVENTORY_FILES + DOC_FILES + EXAMPLE_FILES + AUDIT_FILES)
    for rel in required:
        if not (repo_root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    if errors:
        return _report(errors)

    payloads = {rel: _read_json(repo_root / rel) for rel in INVENTORY_FILES + EXAMPLE_FILES}
    errors.extend(validate_plan_record(payloads[INVENTORY_FILES[0]], INVENTORY_FILES[0]))
    errors.extend(_validate_runtime_policy(payloads[INVENTORY_FILES[1]], INVENTORY_FILES[1]))
    errors.extend(_validate_path_policy(payloads[INVENTORY_FILES[2]], repo_root, INVENTORY_FILES[2]))
    errors.extend(_validate_source_access_policy(payloads[INVENTORY_FILES[3]], INVENTORY_FILES[3]))
    errors.extend(_validate_record_policy(payloads[INVENTORY_FILES[4]], INVENTORY_FILES[4]))
    errors.extend(_validate_review_policy(payloads[INVENTORY_FILES[5]], INVENTORY_FILES[5]))
    errors.extend(_validate_rollout_plan(payloads[INVENTORY_FILES[6]], INVENTORY_FILES[6]))

    for rel in EXAMPLE_FILES:
        errors.extend(validate_plan_record(payloads[rel], rel))
        errors.extend(_scan_payload_for_forbidden_content(payloads[rel], rel))

    audit_report = _read_json(repo_root / "control/audits/track-b-13-local-source-cache-runtime-planning-v0/track_b_13_report.json")
    errors.extend(_validate_audit_report(audit_report))
    errors.extend(_validate_docs(repo_root))
    errors.extend(_validate_no_private_roots(repo_root))
    return _report(errors)


def validate_plan_record(record: Mapping[str, Any], ref: str = "plan") -> list[str]:
    errors: list[str] = []
    if record.get("runtime_status") != "runtime_not_implemented":
        errors.append(f"{ref}: runtime_status must be runtime_not_implemented")
    if record.get("source_access_status") != "source_access_disabled":
        errors.append(f"{ref}: source_access_status must be source_access_disabled")
    current_phase = record.get("current_phase")
    if current_phase is None:
        current_phase = _get_nested(record, ("rollout_phases", "current_phase"))
    if current_phase != "phase_0_planning_only":
        errors.append(f"{ref}: current_phase must be phase_0_planning_only")

    current_modes = _extract_current_modes(record)
    unknown_modes = current_modes - ALL_ACCESS_MODES - FORBIDDEN_ACCESS_NAMES
    if unknown_modes:
        errors.append(f"{ref}: unknown current source access modes: {sorted(unknown_modes)}")
    future_current = sorted(current_modes & FUTURE_ACCESS_MODES)
    if future_current:
        errors.append(f"{ref}: future source access modes cannot be current: {future_current}")
    forbidden_current = sorted(current_modes & FORBIDDEN_ACCESS_NAMES)
    if forbidden_current:
        errors.append(f"{ref}: forbidden source access modes cannot be current: {forbidden_current}")
    unsupported_current = sorted(current_modes - CURRENT_ALLOWED_ACCESS_MODES - FORBIDDEN_ACCESS_NAMES)
    if unsupported_current:
        errors.append(f"{ref}: current source access modes must be fixture/repo-local/manual/no-autonomous only: {unsupported_current}")

    future_modes = _extract_future_modes(record)
    if future_modes & FUTURE_ACCESS_MODES:
        gates = _extract_future_gates(record)
        missing_gates = sorted(gate for gate in REQUIRED_FUTURE_GATES if gates.get(gate) is not True)
        if missing_gates:
            errors.append(f"{ref}: future source access modes require approval gates: {missing_gates}")

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

    for key in ("allowed_outputs", "forbidden_outputs", "forbidden_inputs"):
        value = record.get(key)
        if value is not None and not isinstance(value, list):
            errors.append(f"{ref}: {key} must be a list")
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
    if rel.startswith("control/audits/") and "/generated/source_cache/" in rel:
        return True
    return False


def _validate_runtime_policy(policy: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    if policy.get("current_plan_status") != "planning_only":
        errors.append(f"{ref}: current_plan_status must be planning_only")
    if policy.get("current_runtime_status") != "runtime_not_implemented":
        errors.append(f"{ref}: current_runtime_status must be runtime_not_implemented")
    if policy.get("current_source_access_status") != "source_access_disabled":
        errors.append(f"{ref}: current_source_access_status must be source_access_disabled")
    errors.extend(_require_values(ref, "allowed_source_access_modes", policy, ALL_ACCESS_MODES))
    current = set(policy.get("allowed_current_source_access_modes", []))
    if current != CURRENT_ALLOWED_ACCESS_MODES:
        errors.append(f"{ref}: allowed_current_source_access_modes must be {sorted(CURRENT_ALLOWED_ACCESS_MODES)}")
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
        repo_root / "control/audits/track-b-13-local-source-cache-runtime-planning-v0/generated/source_cache/example.json",
        repo_root.parent / "__eureka_source_cache_temp" / "example.json",
    ):
        if not output_path_allowed(candidate, repo_root):
            errors.append(f"{ref}: allowed output root rejected: {candidate}")
    for candidate in (
        repo_root / "site/dist/source_cache.json",
        repo_root / "runtime/source_cache.json",
        repo_root / "contracts/source_cache.json",
        repo_root / ".aide.local/eureka/source_cache/source_cache.json",
    ):
        if output_path_allowed(candidate, repo_root):
            errors.append(f"{ref}: forbidden output root accepted: {candidate}")
    return errors


def _validate_source_access_policy(policy: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    if policy.get("current_source_access_status") != "source_access_disabled":
        errors.append(f"{ref}: current_source_access_status must be source_access_disabled")
    errors.extend(_require_values(ref, "source_access_modes", policy, ALL_ACCESS_MODES))
    if set(policy.get("current_allowed_modes", [])) != CURRENT_ALLOWED_ACCESS_MODES:
        errors.append(f"{ref}: current_allowed_modes must be {sorted(CURRENT_ALLOWED_ACCESS_MODES)}")
    missing_forbidden = sorted(FORBIDDEN_ACCESS_NAMES - set(policy.get("explicitly_forbidden_access", [])))
    if missing_forbidden:
        errors.append(f"{ref}: explicitly_forbidden_access missing {missing_forbidden}")
    requirements = policy.get("future_mode_requirements", {})
    if not isinstance(requirements, Mapping):
        return errors + [f"{ref}: future_mode_requirements must be an object"]
    for mode in sorted(FUTURE_ACCESS_MODES & set(requirements)):
        gates = requirements.get(mode, {})
        if not isinstance(gates, Mapping):
            errors.append(f"{ref}: future_mode_requirements.{mode} must be an object")
            continue
        missing = sorted(gate for gate in REQUIRED_FUTURE_GATES if gates.get(gate) is not True)
        if missing:
            errors.append(f"{ref}: {mode} missing required gates {missing}")
    for mode in (
        "approved_metadata_probe_future",
        "approved_api_future",
        "approved_static_dump_future",
        "approved_common_crawl_or_archive_future",
    ):
        if mode not in requirements:
            errors.append(f"{ref}: future_mode_requirements missing {mode}")
    return errors


def _validate_record_policy(policy: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    errors.extend(_require_values(ref, "allowed_record_statuses", policy, REQUIRED_RECORD_STATUSES))
    errors.extend(_require_values(ref, "allowed_record_types", policy, REQUIRED_RECORD_TYPES))
    current_statuses = set(policy.get("current_allowed_record_statuses", []))
    forbidden_current = current_statuses & {"future_live_probe_result", "accepted_public_future"}
    if forbidden_current:
        errors.append(f"{ref}: future/accepted statuses cannot be current: {sorted(forbidden_current)}")
    errors.extend(_require_false_map(ref, policy.get("truth_boundary", {}), TRUTH_FALSE_FIELDS, "truth_boundary"))
    if _get_nested(policy, ("truth_boundary", "human_review_required_for_downstream_use")) is not True:
        errors.append(f"{ref}: truth_boundary.human_review_required_for_downstream_use must be true")
    return errors


def _validate_review_policy(policy: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    for key in sorted(REVIEW_TRUE_FIELDS):
        if policy.get(key) is not True:
            errors.append(f"{ref}: {key} must be true")
    for key in sorted(REVIEW_FALSE_FIELDS | {"automatic_source_sync_allowed"}):
        if policy.get(key) is not False:
            errors.append(f"{ref}: {key} must be false")
    return errors


def _validate_rollout_plan(plan: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    if plan.get("current_phase") != "phase_0_planning_only":
        errors.append(f"{ref}: current_phase must be phase_0_planning_only")
    phases = plan.get("phases", [])
    if not isinstance(phases, list):
        return [f"{ref}: phases must be a list"]
    required = {
        "phase_0_planning_only",
        "phase_1_fixture_only_runtime_future",
        "phase_2_source_policy_evaluator_future",
        "phase_3_approved_metadata_probe_future",
        "phase_4_source_cache_to_evidence_bridge_future",
        "phase_5_reviewed_public_index_bridge_future",
    }
    phase_ids = {phase.get("phase_id") for phase in phases if isinstance(phase, Mapping)}
    missing = sorted(required - phase_ids)
    if missing:
        errors.append(f"{ref}: phases missing {missing}")
    current = [phase for phase in phases if isinstance(phase, Mapping) and phase.get("phase_id") == "phase_0_planning_only"]
    if not current:
        return errors
    if current[0].get("phase_status") != "current":
        errors.append(f"{ref}: phase_0_planning_only must be current")
    errors.extend(_require_false_map(ref, current[0].get("product_boundary", {}), {
        "implemented_source_cache_runtime",
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
    ref = "control/audits/track-b-13-local-source-cache-runtime-planning-v0/track_b_13_report.json"
    if report.get("current_phase") != "phase_0_planning_only":
        errors.append(f"{ref}: current_phase must be phase_0_planning_only")
    runtime_scope = report.get("runtime_scope", {})
    for key in ("implemented_source_cache_runtime", "created_local_source_cache_state", "source_access_enabled"):
        if runtime_scope.get(key) is not False:
            errors.append(f"{ref}: runtime_scope.{key} must be false")
    if runtime_scope.get("writes_no_files_by_default") is not True:
        errors.append(f"{ref}: runtime_scope.writes_no_files_by_default must be true")
    errors.extend(_require_false_map(ref, report.get("truth_boundary", {}), {
        "source_cache_record_is_public_truth",
        "source_cache_record_is_accepted_evidence",
        "source_cache_record_can_mutate_master_index",
    }, "truth_boundary"))
    if _get_nested(report, ("truth_boundary", "human_review_required_for_downstream_use")) is not True:
        errors.append(f"{ref}: truth_boundary.human_review_required_for_downstream_use must be true")
    errors.extend(_require_false_map(ref, report.get("product_boundary", {}), PRODUCT_FALSE_FIELDS, "product_boundary"))
    return errors


def _validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    required_phrases = {
        "docs/reference/LOCAL_SOURCE_CACHE_RUNTIME_PLAN.md": [
            "runtime_not_implemented",
            "source_access_disabled",
            "Source cache records are observations or drafts",
            "Future modes require explicit source policy approval",
            "B-13 documents future roots but does not create them",
        ],
        "docs/architecture/LOCAL_SOURCE_CACHE_MODEL.md": [
            "sits after candidate discovery",
            "before evidence ledger conversion",
            "B-13 only authorizes phase 0",
        ],
        "docs/operations/LOCAL_SOURCE_CACHE_APPROVAL_GATES.md": [
            "Before Metadata Probes",
            "Always Forbidden Now",
            "automatic master-index mutation",
        ],
        "docs/operations/LOCAL_SOURCE_CACHE_PRIVACY_RISK_POLICY.md": [
            "not a telemetry feature",
            "Future local source-cache roots are documented for planning only",
            "Source-cache output may become an evidence candidate only",
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
            errors.append(f"local private source-cache root must not exist: {rel.as_posix()}")
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


def _extract_current_modes(record: Mapping[str, Any]) -> set[str]:
    modes = record.get("current_source_access_modes")
    if modes is None:
        modes = _get_nested(record, ("source_cache_scope", "current_allowed_access_modes"))
    if modes is None:
        modes = _get_nested(record, ("source_access_modes", "current_source_access_modes"))
    return set(modes or [])


def _extract_future_modes(record: Mapping[str, Any]) -> set[str]:
    modes = record.get("future_source_access_modes")
    if modes is None:
        modes = _get_nested(record, ("source_cache_scope", "future_deferred_access_modes"))
    if modes is None:
        modes = _get_nested(record, ("source_access_modes", "future_source_access_modes"))
    return set(modes or [])


def _extract_future_gates(record: Mapping[str, Any]) -> Mapping[str, Any]:
    gates = record.get("future_approval_gates")
    if gates is None:
        gates = _get_nested(record, ("source_access_modes", "future_approval_gates"))
    return gates if isinstance(gates, Mapping) else {}


def _extract_truth_boundary(record: Mapping[str, Any]) -> Mapping[str, Any]:
    truth = record.get("truth_boundary")
    if truth is None:
        truth = _get_nested(record, ("source_cache_record_model", "truth_boundary"))
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
        "schema_version": "local_source_cache_runtime_plan_validation.v0",
        "status": "valid" if not errors else "invalid",
        "errors": sorted(dict.fromkeys(errors)),
        "validated_examples": len(EXAMPLE_FILES),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_local_source_cache_runtime_plan()
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
