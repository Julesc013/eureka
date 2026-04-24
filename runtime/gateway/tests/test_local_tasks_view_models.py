from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.gateway import build_demo_local_tasks_public_api
from runtime.gateway.public_api import LocalTaskRunRequest, local_tasks_envelope_to_view_model


class LocalTasksViewModelsTestCase(unittest.TestCase):
    def test_completed_task_envelope_coerces_to_view_model(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_local_tasks_public_api(temp_dir)
            response = public_api.run_task(
                LocalTaskRunRequest.from_parts(
                    "query-local-index",
                    {
                        "index_path": str(Path(temp_dir) / "missing.sqlite3"),
                        "query": "archive",
                    },
                ),
            )

        view_model = local_tasks_envelope_to_view_model(response.body)

        self.assertEqual(view_model["task_count"], 1)
        self.assertEqual(view_model["tasks"][0]["task_kind"], "query_local_index")
        self.assertEqual(view_model["tasks"][0]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
