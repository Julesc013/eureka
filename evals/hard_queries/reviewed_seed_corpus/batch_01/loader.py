"""Loader and SurfaceKernel projection helpers for reviewed corpus seed batch one."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries.seed_corpus.loader import BASELINE_PROFILES, PUBLIC_ALPHA_TARGETS, REQUIRED_HARD_QUERY_IDS
from runtime.surface import SurfaceKernel, SurfaceRequest


PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
OUTCOME_STATUSES = frozenset({"verified", "candidate", "need", "near_miss", "policy_blocked", "unavailable", "unknown"})
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


def batch_root() -> Path:
    return Path(__file__).resolve().parent


def family_root() -> Path:
    return batch_root().parent


def load_batch_manifest(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "batch_manifest.json")


def load_reviewed_seed_records(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "reviewed_seed_records.json")


def load_review_decision_backed_outcomes(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "review_decision_backed_outcomes.json")


def load_query_coverage(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "query_coverage.json")


def load_public_alpha_gate(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "public_alpha_gate.json")


def load_surface_projection_fixtures(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "surface_projection_fixtures.json")


def load_renderer_expected_outputs(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "renderer_expected_outputs.json")


def load_family_index(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or family_root()) / "index.json")


def load_family_public_alpha_gate(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or family_root()) / "public_alpha_gate.json")


def read_batch_text(name: str, root: Path | None = None) -> str:
    return ((root or batch_root()) / name).read_text(encoding="utf-8")


def reviewed_seed_record_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("reviewed_seed_records") or [] if isinstance(item, Mapping))


def outcome_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("outcomes") or [] if isinstance(item, Mapping))


def query_coverage_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("query_coverage") or [] if isinstance(item, Mapping))


def reviewed_corpus_counts(outcomes_payload: Mapping[str, Any]) -> dict[str, int]:
    counts = {
        "reviewed": 0,
        "review_decision_backed": 0,
        "candidate": 0,
        "need": 0,
        "near_miss": 0,
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
        elif status in {"candidate", "need", "near_miss", "policy_blocked", "unavailable"}:
            counts[status] += 1
        elif status != "verified":
            counts["unknown"] += 1
    return counts


def validate_batch_manifest(manifest: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if manifest.get("task_id") != "REVIEWED-CORPUS-SEED-BATCH-01":
        errors.append("manifest task_id must be REVIEWED-CORPUS-SEED-BATCH-01")
    if manifest.get("batch_id") != "batch_01":
        errors.append("manifest batch_id must be batch_01")
    outputs = manifest.get("required_outputs")
    if not isinstance(outputs, list):
        errors.append("manifest required_outputs must be a list")
    else:
        missing = [name for name in outputs if not (batch_root() / str(name)).exists()]
        if missing:
            errors.append(f"manifest outputs missing: {', '.join(missing)}")
    for flag in TRUTH_BOUNDARY_FLAGS:
        if manifest.get("truth_boundary", {}).get(flag) is not False:
            errors.append(f"manifest truth boundary flag must be false: {flag}")
    return tuple(errors)


def validate_reviewed_seed_records(records: Mapping[str, Any], outcomes: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    record_items = reviewed_seed_record_records(records)
    if len(record_items) != 2:
        errors.append("batch one must contain exactly two reviewed seed records")
    promote_outcomes = {
        str(item.get("reviewed_seed_record_id") or ""): item
        for item in outcome_records(outcomes or load_review_decision_backed_outcomes())
        if item.get("decision") == "promote"
    }
    for record in record_items:
        record_id = str(record.get("reviewed_seed_record_id") or "<missing>")
        if record_id not in promote_outcomes:
            errors.append(f"{record_id} must be backed by a promote outcome")
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
    if len(records) != len(REQUIRED_HARD_QUERY_IDS):
        errors.append("outcomes must cover exactly the six hard queries")
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
            if item.get("reviewed_seed_record_id") is not None or item.get("counts_as_reviewed") is not False:
                errors.append(f"{outcome_id} non-promote must not create reviewed record")
            if status == "verified":
                errors.append(f"{outcome_id} non-promote must not become verified")
        for flag in TRUTH_BOUNDARY_FLAGS:
            if item.get("truth_boundary", {}).get(flag) is not False:
                errors.append(f"{outcome_id} truth boundary flag must be false: {flag}")
    return tuple(errors)


def validate_query_coverage(coverage: Mapping[str, Any], outcomes: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    coverage_items = query_coverage_records(coverage)
    if len(coverage_items) != len(REQUIRED_HARD_QUERY_IDS):
        errors.append("query coverage must cover all six hard queries")
    outcome_by_query = {
        str(item.get("hard_query_id") or ""): item
        for item in outcome_records(outcomes or load_review_decision_backed_outcomes())
    }
    for item in coverage_items:
        query_id = str(item.get("hard_query_id") or "")
        outcome = outcome_by_query.get(query_id)
        if outcome is None:
            errors.append(f"{query_id or '<missing>'} has no matching outcome")
            continue
        if item.get("best_current_status") != outcome.get("outcome_status"):
            errors.append(f"{query_id} coverage status does not match outcome")
        if item.get("public_alpha_readiness") != "not_ready":
            errors.append(f"{query_id} must remain not_ready")
        if not item.get("next_required_action"):
            errors.append(f"{query_id} must include next_required_action")
    return tuple(errors)


def validate_public_alpha_gate(gate: Mapping[str, Any], outcomes: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    if gate.get("public_alpha_corpus_gate") != "FAIL_INSUFFICIENT_REVIEWED_CORPUS":
        errors.append("public alpha corpus gate must remain failed")
    counts = gate.get("counts")
    if not isinstance(counts, Mapping):
        return tuple(errors + ["gate counts must be present"])
    if outcomes is not None:
        computed = reviewed_corpus_counts(outcomes)
        for key, value in computed.items():
            count_key = f"{key}_count"
            if int(counts.get(count_key, -1)) != value:
                errors.append(f"{count_key} does not match outcomes")
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
    expected = payload.get("expected_status_by_query")
    if not isinstance(expected, Mapping):
        return tuple(errors + ["expected_status_by_query must be present"])
    outcomes_by_query = {
        str(item.get("hard_query_id") or ""): item
        for item in outcome_records(outcomes or load_review_decision_backed_outcomes())
    }
    for query_id, outcome in outcomes_by_query.items():
        if expected.get(query_id) != outcome.get("outcome_status"):
            errors.append(f"{query_id} expected status does not match outcome")
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
            data_version="reviewed-corpus-seed-batch-01",
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
            data_version="reviewed-corpus-seed-batch-01",
        )
    )


def _outcome_view_payload(outcome: Mapping[str, Any], *, public: bool) -> dict[str, Any]:
    payload = {
        "schema_version": "reviewed_corpus_outcome_view.v0",
        "id": _public_outcome_ref(outcome) if public else str(outcome.get("outcome_id") or "reviewed-corpus-outcome"),
        "title": str(outcome.get("title") or outcome.get("hard_query_id") or "Reviewed corpus outcome"),
        "summary": str(outcome.get("useful_unit") or outcome.get("rationale") or ""),
        "status": str(outcome.get("public_projection_status") or outcome.get("outcome_status") or "unknown"),
        "hard_query_id": str(outcome.get("hard_query_id") or ""),
        "public_review_ref": _public_outcome_ref(outcome),
        "evidence_posture": str(outcome.get("evidence_posture") or "review_decision_backed"),
        "known_gaps": _strings(outcome.get("known_gaps")),
        "next_required_action": str(outcome.get("public_next_action") or outcome.get("next_required_action") or ""),
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
        "schema_version": "reviewed_corpus_seed_record_view.v0",
        "id": str(record.get("reviewed_seed_record_id") or "reviewed-seed-record"),
        "title": str(record.get("title") or "Reviewed seed record"),
        "summary": str(record.get("summary") or ""),
        "status": str(record.get("canonical_status") or "unknown"),
        "hard_query_id": str(record.get("hard_query_id") or ""),
        "public_review_ref": f"reviewed_corpus_record_public_{record.get('hard_query_id', 'unknown')}",
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
    return f"reviewed_corpus_public_{outcome.get('hard_query_id', 'unknown')}"


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
