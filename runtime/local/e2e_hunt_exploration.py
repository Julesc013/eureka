"""Private local exploration workspace over the E2E runner and Preview Index."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Any, Mapping, Sequence

from runtime.index.preview import (
    DEFAULT_PREVIEW_INDEX_ROOT,
    PreviewIndexError,
    preview_record_to_result_card,
    preview_stats_payload,
    search_preview_index,
    validate_preview_index,
)
from runtime.resolution_run import (
    command_run_bundle,
    replay_run_bundle,
    run_e2e_reference_run,
    validate_run_bundle,
)
from runtime.resolution_run.errors import ResolutionRunValidationError
from runtime.resolution_run.runner import DEFAULT_OUTPUT_ROOT, DEFAULT_SYNTHETIC_FIXTURE, TERMINAL_STATES


EXPLORE_SCHEMA_VERSION = "eureka.e2e_hunt_exploration.v0"
DEFAULT_PREVIEW_INDEX_PATH = DEFAULT_PREVIEW_INDEX_ROOT / "current.json"
DEFAULT_RUNS_ROOT = DEFAULT_OUTPUT_ROOT
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")
LANE_ORDER = (
    "reviewed",
    "candidates",
    "near_misses",
    "needs",
    "absence_or_next_steps",
    "blocked_or_unavailable",
    "mentions_and_traces",
    "unknown",
)
LANE_TITLES = {
    "reviewed": "Reviewed",
    "candidates": "Candidates",
    "near_misses": "Near Misses",
    "needs": "Needs",
    "absence_or_next_steps": "Absence And Next Steps",
    "blocked_or_unavailable": "Blocked Or Unavailable",
    "mentions_and_traces": "Mentions And Traces",
    "unknown": "Unknown",
}
LANE_NOTES = {
    "reviewed": "Accepted local reviewed records, when present.",
    "candidates": "Provisional candidate material; review remains required.",
    "near_misses": "Related material that does not satisfy a material constraint.",
    "needs": "Unresolved query demand or follow-up work.",
    "absence_or_next_steps": "Local absence clues and deferred next steps.",
    "blocked_or_unavailable": "Policy-blocked, unavailable, or deferred source states.",
    "mentions_and_traces": "Evidence or source-observation mentions that support discovery but are not candidates.",
    "unknown": "Records whose preview status is intentionally unresolved.",
}
BOUNDARY_FLAGS = {
    "local_private": True,
    "public_workbench": False,
    "public_exposure": False,
    "network_provider_calls": False,
    "downloads": False,
    "file_fetch": False,
    "wayback_replay": False,
    "review_decision_mutation": False,
    "reviewed_record_created": False,
    "reviewed_master_mutation": False,
    "public_index_mutation": False,
    "candidate_index_store_mutation": False,
    "evidence_ledger_store_mutation": False,
    "accepted_truth_created": False,
    "production_readiness_claimed": False,
}
LIMITATIONS = (
    "Explore is a private local operator workspace.",
    "Preview records are searchable without becoming reviewed truth.",
    "Synthetic Hunts use the shared E2E Reference Runner.",
    "Live providers, downloads, review decisions, and index mutations remain gated.",
)


@dataclass(frozen=True)
class E2EExploreOptions:
    preview_index_path: Path = DEFAULT_PREVIEW_INDEX_PATH
    runs_root: Path = DEFAULT_RUNS_ROOT
    default_fixture: str = DEFAULT_SYNTHETIC_FIXTURE


def options_from_runtime(runtime: Any) -> E2EExploreOptions:
    """Return route options without accepting caller-provided filesystem paths."""

    return E2EExploreOptions(
        preview_index_path=Path(getattr(runtime, "e2e_explore_preview_index_path", DEFAULT_PREVIEW_INDEX_PATH)),
        runs_root=Path(getattr(runtime, "e2e_explore_runs_root", DEFAULT_RUNS_ROOT)),
        default_fixture=str(getattr(runtime, "e2e_explore_default_fixture", DEFAULT_SYNTHETIC_FIXTURE)),
    )


def build_explore_workspace(
    query: str = "",
    *,
    options: E2EExploreOptions | None = None,
    limit: int = 20,
    include_synthetic: bool = False,
) -> dict[str, Any]:
    opts = options or E2EExploreOptions()
    preview = _preview_search(query, opts.preview_index_path, limit=limit, include_synthetic=include_synthetic)
    runs = list_run_bundles(opts.runs_root, limit=10)
    payload = _base_payload("explore_workspace")
    payload.update(
        {
            "query": str(query or ""),
            "preview_index": preview,
            "lanes": preview["lanes"],
            "lane_counts": preview["lane_counts"],
            "runs": runs,
            "run_controls": _workspace_controls(query),
            "routes": _routes(),
        }
    )
    payload["warnings"].extend(preview.get("warnings", []))
    payload["warnings"].extend(runs.get("warnings", []))
    return payload


def list_run_bundles(runs_root: str | Path = DEFAULT_RUNS_ROOT, *, limit: int = 50) -> dict[str, Any]:
    root = Path(runs_root)
    runs: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not root.exists():
        warnings.append("no durable E2E run bundle root exists yet")
    elif not root.is_dir():
        warnings.append("durable E2E run bundle root is not a directory")
    else:
        for child in sorted(root.iterdir(), key=lambda item: item.name):
            if not child.is_dir():
                continue
            manifest_path = child / "run_manifest.json"
            if not manifest_path.is_file():
                continue
            try:
                manifest = _load_json(manifest_path)
                validation = validate_run_bundle(child, strict=True, write_report=False)
            except Exception as exc:  # pragma: no cover - defensive corrupt bundle path
                manifest = {"run_id": child.name, "current_state": "unknown"}
                validation = {"status": "invalid", "errors": [str(exc)]}
            runs.append(_run_list_entry(child, manifest, validation))
    runs.sort(key=lambda item: (str(item.get("updated_at", "")), str(item.get("run_id", ""))), reverse=True)
    limited = runs[: max(1, min(int(limit), 100))]
    return {
        "schema_version": "eureka.e2e_explore_run_list.v0",
        "runs_root": _safe_display_path(root),
        "run_count": len(limited),
        "total_run_count": len(runs),
        "runs": limited,
        "warnings": warnings,
        "limitations": list(LIMITATIONS),
        **BOUNDARY_FLAGS,
    }


def load_run_detail(run_id: str, runs_root: str | Path = DEFAULT_RUNS_ROOT) -> dict[str, Any]:
    run_dir = _run_dir(runs_root, run_id)
    validation = validate_run_bundle(run_dir, strict=True, write_report=False)
    manifest = _load_json(run_dir / "run_manifest.json")
    run_state = _load_json(run_dir / "run_state.json")
    result = _load_json(run_dir / "result.json")
    lane_snapshot = _load_json(run_dir / "lane_snapshot.json")
    boundary_report = _load_json(run_dir / "boundary_report.json")
    events = _load_jsonl(run_dir / "events.jsonl")
    workunits = _load_jsonl(run_dir / "workunits.jsonl")
    replay_report = _load_json_optional(run_dir / "replay_report.json")
    payload = _base_payload("explore_run_detail")
    payload.update(
        {
            "run_id": str(run_id),
            "run": run_state,
            "manifest": manifest,
            "validation": validation,
            "result": result,
            "lane_snapshot": lane_snapshot,
            "boundary_report": boundary_report,
            "events": events,
            "event_count": len(events),
            "workunits": workunits,
            "workunit_count": len(workunits),
            "replay_report": replay_report,
            "controls": _run_controls(run_state),
            "run_dir": manifest.get("run_dir", Path(run_dir).name),
        }
    )
    return payload


def start_synthetic_hunt(
    query: str,
    *,
    options: E2EExploreOptions | None = None,
    fixture: str | None = None,
) -> dict[str, Any]:
    opts = options or E2EExploreOptions()
    clean_query = str(query or "").strip()
    if not clean_query:
        raise ResolutionRunValidationError("query is required")
    result = run_e2e_reference_run(
        clean_query,
        mode="synthetic",
        projection_profile="operator_workbench",
        fixture=str(fixture or opts.default_fixture or DEFAULT_SYNTHETIC_FIXTURE),
        out_root=opts.runs_root,
        write_bundle=True,
        include_ia_hunt=False,
        scheduler_kind="synthetic_fixture",
    )
    payload = _base_payload("explore_synthetic_hunt_started")
    payload.update(
        {
            "action": "start_synthetic_hunt",
            "run_id": str(result.get("run_id", "")),
            "query": clean_query,
            "fixture": str(fixture or opts.default_fixture or DEFAULT_SYNTHETIC_FIXTURE),
            "run": dict(result.get("run") or {}),
            "manifest": dict(result.get("bundle_manifest") or {}),
            "result_count": int(result.get("result_count", 0) or 0),
            "event_count": int(result.get("event_count", 0) or 0),
            "workunit_count": int((result.get("workunit_schedule") or {}).get("workunit_count", 0) or 0),
            "replay_eligible": True,
            "review_required": True,
        }
    )
    return payload


def apply_run_control(
    run_id: str,
    command: str,
    *,
    runs_root: str | Path = DEFAULT_RUNS_ROOT,
) -> dict[str, Any]:
    action = str(command or "").strip().lower()
    run_dir = _run_dir(runs_root, run_id)
    if action == "replay":
        report = replay_run_bundle(run_dir, strict=True)
        payload = _base_payload("explore_run_replayed")
        payload.update({"action": "replay", "run_id": run_id, "replay_report": report, "mutation_scope": "generated_replay_report_only"})
        return payload
    run_state = _load_json(run_dir / "run_state.json")
    current_state = str(run_state.get("state", ""))
    if current_state in TERMINAL_STATES:
        return _blocked_control(run_id, action, f"{action} is disabled for terminal run state {current_state}", current_state)
    if action in {"step", "advance"}:
        return _blocked_control(run_id, action, "incremental stepping is reserved for a future non-terminal runner mode", current_state)
    if action not in {"pause", "resume", "cancel"}:
        raise ResolutionRunValidationError(f"unsupported explore run command: {action}")
    try:
        result = command_run_bundle(run_dir, action)
    except ResolutionRunValidationError as exc:
        return _blocked_control(run_id, action, str(exc), current_state)
    payload = _base_payload("explore_run_command_applied")
    payload.update({"action": action, "run_id": run_id, "command_result": result, "state": result.get("state", "")})
    return payload


def compare_runs(left_run_id: str, right_run_id: str, *, runs_root: str | Path = DEFAULT_RUNS_ROOT) -> dict[str, Any]:
    left = load_run_detail(left_run_id, runs_root)
    right = load_run_detail(right_run_id, runs_root)
    left_lanes = _lane_ids(left.get("lane_snapshot") or {})
    right_lanes = _lane_ids(right.get("lane_snapshot") or {})
    payload = _base_payload("explore_run_compare")
    payload.update(
        {
            "left_run_id": left_run_id,
            "right_run_id": right_run_id,
            "left": _compare_side(left),
            "right": _compare_side(right),
            "diff": {
                "same_query": left["run"].get("query") == right["run"].get("query"),
                "same_state": left["run"].get("state") == right["run"].get("state"),
                "event_count_delta": int(right.get("event_count", 0)) - int(left.get("event_count", 0)),
                "workunit_count_delta": int(right.get("workunit_count", 0)) - int(left.get("workunit_count", 0)),
                "result_count_delta": int((right.get("result") or {}).get("result_count", 0) or 0)
                - int((left.get("result") or {}).get("result_count", 0) or 0),
                "added_lanes": sorted(right_lanes - left_lanes),
                "removed_lanes": sorted(left_lanes - right_lanes),
                "shared_lanes": sorted(left_lanes & right_lanes),
            },
            "read_only_compare": True,
        }
    )
    return payload


def empty_compare_payload(left_run_id: str = "", right_run_id: str = "") -> dict[str, Any]:
    payload = _base_payload("explore_run_compare")
    payload.update(
        {
            "status": "pending",
            "left_run_id": str(left_run_id or ""),
            "right_run_id": str(right_run_id or ""),
            "left": None,
            "right": None,
            "diff": {},
            "read_only_compare": True,
        }
    )
    return payload


def _preview_search(index_query: str, index_path: Path, *, limit: int, include_synthetic: bool) -> dict[str, Any]:
    warnings: list[str] = []
    stats: dict[str, Any] = {}
    validation: dict[str, Any] = {}
    search: dict[str, Any] = {
        "schema_version": "eureka.e2e_preview_index_search.v0",
        "query": str(index_query or ""),
        "result_count": 0,
        "results": [],
        "lanes": {},
        "lane_counts": {},
    }
    try:
        stats = preview_stats_payload(index_path)
        validation = validate_preview_index(index_path, strict=True)
        if str(index_query or "").strip():
            search = search_preview_index(index_path, index_query, limit=limit, include_synthetic=include_synthetic)
    except PreviewIndexError as exc:
        warnings.append(str(exc))
        validation = {"status": "missing_or_invalid", "errors": [str(exc)]}
    return {
        "schema_version": "eureka.e2e_explore_preview_panel.v0",
        "index": _safe_display_path(index_path),
        "status": "pass" if not warnings and validation.get("status") in {"pass", ""} else "degraded",
        "stats": stats,
        "validation": validation,
        "search": search,
        "result_count": int(search.get("result_count", 0) or 0),
        "lanes": _project_lanes(search.get("lanes") or {}),
        "lane_counts": dict(search.get("lane_counts") or {}),
        "warnings": warnings,
        "limitations": list(LIMITATIONS),
        **BOUNDARY_FLAGS,
    }


def _project_lanes(raw_lanes: Mapping[str, Any]) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    normalized = {str(key): list(value or []) for key, value in dict(raw_lanes or {}).items()}
    if "mention_only" in normalized:
        normalized.setdefault("mentions_and_traces", []).extend(normalized.pop("mention_only"))
    for lane_id in LANE_ORDER:
        records = [preview_record_to_result_card(record) for record in normalized.get(lane_id, [])]
        projected.append(
            {
                "lane_id": lane_id,
                "title": LANE_TITLES[lane_id],
                "note": LANE_NOTES[lane_id],
                "record_count": len(records),
                "records": records,
            }
        )
    for lane_id in sorted(key for key in normalized if key not in LANE_ORDER):
        records = [preview_record_to_result_card(record) for record in normalized[lane_id]]
        projected.append({"lane_id": lane_id, "title": lane_id.replace("_", " ").title(), "note": "Additional preview lane.", "record_count": len(records), "records": records})
    return projected


def _run_list_entry(run_dir: Path, manifest: Mapping[str, Any], validation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_id": str(manifest.get("run_id") or run_dir.name),
        "query": str(manifest.get("query", "")),
        "state": str(manifest.get("current_state", "")),
        "mode": str(manifest.get("mode", "")),
        "synthetic": bool(manifest.get("synthetic", False)),
        "updated_at": str(manifest.get("updated_at", "")),
        "workunit_count": int(manifest.get("workunit_count", 0) or 0),
        "event_count": int(manifest.get("event_count", 0) or 0),
        "result_count": int(manifest.get("result_count", 0) or 0),
        "validation_status": str(validation.get("status", "")),
        "replay_eligible": bool(manifest.get("replay_eligible", False)),
        "accepted_truth": False,
        "reviewed_record_created": False,
    }


def _workspace_controls(query: str) -> dict[str, Any]:
    has_query = bool(str(query or "").strip())
    return {
        "schema_version": "eureka.e2e_explore_workspace_controls.v0",
        "start_synthetic_hunt": {
            "enabled": has_query,
            "method": "POST",
            "path": "/explore/run/start",
            "api_path": "/api/v1/explore/run/start",
            "requires_operator_token": True,
            "disabled_reason": "" if has_query else "query is required",
        },
        "live_hunt": {"enabled": False, "disabled_reason": "live provider access requires a separate approval gate"},
    }


def _run_controls(run_state: Mapping[str, Any]) -> dict[str, Any]:
    state = str(run_state.get("state", ""))
    terminal = state in TERMINAL_STATES
    disabled_reason = f"terminal run state {state}" if terminal else ""
    return {
        "schema_version": "eureka.e2e_explore_run_controls.v0",
        "state": state,
        "pause": {"enabled": state == "running", "disabled_reason": "" if state == "running" else disabled_reason or "run is not running"},
        "resume": {"enabled": state == "paused", "disabled_reason": "" if state == "paused" else disabled_reason or "run is not paused"},
        "cancel": {"enabled": not terminal, "disabled_reason": "" if not terminal else disabled_reason},
        "step": {"enabled": False, "disabled_reason": "incremental stepping is reserved for a future non-terminal runner mode"},
        "replay": {"enabled": True, "disabled_reason": "", "method": "POST", "requires_operator_token": True},
    }


def _blocked_control(run_id: str, action: str, reason: str, state: str) -> dict[str, Any]:
    payload = _base_payload("explore_run_command_blocked")
    payload.update(
        {
            "status": "blocked",
            "action": action,
            "run_id": run_id,
            "state": state,
            "allowed": False,
            "blocked_reason": reason,
            "state_mutated": False,
            "store_mutation_performed": False,
        }
    )
    return payload


def _base_payload(endpoint: str) -> dict[str, Any]:
    return {
        "schema_version": EXPLORE_SCHEMA_VERSION,
        "endpoint": endpoint,
        "status": "pass",
        "warnings": [],
        "limitations": list(LIMITATIONS),
        **BOUNDARY_FLAGS,
    }


def _routes() -> dict[str, str]:
    return {
        "workspace": "/explore",
        "workspace_json": "/api/v1/explore",
        "runs": "/explore/runs",
        "runs_json": "/api/v1/explore/runs",
        "compare": "/explore/compare",
        "compare_json": "/api/v1/explore/compare",
    }


def _run_dir(runs_root: str | Path, run_id: str) -> Path:
    safe = _safe_run_id(run_id)
    root = Path(runs_root).resolve()
    path = (root / safe).resolve()
    if root != path and root not in path.parents:
        raise ResolutionRunValidationError("run path escapes durable run root")
    if not (path / "run_manifest.json").is_file():
        raise FileNotFoundError(f"run bundle not found: {safe}")
    return path


def _safe_run_id(run_id: str) -> str:
    value = str(run_id or "").strip()
    if not value or not RUN_ID_PATTERN.match(value) or ".." in value or "/" in value or "\\" in value:
        raise ResolutionRunValidationError("unsafe or missing run_id")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ResolutionRunValidationError(f"JSON file must be an object: {path.name}")
    return dict(payload)


def _load_json_optional(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return _load_json(path)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if isinstance(payload, Mapping):
            records.append(dict(payload))
    return records


def _safe_display_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def _lane_ids(lane_snapshot: Mapping[str, Any]) -> set[str]:
    lanes = lane_snapshot.get("lanes")
    if isinstance(lanes, Sequence) and not isinstance(lanes, (str, bytes)):
        return {str(item.get("lane_id") or item.get("id") or "") for item in lanes if isinstance(item, Mapping)}
    if isinstance(lanes, Mapping):
        return {str(item) for item in lanes.keys()}
    return set()


def _compare_side(detail: Mapping[str, Any]) -> dict[str, Any]:
    run = dict(detail.get("run") or {})
    result = dict(detail.get("result") or {})
    return {
        "run_id": str(run.get("run_id", "")),
        "query": str(run.get("query", "")),
        "state": str(run.get("state", "")),
        "event_count": int(detail.get("event_count", 0) or 0),
        "workunit_count": int(detail.get("workunit_count", 0) or 0),
        "result_count": int(result.get("result_count", 0) or 0),
        "validation_status": str((detail.get("validation") or {}).get("status", "")),
    }
