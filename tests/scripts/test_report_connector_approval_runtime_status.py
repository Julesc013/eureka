import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONNECTORS = {
    "internet_archive_metadata",
    "wayback_cdx_memento",
    "github_releases",
    "pypi_metadata",
    "npm_metadata",
    "software_heritage",
}


class ConnectorApprovalRuntimeStatusReporterTests(unittest.TestCase):
    def test_reporter_json_parses(self):
        completed = subprocess.run(
            [sys.executable, "scripts/report_connector_approval_runtime_status.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(set(payload["connector_status_matrix"].keys()), CONNECTORS)

    def test_reporter_hard_booleans_hold(self):
        completed = subprocess.run(
            [sys.executable, "scripts/report_connector_approval_runtime_status.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        hard = payload["hard_booleans"]
        self.assertTrue(hard["audit_only"])
        for key, value in hard.items():
            if key != "audit_only":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
