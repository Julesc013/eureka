import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/connectors/software_heritage_approval_v0/SOFTWARE_HERITAGE_CONNECTOR_APPROVAL.json"


class SoftwareHeritageConnectorApprovalValidatorTests(unittest.TestCase):
    def test_approval_validator_passes(self):
        c = subprocess.run(
            [sys.executable, "scripts/validate_software_heritage_connector_approval.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", c.stdout)

    def test_approval_validator_json_parses(self):
        c = subprocess.run(
            [sys.executable, "scripts/validate_software_heritage_connector_approval.py", "--all-examples", "--json"],
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
            ("software_heritage_api_called", ["no_runtime_guarantees", "software_heritage_api_called"]),
            ("swhid_resolved_live", ["no_runtime_guarantees", "swhid_resolved_live"]),
            ("origin_lookup_performed", ["no_runtime_guarantees", "origin_lookup_performed"]),
            ("content_blob_lookup_performed", ["no_runtime_guarantees", "content_blob_lookup_performed"]),
            ("repository_cloned", ["no_runtime_guarantees", "repository_cloned"]),
            ("source_code_downloaded", ["no_runtime_guarantees", "source_code_downloaded"]),
            ("source_archive_downloaded", ["no_runtime_guarantees", "source_archive_downloaded"]),
            ("source_file_retrieved", ["no_runtime_guarantees", "source_file_retrieved"]),
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

    def test_negative_identity_contact_and_secret_fail(self):
        base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        p = copy.deepcopy(base)
        p["user_agent_and_contact_policy"]["contact_value"] = "ops@example.invalid"
        p["user_agent_and_contact_policy"]["contact_value_configured_now"] = True
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        p["notes"].append("software_heritage_token=not-a-real-token")
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        p["swhid_origin_repository_policy"]["example_origin_url"] = "https://example.invalid/private/repository"
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        p["swhid_origin_repository_policy"]["arbitrary_public_query_origin_allowed"] = True
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        p["public_search_boundary"]["public_search_may_accept_arbitrary_swhid_param"] = True
        self._assert_invalid(p)

    def test_negative_policy_outputs_and_claims_fail(self):
        base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        p = copy.deepcopy(base)
        p["expected_source_cache_outputs"][0]["output_runtime_implemented"] = True
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        for item in p["forbidden_capabilities"]:
            if item["capability"] == "content_blob_fetch":
                item["forbidden_now"] = False
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        p["source_code_content_risk_policy"]["content_blob_fetch_allowed"] = True
        self._assert_invalid(p)
        p = copy.deepcopy(base)
        p["source_code_content_risk_policy"]["repository_clone_allowed"] = True
        self._assert_invalid(p)
        for key in ("rights_clearance_claimed", "malware_safety_claimed", "source_code_safety_claimed", "source_completeness_claimed"):
            with self.subTest(key=key):
                p = copy.deepcopy(base)
                p["rights_access_and_risk_policy"][key] = True
                self._assert_invalid(p)

    def _assert_invalid(self, payload):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "approval.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            c = subprocess.run(
                [sys.executable, "scripts/validate_software_heritage_connector_approval.py", "--approval", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(c.returncode, 0, c.stdout)
            self.assertEqual(json.loads(c.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
