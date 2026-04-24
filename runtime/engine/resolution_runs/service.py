from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.public import (
    CheckedSourceSummary,
    DeterministicSearchRunRequest,
    ExactResolutionRunRequest,
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
    ResolutionRunService,
    ResolutionService,
    SearchService,
)
from runtime.engine.resolve.source_summary import normalized_record_to_source_summary
from runtime.engine.resolution_runs.run_store import LocalResolutionRunStore
from runtime.source_registry import SourceRecordNotFoundError, SourceRegistry


@dataclass(frozen=True)
class LocalResolutionRunService(ResolutionRunService):
    catalog: NormalizedCatalog
    source_registry: SourceRegistry
    resolution_service: ResolutionService
    search_service: SearchService
    absence_service: AbsenceService
    run_store: LocalResolutionRunStore
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
        run_id = self.run_store.allocate_run_id("deterministic_search")
        started_at = self._timestamp()
        checked_sources = _collect_checked_sources(self.catalog, self.source_registry)
        checked_source_ids = tuple(source.source_id for source in checked_sources)
        checked_source_families = tuple(source.source_family for source in checked_sources)
        try:
            response = self.search_service.search(SearchRequest.from_parts(request.query))
            notices = ()
            result_summary = None
            absence_report = None
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
                    SearchAbsenceRequest.from_parts(request.query),
                )
                if response.absence is not None:
                    notices = (response.absence,)
            run = ResolutionRunRecord(
                run_id=run_id,
                run_kind="deterministic_search",
                requested_value=request.query,
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
                run_kind="deterministic_search",
                requested_value=request.query,
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


def _failure_notice(code: str, message: str):
    from runtime.engine.interfaces.public import Notice

    return Notice(code=code, severity="error", message=message)
