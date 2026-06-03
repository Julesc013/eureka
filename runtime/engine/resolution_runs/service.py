from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import hashlib
from typing import Any, Callable, Mapping, Protocol

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.public import (
    CheckedSourceSummary,
    DeterministicSearchRunRequest,
    ExactResolutionRunRequest,
    Notice,
    PlannedSearchRunRequest,
    QueryPlanRequest,
    ResolveAbsenceRequest,
    ResolutionRequest,
    ResolutionRunRecord,
    ResolutionRunResultItem,
    ResolutionRunResultSummary,
    SearchAbsenceRequest,
    SearchRequest,
)
from runtime.engine.interfaces.service import (
    AbsenceService,
    QueryPlannerService,
    ResolutionRunService,
    ResolutionService,
    SearchService,
)
from runtime.engine.query_planner import derive_search_query_from_task
from runtime.engine.resolve.source_summary import normalized_record_to_source_summary
from runtime.engine.resolution_runs.run_store import LocalResolutionRunStore
from runtime.source.registry import SourceRecordNotFoundError, SourceRegistry


@dataclass(frozen=True)
class ResolutionRunFallbackPolicy:
    enabled: bool = False
    allowed_source_families: tuple[str, ...] = ("internet_archive",)
    disabled_source_families: tuple[str, ...] = ()
    max_requests: int = 1
    candidate_limit: int = 5
    timeout_seconds: int = 5


class ResolutionRunFallbackProvider(Protocol):
    def search_metadata_candidates(self, query: str, limit: int) -> Mapping[str, Any]:
        """Return metadata-only fallback candidates for a run-local search miss."""


