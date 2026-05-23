"""Policy-gated Internet Archive live metadata lane for resolution runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from runtime.resolution_run.run_store import FIXED_CREATED_AT, stable_id
from runtime.source.observation.internet_archive_live_probe import (
    load_live_probe_policy,
    run_live_metadata_probe,
)
from runtime.source.observation.internet_archive_metadata import default_boundary_flags
from runtime.source.observation.internet_archive_normalization import normalize_ia_metadata_fixture


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_POLICY_PATH = REPO_ROOT / "control" / "policies" / "ia_live_metadata_lane_policy.json"

PROJECTION_PROFILES = ("operator_workbench", "public_web", "native_desktop_read_only")
IA_LIVE_COMMANDS = (
    "request_live_ia_metadata",
    "approve_live_ia_metadata",
    "run_live_ia_metadata_dry_run",
    "run_live_ia_metadata_mock",
    "run_live_ia_metadata_now",
    "cancel_live_ia_metadata",
    "inspect_live_ia_metadata_result",
)
REQUIRED_EVENT_TYPES = (
    "ia_live_metadata.requested",
    "ia_live_metadata.policy_checked",
    "ia_live_metadata.approved",
    "ia_live_metadata.blocked",
    "ia_live_metadata.started",
    "ia_live_metadata.request_succeeded",
    "ia_live_metadata.request_failed",
    "ia_live_metadata.rate_limited",
    "ia_live_metadata.tls_failed",
    "ia_live_metadata.normalized",
    "ia_live_metadata.candidates_projected",
    "ia_live_metadata.completed",
    "ia_live_metadata.cancelled",
)
BLOCKED_LIVE_ACTIONS = (
    "public_live_ia_metadata",
    "native_live_ia_metadata",
    "download",
    "upload",
    "extract",
    "execute",
    "call_model_provider",
    "mutate_operator_instance",
    "mutate_master_index",
    "commit_raw_response",
)


def load_ia_live_metadata_lane_policy(path: str | Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    """Load the lane policy, returning the fail-closed default if absent during early tests."""
    policy_path = Path(path)
    if not policy_path.exists():
        return default_ia_live_metadata_lane_policy()
    return json.loads(policy_path.read_text(encoding="utf-8"))


def default_ia_live_metadata_lane_policy() -> dict[str, Any]:
    return {
        "schema_version": "ia_live_metadata_lane_policy.v0",
        "live_ia_metadata_enabled_by_default": False,
        "live_ia_metadata_requires_operator_command": True,
        "live_ia_metadata_requires_operator_token": True,
        "live_ia_metadata_requires_policy_gate": True,
        "public_live_ia_metadata_enabled": False,
        "native_live_ia_metadata_enabled": False,
        "live_ia_max_requests_default": 2,
        "live_ia_timeout_seconds_default": 15,
        "live_ia_rows_default": 5,
        "live_ia_raw_response_commit_allowed": False,
        "live_ia_redacted_summary_allowed": True,
        "live_ia_normalized_preview_allowed": True,
        "source_cache_write_default": False,
        "evidence_write_default": False,
        "candidate_write_default": False,
        "reviewed_index_write_default": False,
        "operator_instance_mutation_default": False,
        "temp_instance_write_allowed_if_explicit": True,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_enabled": False,
        "master_index_mutation_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "full_archive_org_integration_claimed": False,
    }


def plan_ia_live_metadata_lane(
    run: Mapping[str, Any],
    query: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Plan the lane as blocked/pending approval by default."""
    merged_policy = _policy(policy)
    run_id = str(run.get("run_id", ""))
    policy_decision = _policy_decision("request_live_ia_metadata", "operator_workbench", merged_policy)
    events = [
        _event(run_id, "ia_live_metadata.requested", "IA live metadata lane is visible but requires operator approval."),
        _event(run_id, "ia_live_metadata.policy_checked", "IA live metadata policy checked; live access is disabled by default."),
        _event(run_id, "ia_live_metadata.blocked", "IA live metadata is blocked pending operator approval and token."),
    ]
    return _lane_result(
        run_id=run_id,
        query=query,
        state="blocked_pending_operator_approval",
        mode="planned",
        command_type="request_live_ia_metadata",
        allowed=False,
        policy_decision=policy_decision,
        events=events,
        normalized_candidates=[],
        redacted_summary={},
        live_ia_call_performed=False,
        source_probe_executed=False,
        total_http_requests=0,
        raw_response_committed=False,
    )


