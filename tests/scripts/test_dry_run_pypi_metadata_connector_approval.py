import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PyPIMetadataConnectorDryRunTests(unittest.TestCase):
    def test_dry_run_json_is_stdout_only_record(self):
        c = subprocess.run(
            [sys.executable, "scripts/dry_run_pypi_metadata_connector_approval.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        r = json.loads(c.stdout)
        self.assertEqual(r["approval_record_kind"], "pypi_metadata_connector_approval")
        self.assertFalse(r["connector_runtime_implemented"])
        self.assertFalse(r["connector_approved_now"])
        self.assertFalse(r["live_source_called"])
        self.assertFalse(r["external_calls_performed"])
        self.assertFalse(r["pypi_api_called"])
        self.assertFalse(r["package_metadata_fetched"])
        self.assertFalse(r["wheels_downloaded"])
        self.assertFalse(r["sdists_downloaded"])
        self.assertFalse(r["package_files_downloaded"])
        self.assertFalse(r["package_installed"])
        self.assertFalse(r["dependency_resolution_performed"])
        self.assertFalse(r["source_cache_mutated"])
        self.assertFalse(r["evidence_ledger_mutated"])
        self.assertFalse(r["master_index_mutated"])
        self.assertFalse(r["pypi_token_used"])
        self.assertFalse(r["dependency_safety_claimed"])
        self.assertFalse(r["installability_claimed"])


if __name__ == "__main__":
    unittest.main()
