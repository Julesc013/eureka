import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/connectors/internet_archive_metadata_approval_v0/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.json"


class InternetArchiveMetadataConnectorApprovalValidatorTests(unittest.TestCase):
    def test_approval_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_internet_archive_metadata_connector_approval.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_approval_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_internet_archive_metadata_connector_approval.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 1)

    def test_negative_runtime_mutation_and_source_calls_fail(self) -> None:
        cases = [
            ("connector_runtime_implemented", ["no_runtime_guarantees", "connector_runtime_implemented"]),
            ("connector_approved_now", ["no_runtime_guarantees", "connector_approved_now"]),
            ("live_source_called", ["no_runtime_guarantees", "live_source_called"]),
            ("external_calls_performed", ["no_runtime_guarantees", "external_calls_performed"]),
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
                payload = copy.deepcopy(base)
                target = payload
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = True
                self._assert_invalid(payload)

    def test_negative_fake_contact_and_secret_fail(self) -> None:
        base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        fake_contact = copy.deepcopy(base)
        fake_contact["user_agent_and_contact_policy"]["contact_value"] = "ops@example.invalid"
        fake_contact["user_agent_and_contact_policy"]["contact_value_configured_now"] = True
        self._assert_invalid(fake_contact)

        secret = copy.deepcopy(base)
        secret["notes"].append("api_key=not-a-real-key")
        self._assert_invalid(secret)

    def test_negative_output_runtime_and_scrape_policy_fail(self) -> None:
        base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        output = copy.deepcopy(base)
        output["expected_source_cache_outputs"][0]["output_runtime_implemented"] = True
        self._assert_invalid(output)

        forbidden = copy.deepcopy(base)
        for item in forbidden["forbidden_capabilities"]:
            if item["capability"] == "scraping":
                item["forbidden_now"] = False
        self._assert_invalid(forbidden)

    def _assert_invalid(self, payload: dict) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "approval.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_internet_archive_metadata_connector_approval.py", "--approval", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(completed.returncode, 0, completed.stdout)
            report = json.loads(completed.stdout)
            self.assertEqual(report["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
