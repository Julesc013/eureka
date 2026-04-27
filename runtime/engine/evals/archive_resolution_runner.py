from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from json import JSONDecodeError
from pathlib import Path
import re
import tempfile
from typing import Any, Callable, Iterable, Mapping

from runtime.engine.absence import DeterministicAbsenceService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.evals.eval_result import (
    ArchiveResolutionEvalLoadError,
    ArchiveResolutionEvalLoadResult,
    ArchiveResolutionEvalResult,
    ArchiveResolutionEvalSuiteResult,
    ArchiveResolutionEvalTask,
    EvalCheckResult,
)
from runtime.engine.index import LocalIndexEngineService, LocalIndexSqliteStore
from runtime.engine.interfaces.public import (
    LocalIndexBuildRequest,
    LocalIndexQueryRequest,
    QueryPlanRequest,
    SearchAbsenceRequest,
    SearchRequest,
)
from runtime.engine.interfaces.service import (
    AbsenceService,
    LocalIndexService,
    QueryPlannerService,
    SearchService,
)
from runtime.engine.query_planner import (
    DeterministicQueryPlannerService,
    derive_search_query_from_task,
)
from runtime.engine.resolve import DeterministicSearchService, ExactMatchResolutionService
from runtime.engine.interfaces.public.query_plan import ResolutionTask
from runtime.source_registry import SourceRegistry, load_source_registry


DEFAULT_ARCHIVE_RESOLUTION_EVAL_ROOT = (
    Path(__file__).resolve().parents[3] / "evals" / "archive_resolution"
)
CREATED_BY_SLICE = "archive_resolution_eval_runner_v0"
TOP_RESULT_LIMIT = 5


def _default_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class _SearchContext:
    search_mode: str
    index_path: str | None
    index_available: bool


@dataclass(frozen=True)
class _SearchObservation:
    search_mode: str
    search_query: str | None
    result_count: int
    top_results: tuple[dict[str, Any], ...]
    absence_summary: dict[str, Any] | None
    checks: tuple[EvalCheckResult, ...]
    notices: tuple[dict[str, str], ...]


class ArchiveResolutionEvalRunner:
    def __init__(
        self,
        *,
        query_planner: QueryPlannerService,
        local_index_service: LocalIndexService | None = None,
        search_service: SearchService | None = None,
        absence_service: AbsenceService | None = None,
        eval_root: Path | str = DEFAULT_ARCHIVE_RESOLUTION_EVAL_ROOT,
        created_by_slice: str = CREATED_BY_SLICE,
        timestamp_factory: Callable[[], str] = _default_timestamp,
    ) -> None:
        self._query_planner = query_planner
        self._local_index_service = local_index_service
        self._search_service = search_service
        self._absence_service = absence_service
        self._eval_root = Path(eval_root)
        self._created_by_slice = created_by_slice
        self._timestamp_factory = timestamp_factory

    def run_suite(
        self,
        *,
        task_id: str | None = None,
        index_path: str | None = None,
        use_local_index: bool = True,
    ) -> ArchiveResolutionEvalSuiteResult:
        load_result = load_archive_resolution_eval_tasks(self._eval_root)
        selected_tasks, selection_notices = _select_tasks(load_result.tasks, task_id)

        if use_local_index and index_path is None and self._local_index_service is not None:
            with tempfile.TemporaryDirectory() as temp_dir:
                transient_index_path = str(Path(temp_dir) / "archive-resolution-eval.sqlite3")
                return self._run_loaded_suite(
                    load_result,
                    selected_tasks,
                    index_path=transient_index_path,
                    use_local_index=True,
                    suite_notices=selection_notices
                    + (
                        _notice(
                            "transient_local_index",
                            "info",
                            (
                                "Built a transient Local Index v0 database for this eval run. "
                                "The report omits the temporary path so JSON remains inspectable."
                            ),
                        ),
                    ),
                )

        return self._run_loaded_suite(
            load_result,
            selected_tasks,
            index_path=index_path,
            use_local_index=use_local_index,
            suite_notices=selection_notices,
        )

    def _run_loaded_suite(
        self,
        load_result: ArchiveResolutionEvalLoadResult,
        selected_tasks: tuple[ArchiveResolutionEvalTask, ...],
        *,
        index_path: str | None,
        use_local_index: bool,
        suite_notices: tuple[dict[str, str], ...],
    ) -> ArchiveResolutionEvalSuiteResult:
        search_context, index_notices = self._prepare_search_context(
            index_path=index_path,
            use_local_index=use_local_index,
        )
        task_results = tuple(
            self._run_task(task, search_context) for task in selected_tasks
        )
        status_counts = Counter(result.overall_status for result in task_results)
        notices = suite_notices + index_notices
        if load_result.errors:
            notices = notices + (
                _notice(
                    "eval_packet_load_errors",
                    "warning",
                    "One or more archive-resolution eval fixtures were not evaluable.",
                ),
            )
        return ArchiveResolutionEvalSuiteResult(
            total_task_count=len(task_results),
            status_counts=dict(sorted(status_counts.items())),
            task_results=task_results,
            created_at=self._timestamp_factory(),
            created_by_slice=self._created_by_slice,
            load_errors=load_result.errors,
            notices=notices,
        )

    def _prepare_search_context(
        self,
        *,
        index_path: str | None,
        use_local_index: bool,
    ) -> tuple[_SearchContext, tuple[dict[str, str], ...]]:
        if not use_local_index or self._local_index_service is None:
            if self._search_service is not None:
                return _SearchContext("deterministic_search", None, False), (
                    _notice(
                        "deterministic_search_mode",
                        "info",
                        "Local Index v0 was disabled or unavailable; using deterministic search fallback.",
                    ),
                )
            return _SearchContext("unavailable", None, False), (
                _notice(
                    "search_unavailable",
                    "warning",
                    "No Local Index v0 or deterministic search service was configured.",
                ),
            )

        if index_path is None or not index_path.strip():
            return _SearchContext("deterministic_search", None, False), (
                _notice(
                    "index_path_unavailable",
                    "warning",
                    "No index_path was available; using deterministic search fallback.",
                ),
            )

        try:
            self._local_index_service.build_index(
                LocalIndexBuildRequest.from_parts(index_path),
            )
        except Exception as error:
            if self._search_service is not None:
                return _SearchContext("deterministic_search", None, False), (
                    _notice(
                        "local_index_build_failed",
                        "warning",
                        (
                            "Local Index v0 build failed; using deterministic search fallback. "
                            f"Reason: {error}"
                        ),
                    ),
                )
            return _SearchContext("unavailable", None, False), (
                _notice(
                    "local_index_build_failed",
                    "warning",
                    f"Local Index v0 build failed and no fallback search service was configured: {error}",
                ),
            )

        return _SearchContext("local_index", index_path, True), (
            _notice(
                "local_index_built_for_eval",
                "info",
                "Built Local Index v0 once for this synchronous archive-resolution eval suite.",
            ),
        )

    def _run_task(
        self,
        task: ArchiveResolutionEvalTask,
        search_context: _SearchContext,
    ) -> ArchiveResolutionEvalResult:
        planner_task: ResolutionTask | None = None
        planner_observed: dict[str, Any] | None = None
        planner_exception: Exception | None = None
        try:
            planner_task = self._query_planner.plan_query(
                QueryPlanRequest.from_parts(task.raw_query),
            )
            planner_observed = planner_task.to_dict()
        except Exception as error:
            planner_exception = error

        planner_checks, planner_status = _evaluate_planner(task, planner_task, planner_exception)
        search_observation = self._observe_search(task, planner_task, search_context)
        all_checks = (
            planner_checks
            + search_observation.checks
            + _evaluate_result_refinement_checks(task, search_observation.top_results)
        )
        satisfied_checks = tuple(check for check in all_checks if check.status == "satisfied")
        partial_checks = tuple(check for check in all_checks if check.status == "partial")
        failed_checks = tuple(check for check in all_checks if check.status == "not_satisfied")
        skipped_checks = tuple(check for check in all_checks if check.status == "not_evaluable")
        capability_gaps = tuple(check for check in all_checks if check.status == "capability_gap")
        overall_status = _overall_status(
            planner_status=planner_status,
            failed_checks=failed_checks,
            skipped_checks=skipped_checks,
            capability_gaps=capability_gaps,
            partial_checks=partial_checks,
            satisfied_checks=satisfied_checks,
        )
        return ArchiveResolutionEvalResult(
            task_id=task.task_id,
            raw_query=task.raw_query,
            query_family=task.query_family,
            planner_observed_task_kind=planner_task.task_kind if planner_task is not None else None,
            planner_expected_task_kind=_expected_task_kind(task),
            planner_status=planner_status,
            search_mode=search_observation.search_mode,
            search_query=search_observation.search_query,
            search_observed_result_count=search_observation.result_count,
            expected_result_hints=_expected_result_hints(task),
            satisfied_checks=satisfied_checks,
            partial_checks=partial_checks,
            failed_checks=failed_checks,
            skipped_checks=skipped_checks,
            capability_gaps=capability_gaps,
            notices=(
                _notice(
                    "eval_runner_scope",
                    "info",
                    (
                        "Archive Resolution Eval Runner v0 records deterministic planner, local search, "
                        "absence behavior, and bounded lane/user-cost annotations only; production ranking, "
                        "fuzzy, vector, LLM, crawling, and live sync are intentionally out of scope."
                    ),
                ),
            )
            + search_observation.notices,
            overall_status=overall_status,
            planner_observed=planner_observed,
            top_results=search_observation.top_results,
            absence_summary=search_observation.absence_summary,
        )

    def _observe_search(
        self,
        task: ArchiveResolutionEvalTask,
        planner_task: ResolutionTask | None,
        search_context: _SearchContext,
    ) -> _SearchObservation:
        if planner_task is None:
            return _SearchObservation(
                search_mode=search_context.search_mode,
                search_query=None,
                result_count=0,
                top_results=(),
                absence_summary=None,
                checks=(
                    EvalCheckResult(
                        name="search.not_evaluable_without_plan",
                        status="not_evaluable",
                        message="Search was skipped because the raw query could not be planned.",
                    ),
                ),
                notices=(),
            )

        search_query = derive_search_query_from_task(planner_task)
        if search_context.search_mode == "local_index" and search_context.index_available:
            return self._observe_local_index_search(task, search_context, search_query)

        if search_context.search_mode == "deterministic_search" and self._search_service is not None:
            return self._observe_deterministic_search(task, search_query)

        return _SearchObservation(
            search_mode=search_context.search_mode,
            search_query=search_query,
            result_count=0,
            top_results=(),
            absence_summary=None,
            checks=(
                EvalCheckResult(
                    name="search.path_available",
                    status="not_evaluable",
                    message="No bounded local search path was available for this eval task.",
                ),
            ),
            notices=(
                _notice(
                    "search_not_evaluable",
                    "warning",
                    "No bounded local search path was available for this eval task.",
                ),
            ),
        )

    def _observe_local_index_search(
        self,
        task: ArchiveResolutionEvalTask,
        search_context: _SearchContext,
        search_query: str,
    ) -> _SearchObservation:
        if self._local_index_service is None or search_context.index_path is None:
            return self._observe_deterministic_or_unavailable(task, search_query)
        try:
            query_result = self._local_index_service.query_index(
                LocalIndexQueryRequest.from_parts(search_context.index_path, search_query),
            )
        except Exception as error:
            if self._search_service is not None:
                fallback = self._observe_deterministic_search(task, search_query)
                return _SearchObservation(
                    search_mode="deterministic_search",
                    search_query=fallback.search_query,
                    result_count=fallback.result_count,
                    top_results=fallback.top_results,
                    absence_summary=fallback.absence_summary,
                    checks=fallback.checks,
                    notices=fallback.notices
                    + (
                        _notice(
                            "local_index_query_failed",
                            "warning",
                            (
                                "Local Index v0 query failed; used deterministic search fallback. "
                                f"Reason: {error}"
                            ),
                        ),
                    ),
                )
            return _SearchObservation(
                search_mode="local_index",
                search_query=search_query,
                result_count=0,
                top_results=(),
                absence_summary=None,
                checks=(
                    EvalCheckResult(
                        name="search.local_index_query",
                        status="not_evaluable",
                        message=f"Local Index v0 query failed: {error}",
                    ),
                ),
                notices=(
                    _notice("local_index_query_failed", "warning", str(error)),
                ),
            )

        top_results = tuple(item.to_dict() for item in query_result.results[:TOP_RESULT_LIMIT])
        absence_summary = (
            self._absence_summary(search_query) if not query_result.results else None
        )
        return _SearchObservation(
            search_mode="local_index",
            search_query=search_query,
            result_count=len(query_result.results),
            top_results=top_results,
            absence_summary=absence_summary,
            checks=_evaluate_search(task, top_results, absence_summary),
            notices=tuple(notice.to_dict() for notice in query_result.notices),
        )

    def _observe_deterministic_or_unavailable(
        self,
        task: ArchiveResolutionEvalTask,
        search_query: str,
    ) -> _SearchObservation:
        if self._search_service is not None:
            return self._observe_deterministic_search(task, search_query)
        return _SearchObservation(
            search_mode="unavailable",
            search_query=search_query,
            result_count=0,
            top_results=(),
            absence_summary=None,
            checks=(
                EvalCheckResult(
                    name="search.path_available",
                    status="not_evaluable",
                    message="No deterministic search fallback was configured.",
                ),
            ),
            notices=(),
        )

    def _observe_deterministic_search(
        self,
        task: ArchiveResolutionEvalTask,
        search_query: str,
    ) -> _SearchObservation:
        if self._search_service is None:
            return self._observe_deterministic_or_unavailable(task, search_query)
        response = self._search_service.search(SearchRequest.from_parts(search_query))
        top_results = tuple(_search_result_to_dict(item) for item in response.results[:TOP_RESULT_LIMIT])
        absence_summary = self._absence_summary(search_query) if not response.results else None
        notices: tuple[dict[str, str], ...] = ()
        if response.absence is not None:
            notices = (response.absence.to_dict(),)
        return _SearchObservation(
            search_mode="deterministic_search",
            search_query=search_query,
            result_count=len(response.results),
            top_results=top_results,
            absence_summary=absence_summary,
            checks=_evaluate_search(task, top_results, absence_summary),
            notices=notices,
        )

    def _absence_summary(self, search_query: str) -> dict[str, Any] | None:
        if self._absence_service is None:
            return None
        try:
            report = self._absence_service.explain_search_miss(
                SearchAbsenceRequest.from_parts(search_query),
            )
        except Exception as error:
            return {
                "status": "not_evaluable",
                "likely_reason_code": "absence_reasoning_failed",
                "reason_message": str(error),
                "near_match_count": 0,
            }
        return {
            "status": report.status,
            "likely_reason_code": report.likely_reason_code,
            "reason_message": report.reason_message,
            "checked_source_families": list(report.checked_source_families),
            "checked_record_count": report.checked_record_count,
            "checked_subject_count": report.checked_subject_count,
            "near_match_count": len(report.near_matches),
            "next_steps": list(report.next_steps),
        }


