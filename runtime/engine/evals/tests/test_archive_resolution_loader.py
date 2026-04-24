from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.engine.evals import load_archive_resolution_eval_tasks


REPO_ROOT = Path(__file__).resolve().parents[4]
ARCHIVE_RESOLUTION_ROOT = REPO_ROOT / "evals" / "archive_resolution"


class ArchiveResolutionEvalLoaderTestCase(unittest.TestCase):
    def test_loads_all_current_tasks(self) -> None:
        result = load_archive_resolution_eval_tasks(ARCHIVE_RESOLUTION_ROOT)

        self.assertEqual(result.errors, ())
        self.assertEqual(result.task_count, 6)
        self.assertEqual(
            sorted(task.task_id for task in result.tasks),
            [
                "article_inside_magazine_scan",
                "driver_inside_support_cd",
                "latest_firefox_before_xp_drop",
                "old_blue_ftp_client_xp",
                "win98_registry_repair",
                "windows_7_apps",
            ],
        )

    def test_expected_plan_fields_are_coherent(self) -> None:
        result = load_archive_resolution_eval_tasks(ARCHIVE_RESOLUTION_ROOT)

        for task in result.tasks:
            with self.subTest(task=task.task_id):
                self.assertIsInstance(task.expected_plan, dict)
                self.assertIsInstance(task.expected_plan["task_kind"], str)
                self.assertIsInstance(task.expected_plan["object_type"], str)
                self.assertTrue(task.expected_plan["task_kind"])
                self.assertTrue(task.expected_plan["object_type"])

    def test_malformed_task_returns_structured_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "archive_resolution"
            tasks_dir = root / "tasks"
            tasks_dir.mkdir(parents=True)
            (root / "task.schema.yaml").write_text(
                (ARCHIVE_RESOLUTION_ROOT / "task.schema.yaml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            malformed = {
                "id": "broken_task",
                "query_family": "malformed",
            }
            (tasks_dir / "broken_task.yaml").write_text(
                json.dumps(malformed),
                encoding="utf-8",
            )

            result = load_archive_resolution_eval_tasks(root)

        self.assertEqual(result.task_count, 0)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].code, "malformed_task")
        self.assertIn("raw_query", result.errors[0].message)


if __name__ == "__main__":
    unittest.main()
