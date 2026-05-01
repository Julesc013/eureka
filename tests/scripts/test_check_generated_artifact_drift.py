from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_generated_artifact_drift.py"


class CheckGeneratedArtifactDriftScriptTest(unittest.TestCase):
    def test_list_succeeds(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--list"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("public_data_summaries", completed.stdout)
        self.assertIn("aide_metadata", completed.stdout)

    def test_json_passes_and_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["errors"], [])
        passed_ids = {
            item["artifact_id"]
            for item in payload["artifact_results"]
            if item["status"] == "passed"
        }
        self.assertEqual(payload["status_counts"]["passed"], len(payload["artifact_results"]))
        self.assertIn("public_search_index", passed_ids)

    def test_default_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("- static_snapshot_example: passed", completed.stdout)

    def test_single_artifact_filter(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--artifact", "test_registry", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(len(payload["artifact_results"]), 1)
        self.assertEqual(payload["artifact_results"][0]["artifact_id"], "test_registry")


if __name__ == "__main__":
    unittest.main()