def load_archive_resolution_eval_tasks(
    eval_root: Path | str = DEFAULT_ARCHIVE_RESOLUTION_EVAL_ROOT,
) -> ArchiveResolutionEvalLoadResult:
    root = Path(eval_root)
    schema_path = root / "task.schema.yaml"
    tasks_dir = root / "tasks"
    errors: list[ArchiveResolutionEvalLoadError] = []
    schema = _read_json_object(schema_path, errors)
    required_fields = _schema_required_fields(schema, schema_path, errors)
    allowed_fields = _schema_allowed_fields(schema)

    if not tasks_dir.is_dir():
        errors.append(
            ArchiveResolutionEvalLoadError(
                source_path=str(tasks_dir),
                code="tasks_dir_missing",
                message=f"Archive-resolution eval tasks directory '{tasks_dir}' was not found.",
            )
        )
        return ArchiveResolutionEvalLoadResult(
            eval_root=str(root),
            schema_path=str(schema_path),
            task_count=0,
            errors=tuple(errors),
        )

    tasks: list[ArchiveResolutionEvalTask] = []
    seen_task_ids: set[str] = set()
    for task_path in sorted(tasks_dir.glob("*.yaml")):
        payload = _read_json_object(task_path, errors)
        if payload is None:
            continue
        try:
            task = _task_from_payload(
                payload,
                task_path=task_path,
                required_fields=required_fields,
                allowed_fields=allowed_fields,
            )
        except ValueError as error:
            errors.append(
                ArchiveResolutionEvalLoadError(
                    source_path=str(task_path),
                    code="malformed_task",
                    message=str(error),
                )
            )
            continue
        if task.task_id in seen_task_ids:
            errors.append(
                ArchiveResolutionEvalLoadError(
                    source_path=str(task_path),
                    code="duplicate_task_id",
                    message=f"Duplicate archive-resolution eval task id '{task.task_id}'.",
                )
            )
            continue
        seen_task_ids.add(task.task_id)
        tasks.append(task)

    return ArchiveResolutionEvalLoadResult(
        eval_root=str(root),
        schema_path=str(schema_path),
        task_count=len(tasks),
        tasks=tuple(tasks),
        errors=tuple(errors),
    )


