"""Loader and SurfaceKernel projection helpers for reviewed corpus seed batch two."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries.seed_corpus.loader import BASELINE_PROFILES, PUBLIC_ALPHA_TARGETS, REQUIRED_HARD_QUERY_IDS
from runtime.surface import SurfaceKernel, SurfaceRequest


PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
OUTCOME_STATUSES = frozenset(
    {"verified", "candidate", "need", "near_miss", "superseded", "policy_blocked", "unavailable", "unknown"}
)
TRUTH_BOUNDARY_FLAGS = (
    "synthetic_eval_fixture_used_as_evidence",
    "ai_model_output_counted_as_truth",
    "source_observation_self_promoted",
    "candidate_self_promoted",
    "fallback_summary_self_promoted",
    "reviewable_item_self_promoted",
    "reviewed_index_mutated",
    "public_index_mutated",
    "master_index_mutated",
    "product_runtime_live_source_calls_performed",
    "downloads_performed",
    "file_fetches_performed",
    "wayback_replay_performed",
)
REQUIRED_OUTPUTS = (
    "README.md",
    "reviewed_seed_records.json",
    "review_decision_backed_outcomes.json",
    "cumulative_corpus_counts.json",
    "query_coverage.json",
    "public_alpha_gate.json",
    "evidence_gap_queue.yml",
    "reviewed_record_backlog.yml",
    "manual_followups.yml",
    "blocked_for_user_details.yml",
    "supersession_map.json",
    "source_reference_index.json",
    "surface_projection_fixtures.json",
    "renderer_expected_outputs.json",
    "truth_boundary_report.md",
    "validation_summary.json",
    "next_validation_pivot.json",
)


def batch_root() -> Path:
    return Path(__file__).resolve().parent


def load_reviewed_seed_records(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "reviewed_seed_records.json")


def load_review_decision_backed_outcomes(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "review_decision_backed_outcomes.json")


def load_cumulative_corpus_counts(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "cumulative_corpus_counts.json")


def load_query_coverage(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "query_coverage.json")


def load_public_alpha_gate(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "public_alpha_gate.json")


def load_supersession_map(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "supersession_map.json")


def load_source_reference_index(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "source_reference_index.json")


def load_surface_projection_fixtures(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "surface_projection_fixtures.json")


def load_renderer_expected_outputs(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "renderer_expected_outputs.json")


def load_validation_summary(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "validation_summary.json")


def load_next_validation_pivot(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "next_validation_pivot.json")


def read_batch_text(name: str, root: Path | None = None) -> str:
    return ((root or batch_root()) / name).read_text(encoding="utf-8")


def reviewed_seed_record_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("reviewed_seed_records") or [] if isinstance(item, Mapping))


def outcome_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("outcomes") or [] if isinstance(item, Mapping))


def query_coverage_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("query_coverage") or [] if isinstance(item, Mapping))


def source_reference_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("source_references") or [] if isinstance(item, Mapping))


def supersession_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("supersessions") or [] if isinstance(item, Mapping))


def reviewed_corpus_counts(outcomes_payload: Mapping[str, Any]) -> dict[str, int]:
    counts = {
        "reviewed": 0,
        "review_decision_backed": 0,
        "candidate": 0,
        "need": 0,
        "near_miss": 0,
        "superseded": 0,
        "policy_blocked": 0,
        "unavailable": 0,
        "unknown": 0,
        "request_more_evidence": 0,
        "blocked_for_user_details": 0,
    }
    for outcome in outcome_records(outcomes_payload):
        status = str(outcome.get("outcome_status") or "unknown")
        decision = str(outcome.get("decision") or "")
        if outcome.get("review_decision_id"):
            counts["review_decision_backed"] += 1
        if decision == "request_more_evidence":
            counts["request_more_evidence"] += 1
        if outcome.get("blocked_for_user_details") is True:
            counts["blocked_for_user_details"] += 1
        if _counts_as_reviewed(outcome):
            counts["reviewed"] += 1
        elif status in {"candidate", "need", "near_miss", "superseded", "policy_blocked", "unavailable"}:
            counts[status] += 1
        elif status != "verified":
            counts["unknown"] += 1
    return counts


def validate_required_outputs() -> tuple[str, ...]:
    missing = [name for name in REQUIRED_OUTPUTS if not (batch_root() / name).exists()]
    return tuple(f"missing required output: {name}" for name in missing)


def validate_reviewed_seed_records(records: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    record_items = reviewed_seed_record_records(records)
    if len(record_items) != 3:
        errors.append("batch two must carry exactly three reviewed seed records")
    record_ids = {str(record.get("reviewed_seed_record_id") or "") for record in record_items}
    for expected in {
        "reviewed_seed_hq_windows_7_firefox_115_support_fact",
        "reviewed_seed_hq_firefox_xp_52_9_support_fact",
        "reviewed_seed_b01_hq_windows_7_7zip_support_fact",
    }:
        if expected not in record_ids:
            errors.append(f"missing reviewed seed record: {expected}")
    for record in record_items:
        record_id = str(record.get("reviewed_seed_record_id") or "<missing>")
        if record.get("canonical_status") != "verified":
            errors.append(f"{record_id} must be verified")
        if record.get("accepted_truth") is not True:
            errors.append(f"{record_id} must mark accepted_truth=true")
        if not record.get("review_event_id") or not record.get("review_decision_id"):
            errors.append(f"{record_id} must include review event and decision refs")
        if not record.get("evidence_refs") or not record.get("source_observation_refs"):
            errors.append(f"{record_id} must include evidence and source observation refs")
        for flag in ("reviewed_index_mutated", "public_index_mutated", "master_index_mutated"):
            if record.get(flag) is not False:
                errors.append(f"{record_id} must keep {flag}=false")
    return tuple(errors)


def validate_review_decision_backed_outcomes(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    records = outcome_records(payload)
    if len(records) != 12:
        errors.append("batch two must preserve twelve Batch 01 review-decision-backed outcomes")
    hard_query_ids = {str(item.get("hard_query_id") or "") for item in records}
    for required in REQUIRED_HARD_QUERY_IDS:
        if required not in hard_query_ids:
            errors.append(f"missing outcome for {required}")
    for item in records:
        outcome_id = str(item.get("outcome_id") or "<missing>")
        status = str(item.get("outcome_status") or "")
        decision = str(item.get("decision") or "")
        if status not in OUTCOME_STATUSES:
            errors.append(f"{outcome_id} has unsupported status")
        if not item.get("review_decision_id") or not item.get("review_event_id"):
            errors.append(f"{outcome_id} must include review decision and event refs")
        if decision == "promote":
            if not _counts_as_reviewed(item):
                errors.append(f"{outcome_id} promote outcome must count as reviewed")
        else:
            if item.get("reviewed_seed_record_created") is not False:
                errors.append(f"{outcome_id} non-promote must not create reviewed seed record")
            if status == "verified":
                errors.append(f"{outcome_id} non-promote must not become verified")
        for flag in TRUTH_BOUNDARY_FLAGS:
            if item.get("truth_boundary", {}).get(flag) is not False:
                errors.append(f"{outcome_id} truth boundary flag must be false: {flag}")
    return tuple(errors)


def validate_cumulative_corpus_counts(payload: Mapping[str, Any], outcomes: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    batch_counts = payload.get("batch_02_added_counts")
    cumulative = payload.get("cumulative_counts")
    if not isinstance(batch_counts, Mapping) or not isinstance(cumulative, Mapping):
        return ("batch_02_added_counts and cumulative_counts must be present",)
    computed = reviewed_corpus_counts(outcomes or load_review_decision_backed_outcomes())
    for key, value in computed.items():
        if int(batch_counts.get(f"{key}_count", -1)) != value:
            errors.append(f"batch {key}_count does not match outcomes")
    expected_cumulative = {
        "reviewed_count": 3,
        "review_decision_backed_count": 18,
        "need_count": 5,
        "near_miss_count": 3,
        "superseded_count": 3,
        "request_more_evidence_count": 4,
        "blocked_for_user_details_count": 1,
    }
    for key, value in expected_cumulative.items():
        if int(cumulative.get(key, -1)) != value:
            errors.append(f"cumulative {key} must be {value}")
    return tuple(errors)


def validate_query_coverage(coverage: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    coverage_items = query_coverage_records(coverage)
    if len(coverage_items) != len(REQUIRED_HARD_QUERY_IDS):
        errors.append("query coverage must cover all six hard queries")
    query_ids = {str(item.get("query_id") or item.get("hard_query_id") or "") for item in coverage_items}
    for required in REQUIRED_HARD_QUERY_IDS:
        if required not in query_ids:
            errors.append(f"missing query coverage for {required}")
    for item in coverage_items:
        query_id = str(item.get("query_id") or item.get("hard_query_id") or "<missing>")
        if item.get("readiness") != "not_ready":
            errors.append(f"{query_id} must remain not_ready")
        if not item.get("next_action"):
            errors.append(f"{query_id} must include next_action")
    return tuple(errors)


def validate_public_alpha_gate(gate: Mapping[str, Any], counts: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    if gate.get("public_alpha_corpus_gate") != "FAIL_INSUFFICIENT_REVIEWED_CORPUS":
        errors.append("public alpha corpus gate must remain failed")
    gate_counts = gate.get("counts")
    cumulative = (counts or load_cumulative_corpus_counts()).get("cumulative_counts")
    if not isinstance(gate_counts, Mapping) or not isinstance(cumulative, Mapping):
        return tuple(errors + ["gate and cumulative counts must be present"])
    for key in ("reviewed_count", "review_decision_backed_count", "need_count", "near_miss_count", "superseded_count", "blocked_for_user_details_count"):
        if int(gate_counts.get(key, -1)) != int(cumulative.get(key, -2)):
            errors.append(f"gate {key} must match cumulative counts")
    targets = gate.get("minimum_public_alpha_targets")
    if not isinstance(targets, Mapping):
        errors.append("gate targets must be present")
    else:
        for key, value in PUBLIC_ALPHA_TARGETS.items():
            if int(targets.get(key, -1)) != value:
                errors.append(f"target mismatch for {key}")
    for flag in TRUTH_BOUNDARY_FLAGS:
        if gate.get("truth_boundary", {}).get(flag) is not False:
            errors.append(f"gate truth boundary flag must be false: {flag}")
    if gate.get("next_primary_task") != "SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01":
        errors.append("gate must pivot to SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01")
    return tuple(errors)


def validate_supersession_map(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    items = supersession_records(payload)
    if len(items) != 3:
        errors.append("supersession map must contain three duplicate-control entries")
    for item in items:
        item_id = str(item.get("supersession_id") or "<missing>")
        if not item.get("source_review_decision_id") or not item.get("target_reviewed_seed_record_id"):
            errors.append(f"{item_id} must link decision to target reviewed seed record")
        if item.get("counts_as_new_reviewed_record") is not False:
            errors.append(f"{item_id} must not count as a new reviewed record")
    return tuple(errors)


def validate_source_reference_index(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    refs = source_reference_records(payload)
    if len(refs) != 17:
        errors.append("source reference index must contain the 17 Batch 00 and Batch 01 source refs")
    ids = {str(item.get("source_ref_id") or "") for item in refs}
    for required in {
        "src_mozilla_win7_firefox_115",
        "src_mozilla_xp_firefox_52_9",
        "src_b01_7zip_official",
        "src_b01_firefox_xp_support_article",
        "src_b01_radiance_paper_page",
    }:
        if required not in ids:
            errors.append(f"missing source ref: {required}")
    for item in refs:
        item_id = str(item.get("source_ref_id") or "<missing>")
        if not item.get("title") or "confidence" not in item:
            errors.append(f"{item_id} must include title and confidence")
        if item.get("runtime_live_source_call_performed") is not False:
            errors.append(f"{item_id} must record no runtime source call")
    return tuple(errors)


def validate_surface_projection_fixtures(payload: Mapping[str, Any], outcomes: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list):
        return ("surface projection fixtures must be a list",)
    outcome_ids = {str(item.get("outcome_id") or "") for item in outcome_records(outcomes or load_review_decision_backed_outcomes())}
    for fixture in fixtures:
        if not isinstance(fixture, Mapping):
            errors.append("fixture must be an object")
            continue
        fixture_id = str(fixture.get("outcome_id") or "")
        if fixture_id not in outcome_ids:
            errors.append(f"{fixture_id or '<missing>'} references unknown outcome")
        if tuple(fixture.get("renderer_profiles_expected") or ()) != BASELINE_PROFILES:
            errors.append(f"{fixture_id or '<missing>'} must cover all baseline profiles")
        public_actions = set(_strings(fixture.get("public_actions")))
        if not public_actions.issubset(PUBLIC_ALLOWED_ACTIONS):
            errors.append(f"{fixture_id or '<missing>'} has unsafe public action")
    return tuple(errors)


def validate_renderer_expected_outputs(payload: Mapping[str, Any], outcomes: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    if tuple(payload.get("renderer_profiles") or ()) != BASELINE_PROFILES:
        errors.append("renderer expected outputs must cover all baseline profiles")
    expected = payload.get("expected_status_by_outcome")
    if not isinstance(expected, Mapping):
        return tuple(errors + ["expected_status_by_outcome must be present"])
    for outcome in outcome_records(outcomes or load_review_decision_backed_outcomes()):
        outcome_id = str(outcome.get("outcome_id") or "")
        if expected.get(outcome_id) != outcome.get("outcome_status"):
            errors.append(f"{outcome_id} expected status does not match outcome")
    return tuple(errors)


def validate_next_validation_pivot(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if payload.get("next_primary_task") != "SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01":
        errors.append("next primary task must be SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01")
    for key in ("root_structure_frozen", "public_alpha_blocked", "dev_to_main_blocked", "source_snapshot_closeout_needed"):
        if payload.get(key) is not True:
            errors.append(f"{key} must be true")
    if payload.get("public_alpha_corpus_gate") != "FAIL_INSUFFICIENT_REVIEWED_CORPUS":
        errors.append("pivot must preserve failed corpus gate")
    return tuple(errors)


def project_outcome(outcome: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    public = visibility_posture != "operator_private"
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="object",
            entity_id=_public_outcome_ref(outcome) if public else str(outcome.get("outcome_id") or "reviewed-corpus-outcome"),
            payload=_outcome_view_payload(outcome, public=public),
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="reviewed-corpus-seed-batch-02",
        )
    )


def project_reviewed_seed_record(record: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    public = visibility_posture != "operator_private"
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="object",
            entity_id=str(record.get("reviewed_seed_record_id") or "reviewed-seed-record"),
            payload=_record_view_payload(record, public=public),
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="reviewed-corpus-seed-batch-02",
        )
    )


def _outcome_view_payload(outcome: Mapping[str, Any], *, public: bool) -> dict[str, Any]:
    payload = {
        "schema_version": "reviewed_corpus_outcome_view.v1",
        "id": _public_outcome_ref(outcome) if public else str(outcome.get("outcome_id") or "reviewed-corpus-outcome"),
        "title": str(outcome.get("title") or outcome.get("query_id") or "Reviewed corpus outcome"),
        "summary": str(outcome.get("public_summary") or outcome.get("useful_unit") or outcome.get("rationale") or ""),
        "status": str(outcome.get("public_projection_status") or outcome.get("outcome_status") or "unknown"),
        "query_id": str(outcome.get("query_id") or outcome.get("hard_query_id") or ""),
        "public_review_ref": _public_outcome_ref(outcome),
        "evidence_posture": str(outcome.get("evidence_posture") or "review_decision_backed"),
        "known_gaps": _strings(outcome.get("known_gaps")),
        "next_required_action": str(outcome.get("public_next_action") or ""),
        "blocked_for_user_details": bool(outcome.get("blocked_for_user_details")),
        "reviewed_seed_record_created": bool(outcome.get("reviewed_seed_record_created")),
        "counts_as_reviewed": bool(outcome.get("counts_as_reviewed")),
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }
    if not public:
        payload["review_decision_id"] = str(outcome.get("review_decision_id") or "")
        payload["review_event_id"] = str(outcome.get("review_event_id") or "")
        payload["decision"] = str(outcome.get("decision") or "")
        payload["operator_actions"] = _strings(outcome.get("operator_actions"))
    return payload


def _record_view_payload(record: Mapping[str, Any], *, public: bool) -> dict[str, Any]:
    payload = {
        "schema_version": "reviewed_corpus_seed_record_view.v1",
        "id": str(record.get("reviewed_seed_record_id") or "reviewed-seed-record"),
        "title": str(record.get("title") or "Reviewed seed record"),
        "summary": str(record.get("summary") or ""),
        "status": str(record.get("canonical_status") or "unknown"),
        "query_id": str(record.get("query_id") or record.get("hard_query_id") or ""),
        "public_review_ref": f"reviewed_corpus_record_public_{record.get('query_id') or record.get('hard_query_id', 'unknown')}",
        "evidence_posture": "review_event_backed",
        "accepted_truth": bool(record.get("accepted_truth")),
        "reviewed_seed_record_created": bool(record.get("reviewed_record_created")),
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }
    if not public:
        payload["review_decision_id"] = str(record.get("review_decision_id") or "")
        payload["review_event_id"] = str(record.get("review_event_id") or "")
        payload["operator_actions"] = ["review_candidate", "rebuild_index"]
    return payload


def _counts_as_reviewed(outcome: Mapping[str, Any]) -> bool:
    return (
        outcome.get("decision") == "promote"
        and outcome.get("outcome_status") == "verified"
        and outcome.get("counts_as_reviewed") is True
        and bool(outcome.get("reviewed_seed_record_id"))
    )


def _public_outcome_ref(outcome: Mapping[str, Any]) -> str:
    return str(outcome.get("public_ref") or f"reviewed_corpus_public_{outcome.get('query_id') or outcome.get('hard_query_id', 'unknown')}")


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