def request_ia_live_metadata_lane(
    run_id: str,
    command: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a request/approval decision for an IA live metadata command."""
    command_type = str(command.get("command_type") or "request_live_ia_metadata")
    projection_profile = _projection_profile(str(command.get("projection_profile") or "operator_workbench"))
    query = str(command.get("query") or "sampleproject")
    merged_policy = _policy(policy)
    decision = _policy_decision(command_type, projection_profile, merged_policy, command)
    events = [
        _event(run_id, "ia_live_metadata.requested", f"Command requested: {command_type}."),
        _event(run_id, "ia_live_metadata.policy_checked", "IA live metadata lane policy gate evaluated."),
    ]
    if decision["allowed"]:
        events.append(_event(run_id, "ia_live_metadata.approved", "Operator-scoped IA metadata command is approved."))
    else:
        events.append(_event(run_id, "ia_live_metadata.blocked", "IA live metadata command was blocked by policy."))
    return _lane_result(
        run_id=run_id,
        query=query,
        state="approved_pending_run" if decision["allowed"] else _blocked_state_for_projection(projection_profile),
        mode="requested",
        command_type=command_type,
        allowed=decision["allowed"],
        policy_decision=decision,
        events=events,
        normalized_candidates=[],
        redacted_summary={},
        live_ia_call_performed=False,
        source_probe_executed=False,
        total_http_requests=0,
        raw_response_committed=False,
    )


def approve_ia_live_metadata_lane(
    run_id: str,
    operator_context: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    command = dict(operator_context)
    command["command_type"] = "approve_live_ia_metadata"
    return request_ia_live_metadata_lane(run_id, command, policy)


def run_ia_live_metadata_lane_dry_run(
    run_id: str,
    query: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a dry-run lane path with no network or source probe."""
    merged_policy = _policy(policy)
    decision = _policy_decision(
        "run_live_ia_metadata_dry_run",
        "operator_workbench",
        merged_policy,
        {"dry_run": True, "operator_approved": True},
    )
    events = [
        _event(run_id, "ia_live_metadata.requested", "IA live metadata dry-run requested."),
        _event(run_id, "ia_live_metadata.policy_checked", "Dry-run path does not require network access."),
        _event(run_id, "ia_live_metadata.approved", "Dry-run IA metadata command approved by policy."),
        _event(run_id, "ia_live_metadata.started", "Dry-run IA metadata lane started."),
        _event(run_id, "ia_live_metadata.completed", "Dry-run IA metadata lane completed without source access."),
    ]
    return _lane_result(
        run_id=run_id,
        query=query,
        state="approved_pending_run",
        mode="dry_run",
        command_type="run_live_ia_metadata_dry_run",
        allowed=decision["allowed"],
        policy_decision=decision,
        events=events,
        normalized_candidates=[],
        redacted_summary={
            "schema_version": "ia_live_metadata_redacted_summary.v0",
            "query": query,
            "probe_status": "dry_run",
            "total_http_requests": 0,
            "raw_response_committed": False,
        },
        live_ia_call_performed=False,
        source_probe_executed=False,
        total_http_requests=0,
        raw_response_committed=False,
    )


def run_ia_live_metadata_lane_mock(
    run_id: str,
    query: str,
    mock_transport: Callable[..., Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run deterministic mock-live normalization with no network."""
    merged_policy = _policy(policy)
    decision = _policy_decision(
        "run_live_ia_metadata_mock",
        "operator_workbench",
        merged_policy,
        {"mock_live": True, "operator_approved": True},
    )
    fixture = dict(mock_transport(query=query) if mock_transport else _mock_metadata_fixture(query))
    normalized = normalize_ia_live_metadata_response(fixture, merged_policy)
    candidates = project_ia_live_metadata_candidates(run_id, normalized, "operator_workbench")
    events = [
        _event(run_id, "ia_live_metadata.requested", "IA live metadata mock-live requested."),
        _event(run_id, "ia_live_metadata.policy_checked", "Mock-live path uses deterministic fixture transport."),
        _event(run_id, "ia_live_metadata.approved", "Mock-live IA metadata command approved by policy."),
        _event(run_id, "ia_live_metadata.started", "Mock-live IA metadata lane started."),
        _event(run_id, "ia_live_metadata.request_succeeded", "Mock-live metadata response received from fixture transport."),
        _event(run_id, "ia_live_metadata.normalized", "Mock-live metadata response normalized and redacted."),
        _event(run_id, "ia_live_metadata.candidates_projected", "IA metadata candidates projected into result lanes."),
        _event(run_id, "ia_live_metadata.completed", "Mock-live IA metadata lane completed."),
    ]
    return _lane_result(
        run_id=run_id,
        query=query,
        state="candidates_available" if candidates else "completed",
        mode="mock_live",
        command_type="run_live_ia_metadata_mock",
        allowed=decision["allowed"],
        policy_decision=decision,
        events=events,
        normalized_candidates=candidates,
        redacted_summary=_redacted_summary(query, normalized, "mock_live"),
        live_ia_call_performed=False,
        source_probe_executed=False,
        total_http_requests=0,
        raw_response_committed=False,
    )


def run_ia_live_metadata_lane_live(
    run_id: str,
    query: str,
    transport: Any = None,
    policy: Mapping[str, Any] | None = None,
    *,
    operator_token: str = "",
    allow_live: bool = False,
    max_requests: int = 2,
    rows: int = 5,
    timeout_seconds: int = 15,
) -> dict[str, Any]:
    """Run the optional live path only after explicit approval and policy gates."""
    merged_policy = _policy(policy)
    command = {
        "operator_token": operator_token,
        "allow_live": allow_live,
        "max_requests": max_requests,
        "rows": rows,
        "timeout_seconds": timeout_seconds,
        "operator_approved": True,
    }
    decision = _policy_decision("run_live_ia_metadata_now", "operator_workbench", merged_policy, command)
    if not decision["allowed"]:
        result = request_ia_live_metadata_lane(
            run_id,
            {"command_type": "run_live_ia_metadata_now", "query": query, **command},
            merged_policy,
        )
        result["state"] = "blocked_pending_operator_approval"
        return result

    probe_policy = _live_probe_policy_from_lane_policy(merged_policy, rows=rows, max_requests=max_requests, timeout_seconds=timeout_seconds)
    transport_factory = transport if callable(transport) else None
    events = [
        _event(run_id, "ia_live_metadata.requested", "Approved IA live metadata command requested."),
        _event(run_id, "ia_live_metadata.policy_checked", "Live IA metadata policy gate passed."),
        _event(run_id, "ia_live_metadata.approved", "Operator token and live approval were provided."),
        _event(run_id, "ia_live_metadata.started", "Live IA metadata request started."),
    ]
    try:
        report = run_live_metadata_probe(
            probe_policy,
            approve_live=True,
            dry_run=False,
            query=query,
            rows=min(rows, int(probe_policy["metadata_search_rows_max"])),
            max_requests=min(max_requests, int(probe_policy["total_http_requests_max"])),
            client_label="EurekaLocalWorkbenchLiveMetadataLane/0",
            contact="local-operator-approved",
            kill_switch_enabled=True,
            transport_factory=transport_factory,
        )
        summary = dict(report.get("redacted_summary") or {})
        boundary = dict(report.get("boundary_report") or {})
        normalized = [dict(item) for item in report.get("normalized_preview") or []]
        candidates = project_ia_live_metadata_candidates(run_id, normalized, "operator_workbench")
        status = str(summary.get("probe_status", "succeeded"))
        if status == "rate_limited":
            events.append(_event(run_id, "ia_live_metadata.rate_limited", "IA live metadata request was rate-limited."))
            state = "rate_limited"
        elif status == "failed" and str(summary.get("failure_reason", "")).startswith("ssl"):
            events.append(_event(run_id, "ia_live_metadata.tls_failed", "IA live metadata TLS validation failed."))
            state = "tls_failed"
        elif status == "failed":
            events.append(_event(run_id, "ia_live_metadata.request_failed", "IA live metadata request failed."))
            state = "failed"
        else:
            events.append(_event(run_id, "ia_live_metadata.request_succeeded", "IA live metadata request succeeded."))
            state = "candidates_available" if candidates else "completed"
        events.extend(
            [
                _event(run_id, "ia_live_metadata.normalized", "IA live metadata response normalized and redacted."),
                _event(run_id, "ia_live_metadata.candidates_projected", "IA metadata candidates projected into result lanes."),
                _event(run_id, "ia_live_metadata.completed", "IA live metadata lane completed."),
            ]
        )
        return _lane_result(
            run_id=run_id,
            query=query,
            state=state,
            mode="live",
            command_type="run_live_ia_metadata_now",
            allowed=True,
            policy_decision=decision,
            events=events,
            normalized_candidates=candidates,
            redacted_summary=summary,
            live_ia_call_performed=bool(boundary.get("live_source_call_performed", False)),
            source_probe_executed=bool(boundary.get("source_probe_executed", False)),
            total_http_requests=int(summary.get("total_http_requests", 0) or 0),
            raw_response_committed=False,
        )
    except Exception as exc:  # pragma: no cover - defensive optional live path
        reason = str(exc)
        event_type = "ia_live_metadata.tls_failed" if "ssl" in reason.lower() or "certificate" in reason.lower() else "ia_live_metadata.request_failed"
        events.append(_event(run_id, event_type, "IA live metadata request failed before candidate projection."))
        return _lane_result(
            run_id=run_id,
            query=query,
            state="tls_failed" if event_type.endswith("tls_failed") else "failed",
            mode="live",
            command_type="run_live_ia_metadata_now",
            allowed=True,
            policy_decision=decision,
            events=events,
            normalized_candidates=[],
            redacted_summary={
                "schema_version": "ia_live_metadata_redacted_summary.v0",
                "probe_status": "failed",
                "failure_reason": "transport_failure",
                "failure_class": type(exc).__name__,
                "total_http_requests": 0,
                "raw_response_committed": False,
            },
            live_ia_call_performed=False,
            source_probe_executed=False,
            total_http_requests=0,
            raw_response_committed=False,
        )


def normalize_ia_live_metadata_response(response: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Normalize a mock/live metadata response into candidate-only preview records."""
    _ = _policy(policy)
    if response.get("schema_version") == "ia_live_probe_report.v0":
        return [dict(item) for item in response.get("normalized_preview", []) or []]
    fixture = {
        "fixture_id": str(response.get("fixture_id") or "ia_live_metadata_mock_fixture"),
        "fixture_class": str(response.get("fixture_class") or "metadata_search_small"),
        "endpoint_class": str(response.get("endpoint_class") or "metadata_search_small"),
        "request": dict(response.get("request") or {}),
        "payload": dict(response.get("payload") or response),
    }
    record = normalize_ia_metadata_fixture(fixture)
    payload = record.to_dict()
    payload["source_kind"] = "ia_live_metadata_lane_preview"
    payload["raw_response_committed"] = False
    return [payload]


def project_ia_live_metadata_candidates(
    run_id: str,
    normalized: Sequence[Mapping[str, Any]],
    projection_profile: str,
) -> list[dict[str, Any]]:
    """Project normalized records into provisional lane items."""
    profile = _projection_profile(projection_profile)
    candidates: list[dict[str, Any]] = []
    for index, record in enumerate(normalized):
        title = str(record.get("title_candidate") or record.get("observation_kind") or "Internet Archive metadata candidate")
        identifier = str(record.get("item_identifier") or "")
        item = {
            "item_id": stable_id("ia_live_candidate", {"run_id": run_id, "index": index, "title": title, "identifier": identifier}),
            "title": title if profile == "operator_workbench" else "Internet Archive metadata candidate",
            "summary": "Provisional Internet Archive metadata candidate; review required before downstream use.",
            "source_mapping": "internet_archive_metadata_live_lane",
            "truth_level": "candidate_not_truth",
            "review_required": True,
            "accepted_truth": False,
            "confidence": float(record.get("confidence", 0.0) or 0.0),
            "limitations": list(record.get("limitations") or []) + ["Live metadata lane output does not create evidence or reviewed records."],
            "risk_flags": list(record.get("risk_flags") or []),
            "rights_flags": list(record.get("rights_flags") or []),
            "blocked_actions": list(BLOCKED_LIVE_ACTIONS),
            "provenance": {
                "source_family": "internet_archive_metadata",
                "source_kind": "ia_live_metadata_lane_preview",
                "source_probe_executed": False,
                "store_mutation_performed": False,
            },
        }
        if profile == "operator_workbench":
            item["identifier_present"] = bool(identifier)
            item["observation_id"] = str(record.get("observation_id", ""))
            item["mediatype_candidate"] = str(record.get("mediatype_candidate", ""))
            item["collection_candidate_count"] = len(record.get("collection_candidates", []) or [])
        candidates.append(item)
    return candidates


def build_ia_live_metadata_lane_events(run_id: str, state: str) -> list[dict[str, Any]]:
    return [_event(run_id, "ia_live_metadata.policy_checked", f"IA live metadata lane state: {state}.")]


def build_ia_live_metadata_lane_boundary_report(run_id: str, result: Mapping[str, Any]) -> dict[str, Any]:
    flags = default_boundary_flags()
    flags["live_source_call_performed"] = bool(result.get("live_ia_call_performed", False))
    flags["source_probe_executed"] = bool(result.get("source_probe_executed", False))
    return {
        "schema_version": "ia_live_metadata_lane_boundary_report.v0",
        "run_id": run_id,
        "raw_response_committed": bool(result.get("raw_response_committed", False)),
        "live_smoke_total_http_requests": int(result.get("total_http_requests", 0) or 0),
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "operator_instance_mutated": False,
        "full_archive_org_integration_claimed": False,
        **flags,
    }


def build_ia_live_metadata_lane_packet(result: Mapping[str, Any], projection_profile: str) -> dict[str, Any]:
    """Build a Workbench result lane packet for the IA live metadata state."""
    profile = _projection_profile(projection_profile)
    state = str(result.get("state", "blocked_pending_operator_approval"))
    candidates = [
        dict(item)
        for item in result.get("normalized_candidates", []) or []
        if isinstance(item, Mapping)
    ]
    if profile != "operator_workbench":
        state = "unavailable"
        candidates = []
    items: list[dict[str, Any]]
    if candidates:
        items = candidates
    else:
        items = [
            {
                "item_id": stable_id("ia_live_metadata_lane_state", {"run_id": result.get("run_id"), "profile": profile, "state": state}),
                "title": "Internet Archive metadata lane",
                "summary": _lane_summary(state, profile),
                "truth_level": "candidate_not_truth",
                "review_required": True,
                "accepted_truth": False,
                "blocked_actions": list(BLOCKED_LIVE_ACTIONS),
                "limitations": [
                    "Live IA metadata is policy-gated and blocked unless explicitly approved.",
                    "No downloads, extraction, raw response commit, evidence creation, or index mutation is allowed.",
                ],
            }
        ]
    return {
        "schema_version": "result_lane_packet.v0",
        "packet_type": "ResultLanePacket",
        "lane_id": "lane-ia_live_metadata",
        "lane_kind": "ia_live_metadata_candidates",
        "state": state,
        "projection_profile": profile,
        "visible": True,
        "result_count": len(candidates),
        "items": items,
        "blocked_actions": list(BLOCKED_LIVE_ACTIONS),
        "action_posture": {
            "can_view": True,
            "can_inspect": profile == "operator_workbench",
            "can_review": False,
            "can_download": False,
            "can_extract": False,
            "can_call_model": False,
            "can_rebuild_index": False,
            "blocked_actions": list(BLOCKED_LIVE_ACTIONS),
            "policy_reasons": [
                "Live IA metadata requires explicit operator approval.",
                "Public and native projections are read-only and cannot run live source actions.",
            ],
        },
        "source_mapping": "internet_archive_metadata_live_lane",
        "provenance": {
            "source_family": "internet_archive_metadata",
            "live_ia_call_performed": bool(result.get("live_ia_call_performed", False)),
            "source_probe_executed": bool(result.get("source_probe_executed", False)),
            "store_mutation_performed": False,
        },
        "truth_level": "candidate_not_truth",
        "accepted_truth": False,
        "review_required": True,
        "limitations": [
            "IA live metadata lane output is candidate-only.",
            "It is not full Archive.org integration and does not create accepted evidence.",
        ],
        "uncertainty": [
            "Metadata availability and identity require review.",
            "Rights, safety, compatibility, and installability are not inferred.",
        ],
    }


def ensure_ia_live_metadata_lane_in_snapshot(
    snapshot: Mapping[str, Any],
    lane_result: Mapping[str, Any],
    projection_profile: str,
) -> dict[str, Any]:
    """Return a lane snapshot with the IA live metadata lane appended/replaced."""
    value = json.loads(json.dumps(snapshot))
    page = dict(value.get("lane_page") or {})
    lanes = [dict(item) for item in page.get("lanes", []) or [] if item.get("lane_kind") != "ia_live_metadata_candidates"]
    lanes.append(build_ia_live_metadata_lane_packet(lane_result, projection_profile))
    page["lanes"] = lanes
    page["lane_count"] = len(lanes)
    page["visible_lane_count"] = sum(1 for item in lanes if item.get("visible", True))
    value["lane_page"] = page
    value["lane_count"] = page["lane_count"]
    value["visible_lane_count"] = page["visible_lane_count"]
    return value


def command_response_from_lane_result(result: Mapping[str, Any], projection_profile: str) -> dict[str, Any]:
    profile = _projection_profile(projection_profile)
    return {
        "schema_version": "ia_live_metadata_lane_command_response.v0",
        "run_id": str(result.get("run_id", "")),
        "projection_profile": profile,
        "command_type": str(result.get("command_type", "")),
        "allowed": bool(result.get("allowed", False)),
        "state": str(result.get("state", "")),
        "dry_run": str(result.get("mode", "")) == "dry_run",
        "mock_live": str(result.get("mode", "")) == "mock_live",
        "store_mutation_performed": False,
        "raw_response_committed": False,
        "blocked_reasons": list((result.get("policy_decision") or {}).get("blocked_reasons", []) or []),
        "events": [dict(item) for item in result.get("events", []) or []],
        "lane": build_ia_live_metadata_lane_packet(result, profile),
        "boundary_report": build_ia_live_metadata_lane_boundary_report(str(result.get("run_id", "")), result),
        "live_ia_call_performed": bool(result.get("live_ia_call_performed", False)),
        "source_probe_executed": bool(result.get("source_probe_executed", False)),
        "limitations": [
            "Command response is projection-safe and does not include raw IA response bodies.",
            "Live source execution remains blocked unless explicit operator approval and policy are supplied.",
        ],
    }


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = default_ia_live_metadata_lane_policy()
    merged.update(dict(policy or load_ia_live_metadata_lane_policy()))
    return merged


def _policy_decision(
    command_type: str,
    projection_profile: str,
    policy: Mapping[str, Any],
    command: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    command_payload = dict(command or {})
    blocked_reasons: list[str] = []
    allowed = True
    profile = _projection_profile(projection_profile)
    if profile != "operator_workbench" and command_type not in {"inspect_live_ia_metadata_result"}:
        allowed = False
        blocked_reasons.append("public/native projections cannot run IA live metadata commands")
    if command_type == "run_live_ia_metadata_now":
        if command_payload.get("allow_live") is not True:
            allowed = False
            blocked_reasons.append("allow_live must be true for live IA metadata")
        if not str(command_payload.get("operator_token", "")).strip():
            allowed = False
            blocked_reasons.append("operator token is required for live IA metadata")
        if command_payload.get("operator_approved") is not True:
            allowed = False
            blocked_reasons.append("explicit operator approval is required")
    if command_type == "approve_live_ia_metadata" and not str(command_payload.get("operator_token", "")).strip():
        allowed = False
        blocked_reasons.append("operator token is required for live IA metadata approval")
    if command_type not in IA_LIVE_COMMANDS:
        allowed = False
        blocked_reasons.append(f"unsupported IA live metadata command: {command_type}")
    if command_type in {"request_live_ia_metadata", "run_live_ia_metadata_dry_run", "run_live_ia_metadata_mock", "inspect_live_ia_metadata_result"}:
        allowed = allowed and profile == "operator_workbench"
    for key, expected in (
        ("live_ia_metadata_enabled_by_default", False),
        ("live_ia_metadata_requires_operator_command", True),
        ("live_ia_metadata_requires_operator_token", True),
        ("live_ia_metadata_requires_policy_gate", True),
        ("public_live_ia_metadata_enabled", False),
        ("native_live_ia_metadata_enabled", False),
        ("live_ia_raw_response_commit_allowed", False),
        ("source_cache_write_default", False),
        ("evidence_write_default", False),
        ("candidate_write_default", False),
        ("reviewed_index_write_default", False),
        ("operator_instance_mutation_default", False),
        ("downloads_enabled", False),
        ("uploads_enabled", False),
        ("extraction_enabled", False),
        ("model_provider_enabled", False),
        ("deployment_enabled", False),
        ("master_index_mutation_enabled", False),
        ("production_readiness_claimed", False),
        ("public_launch_readiness_claimed", False),
        ("full_archive_org_integration_claimed", False),
    ):
        if policy.get(key) is not expected:
            allowed = False
            blocked_reasons.append(f"{key} must be {str(expected).lower()}")
    return {
        "schema_version": "ia_live_metadata_lane_policy_decision.v0",
        "command_type": command_type,
        "projection_profile": profile,
        "allowed": allowed,
        "blocked_reasons": blocked_reasons,
        "operator_approval_required": True,
        "operator_token_required": command_type in {"approve_live_ia_metadata", "run_live_ia_metadata_now"},
        "raw_response_commit_allowed": False,
    }


def _lane_result(
    *,
    run_id: str,
    query: str,
    state: str,
    mode: str,
    command_type: str,
    allowed: bool,
    policy_decision: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    normalized_candidates: Sequence[Mapping[str, Any]],
    redacted_summary: Mapping[str, Any],
    live_ia_call_performed: bool,
    source_probe_executed: bool,
    total_http_requests: int,
    raw_response_committed: bool,
) -> dict[str, Any]:
    return {
        "schema_version": "ia_live_metadata_lane_result_packet.v0",
        "run_id": run_id,
        "query": query,
        "state": state,
        "mode": mode,
        "command_type": command_type,
        "allowed": allowed,
        "policy_decision": dict(policy_decision),
        "events": [dict(item) for item in events],
        "normalized_candidates": [dict(item) for item in normalized_candidates],
        "candidate_count": len(normalized_candidates),
        "redacted_summary": dict(redacted_summary),
        "total_http_requests": total_http_requests,
        "live_ia_call_performed": live_ia_call_performed,
        "source_probe_executed": source_probe_executed,
        "raw_response_committed": raw_response_committed,
        "source_cache_write_performed": False,
        "evidence_write_performed": False,
        "candidate_index_mutated": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "operator_instance_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "full_archive_org_integration_claimed": False,
    }


def _event(run_id: str, event_type: str, summary: str) -> dict[str, Any]:
    return {
        "schema_version": "ia_live_metadata_lane_event.v0",
        "event_id": stable_id("ia_live_evt", {"run_id": run_id, "event_type": event_type, "summary": summary}),
        "run_id": run_id,
        "created_at": FIXED_CREATED_AT,
        "event_type": event_type,
        "summary": summary,
        "accepted_truth": False,
        "review_required": False,
    }


def _projection_profile(value: str) -> str:
    profile = str(value or "operator_workbench")
    if profile not in PROJECTION_PROFILES:
        raise ValueError(f"unsupported projection profile: {profile}")
    return profile


def _blocked_state_for_projection(profile: str) -> str:
    return "unavailable" if profile != "operator_workbench" else "blocked_pending_operator_approval"


def _lane_summary(state: str, profile: str) -> str:
    if profile != "operator_workbench":
        return "Live Internet Archive metadata is unavailable in this read-only projection."
    if state == "blocked_pending_operator_approval":
        return "Live Internet Archive metadata is pending explicit operator approval."
    if state == "approved_pending_run":
        return "Live Internet Archive metadata is approved but has not run."
    if state == "running":
        return "Live Internet Archive metadata is running."
    if state == "candidates_available":
        return "Provisional Internet Archive metadata candidates are available."
    if state == "rate_limited":
        return "Internet Archive metadata returned a rate-limit response."
    if state == "tls_failed":
        return "Internet Archive metadata TLS validation failed."
    if state == "failed":
        return "Internet Archive metadata request failed."
    return "Live Internet Archive metadata lane is complete."


def _mock_metadata_fixture(query: str) -> dict[str, Any]:
    return {
        "fixture_id": "ia_live_metadata_mock_search",
        "fixture_class": "metadata_search_small",
        "endpoint_class": "metadata_search_small",
        "request": {"query": query, "rows": 2},
        "payload": {
            "response": {
                "numFound": 2,
                "docs": [
                    {
                        "identifier": "sampleproject-demo",
                        "title": f"Mock IA metadata candidate for {query}",
                        "mediatype": "software",
                        "collection": ["software", "opensource"],
                        "creator": "Eureka deterministic fixture",
                        "date": "1993",
                        "description": "Deterministic mock-live metadata preview; no network request was made.",
                    },
                    {
                        "identifier": "sampleproject-support-disc",
                        "title": "Mock IA support media candidate",
                        "mediatype": "data",
                        "collection": ["software"],
                        "creator": "Eureka deterministic fixture",
                    },
                ],
            }
        },
    }


def _redacted_summary(query: str, normalized: Sequence[Mapping[str, Any]], status: str) -> dict[str, Any]:
    return {
        "schema_version": "ia_live_metadata_redacted_summary.v0",
        "probe_status": status,
        "query": query,
        "normalized_preview_count": len(normalized),
        "identifier_count": sum(1 for item in normalized if item.get("item_identifier")),
        "total_http_requests": 0,
        "raw_response_committed": False,
        "live_ia_call_performed": False,
        "source_probe_executed": False,
    }


def _live_probe_policy_from_lane_policy(
    policy: Mapping[str, Any],
    *,
    rows: int,
    max_requests: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    base = load_live_probe_policy()
    base["metadata_search_rows_max"] = min(int(rows), int(policy.get("live_ia_rows_default", 5)))
    base["total_http_requests_max"] = min(int(max_requests), int(policy.get("live_ia_max_requests_default", 2)))
    base["timeout_seconds_max"] = min(int(timeout_seconds), int(policy.get("live_ia_timeout_seconds_default", 15)))
    return base
