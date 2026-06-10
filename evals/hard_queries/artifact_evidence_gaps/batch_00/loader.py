"""Loader and projection helpers for artifact evidence gap batch zero."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries.reviewed_artifact_corpus.batch_01 import BASELINE_PROFILES
from runtime.surface import SurfaceKernel, SurfaceRequest


PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
FORBIDDEN_PUBLIC_ACTIONS = frozenset(
    {
        "review_candidate",
        "promote",
        "reject",
        "download",
        "install",
        "rebuild_index",
        "crawl_source",
        "arbitrary_live_lookup",
    }
)


def batch_root() -> Path:
    return Path(__file__).resolve().parent


def load_evidence_gap_triage(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "evidence_gap_triage.json")


def load_verification_gap_triage(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "verification_gap_triage.json")


def load_source_target_plan(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "source_target_plan.json")


def load_public_alpha_artifact_gate(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "public_alpha_artifact_gate.json")


def load_surface_projection_fixtures(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "surface_projection_fixtures.json")


def load_renderer_expected_outputs(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "renderer_expected_outputs.json")


def read_batch_text(name: str, root: Path | None = None) -> str:
    return ((root or batch_root()) / name).read_text(encoding="utf-8")


def evidence_gap_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("evidence_gaps") or [] if isinstance(item, Mapping))


def verification_gap_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("verification_gaps") or [] if isinstance(item, Mapping))


def source_target_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("targets") or [] if isinstance(item, Mapping))


def validate_evidence_gap_triage(payload: Mapping[str, Any]) -> tuple[str, ...]:
    records = evidence_gap_records(payload)
    errors: list[str] = []
    if len(records) != 6:
        errors.append("must triage six evidence gaps")
    counts = payload.get("triage_counts") or {}
    expected = {"total_evidence_gaps": 6, "p0_count": 2, "p1_count": 2, "p2_count": 2, "ready_for_manual_observation_count": 6}
    for key, value in expected.items():
        if int(counts.get(key, -1)) != value:
            errors.append(f"{key} must be {value}")
    for item in records:
        gap_id = str(item.get("gap_id") or "<missing>")
        if item.get("triage_status") != "ready_for_manual_observation":
            errors.append(f"{gap_id} must be ready_for_manual_observation")
        for flag in ("runtime_source_call_allowed", "download_allowed"):
            if item.get(flag) is not False:
                errors.append(f"{gap_id} must keep {flag}=false")
    return tuple(errors)


def validate_verification_gap_triage(payload: Mapping[str, Any]) -> tuple[str, ...]:
    records = verification_gap_records(payload)
    errors: list[str] = []
    if len(records) != 2:
        errors.append("must triage two verification gaps")
    for item in records:
        gap_id = str(item.get("gap_id") or "<missing>")
        if item.get("verified_artifact") is not False:
            errors.append(f"{gap_id} must not be verified")
        for flag in ("runtime_source_call_allowed", "download_allowed", "safety_claim_allowed", "rights_clearance_claim_allowed"):
            if item.get(flag) is not False:
                errors.append(f"{gap_id} must keep {flag}=false")
    return tuple(errors)


def validate_source_target_plan(payload: Mapping[str, Any]) -> tuple[str, ...]:
    records = source_target_records(payload)
    errors: list[str] = []
    if len(records) != 6:
        errors.append("source target plan must contain six targets")
    if payload.get("runtime_source_calls_allowed") is not False:
        errors.append("runtime source calls must remain disabled")
    if payload.get("downloads_allowed") is not False:
        errors.append("downloads must remain disabled")
    for item in records:
        if item.get("safe_next_task") != "MANUAL-ARTIFACT-OBSERVATION-BATCH-01":
            errors.append(f"{item.get('target_id')} must point to manual observation batch one")
    return tuple(errors)


def validate_public_alpha_artifact_gate(payload: Mapping[str, Any]) -> tuple[str, ...]:
    expected = {
        "reviewed_artifact_record_count": 2,
        "verified_artifact_count": 0,
        "threshold_reviewed_artifact_records": 25,
        "reviewed_artifact_record_gap": 23,
        "new_reviewed_artifact_records_created": 0,
        "new_verified_artifacts_created": 0,
    }
    errors = []
    if payload.get("status") != "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS":
        errors.append("artifact gate must remain failed")
    for key, value in expected.items():
        if int(payload.get(key, -1)) != value:
            errors.append(f"{key} must be {value}")
    if payload.get("public_alpha_blocked") is not True:
        errors.append("public alpha must remain blocked")
    if payload.get("next_recommended_task") != "MANUAL-ARTIFACT-OBSERVATION-BATCH-01":
        errors.append("next recommended task must be manual artifact observation batch one")
    return tuple(errors)


def validate_surface_projection_fixtures(payload: Mapping[str, Any]) -> tuple[str, ...]:
    fixtures = payload.get("fixtures")
    errors: list[str] = []
    if not isinstance(fixtures, list) or len(fixtures) != 3:
        return ("must contain three surface fixtures",)
    for fixture in fixtures:
        fixture_id = str(fixture.get("fixture_id") or "<missing>")
        if fixture.get("expected_status") != "need":
            errors.append(f"{fixture_id} must project as need")
        if tuple(fixture.get("renderer_profiles_expected") or ()) != BASELINE_PROFILES:
            errors.append(f"{fixture_id} must cover baseline profiles")
        if set(_strings(fixture.get("public_actions"))) - PUBLIC_ALLOWED_ACTIONS:
            errors.append(f"{fixture_id} has unsafe public action")
    return tuple(errors)


def validate_renderer_expected_outputs(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if tuple(payload.get("renderer_profiles") or ()) != BASELINE_PROFILES:
        errors.append("renderer profiles must match baseline profiles")
    for status in (payload.get("expected_status_by_fixture") or {}).values():
        if status != "need":
            errors.append("all gap fixtures must render as need")
    return tuple(errors)


def blocked_gap_fixture() -> dict[str, Any]:
    return {
        "gap_id": "block_b00_win98_driver_hardware_identity",
        "title": "Windows 98 driver evidence blocked",
        "summary": "Driver evidence collection remains unsafe without hardware vendor, model, device ID/chipset, bus/interface, exact Windows version, architecture, board/machine model, and source/media context.",
        "status": "need",
        "verified_artifact": False,
        "runtime_source_call_allowed": False,
        "download_allowed": False,
    }


def project_gap_item(item: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="object",
            entity_id=str(item.get("gap_id") or "artifact-gap"),
            payload=_gap_view_payload(item),
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="artifact-evidence-gap-batch-00",
        )
    )


def _gap_view_payload(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "artifact_evidence_gap_view.v0",
        "id": str(item.get("gap_id") or "artifact-gap"),
        "title": str(item.get("title") or item.get("collection_target") or item.get("artifact_record_id") or "Artifact evidence gap"),
        "summary": str(item.get("summary") or "; ".join(_strings(item.get("needed"))) or ""),
        "status": "need",
        "verified_artifact": False,
        "known_gaps": _strings(item.get("needed")),
        "runtime_source_call_allowed": False,
        "download_allowed": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [value]
    return []

