from __future__ import annotations

from typing import Any

from runtime.engine.interfaces.public import (
    LocalTaskReadRequest,
    LocalTaskRecord,
    LocalTaskRunRequest,
)
from runtime.engine.interfaces.service import LocalTaskNotFoundError, LocalTaskService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


class LocalTasksPublicApi:
    def __init__(self, task_service: LocalTaskService) -> None:
        self._task_service = task_service

    def run_task(self, request: LocalTaskRunRequest) -> PublicApiResponse:
        try:
            task = self._task_service.run_task(request)
        except ValueError as error:
            return PublicApiResponse(
                status_code=400,
                body=local_task_bad_request_envelope(
                    code="invalid_local_task_request",
                    message=str(error),
                    task_kind=request.task_kind,
                ),
            )
        return PublicApiResponse(
            status_code=200,
            body=local_tasks_to_public_envelope(
                (task,),
                status=task.status,
                selected_task_id=task.task_id,
            ),
        )

    def get_task(self, request: LocalTaskReadRequest) -> PublicApiResponse:
        try:
            task = self._task_service.get_task(request)
        except LocalTaskNotFoundError:
            return PublicApiResponse(
                status_code=404,
                body=local_task_not_found_envelope(request.task_id),
            )
        return PublicApiResponse(
            status_code=200,
            body=local_tasks_to_public_envelope(
                (task,),
                status=task.status,
                selected_task_id=task.task_id,
            ),
        )

    def list_tasks(self) -> PublicApiResponse:
        tasks = self._task_service.list_tasks()
        return PublicApiResponse(
            status_code=200,
            body=local_tasks_to_public_envelope(tasks, status="listed"),
        )


def local_tasks_to_public_envelope(
    tasks: tuple[LocalTaskRecord, ...],
    *,
    status: str,
    selected_task_id: str | None = None,
    notices: tuple[dict[str, str], ...] = (),
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": status,
        "task_count": len(tasks),
        "tasks": [local_task_to_public_entry(task) for task in tasks],
    }
    if selected_task_id is not None:
        envelope["selected_task_id"] = selected_task_id
    if notices:
        envelope["notices"] = list(notices)
    return envelope


def local_task_to_public_entry(task: LocalTaskRecord) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "task_id": task.task_id,
        "task_kind": task.task_kind,
        "status": task.status,
        "requested_inputs": dict(task.requested_inputs),
        "created_at": task.created_at,
        "notices": [notice.to_dict() for notice in task.notices],
        "created_by_slice": task.created_by_slice,
    }
    if task.started_at is not None:
        entry["started_at"] = task.started_at
    if task.completed_at is not None:
        entry["completed_at"] = task.completed_at
    if task.result_summary is not None:
        entry["result_summary"] = dict(task.result_summary)
    if task.error_summary is not None:
        entry["error_summary"] = dict(task.error_summary)
    if task.output_references is not None:
        entry["output_references"] = dict(task.output_references)
    return entry


def local_task_not_found_envelope(task_id: str) -> dict[str, Any]:
    return {
        "status": "blocked",
        "task_count": 0,
        "selected_task_id": task_id,
        "tasks": [],
        "notices": [
            {
                "code": "local_task_not_found",
                "severity": "warning",
                "message": f"Local task '{task_id}' was not found.",
            }
        ],
    }


def local_task_bad_request_envelope(
    *,
    code: str,
    message: str,
    task_kind: str | None = None,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": "blocked",
        "task_count": 0,
        "tasks": [],
        "notices": [
            {
                "code": code,
                "severity": "warning",
                "message": message,
            }
        ],
    }
    if task_kind is not None:
        envelope["requested_task_kind"] = task_kind
    return envelope
