from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_archive_resolution_evals.py"


class ArchiveResolutionEvalScriptTestCase(unittest.TestCase):
    def test_script_runs_full_suite_plain_text(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("Archive resolution evals", completed.stdout)
        self.assertIn("task_count: 6", completed.stdout)
        self.assertIn("capability_gap", completed.stdout)

    def test_script_runs_one_task(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--task", "windows_7_apps"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("windows_7_apps", completed.stdout)
        self.assertIn("task_count: 1", completed.stdout)

    def test_script_json_mode_and_output_path_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "report.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--task",
                    "windows_7_apps",
                    "--json",
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            stdout_payload = json.loads(completed.stdout)
            file_payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(stdout_payload["total_task_count"], 1)
        self.assertEqual(file_payload["total_task_count"], 1)
        self.assertEqual(stdout_payload["tasks"][0]["task_id"], "windows_7_apps")


if __name__ == "__main__":
    unittest.main()
