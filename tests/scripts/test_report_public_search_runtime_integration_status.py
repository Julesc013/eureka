import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PublicSearchRuntimeIntegrationReporterTests(unittest.TestCase):
    def test_reporter_json_parses(self):
        completed = subprocess.run(
            [sys.executable, "scripts/report_public_search_runtime_integration_status.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["classification_matrix"]["public_search_api"], "implemented_local_runtime")

    def test_reporter_reports_no_mutation_or_external_calls(self):
        completed = subprocess.run(
            [sys.executable, "scripts/report_public_search_runtime_integration_status.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        hard = json.loads(completed.stdout)["hard_booleans"]
        self.assertTrue(hard["audit_only"])
        for key in (
            "runtime_integration_implemented",
            "public_search_live_source_fanout_enabled",
            "source_cache_dry_run_integrated_with_public_search",
            "evidence_ledger_dry_run_integrated_with_public_search",
            "connector_runtime_integrated_with_public_search",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "master_index_mutated",
            "external_calls_performed",
            "live_source_called",
            "telemetry_enabled",
            "downloads_enabled",
        ):
            self.assertFalse(hard[key], key)


if __name__ == "__main__":
    unittest.main()
