"""Blocked request report helpers."""

from __future__ import annotations

TRUTH_BOUNDARY = {
    "hosting_rehearsal_is_launch": False,
    "public_alpha_live_claimed": False,
    "production_claimed": False,
    "operator_signoff_inferred": False,
    "public_index_mutated": False,
    "master_index_mutated": False,
    "rights_clearance_claimed": False,
    "malware_safety_claimed": False,
    "verified_installability_claimed": False,
}
PRODUCT_BOUNDARY = {
    "changed_public_search_behavior": False,
    "enabled_hosting": False,
    "enabled_live_source_fanout": False,
    "enabled_downloads": False,
    "enabled_uploads": False,
    "enabled_accounts": False,
    "enabled_telemetry": False,
    "enabled_public_relay": False,
    "mutated_site_dist": False,
    "mutated_public_index": False,
    "mutated_master_index": False,
}


def build_blocked_request_report(request_kind: str, policy: dict | None = None) -> dict:
    return {
        "schema_version": "public_alpha_blocked_request_report.v0",
        "blocked_request_report_id": f"blocked_request.{request_kind}.runtime.v0",
        "request_kind": request_kind,
        "request_shape": {"path": f"/blocked/{request_kind}", "body_allowed": False},
        "blocked": True,
        "blocked_reason": f"{request_kind} is outside the local rehearsal boundary",
        "policy_ref": "control/inventory/hosting/public_alpha_blocked_request_policy.json",
        "safe_alternative": "Use public-safe local fixture summaries.",
        "limitations": ["Runtime helper builds descriptive reports only."],
        "truth_boundary": dict(TRUTH_BOUNDARY),
        "product_boundary": dict(PRODUCT_BOUNDARY),
    }


def validate_blocked_request_report(report: dict, policy: dict | None = None) -> dict:
    errors: list[str] = []
    if report.get("schema_version") != "public_alpha_blocked_request_report.v0":
        errors.append("schema_version must be public_alpha_blocked_request_report.v0")
    if report.get("blocked") is not True:
        errors.append("blocked must be true")
    for key in ("public_alpha_live_claimed", "production_claimed", "public_index_mutated", "master_index_mutated"):
        if report.get("truth_boundary", {}).get(key) is True:
            errors.append(f"truth_boundary.{key} must be false")
    return {"schema_version": "blocked_request_validation.v0", "status": "fail" if errors else "pass", "errors": errors}
