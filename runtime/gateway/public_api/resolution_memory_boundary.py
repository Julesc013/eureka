from __future__ import annotations

from typing import Any

from runtime.engine.interfaces.public import (
    ResolutionMemoryCatalogRequest,
    ResolutionMemoryCreateRequest,
    ResolutionMemoryReadRequest,
    ResolutionMemoryRecord,
)
from runtime.engine.interfaces.service import (
    ResolutionMemoryNotFoundError,
    ResolutionMemoryService,
    ResolutionMemorySourceRunNotFoundError,
)
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


class ResolutionMemoryPublicApi:
    def __init__(self, memory_service: ResolutionMemoryService) -> None:
        self._memory_service = memory_service

    def create_memory_from_run(self, request: ResolutionMemoryCreateRequest) -> PublicApiResponse:
        try:
            memory = self._memory_service.create_memory_from_run(request)
        except ResolutionMemorySourceRunNotFoundError:
            return PublicApiResponse(
                status_code=404,
                body=resolution_memory_source_run_not_found_envelope(request.run_id),
            )
        except ValueError as error:
            return PublicApiResponse(
                status_code=400,
                body=resolution_memory_bad_request_envelope(
                    code="invalid_resolution_memory_request",
                    message=str(error),
                    run_id=request.run_id,
                ),
            )
        return PublicApiResponse(
            status_code=200,
            body=resolution_memories_to_public_envelope(
                (memory,),
                status="available",
                selected_memory_id=memory.memory_id,
                requested_run_id=request.run_id,
            ),
        )

    def get_memory(self, request: ResolutionMemoryReadRequest) -> PublicApiResponse:
        try:
            memory = self._memory_service.get_memory(request)
        except ResolutionMemoryNotFoundError:
            return PublicApiResponse(
                status_code=404,
                body=resolution_memory_not_found_envelope(request.memory_id),
            )
        return PublicApiResponse(
            status_code=200,
            body=resolution_memories_to_public_envelope(
                (memory,),
                status="available",
                selected_memory_id=memory.memory_id,
            ),
        )

    def list_memories(
        self,
        request: ResolutionMemoryCatalogRequest | None = None,
    ) -> PublicApiResponse:
        memories = self._memory_service.list_memories(request)
        return PublicApiResponse(
            status_code=200,
            body=resolution_memories_to_public_envelope(memories, status="listed"),
        )


def resolution_memories_to_public_envelope(
    memories: tuple[ResolutionMemoryRecord, ...],
    *,
    status: str,
    selected_memory_id: str | None = None,
    requested_run_id: str | None = None,
    notices: tuple[dict[str, str], ...] = (),
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": status,
        "memory_count": len(memories),
        "memories": [resolution_memory_to_public_entry(memory) for memory in memories],
    }
    if selected_memory_id is not None:
        envelope["selected_memory_id"] = selected_memory_id
    if requested_run_id is not None:
        envelope["requested_run_id"] = requested_run_id
    if notices:
        envelope["notices"] = list(notices)
    return envelope


def resolution_memory_to_public_entry(memory: ResolutionMemoryRecord) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "memory_id": memory.memory_id,
        "memory_kind": memory.memory_kind,
        "source_run_id": memory.source_run_id,
        "created_at": memory.created_at,
        "checked_source_ids": list(memory.checked_source_ids),
        "checked_source_families": list(memory.checked_source_families),
        "checked_sources": [source.to_dict() for source in memory.checked_sources],
        "result_summaries": [summary.to_dict() for summary in memory.result_summaries],
        "useful_source_ids": list(memory.useful_source_ids),
        "evidence_summary": [summary.to_dict() for summary in memory.evidence_summary],
        "notices": [notice.to_dict() for notice in memory.notices],
        "created_by_slice": memory.created_by_slice,
    }
    if memory.raw_query is not None:
        entry["raw_query"] = memory.raw_query
    if memory.task_kind is not None:
        entry["task_kind"] = memory.task_kind
    if memory.requested_value is not None:
        entry["requested_value"] = memory.requested_value
    if memory.resolution_task is not None:
        entry["resolution_task"] = memory.resolution_task.to_dict()
    if memory.absence_report is not None:
        entry["absence_report"] = memory.absence_report.to_dict()
    if memory.primary_resolved_resource_id is not None:
        entry["primary_resolved_resource_id"] = memory.primary_resolved_resource_id
    if memory.invalidation_hints is not None:
        entry["invalidation_hints"] = dict(memory.invalidation_hints)
    return entry


def resolution_memory_not_found_envelope(memory_id: str) -> dict[str, Any]:
    return {
        "status": "blocked",
        "memory_count": 0,
        "selected_memory_id": memory_id,
        "memories": [],
        "notices": [
            {
                "code": "resolution_memory_not_found",
                "severity": "warning",
                "message": f"Unknown resolution memory '{memory_id}'.",
            }
        ],
    }


def resolution_memory_source_run_not_found_envelope(run_id: str) -> dict[str, Any]:
    return {
        "status": "blocked",
        "memory_count": 0,
        "requested_run_id": run_id,
        "memories": [],
        "notices": [
            {
                "code": "resolution_memory_source_run_not_found",
                "severity": "warning",
                "message": f"Unknown source resolution run '{run_id}'.",
            }
        ],
    }


def resolution_memory_bad_request_envelope(
    *,
    code: str,
    message: str,
    run_id: str | None = None,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": "blocked",
        "memory_count": 0,
        "memories": [],
        "notices": [
            {
                "code": code,
                "severity": "warning",
                "message": message,
            }
        ],
    }
    if run_id is not None:
        envelope["requested_run_id"] = run_id
    return envelope
