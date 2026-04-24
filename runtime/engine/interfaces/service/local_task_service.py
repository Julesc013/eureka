from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.local_task import (
    LocalTaskReadRequest,
    LocalTaskRecord,
    LocalTaskRunRequest,
)


class LocalTaskNotFoundError(LookupError):
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Unknown local task '{task_id}'.")


class LocalTaskService(Protocol):
    def run_task(self, request: LocalTaskRunRequest) -> LocalTaskRecord:
        """Create, execute, persist, and return one synchronous bootstrap local task."""

    def get_task(self, request: LocalTaskReadRequest) -> LocalTaskRecord:
        """Read one persisted synchronous bootstrap local task by task_id."""

    def list_tasks(self) -> tuple[LocalTaskRecord, ...]:
        """List persisted synchronous bootstrap local tasks."""