@dataclass(frozen=True)
class LocalResolutionRunService(ResolutionRunService):
    catalog: NormalizedCatalog
    source_registry: SourceRegistry
    resolution_service: ResolutionService
    search_service: SearchService
    absence_service: AbsenceService
    run_store: LocalResolutionRunStore
    query_planner: QueryPlannerService | None = None
    fallback_provider: ResolutionRunFallbackProvider | None = None
    fallback_policy: ResolutionRunFallbackPolicy = field(default_factory=ResolutionRunFallbackPolicy)
    created_by_slice: str = "resolution_runs_v0"
    timestamp_factory: Callable[[], datetime | str] | None = None

    def run_exact_resolution(self, request: ExactResolutionRunRequest) -> ResolutionRunRecord:
        run_id = self.run_store.allocate_run_id("exact_resolution")
        started_at = self._timestamp()
        checked_sources = _collect_checked_sources(self.catalog, self.source_registry)
        checked_source_ids = tuple(source.source_id for source in checked_sources)
        checked_source_families = tuple(source.source_family for source in checked_sources)
        try:
            outcome = self.resolution_service.resolve(ResolutionRequest.from_parts(request.target_ref))
            result_summary = None
            absence_report = None
            notices = outcome.notices
            if outcome.result is not None:
                primary_object = outcome.result.primary_object
                if primary_object is not None:
                    result_summary = ResolutionRunResultSummary(
                        result_kind="exact_resolution",
                        result_count=1,
                        items=(
                            ResolutionRunResultItem(
                                target_ref=request.target_ref,
                                object_summary=primary_object,
                                resolved_resource_id=outcome.result.resolved_resource_id,
                                source=outcome.result.source,
                                evidence=outcome.result.evidence,
                            ),
                        ),
                    )
            else:
                absence_report = self.absence_service.explain_resolution_miss(
                    ResolveAbsenceRequest.from_parts(request.target_ref),
                )
            run = ResolutionRunRecord(
                run_id=run_id,
                run_kind="exact_resolution",
                requested_value=request.target_ref,
                status="completed",
                started_at=started_at,
                completed_at=self._timestamp(),
                checked_source_ids=checked_source_ids,
                checked_source_families=checked_source_families,
                checked_sources=checked_sources,
                result_summary=result_summary,
                absence_report=absence_report,
                notices=notices,
                created_by_slice=self.created_by_slice,
            )
        except Exception as error:
            run = ResolutionRunRecord(
                run_id=run_id,
                run_kind="exact_resolution",
                requested_value=request.target_ref,
                status="failed",
                started_at=started_at,
                completed_at=self._timestamp(),
                checked_source_ids=checked_source_ids,
                checked_source_families=checked_source_families,
                checked_sources=checked_sources,
                notices=(
                    _failure_notice(
                        "resolution_run_failed",
                        f"Resolution run failed: {error}",
                    ),
                ),
                created_by_slice=self.created_by_slice,
            )
        return self.run_store.save_run(run)

    def run_deterministic_search(
        self,
        request: DeterministicSearchRunRequest,
    ) -> ResolutionRunRecord:
        return self._run_search(
            request.query,
            run_kind="deterministic_search",
            requested_value=request.query,
            resolution_task=None,
        )

    def run_planned_search(self, request: PlannedSearchRunRequest) -> ResolutionRunRecord:
        if self.query_planner is None:
            raise ValueError("Query Planner v0 is not configured for planned-search runs.")
        resolution_task = self.query_planner.plan_query(
            QueryPlanRequest.from_parts(request.raw_query),
        )
        search_query = derive_search_query_from_task(resolution_task)
        return self._run_search(
            search_query,
            run_kind="planned_search",
            requested_value=request.raw_query,
            resolution_task=resolution_task,
        )

    def _run_search(
        self,
        search_query: str,
        *,
        run_kind: str,
        requested_value: str,
        resolution_task,
    ) -> ResolutionRunRecord:
        run_id = self.run_store.allocate_run_id(run_kind)
        started_at = self._timestamp()
        checked_sources = _collect_checked_sources(self.catalog, self.source_registry)
        checked_source_ids = tuple(source.source_id for source in checked_sources)
        checked_source_families = tuple(source.source_family for source in checked_sources)
        try:
            response = self.search_service.search(SearchRequest.from_parts(search_query))
            notices = ()
            result_summary = None
            absence_report = None
            fallback_summary = None
            if response.results:
                result_summary = ResolutionRunResultSummary(
                    result_kind="search_results",
                    result_count=len(response.results),
                    items=tuple(
                        ResolutionRunResultItem(
                            target_ref=result.target_ref,
                            object_summary=result.object_summary,
                            resolved_resource_id=result.resolved_resource_id,
                            source=result.source,
                            evidence=result.evidence,
                        )
                        for result in response.results
                    ),
                )
            else:
                absence_report = self.absence_service.explain_search_miss(
                    SearchAbsenceRequest.from_parts(search_query),
                )
                if response.absence is not None:
                    notices = (response.absence,)
                fallback_summary = self._run_indexless_fallback(
                    search_query,
                    trigger="local_lookup_no_results",
                )
                if fallback_summary is not None:
                    notices = notices + (_fallback_notice(fallback_summary),)
            run = ResolutionRunRecord(
                run_id=run_id,
                run_kind=run_kind,
                requested_value=requested_value,
                status="completed",
                started_at=started_at,
                completed_at=self._timestamp(),
                checked_source_ids=checked_source_ids,
                checked_source_families=checked_source_families,
                checked_sources=checked_sources,
                resolution_task=resolution_task,
                result_summary=result_summary,
                absence_report=absence_report,
                fallback_summary=fallback_summary,
                notices=notices,
                created_by_slice=self.created_by_slice,
            )
        except Exception as error:
            fallback_summary = self._run_indexless_fallback(
                search_query,
                trigger="local_lookup_unavailable",
            )
            if fallback_summary is not None:
                run = ResolutionRunRecord(
                    run_id=run_id,
                    run_kind=run_kind,
                    requested_value=requested_value,
                    status="completed",
                    started_at=started_at,
                    completed_at=self._timestamp(),
                    checked_source_ids=checked_source_ids,
                    checked_source_families=checked_source_families,
                    checked_sources=checked_sources,
                    resolution_task=resolution_task,
                    fallback_summary=fallback_summary,
                    notices=(
                        _warning_notice(
                            "local_lookup_unavailable",
                            "Local search lookup was unavailable; fallback state was recorded.",
                        ),
                        _fallback_notice(fallback_summary),
                    ),
                    created_by_slice=self.created_by_slice,
                )
            else:
                run = ResolutionRunRecord(
                    run_id=run_id,
                    run_kind=run_kind,
                    requested_value=requested_value,
                    status="failed",
                    started_at=started_at,
                    completed_at=self._timestamp(),
                    checked_source_ids=checked_source_ids,
                    checked_source_families=checked_source_families,
                    checked_sources=checked_sources,
                    resolution_task=resolution_task,
                    notices=(
                        _failure_notice(
                            "resolution_run_failed",
                            f"Resolution run failed: {error}",
                        ),
                    ),
                    created_by_slice=self.created_by_slice,
                )
        return self.run_store.save_run(run)

    def _run_indexless_fallback(
        self,
        search_query: str,
        *,
        trigger: str,
    ) -> dict[str, Any] | None:
        policy = self.fallback_policy
        provider = self.fallback_provider
        if provider is None and not policy.enabled:
            return None

        source_family = _provider_source_family(provider)
        source_id = _provider_source_id(provider)
        if not policy.enabled:
            return _fallback_summary(
                search_query,
                status="policy_blocked",
                trigger=trigger,
                policy=policy,
                source_id=source_id,
                source_family=source_family,
                reason_codes=("fallback_disabled",),
            )
        if provider is None:
            return _fallback_summary(
                search_query,
                status="unavailable",
                trigger=trigger,
                policy=policy,
                source_id=source_id,
                source_family=source_family,
                reason_codes=("fallback_provider_unavailable",),
                failure_reason="fallback_provider_unavailable",
            )

        allowed_families = _normalized_names(policy.allowed_source_families)
        disabled_families = _normalized_names(policy.disabled_source_families)
        normalized_source_family = source_family.casefold()
        if normalized_source_family in disabled_families:
            return _fallback_summary(
                search_query,
                status="policy_blocked",
                trigger=trigger,
                policy=policy,
                source_id=source_id,
                source_family=source_family,
                reason_codes=("source_family_disabled",),
            )
        if allowed_families and normalized_source_family not in allowed_families:
            return _fallback_summary(
                search_query,
                status="policy_blocked",
                trigger=trigger,
                policy=policy,
                source_id=source_id,
                source_family=source_family,
                reason_codes=("source_family_not_allowlisted",),
            )
        if policy.max_requests < 1 or policy.candidate_limit < 1:
            return _fallback_summary(
                search_query,
                status="unavailable",
                trigger=trigger,
                policy=policy,
                source_id=source_id,
                source_family=source_family,
                reason_codes=("fallback_budget_exceeded",),
                failure_reason="fallback_budget_exceeded",
            )
        if policy.timeout_seconds <= 0:
            return _fallback_summary(
                search_query,
                status="unavailable",
                trigger=trigger,
                policy=policy,
                source_id=source_id,
                source_family=source_family,
                reason_codes=("fallback_timeout_budget_exceeded",),
                failure_reason="fallback_timeout_budget_exceeded",
            )

        try:
            source_result = dict(
                provider.search_metadata_candidates(
                    search_query,
                    min(policy.candidate_limit, 25),
                )
            )
        except TimeoutError:
            return _fallback_summary(
                search_query,
                status="unavailable",
                trigger=trigger,
                policy=policy,
                source_id=source_id,
                source_family=source_family,
                reason_codes=("source_timeout",),
                failure_reason="source_timeout",
                source_observation=_source_observation_from_failure(
                    search_query,
                    source_id=source_id,
                    source_family=source_family,
                    status="timeout",
                    failure_reason="source_timeout",
                ),
            )
        except Exception:
            return _fallback_summary(
                search_query,
                status="unavailable",
                trigger=trigger,
                policy=policy,
                source_id=source_id,
                source_family=source_family,
                reason_codes=("source_error",),
                failure_reason="source_error",
                source_observation=_source_observation_from_failure(
                    search_query,
                    source_id=source_id,
                    source_family=source_family,
                    status="failed",
                    failure_reason="source_error",
                ),
            )

        observed_source_family = _string_or_default(source_result.get("source_family"), source_family)
        observed_source_id = _string_or_default(source_result.get("source_id"), source_id)
        if allowed_families and observed_source_family.casefold() not in allowed_families:
            return _fallback_summary(
                search_query,
                status="policy_blocked",
                trigger=trigger,
                policy=policy,
                source_id=observed_source_id,
                source_family=observed_source_family,
                reason_codes=("source_family_not_allowlisted",),
                source_observation=_source_observation_from_result(
                    search_query,
                    source_result,
                    source_id=observed_source_id,
                    source_family=observed_source_family,
                ),
            )

        source_observation = _source_observation_from_result(
            search_query,
            source_result,
            source_id=observed_source_id,
            source_family=observed_source_family,
        )
        if _non_negative_int(source_result.get("total_http_requests"), 1) > policy.max_requests:
            return _fallback_summary(
                search_query,
                status="unavailable",
                trigger=trigger,
                policy=policy,
                source_id=observed_source_id,
                source_family=observed_source_family,
                reason_codes=("fallback_budget_exceeded",),
                failure_reason="fallback_budget_exceeded",
                source_observation=source_observation,
            )

        source_status = _string_or_default(source_result.get("status"), "unknown")
        if source_status != "succeeded":
            return _fallback_summary(
                search_query,
                status="unavailable",
                trigger=trigger,
                policy=policy,
                source_id=observed_source_id,
                source_family=observed_source_family,
                reason_codes=(f"source_{source_status}",),
                failure_reason=_string_or_default(source_result.get("failure_reason"), f"source_{source_status}"),
                source_observation=source_observation,
            )

        candidates = tuple(
            _fallback_candidate_from_source_candidate(
                candidate,
                source_id=observed_source_id,
                source_family=observed_source_family,
            )
            for candidate in _candidate_mappings(source_result.get("candidates"), policy.candidate_limit)
        )
        if candidates:
            return _fallback_summary(
                search_query,
                status="candidate",
                trigger=trigger,
                policy=policy,
                source_id=observed_source_id,
                source_family=observed_source_family,
                reason_codes=("fallback_candidates_available",),
                source_observation=source_observation,
                candidates=candidates,
            )

        return _fallback_summary(
            search_query,
            status="need",
            trigger=trigger,
            policy=policy,
            source_id=observed_source_id,
            source_family=observed_source_family,
            reason_codes=("fallback_no_candidates",),
            source_observation=source_observation,
            needs=(_fallback_need(search_query, reason_code="fallback_no_candidates"),),
        )

    def get_run(self, run_id: str) -> ResolutionRunRecord:
        return self.run_store.get_run(run_id)

    def list_runs(self) -> tuple[ResolutionRunRecord, ...]:
        return self.run_store.list_runs()

    def _timestamp(self) -> str:
        factory = self.timestamp_factory or _default_timestamp
        value = factory()
        if isinstance(value, datetime):
            return value.astimezone(UTC).isoformat(timespec="seconds")
        return str(value)


