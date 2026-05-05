import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DryRunNpmMetadataConnectorApprovalTests(unittest.TestCase):
    def test_dry_run_outputs_json_and_writes_no_files(self):
        before = {p.relative_to(ROOT) for p in ROOT.rglob("*") if p.is_file()}
        c = subprocess.run(
            [sys.executable, "scripts/dry_run_npm_metadata_connector_approval.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        after = {p.relative_to(ROOT) for p in ROOT.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        r = json.loads(c.stdout)
        self.assertEqual(r["approval_record_kind"], "npm_metadata_connector_approval")
        self.assertEqual(r["status"], "draft_example")
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_source_called",
            "external_calls_performed",
            "npm_registry_api_called",
            "npm_cli_called",
            "package_metadata_fetched",
            "versions_fetched",
            "dist_tags_fetched",
            "tarball_metadata_fetched",
            "tarballs_downloaded",
            "package_files_downloaded",
            "package_installed",
            "dependency_resolution_performed",
            "lifecycle_scripts_executed",
            "npm_audit_performed",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "master_index_mutated",
            "downloads_enabled",
            "file_retrieval_enabled",
            "npm_token_used",
            "dependency_safety_claimed",
            "vulnerability_status_claimed",
            "script_safety_claimed",
            "installability_claimed",
        ):
            self.assertFalse(r[key], key)


if __name__ == "__main__":
    unittest.main()
