"""Rollback rehearsal report helpers."""

from __future__ import annotations


def build_rollback_rehearsal_report(inputs: dict | None, policy: dict | None = None) -> dict:
    return {
        "schema_version": "rollback_rehearsal_report.v0",
        "rollback_rehearsal_id": "runtime_rollback_rehearsal.v0",
        "status": "documented_not_executed",
        "rollback_steps": (inputs or {}).get("rollback_steps", ["return to local fixture posture"]),
        "deployment_rollback_performed": False,
        "limitations": ["No deployment exists to roll back in E-BUNDLE-02."],
    }


def validate_rollback_rehearsal_report(report: dict, policy: dict | None = None) -> dict:
    errors: list[str] = []
    if report.get("deployment_rollback_performed") is True:
        errors.append("deployment rollback must not be performed by rehearsal")
    if not report.get("rollback_steps"):
        errors.append("rollback steps are required")
    return {"schema_version": "rollback_rehearsal_validation.v0", "status": "fail" if errors else "pass", "errors": errors}
