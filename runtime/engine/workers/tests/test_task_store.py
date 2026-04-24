from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.engine.interfaces.public import LocalTaskRecord, Notice
from runtime.engine.workers import LocalTaskNotFoundError, LocalTaskStore


class LocalTaskStoreTestCase(unittest.TestCase):
    def test_save_load_and_list_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalTaskStore(temp_dir)
            task = LocalTaskRecord(
                task_id=store.allocate_task_id("validate_source_registry"),
                task_kind="validate_source_registry",
                status="completed",
                requested_inputs={},
                created_at="2026-04-24T00:00:00+00:00",
                started_at="2026-04-24T00:00:00+00:00",
                completed_at="2026-04-24T00:00:01+00:00",
                result_summary={"source_count": 6},
                notices=(Notice(code="task_completed", severity="info"),),
            )
            task_path = store.save_task(task)

            loaded = store.get_task(task.task_id)
            listed = store.list_tasks()

        self.assertEqual(task_path.name, f"{task.task_id}.json")
        self.assertEqual(loaded.task_id, task.task_id)
        self.assertEqual(loaded.result_summary, {"source_count": 6})
        self.assertEqual(tuple(item.task_id for item in listed), (task.task_id,))

    def test_unknown_task_raises_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalTaskStore(temp_dir)
            with self.assertRaises(LocalTaskNotFoundError):
                store.get_task("missing-task")

    def test_saved_json_is_stable_and_readable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalTaskStore(temp_dir)
            task = LocalTaskRecord(
                task_id=store.allocate_task_id("build_local_index"),
                task_kind="build_local_index",
                status="blocked",
                requested_inputs={"index_path": "D:/tmp/example.sqlite3"},
                created_at="2026-04-24T00:00:00+00:00",
                completed_at="2026-04-24T00:00:00+00:00",
                error_summary={"code": "index_path_required", "message": "missing"},
                notices=(Notice(code="index_path_required", severity="warning"),),
            )
            task_path = store.save_task(task)
            raw_payload = json.loads(task_path.read_text(encoding="utf-8"))

        self.assertEqual(raw_payload["record_kind"], "eureka.local_task")
        self.assertEqual(raw_payload["task_kind"], "build_local_index")
        self.assertEqual(raw_payload["status"], "blocked")
        self.assertEqual(raw_payload["requested_inputs"]["index_path"], "D:/tmp/example.sqlite3")


if __name__ == "__main__":
    unittest.main()
