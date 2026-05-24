from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Protocol, Sequence


CREATED_AT = "2026-05-25T00:00:00Z"
DEFAULT_PROJECTION = "operator_workbench"

UNSAFE_BOUNDARY_FALSES = (
    "live_call_performed",
    "raw_response_committed",
    "source_cache_write_performed",
    "evidence_write_performed",
    "candidate_write_performed",
    "review_write_performed",
    "reviewed_index_mutated",
    "master_index_mutated",
    "operator_instance_mutated",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


class SourceActionPolicyError(ValueError):
    """Raised when a source action would cross a disabled policy boundary."""


class SourceActionAdapter(Protocol):
    adapter_id: str
    source_family: str
    supported_action_kinds: Sequence[str]
    supported_transport_modes: Sequence[str]

    def manifest(self) -> Mapping[str, Any]:
        ...

    def run_fixture(self, plan: Mapping[str, Any]) -> Mapping[str, Any]:
        ...

    def run_mock(self, plan: Mapping[str, Any]) -> Mapping[str, Any]:
        ...

    def normalize(self, transport_result: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


_ADAPTERS: dict[str, SourceActionAdapter] = {}


def stable_id(prefix: str, *parts: object) -> str:
    payload = json.dumps(parts, sort_keys=True, default=str)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def default_source_action_policy() -> dict[str, Any]:
    return {
        "schema_version": "source_action_policy.v0",
        "record_type": "source_action_policy",
        "created_at": CREATED_AT,
        "source_actions_are_not_truth": True,
        "source_actions_do_not_create_reviewed_records": True,
        "source_actions_do_not_mutate_master_index": True,
        "source_actions_do_not_mutate_public_index": True,
        "source_actions_do_not_mutate_operator_instance_by_default": True,
        "source_actions_require_policy_gate": True,
        "source_actions_require_boundary_report": True,
        "source_actions_require_source_family_manifest": True,
        "source_actions_require_capability_profile": True,
        "source_actions_require_rate_limit_policy": True,
        "source_actions_require_redaction_policy_for_live": True,
        "source_actions_require_transport_result_classification": True,
        "live_source_calls_enabled_by_default": False,
        "mock_transport_enabled": True,
        "fixture_transport_enabled": True,
        "live_transport_requires_operator_policy": True,
        "public_live_source_action_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def load_source_action_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_source_action_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    required = (
        "source_family",
        "display_name",
        "manifest_version",
        "adapter_id",
        "supported_action_kinds",
        "supported_transport_modes",
        "capability_profile_ref",
        "policy_ref",
        "fixture_refs",
        "live_policy_required",
        "default_enabled",
        "public_fanout_allowed",
        "downloads_allowed",
        "extraction_allowed",
        "review_required",
    )
    errors = [field for field in required if field not in manifest]
    for field in ("default_enabled", "public_fanout_allowed", "downloads_allowed", "extraction_allowed"):
        if manifest.get(field) is not False:
            errors.append(f"{field}_must_be_false")
    if manifest.get("review_required") is not True:
        errors.append("review_required_must_be_true")
    return {
        "schema_version": "source_action_manifest_validation.v0",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "source_family": manifest.get("source_family"),
        "adapter_id": manifest.get("adapter_id"),
    }


def register_source_action_adapter(adapter: SourceActionAdapter) -> dict[str, Any]:
    validation = validate_source_action_manifest(adapter.manifest())
    if validation["status"] != "pass":
        raise ValueError(f"invalid source action adapter manifest: {validation['errors']}")
    _ADAPTERS[adapter.source_family] = adapter
    return {
        "schema_version": "source_action_adapter_registration.v0",
        "record_type": "source_action_adapter_registration",
        "created_at": CREATED_AT,
        "source_family": adapter.source_family,
        "adapter_id": adapter.adapter_id,
        "registered": True,
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["registration-only"],
        "non_claims": source_action_non_claims(),
    }


def get_source_action_adapter(source_family: str) -> SourceActionAdapter:
    if source_family not in _ADAPTERS:
        raise KeyError(f"source action adapter is not registered: {source_family}")
    return _ADAPTERS[source_family]


def list_registered_source_action_adapters() -> list[str]:
    return sorted(_ADAPTERS)


def plan_source_action(
    query_context: str | Mapping[str, Any],
    source_family: str,
    action_kind: str,
    policy: Mapping[str, Any] | None = None,
    *,
    transport_mode: str = "fixture",
    projection_profile: str = DEFAULT_PROJECTION,
    dry_run: bool = True,
) -> dict[str, Any]:
    policy_payload = dict(policy or default_source_action_policy())
    query_payload = {"query": query_context} if isinstance(query_context, str) else dict(query_context)
    live_allowed = transport_mode == "operator_approved_live" and bool(
        policy_payload.get("live_source_calls_enabled_by_default")
    )
    blocked_reasons: list[str] = []
    if transport_mode == "operator_approved_live" and not live_allowed:
        blocked_reasons.append("live_transport_disabled_by_policy")
    if projection_profile in {"public_web", "native_desktop_read_only"} and transport_mode != "fixture":
        blocked_reasons.append("projection_is_read_only")
    return {
        "schema_version": "source_request_plan.v0",
        "record_type": "source_request_plan",
        "created_at": CREATED_AT,
        "request_plan_id": stable_id("source_request_plan", query_payload, source_family, action_kind, transport_mode),
        "source_family": source_family,
        "source_action_id": stable_id("source_action", query_payload, source_family, action_kind),
        "action_kind": action_kind,
        "query_context": query_payload,
        "request_budget": {"max_requests": 0 if dry_run else 1, "timeout_seconds": 5},
        "transport_mode": transport_mode,
        "rate_limit_policy_ref": "control/policies/source_action_rate_limit_policy.json",
        "redaction_policy_ref": "control/policies/source_action_transport_policy.json",
        "policy_ref": "control/policies/source_action_kernel_policy.json",
        "projection_profile": projection_profile,
        "live_allowed": live_allowed,
        "dry_run": dry_run,
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": blocked_reasons or ["fixture_or_mock_transport_only"],
        "blocked_reasons": blocked_reasons,
        "non_claims": source_action_non_claims(),
    }


def check_source_action_policy(plan: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    policy_payload = dict(policy or default_source_action_policy())
    blocked_reasons = list(plan.get("blocked_reasons", []))
    transport_mode = plan.get("transport_mode")
    if transport_mode == "fixture" and not policy_payload.get("fixture_transport_enabled", False):
        blocked_reasons.append("fixture_transport_disabled")
    if transport_mode == "mock_live" and not policy_payload.get("mock_transport_enabled", False):
        blocked_reasons.append("mock_transport_disabled")
    if transport_mode == "operator_approved_live":
        if not policy_payload.get("live_source_calls_enabled_by_default", False):
            blocked_reasons.append("live_source_calls_disabled_by_default")
        if plan.get("projection_profile") in {"public_web", "native_desktop_read_only"}:
            blocked_reasons.append("read_only_projection_cannot_run_live")
    if not policy_payload.get("source_actions_require_boundary_report", False):
        blocked_reasons.append("boundary_report_policy_missing")
    return {
        "schema_version": "source_action_policy_check.v0",
        "record_type": "source_action_policy_check",
        "created_at": CREATED_AT,
        "source_family": plan.get("source_family"),
        "source_action_id": plan.get("source_action_id"),
        "policy_ref": plan.get("policy_ref"),
        "projection_profile": plan.get("projection_profile"),
        "dry_run": plan.get("dry_run", True),
        "live_call_performed": False,
        "allowed": not blocked_reasons,
        "blocked_reasons": sorted(set(blocked_reasons)),
        "accepted_truth": False,
        "review_required": True,
        "limitations": sorted(set(blocked_reasons)) or ["policy_checked"],
        "non_claims": source_action_non_claims(),
    }


def run_source_action_fixture(plan: Mapping[str, Any], adapter: SourceActionAdapter) -> dict[str, Any]:
    payload = adapter.run_fixture(plan)
    records = list(payload.get("records", []))
    return source_transport_result(plan, "fixture", "completed", records)


def run_source_action_mock(plan: Mapping[str, Any], adapter: SourceActionAdapter) -> dict[str, Any]:
    payload = adapter.run_mock(plan)
    records = list(payload.get("records", []))
    return source_transport_result(plan, "mock_live", "completed", records)


def run_source_action_live(
    plan: Mapping[str, Any],
    adapter: SourceActionAdapter,
    operator_context: Mapping[str, Any] | None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del adapter
    policy_result = check_source_action_policy(plan, policy)
    if not operator_context or not policy_result["allowed"]:
        raise SourceActionPolicyError("operator-approved live source action is disabled by policy")
    raise SourceActionPolicyError("live source action transport is not implemented in SOURCE-ACTION-KERNEL-00")


def source_transport_result(
    plan: Mapping[str, Any],
    transport_mode: str,
    status: str,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "source_transport_result.v0",
        "record_type": "source_transport_result",
        "created_at": CREATED_AT,
        "transport_result_id": stable_id("source_transport_result", plan.get("request_plan_id"), transport_mode),
        "request_plan_id": plan.get("request_plan_id"),
        "source_family": plan.get("source_family"),
        "source_action_id": plan.get("source_action_id"),
        "policy_ref": plan.get("policy_ref"),
        "projection_profile": plan.get("projection_profile"),
        "dry_run": plan.get("dry_run", True),
        "transport_mode": transport_mode,
        "status": status,
        "total_requests": 0,
        "rate_limited": False,
        "tls_error": False,
        "response_summary_ref": stable_id("source_response_summary", plan.get("request_plan_id"), len(records)),
        "raw_response_persisted": False,
        "redacted_summary_available": True,
        "normalized_preview_available": True,
        "records": list(records),
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["fixture_or_mock_summary_only"],
        "non_claims": source_action_non_claims(),
    }


def normalize_source_action_result(
    transport_result: Mapping[str, Any],
    adapter: SourceActionAdapter,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del policy
    normalized = adapter.normalize(transport_result)
    observations = list(normalized.get("observations", []))
    return {
        "schema_version": "source_normalizer_result.v0",
        "record_type": "source_normalizer_result",
        "created_at": CREATED_AT,
        "normalizer_result_id": stable_id("source_normalizer_result", transport_result.get("transport_result_id")),
        "source_family": transport_result.get("source_family"),
        "source_action_id": transport_result.get("source_action_id"),
        "policy_ref": transport_result.get("policy_ref"),
        "projection_profile": transport_result.get("projection_profile"),
        "dry_run": transport_result.get("dry_run", True),
        "transport_result_id": transport_result.get("transport_result_id"),
        "observation_count": len(observations),
        "observations": observations,
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["normalized_fixture_or_mock_records"],
        "non_claims": source_action_non_claims(),
    }


def build_source_observation_envelope(
    normalized_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del policy
    observations = list(normalized_result.get("observations", []))
    return {
        "schema_version": "source_observation_envelope.v0",
        "record_type": "source_observation_envelope",
        "created_at": CREATED_AT,
        "observation_envelope_id": stable_id("source_observation_envelope", normalized_result.get("normalizer_result_id")),
        "source_family": normalized_result.get("source_family"),
        "source_action_id": normalized_result.get("source_action_id"),
        "policy_ref": normalized_result.get("policy_ref"),
        "projection_profile": normalized_result.get("projection_profile"),
        "dry_run": normalized_result.get("dry_run", True),
        "observations": observations,
        "observation_count": len(observations),
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["observation_envelope_is_not_truth"],
        "non_claims": source_action_non_claims(),
    }


def build_source_cache_mapping_plan(
    observation: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del policy
    return build_mapping_plan("source_cache_mapping_plan", observation, "source_cache_record_plan")


def build_evidence_candidate_mapping_plan(
    observation: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del policy
    return build_mapping_plan("evidence_candidate_mapping_plan", observation, "evidence_candidate_plan")


def build_candidate_mapping_plan(
    observation: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del policy
    return build_mapping_plan("candidate_mapping_plan", observation, "candidate_record_plan")


def build_mapping_plan(kind: str, observation: Mapping[str, Any], mapping_type: str) -> dict[str, Any]:
    return {
        "schema_version": f"{kind}.v0",
        "record_type": kind,
        "created_at": CREATED_AT,
        f"{kind}_id": stable_id(kind, observation.get("observation_envelope_id"), mapping_type),
        "source_family": observation.get("source_family"),
        "source_action_id": observation.get("source_action_id"),
        "policy_ref": observation.get("policy_ref"),
        "projection_profile": observation.get("projection_profile"),
        "dry_run": observation.get("dry_run", True),
        "mapping_type": mapping_type,
        "planned_records": list(observation.get("observations", [])),
        "write_performed": False,
        "store_mutation_performed": False,
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["mapping_plan_only_no_store_mutation"],
        "non_claims": source_action_non_claims(),
    }


def build_review_handoff_plan(
    candidate_plan: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del policy
    planned_records = list(candidate_plan.get("planned_records", []))
    return {
        "schema_version": "review_handoff_plan.v0",
        "record_type": "review_handoff_plan",
        "created_at": CREATED_AT,
        "review_handoff_plan_id": stable_id("review_handoff_plan", candidate_plan.get("candidate_mapping_plan_id")),
        "source_family": candidate_plan.get("source_family"),
        "source_action_id": candidate_plan.get("source_action_id"),
        "policy_ref": candidate_plan.get("policy_ref"),
        "projection_profile": candidate_plan.get("projection_profile"),
        "dry_run": candidate_plan.get("dry_run", True),
        "candidate_count": len(planned_records),
        "review_item_plan_count": len(planned_records),
        "review_acceptance_performed": False,
        "promotion_performed": False,
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["review_handoff_is_not_review_acceptance"],
        "non_claims": source_action_non_claims(),
    }


def build_result_lane_projection_plan(
    candidate_plan: Mapping[str, Any],
    projection_profile: str = DEFAULT_PROJECTION,
) -> dict[str, Any]:
    planned_records = list(candidate_plan.get("planned_records", []))
    lanes = [
        {
            "lane_kind": "local_candidate_results",
            "item_count": len(planned_records),
            "source_family": candidate_plan.get("source_family"),
        },
        {
            "lane_kind": "blocked_actions",
            "item_count": 1,
            "blocked": ["live_source_call", "download", "extraction", "review_acceptance"],
        },
    ]
    if candidate_plan.get("source_family") == "fixture_source_action":
        lanes.insert(0, {"lane_kind": "source_cache_hits", "item_count": len(planned_records)})
    return {
        "schema_version": "result_lane_projection_plan.v0",
        "record_type": "result_lane_projection_plan",
        "created_at": CREATED_AT,
        "lane_projection_plan_id": stable_id("result_lane_projection_plan", candidate_plan.get("source_action_id")),
        "source_family": candidate_plan.get("source_family"),
        "source_action_id": candidate_plan.get("source_action_id"),
        "policy_ref": candidate_plan.get("policy_ref"),
        "projection_profile": projection_profile,
        "dry_run": candidate_plan.get("dry_run", True),
        "lanes": lanes,
        "lane_count": len(lanes),
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["lane_projection_plan_only"],
        "non_claims": source_action_non_claims(),
    }


def update_source_rate_limit_ledger(
    plan: Mapping[str, Any],
    transport_result: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "source_rate_limit_ledger.v0",
        "record_type": "source_rate_limit_ledger",
        "created_at": CREATED_AT,
        "rate_limit_ledger_id": stable_id("source_rate_limit_ledger", plan.get("source_family")),
        "source_family": plan.get("source_family"),
        "source_action_id": plan.get("source_action_id"),
        "policy_ref": plan.get("policy_ref"),
        "projection_profile": plan.get("projection_profile"),
        "dry_run": plan.get("dry_run", True),
        "total_requests": transport_result.get("total_requests", 0),
        "rate_limited": transport_result.get("rate_limited", False),
        "retry_after_respected": True,
        "kill_switch_required": True,
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["fixture_transport_has_zero_remote_requests"],
        "non_claims": source_action_non_claims(),
    }


def build_source_backoff_decision(plan: Mapping[str, Any], transport_result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "source_backoff_decision.v0",
        "record_type": "source_backoff_decision",
        "created_at": CREATED_AT,
        "source_family": plan.get("source_family"),
        "source_action_id": plan.get("source_action_id"),
        "policy_ref": plan.get("policy_ref"),
        "projection_profile": plan.get("projection_profile"),
        "dry_run": plan.get("dry_run", True),
        "backoff_required": bool(transport_result.get("rate_limited")),
        "retry_after_seconds": 0,
        "reason": "no_backoff_for_fixture_transport",
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["backoff_decision_only"],
        "non_claims": source_action_non_claims(),
    }


def build_source_action_boundary_report(source_action_run: Mapping[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_version": "source_action_boundary_report.v0",
        "record_type": "source_action_boundary_report",
        "created_at": CREATED_AT,
        "boundary_report_id": stable_id("source_action_boundary_report", source_action_run.get("source_action_run_id")),
        "source_action_run_id": source_action_run.get("source_action_run_id"),
        "source_family": source_action_run.get("source_family"),
        "source_action_id": source_action_run.get("source_action_id"),
        "policy_ref": source_action_run.get("policy_ref"),
        "projection_profile": source_action_run.get("projection_profile"),
        "dry_run": source_action_run.get("dry_run", True),
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["boundary_report_for_fixture_or_mock_source_action"],
        "non_claims": source_action_non_claims(),
    }
    for field in UNSAFE_BOUNDARY_FALSES:
        report[field] = False
    return report


def build_source_action_scorecard(
    source_family: str,
    observations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    observation_count = len(observations)
    return {
        "schema_version": "source_action_scorecard.v0",
        "record_type": "source_action_scorecard",
        "created_at": CREATED_AT,
        "source_family": source_family,
        "source_action_id": stable_id("source_action_scorecard", source_family, observation_count),
        "policy_ref": "control/policies/source_action_kernel_policy.json",
        "projection_profile": DEFAULT_PROJECTION,
        "dry_run": True,
        "dimensions": {
            "metadata_quality": "fixture-high" if observation_count else "fixture-empty",
            "provenance_quality": "fixture",
            "identifier_richness": "sample",
            "locator_stability": "stable-fixture",
            "false_positive_rate": "not-measured",
            "accepted_evidence_yield": "not-measured",
            "rights_risk": "not-assessed",
            "safety_risk": "low-fixture-only",
            "rate_limit_reliability": "not-applicable-fixture",
            "domain_coverage": "fixture-only",
        },
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["scorecard_is_fixture_only"],
        "non_claims": source_action_non_claims(),
    }


def run_source_action(
    *,
    query: str,
    source_family: str = "fixture_source_action",
    action_kind: str = "metadata_search",
    transport_mode: str = "fixture",
    projection_profile: str = DEFAULT_PROJECTION,
    dry_run: bool = True,
    policy: Mapping[str, Any] | None = None,
    adapter: SourceActionAdapter | None = None,
) -> dict[str, Any]:
    adapter = adapter or get_source_action_adapter(source_family)
    plan = plan_source_action(
        query,
        source_family,
        action_kind,
        policy,
        transport_mode=transport_mode,
        projection_profile=projection_profile,
        dry_run=dry_run,
    )
    policy_result = check_source_action_policy(plan, policy)
    if not policy_result["allowed"]:
        run = empty_source_action_run(plan, policy_result, status="blocked_by_policy")
        run["boundary_report"] = build_source_action_boundary_report(run)
        return run
    if transport_mode == "fixture":
        transport_result = run_source_action_fixture(plan, adapter)
    elif transport_mode == "mock_live":
        transport_result = run_source_action_mock(plan, adapter)
    else:
        raise SourceActionPolicyError("live source actions are disabled in SOURCE-ACTION-KERNEL-00")
    normalized = normalize_source_action_result(transport_result, adapter, policy)
    observation = build_source_observation_envelope(normalized, policy)
    source_cache_plan = build_source_cache_mapping_plan(observation, policy)
    evidence_plan = build_evidence_candidate_mapping_plan(observation, policy)
    candidate_plan = build_candidate_mapping_plan(observation, policy)
    review_handoff = build_review_handoff_plan(candidate_plan, policy)
    lane_projection = build_result_lane_projection_plan(candidate_plan, projection_profile)
    rate_limit = update_source_rate_limit_ledger(plan, transport_result)
    backoff = build_source_backoff_decision(plan, transport_result)
    scorecard = build_source_action_scorecard(source_family, observation.get("observations", []))
    run: dict[str, Any] = {
        "schema_version": "source_action_run.v0",
        "record_type": "source_action_run",
        "created_at": CREATED_AT,
        "source_action_run_id": stable_id("source_action_run", plan["request_plan_id"], transport_mode),
        "source_family": source_family,
        "source_action_id": plan["source_action_id"],
        "policy_ref": plan["policy_ref"],
        "projection_profile": projection_profile,
        "dry_run": dry_run,
        "status": "completed",
        "request_plan": plan,
        "policy_result": policy_result,
        "transport_result": transport_result,
        "normalizer_result": normalized,
        "source_observation_envelope": observation,
        "source_cache_mapping_plan": source_cache_plan,
        "evidence_candidate_mapping_plan": evidence_plan,
        "candidate_mapping_plan": candidate_plan,
        "review_handoff_plan": review_handoff,
        "result_lane_projection_plan": lane_projection,
        "source_rate_limit_ledger": rate_limit,
        "source_backoff_decision": backoff,
        "scorecard": scorecard,
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["source_action_outputs_are_plans_not_truth"],
        "non_claims": source_action_non_claims(),
    }
    run["boundary_report"] = build_source_action_boundary_report(run)
    return run


def empty_source_action_run(
    plan: Mapping[str, Any],
    policy_result: Mapping[str, Any],
    *,
    status: str,
) -> dict[str, Any]:
    run: dict[str, Any] = {
        "schema_version": "source_action_run.v0",
        "record_type": "source_action_run",
        "created_at": CREATED_AT,
        "source_action_run_id": stable_id("source_action_run", plan.get("request_plan_id"), status),
        "source_family": plan.get("source_family"),
        "source_action_id": plan.get("source_action_id"),
        "policy_ref": plan.get("policy_ref"),
        "projection_profile": plan.get("projection_profile"),
        "dry_run": plan.get("dry_run", True),
        "status": status,
        "request_plan": dict(plan),
        "policy_result": dict(policy_result),
        "transport_result": None,
        "normalizer_result": None,
        "source_observation_envelope": None,
        "source_cache_mapping_plan": None,
        "evidence_candidate_mapping_plan": None,
        "candidate_mapping_plan": None,
        "review_handoff_plan": None,
        "result_lane_projection_plan": None,
        "source_rate_limit_ledger": None,
        "source_backoff_decision": None,
        "scorecard": None,
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": list(policy_result.get("blocked_reasons", [])),
        "non_claims": source_action_non_claims(),
    }
    return run


def source_action_non_claims() -> list[str]:
    return [
        "not_truth",
        "not_review_acceptance",
        "not_reviewed_index_mutation",
        "not_master_or_public_index_mutation",
        "not_public_live_fanout",
        "not_download_or_extraction",
        "not_production_or_public_launch_readiness",
    ]


def redact_run_for_cli(run: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(run)
    # Keep this hook explicit so future live adapters have one safe place to redact.
    payload["operator_context_redacted"] = True
    return payload


def write_json_if_requested(payload: Mapping[str, Any], output: str | None) -> None:
    if not output:
        return
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def reset_source_action_registry_for_tests() -> None:
    _ADAPTERS.clear()


def merge_policy(base: Mapping[str, Any] | None, override: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result: MutableMapping[str, Any] = dict(default_source_action_policy())
    if base:
        result.update(base)
    if override:
        result.update(override)
    return dict(result)
