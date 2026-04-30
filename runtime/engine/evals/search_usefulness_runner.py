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
from runtime.engine.index import LocalIndexEngineService, LocalIndexSqliteStore
from runtime.engine.interfaces.public import (
    LocalIndexBuildRequest,
    LocalIndexQueryRequest,
    QueryPlanRequest,
    SearchAbsenceRequest,
    SearchRequest,
)
from runtime.engine.interfaces.public.query_plan import ResolutionTask
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
from runtime.source_registry import SourceRegistry, load_source_registry


DEFAULT_SEARCH_USEFULNESS_EVAL_ROOT = (
    Path(__file__).resolve().parents[3] / "evals" / "search_usefulness"
)
CREATED_BY_SLICE = "search_usefulness_audit_v0"
TOP_RESULT_LIMIT = 5

VALID_EUREKA_STATUSES = (
    "covered",
    "partial",
    "source_gap",
    "capability_gap",
    "not_evaluable",
    "unknown",
)
VALID_OBSERVATION_STATUSES = (
    "observed",
    "pending_manual_observation",
    "not_applicable",
    "not_available",
)
VALID_FAILURE_LABELS = (
    "source_coverage_gap",
    "live_source_gap",
    "index_gap",
    "planner_gap",
    "query_interpretation_gap",
    "decomposition_gap",
    "member_access_gap",
    "representation_gap",
    "compatibility_evidence_gap",
    "identity_cluster_gap",
    "ranking_gap",
    "absence_reasoning_gap",
    "actionability_gap",
    "surface_ux_gap",
    "public_alpha_blocked",
    "external_baseline_pending",
)
EXTERNAL_BASELINE_SYSTEMS = (
    "google",
    "internet_archive_metadata",
    "internet_archive_full_text",
)


def _default_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class SearchUsefulnessQuery:
    query_id: str
    query: str
    query_family: str
    intent: str
    target_object_type: str
    constraints: dict[str, Any]
    expected_useful_units: tuple[str, ...]
    known_bad_result_patterns: tuple[str, ...]
    minimum_granularity: str
    target_actions: tuple[str, ...]
    expected_eureka_current_status: str
    audit_tags: tuple[str, ...]
    notes: str
    expected_failure_modes: tuple[str, ...] = ()
    future_work_labels: tuple[str, ...] = ()
    source_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "id": self.query_id,
            "query": self.query,
            "query_family": self.query_family,
            "intent": self.intent,
            "target_object_type": self.target_object_type,
            "constraints": _clone_json_like(self.constraints),
            "expected_useful_units": list(self.expected_useful_units),
            "known_bad_result_patterns": list(self.known_bad_result_patterns),
            "minimum_granularity": self.minimum_granularity,
            "target_actions": list(self.target_actions),
            "expected_eureka_current_status": self.expected_eureka_current_status,
            "audit_tags": list(self.audit_tags),
            "notes": self.notes,
            "expected_failure_modes": list(self.expected_failure_modes),
            "future_work_labels": list(self.future_work_labels),
        }
        if self.source_path is not None:
            payload["source_path"] = self.source_path
        return payload


@dataclass(frozen=True)
class SearchUsefulnessLoadError:
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
class SearchUsefulnessLoadResult:
    eval_root: str
    schema_path: str
    query_count: int
    queries: tuple[SearchUsefulnessQuery, ...] = ()
    errors: tuple[SearchUsefulnessLoadError, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "eval_root": self.eval_root,
            "schema_path": self.schema_path,
            "query_count": self.query_count,
            "queries": [query.to_dict() for query in self.queries],
            "errors": [error.to_dict() for error in self.errors],
        }


@dataclass(frozen=True)
class SearchUsefulnessSystemObservation:
    system: str
    observation_status: str
    top_results: tuple[dict[str, Any], ...] = ()
    first_useful_result_rank: int | None = None
    usefulness_scores: dict[str, int] | None = None
    notes: tuple[str, ...] = ()
    failure_modes: tuple[str, ...] = ()
    next_eureka_work: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        if self.observation_status not in VALID_OBSERVATION_STATUSES:
            raise ValueError(
                f"Observation for {self.system} used unknown status "
                f"'{self.observation_status}'."
            )
        payload: dict[str, Any] = {
            "system": self.system,
            "observation_status": self.observation_status,
            "top_results": [_clone_json_like(result) for result in self.top_results],
            "failure_modes": list(self.failure_modes),
            "next_eureka_work": list(self.next_eureka_work),
            "notes": list(self.notes),
        }
        if self.first_useful_result_rank is not None:
            payload["first_useful_result_rank"] = self.first_useful_result_rank
        if self.usefulness_scores is not None:
            payload["usefulness_scores"] = dict(sorted(self.usefulness_scores.items()))
        return payload


