"""Blocked action report builders for disabled J0 action families."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.actions.action_policy import (
    action_product_boundary,
    action_truth_boundary,
    normalize_action_family,
    stable_id,
    subject_ref,
)


SCHEMA_VERSION = "blocked_action_report.v0"
SAFE_ALTERNATIVES = {
    "download": ["view", "inspect", "cite", "acquisition_manifest", "export"],
    "mirror": ["preserve_manifest", "cite", "export"],
    "install": ["inspect", "cite", "acquisition_manifest"],
    "execute": ["inspect", "compare", "blocked_action"],
    "emulate": ["inspect", "compare", "blocked_action"],
    "submit": ["export", "cite"],
    "import": ["export", "inspect"],
}


def build_blocked_action_report(action_family: str, subject: Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    family = normalize_action_family(action_family).removesuffix("_future")
    subject = subject or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "blocked_action_report_id": stable_id("blocked_action_report", {"family": family, "subject": subject_ref(subject)}),
        "blocked_action_family": family,
        "subject_ref": subject_ref(subject),
        "blocked_reason": f"{family} is a future risky action and is disabled in J0",
        "required_policy": [
            "rights_review",
            "risk_review",
            "malware_policy",
            "user_confirmation",
            "action_audit",
            "rollback_or_incident_policy",
            "no_auto_run_policy",
        ],
        "required_review": True,
        "future_gate": "J1_or_later_risky_action_review",
        "safe_alternative_actions": SAFE_ALTERNATIVES.get(family, ["view", "inspect", "cite"]),
        "limitations": ["Report explains why the action is blocked; it does not perform the blocked action."],
        "truth_boundary": action_truth_boundary(),
        "product_boundary": action_product_boundary(),
    }


def build_download_blocked_report(subject: Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_blocked_action_report("download", subject, policy)


def build_install_blocked_report(subject: Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_blocked_action_report("install", subject, policy)


def build_execute_blocked_report(subject: Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_blocked_action_report("execute", subject, policy)


def build_emulate_blocked_report(subject: Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_blocked_action_report("emulate", subject, policy)


def validate_blocked_action_report(report: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "blocked_action_report_id",
        "blocked_action_family",
        "subject_ref",
        "blocked_reason",
        "required_policy",
        "required_review",
        "future_gate",
        "safe_alternative_actions",
        "limitations",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in report:
            errors.append(f"missing blocked action field: {field}")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if not report.get("blocked_reason"):
        errors.append("blocked_reason is required")
    if not report.get("safe_alternative_actions"):
        errors.append("safe_alternative_actions is required")
    if report.get("required_review") is not True:
        errors.append("required_review must be true")
    from runtime.actions.action_policy import detect_action_boundary_violations

    errors.extend(detect_action_boundary_violations(report))
    return sorted(dict.fromkeys(errors))
