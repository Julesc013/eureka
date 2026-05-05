import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/connectors/github_releases_approval_v0/GITHUB_RELEASES_CONNECTOR_APPROVAL.json"


class GitHubReleasesConnectorApprovalValidatorTests(unittest.TestCase):
    def test_approval_validator_passes(self):
        c = subprocess.run(
            [sys.executable, "scripts/validate_github_releases_connector_approval.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", c.stdout)

    def test_approval_validator_json_parses(self):
        c = subprocess.run(
            [sys.executable, "scripts/validate_github_releases_connector_approval.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        r = json.loads(c.stdout)
        self.assertEqual(r["status"], "valid")
        self.assertEqual(r["example_count"], 1)

    def test_negative_runtime_mutation_and_source_calls_fail(self):
        cases = [
            ("connector_runtime_implemented", ["no_runtime_guarantees", "connector_runtime_implemented"]),
            ("connector_approved_now", ["no_runtime_guarantees", "connector_approved_now"]),
            ("live_source_called", ["no_runtime_guarantees", "live_source_called"]),
            ("external_calls_performed", ["no_runtime_guarantees", "external_calls_performed"]),
            ("github_api_called", ["no_runtime_guarantees", "github_api_called"]),
            ("repository_cloned", ["no_runtime_guarantees", "repository_cloned"]),
            ("releases_fetched", ["no_runtime_guarantees", "releases_fetched"]),
            ("release_assets_downloaded", ["no_runtime_guarantees", "release_assets_downloaded"]),
            ("source_archive_downloaded", ["no_runtime_guarantees", "source_archive_downloaded"]),
            ("downloads_enabled", ["no_runtime_guarantees", "downloads_enabled"]),
            ("file_retrieval_enabled", ["no_runtime_guarantees", "file_retrieval_enabled"]),
            ("public_search_live_fanout_enabled", ["no_runtime_guarantees", "public_search_live_fanout_enabled"]),
            ("source_cache_mutated", ["no_mutation_guarantees", "source_cache_mutated"]),
            ("evidence_ledger_mutated", ["no_mutation_guarantees", "evidence_ledger_mutated"]),
            ("master_index_mutated", ["no_mutation_guarantees", "master_index_mutated"]),
        ]
        base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for label, path in cases:
            with self.subTest(label=label):
                p = copy.deepcopy(base)
                t = p
                for key in path[:-1]:
                    t = t[key]
                t[path[-1]] = True
                self._assert_invalid(p)

    def test_negative_repository_policy_contact_and_secret_fail(self):
        base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        p = copy.deepcopy(base)
        p["user_agent_and_contact_policy"]["contact_value"] = "ops@example.invalid"
        p["user_agent_and_contact_policy"]["contact_value_configured_now"] = True
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        p["notes"].append("github_token=not-a-real-token")
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        p["repository_identity_policy"]["example_owner_repo"] = "private/repo"
        self._assert_invalid(p)

    def test_negative_output_runtime_and_forbidden_policy_fail(self):
        base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        p = copy.deepcopy(base)
        p["expected_source_cache_outputs"][0]["output_runtime_implemented"] = True
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        for item in p["forbidden_capabilities"]:
            if item["capability"] == "release_asset_download":
                item["forbidden_now"] = False
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        p["repository_identity_policy"]["arbitrary_public_query_repository_allowed"] = True
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        p["repository_identity_policy"]["arbitrary_repository_fetch_allowed"] = True
        self._assert_invalid(p)

    def _assert_invalid(self, payload):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "approval.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            c = subprocess.run(
                [sys.executable, "scripts/validate_github_releases_connector_approval.py", "--approval", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(c.returncode, 0, c.stdout)
            self.assertEqual(json.loads(c.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
