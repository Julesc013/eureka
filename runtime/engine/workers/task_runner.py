from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping
from datetime import datetime, timezone

from runtime.engine.index import (
    LocalIndexEngineService,
    LocalIndexNotFoundError,
    LocalIndexSchemaError,
)
from runtime.engine.interfaces.public import (
    LocalIndexBuildRequest,
    LocalIndexQueryRequest,
    LocalTaskReadRequest,
    LocalTaskRecord,
    LocalTaskRunRequest,
    Notice,
)
from runtime.engine.interfaces.service import LocalTaskService
from runtime.engine.workers.task_kinds import (
    BUILD_LOCAL_INDEX_TASK_KIND,
    QUERY_LOCAL_INDEX_TASK_KIND,
    SUPPORTED_LOCAL_TASK_KINDS,
    VALIDATE_ARCHIVE_RESOLUTION_EVALS_TASK_KIND,
    VALIDATE_SOURCE_REGISTRY_TASK_KIND,
    normalize_task_kind,
)
from runtime.engine.workers.task_store import LocalTaskStore
from runtime.source_registry import DEFAULT_SOURCE_INVENTORY_DIR, SourceRegistry, load_source_registry


DEFAULT_ARCHIVE_RESOLUTION_EVAL_DIR = (
    Path(__file__).resolve().parents[3] / "evals" / "archive_resolution"
)