def _default_timestamp() -> datetime:
    return datetime.now(tz=UTC)


def _collect_checked_sources(
    catalog: NormalizedCatalog,
    source_registry: SourceRegistry,
) -> tuple[CheckedSourceSummary, ...]:
    checked_by_id: dict[str, CheckedSourceSummary] = {}
    for record in catalog.records:
        source_summary = normalized_record_to_source_summary(record)
        if source_summary.source_id is None:
            continue
        if source_summary.source_id in checked_by_id:
            continue
        try:
            source_record = source_registry.get_record(source_summary.source_id)
        except SourceRecordNotFoundError:
            checked_by_id[source_summary.source_id] = CheckedSourceSummary(
                source_id=source_summary.source_id,
                name=source_summary.label or source_summary.source_id,
                source_family=source_summary.family,
                status="unknown",
                trust_lane="unknown",
            )
            continue
        checked_by_id[source_record.source_id] = CheckedSourceSummary(
            source_id=source_record.source_id,
            name=source_record.name,
            source_family=source_record.source_family,
            status=source_record.status,
            trust_lane=source_record.trust_lane,
        )
    return tuple(checked_by_id[source_id] for source_id in sorted(checked_by_id))


def _fallback_summary(
    search_query: str,
    *,
    status: str,
    trigger: str,
    policy: ResolutionRunFallbackPolicy,
    source_id: str,
    source_family: str,
    reason_codes: tuple[str, ...],
    failure_reason: str | None = None,
    source_observation: Mapping[str, Any] | None = None,
    candidates: tuple[Mapping[str, Any], ...] = (),
    needs: tuple[Mapping[str, Any], ...] = (),
) -> dict[str, Any]:
    allowed_families = _normalized_names(policy.allowed_source_families)
    return {
        "schema_version": "eureka.resolution_run.indexless_fallback.v0",
        "mode": "indexless_live_search_fallback",
        "status": status,
        "trigger": trigger,
        "query": search_query,
        "source_id": source_id,
        "source_family": source_family,
        "source_allowlisted": not allowed_families or source_family.casefold() in allowed_families,
        "fallback_enabled": policy.enabled,
        "reason_codes": list(reason_codes),
        "failure_reason": failure_reason,
        "budget": {
            "max_requests": policy.max_requests,
            "candidate_limit": policy.candidate_limit,
            "timeout_seconds": policy.timeout_seconds,
        },
        "source_observation": dict(source_observation) if source_observation is not None else None,
        "candidate_count": len(candidates),
        "candidates": [dict(candidate) for candidate in candidates],
        "need_count": len(needs),
        "needs": [dict(need) for need in needs],
        "accepted_truth": False,
        "verified": False,
        "review_required": status == "candidate",
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_action_posture": {
            "allowed": ["view", "inspect_evidence"],
            "operator_actions_exposed": False,
            "unsafe_actions_enabled": False,
        },
        "limitations": [
            "candidate_not_reviewed_truth",
            "metadata_only",
            "no_download",
            "no_file_fetch",
            "no_wayback_replay",
            "no_public_source_fanout",
        ],
    }


