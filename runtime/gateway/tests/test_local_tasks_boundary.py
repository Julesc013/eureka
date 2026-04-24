from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.gateway import build_demo_local_tasks_public_api
from runtime.gateway.public_api import LocalTaskReadRequest, LocalTaskRunRequest


class LocalTasksPublicApiTestCase(unittest.TestCase):
    def test_run_read_and_list_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_local_tasks_public_api(temp_dir)
            build_response = public_api.run_task(
                LocalTaskRunRequest.from_parts(
                    "build-local-index",
                    {"index_path": str(Path(temp_dir) / "local-index.sqlite3")},
                ),
            )
            task_id = build_response.body["tasks"][0]["task_id"]
            read_response = public_api.get_task(LocalTaskReadRequest.from_parts(task_id))
            list_response = public_api.list_tasks()

        self.assertEqual(build_response.status_code, 200)
        self.assertEqual(build_response.body["status"], "completed")
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(read_response.body["selected_task_id"], task_id)
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.body["task_count"], 1)

    def test_unknown_task_returns_structured_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_local_tasks_public_api(temp_dir)
            response = public_api.get_task(LocalTaskReadRequest.from_parts("missing-task"))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["notices"][0]["code"], "local_task_not_found")


if __name__ == "__main__":
    unittest.main()