def _default_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class LocalTaskRunnerService(LocalTaskService):
    task_store: LocalTaskStore
    source_registry: SourceRegistry
    local_index_service: LocalIndexEngineService
    source_inventory_dir: Path = DEFAULT_SOURCE_INVENTORY_DIR
    archive_resolution_eval_dir: Path = DEFAULT_ARCHIVE_RESOLUTION_EVAL_DIR
    created_by_slice: str = "local_worker_task_model_v0"
    timestamp_factory: Callable[[], str] = _default_timestamp

    def run_task(self, request: LocalTaskRunRequest) -> LocalTaskRecord:
        task_kind = normalize_task_kind(request.task_kind)
        task_id = self.task_store.allocate_task_id(task_kind)
        pending_task = LocalTaskRecord(
            task_id=task_id,
            task_kind=task_kind,
            status="pending",
            requested_inputs=request.requested_inputs,
            created_at=self.timestamp_factory(),
            notices=(),
            created_by_slice=self.created_by_slice,
        )
        self.task_store.save_task(pending_task)

        running_task = LocalTaskRecord(
            task_id=task_id,
            task_kind=task_kind,
            status="running",
            requested_inputs=request.requested_inputs,
            created_at=pending_task.created_at,
            started_at=self.timestamp_factory(),
            notices=(
                Notice(
                    code="task_running",
                    severity="info",
                    message="Executing one synchronous bootstrap local task.",
                ),
            ),
            created_by_slice=self.created_by_slice,
        )
        self.task_store.save_task(running_task)

        try:
            final_task = self._dispatch_task(running_task)
        except Exception as error:
            failed_task = LocalTaskRecord(
                task_id=running_task.task_id,
                task_kind=running_task.task_kind,
                status="failed",
                requested_inputs=running_task.requested_inputs,
                created_at=running_task.created_at,
                started_at=running_task.started_at,
                completed_at=self.timestamp_factory(),
                error_summary={
                    "code": "task_execution_failed",
                    "message": str(error),
                },
                notices=running_task.notices
                + (
                    Notice(
                        code="task_failed",
                        severity="error",
                        message=str(error),
                    ),
                ),
                created_by_slice=self.created_by_slice,
            )
            self.task_store.save_task(failed_task)
            return failed_task

        self.task_store.save_task(final_task)
        return final_task

    def get_task(self, request: LocalTaskReadRequest) -> LocalTaskRecord:
        return self.task_store.get_task(request.task_id)

    def list_tasks(self) -> tuple[LocalTaskRecord, ...]:
        return self.task_store.list_tasks()

    def _dispatch_task(self, task: LocalTaskRecord) -> LocalTaskRecord:
        if task.task_kind == VALIDATE_SOURCE_REGISTRY_TASK_KIND:
            return self._complete_task(task, **self._handle_validate_source_registry())
        if task.task_kind == BUILD_LOCAL_INDEX_TASK_KIND:
            return self._handle_build_local_index(task)
        if task.task_kind == QUERY_LOCAL_INDEX_TASK_KIND:
            return self._handle_query_local_index(task)
        if task.task_kind == VALIDATE_ARCHIVE_RESOLUTION_EVALS_TASK_KIND:
            return self._complete_task(task, **self._handle_validate_archive_resolution_evals())
        return self._blocked_task(
            task,
            code="unsupported_task_kind",
            message=(
                f"Local Worker and Task Model v0 does not support task_kind '{task.task_kind}'."
            ),
        )

    def _handle_validate_source_registry(
        self,
    ) -> dict[str, Any]:
        registry = load_source_registry(self.source_inventory_dir)
        records = registry.records
        status_counts = Counter(record.status for record in records)
        active_fixture_sources = sorted(
            record.source_id for record in records if record.status == "active_fixture"
        )
        placeholder_sources = sorted(
            record.source_id for record in records if record.status == "placeholder"
        )
        return {
            "result_summary": {
                "source_count": len(records),
                "status_counts": dict(sorted(status_counts.items())),
                "active_fixture_sources": active_fixture_sources,
                "placeholder_sources": placeholder_sources,
            },
            "notices": (
                Notice(
                    code="source_registry_validated",
                    severity="info",
                    message=(
                        "Validated Source Registry v0 inventory records. "
                        "This is a synchronous bootstrap local validation task."
                    ),
                ),
            ),
        }

    def _handle_build_local_index(self, task: LocalTaskRecord) -> LocalTaskRecord:
        index_path = str(task.requested_inputs.get("index_path", "")).strip()
        if not index_path:
            return self._blocked_task(
                task,
                code="index_path_required",
                message="build_local_index requires a non-empty index_path input.",
            )
        try:
            result = self.local_index_service.build_index(
                LocalIndexBuildRequest.from_parts(index_path)
            )
        except (LocalIndexSchemaError, ValueError) as error:
            return self._blocked_task(
                task,
                code="invalid_local_index_request",
                message=str(error),
            )
        return self._complete_task(
            task,
            result_summary={
                "index_path_kind": result.metadata.index_path_kind,
                "fts_mode": result.metadata.fts_mode,
                "record_count": result.metadata.record_count,
                "record_kind_counts": dict(result.metadata.record_kind_counts),
            },
            output_references={
                "index": result.metadata.to_dict(),
            },
            notices=result.notices
            + (
                Notice(
                    code="task_completed",
                    severity="info",
                    message="Built one bootstrap local SQLite index synchronously.",
                ),
            ),
        )

    def _handle_query_local_index(self, task: LocalTaskRecord) -> LocalTaskRecord:
        index_path = str(task.requested_inputs.get("index_path", "")).strip()
        query = str(task.requested_inputs.get("query", "")).strip()
        if not index_path:
            return self._blocked_task(
                task,
                code="index_path_required",
                message="query_local_index requires a non-empty index_path input.",
            )
        if not query:
            return self._blocked_task(
                task,
                code="query_required",
                message="query_local_index requires a non-empty query input.",
            )
        try:
            result = self.local_index_service.query_index(
                LocalIndexQueryRequest.from_parts(index_path, query),
            )
        except LocalIndexNotFoundError as error:
            return self._blocked_task(
                task,
                code="local_index_not_found",
                message=str(error),
            )
        except (LocalIndexSchemaError, ValueError) as error:
            return self._blocked_task(
                task,
                code="invalid_local_index_query",
                message=str(error),
            )
        return self._complete_task(
            task,
            result_summary={
                "query": result.query,
                "result_count": len(result.results),
                "top_results": [
                    {
                        "index_record_id": item.index_record_id,
                        "record_kind": item.record_kind,
                        "label": item.label,
                        "target_ref": item.target_ref,
                        "resolved_resource_id": item.resolved_resource_id,
                        "source_id": item.source_id,
                        "source_family": item.source_family,
                    }
                    for item in result.results[:5]
                ],
                "fts_mode": result.metadata.fts_mode,
            },
            output_references={
                "index": result.metadata.to_dict(),
            },
            notices=result.notices
            + (
                Notice(
                    code="task_completed",
                    severity="info",
                    message="Queried one bootstrap local SQLite index synchronously.",
                ),
            ),
        )

    def _handle_validate_archive_resolution_evals(
        self,
    ) -> dict[str, Any]:
        eval_root = self.archive_resolution_eval_dir
        tasks_dir = eval_root / "tasks"
        if not tasks_dir.is_dir():
            raise ValueError(f"Archive-resolution eval tasks directory '{tasks_dir}' was not found.")
        schema_path = eval_root / "task.schema.yaml"
        if not schema_path.is_file():
            raise ValueError(f"Archive-resolution eval schema '{schema_path}' was not found.")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        required_fields = schema.get("required", [])
        if not isinstance(required_fields, list):
            required_fields = []
        task_ids: list[str] = []
        query_families: list[str] = []
        for task_path in sorted(tasks_dir.glob("*.yaml")):
            task_payload = json.loads(task_path.read_text(encoding="utf-8"))
            if not isinstance(task_payload, Mapping):
                raise ValueError(f"{task_path} must contain one JSON object.")
            for field_name in required_fields:
                if field_name not in task_payload:
                    raise ValueError(f"{task_path} is missing required field '{field_name}'.")
            task_id = task_payload.get("id")
            if not isinstance(task_id, str) or not task_id:
                raise ValueError(f"{task_path} must define a non-empty 'id'.")
            task_ids.append(task_id)
            query_family = task_payload.get("query_family")
            if isinstance(query_family, str) and query_family:
                query_families.append(query_family)
        return {
            "result_summary": {
                "eval_packet": "archive_resolution",
                "task_count": len(task_ids),
                "task_ids": task_ids,
                "query_families": sorted(set(query_families)),
            },
            "notices": (
                Notice(
                    code="archive_resolution_evals_validated",
                    severity="info",
                    message=(
                        "Validated archive-resolution eval packet structure. "
                        "This is a synchronous bootstrap local validation task, not a benchmark runner."
                    ),
                ),
            ),
        }

    def _complete_task(
        self,
        task: LocalTaskRecord,
        *,
        result_summary: Mapping[str, Any] | None = None,
        output_references: Mapping[str, Any] | None = None,
        notices: tuple[Notice, ...] = (),
    ) -> LocalTaskRecord:
        return LocalTaskRecord(
            task_id=task.task_id,
            task_kind=task.task_kind,
            status="completed",
            requested_inputs=task.requested_inputs,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=self.timestamp_factory(),
            result_summary=dict(result_summary or {}),
            output_references=dict(output_references or {}) or None,
            notices=notices,
            created_by_slice=self.created_by_slice,
        )

    def _blocked_task(self, task: LocalTaskRecord, *, code: str, message: str) -> LocalTaskRecord:
        return LocalTaskRecord(
            task_id=task.task_id,
            task_kind=task.task_kind,
            status="blocked",
            requested_inputs=task.requested_inputs,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=self.timestamp_factory(),
            error_summary={
                "code": code,
                "message": message,
            },
            notices=task.notices
            + (
                Notice(
                    code=code,
                    severity="warning",
                    message=message,
                ),
            ),
            created_by_slice=self.created_by_slice,
        )