def _source_observation_from_result(
    search_query: str,
    result: Mapping[str, Any],
    *,
    source_id: str,
    source_family: str,
) -> dict[str, Any]:
    source_status = _string_or_default(result.get("status"), "unknown")
    candidates = result.get("candidates")
    candidate_count = len(candidates) if isinstance(candidates, list) else _non_negative_int(result.get("candidate_count"), 0)
    return {
        "schema_version": "eureka.source_observation.summary.v0",
        "observation_id": _stable_id("source-observation", f"{source_id}:{source_status}:{search_query}"),
        "status": source_status,
        "source_id": source_id,
        "source_family": source_family,
        "source_label": _string_or_default(result.get("source_label"), source_id),
        "candidate_count": candidate_count,
        "total_http_requests": _non_negative_int(result.get("total_http_requests"), 0),
        "external_call_performed": _bool_value(result.get("live_call_performed")),
        "metadata_request_performed": _bool_value(result.get("metadata_request_performed")),
        "raw_response_committed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "accepted_truth": False,
        "verified": False,
        "review_required": True,
        "limitations": _string_list(result.get("limitations"))
        or ["metadata_only", "candidate_not_reviewed_truth"],
        "warnings": _string_list(result.get("warnings")),
    }


def _source_observation_from_failure(
    search_query: str,
    *,
    source_id: str,
    source_family: str,
    status: str,
    failure_reason: str,
) -> dict[str, Any]:
    return {
        "schema_version": "eureka.source_observation.summary.v0",
        "observation_id": _stable_id("source-observation", f"{source_id}:{failure_reason}:{search_query}"),
        "status": status,
        "source_id": source_id,
        "source_family": source_family,
        "candidate_count": 0,
        "total_http_requests": 0,
        "external_call_performed": False,
        "metadata_request_performed": False,
        "raw_response_committed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "accepted_truth": False,
        "verified": False,
        "review_required": True,
        "failure_reason": failure_reason,
        "limitations": ["metadata_only", "candidate_not_reviewed_truth"],
        "warnings": [failure_reason],
    }