def build_default_archive_resolution_eval_runner(
    *,
    eval_root: Path | str = DEFAULT_ARCHIVE_RESOLUTION_EVAL_ROOT,
    timestamp_factory: Callable[[], str] = _default_timestamp,
) -> ArchiveResolutionEvalRunner:
    catalog = _build_default_catalog()
    source_registry = load_source_registry()
    search_service = DeterministicSearchService(catalog)
    resolution_service = ExactMatchResolutionService(catalog)
    absence_service = DeterministicAbsenceService(
        catalog,
        resolution_service=resolution_service,
        search_service=search_service,
    )
    index_service = LocalIndexEngineService(
        catalog=catalog,
        source_registry=source_registry,
        sqlite_store=LocalIndexSqliteStore(),
    )
    return ArchiveResolutionEvalRunner(
        query_planner=DeterministicQueryPlannerService(),
        local_index_service=index_service,
        search_service=search_service,
        absence_service=absence_service,
        eval_root=eval_root,
        timestamp_factory=timestamp_factory,
    )


def build_archive_resolution_eval_runner_from_corpus(
    catalog: NormalizedCatalog,
    source_registry: SourceRegistry,
    *,
    eval_root: Path | str = DEFAULT_ARCHIVE_RESOLUTION_EVAL_ROOT,
    timestamp_factory: Callable[[], str] = _default_timestamp,
) -> ArchiveResolutionEvalRunner:
    search_service = DeterministicSearchService(catalog)
    resolution_service = ExactMatchResolutionService(catalog)
    absence_service = DeterministicAbsenceService(
        catalog,
        resolution_service=resolution_service,
        search_service=search_service,
    )
    index_service = LocalIndexEngineService(
        catalog=catalog,
        source_registry=source_registry,
        sqlite_store=LocalIndexSqliteStore(),
    )
    return ArchiveResolutionEvalRunner(
        query_planner=DeterministicQueryPlannerService(),
        local_index_service=index_service,
        search_service=search_service,
        absence_service=absence_service,
        eval_root=eval_root,
        timestamp_factory=timestamp_factory,
    )


def format_archive_resolution_eval_summary(
    suite: ArchiveResolutionEvalSuiteResult,
) -> str:
    lines = [
        "Archive resolution evals",
        f"created_by_slice: {suite.created_by_slice}",
        f"task_count: {suite.total_task_count}",
        f"status_counts: {_mapping_text(suite.status_counts)}",
    ]
    if suite.load_errors:
        lines.extend(["", "Load errors"])
        for error in suite.load_errors:
            lines.append(f"- {error.code}: {error.source_path}: {error.message}")
    lines.extend(["", "Tasks"])
    for result in suite.task_results:
        lines.append(
            "- "
            f"{result.task_id}: {result.overall_status} "
            f"(planner={result.planner_status}, search={result.search_mode}, "
            f"results={result.search_observed_result_count})"
        )
    capability_gap_results = [
        result for result in suite.task_results if result.capability_gaps
    ]
    if capability_gap_results:
        lines.extend(["", "Capability gaps"])
        for result in capability_gap_results:
            first_gap = result.capability_gaps[0]
            lines.append(f"- {result.task_id}: {first_gap.message}")
    failed_results = [result for result in suite.task_results if result.failed_checks]
    if failed_results:
        lines.extend(["", "Failed checks"])
        for result in failed_results:
            first_failure = result.failed_checks[0]
            lines.append(f"- {result.task_id}: {first_failure.name}: {first_failure.message}")
    return "\n".join(lines) + "\n"


def _select_tasks(
    tasks: tuple[ArchiveResolutionEvalTask, ...],
    task_id: str | None,
) -> tuple[tuple[ArchiveResolutionEvalTask, ...], tuple[dict[str, str], ...]]:
    normalized_task_id = (task_id or "").strip()
    if not normalized_task_id:
        return tasks, ()
    selected = tuple(task for task in tasks if task.task_id == normalized_task_id)
    if selected:
        return selected, ()
    return (), (
        _notice(
            "eval_task_not_found",
            "warning",
            f"Archive-resolution eval task '{normalized_task_id}' was not found.",
        ),
    )


def _evaluate_planner(
    task: ArchiveResolutionEvalTask,
    planner_task: ResolutionTask | None,
    planner_exception: Exception | None,
) -> tuple[tuple[EvalCheckResult, ...], str]:
    if planner_exception is not None:
        return (
            (
                EvalCheckResult(
                    name="planner.execution",
                    status="not_evaluable",
                    message=f"Query Planner v0 could not plan the raw query: {planner_exception}",
                ),
            ),
            "not_evaluable",
        )
    if planner_task is None:
        return (
            (
                EvalCheckResult(
                    name="planner.execution",
                    status="not_evaluable",
                    message="Query Planner v0 did not return a plan.",
                ),
            ),
            "not_evaluable",
        )
    if task.expected_plan is None:
        return (
            (
                EvalCheckResult(
                    name="planner.expected_plan",
                    status="not_evaluable",
                    message="This fixture does not declare an expected_plan block.",
                ),
            ),
            "not_evaluable",
        )

    checks: list[EvalCheckResult] = [
        _check_exact(
            "planner.task_kind",
            expected=task.expected_plan.get("task_kind"),
            observed=planner_task.task_kind,
            success_message="Planner task_kind matched expected_plan.",
            failure_message="Planner task_kind did not match expected_plan.",
        ),
        _check_exact(
            "planner.object_type",
            expected=task.expected_plan.get("object_type"),
            observed=planner_task.object_type,
            success_message="Planner object_type matched expected_plan.",
            failure_message="Planner object_type did not match expected_plan.",
        ),
    ]

    expected_constraints = task.expected_plan.get("constraints")
    if isinstance(expected_constraints, Mapping):
        for key, expected_value in sorted(expected_constraints.items()):
            checks.append(
                _check_constraint(
                    key,
                    expected=expected_value,
                    observed=planner_task.constraints.get(key),
                )
            )

    for preferred in _string_iter(task.expected_plan.get("prefer")):
        checks.append(
            _check_membership(
                f"planner.prefer.{preferred}",
                expected=preferred,
                observed=planner_task.prefer,
                success_message=f"Planner prefer includes '{preferred}'.",
                failure_message=f"Planner prefer does not include '{preferred}'.",
            )
        )
    for excluded in _string_iter(task.expected_plan.get("exclude")):
        checks.append(
            _check_membership(
                f"planner.exclude.{excluded}",
                expected=excluded,
                observed=planner_task.exclude,
                success_message=f"Planner exclude includes '{excluded}'.",
                failure_message=f"Planner exclude does not include '{excluded}'.",
            )
        )

    status = _aggregate_check_status(tuple(checks))
    return tuple(checks), status


def _evaluate_search(
    task: ArchiveResolutionEvalTask,
    top_results: tuple[dict[str, Any], ...],
    absence_summary: dict[str, Any] | None,
) -> tuple[EvalCheckResult, ...]:
    if not top_results:
        checks: list[EvalCheckResult] = [
            EvalCheckResult(
                name="search.expected_result_hints",
                status="capability_gap",
                message=(
                    "No bounded local result matched this hard fixture. Current bootstrap corpus "
                    "does not contain the direct artifact, member, article, or evidence shape required "
                    "to satisfy the task."
                ),
                expected=_expected_result_hints(task),
                observed={"result_count": 0},
            )
        ]
        if absence_summary is None:
            checks.append(
                EvalCheckResult(
                    name="absence.reasoning",
                    status="not_evaluable",
                    message="No bounded absence report was produced for the empty search result.",
                )
            )
        else:
            checks.append(
                EvalCheckResult(
                    name="absence.reasoning",
                    status="partial",
                    message="Absence reasoning explained the empty bounded search result.",
                    observed=absence_summary,
                )
            )
        return tuple(checks)

    evidence_report = _structured_expected_result_evidence(task, top_results)
    if evidence_report["status"] == "satisfied":
        return (
            EvalCheckResult(
                name="search.expected_result_hints",
                status="satisfied",
                message=(
                    "Observed bounded results include source-backed structured evidence for "
                    "the required hard-eval result hints."
                ),
                expected=_expected_result_hints(task),
                observed=evidence_report,
            ),
        )
    if evidence_report["status"] == "partial":
        return (
            EvalCheckResult(
                name="search.expected_result_hints",
                status="partial",
                message=(
                    "Observed bounded results include source-backed evidence for the core "
                    "task intent, but one or more hard expected-result hints remain unmet."
                ),
                expected=_expected_result_hints(task),
                observed=evidence_report,
            ),
        )
    return (
        EvalCheckResult(
            name="search.expected_result_hints",
            status="not_satisfied",
            message=(
                "Search returned bounded results, but current source-backed evidence did not "
                "satisfy the structured hard expected-result hints. Eval Runner v0 still "
                "does not infer semantic relevance."
            ),
            expected=_expected_result_hints(task),
            observed=evidence_report,
        ),
    )


def _evaluate_result_refinement_checks(
    task: ArchiveResolutionEvalTask,
    top_results: tuple[dict[str, Any], ...],
) -> tuple[EvalCheckResult, ...]:
    shape = _result_shape_summary(task, top_results)
    return (
        _check_primary_result_shape(task, shape),
        _check_expected_lanes(task, shape),
        _check_bad_result_patterns(task, shape),
    )


