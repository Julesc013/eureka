from __future__ import annotations

import unittest

from surfaces.web.workbench import render_local_tasks_html


class LocalTasksRenderingTestCase(unittest.TestCase):
    def test_local_tasks_rendering_shows_selected_task(self) -> None:
        html = render_local_tasks_html(
            {
                "status": "completed",
                "task_count": 1,
                "selected_task_id": "task-validate-source-registry-0001",
                "tasks": [
                    {
                        "task_id": "task-validate-source-registry-0001",
                        "task_kind": "validate_source_registry",
                        "status": "completed",
                        "requested_inputs": {},
                        "created_at": "2026-04-24T00:00:00+00:00",
                        "started_at": "2026-04-24T00:00:00+00:00",
                        "completed_at": "2026-04-24T00:00:01+00:00",
                        "result_summary": {
                            "source_count": 8,
                            "active_fixture_sources": ["local-bundle-fixtures", "synthetic-fixtures"],
                        },
                        "notices": [{"code": "task_completed", "severity": "info", "message": "done"}],
                        "created_by_slice": "local_worker_task_model_v0",
                    }
                ],
            },
            task_store_root="D:/tmp/local-tasks",
        )

        self.assertIn("Eureka Local Tasks", html)
        self.assertIn("task-validate-source-registry-0001", html)
        self.assertIn("validate_source_registry", html)
        self.assertIn("source_count=8", html)


if __name__ == "__main__":
    unittest.main()
