"""Readiness builders for hosted-wrapper rehearsal evidence."""

from __future__ import annotations


def build_hosted_wrapper_rehearsal(inputs: dict | None, policy: dict | None = None) -> dict:
    payload = dict(inputs or {})
    payload.setdefault("schema_version", "hosted_wrapper_rehearsal.v0")
    payload.setdefault("rehearsal_id", "runtime_hosted_wrapper_rehearsal.v0")
    payload.setdefault("rehearsal_status", "local_fixture_rehearsal")
    payload.setdefault(
        "rehearsal_scope",
        {
            "local_fixture_only": True,
            "deployment_performed": False,
            "provider_api_called": False,
            "public_alpha_live_claimed": False,
            "production_claimed": False,
        },
    )
    payload.setdefault("truth_boundary", {"public_alpha_live_claimed": False, "production_claimed": False})
    payload.setdefault("product_boundary", {"enabled_hosting": False, "mutated_site_dist": False})
    return payload


def build_hosting_readiness_report(inputs: dict | None, policy: dict | None = None) -> dict:
    return {
        "schema_version": "hosting_readiness_report.v0",
        "readiness_report_id": "runtime_hosting_readiness_report.v0",
        "readiness_status": "ready_for_rehearsal_future",
        "launch_evidence_status": "operator_gated_not_collected",
        "truth_boundary": {"public_alpha_live_claimed": False, "production_claimed": False},
        "product_boundary": {"enabled_hosting": False, "mutated_site_dist": False},
    }


def build_public_launch_readiness_audit(inputs: dict | None, policy: dict | None = None) -> dict:
    payload = dict(inputs or {})
    payload.setdefault("schema_version", "public_launch_readiness_audit.v0")
    payload.setdefault("readiness_audit_id", "runtime_public_launch_readiness_audit.v0")
    payload.setdefault("readiness_status", "ready_for_local_rehearsal")
    payload.setdefault("operator_signoff_required", True)
    payload.setdefault("missing_evidence", ["operator signoff", "public endpoint evidence"])
    payload.setdefault("truth_boundary", {"public_alpha_live_claimed": False, "production_claimed": False})
    payload.setdefault("product_boundary", {"enabled_hosting": False, "mutated_site_dist": False})
    return payload


def validate_public_launch_readiness_audit(audit: dict, policy: dict | None = None) -> dict:
    errors: list[str] = []
    if audit.get("readiness_status") == "ready_for_public_alpha_future":
        if audit.get("operator_signoff_required") is True or audit.get("missing_evidence"):
            errors.append("ready_for_public_alpha_future requires completed evidence and signoff")
    if audit.get("truth_boundary", {}).get("public_alpha_live_claimed") is True:
        errors.append("public alpha live claim is not allowed")
    if audit.get("product_boundary", {}).get("enabled_hosting") is True:
        errors.append("enabled_hosting must remain false")
    return {"schema_version": "public_launch_readiness_audit_validation.v0", "status": "fail" if errors else "pass", "errors": errors}
