"""Loader, validation, and projection helpers for reviewed artifact corpus batch one."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries.artifact_observations.batch_00 import BASELINE_PROFILES, REQUIRED_HARD_QUERY_IDS
from runtime.surface import SurfaceKernel, SurfaceRequest


PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
FORBIDDEN_PUBLIC_ACTIONS = frozenset(
    {
        "review_candidate",
        "promote",
        "reject",
        "request_more_evidence",
        "download",
        "install",
        "rebuild_index",
        "crawl_source",
        "arbitrary_live_lookup",
    }
)
TRUTH_FLAGS = (
    "source_observation_self_promoted",
    "reviewed_index_mutated",
    "public_index_mutated",
    "master_index_mutated",
    "runtime_source_calls_performed",
    "downloads_performed",
    "file_fetches_performed",
    "wayback_replay_performed",
)


def batch_root() -> Path:
    return Path(__file__).resolve().parent


def load_reviewed_artifact_records(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "reviewed_artifact_records.json")


def load_artifact_decision_backed_outcomes(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "artifact_decision_backed_outcomes.json")


def load_non_promoted_artifact_leads(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "non_promoted_artifact_leads.json")


def load_artifact_level_inventory(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "artifact_level_inventory.json")


def load_query_coverage(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "query_coverage.json")


def load_public_alpha_artifact_gate(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "public_alpha_artifact_gate.json")


def load_cumulative_artifact_counts(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "cumulative_artifact_counts.json")


def load_source_reference_index(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "source_reference_index.json")


def load_supersession_or_duplicate_control(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "supersession_or_duplicate_control.json")


def load_surface_projection_fixtures(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "surface_projection_fixtures.json")


def load_renderer_expected_outputs(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "renderer_expected_outputs.json")


def read_batch_text(name: str, root: Path | None = None) -> str:
    return ((root or batch_root()) / name).read_text(encoding="utf-8")


def reviewed_artifact_record_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("reviewed_artifact_records") or [] if isinstance(item, Mapping))


def artifact_decision_outcome_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("outcomes") or [] if isinstance(item, Mapping))


def non_promoted_lead_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("non_promoted_artifact_leads") or [] if isinstance(item, Mapping))


def query_coverage_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("query_coverage") or [] if isinstance(item, Mapping))


def source_reference_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("source_references") or [] if isinstance(item, Mapping))


def validate_reviewed_artifact_records(payload: Mapping[str, Any]) -> tuple[str, ...]:
    records = reviewed_artifact_record_records(payload)
    errors: list[str] = []
    if len(records) != 2:
        errors.append("batch one must contain two reviewed artifact records")
    for record in records:
        record_id = str(record.get("artifact_record_id") or "<missing>")
        if record.get("status") != "reviewed_artifact_record":
            errors.append(f"{record_id} must have reviewed_artifact_record status")
        if record.get("verified_artifact") is not False:
            errors.append(f"{record_id} must not be a verified artifact")
        if record.get("artifact_level") != "artifact_level_3_artifact_identity_evidence":
            errors.append(f"{record_id} must be level3 identity evidence")
        if record.get("manual_reference_only") is not True:
            errors.append(f"{record_id} must be manual_reference_only")
        for field in (
            "review_decision_id",
            "review_event_id",
            "review_batch_id",
            "review_rationale",
            "evidence_summary",
            "identity_evidence",
            "integrity_evidence",
            "acquisition_or_reproducibility_evidence",
        ):
            if not record.get(field):
                errors.append(f"{record_id} missing {field}")
        for flag in ("reviewed_index_mutated", "public_index_mutated", "master_index_mutated"):
            if record.get(flag) is not False:
                errors.append(f"{record_id} must keep {flag}=false")
    return tuple(errors)


def validate_artifact_decision_backed_outcomes(payload: Mapping[str, Any]) -> tuple[str, ...]:
    records = artifact_decision_outcome_records(payload)
    errors: list[str] = []
    if len(records) != 10:
        errors.append("batch one must preserve ten human artifact review outcomes")
    promote_count = 0
    for outcome in records:
        outcome_id = str(outcome.get("outcome_id") or "<missing>")
        if not outcome.get("review_decision_id") or not outcome.get("review_event_id"):
            errors.append(f"{outcome_id} must include review decision and event refs")
        if outcome.get("decision") == "promote":
            promote_count += 1
            if outcome.get("counts_as_reviewed_artifact_record") is not True:
                errors.append(f"{outcome_id} promote must count as reviewed artifact record")
            if not outcome.get("artifact_record_id"):
                errors.append(f"{outcome_id} promote must link artifact_record_id")
        else:
            if outcome.get("counts_as_reviewed_artifact_record") is not False:
                errors.append(f"{outcome_id} non-promote must not count as reviewed artifact record")
            if outcome.get("artifact_record_id") is not None:
                errors.append(f"{outcome_id} non-promote must not link artifact_record_id")
        if outcome.get("verified_artifact") is not False:
            errors.append(f"{outcome_id} must not be verified artifact")
        for flag in TRUTH_FLAGS:
            if outcome.get("truth_boundary", {}).get(flag) is not False:
                errors.append(f"{outcome_id} truth flag must be false: {flag}")
    if promote_count != 2:
        errors.append("batch one must have exactly two promote outcomes")
    return tuple(errors)


def validate_non_promoted_artifact_leads(payload: Mapping[str, Any]) -> tuple[str, ...]:
    leads = non_promoted_lead_records(payload)
    errors: list[str] = []
    if len(leads) != 8:
        errors.append("batch one must contain eight non-promoted artifact leads")
    for lead in leads:
        lead_id = str(lead.get("artifact_observation_id") or "<missing>")
        if lead.get("decision") == "promote":
            errors.append(f"{lead_id} must not be promoted")
        if lead.get("status") not in {"need", "near_miss", "unavailable"}:
            errors.append(f"{lead_id} has unsupported non-promoted status")
        if lead.get("verified_artifact") is not False:
            errors.append(f"{lead_id} must not be verified")
    return tuple(errors)


def validate_artifact_level_inventory(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if payload.get("inflation_prevented") is not True:
        errors.append("inflation_prevented must be true")
    reviewed = payload.get("reviewed_artifact_record_level_counts")
    non_promoted = payload.get("non_promoted_level_counts")
    if not isinstance(reviewed, Mapping) or not isinstance(non_promoted, Mapping):
        return tuple(errors + ["reviewed and non-promoted level counts must be present"])
    if int(reviewed.get("artifact_level_3_artifact_identity_evidence", -1)) != 2:
        errors.append("level3 reviewed artifact record count must be 2")
    if int(non_promoted.get("artifact_level_1_metadata_or_source_lead", -1)) != 1:
        errors.append("level1 material must remain non-promoted")
    if int(non_promoted.get("artifact_level_2_source_observed_artifact_listing", -1)) != 4:
        errors.append("level2 material must remain non-promoted")
    return tuple(errors)


def validate_query_coverage(payload: Mapping[str, Any]) -> tuple[str, ...]:
    records = query_coverage_records(payload)
    errors: list[str] = []
    query_ids = {str(item.get("query_id") or "") for item in records}
    if query_ids != set(REQUIRED_HARD_QUERY_IDS):
        errors.append("query coverage must cover all six hard queries")
    if payload.get("hard_query_reviewed_artifact_coverage") != "2/6":
        errors.append("reviewed artifact coverage must be 2/6")
    if payload.get("hard_query_verified_artifact_coverage") != "0/6":
        errors.append("verified artifact coverage must be 0/6")
    for item in records:
        if item.get("public_alpha_ready") is not False:
            errors.append(f"{item.get('query_id')} must not be public-alpha ready")
        if not item.get("next_action"):
            errors.append(f"{item.get('query_id')} must include next_action")
    return tuple(errors)


def validate_public_alpha_artifact_gate(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    expected = {
        "reviewed_artifact_record_count": 2,
        "verified_artifact_count": 0,
        "threshold_reviewed_artifact_records": 25,
        "reviewed_artifact_record_gap": 23,
    }
    if payload.get("status") != "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS":
        errors.append("artifact gate must remain failed")
    for key, value in expected.items():
        if int(payload.get(key, -1)) != value:
            errors.append(f"{key} must be {value}")
    if payload.get("public_alpha_blocked") is not True:
        errors.append("public alpha must remain blocked")
    if payload.get("dev_to_main_promotion_blocked") is not True:
        errors.append("dev to main promotion must remain blocked")
    if payload.get("next_recommended_task") != "ARTIFACT-EVIDENCE-GAP-BATCH-00":
        errors.append("next recommended task must be artifact evidence gap batch")
    return tuple(errors)


def validate_cumulative_artifact_counts(payload: Mapping[str, Any]) -> tuple[str, ...]:
    expected = {
        "reviewed_artifact_record_count": 2,
        "verified_artifact_count": 0,
        "non_promoted_artifact_lead_count": 8,
        "need_count": 4,
        "unavailable_count": 1,
        "near_miss_count": 3,
        "request_more_evidence_count": 5,
        "blocked_for_user_details_count": 1,
    }
    errors = [f"{key} must be {value}" for key, value in expected.items() if int(payload.get(key, -1)) != value]
    if payload.get("public_alpha_artifact_gate") != "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS":
        errors.append("artifact gate must remain failed")
    return tuple(errors)


def validate_source_reference_index(payload: Mapping[str, Any]) -> tuple[str, ...]:
    refs = source_reference_records(payload)
    errors: list[str] = []
    if len(refs) != 11:
        errors.append("source reference index must contain eleven manual references")
    for ref in refs:
        source_id = str(ref.get("source_id") or "<missing>")
        if ref.get("manual_reference_only") is not True:
            errors.append(f"{source_id} must be manual_reference_only")
        for flag in ("runtime_source_call_performed", "download_performed", "file_fetch_performed", "wayback_replay_performed"):
            if ref.get(flag) is not False:
                errors.append(f"{source_id} must keep {flag}=false")
    return tuple(errors)


def validate_supersession_or_duplicate_control(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    items = payload.get("duplicate_control")
    if not isinstance(items, list) or len(items) != 2:
        return ("duplicate control must contain two reviewed artifact records",)
    if payload.get("supersession_required") is not False:
        errors.append("supersession_required must be false")
    for item in items:
        if item.get("duplicate_of_existing_record") is not False:
            errors.append(f"{item.get('control_id')} must not be duplicate")
    return tuple(errors)


def validate_surface_projection_fixtures(payload: Mapping[str, Any]) -> tuple[str, ...]:
    fixtures = payload.get("fixtures")
    errors: list[str] = []
    if not isinstance(fixtures, list):
        return ("fixtures must be a list",)
    expected_kinds = {"reviewed_artifact_record", "outcome", "blocked_for_user_details"}
    for fixture in fixtures:
        fixture_id = str(fixture.get("fixture_id") or "<missing>")
        if fixture.get("kind") not in expected_kinds:
            errors.append(f"{fixture_id} has unsupported kind")
        if tuple(fixture.get("renderer_profiles_expected") or ()) != BASELINE_PROFILES:
            errors.append(f"{fixture_id} must cover baseline profiles")
        if set(_strings(fixture.get("public_actions"))) - PUBLIC_ALLOWED_ACTIONS:
            errors.append(f"{fixture_id} exposes unsupported public action")
        if fixture.get("expected_verified_artifact") is not False:
            errors.append(f"{fixture_id} must not expect verified artifact")
    return tuple(errors)


def validate_renderer_expected_outputs(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if tuple(payload.get("renderer_profiles") or ()) != BASELINE_PROFILES:
        errors.append("renderer profiles must match baseline profiles")
    expected = payload.get("expected_status_by_fixture")
    if not isinstance(expected, Mapping):
        return tuple(errors + ["expected_status_by_fixture must be present"])
    for fixture in load_surface_projection_fixtures().get("fixtures") or []:
        if expected.get(fixture["fixture_id"]) != fixture["expected_status"]:
            errors.append(f"{fixture['fixture_id']} expected status mismatch")
    return tuple(errors)


def blocked_for_user_details_fixture() -> dict[str, Any]:
    return {
        "id": "artifact_corpus_b01_win98_driver_blocked",
        "title": "Windows 98 driver query blocked for hardware details",
        "summary": "A Windows 98 driver recommendation is unsafe without hardware vendor, model, device ID/chipset, bus/interface, exact Windows version, architecture, board/machine model, and known source/media context.",
        "status": "need",
        "artifact_claim_status": "blocked_for_user_details",
        "verified_artifact": False,
        "known_gaps": [
            "hardware_vendor",
            "hardware_model",
            "device_id_or_chipset",
            "bus_or_interface",
            "exact_windows_version",
            "architecture",
            "machine_or_board_model",
            "known_source_or_media_context",
        ],
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def project_artifact_corpus_item(item: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="object",
            entity_id=str(item.get("artifact_record_id") or item.get("outcome_id") or item.get("id") or "artifact-corpus-item"),
            payload=_view_payload(item),
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="reviewed-artifact-corpus-batch-01",
        )
    )


def _view_payload(item: Mapping[str, Any]) -> dict[str, Any]:
    status = str(item.get("surface_projection_status") or item.get("public_projection_status") or item.get("canonical_status") or item.get("status") or "unknown")
    return {
        "schema_version": "reviewed_artifact_corpus_item_view.v0",
        "id": str(item.get("artifact_record_id") or item.get("outcome_id") or item.get("id") or "artifact-corpus-item"),
        "title": str(item.get("title") or item.get("artifact_observation_id") or item.get("query_id") or "Artifact corpus item"),
        "summary": str(item.get("evidence_summary") or item.get("reason") or "; ".join(_strings(item.get("known_gaps"))) or ""),
        "status": status,
        "artifact_claim_status": str(item.get("artifact_claim_status") or item.get("status") or "artifact_lead"),
        "verified_artifact": bool(item.get("verified_artifact")),
        "known_gaps": _strings(item.get("known_gaps") or item.get("required_evidence")),
        "source_reference_ids": _strings(item.get("source_reference_ids")),
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

