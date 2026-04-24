from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


EVAL_STATUSES = (
    "satisfied",
    "partial",
    "not_satisfied",
    "not_evaluable",
    "capability_gap",
)


@dataclass(frozen=True)
class ArchiveResolutionEvalTask:
    task_id: str
    raw_query: str
    query_family: str
    desired_intent: str
    desired_object_types: tuple[str, ...]
    target_constraints: dict[str, Any]
    bad_result_patterns: tuple[str, ...]
    acceptable_result_patterns: tuple[str, ...]
    minimum_granularity: str
    required_evidence: tuple[str, ...]
    expected_lanes: tuple[str, ...]
    allowed_absence_outcomes: tuple[str, ...]
    expected_plan: dict[str, Any] | None = None
    notes: str | None = None
    source_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.task_id,
            "raw_query": self.raw_query,
            "query_family": self.query_family,
            "desired_intent": self.desired_intent,
            "desired_object_types": list(self.desired_object_types),
            "target_constraints": _clone_json_like(self.target_constraints),
            "bad_result_patterns": list(self.bad_result_patterns),
            "acceptable_result_patterns": list(self.acceptable_result_patterns),
            "minimum_granularity": self.minimum_granularity,
            "required_evidence": list(self.required_evidence),
            "expected_lanes": list(self.expected_lanes),
            "allowed_absence_outcomes": list(self.allowed_absence_outcomes),
        }
        if self.expected_plan is not None:
            payload["expected_plan"] = _clone_json_like(self.expected_plan)
        if self.notes is not None:
            payload["notes"] = self.notes
        if self.source_path is not None:
            payload["source_path"] = self.source_path
        return payload


@dataclass(frozen=True)
class ArchiveResolutionEvalLoadError:
    source_path: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source_path": self.source_path,
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class ArchiveResolutionEvalLoadResult:
    eval_root: str
    schema_path: str
    task_count: int
    tasks: tuple[ArchiveResolutionEvalTask, ...] = ()
    errors: tuple[ArchiveResolutionEvalLoadError, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "eval_root": self.eval_root,
            "schema_path": self.schema_path,
            "task_count": self.task_count,
            "tasks": [task.to_dict() for task in self.tasks],
            "errors": [error.to_dict() for error in self.errors],
        }


@dataclass(frozen=True)
class EvalCheckResult:
    name: str
    status: str
    message: str
    expected: Any = None
    observed: Any = None
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        _validate_status(self.status, f"Eval check '{self.name}'")
        payload: dict[str, Any] = {
            "name": self.name,
            "status": self.status,
            "message": self.message,
        }
        if self.expected is not None:
            payload["expected"] = _clone_json_like(self.expected)
        if self.observed is not None:
            payload["observed"] = _clone_json_like(self.observed)
        if self.details is not None:
            payload["details"] = _clone_json_like(self.details)
        return payload


@dataclass(frozen=True)
class ArchiveResolutionEvalResult:
    task_id: str
    raw_query: str
    query_family: str
    planner_observed_task_kind: str | None
    planner_expected_task_kind: str | None
    planner_status: str
    search_mode: str
    search_query: str | None
    search_observed_result_count: int
    expected_result_hints: dict[str, Any]
    satisfied_checks: tuple[EvalCheckResult, ...] = ()
    partial_checks: tuple[EvalCheckResult, ...] = ()
    failed_checks: tuple[EvalCheckResult, ...] = ()
    skipped_checks: tuple[EvalCheckResult, ...] = ()
    capability_gaps: tuple[EvalCheckResult, ...] = ()
    notices: tuple[dict[str, str], ...] = ()
    overall_status: str = "not_evaluable"
    planner_observed: dict[str, Any] | None = None
    top_results: tuple[dict[str, Any], ...] = ()
    absence_summary: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        _validate_status(self.planner_status, f"Planner status for '{self.task_id}'")
        _validate_status(self.overall_status, f"Overall status for '{self.task_id}'")
        payload: dict[str, Any] = {
            "task_id": self.task_id,
            "raw_query": self.raw_query,
            "query_family": self.query_family,
            "planner_observed_task_kind": self.planner_observed_task_kind,
            "planner_expected_task_kind": self.planner_expected_task_kind,
            "planner_status": self.planner_status,
            "search_mode": self.search_mode,
            "search_query": self.search_query,
            "search_observed_result_count": self.search_observed_result_count,
            "expected_result_hints": _clone_json_like(self.expected_result_hints),
            "satisfied_checks": [check.to_dict() for check in self.satisfied_checks],
            "partial_checks": [check.to_dict() for check in self.partial_checks],
            "failed_checks": [check.to_dict() for check in self.failed_checks],
            "skipped_checks": [check.to_dict() for check in self.skipped_checks],
            "capability_gaps": [check.to_dict() for check in self.capability_gaps],
            "notices": [_clone_json_like(notice) for notice in self.notices],
            "overall_status": self.overall_status,
            "top_results": [_clone_json_like(result) for result in self.top_results],
        }
        if self.planner_observed is not None:
            payload["planner_observed"] = _clone_json_like(self.planner_observed)
        if self.absence_summary is not None:
            payload["absence_summary"] = _clone_json_like(self.absence_summary)
        return payload

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "raw_query": self.raw_query,
            "query_family": self.query_family,
            "overall_status": self.overall_status,
            "planner_status": self.planner_status,
            "planner_observed_task_kind": self.planner_observed_task_kind,
            "planner_expected_task_kind": self.planner_expected_task_kind,
            "search_mode": self.search_mode,
            "search_observed_result_count": self.search_observed_result_count,
            "capability_gap_count": len(self.capability_gaps),
            "failed_check_count": len(self.failed_checks),
            "not_evaluable_check_count": len(self.skipped_checks),
        }


@dataclass(frozen=True)
class ArchiveResolutionEvalSuiteResult:
    total_task_count: int
    status_counts: dict[str, int]
    task_results: tuple[ArchiveResolutionEvalResult, ...]
    created_at: str
    created_by_slice: str
    load_errors: tuple[ArchiveResolutionEvalLoadError, ...] = ()
    notices: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_task_count": self.total_task_count,
            "status_counts": dict(sorted(self.status_counts.items())),
            "task_summaries": [result.to_summary_dict() for result in self.task_results],
            "tasks": [result.to_dict() for result in self.task_results],
            "created_at": self.created_at,
            "created_by_slice": self.created_by_slice,
            "load_errors": [error.to_dict() for error in self.load_errors],
            "notices": [_clone_json_like(notice) for notice in self.notices],
        }


def _validate_status(status: str, label: str) -> None:
    if status not in EVAL_STATUSES:
        raise ValueError(f"{label} used unknown eval status '{status}'.")


def _clone_json_like(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _clone_json_like(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_clone_json_like(item) for item in value]
    if isinstance(value, list):
        return [_clone_json_like(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
