"""Local Workbench projection over the headless resolution-run kernel."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from runtime.resolution_run import BLOCKED_ACTIONS, run_resolution_dry_run
from runtime.resolution_run.run_store import FIXED_CREATED_AT, stable_id
from runtime.source_observation import ia_live_metadata_lane


PROJECTION_PROFILES = ("operator_workbench", "public_web", "native_desktop_read_only")
READ_COMMANDS = (
    "create_run",
    "inspect_run",
    "list_events",
    "list_lanes",
    "list_workunits",
    "export_run_packet",
)
BLOCKED_COMMANDS = (
    "pause",
    "resume",
    "cancel",
    "deepen",
    "run_live_source",
    "run_live_ia_metadata_now",
    "cancel_live_ia_metadata",
    "apply_to_operator_instance",
    "review_candidate",
    "promote_candidate",
    "rebuild_index",
)
EVENT_TYPE_MAP = {
    "run_created": "run.created",
    "query_compiled": "query.compiled",
    "command_applied": "run.command_applied",
    "workunits_scheduled": "workunits.planned",
    "lane_snapshot_built": "lanes.snapshot_created",
    "coverage_report_built": "run.completed",
}

_RUNS: dict[str, dict[str, Any]] = {}


def create_workbench_resolution_run(
    query: str,
    projection_profile: str = "operator_workbench",
    policy: Mapping[str, Any] | None = None,
    *,
    include_ia_hunt_dry_run: bool = True,
) -> dict[str, Any]:
    """Create a local dry-run packet for Workbench/API presentation."""
    profile = _projection_profile(projection_profile)
    result = run_resolution_dry_run(
        query,
        projection_profile=profile,
        include_ia_hunt=include_ia_hunt_dry_run,
        policy=policy,
    )
    result["ia_live_metadata_lane"] = ia_live_metadata_lane.plan_ia_live_metadata_lane(
        result.get("run") or {},
        query,
        policy,
    )
    packet = project_run_for_workbench(result, profile)
    _RUNS[packet["run_id"]] = deepcopy(result)
    return packet


def get_workbench_resolution_run(run_id: str, projection_profile: str = "operator_workbench") -> dict[str, Any]:
    """Return a previously created run packet from the process-local store."""
    result = _stored_result(run_id)
    return project_run_for_workbench(result, _projection_profile(projection_profile))


def list_workbench_resolution_runs(projection_profile: str = "operator_workbench") -> dict[str, Any]:
    """List process-local runs without reading or writing operator instance state."""
    profile = _projection_profile(projection_profile)
    runs = [project_run_for_workbench(result, profile) for result in _RUNS.values()]
    return {
        "schema_version": "workbench_live_run_list.v0",
        "projection_profile": profile,
        "run_count": len(runs),
        "runs": [
            {
                "run_id": run["run_id"],
                "query": run["query"],
                "state": run["state"],
                "lane_count": run["lane_count"],
                "workunit_count": run["workunit_count"],
                "event_count": run["event_count"],
            }
            for run in runs
        ],
        "warnings": [],
        "limitations": [
            "List is process-local demo state only.",
            "No operator instance, public index, or master index state is mutated.",
        ],
    }


def get_workbench_run_events(run_id: str, projection_profile: str = "operator_workbench") -> dict[str, Any]:
    packet = get_workbench_resolution_run(run_id, projection_profile)
    return _api_envelope(packet, "events", packet["events"])


def get_workbench_run_lanes(run_id: str, projection_profile: str = "operator_workbench") -> dict[str, Any]:
    packet = get_workbench_resolution_run(run_id, projection_profile)
    return _api_envelope(packet, "lanes", packet["lane_snapshot"])


def get_workbench_run_workunits(run_id: str, projection_profile: str = "operator_workbench") -> dict[str, Any]:
    packet = get_workbench_resolution_run(run_id, projection_profile)
    return _api_envelope(packet, "workunits", packet["workunits"])


def build_workbench_live_run_boundary_report(run_or_packet: Mapping[str, Any]) -> dict[str, Any]:
    boundaries = dict(run_or_packet.get("boundary_report") or run_or_packet.get("boundaries") or {})
    boundaries.pop("schema_version", None)
    return {
        "schema_version": "workbench_live_run_boundary_report.v0",
        "workbench_is_projection_only": True,
        "resolution_run_kernel_used": True,
        "local_service_projection_added": True,
        "transitional_runtime_local_workbench_presentation_debt": True,
        "debt_note": (
            "Existing runtime/local_workbench presentation remains transitional; "
            "runtime/resolution_run owns behavior and runtime/local_workbench only renders local HTML."
        ),
        "live_ia_call_performed": False,
        "source_probe_executed": False,
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
        **{key: value for key, value in boundaries.items() if key not in {"review_queue_mutated"}},
    }


def build_command_response(
    run_id: str,
    command_type: str,
    projection_profile: str = "operator_workbench",
    *,
    operator_token: str = "",
    allow_live: bool = False,
    mock_live: bool = False,
    max_requests: int = 2,
    rows: int = 5,
    timeout_seconds: int = 15,
) -> dict[str, Any]:
    """Return a command outcome; unsafe or future commands are policy-blocked."""
    profile = _projection_profile(projection_profile)
    result = _stored_result(run_id)
    packet = project_run_for_workbench(result, profile)
    if command_type in ia_live_metadata_lane.IA_LIVE_COMMANDS:
        run = dict(result.get("run") or {})
        query = str(run.get("query") or packet.get("query") or "sampleproject")
        command_payload = {
            "command_type": command_type,
            "projection_profile": profile,
            "query": query,
            "operator_token": operator_token,
            "allow_live": allow_live,
            "mock_live": mock_live,
            "max_requests": max_requests,
            "rows": rows,
            "timeout_seconds": timeout_seconds,
            "operator_approved": bool(operator_token and allow_live),
        }
        if profile != "operator_workbench":
            lane_result = ia_live_metadata_lane.request_ia_live_metadata_lane(run_id, command_payload)
        elif command_type == "run_live_ia_metadata_dry_run":
            lane_result = ia_live_metadata_lane.run_ia_live_metadata_lane_dry_run(run_id, query)
        elif command_type == "run_live_ia_metadata_mock":
            lane_result = ia_live_metadata_lane.run_ia_live_metadata_lane_mock(run_id, query)
        elif command_type == "run_live_ia_metadata_now":
            lane_result = ia_live_metadata_lane.run_ia_live_metadata_lane_live(
                run_id,
                query,
                operator_token=operator_token,
                allow_live=allow_live,
                max_requests=max_requests,
                rows=rows,
                timeout_seconds=timeout_seconds,
            )
        elif command_type == "approve_live_ia_metadata":
            lane_result = ia_live_metadata_lane.approve_ia_live_metadata_lane(run_id, command_payload)
        elif command_type == "cancel_live_ia_metadata":
            lane_result = ia_live_metadata_lane.request_ia_live_metadata_lane(run_id, command_payload)
            lane_result["state"] = "cancelled" if lane_result.get("allowed") else lane_result.get("state", "blocked_pending_operator_approval")
            lane_result["events"] = list(lane_result.get("events", [])) + ia_live_metadata_lane.build_ia_live_metadata_lane_events(run_id, "cancelled")
        else:
            lane_result = ia_live_metadata_lane.request_ia_live_metadata_lane(run_id, command_payload)
        result["ia_live_metadata_lane"] = lane_result
        _RUNS[run_id] = deepcopy(result)
        return ia_live_metadata_lane.command_response_from_lane_result(lane_result, profile)

    allowed = command_type in READ_COMMANDS
    blocked_reasons: list[str] = []
    if not allowed:
        blocked_reasons.append(f"{command_type} is reserved for a future governed Workbench run task")
    response = {
        "schema_version": "workbench_live_run_command_response.v0",
        "run_id": packet["run_id"],
        "projection_profile": packet["projection_profile"],
        "command_type": command_type,
        "allowed": allowed,
        "dry_run": True,
        "state_mutated": False,
        "store_mutation_performed": False,
        "blocked_reasons": blocked_reasons,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "warnings": [],
        "limitations": packet["limitations"],
    }
    if allowed:
        response["data"] = {
            "run_id": packet["run_id"],
            "state": packet["state"],
            "available_read_commands": list(READ_COMMANDS),
        }
    return response


def build_api_response(packet: Mapping[str, Any], endpoint: str = "run") -> dict[str, Any]:
    return _api_envelope(packet, endpoint, dict(packet))


def project_run_for_workbench(
    kernel_result: Mapping[str, Any],
    projection_profile: str = "operator_workbench",
) -> dict[str, Any]:
    """Shape a kernel result into a projection-safe Workbench live-run packet."""
    profile = _projection_profile(projection_profile)
    run = dict(kernel_result.get("run") or {})
    ia_lane_result = dict(kernel_result.get("ia_live_metadata_lane") or {})
    raw_lane_snapshot = kernel_result.get("lane_snapshot") or {}
    if ia_lane_result:
        raw_lane_snapshot = ia_live_metadata_lane.ensure_ia_live_metadata_lane_in_snapshot(
            raw_lane_snapshot,
            ia_lane_result,
            profile,
        )
    lane_snapshot = _project_lane_snapshot(raw_lane_snapshot, profile)
    workunits = _project_workunits(kernel_result.get("workunit_schedule") or {}, profile)
    raw_events = list(kernel_result.get("events") or ())
    raw_events.extend(ia_lane_result.get("events", []) or [])
    events = _project_events(raw_events, profile)
    raw_boundaries = dict(kernel_result.get("boundaries") or {})
    if ia_lane_result:
        raw_boundaries.update(
            {
                key: value
                for key, value in ia_live_metadata_lane.build_ia_live_metadata_lane_boundary_report(
                    str(run.get("run_id", "")),
                    ia_lane_result,
                ).items()
                if key != "schema_version"
            }
        )
    boundary_report = build_workbench_live_run_boundary_report(raw_boundaries)
    blocked_actions = list(kernel_result.get("blocked_actions") or BLOCKED_ACTIONS)
    warnings = _warnings_for_profile(profile)
    limitations = _limitations_for_profile(profile)
    packet = {
        "schema_version": "workbench_live_run_packet.v0",
        "packet_type": "WorkbenchLiveRunPacket",
        "created_at": run.get("created_at", FIXED_CREATED_AT),
        "run_id": str(run.get("run_id", "")),
        "request_id": str(run.get("request_id") or stable_id("req", run.get("query", ""))),
        "projection_profile": profile,
        "query": str(run.get("query", "")),
        "state": str(run.get("state", "")),
        "compiled_query_id": str(run.get("compiled_query_id", "")),
        "run": _project_run(run, profile),
        "events": events,
        "event_count": len(events),
        "lane_snapshot": lane_snapshot,
        "lane_count": int(lane_snapshot.get("lane_count", 0) or 0),
        "visible_lane_count": int(lane_snapshot.get("visible_lane_count", 0) or 0),
        "workunits": workunits,
        "workunit_count": len(workunits),
        "blocked_actions": blocked_actions,
        "blocked_commands": list(BLOCKED_COMMANDS),
        "read_commands": list(READ_COMMANDS),
        "ia_live_metadata_commands": list(ia_live_metadata_lane.IA_LIVE_COMMANDS),
        "ia_live_metadata_lane": ia_live_metadata_lane.build_ia_live_metadata_lane_packet(
            ia_lane_result or ia_live_metadata_lane.plan_ia_live_metadata_lane(run, run.get("query", ""), {}),
            profile,
        ),
        "boundary_report": boundary_report,
        "coverage_report": _project_coverage_report(kernel_result.get("coverage_report") or {}, profile),
        "warnings": warnings,
        "limitations": limitations,
        "accepted_truth": False,
        "review_required": True,
        "source_probe_executed": bool(ia_lane_result.get("source_probe_executed", False)),
        "live_ia_call_performed": bool(ia_lane_result.get("live_ia_call_performed", False)),
        "store_mutation_performed": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
    }
    if profile != "operator_workbench":
        packet.pop("compiled_query_id", None)
    return packet


def _stored_result(run_id: str) -> dict[str, Any]:
    value = _RUNS.get(str(run_id))
    if value is None:
        raise KeyError(f"workbench live run not found: {run_id}")
    return deepcopy(value)


def _api_envelope(packet: Mapping[str, Any], endpoint: str, data: Any) -> dict[str, Any]:
    return {
        "schema_version": "workbench_live_run_api_response.v0",
        "request_id": str(packet.get("request_id", "")),
        "run_id": str(packet.get("run_id", "")),
        "endpoint": endpoint,
        "projection_profile": str(packet.get("projection_profile", "operator_workbench")),
        "state": str(packet.get("state", "")),
        "data": data,
        "warnings": list(packet.get("warnings") or []),
        "limitations": list(packet.get("limitations") or []),
        "blocked_actions": list(packet.get("blocked_actions") or []),
    }


def _projection_profile(value: str) -> str:
    profile = str(value or "operator_workbench")
    if profile not in PROJECTION_PROFILES:
        raise ValueError(f"unsupported projection profile: {profile}")
    return profile


def _project_run(run: Mapping[str, Any], profile: str) -> dict[str, Any]:
    allowed = {
        "schema_version",
        "packet_type",
        "created_at",
        "updated_at",
        "run_id",
        "request_id",
        "query",
        "projection_profile",
        "state",
        "state_history",
        "active_lanes",
        "controls_available",
        "dry_run",
        "accepted_truth",
        "review_required",
        "limitations",
    }
    if profile == "operator_workbench":
        allowed |= {"compiled_query_id", "coverage_report_id", "policy_decision"}
    return {key: deepcopy(value) for key, value in run.items() if key in allowed}


def _project_events(events: Sequence[Mapping[str, Any]], profile: str) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for event in events:
        event_type = str(event.get("event_type", ""))
        packet = {
            "schema_version": "workbench_live_run_event.v0",
            "event_id": str(event.get("event_id", "")),
            "run_id": str(event.get("run_id", "")),
            "created_at": str(event.get("created_at", FIXED_CREATED_AT)),
            "event_type": EVENT_TYPE_MAP.get(event_type, event_type.replace("_", ".")),
            "summary": _event_summary(event_type, event.get("payload") or {}),
            "accepted_truth": False,
            "review_required": False,
        }
        if profile == "operator_workbench":
            packet["kernel_event_type"] = event_type
            packet["payload"] = deepcopy(event.get("payload") or {})
        projected.append(packet)
    if not any(event["event_type"] == "local_index.checked" for event in projected):
        projected.insert(2, _synthetic_event(projected, "local_index.checked", "Local reviewed index lane checked without source probes."))
    if not any(event["event_type"] == "ia_hunt.dry_run_planned" for event in projected):
        projected.insert(4, _synthetic_event(projected, "ia_hunt.dry_run_planned", "IA-HUNT WorkUnits planned in dry-run mode only."))
    projected.append(_synthetic_event(projected, "action.blocked", "Unsafe live/source/apply commands remain policy-blocked."))
    return projected


def _synthetic_event(existing: Sequence[Mapping[str, Any]], event_type: str, summary: str) -> dict[str, Any]:
    run_id = str(existing[0].get("run_id", "")) if existing else ""
    return {
        "schema_version": "workbench_live_run_event.v0",
        "event_id": stable_id("wblr_evt", {"run_id": run_id, "event_type": event_type, "index": len(existing)}),
        "run_id": run_id,
        "created_at": FIXED_CREATED_AT,
        "event_type": event_type,
        "summary": summary,
        "accepted_truth": False,
        "review_required": False,
    }


def _event_summary(event_type: str, payload: Mapping[str, Any]) -> str:
    if event_type == "run_created":
        return f"Resolution run created for query {payload.get('query', '')!r}."
    if event_type == "query_compiled":
        return "Query compilation packet recorded by the run kernel."
    if event_type == "workunits_scheduled":
        return f"{payload.get('workunit_count', 0)} IA-HUNT dry-run WorkUnits planned."
    if event_type == "lane_snapshot_built":
        return "Result lane snapshot built from the run kernel projector."
    if event_type == "coverage_report_built":
        return "Dry-run coverage report built; live/apply work remains deferred."
    if event_type == "command_applied":
        command = dict(payload.get("command") or {})
        return f"Safe command applied: {command.get('command_type', '')}."
    return event_type.replace("_", " ")


def _project_lane_snapshot(snapshot: Mapping[str, Any], profile: str) -> dict[str, Any]:
    value = deepcopy(dict(snapshot))
    lane_page = dict(value.get("lane_page") or {})
    lanes = []
    for lane in lane_page.get("lanes", []) or []:
        lanes.append(_project_lane(lane, profile))
    lane_page["lanes"] = lanes
    value["lane_page"] = lane_page
    value["projection_profile"] = profile
    return value


def _project_lane(lane: Mapping[str, Any], profile: str) -> dict[str, Any]:
    packet = deepcopy(dict(lane))
    packet["projection_profile"] = profile
    if profile != "operator_workbench":
        for item in packet.get("items", []) or []:
            if isinstance(item, dict):
                item.pop("debug", None)
                item.pop("operator_notes", None)
                item.pop("private_local_path_refs", None)
    return packet


def _project_workunits(schedule: Mapping[str, Any], profile: str) -> list[dict[str, Any]]:
    workunits = []
    for workunit in schedule.get("workunits", []) or []:
        packet = {
            "schema_version": "workbench_live_run_workunit.v0",
            "workunit_id": str(workunit.get("workunit_id", "")),
            "hunt_id": str(workunit.get("hunt_id", "")),
            "source_family": str(workunit.get("source_family", "")),
            "workunit_type": str(workunit.get("workunit_type", "")),
            "state": str(workunit.get("state", "")),
            "dry_run": bool(workunit.get("dry_run", True)),
            "writes_instance_state": bool(workunit.get("writes_instance_state", False)),
            "write_scope": str(workunit.get("write_scope", "")),
            "blocked_actions": list(workunit.get("blocked_actions") or []),
            "limitations": list(workunit.get("limitations") or []),
        }
        if profile == "operator_workbench":
            packet["input_ref"] = deepcopy(workunit.get("input_ref") or {})
            packet["output_ref"] = deepcopy(workunit.get("output_ref") or {})
            packet["policy_ref"] = str(workunit.get("policy_ref", ""))
        workunits.append(packet)
    return workunits


def _project_coverage_report(report: Mapping[str, Any], profile: str) -> dict[str, Any]:
    packet = deepcopy(dict(report))
    if profile != "operator_workbench":
        packet.pop("coverage_report_id", None)
    return packet


def _warnings_for_profile(profile: str) -> list[str]:
    if profile == "operator_workbench":
        return []
    return ["Projection is read-only and omits operator-only details."]


def _limitations_for_profile(profile: str) -> list[str]:
    limitations = [
        "Workbench live run is a projection of the headless ResolutionRunKernel.",
        "Run store is process-local and deterministic for this foundation task.",
        "No live IA calls, source probes, downloads, extraction, model calls, or store mutations are performed.",
        "Review/promote and Local Apply Gate flows are deferred.",
    ]
    if profile != "operator_workbench":
        limitations.append("Public/native projections are read-only summaries.")
    return limitations
