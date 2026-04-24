from __future__ import annotations

import json
from pathlib import Path

from runtime.engine.interfaces.public.local_task import LocalTaskRecord
from runtime.engine.interfaces.service.local_task_service import LocalTaskNotFoundError
from runtime.engine.workers.local_task import (
    local_task_from_dict,
    local_task_to_dict,
)
from runtime.engine.workers.task_kinds import task_kind_cli_name


class LocalTaskStore:
    def __init__(self, root_path: str) -> None:
        self._root_path = Path(root_path)
        self._store_path = self._root_path / "local_tasks"
        self._tasks_path = self._store_path / "tasks"
        self._index_path = self._store_path / "index.json"

    def allocate_task_id(self, task_kind: str) -> str:
        index = self._read_index()
        next_sequence = int(index.get("next_task_sequence", 1))
        task_id = f"task-{task_kind_cli_name(task_kind)}-{next_sequence:04d}"
        index["next_task_sequence"] = next_sequence + 1
        self._write_index(index)
        return task_id

    def save_task(self, task: LocalTaskRecord) -> Path:
        self._tasks_path.mkdir(parents=True, exist_ok=True)
        task_path = self._tasks_path / f"{task.task_id}.json"
        task_path.write_text(
            json.dumps(local_task_to_dict(task), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return task_path

    def get_task(self, task_id: str) -> LocalTaskRecord:
        task_path = self._tasks_path / f"{task_id}.json"
        if not task_path.is_file():
            raise LocalTaskNotFoundError(task_id)
        raw_record = json.loads(task_path.read_text(encoding="utf-8"))
        return local_task_from_dict(raw_record, source_path=task_path)

    def list_tasks(self) -> tuple[LocalTaskRecord, ...]:
        if not self._tasks_path.is_dir():
            return ()
        tasks = [
            self.get_task(task_path.stem)
            for task_path in sorted(self._tasks_path.glob("*.json"))
        ]
        return tuple(tasks)

    def _read_index(self) -> dict[str, int]:
        if not self._index_path.is_file():
            return {"next_task_sequence": 1}
        raw_index = json.loads(self._index_path.read_text(encoding="utf-8"))
        if not isinstance(raw_index, dict):
            return {"next_task_sequence": 1}
        next_task_sequence = raw_index.get("next_task_sequence", 1)
        if not isinstance(next_task_sequence, int) or next_task_sequence < 1:
            next_task_sequence = 1
        return {"next_task_sequence": next_task_sequence}

    def _write_index(self, index: dict[str, int]) -> None:
        self._store_path.mkdir(parents=True, exist_ok=True)
        self._index_path.write_text(
            json.dumps(index, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
