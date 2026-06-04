"""Deterministic hard-query usefulness scoring helpers."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from runtime.surface import SurfaceKernel, SurfaceRequest

from evals.hard_queries.fixtures_v0 import fixture_cases, resolution_run_for_fixture


BASELINE_PROFILES = ("json_v0", "text_v0", "html_basic_v0", "snapshot_v0")
REQUIRED_HARD_QUERY_IDS = (
    "hq_windows_7_apps",
    "hq_driver_win98",
    "hq_blue_ftp_client_xp",
    "hq_sound_blaster_ct1740_manual",
    "hq_firefox_last_xp",
    "hq_ray_tracing_1994_magazine",
)
PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
PUBLIC_FORBIDDEN_ACTIONS = frozenset(
    {
        "review_candidate",
        "promote",
        "reject",
        "supersede",
        "request_more_evidence",
        "rebuild_index",
        "freeze_review",
        "download",
        "install",
        "launch_emulator",
        "run_extraction",
        "submit_direct_evidence",
        "crawl_source",
        "arbitrary_live_lookup",
    }
)


def hard_query_root() -> Path:
    return Path(__file__).resolve().parent


def load_hard_query_registry(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or hard_query_root()) / "hard_query_set_v0.json")


def load_expected_answer_shapes(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or hard_query_root()) / "expected_answer_shapes_v0.json")


def load_scorecard(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or hard_query_root()) / "usefulness_scorecard_v0.json")


def validate_hard_query_registry(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    queries = payload.get("queries")
    if not isinstance(queries, list):
        return ("queries must be a list",)
    ids = [str(item.get("query_id", "")) for item in queries if isinstance(item, Mapping)]
    if len(ids) != len(set(ids)):
        errors.append("query ids must be unique")
    for required_id in REQUIRED_HARD_QUERY_IDS:
        if required_id not in ids:
            errors.append(f"missing required query id: {required_id}")
    for query in queries:
        if not isinstance(query, Mapping):
            errors.append("query entries must be objects")
            continue
        for field in _required_query_fields():
            if field not in query:
                errors.append(f"{query.get('query_id', '<missing>')} missing {field}")
        profiles = tuple(query.get("renderer_profiles_required") or ())
        if profiles != BASELINE_PROFILES:
            errors.append(f"{query.get('query_id', '<missing>')} must require baseline renderer profiles")
        forbidden = set(query.get("forbidden_actions") or ())
        if not PUBLIC_FORBIDDEN_ACTIONS.issubset(forbidden):
            errors.append(f"{query.get('query_id', '<missing>')} missing forbidden public actions")
    return tuple(errors)


def validate_expected_answer_shapes(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    shapes = payload.get("shapes")
    if not isinstance(shapes, list):
        return ("shapes must be a list",)
    ids = {str(item.get("query_id", "")) for item in shapes if isinstance(item, Mapping)}
    for required_id in REQUIRED_HARD_QUERY_IDS:
        if required_id not in ids:
            errors.append(f"missing expected answer shape: {required_id}")
    for shape in shapes:
        if not isinstance(shape, Mapping):
            errors.append("shape entries must be objects")
            continue
        for field in ("useful_units", "must_include", "must_not_include"):
            value = shape.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{shape.get('query_id', '<missing>')} {field} must be a non-empty list")
    return tuple(errors)


def validate_scorecard(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    dimensions = payload.get("dimensions")
    if not isinstance(dimensions, list):
        return ("dimensions must be a list",)
    by_dimension = {
        str(item.get("dimension", "")): item
        for item in dimensions
        if isinstance(item, Mapping)
    }
    for dimension in _score_dimensions():
        item = by_dimension.get(dimension)
        if not item:
            errors.append(f"missing score dimension: {dimension}")
        elif not isinstance(item.get("pass_gate"), int):
            errors.append(f"{dimension} pass_gate must be an integer")
    if tuple(payload.get("renderer_profiles_required") or ()) != BASELINE_PROFILES:
        errors.append("scorecard must require baseline renderer profiles")
    return tuple(errors)


def render_fixture_case(fixture: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    run = resolution_run_for_fixture(fixture)
    rendered: dict[str, dict[str, Any]] = {}
    for profile in BASELINE_PROFILES:
        rendered[profile] = SurfaceKernel().project(
            SurfaceRequest(
                route_id="resolution_run",
                entity_id=str(fixture["query_id"]),
                payload=run,
                requested_profile=profile,
                visibility_posture="public",
                data_version="hard-query-fixtures-v0",
            )
        )
    return rendered


def evaluate_fixture_case(fixture: Mapping[str, Any]) -> dict[str, Any]:
    rendered = render_fixture_case(fixture)
    expected_status = str(fixture["expected_status"])
    scores = {
        "status_honesty": _score_status_honesty(rendered, expected_status),
        "smallest_useful_unit": _score_smallest_unit(fixture),
        "evidence_or_uncertainty_explanation": _score_explanation(fixture, rendered),
        "candidate_need_or_absence_quality": _score_status_quality(fixture),
        "result_reason_quality": _score_reason_quality(fixture),
        "public_action_policy_compliance": _score_public_actions(rendered),
        "renderer_profile_coverage": _score_renderer_coverage(rendered, expected_status),
        "surface_consistency": _score_surface_consistency(rendered, expected_status),
        "no_truth_boundary_bypass": _score_truth_boundary(fixture, rendered),
        "no_live_source_fanout": _score_no_source_fanout(fixture, rendered),
    }
    gates = _pass_gates(load_scorecard())
    return {
        "schema_version": "hard_query_eval_result.v0",
        "query_id": str(fixture["query_id"]),
        "query_text": str(fixture["query_text"]),
        "expected_status": expected_status,
        "scores": scores,
        "pass_gates_met": all(scores.get(dimension, 0) >= threshold for dimension, threshold in gates.items()),
        "rendered_profiles": sorted(rendered),
        "fixture_disclaimer": str(fixture["fixture_disclaimer"]),
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "live_source_calls": False,
    }


def evaluate_fixture_suite() -> dict[str, Any]:
    results = [evaluate_fixture_case(fixture) for fixture in fixture_cases()]
    return {
        "schema_version": "hard_query_eval_suite_result.v0",
        "fixture_count": len(results),
        "query_ids": [result["query_id"] for result in results],
        "all_pass_gates_met": all(result["pass_gates_met"] for result in results),
        "results": results,
        "live_source_calls": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _required_query_fields() -> tuple[str, ...]:
    return (
        "query_id",
        "query_text",
        "intent_summary",
        "intent_type",
        "object_types_expected",
        "smallest_useful_unit",
        "allowed_result_statuses",
        "minimum_useful_public_output",
        "expected_evidence_shape",
        "known_ambiguities",
        "near_miss_rules",
        "absence_rules",
        "policy_block_rules",
        "allowed_source_families_for_future_runs",
        "forbidden_actions",
        "renderer_profiles_required",
        "score_weights",
        "public_alpha_relevance",
        "notes",
    )


def _score_dimensions() -> tuple[str, ...]:
    return (
        "status_honesty",
        "smallest_useful_unit",
        "evidence_or_uncertainty_explanation",
        "candidate_need_or_absence_quality",
        "result_reason_quality",
        "public_action_policy_compliance",
        "renderer_profile_coverage",
        "surface_consistency",
        "no_truth_boundary_bypass",
        "no_live_source_fanout",
    )


def _pass_gates(scorecard: Mapping[str, Any]) -> dict[str, int]:
    gates: dict[str, int] = {}
    for item in scorecard.get("dimensions") or []:
        if isinstance(item, Mapping):
            gates[str(item.get("dimension"))] = int(item.get("pass_gate", 0))
    return gates


def _score_status_honesty(rendered: Mapping[str, Mapping[str, Any]], expected_status: str) -> int:
    statuses = [_view_status(result) for result in rendered.values()]
    if all(status == expected_status and status != "verified" for status in statuses):
        return 3
    if all(status != "verified" for status in statuses):
        return 1
    return 0


def _score_smallest_unit(fixture: Mapping[str, Any]) -> int:
    fallback = _fallback(fixture)
    status = str(fixture["expected_status"])
    if status in {"candidate", "near_miss"} and fallback.get("candidates"):
        return 3
    if status == "need" and fallback.get("needs"):
        return 3
    if status in {"policy_blocked", "unavailable", "unknown"}:
        return 2
    return 1


def _score_explanation(fixture: Mapping[str, Any], rendered: Mapping[str, Mapping[str, Any]]) -> int:
    fallback = _fallback(fixture)
    text = _combined_text(rendered)
    if fallback.get("reason_codes") and (fallback.get("evidence_summary") or "summary unavailable" not in text):
        return 3
    if fallback.get("reason_codes"):
        return 2
    return 0


def _score_status_quality(fixture: Mapping[str, Any]) -> int:
    fallback = _fallback(fixture)
    status = str(fixture["expected_status"])
    if status in {"candidate", "near_miss"}:
        return 3 if fallback.get("candidates") else 1
    if status == "need":
        return 3 if fallback.get("needs") else 1
    if status == "policy_blocked":
        return 3 if fallback.get("policy_block_reason") else 1
    if status in {"unavailable", "unknown"}:
        return 3 if fallback.get("unavailable_reason") or fallback.get("reason_codes") else 1
    return 1


def _score_reason_quality(fixture: Mapping[str, Any]) -> int:
    reasons = _fallback(fixture).get("reason_codes")
    return 3 if isinstance(reasons, list) and len(reasons) >= 2 else 1


def _score_public_actions(rendered: Mapping[str, Mapping[str, Any]]) -> int:
    combined = _combined_text(rendered)
    if any(action in combined for action in PUBLIC_FORBIDDEN_ACTIONS):
        return 0
    for result in rendered.values():
        actions = result.get("view_model", {}).get("actions", [])
        for action in actions:
            action_id = str(action.get("action_id", "")) if isinstance(action, Mapping) else str(action)
            if action_id and action_id not in PUBLIC_ALLOWED_ACTIONS:
                return 0
    return 3


def _score_renderer_coverage(rendered: Mapping[str, Mapping[str, Any]], expected_status: str) -> int:
    if tuple(sorted(rendered)) != tuple(sorted(BASELINE_PROFILES)):
        return 0
    if all(expected_status in repr(result.get("renderer_result", {}).get("renderer_output", {})) for result in rendered.values()):
        return 3
    return 2


def _score_surface_consistency(rendered: Mapping[str, Mapping[str, Any]], expected_status: str) -> int:
    statuses = {_view_status(result) for result in rendered.values()}
    return 3 if statuses == {expected_status} else 0


def _score_truth_boundary(fixture: Mapping[str, Any], rendered: Mapping[str, Mapping[str, Any]]) -> int:
    if any(bool(fixture.get(key)) for key in _mutation_keys()):
        return 0
    fallback = _fallback(fixture)
    if bool(fallback.get("verified")) or bool(fallback.get("accepted_truth")):
        return 0
    if any(bool(fallback.get(key)) for key in _mutation_keys()):
        return 0
    for result in rendered.values():
        if bool(result.get("surface_kernel_mutated_reviewed_index")):
            return 0
        renderer = result.get("renderer_result", {})
        if any(
            bool(renderer.get(key))
            for key in (
                "renderer_created_verified_state",
                "renderer_mutated_reviewed_index",
                "renderer_mutated_public_index",
                "renderer_mutated_master_index",
            )
        ):
            return 0
    return 3


def _score_no_source_fanout(fixture: Mapping[str, Any], rendered: Mapping[str, Mapping[str, Any]]) -> int:
    if bool(fixture.get("live_source_calls")) or bool(_fallback(fixture).get("live_source_calls")):
        return 0
    for result in rendered.values():
        if bool(result.get("surface_kernel_called_source_provider")):
            return 0
        if bool(result.get("renderer_result", {}).get("renderer_called_source_provider")):
            return 0
    return 3


def _fallback(fixture: Mapping[str, Any]) -> Mapping[str, Any]:
    value = fixture.get("fallback_summary")
    return value if isinstance(value, Mapping) else {}


def _view_status(result: Mapping[str, Any]) -> str:
    return str(result.get("view_model", {}).get("canonical_status", "unknown"))


def _combined_text(rendered: Mapping[str, Mapping[str, Any]]) -> str:
    outputs = [result.get("renderer_result", {}).get("renderer_output", {}) for result in rendered.values()]
    return repr(deepcopy(outputs))


def _mutation_keys() -> tuple[str, ...]:
    return (
        "reviewed_record_created",
        "reviewed_index_mutated",
        "public_index_mutated",
        "master_index_mutated",
    )
