import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DryRunGitHubReleasesConnectorApprovalTests(unittest.TestCase):
    def test_dry_run_json_is_safe_stdout_only_record(self):
        c = subprocess.run(
            [sys.executable, "scripts/dry_run_github_releases_connector_approval.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        p = json.loads(c.stdout)
        self.assertEqual(p["approval_record_kind"], "github_releases_connector_approval")
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_source_called",
            "external_calls_performed",
            "github_api_called",
            "repository_cloned",
            "releases_fetched",
            "release_assets_downloaded",
            "source_archive_downloaded",
            "public_search_live_fanout_enabled",
            "arbitrary_repository_fetch_allowed",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "master_index_mutated",
            "github_token_used",
        ):
            self.assertFalse(p[key], key)


if __name__ == "__main__":
    unittest.main()
