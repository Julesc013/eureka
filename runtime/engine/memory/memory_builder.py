from __future__ import annotations

from dataclasses import dataclass

from runtime.engine.interfaces.public import ResolutionMemoryRecord, ResolutionMemoryResultSummary
from runtime.engine.interfaces.public.resolution_run import ResolutionRunRecord
from runtime.engine.provenance import EvidenceSummary


MAX_RESULT_SUMMARIES = 5
MAX_EVIDENCE_SUMMARIES = 8


@dataclass(frozen=True)
class ResolutionMemoryBuilder:
    created_by_slice: str = "resolution_memory_v0"

    def build_from_run(
        self,
        *,
        memory_id: str,
        run: ResolutionRunRecord,
        created_at: str,
    ) -> ResolutionMemoryRecord:
        if run.status != "completed":
            raise ValueError(
                f"Resolution Memory v0 can only be created from completed runs, not '{run.status}'."
            )
        if run.result_summary is None and run.absence_report is None:
            raise ValueError(
                "Resolution Memory v0 requires either a completed result summary or an absence report."
            )

        memory_kind = _memory_kind_for_run(run)
        result_summaries = _result_summaries_from_run(run)
        useful_source_ids = _useful_source_ids_from_run(run, result_summaries)
        evidence_summary = _evidence_summary_from_run(run)
        primary_resolved_resource_id = _primary_resolved_resource_id(result_summaries)

        return ResolutionMemoryRecord(
            memory_id=memory_id,
            memory_kind=memory_kind,
            source_run_id=run.run_id,
            raw_query=_raw_query_from_run(run),
            task_kind=_task_kind_from_run(run),
            requested_value=run.requested_value,
            resolution_task=run.resolution_task,
            checked_source_ids=run.checked_source_ids,
            checked_source_families=run.checked_source_families,
            checked_sources=run.checked_sources,
            result_summaries=result_summaries,
            absence_report=run.absence_report,
            useful_source_ids=useful_source_ids,
            primary_resolved_resource_id=primary_resolved_resource_id,
            evidence_summary=evidence_summary,
            created_at=created_at,
            notices=(),
            created_by_slice=self.created_by_slice,
            invalidation_hints={
                "created_from_run": run.run_id,
                "checked_source_ids": list(run.checked_source_ids),
                "invalidation_policy": "future_work",
            },
        )


def _memory_kind_for_run(run: ResolutionRunRecord) -> str:
    if run.absence_report is not None:
        return "absence_finding"
    if run.run_kind == "exact_resolution":
        return "successful_resolution"
    return "successful_search"


def _raw_query_from_run(run: ResolutionRunRecord) -> str | None:
    if run.resolution_task is not None:
        return run.resolution_task.raw_query
    if run.run_kind in {"deterministic_search", "planned_search", "local_index_search"}:
        return run.requested_value
    return None


def _task_kind_from_run(run: ResolutionRunRecord) -> str:
    if run.resolution_task is not None:
        return run.resolution_task.task_kind
    return run.run_kind


def _result_summaries_from_run(
    run: ResolutionRunRecord,
) -> tuple[ResolutionMemoryResultSummary, ...]:
    if run.result_summary is None:
        return ()
    summaries: list[ResolutionMemoryResultSummary] = []
    for item in run.result_summary.items[:MAX_RESULT_SUMMARIES]:
        summaries.append(
            ResolutionMemoryResultSummary(
                target_ref=item.target_ref,
                object_summary=item.object_summary,
                resolved_resource_id=item.resolved_resource_id,
                source=item.source,
            )
        )
    return tuple(summaries)


def _useful_source_ids_from_run(
    run: ResolutionRunRecord,
    result_summaries: tuple[ResolutionMemoryResultSummary, ...],
) -> tuple[str, ...]:
    source_ids: list[str] = []
    for summary in result_summaries:
        if summary.source is not None and summary.source.source_id is not None:
            source_ids.append(summary.source.source_id)
    if not source_ids and run.absence_report is not None:
        for near_match in run.absence_report.near_matches:
            if near_match.source is not None and near_match.source.source_id is not None:
                source_ids.append(near_match.source.source_id)
    return tuple(sorted(set(source_ids)))


def _primary_resolved_resource_id(
    result_summaries: tuple[ResolutionMemoryResultSummary, ...],
) -> str | None:
    if not result_summaries:
        return None
    return result_summaries[0].resolved_resource_id


def _evidence_summary_from_run(run: ResolutionRunRecord) -> tuple[EvidenceSummary, ...]:
    evidence_by_key: dict[tuple[str, str, str, str, str, str | None, str | None], EvidenceSummary] = {}
    if run.result_summary is not None:
        for item in run.result_summary.items:
            for evidence in item.evidence:
                key = _evidence_key(evidence)
                evidence_by_key.setdefault(key, evidence)
    if run.absence_report is not None:
        for near_match in run.absence_report.near_matches:
            for evidence in near_match.evidence:
                key = _evidence_key(evidence)
                evidence_by_key.setdefault(key, evidence)
    ordered_evidence = list(evidence_by_key.values())[:MAX_EVIDENCE_SUMMARIES]
    return tuple(ordered_evidence)


def _evidence_key(
    evidence: EvidenceSummary,
) -> tuple[str, str, str, str, str, str | None, str | None]:
    return (
        evidence.claim_kind,
        evidence.claim_value,
        evidence.asserted_by_family,
        evidence.evidence_kind,
        evidence.evidence_locator,
        evidence.asserted_by_label,
        evidence.asserted_at,
    )