def _fallback_candidate_from_source_candidate(
    candidate: Mapping[str, Any],
    *,
    source_id: str,
    source_family: str,
) -> dict[str, Any]:
    candidate_id = _string_or_default(
        candidate.get("candidate_id"),
        _stable_id("fallback-candidate", str(candidate)),
    )
    title = _string_or_default(candidate.get("candidate_title") or candidate.get("title"), candidate_id)
    summary = _string_or_default(
        candidate.get("candidate_summary") or candidate.get("summary") or candidate.get("description"),
        "Metadata candidate returned by governed fallback; review is required before promotion.",
    )
    source_locator = candidate.get("source_locator")
    return {
        "schema_version": "eureka.fallback_candidate.summary.v0",
        "candidate_id": candidate_id,
        "status": "candidate",
        "title": title,
        "summary": summary,
        "source_id": _string_or_default(candidate.get("source_id"), source_id),
        "source_family": _string_or_default(candidate.get("source_family"), source_family),
        "source_locator": dict(source_locator) if isinstance(source_locator, Mapping) else {},
        "accepted_truth": False,
        "verified": False,
        "review_required": True,
        "public_actions": ["view", "inspect_evidence"],
        "limitations": _string_list(candidate.get("limitations"))
        or ["metadata_only", "candidate_not_reviewed_truth"],
        "warnings": _string_list(candidate.get("warnings")),
    }


