from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from json import JSONDecodeError
from pathlib import Path
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
        all_checks = planner_checks + search_observation.checks + _not_yet_evaluable_checks(task)
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

    if _observed_results_match_expected_hints(task, top_results):
        return (
            EvalCheckResult(
                name="search.expected_result_hints",
                status="satisfied",
                message=(
                    "At least one observed result contained an explicit acceptable-result "
                    "or required-evidence hint."
                ),
                expected=_expected_result_hints(task),
                observed={"top_results": top_results},
            ),
        )
    return (
        EvalCheckResult(
            name="search.expected_result_hints",
            status="not_satisfied",
            message=(
                "Search returned bounded results, but none contained an exact known expected result hint. "
                "Eval Runner v0 does not infer semantic relevance."
            ),
            expected=_expected_result_hints(task),
            observed={"top_results": top_results},
        ),
    )


def _not_yet_evaluable_checks(
    task: ArchiveResolutionEvalTask,
) -> tuple[EvalCheckResult, ...]:
    return (
        EvalCheckResult(
            name="lanes.expected_lanes",
            status="not_evaluable",
            message=(
                "Expected future result lanes are recorded but not scored as a benchmark in Eval Runner v0; "
                "current lane/user-cost annotations are bounded result details, not a lane-placement benchmark."
            ),
            expected=list(task.expected_lanes),
        ),
        EvalCheckResult(
            name="ranking.bad_result_patterns",
            status="not_evaluable",
            message=(
                "Bad-result patterns are recorded but not scored in Eval Runner v0; "
                "this runner does not implement production ranking, fuzzy, semantic, or vector evaluation."
            ),
            expected=list(task.bad_result_patterns),
        ),
    )


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


def _observed_results_match_expected_hints(
    task: ArchiveResolutionEvalTask,
    top_results: tuple[dict[str, Any], ...],
) -> bool:
    observed_text = " ".join(_flatten_strings(top_results)).casefold()
    compact_observed = _compact_text(observed_text)
    for hint in task.acceptable_result_patterns + task.required_evidence:
        if _compact_text(hint) and _compact_text(hint) in compact_observed:
            return True
    return False


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
