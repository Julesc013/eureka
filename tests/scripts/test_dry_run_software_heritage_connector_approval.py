import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DryRunSoftwareHeritageConnectorApprovalTests(unittest.TestCase):
    def test_dry_run_outputs_json_and_writes_no_files(self):
        before = {p.relative_to(ROOT) for p in ROOT.rglob("*") if p.is_file()}
        c = subprocess.run(
            [sys.executable, "scripts/dry_run_software_heritage_connector_approval.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        after = {p.relative_to(ROOT) for p in ROOT.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        r = json.loads(c.stdout)
        self.assertEqual(r["approval_record_kind"], "software_heritage_connector_approval")
        self.assertEqual(r["status"], "draft_example")
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_source_called",
            "external_calls_performed",
            "software_heritage_api_called",
            "swhid_resolved_live",
            "origin_lookup_performed",
            "content_blob_lookup_performed",
            "repository_cloned",
            "source_code_downloaded",
            "source_archive_downloaded",
            "source_file_retrieved",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "master_index_mutated",
            "downloads_enabled",
            "file_retrieval_enabled",
            "software_heritage_token_used",
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "source_code_safety_claimed",
            "source_completeness_claimed",
        ):
            self.assertFalse(r[key], key)


if __name__ == "__main__":
    unittest.main()