@dataclass(frozen=True)
class SearchUsefulnessAuditTaskResult:
    query_id: str
    query: str
    query_family: str
    expected_eureka_current_status: str
    eureka_status: str
    planner_observed_task_kind: str | None
    planner_observed_object_type: str | None
    planner_confidence: str | None
    search_mode: str
    search_query: str | None
    search_result_count: int
    first_useful_result_rank: int | None
    observations: tuple[SearchUsefulnessSystemObservation, ...]
    failure_modes: tuple[str, ...]
    future_work_labels: tuple[str, ...]
    absence_summary: dict[str, Any] | None = None
    notices: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        if self.eureka_status not in VALID_EUREKA_STATUSES:
            raise ValueError(
                f"Search usefulness query '{self.query_id}' used unknown status "
                f"'{self.eureka_status}'."
            )
        payload: dict[str, Any] = {
            "query_id": self.query_id,
            "query": self.query,
            "query_family": self.query_family,
            "expected_eureka_current_status": self.expected_eureka_current_status,
            "eureka_status": self.eureka_status,
            "planner_observed_task_kind": self.planner_observed_task_kind,
            "planner_observed_object_type": self.planner_observed_object_type,
            "planner_confidence": self.planner_confidence,
            "search_mode": self.search_mode,
            "search_query": self.search_query,
            "search_result_count": self.search_result_count,
            "observations": [observation.to_dict() for observation in self.observations],
            "failure_modes": list(self.failure_modes),
            "future_work_labels": list(self.future_work_labels),
            "notices": [_clone_json_like(notice) for notice in self.notices],
        }
        if self.first_useful_result_rank is not None:
            payload["first_useful_result_rank"] = self.first_useful_result_rank
        if self.absence_summary is not None:
            payload["absence_summary"] = _clone_json_like(self.absence_summary)
        return payload

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "query": self.query,
            "query_family": self.query_family,
            "eureka_status": self.eureka_status,
            "expected_eureka_current_status": self.expected_eureka_current_status,
            "search_mode": self.search_mode,
            "search_result_count": self.search_result_count,
            "planner_observed_task_kind": self.planner_observed_task_kind,
            "failure_modes": list(self.failure_modes),
            "future_work_labels": list(self.future_work_labels),
        }


@dataclass(frozen=True)
class SearchUsefulnessAuditSuiteResult:
    total_query_count: int
    query_family_counts: dict[str, int]
    eureka_status_counts: dict[str, int]
    external_baseline_pending_counts: dict[str, int]
    failure_mode_counts: dict[str, int]
    future_work_recommendations: tuple[dict[str, Any], ...]
    task_results: tuple[SearchUsefulnessAuditTaskResult, ...]
    created_at: str
    created_by_slice: str
    load_errors: tuple[SearchUsefulnessLoadError, ...] = ()
    notices: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_query_count": self.total_query_count,
            "query_family_counts": dict(sorted(self.query_family_counts.items())),
            "eureka_status_counts": dict(sorted(self.eureka_status_counts.items())),
            "external_baseline_pending_counts": dict(
                sorted(self.external_baseline_pending_counts.items())
            ),
            "failure_mode_counts": dict(sorted(self.failure_mode_counts.items())),
            "future_work_recommendations": [
                _clone_json_like(recommendation)
                for recommendation in self.future_work_recommendations
            ],
            "query_summaries": [result.to_summary_dict() for result in self.task_results],
            "queries": [result.to_dict() for result in self.task_results],
            "created_at": self.created_at,
            "created_by_slice": self.created_by_slice,
            "load_errors": [error.to_dict() for error in self.load_errors],
            "notices": [_clone_json_like(notice) for notice in self.notices],
        }


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
    notices: tuple[dict[str, str], ...]


