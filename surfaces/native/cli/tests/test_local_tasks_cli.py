from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from surfaces.native.cli.main import main


def run_cli(*args: str) -> tuple[int, str]:
    output = StringIO()
    exit_code = main(list(args), stdout=output)
    return exit_code, output.getvalue()


class LocalTasksCliTestCase(unittest.TestCase):
    def test_task_run_status_and_list_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            run_exit_code, run_output = run_cli(
                "task-run",
                "build-local-index",
                "--task-store-root",
                temp_dir,
                "--index-path",
                index_path,
            )
            status_exit_code, status_output = run_cli(
                "task-status",
                "task-build-local-index-0001",
                "--task-store-root",
                temp_dir,
            )
            list_exit_code, list_output = run_cli(
                "tasks",
                "--task-store-root",
                temp_dir,
            )

        self.assertEqual(run_exit_code, 0)
        self.assertIn("Local tasks", run_output)
        self.assertEqual(status_exit_code, 0)
        self.assertIn("task-build-local-index-0001", status_output)
        self.assertEqual(list_exit_code, 0)
        self.assertIn("build_local_index", list_output)

    def test_task_run_supports_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            exit_code, output = run_cli(
                "task-run",
                "validate-source-registry",
                "--task-store-root",
                temp_dir,
                "--json",
            )

        payload = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["task_count"], 1)


if __name__ == "__main__":
    unittest.main()