def _result_shape_summary(
    task: ArchiveResolutionEvalTask,
    top_results: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    evidence_report = (
        _structured_expected_result_evidence(task, top_results)
        if top_results
        else {
            "status": "not_evaluable",
            "source_ids": [],
            "source_families": [],
            "member_paths": [],
            "representation_ids": [],
            "artifact_locators": [],
            "compatibility_evidence_count": 0,
            "matched_platform_terms": [],
            "matched_hardware_terms": [],
            "matched_product_terms": [],
            "matched_function_terms": [],
        }
    )
    primary = top_results[0] if top_results else None
    primary_shape = _primary_candidate_shape(task, primary) if primary is not None else None
    shape_status, limitations = _minimum_granularity_status(
        task,
        primary_shape=primary_shape,
        evidence_report=evidence_report,
    )
    return {
        "top_result_count": len(top_results),
        "primary_candidate": primary_shape,
        "active_lanes": _active_lanes(top_results),
        "source_ids": evidence_report["source_ids"],
        "source_families": evidence_report["source_families"],
        "member_paths": evidence_report["member_paths"],
        "representation_ids": evidence_report["representation_ids"],
        "artifact_locators": evidence_report["artifact_locators"],
        "compatibility_evidence_count": evidence_report["compatibility_evidence_count"],
        "matched_platform_terms": evidence_report["matched_platform_terms"],
        "matched_hardware_terms": evidence_report["matched_hardware_terms"],
        "matched_product_terms": evidence_report["matched_product_terms"],
        "matched_function_terms": evidence_report["matched_function_terms"],
        "minimum_granularity": task.minimum_granularity,
        "minimum_granularity_status": shape_status,
        "limitations": limitations,
    }


def _primary_candidate_shape(
    task: ArchiveResolutionEvalTask,
    result: Mapping[str, Any],
) -> dict[str, Any]:
    primary_artifacts = tuple(
        item
        for item in _result_file_like_strings((dict(result),))
        if _looks_like_artifact_locator(item)
    )
    member_path = result.get("member_path") if isinstance(result.get("member_path"), str) else None
    record_kind = str(result.get("record_kind") or "unknown")
    member_like = record_kind in {"member", "synthetic_member"}
    primary_lane = str(result.get("primary_lane") or "other")
    target_ref = str(result.get("target_ref") or "")
    route_hints = result.get("route_hints") if isinstance(result.get("route_hints"), Mapping) else {}
    representation_id = result.get("representation_id") or route_hints.get("representation_id")
    user_cost_score = result.get("user_cost_score")
    compatibility_evidence = result.get("compatibility_evidence")
    compatibility_count = len(compatibility_evidence) if isinstance(compatibility_evidence, list) else 0
    return {
        "target_ref": target_ref,
        "label": str(result.get("label") or ""),
        "candidate_kind": _candidate_kind(task, result, primary_artifacts),
        "record_kind": record_kind,
        "primary_lane": primary_lane,
        "result_lanes": list(_string_iter(result.get("result_lanes"))),
        "user_cost_score": user_cost_score if isinstance(user_cost_score, int) else None,
        "user_cost_reasons": list(_string_iter(result.get("user_cost_reasons"))),
        "source_id": result.get("source_id"),
        "source_family": result.get("source_family"),
        "evidence_count": len(result.get("evidence")) if isinstance(result.get("evidence"), list) else 0,
        "evidence_kinds": _evidence_kinds(result),
        "compatibility_evidence_count": compatibility_count,
        "compatibility_summary": result.get("compatibility_summary"),
        "representation_id": representation_id,
        "member_path": member_path,
        "parent_target_ref": result.get("parent_target_ref") or (target_ref if record_kind == "member" else None),
        "artifact_locators": list(primary_artifacts),
        "has_direct_artifact_locator": _has_direct_artifact_locator(primary_artifacts),
        "is_member_result": member_like,
        "is_parent_context": "parent_bundle_context_only" in set(_string_iter(result.get("user_cost_reasons"))),
    }


def _candidate_kind(
    task: ArchiveResolutionEvalTask,
    result: Mapping[str, Any],
    artifact_locators: tuple[str, ...],
) -> str:
    text = _compact_text(" ".join(_flatten_strings(result)))
    record_kind = str(result.get("record_kind") or "").casefold()
    if record_kind == "member":
        if any(".inf" in item.casefold() for item in artifact_locators) or "driver" in text:
            return "driver"
        if "readme" in text or "manual" in text:
            return "documentation"
        return "member"
    if any(".inf" in item.casefold() for item in artifact_locators) or "driver" in text:
        return "driver"
    if "registryrepair" in text or "registry" in _compact_text(task.raw_query):
        return "utility"
    if "firefox" in text and "release" in text:
        return "software_release"
    if any(".exe" in item.casefold() or "installer" in item.casefold() for item in artifact_locators):
        return "installer"
    if "readme" in text or "manual" in text or "documentation" in text:
        return "documentation"
    if record_kind in {"resolved_object", "state_or_release"}:
        return "bundle" if "bundle" in text or "archive" in text else "trace"
    return record_kind or "unknown"


def _minimum_granularity_status(
    task: ArchiveResolutionEvalTask,
    *,
    primary_shape: Mapping[str, Any] | None,
    evidence_report: Mapping[str, Any],
) -> tuple[str, list[str]]:
    if primary_shape is None:
        return "not_evaluable", ["no_result"]

    limitations: list[str] = []
    source_backed = bool(primary_shape.get("source_id") or evidence_report.get("source_ids"))
    if not source_backed:
        limitations.append("missing_source_backing")

    minimum = task.minimum_granularity.casefold()
    primary_is_member = bool(primary_shape.get("is_member_result"))
    primary_has_direct_artifact = bool(primary_shape.get("has_direct_artifact_locator"))
    aggregate_has_artifact = bool(evidence_report.get("artifact_locators"))
    has_representation = bool(primary_shape.get("representation_id") or evidence_report.get("representation_ids"))
    has_member_path = bool(primary_shape.get("member_path") or evidence_report.get("member_paths"))
    has_platform = bool(evidence_report.get("matched_platform_terms"))
    has_function = bool(evidence_report.get("matched_function_terms"))
    has_hardware = bool(evidence_report.get("matched_hardware_terms"))
    has_product = bool(evidence_report.get("matched_product_terms"))

    if minimum == "direct_driver_artifact_or_member":
        if primary_is_member and primary_has_direct_artifact and has_hardware and has_platform:
            return "satisfied", limitations
        if has_member_path and aggregate_has_artifact and has_hardware and has_platform:
            limitations.append("best_candidate_not_confirmed_as_driver_member")
            return "partial", limitations
        limitations.append("missing_driver_member_or_platform_hardware_evidence")
        return "not_satisfied", limitations

    if minimum == "versioned_release_artifact":
        release_identity = _release_identity_present(
            tuple(str(term) for term in evidence_report.get("matched_product_terms", [])),
            _compact_text(" ".join(_flatten_strings(evidence_report))),
        )
        if release_identity and aggregate_has_artifact and has_platform:
            return "satisfied", limitations
        limitations.append("exact_latest_compatible_release_not_proven")
        return "partial" if source_backed and has_product and has_platform else "not_satisfied", limitations

    if minimum == "direct_artifact_or_identity_trace":
        if primary_has_direct_artifact and has_function and has_platform:
            return "satisfied", limitations
        if source_backed and has_function and has_platform and (has_member_path or aggregate_has_artifact):
            limitations.append("concrete_identity_or_direct_installer_not_proven")
            return "partial", limitations
        limitations.append("missing_function_platform_or_identity_trace")
        return "not_satisfied", limitations

    if minimum == "direct_artifact_or_extracted_member":
        if source_backed and primary_has_direct_artifact and (has_platform or has_function):
            return "satisfied", limitations
        if source_backed and aggregate_has_artifact and (has_representation or has_member_path):
            limitations.append("best_candidate_is_context_not_direct_artifact")
            return "partial", limitations
        limitations.append("missing_direct_artifact_or_member")
        return "not_satisfied", limitations

    if minimum == "article_or_page_range":
        limitations.append("article_or_page_range_evidence_not_available")
        return "not_evaluable", limitations

    return ("satisfied" if source_backed else "not_satisfied"), limitations


def _check_primary_result_shape(
    task: ArchiveResolutionEvalTask,
    shape: Mapping[str, Any],
) -> EvalCheckResult:
    status = str(shape.get("minimum_granularity_status"))
    if status == "not_evaluable":
        return EvalCheckResult(
            name="result_shape.primary_candidate",
            status="not_evaluable",
            message="No bounded primary candidate was available for result-shape evaluation.",
            expected={
                "minimum_granularity": task.minimum_granularity,
                "desired_object_types": list(task.desired_object_types),
            },
            observed=shape,
        )
    if status == "satisfied":
        return EvalCheckResult(
            name="result_shape.primary_candidate",
            status="satisfied",
            message="Primary candidate shape satisfies the strict minimum granularity for this hard task.",
            expected={
                "minimum_granularity": task.minimum_granularity,
                "desired_object_types": list(task.desired_object_types),
            },
            observed=shape,
        )
    if status == "partial":
        return EvalCheckResult(
            name="result_shape.primary_candidate",
            status="partial",
            message="Primary candidate is source-backed but still misses one or more strict result-shape requirements.",
            expected={
                "minimum_granularity": task.minimum_granularity,
                "desired_object_types": list(task.desired_object_types),
            },
            observed=shape,
        )
    return EvalCheckResult(
        name="result_shape.primary_candidate",
        status="not_satisfied",
        message="Primary candidate shape does not satisfy the minimum result granularity for this hard task.",
        expected={
            "minimum_granularity": task.minimum_granularity,
            "desired_object_types": list(task.desired_object_types),
        },
        observed=shape,
    )


def _check_expected_lanes(
    task: ArchiveResolutionEvalTask,
    shape: Mapping[str, Any],
) -> EvalCheckResult:
    primary = shape.get("primary_candidate")
    if not isinstance(primary, Mapping):
        return EvalCheckResult(
            name="lanes.expected_lanes",
            status="not_evaluable",
            message="No primary candidate was available for lane evaluation.",
            expected=list(task.expected_lanes),
            observed=shape,
        )

    expected_lanes = set(task.expected_lanes)
    active_lanes = set(_string_iter(shape.get("active_lanes")))
    primary_lane = str(primary.get("primary_lane") or "")
    matched_lanes = sorted(expected_lanes & active_lanes)
    direct_member = bool(primary.get("is_member_result")) and bool(primary.get("has_direct_artifact_locator"))
    low_user_cost = isinstance(primary.get("user_cost_score"), int) and int(primary["user_cost_score"]) <= 2
    preferred_direct_lane_satisfied = (
        "best_direct_answer" not in expected_lanes
        or direct_member
        or primary_lane == "best_direct_answer"
    )
    installable_lane_satisfied = (
        "installable_or_usable_now" not in expected_lanes
        or primary_lane == "installable_or_usable_now"
        or (direct_member and low_user_cost)
    )
    observed = {
        "expected_lanes": list(task.expected_lanes),
        "active_lanes": sorted(active_lanes),
        "primary_lane": primary_lane,
        "matched_lanes": matched_lanes,
        "direct_member_counts_as_best_direct_answer": direct_member and low_user_cost,
        "preferred_direct_lane_satisfied": preferred_direct_lane_satisfied,
        "installable_lane_satisfied": installable_lane_satisfied,
        "primary_candidate": primary,
    }
    if primary_lane in expected_lanes and preferred_direct_lane_satisfied and installable_lane_satisfied:
        return EvalCheckResult(
            name="lanes.expected_lanes",
            status="satisfied",
            message="Primary candidate uses an expected lane and satisfies direct/member usefulness expectations.",
            expected=list(task.expected_lanes),
            observed=observed,
        )
    if matched_lanes:
        return EvalCheckResult(
            name="lanes.expected_lanes",
            status="partial",
            message="Some expected lanes are present, but the primary candidate does not yet satisfy the strict lane shape.",
            expected=list(task.expected_lanes),
            observed=observed,
        )
    if shape.get("source_ids") or primary.get("source_id"):
        return EvalCheckResult(
            name="lanes.expected_lanes",
            status="partial",
            message=(
                "Current results are source-backed, but their lanes do not yet match the "
                "strict expected lane set for this hard task."
            ),
            expected=list(task.expected_lanes),
            observed=observed,
        )
    return EvalCheckResult(
        name="lanes.expected_lanes",
        status="not_satisfied",
        message="No current result lane matched the expected lane set for this hard task.",
        expected=list(task.expected_lanes),
        observed=observed,
    )


def _check_bad_result_patterns(
    task: ArchiveResolutionEvalTask,
    shape: Mapping[str, Any],
) -> EvalCheckResult:
    primary = shape.get("primary_candidate")
    if not isinstance(primary, Mapping):
        return EvalCheckResult(
            name="ranking.bad_result_patterns",
            status="not_evaluable",
            message="No primary candidate was available for bad-result evaluation.",
            expected=list(task.bad_result_patterns),
            observed=shape,
        )

    pattern_results = [
        _bad_result_pattern_status(pattern, task=task, shape=shape)
        for pattern in task.bad_result_patterns
    ]
    triggered = [item for item in pattern_results if item["triggered"]]
    observed = {
        "patterns": pattern_results,
        "primary_candidate": primary,
        "limitations": shape.get("limitations", []),
    }
    if triggered:
        return EvalCheckResult(
            name="ranking.bad_result_patterns",
            status="not_satisfied",
            message="A known bad-result pattern appears to be treated as the primary result shape.",
            expected=list(task.bad_result_patterns),
            observed=observed,
        )
    return EvalCheckResult(
        name="ranking.bad_result_patterns",
        status="satisfied",
        message="No known bad-result pattern was accepted as the primary bounded result.",
        expected=list(task.bad_result_patterns),
        observed=observed,
    )


def _bad_result_pattern_status(
    pattern: str,
    *,
    task: ArchiveResolutionEvalTask,
    shape: Mapping[str, Any],
) -> dict[str, Any]:
    compact_pattern = _compact_text(pattern)
    primary = shape.get("primary_candidate")
    primary_text = _compact_text(" ".join(_flatten_strings(primary)))
    member_paths = tuple(str(path) for path in shape.get("member_paths", []))
    artifact_paths = tuple(str(path) for path in shape.get("artifact_locators", []))
    has_artifact = _has_direct_artifact_locator(artifact_paths)
    has_member = bool(member_paths)
    has_platform = bool(shape.get("matched_platform_terms"))
    has_hardware = bool(shape.get("matched_hardware_terms"))
    has_function = bool(shape.get("matched_function_terms"))
    primary_is_parent_context = bool(isinstance(primary, Mapping) and primary.get("is_parent_context"))

    triggered = False
    reason = "pattern_avoided"
    if "operatingsystemiso" in compact_pattern or "installmedia" in compact_pattern:
        triggered = "iso" in primary_text or "operatingsystemimage" in primary_text
        reason = "primary_result_looks_like_os_media" if triggered else "no_os_media_primary"
    elif "wholesupportcds" in compact_pattern:
        triggered = primary_is_parent_context and not has_member
        reason = "parent_support_cd_without_member" if triggered else "member_or_file_listing_present"
    elif "manualsorspecsheets" in compact_pattern:
        triggered = "manual" in primary_text and not has_artifact
        reason = "manual_without_driver_artifact" if triggered else "driver_artifact_or_non_manual_primary"
    elif "wrongoperatingsystem" in compact_pattern or "wronghardware" in compact_pattern:
        triggered = not (has_platform and has_hardware)
        reason = "missing_requested_platform_or_hardware" if triggered else "requested_platform_and_hardware_present"
    elif "latestfirefoxrelease" in compact_pattern or "releasepageswithout" in compact_pattern:
        triggered = not has_platform
        reason = "release_trace_without_platform_evidence" if triggered else "platform_evidence_present"
    elif "browsercollections" in compact_pattern:
        triggered = primary_is_parent_context and not has_artifact
        reason = "browser_collection_without_release_or_asset" if triggered else "not_collection_only_primary"
    elif "genericftpclientlists" in compact_pattern:
        triggered = (not has_function) or ("generic" in primary_text and not has_artifact)
        reason = "generic_list_without_artifact" if triggered else "function_or_member_evidence_present"
    elif "modernsynctools" in compact_pattern:
        triggered = "sync" in primary_text and "ftp" not in primary_text
        reason = "modern_sync_tool_primary" if triggered else "no_modern_sync_tool_primary"
    elif "colorhintwithoutftp" in compact_pattern:
        triggered = not has_function
        reason = "color_hint_without_function_evidence" if triggered else "function_evidence_present"
    elif "genericregistryadvice" in compact_pattern:
        triggered = "advice" in primary_text and not has_artifact
        reason = "generic_advice_without_artifact" if triggered else "artifact_or_tool_trace_present"
    elif "modernregistrycleaners" in compact_pattern:
        triggered = "modern" in primary_text and not has_platform
        reason = "modern_tool_without_requested_platform" if triggered else "requested_platform_evidence_present"
    elif "genericsoftwaredumps" in compact_pattern or "bundleonlyresults" in compact_pattern:
        triggered = primary_is_parent_context and not (has_member or has_artifact)
        reason = "parent_bundle_without_member_or_artifact" if triggered else "member_or_artifact_visible"
    else:
        triggered = False

    return {
        "pattern": pattern,
        "triggered": triggered,
        "reason": reason,
    }


def _active_lanes(top_results: tuple[dict[str, Any], ...]) -> list[str]:
    lanes: set[str] = set()
    for result in top_results:
        primary_lane = result.get("primary_lane")
        if isinstance(primary_lane, str) and primary_lane:
            lanes.add(primary_lane)
        lanes.update(_string_iter(result.get("result_lanes")))
    return sorted(lanes)


def _evidence_kinds(result: Mapping[str, Any]) -> list[str]:
    kinds: set[str] = set()
    for evidence in _string_iter(result.get("evidence")):
        first = evidence.split(" ", 1)[0].split(":", 1)[0]
        if first:
            kinds.add(first)
    if result.get("compatibility_evidence"):
        kinds.add("compatibility_evidence")
    return sorted(kinds)


def _overall_status(
    *,
    planner_status: str,
    failed_checks: tuple[EvalCheckResult, ...],
    skipped_checks: tuple[EvalCheckResult, ...],
    capability_gaps: tuple[EvalCheckResult, ...],
    partial_checks: tuple[EvalCheckResult, ...],
    satisfied_checks: tuple[EvalCheckResult, ...],
) -> str:
    if planner_status == "not_evaluable" and not satisfied_checks:
        return "not_evaluable"
    if failed_checks:
        return "not_satisfied"
    if capability_gaps:
        return "capability_gap"
    if partial_checks or skipped_checks:
        return "partial"
    return "satisfied"


def _expected_task_kind(task: ArchiveResolutionEvalTask) -> str | None:
    if task.expected_plan is None:
        return None
    value = task.expected_plan.get("task_kind")
    return value if isinstance(value, str) else None


def _expected_result_hints(task: ArchiveResolutionEvalTask) -> dict[str, Any]:
    return {
        "desired_object_types": list(task.desired_object_types),
        "acceptable_result_patterns": list(task.acceptable_result_patterns),
        "minimum_granularity": task.minimum_granularity,
        "required_evidence": list(task.required_evidence),
        "allowed_absence_outcomes": list(task.allowed_absence_outcomes),
    }


def _check_exact(
    name: str,
    *,
    expected: Any,
    observed: Any,
    success_message: str,
    failure_message: str,
) -> EvalCheckResult:
    if expected == observed:
        return EvalCheckResult(
            name=name,
            status="satisfied",
            message=success_message,
            expected=expected,
            observed=observed,
        )
    return EvalCheckResult(
        name=name,
        status="not_satisfied",
        message=failure_message,
        expected=expected,
        observed=observed,
    )


def _check_constraint(name: str, *, expected: Any, observed: Any) -> EvalCheckResult:
    if _json_subset_matches(expected, observed):
        return EvalCheckResult(
            name=f"planner.constraints.{name}",
            status="satisfied",
            message=f"Planner constraint '{name}' contains the expected bounded values.",
            expected=expected,
            observed=observed,
        )
    if observed is not None:
        return EvalCheckResult(
            name=f"planner.constraints.{name}",
            status="partial",
            message=f"Planner constraint '{name}' is present but does not fully match expected_plan.",
            expected=expected,
            observed=observed,
        )
    return EvalCheckResult(
        name=f"planner.constraints.{name}",
        status="not_satisfied",
        message=f"Planner constraint '{name}' is missing.",
        expected=expected,
        observed=observed,
    )


def _check_membership(
    name: str,
    *,
    expected: str,
    observed: Iterable[str],
    success_message: str,
    failure_message: str,
) -> EvalCheckResult:
    observed_tuple = tuple(observed)
    if expected in observed_tuple:
        return EvalCheckResult(
            name=name,
            status="satisfied",
            message=success_message,
            expected=expected,
            observed=list(observed_tuple),
        )
    return EvalCheckResult(
        name=name,
        status="not_satisfied",
        message=failure_message,
        expected=expected,
        observed=list(observed_tuple),
    )


def _aggregate_check_status(checks: tuple[EvalCheckResult, ...]) -> str:
    if not checks:
        return "not_evaluable"
    statuses = {check.status for check in checks}
    if "not_satisfied" in statuses:
        return "not_satisfied"
    if "partial" in statuses:
        return "partial"
    if statuses == {"not_evaluable"}:
        return "not_evaluable"
    return "satisfied"


def _json_subset_matches(expected: Any, observed: Any) -> bool:
    if isinstance(expected, Mapping):
        if not isinstance(observed, Mapping):
            return False
        for key, expected_value in expected.items():
            if key not in observed:
                return False
            if not _json_subset_matches(expected_value, observed[key]):
                return False
        return True
    if isinstance(expected, list):
        return expected == observed
    return expected == observed


def _structured_expected_result_evidence(
    task: ArchiveResolutionEvalTask,
    top_results: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    observed_text = " ".join(_flatten_strings(top_results)).casefold()
    compact_observed = _compact_text(observed_text)
    source_ids = sorted(
        {
            str(result.get("source_id"))
            for result in top_results
            if result.get("source_id")
        }
    )
    source_families = sorted(
        {
            str(result.get("source_family"))
            for result in top_results
            if result.get("source_family")
        }
    )
    record_kinds = sorted(
        {
            str(result.get("record_kind"))
            for result in top_results
            if result.get("record_kind")
        }
    )
    result_lanes = sorted(
        {
            str(lane)
            for result in top_results
            for lane in _string_iter(result.get("result_lanes"))
        }
    )
    member_paths = tuple(_result_member_paths(top_results))
    representation_ids = tuple(
        str(result["representation_id"])
        for result in top_results
        if result.get("representation_id")
    )
    compatibility_records = tuple(_compatibility_records(top_results))
    platform_terms = tuple(_platform_terms(task))
    hardware_terms = tuple(_hardware_terms(task))
    product_terms = tuple(_product_terms(task))
    function_terms = tuple(_function_terms(task))
    artifact_paths = tuple(
        path
        for path in member_paths + tuple(_result_file_like_strings(top_results))
        if _looks_like_artifact_locator(path)
    )

    clause_results = [
        _required_evidence_clause_status(
            clause,
            compact_observed=compact_observed,
            source_families=source_families,
            member_paths=member_paths,
            representation_ids=representation_ids,
            compatibility_records=compatibility_records,
            platform_terms=platform_terms,
            hardware_terms=hardware_terms,
            product_terms=product_terms,
            function_terms=function_terms,
            artifact_paths=artifact_paths,
        )
        for clause in task.required_evidence
    ]
    acceptable_patterns = [
        _acceptable_pattern_status(
            pattern,
            compact_observed=compact_observed,
            member_paths=member_paths,
            representation_ids=representation_ids,
            compatibility_records=compatibility_records,
            platform_terms=platform_terms,
            hardware_terms=hardware_terms,
            product_terms=product_terms,
            function_terms=function_terms,
            artifact_paths=artifact_paths,
        )
        for pattern in task.acceptable_result_patterns
    ]
    satisfied_clause_count = sum(1 for item in clause_results if item["satisfied"])
    satisfied_pattern_count = sum(1 for item in acceptable_patterns if item["satisfied"])
    source_backed = bool(source_ids or source_families)
    has_locator = bool(member_paths or representation_ids or artifact_paths)
    has_core_intent = (
        _any_term_matches(platform_terms, compact_observed)
        or _any_term_matches(hardware_terms, compact_observed)
        or _any_term_matches(product_terms, compact_observed)
        or _any_term_matches(function_terms, compact_observed)
    )

    status = "not_satisfied"
    if (
        source_backed
        and has_locator
        and satisfied_clause_count == len(clause_results)
        and satisfied_pattern_count > 0
    ):
        status = "satisfied"
    elif source_backed and has_core_intent and (satisfied_clause_count > 0 or satisfied_pattern_count > 0):
        status = "partial"

    return {
        "status": status,
        "top_result_count": len(top_results),
        "source_ids": source_ids,
        "source_families": source_families,
        "record_kinds": record_kinds,
        "result_lanes": result_lanes,
        "member_paths": list(member_paths),
        "representation_ids": list(representation_ids),
        "artifact_locators": list(artifact_paths),
        "compatibility_evidence_count": len(compatibility_records),
        "matched_platform_terms": _matched_terms(platform_terms, compact_observed),
        "matched_hardware_terms": _matched_terms(hardware_terms, compact_observed),
        "matched_product_terms": _matched_terms(product_terms, compact_observed),
        "matched_function_terms": _matched_terms(function_terms, compact_observed),
        "required_evidence": clause_results,
        "acceptable_result_patterns": acceptable_patterns,
        "top_results": top_results,
    }


def _required_evidence_clause_status(
    clause: str,
    *,
    compact_observed: str,
    source_families: list[str],
    member_paths: tuple[str, ...],
    representation_ids: tuple[str, ...],
    compatibility_records: tuple[Mapping[str, Any], ...],
    platform_terms: tuple[str, ...],
    hardware_terms: tuple[str, ...],
    product_terms: tuple[str, ...],
    function_terms: tuple[str, ...],
    artifact_paths: tuple[str, ...],
) -> dict[str, Any]:
    compact_clause = _compact_text(clause)
    reasons: list[str] = []
    satisfied = False

    if "sourcefamily" in compact_clause:
        satisfied = bool(source_families)
        if satisfied:
            reasons.append("source_family_present")
    elif "hardware" in compact_clause:
        satisfied = _any_term_matches(hardware_terms, compact_observed)
        if satisfied:
            reasons.append("hardware_hint_present")
    elif "ftpclient" in compact_clause or "function" in compact_clause or "registry" in compact_clause:
        satisfied = _any_term_matches(function_terms, compact_observed)
        if satisfied:
            reasons.append("functional_hint_present")
    elif "version" in compact_clause or "release" in compact_clause:
        satisfied = _release_identity_present(product_terms, compact_observed)
        if satisfied:
            reasons.append("version_or_release_identity_present")
    elif (
        "compatibility" in compact_clause
        or "platform" in compact_clause
        or "supportwindow" in compact_clause
        or "periodappropriate" in compact_clause
    ):
        platform_match = _any_term_matches(platform_terms, compact_observed)
        satisfied = platform_match and bool(compatibility_records or "compatibility" in compact_observed)
        if satisfied:
            reasons.append("platform_compatibility_evidence_present")
    elif "artifact" in compact_clause or "member" in compact_clause or "locator" in compact_clause:
        satisfied = bool(artifact_paths or member_paths or representation_ids)
        if satisfied:
            reasons.append("artifact_or_member_locator_present")
    elif "topic" in compact_clause or "page" in compact_clause or "article" in compact_clause:
        satisfied = "article" in compact_observed and ("page" in compact_observed or "section" in compact_observed)
        if satisfied:
            reasons.append("article_or_page_locator_present")
    else:
        satisfied = _compact_text(clause) in compact_observed
        if satisfied:
            reasons.append("literal_required_evidence_present")

    return {
        "clause": clause,
        "satisfied": satisfied,
        "reasons": reasons,
    }


def _acceptable_pattern_status(
    pattern: str,
    *,
    compact_observed: str,
    member_paths: tuple[str, ...],
    representation_ids: tuple[str, ...],
    compatibility_records: tuple[Mapping[str, Any], ...],
    platform_terms: tuple[str, ...],
    hardware_terms: tuple[str, ...],
    product_terms: tuple[str, ...],
    function_terms: tuple[str, ...],
    artifact_paths: tuple[str, ...],
) -> dict[str, Any]:
    compact_pattern = _compact_text(pattern)
    reasons: list[str] = []
    satisfied = False

    if "driver" in compact_pattern:
        satisfied = bool(artifact_paths or member_paths) and _any_term_matches(
            hardware_terms, compact_observed
        )
        if satisfied:
            reasons.append("driver_member_or_artifact_present")
    elif "installer" in compact_pattern or "portable" in compact_pattern or "application" in compact_pattern:
        satisfied = _has_direct_artifact_locator(artifact_paths) and (
            _any_term_matches(platform_terms, compact_observed)
            or _any_term_matches(function_terms, compact_observed)
        )
        if satisfied:
            reasons.append("software_artifact_or_representation_present")
    elif "release" in compact_pattern:
        satisfied = _release_identity_present(product_terms, compact_observed) and bool(
            representation_ids or artifact_paths
        )
        if satisfied:
            reasons.append("versioned_release_trace_present")
    elif "manual" in compact_pattern or "documentation" in compact_pattern or "trace" in compact_pattern:
        requires_concrete_product = "concreteproduct" in compact_pattern
        product_requirement_met = (
            _any_term_matches(product_terms, compact_observed)
            if requires_concrete_product
            else True
        )
        satisfied = product_requirement_met and bool(compatibility_records) and (
            _any_term_matches(platform_terms, compact_observed)
            or _any_term_matches(product_terms, compact_observed)
            or _any_term_matches(function_terms, compact_observed)
        )
        if satisfied:
            reasons.append("documentation_or_trace_evidence_present")
    elif "member" in compact_pattern:
        satisfied = bool(member_paths) and _has_direct_artifact_locator(artifact_paths)
        if satisfied:
            reasons.append("member_path_present")
    else:
        satisfied = compact_pattern in compact_observed
        if satisfied:
            reasons.append("literal_acceptable_pattern_present")

    return {
        "pattern": pattern,
        "satisfied": satisfied,
        "reasons": reasons,
    }


def _result_member_paths(top_results: tuple[dict[str, Any], ...]) -> Iterable[str]:
    for result in top_results:
        member_path = result.get("member_path")
        if isinstance(member_path, str) and member_path:
            yield member_path
        route_hints = result.get("route_hints")
        if isinstance(route_hints, Mapping):
            routed_member_path = route_hints.get("member_path")
            if isinstance(routed_member_path, str) and routed_member_path:
                yield routed_member_path
        for evidence in _string_iter(result.get("evidence")):
            if evidence.startswith("member_path:"):
                yield evidence.removeprefix("member_path:")
            elif "member_listing" in evidence or "file_listing" in evidence:
                tokens = evidence.split()
                for token in tokens:
                    if "/" in token and "." in token:
                        yield token


def _result_file_like_strings(top_results: tuple[dict[str, Any], ...]) -> Iterable[str]:
    for value in _flatten_strings(top_results):
        if "/" in value and "." in value:
            yield value
        elif re.search(r"\b[\w.-]+\.(?:inf|cab|exe|zip|7z|json|txt)\b", value, re.IGNORECASE):
            yield value


def _compatibility_records(top_results: tuple[dict[str, Any], ...]) -> Iterable[Mapping[str, Any]]:
    for result in top_results:
        records = result.get("compatibility_evidence")
        if isinstance(records, list):
            for record in records:
                if isinstance(record, Mapping):
                    yield record


def _platform_terms(task: ArchiveResolutionEvalTask) -> Iterable[str]:
    yield from _constraint_terms(task, ("platform", "os_family", "os_version", "marketing_alias"))
    expected_plan = task.expected_plan or {}
    constraints = expected_plan.get("constraints")
    if isinstance(constraints, Mapping):
        platform = constraints.get("platform")
        if isinstance(platform, Mapping):
            yield from (str(value) for value in platform.values() if isinstance(value, str))
    platform = task.target_constraints.get("platform")
    if isinstance(platform, Mapping):
        family = platform.get("os_family")
        version = platform.get("os_version")
        if isinstance(family, str) and isinstance(version, str):
            yield f"{family} {version}"
            if family.casefold() == "windows" and version.casefold() == "xp":
                yield "Windows NT 5.1"
            elif family.casefold() == "windows" and version == "2000":
                yield "Windows NT 5.0"
            elif family.casefold() == "windows" and version == "7":
                yield "Windows NT 6.1"


def _hardware_terms(task: ArchiveResolutionEvalTask) -> Iterable[str]:
    yield from _constraint_terms(task, ("hardware", "device_family", "hardware_hint"))
    expected_plan = task.expected_plan or {}
    constraints = expected_plan.get("constraints")
    if isinstance(constraints, Mapping):
        value = constraints.get("hardware_hint")
        if isinstance(value, str):
            yield value


def _product_terms(task: ArchiveResolutionEvalTask) -> Iterable[str]:
    yield from _constraint_terms(task, ("product_hint",))
    expected_plan = task.expected_plan or {}
    constraints = expected_plan.get("constraints")
    if isinstance(constraints, Mapping):
        value = constraints.get("product_hint")
        if isinstance(value, str):
            yield value


def _function_terms(task: ArchiveResolutionEvalTask) -> Iterable[str]:
    yield from _constraint_terms(task, ("function_hint", "appearance_hint", "descriptor_hint"))
    expected_plan = task.expected_plan or {}
    constraints = expected_plan.get("constraints")
    if isinstance(constraints, Mapping):
        for key in ("function_hint", "descriptor_hint"):
            value = constraints.get(key)
            if isinstance(value, str):
                yield value
    if "registry" in task.raw_query.casefold():
        yield "registry repair"
    if "ftp" in task.raw_query.casefold():
        yield "FTP client"


def _constraint_terms(value: Any, keys: tuple[str, ...]) -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in keys and isinstance(item, str):
                yield item
            yield from _constraint_terms(item, keys)
    elif isinstance(value, list):
        for item in value:
            yield from _constraint_terms(item, keys)


def _looks_like_artifact_locator(value: str) -> bool:
    lowered = value.casefold()
    return bool(
        re.search(r"\.(?:inf|cab|exe|zip|7z)(?:\.txt)?\b", lowered)
        or "installer" in lowered
        or "driver" in lowered
        or "portable-app-package" in lowered
        or "registry-repair" in lowered
    )


def _has_direct_artifact_locator(paths: tuple[str, ...]) -> bool:
    return any(
        re.search(r"\.(?:inf|cab|exe|7z)(?:\.txt)?\b", path.casefold())
        or "installer" in path.casefold()
        for path in paths
    )


def _release_identity_present(product_terms: tuple[str, ...], compact_observed: str) -> bool:
    has_product = _any_term_matches(product_terms, compact_observed)
    has_release_word = "release" in compact_observed or "version" in compact_observed
    has_version_number = bool(re.search(r"\d+(?:\.\d+)+", compact_observed))
    return has_product and has_release_word and has_version_number


def _any_term_matches(terms: Iterable[str], compact_observed: str) -> bool:
    return any(_compact_text(term) and _compact_text(term) in compact_observed for term in terms)


def _matched_terms(terms: Iterable[str], compact_observed: str) -> list[str]:
    return sorted(
        {
            term
            for term in terms
            if _compact_text(term) and _compact_text(term) in compact_observed
        }
    )


def _flatten_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _flatten_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _flatten_strings(item)


def _compact_text(value: str) -> str:
    return "".join(character for character in value.casefold() if character.isalnum())


def _search_result_to_dict(result: Any) -> dict[str, Any]:
    object_payload = result.object_summary.to_dict()
    payload: dict[str, Any] = {
        "record_kind": object_payload.get("record_kind", "resolved_object"),
        "target_ref": result.target_ref,
        "object": object_payload,
        "label": result.object_summary.label or result.object_summary.id,
    }
    for field_name in (
        "result_lanes",
        "primary_lane",
        "user_cost_score",
        "user_cost_reasons",
        "usefulness_summary",
        "compatibility_evidence",
        "compatibility_summary",
    ):
        value = getattr(result, field_name, None)
        if value is not None and value != ():
            payload[field_name] = _json_value(value)
    if result.resolved_resource_id is not None:
        payload["resolved_resource_id"] = result.resolved_resource_id
    if result.source is not None:
        payload["source"] = result.source.to_dict()
        payload["source_family"] = result.source.family
        if result.source.source_id is not None:
            payload["source_id"] = result.source.source_id
    if result.evidence:
        payload["evidence"] = [summary.to_dict() for summary in result.evidence]
    return payload


def _json_value(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _read_json_object(
    path: Path,
    errors: list[ArchiveResolutionEvalLoadError],
) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(
            ArchiveResolutionEvalLoadError(
                source_path=str(path),
                code="file_missing",
                message=f"Required file '{path}' was not found.",
            )
        )
        return None
    except (OSError, JSONDecodeError) as error:
        errors.append(
            ArchiveResolutionEvalLoadError(
                source_path=str(path),
                code="invalid_json_subset_yaml",
                message=str(error),
            )
        )
        return None
    if not isinstance(payload, Mapping):
        errors.append(
            ArchiveResolutionEvalLoadError(
                source_path=str(path),
                code="invalid_json_object",
                message=f"{path} must contain one JSON object.",
            )
        )
        return None
    return dict(payload)


def _schema_required_fields(
    schema: Mapping[str, Any] | None,
    schema_path: Path,
    errors: list[ArchiveResolutionEvalLoadError],
) -> tuple[str, ...]:
    if schema is None:
        return ()
    required = schema.get("required")
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        errors.append(
            ArchiveResolutionEvalLoadError(
                source_path=str(schema_path),
                code="invalid_schema_required",
                message="Archive-resolution task schema must declare a string-list 'required' field.",
            )
        )
        return ()
    return tuple(required)


def _schema_allowed_fields(schema: Mapping[str, Any] | None) -> set[str]:
    if schema is None:
        return set()
    properties = schema.get("properties")
    if not isinstance(properties, Mapping):
        return set()
    return {str(key) for key in properties.keys()}


def _task_from_payload(
    payload: Mapping[str, Any],
    *,
    task_path: Path,
    required_fields: tuple[str, ...],
    allowed_fields: set[str],
) -> ArchiveResolutionEvalTask:
    for field_name in required_fields:
        if field_name not in payload:
            raise ValueError(f"Missing required field '{field_name}'.")
    if allowed_fields:
        for field_name in payload.keys():
            if field_name not in allowed_fields:
                raise ValueError(f"Unknown field '{field_name}' is not declared by task.schema.yaml.")

    task_id = _require_string(payload.get("id"), "id")
    if task_id != task_path.stem:
        raise ValueError(f"Field 'id' must match task filename stem '{task_path.stem}'.")

    return ArchiveResolutionEvalTask(
        task_id=task_id,
        raw_query=_require_string(payload.get("raw_query"), "raw_query"),
        query_family=_require_string(payload.get("query_family"), "query_family"),
        desired_intent=_require_string(payload.get("desired_intent"), "desired_intent"),
        desired_object_types=_require_string_tuple(
            payload.get("desired_object_types"),
            "desired_object_types",
        ),
        target_constraints=_require_json_mapping(payload.get("target_constraints"), "target_constraints"),
        bad_result_patterns=_require_string_tuple(
            payload.get("bad_result_patterns"),
            "bad_result_patterns",
        ),
        acceptable_result_patterns=_require_string_tuple(
            payload.get("acceptable_result_patterns"),
            "acceptable_result_patterns",
        ),
        minimum_granularity=_require_string(
            payload.get("minimum_granularity"),
            "minimum_granularity",
        ),
        required_evidence=_require_string_tuple(payload.get("required_evidence"), "required_evidence"),
        expected_lanes=_require_string_tuple(payload.get("expected_lanes"), "expected_lanes"),
        allowed_absence_outcomes=_require_string_tuple(
            payload.get("allowed_absence_outcomes"),
            "allowed_absence_outcomes",
        ),
        expected_plan=_optional_expected_plan(payload.get("expected_plan")),
        notes=_optional_string(payload.get("notes"), "notes"),
        source_path=str(task_path),
    )


def _optional_expected_plan(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("Field 'expected_plan' must be an object when present.")
    allowed = {"task_kind", "object_type", "constraints", "prefer", "exclude"}
    for key in value.keys():
        if key not in allowed:
            raise ValueError(f"Field 'expected_plan.{key}' is not supported by Eval Runner v0.")
    payload: dict[str, Any] = {
        "task_kind": _require_string(value.get("task_kind"), "expected_plan.task_kind"),
        "object_type": _require_string(value.get("object_type"), "expected_plan.object_type"),
    }
    if "constraints" in value:
        payload["constraints"] = _require_json_mapping(
            value.get("constraints"),
            "expected_plan.constraints",
        )
    if "prefer" in value:
        payload["prefer"] = list(_require_string_tuple(value.get("prefer"), "expected_plan.prefer"))
    if "exclude" in value:
        payload["exclude"] = list(_require_string_tuple(value.get("exclude"), "expected_plan.exclude"))
    return payload


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{field_name}' must be a non-empty string.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name)


def _require_string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"Field '{field_name}' must be a non-empty list.")
    return tuple(_require_string(item, f"{field_name}[{index}]") for index, item in enumerate(value))


def _require_json_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError(f"Field '{field_name}' must be a non-empty object.")
    return {
        _require_string(key, f"{field_name}.key"): _clone_json_like(item, f"{field_name}.{key}")
        for key, item in value.items()
    }


def _clone_json_like(value: Any, field_name: str) -> Any:
    if isinstance(value, Mapping):
        return {
            _require_string(key, f"{field_name}.key"): _clone_json_like(item, f"{field_name}.{key}")
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_clone_json_like(item, f"{field_name}[]") for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ValueError(f"Field '{field_name}' must contain only JSON-compatible values.")


def _string_iter(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def _notice(code: str, severity: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "message": message}


def _mapping_text(value: Mapping[str, int]) -> str:
    if not value:
        return "(none)"
    return ", ".join(f"{key}={item}" for key, item in sorted(value.items()))


def _build_default_catalog() -> NormalizedCatalog:
    from runtime.connectors.github_releases import GitHubReleasesConnector
    from runtime.connectors.internet_archive_recorded import InternetArchiveRecordedConnector
    from runtime.connectors.local_bundle_fixtures import LocalBundleFixturesConnector
    from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
    from runtime.engine.interfaces.extract import (
        extract_github_release_source_record,
        extract_internet_archive_recorded_source_record,
        extract_local_bundle_source_record,
        extract_synthetic_source_record,
    )
    from runtime.engine.interfaces.normalize import (
        normalize_extracted_record,
        normalize_github_release_record,
        normalize_internet_archive_recorded_item,
        normalize_local_bundle_record,
    )

    synthetic_connector = SyntheticSoftwareConnector()
    github_connector = GitHubReleasesConnector()
    internet_archive_connector = InternetArchiveRecordedConnector()
    local_bundle_connector = LocalBundleFixturesConnector()
    synthetic_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in synthetic_connector.load_source_records()
    )
    github_records = tuple(
        normalize_github_release_record(extract_github_release_source_record(record))
        for record in github_connector.load_source_records()
    )
    internet_archive_records = tuple(
        normalize_internet_archive_recorded_item(
            extract_internet_archive_recorded_source_record(record)
        )
        for record in internet_archive_connector.load_source_records()
    )
    local_bundle_records = tuple(
        normalize_local_bundle_record(extract_local_bundle_source_record(record))
        for record in local_bundle_connector.load_source_records()
    )
    return NormalizedCatalog(
        synthetic_records + github_records + internet_archive_records + local_bundle_records
    )
