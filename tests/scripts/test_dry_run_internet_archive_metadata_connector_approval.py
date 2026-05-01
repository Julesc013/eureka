import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunInternetArchiveMetadataConnectorApprovalTests(unittest.TestCase):
    def test_dry_run_json_is_stdout_only_and_safe(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_internet_archive_metadata_connector_approval.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "draft_example")
        self.assertFalse(payload["connector_runtime_implemented"])
        self.assertFalse(payload["connector_approved_now"])
        self.assertFalse(payload["live_source_called"])
        self.assertFalse(payload["external_calls_performed"])
        self.assertFalse(payload["public_search_live_fanout_enabled"])
        self.assertFalse(payload["downloads_enabled"])
        self.assertFalse(payload["file_retrieval_enabled"])
        self.assertFalse(payload["master_index_mutated"])


if __name__ == "__main__":
    unittest.main()
