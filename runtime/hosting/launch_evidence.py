"""Public launch evidence packet helpers."""

from __future__ import annotations


def build_public_launch_evidence_packet(inputs: dict | None, policy: dict | None = None) -> dict:
    payload = dict(inputs or {})
    payload.setdefault("schema_version", "public_launch_evidence.v0")
    payload.setdefault("launch_evidence_id", "runtime_public_launch_evidence.required.v0")
    payload.setdefault("launch_evidence_status", "operator_gated_not_collected")
    payload.setdefault("operator_signoff_required", True)
    payload.setdefault("required_evidence", ["status", "smoke matrix", "blocked requests", "operator signoff"])
    payload.setdefault("truth_boundary", {"public_alpha_live_claimed": False, "production_claimed": False})
    payload.setdefault("product_boundary", {"enabled_hosting": False, "mutated_site_dist": False})
    return payload


def validate_public_launch_evidence_packet(packet: dict, policy: dict | None = None) -> dict:
    errors: list[str] = []
    if packet.get("operator_signoff_required") is not True:
        errors.append("operator signoff must be required")
    if packet.get("launch_evidence_status") in {"collected", "ready_for_launch"}:
        errors.append("launch evidence must remain operator-gated in E-BUNDLE-02")
    if packet.get("truth_boundary", {}).get("production_claimed") is True:
        errors.append("production claim is not allowed")
    return {"schema_version": "public_launch_evidence_validation.v0", "status": "fail" if errors else "pass", "errors": errors}
