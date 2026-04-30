from __future__ import annotations

import json
import subprocess
import sys
import unittest


class PublicSearchSmokeScriptTest(unittest.TestCase):
    def test_public_search_smoke_json_parses_and_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/public_search_smoke.py", "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["created_by_slice"], "public_search_rehearsal_v0")
        self.assertEqual(report["base_runtime_slice"], "local_public_search_runtime_v0")
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["failed_checks"], 0)
        self.assertEqual(report["mode"], "local_index_only")
        self.assertFalse(report["hosted_public_deployment"])
        self.assertFalse(report["live_probes_enabled"])
        self.assertFalse(report["downloads_enabled"])
        self.assertFalse(report["installs_enabled"])
        self.assertFalse(report["uploads_enabled"])
        self.assertFalse(report["local_paths_enabled"])
        self.assertFalse(report["telemetry_enabled"])
        self.assertGreaterEqual(len(report["route_results"]), 6)
        self.assertEqual(len(report["safe_query_results"]), 9)
        self.assertEqual(len(report["blocked_request_results"]), 14)
        self.assertTrue(all(item["passed"] for item in report["safe_query_results"]))
        self.assertTrue(all(item["passed"] for item in report["blocked_request_results"]))


if __name__ == "__main__":
    unittest.main()
