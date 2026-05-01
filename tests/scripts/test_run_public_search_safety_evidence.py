from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "run_public_search_safety_evidence.py"


class RunPublicSearchSafetyEvidenceScriptTest(unittest.TestCase):
    def test_plain_runner_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(RUNNER)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: passed", completed.stdout)
        self.assertIn("blocked requests: 32/32", completed.stdout)

    def test_json_runner_passes_and_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(RUNNER), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "local_index_only")
        self.assertFalse(payload["server_started"])
        self.assertEqual(payload["summary"]["failed_checks"], 0)
        self.assertEqual(payload["forbidden_parameter_coverage"]["missing_categories"], [])
        self.assertEqual(payload["forbidden_parameter_coverage"]["passed_blocked_case_count"], 32)
        for key, value in payload["hard_booleans"].items():
            with self.subTest(key=key):
                self.assertIs(value, False)

    def test_json_runner_records_static_and_index_safety(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(RUNNER), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(all(item["passed"] for item in payload["static_handoff_results"]))
        self.assertTrue(all(item["passed"] for item in payload["public_index_results"]))
        index = payload["public_index_results"][0]
        self.assertEqual(index["document_count"], 584)
        self.assertFalse(index["contains_live_data"])
        self.assertFalse(index["contains_private_data"])
        self.assertFalse(index["contains_executables"])


if __name__ == "__main__":
    unittest.main()