class SearchUsefulnessAuditRunner:
    def __init__(
        self,
        *,
        query_planner: QueryPlannerService,
        local_index_service: LocalIndexService | None = None,
        search_service: SearchService | None = None,
        absence_service: AbsenceService | None = None,
        eval_root: Path | str = DEFAULT_SEARCH_USEFULNESS_EVAL_ROOT,
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
        query_id: str | None = None,
        index_path: str | None = None,
        use_local_index: bool = True,
    ) -> SearchUsefulnessAuditSuiteResult:
        load_result = load_search_usefulness_queries(self._eval_root)
        selected_queries, selection_notices = _select_queries(load_result.queries, query_id)

        if use_local_index and index_path is None and self._local_index_service is not None:
            with tempfile.TemporaryDirectory() as temp_dir:
                transient_index_path = str(Path(temp_dir) / "search-usefulness-audit.sqlite3")
                return self._run_loaded_suite(
                    load_result,
                    selected_queries,
                    index_path=transient_index_path,
                    use_local_index=True,
                    suite_notices=selection_notices
                    + (
                        _notice(
                            "transient_local_index",
                            "info",
                            (
                                "Built a transient Local Index v0 database for this audit run. "
                                "The report omits the temporary path so JSON remains inspectable."
                            ),
                        ),
                    ),
                )

        return self._run_loaded_suite(
            load_result,
            selected_queries,
            index_path=index_path,
            use_local_index=use_local_index,
            suite_notices=selection_notices,
        )

    def _run_loaded_suite(
        self,
        load_result: SearchUsefulnessLoadResult,
        selected_queries: tuple[SearchUsefulnessQuery, ...],
        *,
        index_path: str | None,
        use_local_index: bool,
        suite_notices: tuple[dict[str, str], ...],
    ) -> SearchUsefulnessAuditSuiteResult:
        search_context, index_notices = self._prepare_search_context(
            index_path=index_path,
            use_local_index=use_local_index,
        )
        task_results = tuple(
            self._run_query(query, search_context) for query in selected_queries
        )
        family_counts = Counter(result.query_family for result in task_results)
        status_counts = Counter(result.eureka_status for result in task_results)
        failure_counts: Counter[str] = Counter()
        external_pending_counts: Counter[str] = Counter()
        future_work_counts: Counter[str] = Counter()
        for result in task_results:
            failure_counts.update(result.failure_modes)
            future_work_counts.update(result.future_work_labels)
            for observation in result.observations:
                if observation.observation_status == "pending_manual_observation":
                    external_pending_counts[observation.system] += 1
        notices = (
            suite_notices
            + index_notices
            + (
                _notice(
                    "external_baselines_pending",
                    "info",
                    (
                        "Search Usefulness Audit v0 does not scrape Google, Internet "
                        "Archive, or other external systems. Baseline records are "
                        "pending manual observation unless explicitly recorded later."
                    ),
                ),
            )
        )
        if load_result.errors:
            notices = notices + (
                _notice(
                    "search_usefulness_load_errors",
                    "warning",
                    "One or more search-usefulness query fixtures were not evaluable.",
                ),
            )
        return SearchUsefulnessAuditSuiteResult(
            total_query_count=len(task_results),
            query_family_counts=dict(sorted(family_counts.items())),
            eureka_status_counts=dict(sorted(status_counts.items())),
            external_baseline_pending_counts=dict(sorted(external_pending_counts.items())),
            failure_mode_counts=dict(sorted(failure_counts.items())),
            future_work_recommendations=_recommendations(future_work_counts),
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
                "local_index_built_for_audit",
                "info",
                "Built Local Index v0 once for this synchronous search-usefulness audit suite.",
            ),
        )

    def _run_query(
        self,
        query: SearchUsefulnessQuery,
        search_context: _SearchContext,
    ) -> SearchUsefulnessAuditTaskResult:
        planner_task: ResolutionTask | None = None
        planner_error: Exception | None = None
        try:
            planner_task = self._query_planner.plan_query(QueryPlanRequest.from_parts(query.query))
        except Exception as error:
            planner_error = error

        observation = self._observe_search(query, planner_task, search_context)
        first_useful_rank = _first_useful_rank(query, observation.top_results)
        failure_modes = _failure_modes(query, planner_task, observation, first_useful_rank)
        future_work_labels = _future_work_labels(query, failure_modes)
        eureka_status = _eureka_status(query, planner_task, observation, first_useful_rank)
        eureka_observation = SearchUsefulnessSystemObservation(
            system="eureka",
            observation_status="observed",
            top_results=observation.top_results,
            first_useful_result_rank=first_useful_rank,
            usefulness_scores=_usefulness_scores(
                query,
                planner_task=planner_task,
                observation=observation,
                first_useful_rank=first_useful_rank,
                eureka_status=eureka_status,
            ),
            notes=_eureka_notes(query, planner_task, observation, eureka_status),
            failure_modes=failure_modes,
            next_eureka_work=future_work_labels,
        )
        external_observations = tuple(
            _pending_external_observation(system) for system in EXTERNAL_BASELINE_SYSTEMS
        )
        notices = observation.notices
        if planner_error is not None:
            notices = notices + (
                _notice("planner_failed", "warning", str(planner_error)),
            )
        return SearchUsefulnessAuditTaskResult(
            query_id=query.query_id,
            query=query.query,
            query_family=query.query_family,
            expected_eureka_current_status=query.expected_eureka_current_status,
            eureka_status=eureka_status,
            planner_observed_task_kind=planner_task.task_kind if planner_task is not None else None,
            planner_observed_object_type=planner_task.object_type if planner_task is not None else None,
            planner_confidence=planner_task.planner_confidence if planner_task is not None else None,
            search_mode=observation.search_mode,
            search_query=observation.search_query,
            search_result_count=observation.result_count,
            first_useful_result_rank=first_useful_rank,
            observations=(eureka_observation,) + external_observations,
            failure_modes=failure_modes,
            future_work_labels=future_work_labels,
            absence_summary=observation.absence_summary,
            notices=notices,
        )

    def _observe_search(
        self,
        query: SearchUsefulnessQuery,
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
                notices=(),
            )
        search_query = derive_search_query_from_task(planner_task)
        if search_context.search_mode == "local_index" and search_context.index_available:
            return self._observe_local_index_search(search_context, search_query)
        if search_context.search_mode == "deterministic_search" and self._search_service is not None:
            return self._observe_deterministic_search(search_query)
        return _SearchObservation(
            search_mode=search_context.search_mode,
            search_query=search_query,
            result_count=0,
            top_results=(),
            absence_summary=None,
            notices=(
                _notice(
                    "search_path_unavailable",
                    "warning",
                    f"No bounded local search path was available for query '{query.query_id}'.",
                ),
            ),
        )

    def _observe_local_index_search(
        self,
        search_context: _SearchContext,
        search_query: str,
    ) -> _SearchObservation:
        if self._local_index_service is None or search_context.index_path is None:
            return self._observe_deterministic_or_unavailable(search_query)
        try:
            query_result = self._local_index_service.query_index(
                LocalIndexQueryRequest.from_parts(search_context.index_path, search_query),
            )
        except Exception as error:
            if self._search_service is not None:
                fallback = self._observe_deterministic_search(search_query)
                return _SearchObservation(
                    search_mode="deterministic_search",
                    search_query=fallback.search_query,
                    result_count=fallback.result_count,
                    top_results=fallback.top_results,
                    absence_summary=fallback.absence_summary,
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
                notices=(_notice("local_index_query_failed", "warning", str(error)),),
            )
        top_results = tuple(item.to_dict() for item in query_result.results[:TOP_RESULT_LIMIT])
        absence_summary = self._absence_summary(search_query) if not query_result.results else None
        return _SearchObservation(
            search_mode="local_index",
            search_query=search_query,
            result_count=len(query_result.results),
            top_results=top_results,
            absence_summary=absence_summary,
            notices=tuple(notice.to_dict() for notice in query_result.notices),
        )

    def _observe_deterministic_or_unavailable(self, search_query: str) -> _SearchObservation:
        if self._search_service is not None:
            return self._observe_deterministic_search(search_query)
        return _SearchObservation(
            search_mode="unavailable",
            search_query=search_query,
            result_count=0,
            top_results=(),
            absence_summary=None,
            notices=(),
        )

    def _observe_deterministic_search(self, search_query: str) -> _SearchObservation:
        if self._search_service is None:
            return self._observe_deterministic_or_unavailable(search_query)
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