def _fallback_need(search_query: str, *, reason_code: str) -> dict[str, Any]:
    return {
        "schema_version": "eureka.search_need.summary.v0",
        "need_id": _stable_id("search-need", search_query),
        "status": "need",
        "query": search_query,
        "reason_code": reason_code,
        "summary": "No reviewed local result or fallback candidate was available for this query.",
        "accepted_truth": False,
        "verified": False,
        "review_required": False,
    }


def _provider_source_family(provider: ResolutionRunFallbackProvider | None) -> str:
    if provider is None:
        return "unconfigured"
    return _string_or_default(
        getattr(provider, "source_family", None) or getattr(provider, "SOURCE_FAMILY", None),
        "internet_archive",
    )


def _provider_source_id(provider: ResolutionRunFallbackProvider | None) -> str:
    if provider is None:
        return "unconfigured"
    return _string_or_default(
        getattr(provider, "source_id", None) or getattr(provider, "SOURCE_ID", None),
        "internet_archive_metadata",
    )


def _fallback_notice(summary: Mapping[str, Any]) -> Notice:
    status = _string_or_default(summary.get("status"), "unknown")
    severity = "info" if status in {"candidate", "need"} else "warning"
    return Notice(
        code=f"indexless_fallback_{status}",
        severity=severity,
        message=f"Indexless fallback returned {status}.",
    )


def _failure_notice(code: str, message: str):
    return Notice(code=code, severity="error", message=message)


def _warning_notice(code: str, message: str):
    return Notice(code=code, severity="warning", message=message)


def _normalized_names(values: tuple[str, ...]) -> set[str]:
    return {value.strip().casefold() for value in values if isinstance(value, str) and value.strip()}


def _string_or_default(value: Any, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _candidate_mappings(value: Any, limit: int) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value[:limit] if isinstance(item, Mapping)]


def _bool_value(value: Any) -> bool:
    return value is True


def _non_negative_int(value: Any, default: int) -> int:
    if isinstance(value, int) and value >= 0:
        return value
    return default


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"
