"""Loader, validation, and projection helpers for reviewed artifact records."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from runtime.surface import SurfaceKernel, SurfaceRequest


def batch_root() -> Path:
    return Path(__file__).resolve().parent


def load_reviewed_artifact_records(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "reviewed_artifact_records.json")


def load_verified_artifacts(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "verified_artifacts.json")


def load_non_promoted_artifact_leads(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "non_promoted_artifact_leads.json")


def load_artifact_record_counts(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "artifact_record_counts.json")


def load_query_coverage(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "query_coverage.json")


def load_source_reference_index(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "source_reference_index.json")


def read_batch_text(name: str, root: Path | None = None) -> str:
    return ((root or batch_root()) / name).read_text(encoding="utf-8")


def reviewed_artifact_record_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("reviewed_artifact_records") or [] if isinstance(item, Mapping))


def non_promoted_lead_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("non_promoted_artifact_leads") or [] if isinstance(item, Mapping))


def query_coverage_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("query_coverage") or [] if isinstance(item, Mapping))


def source_reference_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("source_references") or [] if isinstance(item, Mapping))


def validate_reviewed_artifact_records(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    records = reviewed_artifact_record_records(payload)
    if len(records) != 2:
        errors.append("must contain 2 reviewed artifact records")
    ids = [record.get("reviewed_artifact_record_id") for record in records]
    if len(ids) != len(set(ids)):
        errors.append("reviewed artifact record IDs must be unique")
    for record in records:
        record_id = str(record.get("reviewed_artifact_record_id") or "<missing>")
        if record.get("artifact_claim_status") != "reviewed_artifact_record":
            errors.append(f"{record_id} must be reviewed_artifact_record")
        if record.get("verified_artifact") is not False:
            errors.append(f"{record_id} must not be verified artifact")
        if record.get("artifact_level") != "artifact_level_3_artifact_identity_evidence":
            errors.append(f"{record_id} must be level 3")
        if not record.get("source_refs") or not record.get("evidence_refs"):
            errors.append(f"{record_id} must include source and evidence refs")
        for flag in ("rights_clearance_claimed", "malware_safety_claimed", "download_offered", "reviewed_index_mutated", "public_index_mutated", "master_index_mutated"):
            if record.get(flag) is not False:
                errors.append(f"{record_id} must keep {flag}=false")
    return tuple(errors)


def validate_verified_artifacts(payload: Mapping[str, Any]) -> tuple[str, ...]:
    if payload.get("verified_artifacts") != [] or int(payload.get("verified_artifact_count", -1)) != 0:
        return ("verified artifacts must remain empty",)
    return ()


def validate_non_promoted_artifact_leads(payload: Mapping[str, Any]) -> tuple[str, ...]:
    records = non_promoted_lead_records(payload)
    errors: list[str] = []
    if len(records) != 8:
        errors.append("must contain 8 non-promoted artifact leads")
    for record in records:
        if record.get("decision") == "promote":
            errors.append(f"{record.get('artifact_observation_id')} must not be promoted")
        if record.get("status") not in {"need", "near_miss", "unavailable"}:
            errors.append(f"{record.get('artifact_observation_id')} has unsupported status")
    return tuple(errors)


def validate_artifact_record_counts(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    expected = {
        "reviewed_artifact_record_count": 2,
        "verified_artifact_count": 0,
        "non_promoted_artifact_lead_count": 8,
        "need_count": 5,
        "near_miss_count": 3,
        "blocked_for_user_details_count": 1,
    }
    for key, value in expected.items():
        if int(payload.get(key, -1)) != value:
            errors.append(f"{key} must be {value}")
    if payload.get("public_alpha_artifact_gate") != "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS":
        errors.append("artifact gate must remain failed")
    return tuple(errors)


def validate_query_coverage(payload: Mapping[str, Any]) -> tuple[str, ...]:
    records = query_coverage_records(payload)
    errors: list[str] = []
    if len(records) != 6:
        errors.append("query coverage must cover six hard queries")
    if payload.get("hard_query_reviewed_artifact_coverage") != "2/6":
        errors.append("reviewed artifact coverage must be 2/6")
    if payload.get("hard_query_verified_artifact_coverage") != "0/6":
        errors.append("verified artifact coverage must be 0/6")
    for record in records:
        if record.get("public_alpha_ready") is not False:
            errors.append(f"{record.get('query_id')} must not be alpha ready")
    return tuple(errors)


def validate_source_reference_index(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    records = source_reference_records(payload)
    if len(records) != 3:
        errors.append("source index must contain 3 source references")
    for record in records:
        source_id = str(record.get("source_id") or "<missing>")
        for flag in ("runtime_source_call_performed", "download_performed", "file_fetch_performed", "wayback_replay_performed"):
            if record.get(flag) is not False:
                errors.append(f"{source_id} must keep {flag}=false")
    return tuple(errors)


def project_reviewed_artifact_record(record: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="object",
            entity_id=str(record.get("reviewed_artifact_record_id") or "reviewed-artifact-record"),
            payload=_reviewed_artifact_view_payload(record),
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="reviewed-artifact-records-batch-00",
        )
    )


def project_non_promoted_artifact_lead(lead: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="object",
            entity_id=str(lead.get("artifact_observation_id") or "artifact-lead"),
            payload=_non_promoted_lead_view_payload(lead),
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="reviewed-artifact-records-batch-00",
        )
    )


def _reviewed_artifact_view_payload(record: Mapping[str, Any]) -> dict[str, Any]:
    identity = record.get("artifact_identity") if isinstance(record.get("artifact_identity"), Mapping) else {}
    return {
        "id": str(record.get("reviewed_artifact_record_id") or "reviewed-artifact-record"),
        "title": f"Reviewed artifact record: {identity.get('name', 'artifact')} {identity.get('version', '')}".strip(),
        "summary": str(record.get("public_claim") or ""),
        "status": str(record.get("canonical_status") or "verified"),
        "artifact_claim_status": "reviewed_artifact_record",
        "verified_artifact": False,
        "artifact_level": str(record.get("artifact_level") or ""),
        "source_refs": list(record.get("source_refs") or []),
        "must_not_claim": list(record.get("must_not_claim") or []),
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _non_promoted_lead_view_payload(lead: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": str(lead.get("artifact_observation_id") or "artifact-lead"),
        "title": "Artifact lead requiring review",
        "summary": str(lead.get("reason") or ""),
        "status": str(lead.get("status") or "need"),
        "artifact_claim_status": "artifact_lead",
        "verified_artifact": False,
        "artifact_level": str(lead.get("artifact_level") or ""),
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