def load_search_usefulness_queries(
    eval_root: Path | str = DEFAULT_SEARCH_USEFULNESS_EVAL_ROOT,
) -> SearchUsefulnessLoadResult:
    root = Path(eval_root)
    schema_path = root / "query.schema.yaml"
    errors: list[SearchUsefulnessLoadError] = []
    schema = _read_json_object(schema_path, errors)
    required_fields = _schema_required_fields(schema, schema_path, errors)
    allowed_fields = _schema_allowed_fields(schema)
    query_dir = root / "queries"
    queries: list[SearchUsefulnessQuery] = []
    seen_ids: set[str] = set()
    if not query_dir.is_dir():
        errors.append(
            SearchUsefulnessLoadError(
                source_path=str(query_dir),
                code="query_dir_missing",
                message="Search-usefulness query directory was not found.",
            )
        )
    else:
        for path in sorted(query_dir.glob("*")):
            if path.suffix.lower() not in {".json", ".yaml"}:
                continue
            payload = _read_json_object(path, errors)
            if payload is None:
                continue
            raw_queries = _payload_queries(payload, path, errors)
            for index, raw_query in enumerate(raw_queries):
                source_ref = f"{path}#{index}" if len(raw_queries) > 1 else str(path)
                try:
                    query = _query_from_payload(
                        raw_query,
                        source_path=source_ref,
                        required_fields=required_fields,
                        allowed_fields=allowed_fields,
                    )
                except ValueError as error:
                    errors.append(
                        SearchUsefulnessLoadError(
                            source_path=source_ref,
                            code="invalid_query_fixture",
                            message=str(error),
                        )
                    )
                    continue
                if query.query_id in seen_ids:
                    errors.append(
                        SearchUsefulnessLoadError(
                            source_path=source_ref,
                            code="duplicate_query_id",
                            message=f"Duplicate search-usefulness query id '{query.query_id}'.",
                        )
                    )
                    continue
                seen_ids.add(query.query_id)
                queries.append(query)
    sorted_queries = tuple(sorted(queries, key=lambda item: item.query_id))
    return SearchUsefulnessLoadResult(
        eval_root=str(root),
        schema_path=str(schema_path),
        query_count=len(sorted_queries),
        queries=sorted_queries,
        errors=tuple(errors),
    )


def validate_search_usefulness_observation_payload(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    status = payload.get("observation_status")
    if status not in VALID_OBSERVATION_STATUSES:
        errors.append("observation_status must be a known status.")
    system = payload.get("system")
    if not isinstance(system, str) or not system:
        errors.append("system must be a non-empty string.")
    scores = payload.get("usefulness_scores")
    if scores is not None:
        if not isinstance(scores, Mapping):
            errors.append("usefulness_scores must be an object when present.")
        else:
            for key, value in scores.items():
                if not isinstance(key, str) or not isinstance(value, int) or value < 0 or value > 5:
                    errors.append("usefulness_scores values must be integers from 0 to 5.")
                    break
    failure_modes = payload.get("failure_modes", [])
    if not isinstance(failure_modes, list):
        errors.append("failure_modes must be a list.")
    else:
        for item in failure_modes:
            if item not in VALID_FAILURE_LABELS:
                errors.append(f"Unknown failure mode '{item}'.")
    return tuple(errors)


def build_default_search_usefulness_audit_runner(
    *,
    eval_root: Path | str = DEFAULT_SEARCH_USEFULNESS_EVAL_ROOT,
    timestamp_factory: Callable[[], str] = _default_timestamp,
) -> SearchUsefulnessAuditRunner:
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
    return SearchUsefulnessAuditRunner(
        query_planner=DeterministicQueryPlannerService(),
        local_index_service=index_service,
        search_service=search_service,
        absence_service=absence_service,
        eval_root=eval_root,
        timestamp_factory=timestamp_factory,
    )


def format_search_usefulness_audit_summary(
    suite: SearchUsefulnessAuditSuiteResult,
) -> str:
    lines = [
        "Search usefulness audit",
        f"created_by_slice: {suite.created_by_slice}",
        f"query_count: {suite.total_query_count}",
        f"eureka_status_counts: {_mapping_text(suite.eureka_status_counts)}",
        f"external_pending_counts: {_mapping_text(suite.external_baseline_pending_counts)}",
        f"failure_mode_counts: {_mapping_text(suite.failure_mode_counts)}",
    ]
    if suite.load_errors:
        lines.extend(["", "Load errors"])
        for error in suite.load_errors:
            lines.append(f"- {error.code}: {error.source_path}: {error.message}")
    lines.extend(["", "Top future-work recommendations"])
    if suite.future_work_recommendations:
        for recommendation in suite.future_work_recommendations[:10]:
            lines.append(
                f"- {recommendation['label']}: {recommendation['count']} "
                f"({recommendation['description']})"
            )
    else:
        lines.append("- (none)")
    lines.extend(["", "Queries"])
    for result in suite.task_results:
        lines.append(
            "- "
            f"{result.query_id}: {result.eureka_status} "
            f"(family={result.query_family}, search={result.search_mode}, "
            f"results={result.search_result_count})"
        )
    return "\n".join(lines) + "\n"


def manual_observation_template(
    *,
    query: SearchUsefulnessQuery,
    system: str,
    observation_status: str = "pending_manual_observation",
) -> dict[str, Any]:
    if observation_status not in VALID_OBSERVATION_STATUSES:
        raise ValueError(f"Unknown observation status '{observation_status}'.")
    return {
        "query_id": query.query_id,
        "query": query.query,
        "system": system,
        "observation_status": observation_status,
        "top_results": [],
        "first_useful_result_rank": None,
        "usefulness_scores": {},
        "notes": [
            (
                "Manual observation placeholder only. Do not fill this with "
                "automated scraping output."
            )
        ],
        "failure_modes": ["external_baseline_pending"]
        if observation_status == "pending_manual_observation"
        else [],
        "next_eureka_work": [],
    }


def _select_queries(
    queries: tuple[SearchUsefulnessQuery, ...],
    query_id: str | None,
) -> tuple[tuple[SearchUsefulnessQuery, ...], tuple[dict[str, str], ...]]:
    normalized_query_id = (query_id or "").strip()
    if not normalized_query_id:
        return queries, ()
    selected = tuple(query for query in queries if query.query_id == normalized_query_id)
    if selected:
        return selected, ()
    return (), (
        _notice(
            "search_usefulness_query_not_found",
            "warning",
            f"Search-usefulness query '{normalized_query_id}' was not found.",
        ),
    )


def _payload_queries(
    payload: Mapping[str, Any],
    path: Path,
    errors: list[SearchUsefulnessLoadError],
) -> tuple[Mapping[str, Any], ...]:
    if "queries" not in payload:
        return (payload,)
    raw_queries = payload.get("queries")
    if not isinstance(raw_queries, list):
        errors.append(
            SearchUsefulnessLoadError(
                source_path=str(path),
                code="invalid_query_pack",
                message="Field 'queries' must be a list.",
            )
        )
        return ()
    queries: list[Mapping[str, Any]] = []
    for index, item in enumerate(raw_queries):
        if not isinstance(item, Mapping):
            errors.append(
                SearchUsefulnessLoadError(
                    source_path=f"{path}#{index}",
                    code="invalid_query_fixture",
                    message="Each packed query must be an object.",
                )
            )
            continue
        queries.append(item)
    return tuple(queries)


def _query_from_payload(
    payload: Mapping[str, Any],
    *,
    source_path: str,
    required_fields: tuple[str, ...],
    allowed_fields: set[str],
) -> SearchUsefulnessQuery:
    for field_name in required_fields:
        if field_name not in payload:
            raise ValueError(f"Missing required field '{field_name}'.")
    if allowed_fields:
        for field_name in payload.keys():
            if field_name not in allowed_fields:
                raise ValueError(f"Unknown field '{field_name}' is not declared by query.schema.yaml.")
    expected_status = _require_string(
        payload.get("expected_eureka_current_status"),
        "expected_eureka_current_status",
    )
    if expected_status not in VALID_EUREKA_STATUSES:
        raise ValueError(
            f"Field 'expected_eureka_current_status' used unknown status '{expected_status}'."
        )
    failure_modes = _require_optional_label_tuple(
        payload.get("expected_failure_modes"),
        "expected_failure_modes",
    )
    future_work = _require_optional_label_tuple(
        payload.get("future_work_labels"),
        "future_work_labels",
    )
    return SearchUsefulnessQuery(
        query_id=_require_string(payload.get("id"), "id"),
        query=_require_string(payload.get("query"), "query"),
        query_family=_require_string(payload.get("query_family"), "query_family"),
        intent=_require_string(payload.get("intent"), "intent"),
        target_object_type=_require_string(payload.get("target_object_type"), "target_object_type"),
        constraints=_require_json_mapping(payload.get("constraints"), "constraints"),
        expected_useful_units=_require_string_tuple(
            payload.get("expected_useful_units"),
            "expected_useful_units",
        ),
        known_bad_result_patterns=_require_string_tuple(
            payload.get("known_bad_result_patterns"),
            "known_bad_result_patterns",
        ),
        minimum_granularity=_require_string(payload.get("minimum_granularity"), "minimum_granularity"),
        target_actions=_require_string_tuple(payload.get("target_actions"), "target_actions"),
        expected_eureka_current_status=expected_status,
        audit_tags=_require_string_tuple(payload.get("audit_tags"), "audit_tags"),
        notes=_require_string(payload.get("notes"), "notes"),
        expected_failure_modes=failure_modes,
        future_work_labels=future_work,
        source_path=source_path,
    )


def _first_useful_rank(
    query: SearchUsefulnessQuery,
    top_results: tuple[dict[str, Any], ...],
) -> int | None:
    if not top_results:
        return None
    expected = tuple(_compact_text(item) for item in query.expected_useful_units)
    for index, result in enumerate(top_results, start=1):
        observed_text = _compact_text(" ".join(_flatten_strings(result)))
        if any(item and item in observed_text for item in expected):
            return index
    return None


def _eureka_status(
    query: SearchUsefulnessQuery,
    planner_task: ResolutionTask | None,
    observation: _SearchObservation,
    first_useful_rank: int | None,
) -> str:
    expected_status = query.expected_eureka_current_status
    if planner_task is None or observation.search_mode == "unavailable":
        return "not_evaluable"
    if first_useful_rank is not None:
        if expected_status == "covered":
            return "covered"
        return "partial"
    if observation.result_count > 0:
        return "partial"
    if expected_status in {"source_gap", "capability_gap", "unknown"}:
        return expected_status
    if expected_status == "partial" and observation.absence_summary is not None:
        return "capability_gap"
    return "capability_gap"


def _failure_modes(
    query: SearchUsefulnessQuery,
    planner_task: ResolutionTask | None,
    observation: _SearchObservation,
    first_useful_rank: int | None,
) -> tuple[str, ...]:
    labels: list[str] = list(query.expected_failure_modes)
    if planner_task is None:
        labels.append("planner_gap")
    elif planner_task.task_kind == "generic_search" and query.expected_eureka_current_status != "covered":
        labels.append("planner_gap")
        labels.append("query_interpretation_gap")
    if observation.search_mode == "unavailable":
        labels.append("index_gap")
    if observation.result_count == 0:
        if query.expected_eureka_current_status == "source_gap":
            labels.append("source_coverage_gap")
        elif query.expected_eureka_current_status in {"capability_gap", "unknown"}:
            labels.append("index_gap")
        if observation.absence_summary is None:
            labels.append("absence_reasoning_gap")
    elif first_useful_rank is None:
        labels.append("ranking_gap")
        labels.append("identity_cluster_gap")
    if "external_baseline_pending" not in labels:
        labels.append("external_baseline_pending")
    return _dedupe_valid_labels(labels)


def _future_work_labels(
    query: SearchUsefulnessQuery,
    failure_modes: tuple[str, ...],
) -> tuple[str, ...]:
    labels = list(query.future_work_labels)
    for label in failure_modes:
        if label != "external_baseline_pending":
            labels.append(label)
    return _dedupe_valid_labels(labels)


def _usefulness_scores(
    query: SearchUsefulnessQuery,
    *,
    planner_task: ResolutionTask | None,
    observation: _SearchObservation,
    first_useful_rank: int | None,
    eureka_status: str,
) -> dict[str, int]:
    planner_structured = planner_task is not None and planner_task.task_kind != "generic_search"
    useful_result = first_useful_rank is not None
    any_result = observation.result_count > 0
    absence = observation.absence_summary is not None
    compatibility_relevant = "compatibility" in " ".join(query.audit_tags).casefold()
    scores = {
        "object_type_fit": 4 if useful_result else (2 if planner_structured else 1),
        "smallest_actionable_unit": 4 if useful_result else (2 if any_result else 1),
        "evidence_quality": 3 if any_result else (2 if absence else 1),
        "compatibility_clarity": 3 if compatibility_relevant and useful_result else (2 if compatibility_relevant else 1),
        "actionability": 4 if useful_result else (2 if any_result else 1),
        "absence_explanation": 4 if absence else (1 if not any_result else 2),
        "user_cost_reduction": 4 if eureka_status == "covered" else (3 if eureka_status == "partial" else 2),
    }
    scores["overall"] = round(sum(scores.values()) / len(scores))
    return scores


def _eureka_notes(
    query: SearchUsefulnessQuery,
    planner_task: ResolutionTask | None,
    observation: _SearchObservation,
    eureka_status: str,
) -> tuple[str, ...]:
    notes = [
        (
            "Eureka observation is generated locally from Query Planner v0, "
            "Local Index v0 or deterministic search, and bounded absence reasoning."
        ),
        f"Expected current status from fixture: {query.expected_eureka_current_status}.",
        f"Observed Eureka status: {eureka_status}.",
    ]
    if planner_task is None:
        notes.append("Query Planner v0 did not produce a plan.")
    else:
        notes.append(
            f"Planner task_kind={planner_task.task_kind}, object_type={planner_task.object_type}."
        )
    if not observation.top_results and observation.absence_summary is not None:
        notes.append("No bounded local result was found; absence reasoning was recorded.")
    if observation.top_results:
        notes.append(
            "Observed local results are bounded corpus/index results, not global web recall."
        )
    return tuple(notes)


def _pending_external_observation(system: str) -> SearchUsefulnessSystemObservation:
    return SearchUsefulnessSystemObservation(
        system=system,
        observation_status="pending_manual_observation",
        top_results=(),
        usefulness_scores=None,
        notes=(
            (
                "No automated external lookup was performed. Record this baseline "
                "manually if a human reviewer observes it later."
            ),
        ),
        failure_modes=("external_baseline_pending",),
        next_eureka_work=(),
    )


def _recommendations(future_work_counts: Counter[str]) -> tuple[dict[str, Any], ...]:
    recommendations = []
    for label, count in future_work_counts.most_common():
        recommendations.append(
            {
                "label": label,
                "count": count,
                "description": _future_work_description(label),
            }
        )
    return tuple(recommendations)


def _future_work_description(label: str) -> str:
    descriptions = {
        "source_coverage_gap": "Add governed source coverage or recorded fixtures for the observed query family.",
        "live_source_gap": "Design a governed live-source strategy later; no live crawling is part of this audit.",
        "index_gap": "Improve what Local Index v0 records or exposes without adding ranking semantics.",
        "planner_gap": "Teach deterministic Query Planner v0 another bounded query family.",
        "query_interpretation_gap": "Capture missing structured intent or constraints in the planner.",
        "decomposition_gap": "Represent container/member-level evidence for packages, ISOs, scans, or support media.",
        "member_access_gap": "Expose useful member previews/readback where bounded local fixtures support it.",
        "representation_gap": "Add representation/access-path metadata for actionable units.",
        "compatibility_evidence_gap": "Add source-backed compatibility clues and host-profile evidence.",
        "identity_cluster_gap": "Group ambiguous names, versions, and source-backed states without merging truth.",
        "ranking_gap": "Future ranking work may be needed; this audit does not implement ranking.",
        "absence_reasoning_gap": "Improve miss explanations and checked-source summaries.",
        "actionability_gap": "Make the next bounded action clearer once evidence exists.",
        "surface_ux_gap": "Improve how existing structured results are presented.",
        "public_alpha_blocked": "Separate local-dev-only flows from safe public-alpha paths.",
        "external_baseline_pending": "Record human baseline observations later; no scraping was performed.",
    }
    return descriptions.get(label, "Review this failure label.")


def _dedupe_valid_labels(labels: Iterable[str]) -> tuple[str, ...]:
    values: list[str] = []
    for label in labels:
        if label not in VALID_FAILURE_LABELS:
            continue
        if label not in values:
            values.append(label)
    return tuple(values)


def _read_json_object(
    path: Path,
    errors: list[SearchUsefulnessLoadError],
) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(
            SearchUsefulnessLoadError(
                source_path=str(path),
                code="file_missing",
                message=f"Required file '{path}' was not found.",
            )
        )
        return None
    except (OSError, JSONDecodeError) as error:
        errors.append(
            SearchUsefulnessLoadError(
                source_path=str(path),
                code="invalid_json_subset_yaml",
                message=str(error),
            )
        )
        return None
    if not isinstance(payload, Mapping):
        errors.append(
            SearchUsefulnessLoadError(
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
    errors: list[SearchUsefulnessLoadError],
) -> tuple[str, ...]:
    if schema is None:
        return ()
    required = schema.get("required")
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        errors.append(
            SearchUsefulnessLoadError(
                source_path=str(schema_path),
                code="invalid_schema_required",
                message="Search-usefulness query schema must declare a string-list 'required' field.",
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


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{field_name}' must be a non-empty string.")
    return value


def _require_string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"Field '{field_name}' must be a non-empty list.")
    return tuple(_require_string(item, f"{field_name}[{index}]") for index, item in enumerate(value))


def _require_optional_label_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    labels = _require_string_tuple(value, field_name)
    for label in labels:
        if label not in VALID_FAILURE_LABELS:
            raise ValueError(f"Field '{field_name}' contains unknown label '{label}'.")
    return labels


def _require_json_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"Field '{field_name}' must be an object.")
    return {
        _require_string(key, f"{field_name}.key"): _clone_json_like(item)
        for key, item in value.items()
    }


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


def _mapping_text(value: Mapping[str, int]) -> str:
    if not value:
        return "(none)"
    return ", ".join(f"{key}={item}" for key, item in sorted(value.items()))


def _notice(code: str, severity: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "message": message}


def _build_default_catalog() -> NormalizedCatalog:
    from runtime.connectors.article_scan_recorded import ArticleScanRecordedConnector
    from runtime.connectors.github_releases import GitHubReleasesConnector
    from runtime.connectors.internet_archive_recorded import InternetArchiveRecordedConnector
    from runtime.connectors.local_bundle_fixtures import LocalBundleFixturesConnector
    from runtime.connectors.source_expansion_recorded import SourceExpansionRecordedConnector
    from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
    from runtime.engine.interfaces.extract import (
        extract_article_scan_recorded_source_record,
        extract_github_release_source_record,
        extract_internet_archive_recorded_source_record,
        extract_local_bundle_source_record,
        extract_source_expansion_recorded_source_record,
        extract_synthetic_source_record,
    )
    from runtime.engine.interfaces.normalize import (
        normalize_article_scan_recorded_record,
        normalize_extracted_record,
        normalize_github_release_record,
        normalize_internet_archive_recorded_item,
        normalize_local_bundle_record,
        normalize_source_expansion_recorded_record,
    )

    synthetic_connector = SyntheticSoftwareConnector()
    github_connector = GitHubReleasesConnector()
    internet_archive_connector = InternetArchiveRecordedConnector()
    local_bundle_connector = LocalBundleFixturesConnector()
    article_scan_connector = ArticleScanRecordedConnector()
    source_expansion_connector = SourceExpansionRecordedConnector()
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
    article_scan_records = tuple(
        normalize_article_scan_recorded_record(
            extract_article_scan_recorded_source_record(record)
        )
        for record in article_scan_connector.load_source_records()
    )
    source_expansion_records = tuple(
        normalize_source_expansion_recorded_record(
            extract_source_expansion_recorded_source_record(record)
        )
        for record in source_expansion_connector.load_source_records()
    )
    return NormalizedCatalog(
        synthetic_records
        + github_records
        + internet_archive_records
        + local_bundle_records
        + article_scan_records
        + source_expansion_records
    )
